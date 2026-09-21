"""Gate 2 evidence: example trajectories, and the leakage audit under each realism layer.

Run from the repo root:

    PYTHONPATH=. .venv/bin/python scripts/gate2_report.py [--fresh] [--n 25]

Writes figures to `inflection/notebooks/` and the audit table to stdout and to
`inflection/notebooks/gate2_audit.json`. The generated pool is cached so the audit
can be re-run without paying for integration again.
"""

from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from inflection.sim import models, realism as R
from inflection.sim.generate import generate_pool, ORIGIN_FRAC, T
from inflection.eval import leakage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inflection" / "notebooks"
CACHE = OUT / "_pool_cache.pkl"


def get_pool(n_per_type: int, seed: int, fresh: bool):
    if CACHE.exists() and not fresh:
        worlds, stats = pickle.loads(CACHE.read_bytes())
        if stats["n_requested"] == n_per_type * len(models.TRANSITION_TYPES):
            print(f"using cached pool: {len(worlds)} worlds")
            return worlds, stats
    t0 = time.time()
    worlds, stats = generate_pool(n_per_type=n_per_type, seed=seed)
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.write_bytes(pickle.dumps((worlds, stats)))
    print(f"generated {stats['n_generated']}/{stats['n_requested']} in {time.time() - t0:.0f}s")
    print("  per type: mean attempts per accepted world, and worlds that failed outright")
    for k, v in sorted(stats["mean_attempts"].items(), key=lambda kv: -kv[1]):
        # Failures matter as much as attempts: design variables are fixed before the
        # rejection loop, so a type that often exhausts its attempts at some target
        # CV is dropping those targets from the pool -- selection by another route.
        print(f"    {k:18s} {v:5.1f}   failed {stats['failures'][k]}")
    return worlds, stats


def figure_examples(worlds, path: Path) -> None:
    """One representative world per type, with the origin and both timestamps marked."""
    types = models.TRANSITION_TYPES
    fig, axes = plt.subplots(len(types), 1, figsize=(9, 2.0 * len(types)), sharex=True)
    origin = ORIGIN_FRAC * T

    for ax, tt in zip(axes, types):
        pick = next((w for w in worlds if w.transition_type == tt), None)
        if pick is None:
            ax.set_visible(False)
            continue
        y = pick.raw / np.median(pick.raw[pick.t < origin])
        ax.plot(pick.t, y, lw=0.8, color="#333333")
        ax.axvspan(0, origin, color="#4C78A8", alpha=0.10)
        ax.axvline(origin, color="#4C78A8", lw=1.0, ls="--")
        if pick.transition_time is not None:
            ax.axvline(pick.transition_time, color="#D62728", lw=1.2)
        if pick.observable_onset is not None:
            ax.axvline(pick.observable_onset, color="#F58518", lw=1.2, ls=":")
        lag = pick.onset_lag
        lag_txt = "" if lag is None else f"  lag {lag:+.0f}"
        ax.set_ylabel(tt.replace("_", "\n"), fontsize=8)
        ax.set_title(
            f"{tt}{lag_txt}", fontsize=9, loc="left",
        )
        ax.tick_params(labelsize=8)

    axes[-1].set_xlabel("time")
    fig.suptitle(
        "One world per transition type  —  shaded: record given to methods   "
        "dashed: forecast origin   red: mechanism change   dotted orange: visible onset",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print(f"wrote {path}")


def figure_onset_lag(worlds, path: Path) -> None:
    """How long after the mechanism changes does anything become visible?"""
    fig, ax = plt.subplots(figsize=(8, 4))
    types = [t for t in models.TRANSITION_TYPES if t != "null"]
    data, labels = [], []
    for tt in types:
        lags = [w.onset_lag for w in worlds
                if w.transition_type == tt and w.onset_lag is not None]
        if lags:
            data.append(lags)
            labels.append(f"{tt}\n(n={len(lags)})")
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.axhline(0, color="#D62728", lw=1.0, ls="--")
    ax.set_ylabel("observable onset − mechanism change")
    ax.set_title("Bifurcation delay: the gap a 'when' score would otherwise charge to the method")
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print(f"wrote {path}")


def audit_across_layers(worlds, seed: int, n_perm: int = 30) -> dict:
    results = {}
    for name, layer in R.LAYERS.items():
        rng = np.random.default_rng(seed)
        X, y = [], []
        for w in worlds:
            t, s = w.record(layer, rng)
            X.append(leakage.features(t, s))
            y.append(w.transition_type)
        X, y = np.array(X), np.array(y)
        classes, counts = np.unique(y, return_counts=True)
        base = float(counts.max() / counts.sum())
        stat, _ = leakage._accuracy(X, y, leakage.STATIC_FEATURES, 5, seed)
        null = leakage.permutation_null(X, y, leakage.STATIC_FEATURES, n_perm, 5, seed)
        p = float((np.sum(null >= stat) + 1) / (n_perm + 1))
        phys, _ = leakage._accuracy(X, y, leakage.TEMPORAL_FEATURES, 5, seed)
        comb, recall = leakage._accuracy(X, y, leakage.FEATURE_NAMES, 5, seed)
        results[name] = dict(
            base_rate=base,
            scale_dependent=stat, scale_dependent_null=float(null.mean()), scale_dependent_p=p,
            physical=phys, combined=comb, per_type_recall=recall,
            leak=bool(p < 0.05 and stat - null.mean() > 0.05),
        )
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--n", type=int, default=25, help="worlds per transition type")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    worlds, stats = get_pool(args.n, args.seed, args.fresh)

    figure_examples(worlds, OUT / "gate2_examples.png")
    figure_onset_lag(worlds, OUT / "gate2_onset_lag.png")

    print()
    print(leakage.report(leakage.audit(worlds)))

    print()
    print("=== cheap-classifier accuracy under each realism layer ===")
    print(f"{'layer':20s} {'scale-dep':>10s} {'(chance)':>9s} {'p':>6s} "
          f"{'physical':>10s} {'combined':>10s}")
    results = audit_across_layers(worlds, args.seed)
    for name, r in results.items():
        flag = "  <-- LEAK" if r["leak"] else ""
        print(f"{name:20s} {r['scale_dependent']:10.3f} {r['scale_dependent_null']:9.3f} "
              f"{r['scale_dependent_p']:6.3f} {r['physical']:10.3f} {r['combined']:10.3f}{flag}")
    print(f"\n(base rate {results['clean']['base_rate']:.3f}; "
          "'combined' is the difficulty floor a real method must beat)")

    (OUT / "gate2_audit.json").write_text(json.dumps(
        dict(generation=stats, layers=results), indent=2, sort_keys=True, default=float))
    print(f"wrote {OUT / 'gate2_audit.json'}")


if __name__ == "__main__":
    main()
