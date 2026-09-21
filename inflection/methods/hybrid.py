"""The hybrid method of RESEARCH_PLAN §4.3: fragility for whether, drift and slowing
down for when, a type classifier for what.

Three parts share one feature set: the audit's nine physical features plus the
timing features below.

- **whether:** a calibrated classifier. In practice it learns fragility at rest.
- **what:** a calibrated seven-way classifier.
- **when:** one quantile regressor per level, trained on transitioning worlds, with
  the out-of-fold type probabilities as extra inputs. Timing behaves differently by
  type (transcritical shows before its threshold, Hopf long after), and the type
  classifier is the only place that knowledge can come from.

What the timing features can and cannot do was measured before this was built (LOG.md,
Gate 4 work). On 450 pressure-driven worlds, a flexible model on these features
predicts the *visible onset* about 15% better than the shared window alone
(16.2 against 19.0 steps). It predicts the *mechanism time* not at all (13.0 against
12.6). The information is in how far a slow change has already progressed, not in an
extrapolation of slowing down to the threshold. Extrapolating the recovery rate to
zero gave rank correlations with the true threshold time between −0.4 and +0.5 on
small subsets, which is noise.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter1d
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import StratifiedKFold

from inflection.sim.models import TRANSITION_TYPES

from .base import QUANTILE_LEVELS, Forecast, Method, Record
from .baselines import uniform_grid
from .features import _HGB, _calibrated, physical_features

N_TIMING = 13


def timing_features(record: Record) -> np.ndarray:
    """How far a slow change has progressed, and whether recovery is slowing.

    Level: overall and recent trend, curvature, and the net shift from the start of
    the record to its end, all in units of the record's own spread. Slowing down: the
    lag-1 autocorrelation and log-variance of detrended residuals, in 30-step rolling
    windows, averaged over the first, middle and last thirds, plus their changes.
    Irregular records are put on an even grid first. Records too short for this
    return zeros, which the models learn to treat as "no information".
    """
    _, g, _ = uniform_grid(record.t, record.y)
    ly = np.log(np.maximum(g, 1e-9))
    n = len(ly)
    win = min(30, n // 2)
    if n < 12 or win < 6:
        return np.zeros(N_TIMING)
    tc = np.arange(n)
    sd = ly.std() + 1e-9
    tail = min(30, n)
    level = [
        np.polyfit(tc, ly, 1)[0] * n / sd,
        np.polyfit(tc[-tail:], ly[-tail:], 1)[0] * tail / sd,
        np.polyfit(tc, ly, 2)[0] * n * n / sd,
        (ly[-10:].mean() - ly[: max(n // 3, 5)].mean()) / sd,
    ]
    r = ly - gaussian_filter1d(ly, max(n / 11, 1.0), mode="nearest")
    W = np.lib.stride_tricks.sliding_window_view(r, win)
    c = W - W.mean(axis=1, keepdims=True)
    ac = (c[:, 1:] * c[:, :-1]).sum(axis=1) / np.maximum((c ** 2).sum(axis=1), 1e-12)
    lv = np.log(np.maximum((c ** 2).mean(axis=1), 1e-12))
    thirds = [part for part in np.array_split(np.arange(len(ac)), 3) if len(part)]
    if len(thirds) < 3:
        return np.r_[level, np.zeros(N_TIMING - len(level))]
    a3 = [ac[i].mean() for i in thirds]
    v3 = [lv[i].mean() for i in thirds]
    return np.nan_to_num(np.r_[level, a3, v3, a3[2] - a3[0], v3[2] - v3[0], ac[-1]])


def hybrid_features(record: Record) -> np.ndarray:
    return np.r_[physical_features(record), timing_features(record)]


class Hybrid(Method):
    name = "hybrid"

    def fit(self, records, truths):
        X = np.array([hybrid_features(r) for r in records])
        y_whether = np.array([tr["transitioned"] for tr in truths])
        y_type = np.array([tr["transition_type"] for tr in truths])
        self.whether = _calibrated(X, y_whether)
        self.what = _calibrated(X, y_type)

        # Type probabilities as inputs to the timing model must be out-of-fold, or the
        # timing model learns from type probabilities far sharper than any it will see.
        oof = np.zeros((len(X), len(TRANSITION_TYPES)))
        folds = min(5, int(np.unique(y_type, return_counts=True)[1].min()))
        if folds >= 2:
            for tr, te in StratifiedKFold(folds, shuffle=True, random_state=0).split(X, y_type):
                oof[te] = self._type_matrix(_calibrated(X[tr], y_type[tr]), X[te])
        else:
            oof[:] = self._type_matrix(self.what, X)

        m = np.array([tr["observable_onset"] is not None for tr in truths])
        onset = np.array([tr["observable_onset"] for tr in truths if tr["observable_onset"] is not None])
        Z = np.hstack([X, oof])[m]
        self.when = [HistGradientBoostingRegressor(loss="quantile", quantile=float(q), **_HGB)
                     .fit(Z, onset) for q in QUANTILE_LEVELS]
        return self

    @staticmethod
    def _type_matrix(model, X: np.ndarray) -> np.ndarray:
        probs = model.predict_proba(X)
        classes = list(model.classes_)
        out = np.zeros((len(X), len(TRANSITION_TYPES)))
        for j, k in enumerate(TRANSITION_TYPES):
            if k in classes:
                out[:, j] = probs[:, classes.index(k)]
        return out

    def predict(self, record: Record) -> Forecast:
        x = hybrid_features(record)[None, :]
        p = float(self.whether.predict_proba(x)[0, list(self.whether.classes_).index(True)])
        types = self._type_matrix(self.what, x)
        q = np.sort([float(m.predict(np.hstack([x, types]))[0]) for m in self.when])
        return Forecast(p, tuple(q), dict(zip(TRANSITION_TYPES, types[0].tolist())))
