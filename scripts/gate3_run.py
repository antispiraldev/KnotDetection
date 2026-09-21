"""Gate 3 pipeline: seed -> test pool -> forecasts (hashed) -> unseal -> scores.

Each step is a separate invocation so the ledger shows them as separate events, and
each refuses to run out of order (see `inflection.eval.blind`).

    PYTHONPATH=. .venv/bin/python scripts/gate3_run.py commit-seed --test-set test_v1
    PYTHONPATH=. .venv/bin/python scripts/gate3_run.py build      --test-set test_v1 --n 40
    PYTHONPATH=. .venv/bin/python scripts/gate3_run.py forecast   --test-set test_v1
    PYTHONPATH=. .venv/bin/python scripts/gate3_run.py score      --test-set test_v1

Methods are fitted on a development pool generated from a public seed, separately
for each realism layer (a method may know what kind of record it is looking at). The
test records are read from disk exactly as the build step wrote them.
"""

from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np

from inflection.eval import blind
from inflection.eval.score import score_blind
from inflection.methods.base import Record
from inflection.sim import realism as R
from inflection.sim.generate import T, generate_pool

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "inflection" / "data"
NOTEBOOKS = ROOT / "inflection" / "notebooks"
DEV_SEED = 101


def methods():
    from inflection.methods.baselines import BaseRate, OwnHistory
    from inflection.methods.ews import GenericEWS
    return {"base_rate": BaseRate, "own_history": OwnHistory, "generic_ews": GenericEWS}


def dev_pool(n_per_type: int):
    cache = NOTEBOOKS / f"_dev_pool_s{DEV_SEED}_n{n_per_type}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    t0 = time.time()
    worlds, stats = generate_pool(n_per_type=n_per_type, seed=DEV_SEED)
    cache.write_bytes(pickle.dumps((worlds, stats)))
    print(f"dev pool: {len(worlds)} worlds in {time.time() - t0:.0f}s")
    return worlds, stats


def test_records(test_set: str, layer: str) -> list[Record]:
    d = DATA / test_set / layer
    manifest = json.loads((d / "manifest.json").read_text())
    z = np.load(d / "series.npz")
    return [Record(wid, z[f"t_{wid}"], z[wid], manifest["origins"][wid], T)
            for wid in manifest["world_ids"]]


def cmd_forecast(args):
    worlds, _ = dev_pool(args.dev_n)
    truth = [w.sealed_truth() for w in worlds]
    out = DATA / "forecasts" / args.test_set
    out.mkdir(parents=True, exist_ok=True)
    for li, (layer_name, layer) in enumerate(R.LAYERS.items()):
        rng = np.random.default_rng(DEV_SEED + 1 + li)
        dev = []
        for w in worlds:
            t, y = w.record(layer, rng)
            dev.append(Record(w.world_id, t, y, w.origin, T))
        recs = test_records(args.test_set, layer_name)
        for name, cls in methods().items():
            fc = cls().fit(dev, truth).forecast_all(recs)
            path = out / f"{name}__{layer_name}.json"
            path.write_text(json.dumps(fc, sort_keys=True))
            digest = blind.register_forecasts(path, args.test_set, f"{name}/{layer_name}")
            print(f"registered {path.name}  {digest[:12]}")


def cmd_score(args):
    out = DATA / "forecasts" / args.test_set
    results = {}
    for path in sorted(out.glob("*.json")):
        results[path.stem] = score_blind(path, args.test_set)
    dest = NOTEBOOKS / f"gate3_scores_{args.test_set}.json"
    dest.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {dest}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["commit-seed", "build", "forecast", "score"])
    ap.add_argument("--test-set", required=True)
    ap.add_argument("--n", type=int, default=40, help="test worlds per type")
    ap.add_argument("--dev-n", type=int, default=40, help="development worlds per type")
    args = ap.parse_args()

    if args.step == "commit-seed":
        print("seed committed:", blind.commit_test_seed(args.test_set))
    elif args.step == "build":
        print(blind.build_test_pool(args.test_set, args.n))
    elif args.step == "forecast":
        cmd_forecast(args)
    else:
        cmd_score(args)


if __name__ == "__main__":
    main()
