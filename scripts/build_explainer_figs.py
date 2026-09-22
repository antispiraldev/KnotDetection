"""Figures for the plain-language explainer page (docs/explainer/).

Four pictures, each carrying one idea, drawn from the released blind-test data where
the idea is empirical and drawn schematically where it is definitional:

1. two real income records, one that later fell and one that didn't;
2. how often a record fell, by how jumpy it was;
3. the sign reversal between the simulator and real economies;
4. the already-collapsed artifact (schematic, and labelled as such).

    PYTHONPATH=. .venv/bin/python scripts/build_explainer_figs.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "explainer"

PAPER = "#f6f7f9"        # the plate these sit on, in both page themes
INK = "#171c22"
MUTED = "#626d78"
FELL = "#c8553d"         # rust: records that later fell
HELD = "#2f6fb0"         # blue: records that didn't
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": "#c6ccd3",
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
})


def _real_v2():
    z = np.load(ROOT / "inflection" / "data" / "real_v2" / "series.npz")
    truth = {t["world_id"]: t for t in
             json.loads((ROOT / "inflection" / "data" / "released" / "real_v2" / "truth.json").read_text())}
    ids = sorted(k for k in z.files if not k.startswith("t_"))
    y = np.array([truth[w]["transitioned"] for w in ids])
    vol = np.array([np.std(np.diff(np.log(z[w]))) for w in ids])
    return z, ids, y, vol


def fig_two_records(path: Path) -> None:
    """One jumpy record that later fell, one steady record that didn't."""
    z, ids, y, vol = _real_v2()
    # Typical rather than extreme: a faller at the 70th percentile of jumpiness among
    # fallers, and a survivor at the 30th among survivors. Both median-normalised, as
    # every method saw them.
    def pick(mask, q):
        idx = np.where(mask)[0]
        return ids[int(idx[np.argsort(vol[idx])[int(q * (len(idx) - 1))]])]
    fell, held = pick(y, 0.70), pick(~y, 0.30)
    years = np.arange(-30, 0)

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    for wid, color, label, dy in ((held, HELD, "steady: no fall in the next 15 years", 14),
                                  (fell, FELL, "jumpy: fell by over a quarter within 15 years", -16)):
        s = z[wid] / np.median(z[wid])
        ax.plot(years, s, color=color, lw=2.2, solid_capstyle="round")
        ax.annotate(label, (years[-1], s[-1]), xytext=(8, dy), textcoords="offset points",
                    va="center", ha="left", fontsize=10, color=color, weight="bold")
    ax.axvline(0, color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.annotate("forecast made here", (0, 0.04), xycoords=("data", "axes fraction"),
                xytext=(-8, 0), textcoords="offset points", ha="right", va="bottom",
                fontsize=9.5, color=MUTED)
    ax.set_xlim(-30, 26)
    ax.margins(y=0.18)
    ax.set_xlabel("years before the forecast")
    ax.set_ylabel("income per person\n(relative to its own average)")
    ax.set_yticks([])
    ax.set_title("Two real countries, thirty years of income each", loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor=PAPER)
    plt.close(fig)


def fig_jumpiness(path: Path) -> None:
    """How often a record was followed by a large fall, by how jumpy it was."""
    z, ids, y, vol = _real_v2()
    band = np.digitize(vol, np.quantile(vol, [.25, .5, .75]))
    rates = [100 * y[band == b].mean() for b in range(4)]
    names = ["calmest\nquarter", "second", "third", "jumpiest\nquarter"]
    colors = ["#9db8d4", "#7fa0c4", "#d79b8c", FELL]

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    bars = ax.bar(names, rates, width=0.62, color=colors)
    for bar, r in zip(bars, rates):
        ax.annotate(f"{r:.0f}%", (bar.get_x() + bar.get_width() / 2, r), xytext=(0, 5),
                    textcoords="offset points", ha="center", fontsize=11, weight="bold", color=INK)
    ax.set_ylim(0, max(rates) * 1.25)
    ax.set_yticks([])
    ax.set_ylabel("share that later fell")
    ax.set_title("Jumpier records fell far more often", loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor=PAPER)
    plt.close(fig)


def fig_flip(path: Path) -> None:
    """The same two clues, opposite meanings in the two worlds."""
    d = json.loads((ROOT / "phase2" / "results" / "feature_direction.json").read_text())
    clues = [("jumpiness", "log_step_sd"), ("sluggishness", "lag1_ac")]
    real = [d[k]["real"] - 0.5 for _, k in clues]
    sim = [d[k]["simulated"] - 0.5 for _, k in clues]
    ypos = np.arange(len(clues))

    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    ax.barh(ypos + 0.18, sim, height=0.32, color=HELD)
    ax.barh(ypos - 0.18, real, height=0.32, color=FELL)
    for i, (s, r) in enumerate(zip(sim, real)):
        ax.annotate("simulated worlds", (s, i + 0.18), xytext=(8 if s > 0 else -8, 0),
                    textcoords="offset points", va="center", ha="left" if s > 0 else "right",
                    fontsize=9.5, color=HELD, weight="bold")
        ax.annotate("real economies", (r, i - 0.18), xytext=(8 if r > 0 else -8, 0),
                    textcoords="offset points", va="center", ha="left" if r > 0 else "right",
                    fontsize=9.5, color=FELL, weight="bold")
    ax.axvline(0, color=INK, lw=1.2)
    ax.set_yticks(ypos)
    ax.set_yticklabels([n for n, _ in clues], fontsize=12, color=INK)
    ax.set_xticks([])
    ax.set_xlim(-0.22, 0.40)
    ax.annotate("← suggests safety", (0.5, 1.02), xycoords=("axes fraction", "axes fraction"),
                xytext=(-10, 0), textcoords="offset points", ha="right", va="bottom",
                fontsize=10, color=MUTED)
    ax.annotate("warns of a fall →", (0.5, 1.02), xycoords=("axes fraction", "axes fraction"),
                xytext=(10, 0), textcoords="offset points", ha="left", va="bottom",
                fontsize=10, color=MUTED)
    ax.invert_yaxis()            # jumpiness on top, the clue that matters in reality
    ax.set_title("The same two clues, opposite meanings", loc="left", weight="bold", pad=26)
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor=PAPER)
    plt.close(fig)


def fig_already_fallen(path: Path) -> None:
    """Schematic: the fall sits inside the record the method was given."""
    t = np.arange(-30, 16)
    rng = np.random.default_rng(4)
    level = np.where(t < -12, 1.0, 0.42)
    s = level * (1 + 0.03 * rng.standard_normal(len(t)))
    s[(t >= -13) & (t <= -11)] = [0.95, 0.72, 0.5]

    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    ax.axvspan(-30, 0, color="#e3e7ec")
    ax.plot(t[t <= 0], s[t <= 0], color=INK, lw=2.2)
    ax.plot(t[t >= 0], s[t >= 0], color=MUTED, lw=2.2, alpha=0.65)
    ax.axvline(0, color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.annotate("the record the method is given", (-15, 1.12), ha="center", fontsize=10,
                color=MUTED)
    ax.annotate("the fall already happened here", (-12, 0.5), xytext=(-24, -34),
                textcoords="offset points", fontsize=10, color=FELL, weight="bold",
                arrowprops=dict(arrowstyle="->", color=FELL, lw=1.4))
    ax.annotate("...and this counts as a\nsuccessful forecast", (7, 0.42), xytext=(0, 26),
                textcoords="offset points", ha="center", fontsize=10, color=FELL, weight="bold",
                arrowprops=dict(arrowstyle="->", color=FELL, lw=1.4))
    ax.set_ylim(0.1, 1.3)
    ax.set_yticks([])
    ax.set_xlabel("years before and after the forecast")
    ax.set_title("The mistake that inflated the first real test (illustration)",
                 loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor=PAPER)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in (("two_records.png", fig_two_records),
                       ("jumpiness.png", fig_jumpiness),
                       ("flip.png", fig_flip),
                       ("already_fallen.png", fig_already_fallen)):
        make(OUT / name)
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
