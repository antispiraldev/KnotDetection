"""Leakage audit: can the transition type be read off the pre-transition window?

This is a gate on the *simulator*, not a forecasting method. The benchmark's claim
is that naming the mechanism is hard. That claim is empty if each type also carries
an incidental signature -- its own band of levels, its own noise amplitude, its own
series length -- because then a classifier can name the type from data recorded
before anything has happened, and a good score on sub-question 3 measures nothing
but familiarity with the simulator.

The audit fits a deliberately cheap classifier to summary statistics of the
truncated series and compares its cross-validated accuracy to the base rate. Cheap
is the point: these features encode no dynamics, so any accuracy above chance is a
fingerprint rather than a finding.

A first draft of the simulator scored 1.00 on a single feature for one type. See
LOG.md, 2026-09-21.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict

FEATURE_NAMES = (
    # static -- where the series sits and how much it wobbles
    "median",
    "log_median",
    "sd",
    "iqr",
    "mad",
    "cv",
    "log_step_sd",
    "lag1_ac",
    "skew",
    "kurtosis",
    "n_points",
    # temporal -- how those quantities move across the window
    "slope_norm",         # linear trend in level
    "var_ratio",          # late-half variance / early-half variance
    "lag1_delta",         # late-half lag-1 autocorrelation minus early-half
    "cv_ratio",           # late-half cv / early-half cv
)

# Not every informative feature is a leak, and conflating the two would gut the
# experiment. Rising autocorrelation before a fold is critical slowing down -- the
# phenomenon under study. If the audit demanded that it carry no information about
# type, the only way to pass would be to build a simulator in which early-warning
# signals do not work, and the benchmark would answer its own question in advance.
#
# The line falls where the early-warning literature puts it. Critical slowing down
# is a statement about *change*: variance and autocorrelation that rise as the
# system approaches its threshold. It is not a statement about their level. How
# much a series wobbles in absolute terms is set by the ratio of forcing to damping
# in whichever equations were written down -- a property of the model family, not
# of any society. A real record arrives with no canonical wobble to compare against.
#
# The gate is therefore set where a guarantee is actually available rather than
# where the argument is merely persuasive.
#
# SCALE-DEPENDENT -- level, spread, record length: quantities that change if the
#            series is multiplied by a constant or recorded in different units.
#            These carry no information about a mechanism, and normalising the
#            delivered series by its pre-origin median makes them degenerate by
#            construction. Gated, and the gate is structural: it cannot quietly
#            drift back to informative the way a tuned parameter range can.
# PHYSICAL -- relative spread, relaxation, asymmetry, and how all of those move
#            across the window. Informative when the dynamics make them so, which is
#            the phenomenon under study. Measured and reported, never gated.
#
# Relative spread (`cv`) sits on the physical side but is calibrated to a common
# target in the generator, because its level was a model-family artifact rather than
# a fact about proximity to a threshold. The audit reports it; the generator stops it
# from being a giveaway.
STATIC_FEATURES = ("median", "log_median", "sd", "iqr", "mad", "n_points")
TEMPORAL_FEATURES = (
    "cv", "log_step_sd", "lag1_ac", "skew", "kurtosis",
    "slope_norm", "var_ratio", "lag1_delta", "cv_ratio",
)


def _detrended_lag1(t: np.ndarray, y: np.ndarray) -> float:
    """Lag-1 autocorrelation after removing a linear trend, which would dominate it."""
    if len(y) < 4:
        return 0.0
    resid = y - np.polyval(np.polyfit(t, y, 1), t)
    denom = float(np.sum(resid * resid))
    return float(np.sum(resid[1:] * resid[:-1]) / denom) if denom > 0 else 0.0


def _cv(y: np.ndarray) -> float:
    med = float(np.median(y))
    return float(np.std(y)) / max(abs(med), 1e-12)


def features(t: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Cheap summary statistics of one truncated series."""
    y = np.asarray(y, dtype=float)
    t = np.asarray(t, dtype=float)
    med = float(np.median(y))
    sd = float(np.std(y))
    q75, q25 = np.percentile(y, [75, 25])
    mad = float(np.median(np.abs(y - med)))

    with np.errstate(divide="ignore", invalid="ignore"):
        logy = np.log(np.maximum(y, 1e-12))
        step_sd = float(np.std(np.diff(logy)))

    lag1 = _detrended_lag1(t, y)
    coef = np.polyfit(t, y, 1)

    c = y - y.mean()
    s = y.std() or 1e-12
    skew = float(np.mean(c ** 3) / s ** 3)
    kurt = float(np.mean(c ** 4) / s ** 4)

    # Split the window to turn each static quantity into a change.
    half = len(y) // 2
    early_t, early_y = t[:half], y[:half]
    late_t, late_y = t[half:], y[half:]
    e_res = early_y - np.polyval(np.polyfit(early_t, early_y, 1), early_t)
    l_res = late_y - np.polyval(np.polyfit(late_t, late_y, 1), late_t)
    var_ratio = float(np.var(l_res) / max(np.var(e_res), 1e-18))
    lag1_delta = _detrended_lag1(late_t, late_y) - _detrended_lag1(early_t, early_y)
    cv_ratio = _cv(late_y) / max(_cv(early_y), 1e-12)

    return np.array([
        med,
        float(np.log(max(med, 1e-12))),
        sd,
        float(q75 - q25),
        mad,
        sd / max(abs(med), 1e-12),
        step_sd,
        lag1,
        skew,
        kurt,
        float(len(y)),
        coef[0] / max(abs(med), 1e-12),
        float(np.log(max(var_ratio, 1e-12))),
        lag1_delta,
        float(np.log(max(cv_ratio, 1e-12))),
    ])


