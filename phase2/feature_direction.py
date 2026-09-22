"""Which record features predict a transition, in real data and in simulation?

Single-feature AUCs on the `real_v2` development half (labels are public there) and on
the simulator's development pool, using the same nine features and the same record
length. Writes `phase2/results/feature_direction.json`. This is the diagnostic behind
the negative transfer in `real_v2`: the two domains disagree about what a warning sign
looks like.

    PYTHONPATH=. .venv/bin/python phase2/feature_direction.py
"""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phase2"))

import run_real as R                                              # noqa: E402
from inflection.eval.leakage import TEMPORAL_FEATURES             # noqa: E402
from inflection.methods.base import Record                        # noqa: E402
from inflection.methods.features import physical_features         # noqa: E402
from inflection.sim.generate import T                             # noqa: E402
from inflection.sim.realism import Realism                        # noqa: E402


def main() -> None:
    R.use_test_set("real_v2")
    recs, y, _ = R.load_dev()
    Xr = np.nan_to_num(np.array([physical_features(r) for r in recs]))

    worlds, _ = pickle.loads((ROOT / "inflection" / "notebooks" / "_dev_pool_s102_n100.pkl").read_bytes())
    rng = np.random.default_rng(7)
    layer = Realism(keep_fraction=R.n_points() / 90.0)
    sim = [Record(w.world_id, *w.record(layer, rng), w.origin, T) for w in worlds]
    Xs = np.nan_to_num(np.array([physical_features(r) for r in sim]))
    ys = np.array([w.transitioned for w in worlds])

    out = {}
    for i, k in enumerate(TEMPORAL_FEATURES):
        out[k] = dict(real=float(roc_auc_score(y, Xr[:, i])),
                      simulated=float(roc_auc_score(ys, Xs[:, i])))
        print(f"{k:14s} real {out[k]['real']:.3f}   simulated {out[k]['simulated']:.3f}")
    dest = ROOT / "phase2" / "results" / "feature_direction.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
