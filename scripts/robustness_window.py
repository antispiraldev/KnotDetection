"""Robustness check: does "timing is not forecastable beyond the window" depend on the window?

In the benchmark, every scheduled transition falls in one shared window (steps 100-150).
That makes the window prior strong, so a method can only beat it by a little. Here the
window is widened to steps 100-210 (TSTAR_WINDOW 0.33-0.70; the upper end is limited by
the run length, since an onset needs 60 steps of hold before the run ends). A
development pool is generated under that design and the timing analysis is repeated:

1. two-fold CV of base rate, feature classifier and hybrid on the clean layer
   (onset error, and error against the mechanism time);
2. the "flexible model" ceiling on the pressure-driven types, for onset and for
   mechanism time.

This is a diagnostic on development data. No test set is involved, and nothing here
changes the benchmark itself.

    PYTHONPATH=. .venv/bin/python scripts/robustness_window.py [--n 60] [--seed 303]
"""

from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold

import inflection.sim.generate as G
from inflection.eval.score import score
from inflection.methods.base import Record
from inflection.methods.baselines import BaseRate
from inflection.methods.features import FeatureClassifier
from inflection.methods.hybrid import Hybrid, hybrid_features

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inflection" / "notebooks"
WIDE = (0.33, 0.70)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=303)
    args = ap.parse_args()

    cache = OUT / f"_robust_wide_s{args.seed}_n{args.n}.pkl"
    G.TSTAR_WINDOW = WIDE                      # module constant read at generation time
    if cache.exists():
        worlds, stats = pickle.loads(cache.read_bytes())
    else:
        t0 = time.time()
        worlds, stats = G.generate_pool(n_per_type=args.n, seed=args.seed)
        cache.write_bytes(pickle.dumps((worlds, stats)))
        print(f"generated {len(worlds)} worlds in {time.time() - t0:.0f}s; failures {stats['failures']}")

    truth = [w.sealed_truth() for w in worlds]
    recs = [Record(w.world_id, *w.truncated(), w.origin, G.T) for w in worlds]
    types = np.array([w.transition_type for w in worlds])
    rng = np.random.default_rng(0)
    fold = np.zeros(len(worlds), dtype=int)
    for k in np.unique(types):
        idx = np.where(types == k)[0]; rng.shuffle(idx); fold[idx[: len(idx) // 2]] = 1

    results = {"window": WIDE, "n_worlds": len(worlds), "failures": stats["failures"]}
    for name, cls in (("base_rate", BaseRate), ("feature_classifier", FeatureClassifier),
                      ("hybrid", Hybrid)):
        fc = {}
        for k in (0, 1):
            tr = [i for i in range(len(worlds)) if fold[i] != k]
            te = [i for i in range(len(worlds)) if fold[i] == k]
            m = cls().fit([recs[i] for i in tr], [truth[i] for i in tr])
            fc.update(m.forecast_all([recs[i] for i in te]))
        s = score(fc, truth, n_boot=300)
        results[name] = {k: s[k] for k in ("auc", "mae_onset", "mae_onset_ci", "mae_mechanism",
                                           "type_accuracy") if k in s}
        print(f"{name:20s} onset MAE {s['mae_onset']:.1f} {s['mae_onset_ci']}  "
              f"mechanism MAE {s['mae_mechanism']:.1f}  AUC {s['auc']:.3f}")

    swept = [i for i, w in enumerate(worlds) if w.transition_type in ("fold", "hopf", "transcritical")]
    X = np.array([hybrid_features(recs[i]) for i in swept])
    for target in ("observable_onset", "transition_time"):
        y = np.array([truth[i][target] for i in swept], dtype=float)
        pred, prior = np.zeros(len(y)), np.zeros(len(y))
        for tr, te in KFold(5, shuffle=True, random_state=0).split(X):
            m = HistGradientBoostingRegressor(loss="absolute_error", max_depth=3, learning_rate=0.05,
                                              max_iter=300, min_samples_leaf=15).fit(X[tr], y[tr])
            pred[te] = m.predict(X[te]); prior[te] = np.median(y[tr])
        results[f"ceiling_{target}"] = dict(model=float(np.mean(abs(pred - y))),
                                            prior=float(np.mean(abs(prior - y))), n=len(y))
        print(f"ceiling on pressure-driven worlds, {target}: model {np.mean(abs(pred - y)):.1f} "
              f"vs window prior {np.mean(abs(prior - y)):.1f}  (n={len(y)})")

    (OUT / "robustness_window.json").write_text(json.dumps(results, indent=2, default=float))
    print(f"wrote {OUT / 'robustness_window.json'}")


if __name__ == "__main__":
    main()
