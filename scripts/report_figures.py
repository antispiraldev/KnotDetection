"""Figures for the final write-up, built from the scores the blind tests produced.

Every number is read from the result files, so the figures cannot drift from the
tables: `inflection/notebooks/gate3_scores_test_v2.json` (simulation),
`phase2/results/test_scores_real_v1.json` and `..._real_v2.json` (real data), and
`inflection/notebooks/robustness_window.json`.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "inflection" / "notebooks"
RES = ROOT / "phase2" / "results"

INK, MUTED, ACCENT, WARN, GOOD = "#222222", "#8a8a8a", "#2f6fb0", "#c8553d", "#3a8a5c"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": "#555555", "axes.titleweight": "bold",
    "axes.titlesize": 11,
})


def _load(path: Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def fig_simulation(path: Path) -> None:
    """What the simulated benchmark showed, by data quality."""
    s = _load(NB / "gate3_scores_test_v2.json")
    layers = [("clean", "clean"), ("observation_noise", "noisy"), ("sparse", "sparse"),
              ("irregular", "irregular"), ("short", "short"), ("harsh", "harsh"),
              ("lead_30", "30 steps\nearlier")]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2))
    for ax, (key, title, floor) in zip(axes, [
            ("auc", "WHETHER (ranking score)", 0.5),
            ("type_accuracy", "WHAT (share correct)", 1 / 6),
            ("mae_onset", "WHEN (error, steps)", None)]):
        hyb = [s[f"hybrid__{k}"][key] for k, _ in layers]
        ews = [s[f"generic_ews__{k}"][key] for k, _ in layers]
        base = [s[f"base_rate__{k}"][key] for k, _ in layers]
        x = np.arange(len(layers))
        ax.bar(x - 0.22, hyb, 0.42, label="best method", color=GOOD)
        ax.bar(x + 0.22, ews, 0.42, label="early-warning signals", color=MUTED)
        if key == "mae_onset":
            ax.plot(x, base, "o--", color=WARN, ms=5, label="knowing the window")
            ax.set_ylim(0, 25)
        elif floor is not None:
            ax.axhline(floor, color=INK, ls="--", lw=1)
            ax.set_ylim(0.3 if key == "auc" else 0, 0.9 if key == "auc" else 0.6)
        ax.set_xticks(x); ax.set_xticklabels([n for _, n in layers], fontsize=7.5, rotation=30,
                                             ha="right")
        ax.set_title(title, fontsize=10)
    axes[0].legend(fontsize=7.5, loc="upper right")
    fig.suptitle("Simulated societies: 420 worlds, blind test", fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_real(path: Path) -> None:
    """Simulation against the two real tests, for the methods they share."""
    sim = _load(NB / "gate3_scores_test_v2.json")
    v1, v2 = _load(RES / "test_scores_real_v1.json"), _load(RES / "test_scores_real_v2.json")
    rows = [("trained on simulation", sim["feature_classifier__sparse"]["auc"],
             v1["M3_feature_clf_sim"]["auc"], (v2 or {}).get("M3_feature_clf_sim", {}).get("auc")),
            ("early-warning signals", sim["generic_ews__sparse"]["auc"],
             v1["M2_generic_ews"]["auc"], (v2 or {}).get("M2_generic_ews", {}).get("auc")),
            ("fragility at rest", sim["hybrid__sparse"]["auc"],
             v1["M6_fragility"]["auc"], (v2 or {}).get("M6_fragility", {}).get("auc")),
            ("fitted to the data", sim["feature_classifier__sparse"]["auc"],
             v1["M5_feature_clf_real"]["auc"], (v2 or {}).get("M5_feature_clf_real", {}).get("auc"))]
    labels = ["simulated\nsocieties", "real: territory\n(Cliopatria)", "real: income\n(Maddison)"]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    width = 0.8 / len(rows)
    for i, (name, *vals) in enumerate(rows):
        vals = [np.nan if v is None else v for v in vals]
        ax.bar(np.arange(3) + (i - (len(rows) - 1) / 2) * width, vals, width, label=name)
    ax.axhline(0.5, color=INK, ls="--", lw=1)
    ax.text(2.55, 0.505, "coin flip", fontsize=8, va="bottom", ha="right")
    ax.set_xticks(np.arange(3)); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0.35, 0.9); ax.set_ylabel("ranking score")
    ax.legend(fontsize=8, ncol=2)
    ax.set_title("Does it transfer? The same questions, simulated and real", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_artifact(path: Path) -> None:
    """How much of the real-data skill was polities already collapsing."""
    v1 = _load(RES / "test_scores_real_v1.json")
    names = [("M1_own_history", "recent trend"), ("M5_feature_clf_real", "fitted to data"),
             ("M6_fragility", "fragility")]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    x = np.arange(len(names))
    ax.bar(x - 0.2, [v1[k]["auc"] for k, _ in names], 0.38, color=WARN,
           label="as written (includes polities already collapsing)")
    ax.bar(x + 0.2, [v1[k]["auc_S1"] for k, _ in names], 0.38, color=ACCENT,
           label="excluding them")
    ax.axhline(0.5, color=INK, ls="--", lw=1)
    ax.set_xticks(x); ax.set_xticklabels([n for _, n in names])
    ax.set_ylim(0.4, 0.75); ax.set_ylabel("ranking score")
    ax.legend(fontsize=8)
    ax.set_title("Territory: most of the apparent skill was already-visible collapse", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_timing(path: Path) -> None:
    """Timing against the window prior, in both simulator designs."""
    s = _load(NB / "gate3_scores_test_v2.json")
    r = _load(NB / "robustness_window.json")
    groups = [("narrow window\n(steps 100-150)", s["base_rate__clean"]["mae_onset"],
               s["hybrid__clean"]["mae_onset"]),
              ("wide window\n(steps 100-210)", r["base_rate"]["mae_onset"], r["hybrid"]["mae_onset"])]
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    x = np.arange(len(groups))
    ax.bar(x - 0.2, [g[1] for g in groups], 0.38, color=MUTED, label="knowing the window only")
    ax.bar(x + 0.2, [g[2] for g in groups], 0.38, color=GOOD, label="best method")
    ax.set_xticks(x); ax.set_xticklabels([g[0] for g in groups], fontsize=9)
    ax.set_ylabel("average timing error (steps)")
    ax.legend(fontsize=8)
    ax.set_title("Timing: no method beats knowing when changes happen", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


FIGURES = {
    "fig_simulation.png": fig_simulation,
    "fig_real.png": fig_real,
    "fig_artifact.png": fig_artifact,
    "fig_timing.png": fig_timing,
}
