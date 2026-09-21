"""A supervised classifier on cheap physical summary features.

The nine features the leakage audit calls *physical* -- relative spread, step
variability, lag-1 autocorrelation, shape, trend, and first-half/second-half changes
in variance and autocorrelation (`eval.leakage.TEMPORAL_FEATURES`) -- fed to gradient
boosting trained on the development pool:

- whether: a binary classifier;
- what: a seven-way classifier;
- when: one quantile regressor per level, fitted on the transitioning worlds, with
  crossings removed by sorting.

The scale-dependent features are left out on purpose. The simulator is built so they
carry nothing, and the audit shows they carry at most a little. A method that used
them would be exploiting whatever residue remains, not detecting anything.

This is the obvious machine-learning approach, and it is here to show what such an
approach gets from these records with no theory at all. It is the floor for the
deep-learning classifier and the hybrid in RESEARCH_PLAN §4.3.
"""

from __future__ import annotations

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from inflection.eval.leakage import FEATURE_NAMES, TEMPORAL_FEATURES, features
from inflection.sim.models import TRANSITION_TYPES

from .base import QUANTILE_LEVELS, Forecast, Method, Record

_COLS = [FEATURE_NAMES.index(c) for c in TEMPORAL_FEATURES]
_HGB = dict(max_depth=3, learning_rate=0.05, max_iter=200, l2_regularization=1.0,
            min_samples_leaf=10, random_state=0)


def physical_features(record: Record) -> np.ndarray:
    return np.nan_to_num(features(record.t, record.y)[_COLS])


def _calibrated(X: np.ndarray, y: np.ndarray):
    """Sigmoid-calibrated boosting, with as many folds as the rarest class allows."""
    folds = min(5, int(np.unique(y, return_counts=True)[1].min()))
    if folds < 2:
        return HistGradientBoostingClassifier(**_HGB).fit(X, y)
    return CalibratedClassifierCV(HistGradientBoostingClassifier(**_HGB),
                                  method="sigmoid", cv=folds).fit(X, y)


class FeatureClassifier(Method):
    name = "feature_classifier"

    def fit(self, records, truths):
        X = np.array([physical_features(r) for r in records])
        y_whether = np.array([tr["transitioned"] for tr in truths])
        y_type = np.array([tr["transition_type"] for tr in truths])
        # Boosted trees on ~140 worlds are overconfident (Brier skill -0.15 in
        # development despite AUC 0.76), so both classifiers are sigmoid-calibrated
        # by internal cross-validation. That averages fold models, so ranking moves
        # slightly (AUC 0.759 -> 0.750); the probability scale is fixed (skill +0.055).
        self.whether = _calibrated(X, y_whether)
        self.what = _calibrated(X, y_type)
        m = np.array([tr["observable_onset"] is not None for tr in truths])
        onset = np.array([tr["observable_onset"] for tr in truths if tr["observable_onset"] is not None])
        self.when = [HistGradientBoostingRegressor(loss="quantile", quantile=float(q), **_HGB)
                     .fit(X[m], onset) for q in QUANTILE_LEVELS]
        return self

    def predict(self, record: Record) -> Forecast:
        x = physical_features(record)[None, :]
        p = float(self.whether.predict_proba(x)[0, list(self.whether.classes_).index(True)])
        probs = dict(zip(self.what.classes_, self.what.predict_proba(x)[0].tolist()))
        q = np.sort([float(m.predict(x)[0]) for m in self.when])
        return Forecast(p, tuple(q), {k: probs.get(k, 0.0) for k in TRANSITION_TYPES})
