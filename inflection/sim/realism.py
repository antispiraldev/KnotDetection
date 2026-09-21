"""Realism layers: the degradations that separate a simulation from a record.

Each layer is switchable on its own so that its cost can be attributed, which is
what lets the benchmark answer "how much noise, or sparsity, kills each method?"
rather than only "does this method work?".

Order is not arbitrary. Layers are applied to the true series in the order a real
record acquires them -- the proxy relationship is a fact about what was deposited,
sampling is a fact about what survived, measurement error is a fact about reading it
-- and normalisation happens last, once the series looks like something dug up
rather than computed. Normalising first and then degrading would reintroduce the
absolute scale that the units-invariance gate depends on being absent.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Realism:
    """One configuration of the observation process. All-off is the clean case."""

    obs_noise: float = 0.0        # multiplicative measurement error, as a fraction
    keep_fraction: float = 1.0    # fraction of time points that survive
    irregular: bool = False       # drop at random rather than on a regular grid
    proxy_exponent: float = 1.0   # y -> y**exponent, a monotone distortion
    proxy_floor: float = 0.0      # proxy saturates below this quantile of the series
    max_points: int | None = None  # truncate the record to its final N points

    @property
    def name(self) -> str:
        if self == Realism():
            return "clean"
        bits = []
        if self.obs_noise:
            bits.append(f"obs{self.obs_noise:g}")
        if self.keep_fraction < 1.0:
            bits.append(f"keep{self.keep_fraction:g}{'irr' if self.irregular else ''}")
        if self.proxy_exponent != 1.0:
            bits.append(f"pow{self.proxy_exponent:g}")
        if self.proxy_floor:
            bits.append(f"floor{self.proxy_floor:g}")
        if self.max_points:
            bits.append(f"n{self.max_points}")
        return "+".join(bits)


CLEAN = Realism()

# The named settings the benchmark reports against. `harsh` is the one whose results
# the plan (§8) says to report alongside the clean case, so that nothing rests on the
# simulator being kind.
LAYERS = {
    "clean": CLEAN,
    "observation_noise": Realism(obs_noise=0.05),
    "sparse": Realism(keep_fraction=0.4),
    "irregular": Realism(keep_fraction=0.4, irregular=True),
    "proxy": Realism(proxy_exponent=0.6, proxy_floor=0.1),
    "short": Realism(max_points=40),
    "harsh": Realism(
        obs_noise=0.05, keep_fraction=0.4, irregular=True,
        proxy_exponent=0.6, proxy_floor=0.1, max_points=60,
    ),
}


def apply(
    t: np.ndarray,
    y: np.ndarray,
    realism: Realism,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Degrade a true series into an observed record. Does not normalise."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float).copy()

    # 1. Proxy relationship: what was actually deposited is a monotone, saturating
    #    function of the state, not the state.
    if realism.proxy_floor > 0:
        floor = float(np.quantile(y, realism.proxy_floor))
        y = np.maximum(y, floor)
    if realism.proxy_exponent != 1.0:
        y = np.power(np.maximum(y, 1e-12), realism.proxy_exponent)

    # 2. Survival: which time points are in the record at all.
    if realism.keep_fraction < 1.0:
        n_keep = max(int(round(len(t) * realism.keep_fraction)), 4)
        if realism.irregular:
            idx = np.sort(rng.choice(len(t), size=n_keep, replace=False))
        else:
            idx = np.unique(np.linspace(0, len(t) - 1, n_keep).astype(int))
        t, y = t[idx], y[idx]

    # 3. Measurement error, on top of the process noise already in the trajectory.
    if realism.obs_noise > 0:
        y = y * np.exp(rng.normal(0.0, realism.obs_noise, size=len(y)))

    # 4. Record length: how far back the record goes.
    if realism.max_points is not None and len(t) > realism.max_points:
        t, y = t[-realism.max_points:], y[-realism.max_points:]

    return t, y
