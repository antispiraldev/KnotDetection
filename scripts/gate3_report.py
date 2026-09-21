"""Tables and a figure from the blind Gate 3 scores.

    PYTHONPATH=. .venv/bin/python scripts/gate3_report.py --test-set test_v1

Reads `inflection/notebooks/gate3_scores_<test_set>.json` (written by
`gate3_run.py score`), prints one table per sub-question with bootstrap intervals,
and writes `gate3_summary.png`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from inflection.sim import realism as R

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inflection" / "notebooks"
METHODS = ("base_rate", "own_history", "generic_ews", "feature_classifier", "hybrid")


def fmt(s: dict, key: str, digits: int = 3) -> str:
    v = s.get(key)
    if v is None or not np.isfinite(v):
        return "–"
    ci = s.get(f"{key}_ci")
    body = f"{v:.{digits}f}"
    return f"{body} [{ci[0]:.{digits}f}, {ci[1]:.{digits}f}]" if ci else body


def table(scores: dict, title: str, keys: list[tuple[str, str, int]]) -> str:
    lines = [f"\n### {title}\n", "| layer | method | " + " | ".join(k[1] for k in keys) + " |",
             "|---|---|" + "---|" * len(keys)]
    for layer in R.LAYERS:
        for m in METHODS:
            s = scores.get(f"{m}__{layer}")
            if s is None:
                continue
            lines.append(f"| {layer} | {m} | " + " | ".join(fmt(s, k, d) for k, _, d in keys) + " |")
    return "\n".join(lines)


def breakdown(scores: dict, layer: str) -> str:
    """Per-type means on one layer: where each method's skill comes from."""
    from inflection.sim.models import TRANSITION_TYPES
    cols = [f"mean_p_{k}" for k in TRANSITION_TYPES] + ["mean_p_shock_robust", "mean_p_shock_fragile"]
    names = [k.replace("_", " ") for k in TRANSITION_TYPES] + ["shock: robust", "shock: fragile"]
    lines = [f"\n### Mean p(transition) by type, {layer}\n", "| method | " + " | ".join(names) + " |",
             "|---|" + "---|" * len(cols)]
    for m in METHODS:
        s = scores.get(f"{m}__{layer}", {})
        lines.append(f"| {m} | " + " | ".join(f"{s[c]:.2f}" if c in s else "–" for c in cols) + " |")
    kinds = [k for k in TRANSITION_TYPES if k != "null"]
    lines += [f"\n### Onset MAE by type, {layer}\n", "| method | " + " | ".join(k.replace("_", " ") for k in kinds) + " |",
              "|---|" + "---|" * len(kinds)]
    for m in METHODS:
        s = scores.get(f"{m}__{layer}", {})
        lines.append(f"| {m} | " + " | ".join(f"{s[f'mae_onset_{k}']:.1f}" if f"mae_onset_{k}" in s else "–" for k in kinds) + " |")
    return "\n".join(lines)


def figure(scores: dict, path: Path) -> None:
    panels = [("auc", "whether: AUC", 0.5), ("mae_onset", "when: onset MAE", None),
              ("type_accuracy", "what: type accuracy (excl. mech. change)", 1 / 6)]
    layers = list(R.LAYERS)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    width = 0.8 / len(METHODS)
    for ax, (key, title, chance) in zip(axes, panels):
        for i, m in enumerate(METHODS):
            vals, lo, hi = [], [], []
            for layer in layers:
                s = scores.get(f"{m}__{layer}", {})
                v = s.get(key, np.nan)
                ci = s.get(f"{key}_ci", [v, v])
                vals.append(v); lo.append(v - ci[0]); hi.append(ci[1] - v)
            x = np.arange(len(layers)) + (i - (len(METHODS) - 1) / 2) * width
            ax.bar(x, vals, width, yerr=[lo, hi], capsize=2, label=m)
        if chance is not None:
            ax.axhline(chance, color="#555", lw=1, ls="--")
        ax.set_xticks(np.arange(len(layers)))
        ax.set_xticklabels(layers, rotation=35, ha="right", fontsize=8)
        ax.set_title(title, fontsize=10)
    axes[0].legend(fontsize=8)
    fig.suptitle("Gate 3, blind test set: each method by realism layer (95% bootstrap intervals)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print(f"wrote {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-set", required=True)
    args = ap.parse_args()
    scores = json.loads((OUT / f"gate3_scores_{args.test_set}.json").read_text())

    out = [f"# Gate 3 scores: {args.test_set}"]
    out.append(table(scores, "Whether", [("brier_skill", "Brier skill", 3), ("auc", "AUC", 3),
                                          ("null_fpr", "null FPR @80% TPR", 2)]))
    out.append(table(scores, "When (transitioning worlds)", [
        ("mae_onset", "onset MAE", 1), ("crps_onset", "onset CRPS", 1),
        ("mae_mechanism", "mechanism-time MAE", 1), ("cover90_onset", "90% coverage", 2)]))
    out.append(table(scores, "What", [
        ("type_accuracy", "accuracy (excl. mech.)", 3),
        ("type_accuracy_mechanism_change", "mech. change", 2), ("type_logloss", "log loss", 2)]))
    out.append(breakdown(scores, "clean"))
    text = "\n".join(out)
    print(text)
    (OUT / f"gate3_tables_{args.test_set}.md").write_text(text + "\n")
    figure(scores, OUT / "gate3_summary.png")


if __name__ == "__main__":
    main()
