"""World generation: draw a society, integrate it, label it, keep it if usable.

Design constraints that exist to stop the label leaking into the series
---------------------------------------------------------------------
Every world, whatever its transition type, is delivered on the same footing:

- the same run length `T` and the same observation grid, so series length says
  nothing about mechanism;
- transition times drawn from one shared window, so timing says nothing either --
  including for `noise_induced`, whose escape is a first passage and is therefore
  accepted only when it happens to land in that same window;
- one shared noise envelope (see `models.NOISE_ENVELOPE`);
- a single observable per world -- the primary state -- because a historical proxy
  records one thing, and because delivering the elite series alongside the commoner
  series would announce the two-state models.

Rejection sampling conditions the distribution of escape times for `noise_induced`.
That is a statement about which worlds enter the benchmark, not about the physics
inside any world, and the acceptance rate is recorded with the dataset.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path

import numpy as np

from . import models
from .integrate import simulate
from .label import label
from .realism import CLEAN, Realism, apply as apply_realism

T = 300.0
DT = 0.01
OBS_STEP = 1.0
ORIGIN_FRAC = 0.30          # forecast origin: series truncated here
TSTAR_WINDOW = (0.33, 0.50)  # shared across every transition type

# How much the delivered series wobbles before the origin, drawn per world from one
# shared range and then calibrated for. Left uncalibrated, this is a per-type
# signature: the elite-commoner model has weakly damped oscillatory modes and wobbles
# roughly seven times as much as the harvesting model, which made `hopf` identifiable
# at auc 0.999 from spread alone -- while sitting at K/K_c ~ 0.7, nowhere near its
# bifurcation. That is a property of the equations chosen to represent the type, not
# of any society, so it is calibrated away rather than reported as a finding.
CV_TARGET = (0.02, 0.15)
CV_CLIP = (0.1, 12.0)       # bounds on the noise rescaling a single calibration may apply


def tstar_range() -> tuple[float, float]:
    return TSTAR_WINDOW[0] * T, TSTAR_WINDOW[1] * T


@dataclass
class World:
    world_id: str
    transition_type: str
    transition_time: float | None
    observable_onset: float | None
    onset_lag: float | None
    transitioned: bool
    origin: float
    t: np.ndarray
    x: np.ndarray                 # full multivariate truth, sealed
    raw: np.ndarray               # true primary state, full length, sealed
    state_names: tuple[str, ...]
    primary: int
    params: dict = field(default_factory=dict)
    attempts: int = 1

    def record(
        self,
        realism: Realism = CLEAN,
        rng: np.random.Generator | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """The record a method is given: pre-origin only, degraded, in arbitrary units.

        Normalisation is last, by the median of whatever survived, so the delivered
        series carries no absolute scale however it was degraded on the way.
        """
        m = self.t < self.origin
        t, y = apply_realism(self.t[m], self.raw[m], realism, rng or np.random.default_rng(0))
        unit = float(np.median(y))
        return t, y / (unit if np.isfinite(unit) and unit > 0 else 1.0)

    def truncated(self) -> tuple[np.ndarray, np.ndarray]:
        """The clean record: everything strictly before the origin, undegraded."""
        return self.record(CLEAN)

    def sealed_truth(self) -> dict:
        return dict(
            world_id=self.world_id,
            transition_type=self.transition_type,
            transition_time=self.transition_time,
            observable_onset=self.observable_onset,
            onset_lag=self.onset_lag,
            transitioned=self.transitioned,
        )


def _calibrate_cv(spec, target_cv: float, origin: float, rng: np.random.Generator) -> float:
    """Scale the noise so the pre-origin coefficient of variation hits `target_cv`.

    A short pilot run measures what the model does at its drawn noise level, and the
    noise is rescaled by the shortfall. Fluctuation size is close to linear in the
    forcing for a damped system, so one iteration lands near the target; the residual
    error is absorbed by the shared target range rather than chased.

    The pilot uses its own generator, so the calibration does not correlate with the
    noise path of the run that follows.
    """
    pilot_rng = np.random.default_rng(rng.integers(2**63))
    pilot = simulate(spec, origin, DT, OBS_STEP, pilot_rng)
    s = pilot.series
    med = float(np.median(s))
    if not np.isfinite(med) or med <= 0:
        raise RuntimeError("pilot run degenerate")

    # A pilot that has already transitioned cannot be calibrated against. Near-
    # critical worlds sometimes escape spontaneously inside the pilot window; the
    # collapse makes std/median enormous, and calibrating against it slashes the
    # noise by an order of magnitude. That is not harmless. For `noise_induced` the
    # nearly silent world then never escapes and is rejected, so the damage undoes
    # itself -- but `exogenous_shock` has its transition *imposed*, so the same world
    # is accepted with its noise a tenth of what it should be. Three of 25 shock
    # worlds arrived that way, pinned against the calibration clip, and the
    # resulting low spread identified the type at auc 0.80. Legitimate pre-origin
    # records have CV <= 0.15, so a point beyond half or double the median is a
    # regime change, never a fluctuation. Redraw the world instead.
    if s.min() < 0.5 * med or s.max() > 2.0 * med:
        raise RuntimeError("pilot run transitioned before the origin")

    cv = float(np.std(s)) / med
    if cv <= 0:
        raise RuntimeError("pilot run has no variation")
    factor = float(np.clip(target_cv / cv, *CV_CLIP))
    spec.noise_scale = spec.noise_scale * factor
    spec.params = dict(spec.params, target_cv=target_cv, cv_calibration=factor)
    return factor


def _usable(w_label: dict, origin: float, t_star_lo: float, t_star_hi: float) -> tuple[bool, str]:
    """Is this world fit to forecast from?"""
    t_star = w_label["transition_time"]
    onset = w_label["observable_onset"]
    tt = w_label["transition_type"]

    if tt == "null":
        # A null world that visibly departs is not null. Reject rather than mislabel.
        return (onset is None, "null world departed" if onset is not None else "")

    if t_star is None:
        return False, "no transition occurred"
    if not (t_star_lo <= t_star <= t_star_hi):
        return False, "transition outside the shared window"
    if onset is None:
        return False, "transition never became visible"
    if onset <= origin:
        return False, "visible before the forecast origin"
    return True, ""


def generate_world(
    transition_type: str,
    rng: np.random.Generator,
    max_attempts: int = 60,
) -> World | None:
    """Draw worlds of this type until one is usable, or give up.

    The design variables -- target fluctuation size and scheduled transition time --
    are assigned once, *before* the rejection loop, and held fixed through every
    retry. Retries resample only the physics and the noise path.

    This ordering is what keeps rejection sampling honest. When the target CV was
    redrawn on each attempt, acceptance quietly filtered it: a loud, near-critical
    `exogenous_shock` world tends to escape on its own before its shock arrives, is
    rejected, and redraws, so accepted shock worlds ended up with a median target CV
    of 0.045 against ~0.085 for every other type -- despite all types drawing from
    one shared range. The calibration was undone by selection, and the audit caught
    it as `sd` separating shock worlds at auc 0.80. A variable the leakage gate
    treats as nuisance must be assigned where selection cannot act on it.

    Returns None if no usable world is found at these design values. That is itself
    a bias if it happens often for some types and not others, so failures are
    counted and reported by `generate_pool`.
    """
    origin = ORIGIN_FRAC * T
    lo, hi = tstar_range()

    target_cv = float(rng.uniform(*CV_TARGET))
    if transition_type in ("null", "noise_induced"):
        t_star_req = None
    else:
        t_star_req = float(rng.uniform(lo, hi))

    for attempt in range(1, max_attempts + 1):
        try:
            spec = models.build(transition_type, rng, T, t_star_req)
            _calibrate_cv(spec, target_cv, origin, rng)
            run = simulate(spec, T, DT, OBS_STEP, rng)
        except RuntimeError:
            continue

        lab = label(run)
        ok, _ = _usable(lab, origin, lo, hi)
        if not ok:
            continue

        pre = run.series[run.t < origin]
        unit = float(np.median(pre))
        if not np.isfinite(unit) or unit <= 0:
            continue

        blob = f"{transition_type}:{lab['transition_time']}:{run.series[:5].tobytes()!r}"
        return World(
            world_id=hashlib.sha256(blob.encode()).hexdigest()[:16],
            origin=origin,
            t=run.t,
            x=run.x,
            raw=run.series,
            state_names=run.state_names,
            primary=run.primary,
            params=dict(run.params, clean_unit=unit),
            attempts=attempt,
            **lab,
        )
    return None


def generate_pool(
    n_per_type: int,
    seed: int,
    types: tuple[str, ...] = models.TRANSITION_TYPES,
) -> tuple[list[World], dict]:
    """A balanced pool with one entry per type per index."""
    rng = np.random.default_rng(seed)
    worlds, failures = [], {t: 0 for t in types}
    for tt in types:
        for _ in range(n_per_type):
            w = generate_world(tt, rng)
            if w is None:
                failures[tt] += 1
            else:
                worlds.append(w)
    rng.shuffle(worlds)
    stats = dict(
        seed=seed,
        n_requested=n_per_type * len(types),
        n_generated=len(worlds),
        failures=failures,
        mean_attempts={
            tt: float(np.mean([w.attempts for w in worlds if w.transition_type == tt] or [np.nan]))
            for tt in types
        },
    )
    return worlds, stats


def save_pool(
    worlds: list[World],
    stats: dict,
    out_dir: Path,
    realism: Realism = CLEAN,
    seed: int = 0,
    seal: bool = True,
) -> dict:
    """Write records and (optionally sealed) truth, with a hash manifest.

    With `seal=True` the truth file is written to a sibling `sealed/` directory that
    `.gitignore` excludes, and only its hash goes in the manifest. Methods read the
    records; the truth is opened at scoring time.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    series, times = {}, {}
    for w in worlds:
        t, y = w.record(realism, rng)
        series[w.world_id], times[f"t_{w.world_id}"] = y, t
    origins = {w.world_id: w.origin for w in worlds}
    np.savez_compressed(out_dir / "series.npz", **series, **times)

    truth = [w.sealed_truth() for w in worlds]
    truth_json = json.dumps(truth, indent=2, sort_keys=True)
    truth_hash = hashlib.sha256(truth_json.encode()).hexdigest()

    if seal:
        sealed = out_dir / "sealed"
        sealed.mkdir(exist_ok=True)
        (sealed / "truth.json").write_text(truth_json)
    else:
        (out_dir / "truth.json").write_text(truth_json)

    manifest = dict(
        n_worlds=len(worlds),
        T=T, dt=DT, obs_step=OBS_STEP,
        origin_frac=ORIGIN_FRAC,
        tstar_window=list(TSTAR_WINDOW),
        noise_envelope=list(models.NOISE_ENVELOPE),
        cv_target=list(CV_TARGET),
        realism=realism.name,
        record_seed=seed,
        world_ids=sorted(series),
        origins=origins,
        truth_sha256=truth_hash,
        sealed=seal,
        generation=stats,
    )
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest
