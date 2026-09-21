"""Model library for the synthetic-society benchmark.

Each transition type has its own interpretable social model rather than one shared
equation set with different parameters. This is the §8 circularity mitigation: a
method cannot score well merely by matching the simulator's algebra, because there
is no single algebra to match.

State variables are population-scale quantities in arbitrary units. Where a model
has a second state it is named for its social role (elites, state capacity).

Leakage discipline
------------------
Distinct algebra per type is not enough. If each type also occupies its own band of
levels or its own noise amplitude, a classifier can name the type from the
pre-transition window without detecting anything at all -- scoring well on "what"
by fingerprinting the simulator. An audit of the first draft found exactly that:
`noise_induced` was separable from every other type at 100% accuracy on step noise
alone, and every `hopf` world sat at level 0.500 because the coexistence equilibrium
`m / (a(e - m h))` was built from hard-coded constants.

Two rules follow, and `inflection.eval.leakage` enforces them as a standing gate:

1. **Common envelopes.** Every type draws its noise amplitude from one shared range,
   and every type's level is randomised over a wide overlapping range. A mechanism
   may never be inferable from an amplitude or a level.
2. **Mechanism carries the signal, not the parameters.** Where a type needs to be
   escapable (`noise_induced`), that comes from basin geometry -- parking the system
   near its fold -- rather than from louder forcing. Near-criticality is then shared
   by `fold`, `noise_induced` and `exogenous_shock`, so it fingerprints none of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy.optimize import brentq

TRANSITION_TYPES = (
    "fold",
    "hopf",
    "transcritical",
    "noise_induced",
    "exogenous_shock",
    "mechanism_change",
    "null",
)

# One shared noise envelope for every transition type. Widening or narrowing this
# for a single type reintroduces the fingerprint described above.
NOISE_ENVELOPE = (0.018, 0.032)

# Swept types hold their control parameter fixed until drift begins, then sweep to
# the critical value by `t_star`. The window is shared, and straddles the forecast
# origin on purpose: in some worlds the drift is already under way when the record
# is truncated and a trend is there to be found, in others it has not started and
# there is genuinely nothing to see. That spread is the difficulty of the benchmark.
# Drawing it per type rather than in common would make a pre-origin trend a
# signature of whichever type started drifting first -- which is what the
# transcritical model did in the first draft, at auc 0.999.
DRIFT_START_WINDOW = (0.10, 0.60)

# Models differ in their intrinsic rates -- the elite-commoner system relaxes far
# more slowly than the harvesting one -- and a fixed observation interval turns that
# into a per-type signature in step-to-step variability. A per-world time scale, drawn
# from one shared range, makes the rates overlap.
TIME_SCALE = (0.6, 1.7)

# Barrier between the high state and the separatrix, in units of the delivered
# fluctuation size, for the two near-critical bistable types. See `_a_for_barrier`.
BARRIER_RHO = (1.5, 3.0)
DEFAULT_TARGET_CV = 0.085   # used only when a spec is built outside generation


def draw_noise(rng: np.random.Generator, n: int = 1) -> np.ndarray:
    return rng.uniform(*NOISE_ENVELOPE, size=n)


def draw_drift_start(rng: np.random.Generator, T: float, t_star: float) -> float:
    """Start of the parameter sweep, always leaving room to reach criticality."""
    lo, hi = DRIFT_START_WINDOW[0] * T, DRIFT_START_WINDOW[1] * T
    return float(rng.uniform(lo, min(hi, 0.85 * t_star)))


def _ramp(value_start: float, value_end: float, drift_start: float, t_star: float):
    """Constant until `drift_start`, then linear to `value_end` at `t_star`."""
    span = max(t_star - drift_start, 1e-9)
    slope = (value_end - value_start) / span

    def f(t: float) -> float:
        return value_start if t < drift_start else value_start + slope * (t - drift_start)

    return f


@dataclass
class Spec:
    """A fully specified simulation: dynamics, noise, and sealed ground truth.

    `transition_time` is the time at which the *mechanism* changes -- a parameter
    crossing its critical value, a shock landing. It is not necessarily the time at
    which anything becomes visible in the series; see `sim.label.observable_onset`,
    which measures that separately. For a swept Hopf the gap between the two is
    large and systematic, and conflating them would punish every method for a delay
    that belongs to the system rather than to the forecast.
    """

    rhs: Callable[[float, np.ndarray], np.ndarray]
    x0: np.ndarray
    state_names: tuple[str, ...]
    noise_scale: np.ndarray
    transition_type: str
    transition_time: float | None
    primary: int
    params: dict = field(default_factory=dict)
    shock: tuple[float, np.ndarray] | None = None
    floor: float = 1e-4


# --- May harvesting model: dN/dt = rN(1 - N/K) - a N^2/(h^2 + N^2) ------------
# The canonical fold system. Used for the fold, noise-induced, exogenous-shock,
# mechanism-change and null types, at different points in its parameter space.


def draw_may_params(rng: np.random.Generator) -> dict:
    """Randomised May parameters. K varies widely so no type owns a level band."""
    return dict(
        r=float(rng.uniform(0.6, 1.4)),
        K=float(rng.uniform(6.0, 16.0)),
        h=float(rng.uniform(0.7, 1.5)),
    )


def _may_growth_over_extraction(n, r: float, K: float, h: float):
    """Value of `a` at which N is an equilibrium. Equilibria solve g(N) = a."""
    n = np.asarray(n, dtype=float)
    return r * (1.0 - n / K) * (h * h + n * n) / n


def may_fold_point(r: float = 1.0, K: float = 10.0, h: float = 1.0) -> tuple[float, float]:
    """Locate the saddle-node that destroys the high-population state.

    g(N) has a local maximum on the interior; the upper (stable) and middle
    (unstable) equilibria collide there. Returns (a_critical, N_at_fold).
    """
    grid = np.linspace(1e-3, K - 1e-6, 20000)
    g = _may_growth_over_extraction(grid, r, K, h)
    interior = np.arange(1, len(grid) - 1)
    maxima = interior[(g[1:-1] > g[:-2]) & (g[1:-1] > g[2:])]
    if len(maxima) == 0:
        raise RuntimeError("no fold in this parameter region")
    i = maxima[-1]
    return float(g[i]), float(grid[i])


def may_equilibria(a: float, r: float = 1.0, K: float = 10.0, h: float = 1.0) -> list[float]:
    """All positive equilibria of the May model at extraction level `a`."""
    grid = np.linspace(1e-3, K - 1e-6, 4000)
    g = _may_growth_over_extraction(grid, r, K, h) - a
    roots: list[float] = []
    for i in range(len(grid) - 1):
        if g[i] == 0.0:
            roots.append(float(grid[i]))
        elif g[i] * g[i + 1] < 0:
            roots.append(
                float(brentq(lambda n: _may_growth_over_extraction(n, r, K, h) - a, grid[i], grid[i + 1]))
            )
    return roots


def _may_rhs(a_of_t: Callable[[float], float], r: float, K: float, h: float):
    def rhs(t: float, x: np.ndarray) -> np.ndarray:
        n = x[0]
        a = a_of_t(t)
        return np.array([r * n * (1.0 - n / K) - a * n * n / (h * h + n * n)])

    return rhs


def _relative_barrier(a: float, p: dict) -> float:
    eq = may_equilibria(a, **p)
    if len(eq) != 3:
        return float("nan")
    _, mid, high = sorted(eq)
    return (high - mid) / high


def _a_for_barrier(p: dict, rel_barrier: float) -> float:
    """The extraction level whose high state sits `rel_barrier` (a fraction of its own
    level) above the separatrix.

    Whether a noise-driven escape happens, and when, is governed by the barrier
    measured in units of the fluctuation size -- not by the distance to the fold in
    parameter space. The two near-critical types used to draw a/a_c from a fixed
    window, 0.985-0.996, whatever their noise. Since the delivered fluctuation size is
    a design variable drawn from one shared range, that fixed window meant a quiet
    world had an effectively enormous barrier and a loud one almost none: at CV 0.025
    not one `noise_induced` attempt in 120 escaped at all, and at 0.14 three in four
    escaped before the window. Generation then failed on a quarter of noise-induced
    designs, concentrated at both ends of the CV range -- selection on a nuisance
    variable by the failure route (LOG.md, Gate 3 step 1).
    """
    a_c, _ = may_fold_point(**p)
    grid = a_c * (1.0 - np.geomspace(1e-7, 0.6, 500))
    vals = np.array([_relative_barrier(a, p) for a in grid])
    above = np.where(np.isfinite(vals) & (vals >= rel_barrier))[0]
    if len(above) == 0 or above[0] == 0:
        raise RuntimeError("barrier not reachable inside the bistable window")
    j = above[0]
    return float(brentq(lambda a: _relative_barrier(a, p) - rel_barrier, grid[j], grid[j - 1]))


def _near_critical_a(rng: np.random.Generator, p: dict, target_cv: float | None) -> float:
    """Extraction level for a bistable world with barrier `rho` x the fluctuation size."""
    rho = rng.uniform(*BARRIER_RHO)
    return _a_for_barrier(p, rho * (target_cv or DEFAULT_TARGET_CV))


def spec_fold(rng: np.random.Generator, T: float, t_star: float) -> Spec:
    """Elite extraction intensifies until the productive population cannot be sustained."""
    p = draw_may_params(rng)
    a_c, _ = may_fold_point(**p)
    a_start = a_c * rng.uniform(0.55, 0.72)
    drift_start = draw_drift_start(rng, T, t_star)
    a_of_t = _ramp(a_start, a_c, drift_start, t_star)

    n0 = max(may_equilibria(a_start, **p))
    return Spec(
        rhs=_may_rhs(a_of_t, **p),
        x0=np.array([n0]),
        state_names=("population",),
        noise_scale=draw_noise(rng),
        transition_type="fold",
        transition_time=t_star,
        primary=0,
        params=dict(
            model="may_harvesting", a_start=a_start, a_critical=a_c,
            drift_start=drift_start, **p,
        ),
    )


def spec_null(rng: np.random.Generator, T: float, t_star: float | None = None) -> Spec:
    """Stationary society: parked well clear of the fold, no drift, no shock."""
    p = draw_may_params(rng)
    a_c, _ = may_fold_point(**p)
    a = a_c * rng.uniform(0.45, 0.65)
    n0 = max(may_equilibria(a, **p))
    return Spec(
        rhs=_may_rhs(lambda t: a, **p),
        x0=np.array([n0]),
        state_names=("population",),
        noise_scale=draw_noise(rng),
        transition_type="null",
        transition_time=None,
        primary=0,
        params=dict(model="may_harvesting", a=a, a_critical=a_c, **p),
    )


def spec_noise_induced(rng: np.random.Generator, T: float, t_star: float | None = None,
                       target_cv: float | None = None) -> Spec:
    """Parked in a shallow basin; escape is diffusive, not driven.

    The escape comes from basin geometry -- the barrier to the low state is only
    1.5-3 fluctuation sizes high (`BARRIER_RHO`) -- and not from louder noise, which
    would make the type trivially identifiable. So a quiet world sits nearer the
    fold than a loud one, as a noise-driven escape requires. The system is genuinely
    near-critical and *does* show elevated variance. That is intended: `fold` and
    `exogenous_shock` are near-critical too, so the signature identifies none of
    them. What separates this type is that nothing drifts and nothing arrives; the
    escape is a fluctuation that happens to clear the barrier.
    """
    p = draw_may_params(rng)
    a = _near_critical_a(rng, p, target_cv)
    eq = may_equilibria(a, **p)
    n0 = max(eq)
    return Spec(
        rhs=_may_rhs(lambda t: a, **p),
        x0=np.array([n0]),
        state_names=("population",),
        noise_scale=draw_noise(rng),
        transition_type="noise_induced",
        transition_time=None,  # filled in post hoc: first passage of the separatrix
        primary=0,
        params=dict(model="may_harvesting", a=a, equilibria=eq, **p),
    )


def spec_exogenous_shock(rng: np.random.Generator, T: float, t_star: float,
                         target_cv: float | None = None) -> Spec:
    """Quiet bistable system flipped by a single outside pulse (plague, climate failure).

    Drawn with the same barrier-in-noise-units as `noise_induced` so the two cannot
    be told apart by their resting statistics -- only by whether the departure is a
    fluctuation or an arrival. Worlds that escape on their own before the shock are
    rejected at generation (`label.in_high_state_before`).
    """
    p = draw_may_params(rng)
    a = _near_critical_a(rng, p, target_cv)
    eq = may_equilibria(a, **p)
    n0, separatrix = max(eq), sorted(eq)[1]
    target = separatrix * rng.uniform(0.45, 0.80)
    return Spec(
        rhs=_may_rhs(lambda t: a, **p),
        x0=np.array([n0]),
        state_names=("population",),
        noise_scale=draw_noise(rng),
        transition_type="exogenous_shock",
        transition_time=t_star,
        primary=0,
        shock=(t_star, np.array([target])),
        params=dict(model="may_harvesting", a=a, equilibria=eq, shock_target=target, **p),
    )


def spec_mechanism_change(rng: np.random.Generator, T: float, t_star: float) -> Spec:
    """The equations themselves change: intensification raises capacity and linearises extraction.

    Before `t_star` this is indistinguishable from `null` by construction -- same
    model, same parameter draw, same resting statistics. That is the point: the
    interesting question is whether anything can be said about a change whose
    antecedents are, in the observable record, nothing at all.
    """
    p = draw_may_params(rng)
    a_c, _ = may_fold_point(**p)
    a = a_c * rng.uniform(0.45, 0.65)
    n0 = max(may_equilibria(a, **p))
    K_new = p["K"] * rng.uniform(3.0, 4.5)
    a_lin = rng.uniform(0.10, 0.20)
    r, K, h = p["r"], p["K"], p["h"]

    def rhs(t: float, x: np.ndarray) -> np.ndarray:
        n = x[0]
        if t < t_star:
            return np.array([r * n * (1.0 - n / K) - a * n * n / (h * h + n * n)])
        return np.array([r * n * (1.0 - n / K_new) - a_lin * n])

    return Spec(
        rhs=rhs,
        x0=np.array([n0]),
        state_names=("population",),
        noise_scale=draw_noise(rng),
        transition_type="mechanism_change",
        transition_time=t_star,
        primary=0,
        params=dict(model="may_to_intensified", a=a, K_new=K_new, a_lin=a_lin, **p),
    )


# --- Rosenzweig-MacArthur elites and commoners -------------------------------
# Rising productivity destabilises the elite-commoner equilibrium into secular
# cycles: the paradox of enrichment, read as a cliodynamic Hopf bifurcation.


def rm_hopf_K(a: float, h: float, e: float, m: float) -> float:
    """Carrying capacity at which the coexistence equilibrium loses stability."""
    n_star = m / (a * (e - m * h))
    return 2.0 * n_star + 1.0 / (a * h)


def spec_hopf(rng: np.random.Generator, T: float, t_star: float) -> Spec:
    """Rising productivity tips a stable elite-commoner balance into secular cycles.

    The functional-response parameters are drawn per run rather than fixed. In the
    first draft they were constants, which pinned every hopf world to a commoner
    equilibrium of exactly 0.500 and made the type readable from the series level
    alone.

    Amplitude past the bifurcation grows like sqrt(K - K_c) from whatever the noise
    seeds it with, so cycles become visible well after `t_star` -- a real bifurcation
    delay, not a modelling artefact. The sweep continues to roughly 1.5x K_c by the
    end of the run so the cycle is established within the observation window; see
    LOG.md for the calibration.
    """
    r = float(rng.uniform(0.8, 1.3))
    a = float(rng.uniform(0.8, 1.4))
    h = float(rng.uniform(0.35, 0.65))
    m = float(rng.uniform(0.15, 0.28))
    # Conversion efficiency must satisfy e > m*h for coexistence; keep a margin.
    e = float(rng.uniform(m * h + 0.25, m * h + 0.55))
    scale = float(rng.uniform(1.5, 6.0))  # units of the commoner series

    K_c = rm_hopf_K(a, h, e, m)
    K_start = K_c * rng.uniform(0.62, 0.78)
    drift_start = draw_drift_start(rng, T, t_star)
    # Continue the sweep past t_star at the same rate, so K reaches well beyond K_c
    # and the cycle has room to establish inside the observation window.
    K_of_t = _ramp(K_start, K_c, drift_start, t_star)
    n_star = m / (a * (e - m * h))

    def rhs(t: float, x: np.ndarray) -> np.ndarray:
        n, el = x
        K = K_of_t(t)
        functional = a * n * el / (1.0 + a * h * n)
        return np.array([r * n * (1.0 - n / K) - functional, e * functional - m * el])

    e_star = r * (1.0 - n_star / K_start) * (1.0 + a * h * n_star) / a
    spec = Spec(
        rhs=rhs,
        x0=np.array([n_star, max(e_star, 0.05)]),
        state_names=("commoners", "elites"),
        noise_scale=draw_noise(rng, 2),
        transition_type="hopf",
        transition_time=t_star,
        primary=0,
        params=dict(
            model="rosenzweig_macarthur",
            r=r, a=a, h=h, e=e, m=m,
            K_start=K_start, K_critical=K_c, drift_start=drift_start,
            n_star=n_star, scale=scale,
        ),
    )
    # The RM state lives near n* ~ O(1) regardless of parameters; rescale the whole
    # system into a randomised unit range so the level cannot identify the type.
    return _rescale(spec, scale)


def _rescale(spec: Spec, scale: float) -> Spec:
    """Express a Spec in units `scale` times larger, leaving the dynamics unchanged.

    Multiplicative noise and the relative shape of the trajectory are invariant, so
    this only moves the series' level -- which is exactly what must be randomised.
    """
    inner = spec.rhs
    spec.rhs = lambda t, x: inner(t, x / scale) * scale
    spec.x0 = spec.x0 * scale
    if spec.shock is not None:
        spec.shock = (spec.shock[0], spec.shock[1] * scale)
    spec.floor = spec.floor * scale
    return spec


# --- State capacity versus elite capture -------------------------------------
# dx/dt = x(rho - b x) exchanges stability between x = 0 and x = rho/b at rho = 0:
# a transcritical bifurcation read as institutional capacity losing to capture.


def spec_transcritical(rng: np.random.Generator, T: float, t_star: float) -> Spec:
    b = float(rng.uniform(0.7, 1.4))
    rho_start = float(rng.uniform(0.30, 0.50))
    r_pop = float(rng.uniform(0.25, 0.45))
    K0 = float(rng.uniform(1.2, 3.0))
    c = float(rng.uniform(8.0, 22.0))
    drift_start = draw_drift_start(rng, T, t_star)
    rho_of_t = _ramp(rho_start, 0.0, drift_start, t_star)

    def rhs(t: float, x: np.ndarray) -> np.ndarray:
        cap, n = x
        rho = rho_of_t(t)
        K = K0 + c * cap
        return np.array([cap * (rho - b * cap), r_pop * n * (1.0 - n / K)])

    cap0 = rho_start / b
    return Spec(
        rhs=rhs,
        x0=np.array([cap0, K0 + c * cap0]),
        state_names=("state_capacity", "population"),
        noise_scale=draw_noise(rng, 2),
        transition_type="transcritical",
        transition_time=t_star,
        primary=1,
        params=dict(
            model="capacity_capture", b=b, rho_start=rho_start,
            drift_start=drift_start, K0=K0, c=c, r_pop=r_pop,
        ),
    )


BUILDERS = {
    "fold": spec_fold,
    "hopf": spec_hopf,
    "transcritical": spec_transcritical,
    "noise_induced": spec_noise_induced,
    "exogenous_shock": spec_exogenous_shock,
    "mechanism_change": spec_mechanism_change,
    "null": spec_null,
}


def _apply_time_scale(spec: Spec, tau: float) -> Spec:
    """Run the dynamics `tau` times faster without moving the scheduled events.

    Only the right-hand side is scaled, so a sweep that reaches criticality at
    `t_star` still does so; what changes is how fast the system relaxes relative to
    that schedule. Noise is scaled by sqrt(tau) to hold the stationary fluctuation
    size fixed, so this varies the relaxation rate without varying the noise level.
    """
    inner = spec.rhs
    spec.rhs = lambda t, x: inner(t, x) * tau
    spec.noise_scale = spec.noise_scale * np.sqrt(tau)
    spec.params = dict(spec.params, time_scale=tau)
    return spec


NEEDS_TARGET_CV = ("noise_induced", "exogenous_shock")


def build(transition_type: str, rng: np.random.Generator, T: float, t_star: float | None,
          target_cv: float | None = None) -> Spec:
    if transition_type in NEEDS_TARGET_CV:
        spec = BUILDERS[transition_type](rng, T, t_star, target_cv=target_cv)
    else:
        spec = BUILDERS[transition_type](rng, T, t_star)
    return _apply_time_scale(spec, float(rng.uniform(*TIME_SCALE)))
