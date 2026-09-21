"""Development evaluation: two-fold cross-validation on a development pool, per layer.

This is where methods are built and debugged. It never touches a test set. Each
method is fitted on one half of the pool (stratified by type) and forecasts the
other half, both ways round, and the pooled forecasts are scored.

    PYTHONPATH=. .venv/bin/python scripts/dev_eval.py [--pool PATH] [--layers clean,harsh]

The default pool is the one cached by `gate2_report.py`.
"""

from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np

from inflection.eval.score import score
from inflection.methods.base import Record
from inflection.methods.baselines import BaseRate, OwnHistory
from inflection.methods.ews import GenericEWS
from inflection.methods.features import FeatureClassifier
from inflection.methods.hybrid import Hybrid
from inflection.sim import realism as R
from inflection.sim.generate import T

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inflection" / "notebooks"

METHODS = {"base_rate": BaseRate, "own_history": OwnHistory, "generic_ews": GenericEWS,
           "feature_classifier": FeatureClassifier, "hybrid": Hybrid}


def records_for(worlds, layer, seed):
    rng = np.random.default_rng(seed)
    recs = []
    for w in worlds:
        t, y = w.record(layer, rng)
        recs.append(Record(w.world_id, t, y, w.origin, T))
    return recs


def two_fold(worlds, seed=0):
    rng = np.random.default_rng(seed)
    fold = np.zeros(len(worlds), dtype=int)
    types = np.array([w.transition_type for w in worlds])
    for k in np.unique(types):
        idx = np.where(types == k)[0]
        rng.shuffle(idx)
        fold[idx[: len(idx) // 2]] = 1
    return fold


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=str(OUT / "_pool_cache.pkl"))
    ap.add_argument("--layers", default=",".join(R.LAYERS))
    ap.add_argument("--methods", default=",".join(METHODS))
    args = ap.parse_args()

    worlds, _ = pickle.loads(Path(args.pool).read_bytes())
    truth = [w.sealed_truth() for w in worlds]
    fold = two_fold(worlds)
    results = {}
    for li, layer_name in enumerate(args.layers.split(",")):
        recs = records_for(worlds, R.LAYERS[layer_name], seed=1000 + li)
        for mname in args.methods.split(","):
            t0 = time.time()
            fc = {}
            for k in (0, 1):
                tr = [i for i in range(len(worlds)) if fold[i] != k]
                te = [i for i in range(len(worlds)) if fold[i] == k]
                m = METHODS[mname]().fit([recs[i] for i in tr], [truth[i] for i in tr])
                fc.update(m.forecast_all([recs[i] for i in te]))
            s = score(fc, truth, n_boot=200)
            results[f"{layer_name}/{mname}"] = s
            print(f"{layer_name:18s} {mname:12s} brier {s['brier']:.3f} skill {s['brier_skill']:+.3f} "
                  f"auc {s['auc']:.3f} nullFPR {s['null_fpr']:.2f} | crps {s['crps_onset']:5.1f} "
                  f"mae {s['mae_onset']:5.1f} cov90 {s['cover90_onset']:.2f} | "
                  f"type {s['type_accuracy']:.3f} mech {s['type_accuracy_mechanism_change']:.2f} "
                  f"({time.time() - t0:.0f}s)", flush=True)
    (OUT / "dev_eval.json").write_text(json.dumps(results, indent=2))
    print(f"wrote {OUT / 'dev_eval.json'}")


if __name__ == "__main__":
    main()