def build_matrix(worlds) -> tuple[np.ndarray, np.ndarray]:
    X, labels = [], []
    for w in worlds:
        t, y = w.truncated()
        X.append(features(t, y))
        labels.append(w.transition_type)
    return np.array(X), np.array(labels)


def _accuracy(X: np.ndarray, y: np.ndarray, cols, n_splits: int, seed: int) -> tuple[float, dict]:
    if not cols:
        return float("nan"), {}
    idx = [FEATURE_NAMES.index(c) for c in cols]
    Xs = X[:, idx]
    if np.allclose(Xs.std(axis=0), 0):
        classes, counts = np.unique(y, return_counts=True)
        return float(counts.max() / counts.sum()), {c: 0.0 for c in classes}
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    clf = HistGradientBoostingClassifier(max_iter=200, random_state=seed)
    pred = cross_val_predict(clf, Xs, y, cv=cv)
    recall = {c: float((pred[y == c] == c).mean()) for c in np.unique(y)}
    return float((pred == y).mean()), recall


def _single_feature_aucs(X: np.ndarray, y: np.ndarray, cols) -> list[tuple[float, str, str]]:
    out = []
    for c in np.unique(y):
        mask = y == c
        for name in cols:
            j = FEATURE_NAMES.index(name)
            if np.std(X[:, j]) == 0:
                continue
            a, b = X[mask, j], X[~mask, j]
            # Rank-based separability: P(feature higher for this type) -> AUC.
            order = np.argsort(np.concatenate([a, b]))
            ranks = np.empty(len(order), dtype=float)
            ranks[order] = np.arange(len(order))
            auc = (ranks[:len(a)].mean() - (len(a) - 1) / 2) / len(b)
            out.append((abs(auc - 0.5) + 0.5, c, name))
    out.sort(reverse=True)
    return out


def audit(worlds, n_splits: int = 5, seed: int = 0) -> dict:
    """Two-tier audit: static leakage is gated, temporal signal is measured."""
    X, y = build_matrix(worlds)
    classes, counts = np.unique(y, return_counts=True)
    base_rate = float(counts.max() / counts.sum())

    stat_acc, stat_recall = _accuracy(X, y, STATIC_FEATURES, n_splits, seed)
    temp_acc, temp_recall = _accuracy(X, y, TEMPORAL_FEATURES, n_splits, seed)
    all_acc, _ = _accuracy(X, y, FEATURE_NAMES, n_splits, seed)

    return dict(
        n=len(y),
        base_rate=base_rate,
        static_accuracy=stat_acc,
        static_excess=stat_acc - base_rate,
        static_recall=stat_recall,
        temporal_accuracy=temp_acc,
        temporal_excess=temp_acc - base_rate,
        temporal_recall=temp_recall,
        combined_accuracy=all_acc,
        top_static_auc=[
            dict(auc=round(a, 3), transition_type=c, feature=f)
            for a, c, f in _single_feature_aucs(X, y, STATIC_FEATURES)[:5]
        ],
        top_temporal_auc=[
            dict(auc=round(a, 3), transition_type=c, feature=f)
            for a, c, f in _single_feature_aucs(X, y, TEMPORAL_FEATURES)[:5]
        ],
    )


def report(result: dict, threshold: float = 0.05) -> str:
    lines = [
        f"leakage audit on {result['n']} worlds (base rate {result['base_rate']:.3f})",
        "",
        "  GATED -- scale-dependent features (level, spread, record length):",
        f"    accuracy {result['static_accuracy']:.3f}   excess {result['static_excess']:+.3f}",
    ]
    for d in result["top_static_auc"]:
        lines.append(f"      {d['transition_type']:18s} {d['feature']:14s} auc={d['auc']:.3f}")

    lines += [
        "",
        "  MEASURED -- physical features (relative spread, relaxation, trends):",
        f"    accuracy {result['temporal_accuracy']:.3f}   excess {result['temporal_excess']:+.3f}",
        "    (above base rate here is the phenomenon under study, not a defect)",
    ]
    for d in result["top_temporal_auc"]:
        lines.append(f"      {d['transition_type']:18s} {d['feature']:14s} auc={d['auc']:.3f}")

    verdict = "PASS" if result["static_excess"] <= threshold else "FAIL"
    lines += [
        "",
        f"  combined accuracy: {result['combined_accuracy']:.3f}",
        f"  verdict: {verdict} (gate: scale-dependent excess <= {threshold:.2f})",
    ]
    return "\n".join(lines)
