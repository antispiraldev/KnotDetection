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
moment the series itself departs: the earliest a perfect detector with no model
could possibly fire. Scoring "when" against the first without reporting the second
would charge every method for a delay that belongs to the system.
"""

from __future__ import annotations

import numpy as np

from .integrate import Run


def _rolling(x: np.ndarray, width: int, fn) -> tuple[np.ndarray, np.ndarray]:
    """Non-overlapping window statistic; returns (window start index, value)."""
    idx, vals = [], []
    for lo in range(0, len(x) - width + 1, width):
        idx.append(lo)
        vals.append(fn(x[lo:lo + width]))
    return np.array(idx), np.array(vals)


def _first_sustained(flags: np.ndarray, need: int) -> int | None:
    for i in range(len(flags) - need + 1):
        if flags[i:i + need].all():
            return i
    return None


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


def observable_onset(
    run: Run,
    baseline_frac: float = 0.20,
    width: int = 20,
    z_level: float = 6.0,
    k_amp: float = 3.5,
    need: int = 3,
) -> float | None:
    """First sustained departure from the run's own early behaviour.

    Two departures count, because the types differ in what changes. A level shift
    catches fold, shock, transcritical and mechanism change. An amplitude shift
    catches the Hopf, whose mean is unmoved while its cycles grow. The earlier of
    the two is returned.

    `need` consecutive windows must exceed the threshold, which is what keeps single
    noisy windows from registering as onsets.
    """
    s = run.series
    n_base = max(int(len(s) * baseline_frac), 3 * width)
    if n_base >= len(s):
        return None
    base = s[:n_base]

    med = float(np.median(base))
    mad = float(np.median(np.abs(base - med))) * 1.4826
    if mad <= 0:
        mad = float(np.std(base)) or 1e-9

    idx, level = _rolling(s, width, np.median)
    _, amp = _rolling(s, width, lambda w: float(np.ptp(w)))

    n_base_win = max(n_base // width, 2)
    base_amp = float(np.median(amp[:n_base_win])) or 1e-9

    after = idx >= n_base
    onsets = []

    hit = _first_sustained((np.abs(level - med) > z_level * mad)[after], need)
    if hit is not None:
        onsets.append(float(run.t[idx[after][hit]]))

    hit = _first_sustained((amp > k_amp * base_amp)[after], need)
    if hit is not None:
        onsets.append(float(run.t[idx[after][hit]]))

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
