"""Reference methods: what any real method has to beat.

- `BaseRate` ignores the record. Its scores are the floor.
- `OwnHistory` extrapolates the record itself -- trend plus autocorrelated noise --
  and asks how often the extrapolation departs. It is the honest "no theory" method:
  it uses no labels, and no idea of what a transition is beyond a level departure.
"""

from __future__ import annotations

import zlib

import numpy as np

from inflection.sim.models import TRANSITION_TYPES

from .base import QUANTILE_LEVELS, Forecast, Method, Record


def uniform_grid(t: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Linearly interpolate an irregular record onto an even grid at its median spacing."""
    dt = float(np.median(np.diff(t))) if len(t) > 1 else 1.0
    grid = np.arange(t[0], t[-1] + 1e-9, dt)
    return grid, np.interp(grid, t, y), dt


def _logit(p: np.ndarray) -> np.ndarray:
    return np.log(p / (1 - p))


class BaseRate(Method):
    """Development-pool frequencies, whatever the record says."""

    name = "base_rate"

    def fit(self, records, truths):
        self.p = float(np.mean([tr["transitioned"] for tr in truths]))
        onsets = [tr["observable_onset"] for tr in truths if tr["observable_onset"] is not None]
        self.q = tuple(np.quantile(onsets, QUANTILE_LEVELS))
        counts = {k: 0 for k in TRANSITION_TYPES}
        for tr in truths:
            counts[tr["transition_type"]] += 1
        n = sum(counts.values())
        self.types = {k: v / n for k, v in counts.items()}
        return self

    def predict(self, record):
        return Forecast(self.p, self.q, dict(self.types))


class OwnHistory(Method):
    """Extrapolate trend + AR(1) noise forward; count how often it departs, and when.

    The departure rule is the level half of `label.observable_onset`, applied to each
    simulated continuation against the record's own median and MAD: a centred rolling
    median beyond `z` MADs for `hold` consecutive steps, with the lengths scaled to
    the record's sampling interval. The amplitude half is left out because a linear
    trend with AR(1) noise cannot grow oscillations.

    The slope is drawn from its sampling distribution, widened for autocorrelation,
    so a flat record with a noisy trend estimate does not commit to a straight line.
    Type is not addressed -- it falls back to the development base rate -- and so is
    the onset distribution when too few paths depart to estimate one.
    """

    name = "own_history"

    def __init__(self, n_paths: int = 300, z: float = 6.0, width: int = 20, hold: int = 60,
                 seed: int = 0):
        self.n_paths, self.z, self.width, self.hold = n_paths, z, width, hold
        self.seed = seed

    def fit(self, records, truths):
        """Only the fallbacks and a probability calibration are learned.

        Raw departure frequencies are badly calibrated -- a linear extrapolation over
        200 steps rarely crosses six MADs, so most transitioning worlds get p near 0
        (Brier 0.76 in development). A one-feature logistic regression on the logit
        of the raw frequency fixes the scale without adding information: it is
        monotone, so AUC is unchanged. EWS gets the same treatment.
        """
        self.fallback = BaseRate().fit(records, truths)
        self.calibration = None
        raw = np.array([self._simulate(r)[0] for r in records])
        y = [tr["transitioned"] for tr in truths]
        if 0 < sum(y) < len(y):
            from sklearn.linear_model import LogisticRegression
            self.calibration = LogisticRegression().fit(_logit(raw)[:, None], y)
        return self

    def predict(self, record: Record) -> Forecast:
        p, q = self._simulate(record)
        if self.calibration is not None:
            p = float(self.calibration.predict_proba([[_logit(np.array([p]))[0]]])[0, 1])
        return Forecast(p, q, dict(self.fallback.types))

    def _simulate(self, record: Record) -> tuple[float, tuple]:
        rng = np.random.default_rng([self.seed, zlib.crc32(record.world_id.encode())])
        grid, y, dt = uniform_grid(record.t, record.y)
        ly = np.log(np.maximum(y, 1e-9))               # multiplicative noise: work in logs
        tc = grid - grid.mean()
        X = np.column_stack([np.ones_like(tc), tc])
        beta, *_ = np.linalg.lstsq(X, ly, rcond=None)
        resid = ly - X @ beta
        phi = float(np.clip(np.corrcoef(resid[:-1], resid[1:])[0, 1], -0.95, 0.95)) \
            if len(resid) > 3 else 0.0
        sigma = float(np.std(resid)) or 1e-6
        innov = sigma * np.sqrt(1 - phi ** 2)
        n_eff = max(len(resid) * (1 - phi) / (1 + phi), 3.0)
        se_slope = sigma / np.sqrt(np.sum(tc ** 2)) * np.sqrt(len(resid) / n_eff)

        steps = np.arange(record.origin, record.horizon + 1e-9, dt)
        slopes = beta[1] + se_slope * rng.standard_normal(self.n_paths)
        trend = beta[0] + slopes[:, None] * (steps[None, :] - grid.mean())
        noise = np.empty((self.n_paths, len(steps)))
        e = np.full(self.n_paths, resid[-1])
        for i in range(len(steps)):
            e = phi * e + innov * rng.standard_normal(self.n_paths)
            noise[:, i] = e
        paths = np.exp(trend + noise)

        med = float(np.median(y))
        mad = float(np.median(np.abs(y - med))) * 1.4826 or float(np.std(y)) or 1e-9
        w = max(int(round(self.width / dt)), 3)
        h = max(int(round(self.hold / dt)), 2)
        # Prepend half a window of the record so that window j is centred on step j.
        # Windows are incomplete for the last half-window of steps and are dropped, as
        # the centred detector leaves them NaN.
        pad = w // 2
        full = np.concatenate([np.tile(y[len(y) - pad:], (self.n_paths, 1)), paths], axis=1)
        roll = np.median(np.lib.stride_tricks.sliding_window_view(full, w, axis=1), axis=2)
        hot = np.abs(roll - med) > self.z * mad
        onsets = []
        for row in hot:
            run = 0
            for j, f in enumerate(row):
                run = run + 1 if f else 0
                if run >= h:
                    onsets.append(steps[j - h + 1])
                    break
        p = len(onsets) / self.n_paths
        q = tuple(np.quantile(onsets, QUANTILE_LEVELS)) if len(onsets) >= 10 else self.fallback.q
        return float(np.clip(p, 0.5 / self.n_paths, 1 - 0.5 / self.n_paths)), q
