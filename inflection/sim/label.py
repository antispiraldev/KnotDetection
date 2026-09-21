"""Post-hoc ground truth measured from a finished trajectory.

A Spec knows when its *mechanism* changes. It does not know when that change becomes
visible, and for two types it does not know the transition time at all:

- `noise_induced` has no scheduled time. The escape is a first passage, so its time
  exists only once the path has been drawn.
- `hopf` crosses its bifurcation at `t_star`, but amplitude then grows like
  sqrt(K - K_c) from whatever the noise seeds it with. The cycle becomes visible
  long afterwards, and by a lag that varies run to run.

So the benchmark carries two timestamps. `transition_time` is the mechanism change:
the honest target for "when did the system change?". `observable_onset` is the first
moment the series itself departs, as judged by one fixed and deliberately
conservative threshold detector. It approximates the earliest a model-free detector
could fire, but is not that bound: it runs late on spiky oscillations in particular
(see LOG.md, onset caveat). Scoring "when" against the first without reporting the second
would charge every method for a delay that belongs to the system.
"""

from __future__ import annotations

import numpy as np

from .integrate import Run


def separatrix_crossing(run: Run, hold: int = 15) -> float | None:
    """When the system commits to the low state, not when it first dips.

    The obvious definition -- first passage below the unstable middle equilibrium --
    is wrong for a noisy bistable system, and visibly so: a trajectory can cross the
    separatrix, wander, and climb back to the high state. Labelling that first dip as
    the transition put the transition time 120 units before the series actually left,
    with a full recovery in between.

    So the escape is the *last* departure: the point after which the system never
    returns above the separatrix. `hold` guards the other end, requiring the low
    state to persist to the end of the run rather than counting a dip in the final
    few observations, where there is no evidence it would have stayed.

    Only meaningful for runs built in the bistable window; returns None if the system
    never leaves the high state, or leaves too late to tell.
    """
    eq = run.params.get("equilibria")
    if eq is None or len(eq) != 3:
        return None
    separatrix = sorted(eq)[1] * run.params.get("scale", 1.0)

    above = np.where(run.series >= separatrix)[0]
    if len(above) == 0:
        return float(run.t[0])          # started below: not a usable escape
    last_above = int(above[-1])
    if last_above >= len(run.series) - hold - 1:
        return None                      # never left, or left too late to confirm
    return float(run.t[last_above + 1])


def _centered_rolling_median(x: np.ndarray, width: int) -> np.ndarray:
    """Median of the window centred on each point; NaN where the window is incomplete."""
    out = np.full(len(x), np.nan)
    if len(x) < width:
        return out
    half = width // 2
    windows = np.lib.stride_tricks.sliding_window_view(x, width)
    out[half:half + len(windows)] = np.median(windows, axis=1)
    return out


def _first_sustained_run(flags: np.ndarray, hold: int) -> int | None:
    """Index where the first run of at least `hold` consecutive True values begins."""
    run = 0
    for i, f in enumerate(flags):
        run = run + 1 if f else 0
        if run >= hold:
            return i - hold + 1
    return None


def observable_onset(
    run: Run,
    baseline_frac: float = 0.20,
    width: int = 20,
    z_level: float = 6.0,
    k_amp: float = 3.5,
    hold: int = 60,
) -> float | None:
    """First sustained departure from the run's own early behaviour, to the time step.

    Two departures count, because the types differ in what changes. A level shift
    catches fold, shock, transcritical and mechanism change. An amplitude shift
    catches the Hopf, whose mean is unmoved while its cycles grow. The earlier of the
    two is returned.

    Both signals are *centred rolling medians*, evaluated at every time step. An
    earlier version used non-overlapping 20-step windows and reported the left edge
    of the first window to depart, which quantised every onset to a multiple of 20
    and biased it early by up to a full window: a shock landing at t=106 fell inside
    [100, 120) and was reported as visible at t=100, before it happened. Instantaneous
    transitions showed median lags of about -5 as a result. A centred median flips
    only once more than half its window lies past a step, so it places a step where
    it actually is -- which matters because this timestamp is the proposed target for
    scoring "when".

    - level: centred rolling median of the series, against the baseline median, in
      units of the baseline's point-wise MAD.
    - amplitude: centred rolling median of each point's absolute deviation from the
      local level, against its own baseline value. Median-based for the same reason.

    `hold` consecutive steps must depart, which keeps a stationary series quiet even
    though stride-1 windows give it many more chances to wander over the line.
    """
    s = np.asarray(run.series, dtype=float)
    n_base = max(int(len(s) * baseline_frac), 3 * width)
    if n_base >= len(s):
        return None
    base = s[:n_base]

    med = float(np.median(base))
    mad = float(np.median(np.abs(base - med))) * 1.4826
    if mad <= 0:
        mad = float(np.std(base)) or 1e-9

    level = _centered_rolling_median(s, width)
    local_dev = np.abs(s - np.where(np.isnan(level), med, level))
    amp = _centered_rolling_median(local_dev, width)
    base_amp = float(np.nanmedian(amp[:n_base]))
    if not np.isfinite(base_amp) or base_amp <= 0:
        base_amp = 1e-9

    with np.errstate(invalid="ignore"):
        level_hot = np.abs(level - med) > z_level * mad
        amp_hot = amp > k_amp * base_amp
    level_hot[:n_base] = False
    amp_hot[:n_base] = False

    onsets = []
    for hot in (level_hot, amp_hot):
        i = _first_sustained_run(hot, hold)
        if i is not None:
            onsets.append(float(run.t[i]))
    return min(onsets) if onsets else None


def label(run: Run) -> dict:
    """Full ground truth for one finished run."""
    t_star = run.transition_time
    if run.transition_type == "noise_induced":
        t_star = separatrix_crossing(run)

    onset = observable_onset(run)
    return dict(
        transition_type=run.transition_type,
        transition_time=t_star,
        observable_onset=onset,
        onset_lag=None if (t_star is None or onset is None) else onset - t_star,
        transitioned=t_star is not None,
    )
