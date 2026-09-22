"""Build the plain-language project primer: figures, a Markdown file and a PDF.

    PYTHONPATH=. .venv/bin/python scripts/build_primer.py

Writes to `docs/primer/`. The text lives once, in `CONTENT` below, and both the
Markdown and the PDF are rendered from it so they cannot drift apart. The example
trajectories are real simulator output (fixed seeds); the results chart reads the
second blind test's scores from `inflection/notebooks/gate3_scores_test_v2.json`.
Needs `fpdf2` for the PDF.
"""

from __future__ import annotations

import json
from pathlib import Path

from doc_render import render_markdown, render_pdf

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "primer"
SCORES = ROOT / "inflection" / "notebooks" / "gate3_scores_test_v2.json"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

INK, MUTED, ACCENT, WARN, GOOD = "#222222", "#8a8a8a", "#2f6fb0", "#c8553d", "#3a8a5c"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": "#555555", "axes.titleweight": "bold",
    "axes.titlesize": 11,
})


# --- figures ------------------------------------------------------------------

def fig_landscape(path: Path) -> None:
    """A ball in a valley: resilient, fragile, tipped.

    The ball sits in the right-hand valley. Slow pressure makes that valley
    shallow; then it tips into the deeper valley on the left.
    """
    x = np.linspace(-2.2, 2.2, 600)

    def landscape(tilt):
        v = x ** 4 / 4 - x ** 2 + tilt * x
        return v - v.min()

    def local_min(v, side):
        idx = np.where((v[1:-1] < v[:-2]) & (v[1:-1] < v[2:]))[0] + 1
        pick = idx[x[idx] > 0] if side == "right" else idx[x[idx] < 0]
        return float(x[pick[0]])

    panels = [
        ("Resilient", -0.35, "right", "A deep valley: knocks don't\nmove it far, and it rolls back."),
        ("Fragile", 0.9, "right", "Slow pressures have made its valley\nshallow: a modest knock can tip it."),
        ("Tipped", 0.9, "left", "It has rolled into a different\nvalley: a new state of society."),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.0))
    for ax, (title, tilt, side, caption) in zip(axes, panels):
        v = landscape(tilt)
        top = 3.2
        ax.fill_between(x, v, top, color="#eef3f9")
        ax.plot(x, v, color=INK, lw=2)
        bx = local_min(v, side)
        ax.scatter([bx], [np.interp(bx, x, v) + 0.16], s=180, color=WARN, zorder=3,
                   edgecolor="white", lw=1.5)
        ax.set_title(title)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_ylim(-0.3, top)
        ax.text(0.5, -0.18, caption, transform=ax.transAxes, ha="center", va="top", fontsize=9,
                color=INK)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_visible(False)
    fig.suptitle("The core picture: a society as a ball in a landscape", fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_slowing_down(path: Path) -> None:
    """Far from a tipping point, a system snaps back; near one, it wanders."""
    rng = np.random.default_rng(3)
    n = 150
    fig, axes = plt.subplots(1, 2, figsize=(10, 2.6), sharey=True)
    panels = [(0.3, "Far from a tipping point:\nquick, small, jittery recovery", ACCENT),
              (0.93, "Close to a tipping point:\nslow, wandering, larger swings", WARN)]
    for ax, (phi, title, col) in zip(axes, panels):
        # Same size of knocks in both; only the pull back toward the middle differs,
        # so the swings near the tipping point come out slower *and* larger.
        e = rng.standard_normal(n) * 0.6
        y = np.zeros(n)
        for i in range(1, n):
            y[i] = phi * y[i - 1] + e[i]
        ax.plot(y, color=col, lw=1.3)
        ax.axhline(0, color=MUTED, lw=0.8, ls="--")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("time")
        ax.set_yticks([])
    fig.suptitle("The classic warning sign: recovering from small knocks takes longer",
                 fontweight="bold", y=1.04)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_examples(path: Path) -> None:
    """Four simulated societies, with what a method gets to see."""
    from inflection.sim.generate import generate_world
    picks = [("null", 4, "No change"), ("fold", 3, "Collapse under building pressure"),
             ("hopf", 1, "Boom-and-bust cycles begin"), ("exogenous_shock", 2, "Outside shock")]
    fig, axes = plt.subplots(2, 2, figsize=(10, 5.0), sharex=True)
    for ax, (kind, seed, title) in zip(axes.flat, picks):
        w = generate_world(kind, np.random.default_rng(seed))
        y = w.raw / np.median(w.raw[w.t < w.origin])
        ax.axvspan(0, w.origin, color="#e3edf7")
        ax.plot(w.t, y, color=INK, lw=0.9)
        ax.axvline(w.origin, color=ACCENT, lw=1.2, ls="--")
        if w.observable_onset is not None:
            ax.axvline(w.observable_onset, color=WARN, lw=1.4)
        ax.set_title(title, fontsize=10)
        ax.set_yticks([])
        # Common baseline at zero, so small wobbles look small.
        ax.set_ylim(0, max(1.6, float(y.max()) * 1.05))
    axes[0, 0].text(4, axes[0, 0].get_ylim()[1] * 0.95, "what a method sees", va="top",
                    color=ACCENT, fontsize=7.5)
    for ax in axes[1]:
        ax.set_xlabel("time")
    handles = [plt.Line2D([], [], color=ACCENT, ls="--", label="forecast made here"),
               plt.Line2D([], [], color=WARN, label="change becomes visible")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Simulated societies: forecast the future from the shaded past only",
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_blind_test(path: Path) -> None:
    """The order of events that keeps the test honest."""
    steps = ["Generate\nsocieties", "Seal the\nanswers", "Methods see\nonly the past",
             "Lock forecasts\n(fingerprint)", "Open answers\nand score"]
    fig, ax = plt.subplots(figsize=(10, 1.7))
    ax.set_xlim(0, len(steps)); ax.set_ylim(0, 1); ax.axis("off")
    for i, s in enumerate(steps):
        col = WARN if i in (1, 3) else ACCENT
        ax.add_patch(FancyBboxPatch((i + 0.08, 0.15), 0.78, 0.7, boxstyle="round,pad=0.02",
                                    fc="white", ec=col, lw=2))
        ax.text(i + 0.47, 0.5, s, ha="center", va="center", fontsize=9.5, color=INK)
        if i < len(steps) - 1:
            ax.annotate("", xy=(i + 1.07, 0.5), xytext=(i + 0.87, 0.5),
                        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.5))
    fig.suptitle("A blind test: forecasts are locked before anyone sees the answers",
                 fontweight="bold", y=1.05)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_results(path: Path) -> None:
    """The three answers so far, against what chance would give."""
    s = json.loads(SCORES.read_text())
    good, poor = "hybrid__clean", "hybrid__harsh"
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.1))

    ax = axes[0]
    vals = [s[good]["auc"], s[poor]["auc"], s["generic_ews__clean"]["auc"]]
    ax.bar(["good\ndata", "poor\ndata", "classic\nwarning signs"], vals,
           color=[GOOD, "#9cc5ab", MUTED])
    ax.axhline(0.5, color=INK, ls="--", lw=1)
    ax.text(2.45, 0.51, "coin flip", ha="right", va="bottom", fontsize=8.5)
    ax.set_ylim(0.3, 1.0)
    ax.set_title("WHETHER a change is coming")
    ax.set_ylabel("ranking score (1 = perfect)")

    ax = axes[1]
    vals = [100 * s[good]["type_accuracy"], 100 * s[poor]["type_accuracy"]]
    ax.bar(["good\ndata", "poor\ndata"], vals, color=[GOOD, "#9cc5ab"])
    ax.axhline(100 / 6, color=INK, ls="--", lw=1)
    ax.text(1.55, 100 / 6, "guessing", ha="left", va="center", fontsize=8.5, clip_on=False)
    ax.set_ylim(0, 60)
    ax.set_title("WHAT kind of change")
    ax.set_ylabel("% named correctly")

    ax = axes[2]
    vals = [s[good]["mae_onset"], s["base_rate__clean"]["mae_onset"]]
    ax.bar(["best\nmethod", "just knowing\nthe window"], vals, color=[WARN, MUTED])
    ax.set_ylim(0, 25)
    ax.text(0.5, 21.5, "difference within the\nmargin of error", ha="center", fontsize=8.5,
            color=INK)
    ax.set_title("WHEN it will happen")
    ax.set_ylabel("average error (time steps)")
    for a in axes:
        a.tick_params(axis="x", labelsize=8.5)
    fig.suptitle("What we found in blind tests (simulated societies)", fontweight="bold", y=1.03)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# --- content ------------------------------------------------------------------
# ("h1" | "h2" | "p" | "bullets" | "fig" | "table", payload). Plain text; **bold** allowed.

CONTENT = [
    ("h1", "Can we see a society's turning point coming?"),
    ("p", "A short, plain-language introduction to the KnotDetection project: what it asks, "
          "how it tests the question, what it has found so far, and what it cannot yet say."),

    ("h2", "The question"),
    ("p", "Societies usually change slowly, but sometimes they shift suddenly: a state "
          "collapses, a long peace gives way to recurring unrest, an economy tips into a new "
          "pattern. The project asks whether such turning points can be anticipated using only "
          "data from before they happen. It splits that into three questions:"),
    ("bullets", ["**Whether** a sudden change is coming at all.",
                 "**When** it will happen.",
                 "**What kind** of change it will be."]),
    ("p", "The motivation comes from **cliodynamics**, a field that treats history "
          "quantitatively: it builds mathematical models of how population, wealth, elites and "
          "states interact, and looks for recurring patterns across societies. If those models "
          "capture something real, they should support forecasts, and forecasts can be tested. "
          "This project is about testing that ability honestly."),

    ("h2", "The core idea: tipping points"),
    ("fig", ("fig_landscape.png", "A system resting in a valley returns after small knocks. If "
             "slow pressures make the valley shallow, an ordinary knock can tip it into a "
             "different state.")),
    ("p", "Mathematicians who study systems that change over time (**dynamical systems**) "
          "picture a system as a ball in a landscape. A society in a stable condition sits in a "
          "valley. Slow pressures, such as rising inequality or falling state revenue, can "
          "reshape the landscape so the valley grows shallower. Eventually a small push, or no "
          "push at all, sends the ball into another valley: a **tipping point**."),
    ("p", "Different kinds of tipping point exist. A system can collapse outright, begin to "
          "oscillate in booms and busts, hand over gradually from one state to another, be "
          "knocked over by an outside shock, or change because its rules change. Telling these "
          "apart is the \"what kind\" question."),

    ("h2", "The hoped-for warning sign"),
    ("fig", ("fig_slowing_down.png", "Near a tipping point, a system takes longer to recover "
             "from small disturbances, so its fluctuations become slower and larger.")),
    ("p", "Theory predicts a warning sign. As the valley flattens, the ball rolls back more "
          "slowly after each small knock. In data this shows up as fluctuations that are "
          "slower and larger: each value looks more like the one before. This \"critical "
          "slowing down\" has been used to anticipate shifts in lakes, climate and ecosystems, "
          "and has been applied to archaeological and historical data too."),

    ("h2", "What we did"),
    ("p", "Real historical data are scarce, patchy, and the true causes of past transitions are "
          "debated, so they cannot tell us whether a method works. Instead we built a "
          "**simulator**: a program that generates thousands of artificial societies, each a "
          "single time series (think population or wealth) following one of seven futures. "
          "Because we made them, we know exactly what happens to each one and when."),
    ("fig", ("fig_examples.png", "Four of the simulated societies. Methods see only the shaded "
             "stretch and must forecast what follows.")),
    ("p", "Forecasting methods see only the early part of each society's history and must "
          "predict the rest. We also blurred the data in several ways (added noise, gaps, "
          "irregular dates, shorter records, indirect measurements) because real historical "
          "records look like that. We compared five methods, from a baseline that ignores the "
          "data, through the classic warning-sign approach, to machine-learning models."),

    ("h2", "Keeping ourselves honest"),
    ("fig", ("fig_blind_test.png", "Answers are sealed before forecasting, and forecasts are "
             "fingerprinted and time-stamped before the answers are opened.")),
    ("p", "The same person builds the methods and the tests, and it is easy to fool yourself. "
          "So every result comes from a **blind test**: the answers are sealed, predictions of "
          "the outcome are written down in advance, and every forecast is locked with a digital "
          "fingerprint before the answers are opened. We also checked repeatedly that the "
          "simulator does not accidentally give the answer away through something irrelevant, "
          "such as how noisy a series is. Several such flaws were found and fixed before "
          "testing."),

    ("h2", "What we found so far"),
    ("fig", ("fig_results.png", "Results of the second blind test (420 simulated societies). "
             "The first blind test gave very similar numbers.")),
    ("bullets", [
        "**Whether** a change is coming can be judged moderately well on good data, and less "
        "well on poor data. The skill comes from spotting societies that already look fragile, "
        "not from detecting an approaching tipping point.",
        "**What kind** of change is somewhat predictable on good data (about half right, "
        "against one in six by guessing), but not on poor data.",
        "**When** is not predictable beyond knowing the rough window in which changes happen. "
        "The past shows how far a slow change has already gone, not when the tipping point "
        "will arrive.",
        "The **classic warning signs did no better than a coin flip**: with records this "
        "short, stable societies show apparent warning signs just as often by chance.",
        "Changes with no warning signs, such as a sudden change of rules, were not foreseen, "
        "as expected.",
    ]),

    ("h2", "Limitations"),
    ("bullets", [
        "**These are simulated societies**, built from simple models with one measured quantity "
        "each. Nothing here is yet a finding about real history.",
        "**Design choices shape the results.** For example, changes in the simulator happen "
        "within a fixed time window, which makes timing easier to guess than it may be in "
        "reality. One such choice (outside shocks only hitting fragile societies) was caught "
        "and fixed between the two tests; others may remain.",
        "**The methods are relatively simple.** Stronger ones might do better on \"what "
        "kind\", but the timing analysis suggests the information about \"when\" is simply "
        "not in the data.",
        "**Forecasts were made a limited distance ahead**, roughly 10 to 90 time steps before "
        "the change.",
    ]),

    ("h2", "What happened when we tried real history"),
    ("p", "Two tests on real data followed, each planned in writing before the data was "
          "downloaded, and each anonymised by a separate assistant so that recognising a "
          "famous case could not substitute for forecasting it."),
    ("bullets", [
        "**Territory of 300 historical polities** (which lands a state held, over time). "
        "Almost all of the apparent skill turned out to be polities already visibly "
        "shrinking when the forecast was made. Excluding those, nothing beat a coin flip, "
        "and nothing at all predicted which states would disappear.",
        "**Income per person, annually, for 74 countries.** Here a simple model fitted to "
        "real history did predict large falls in income, and reasonably well.",
        "**But the methods trained on the simulated societies did worse than chance** on "
        "that same data. The reason is a reversal: in the simulations, a society heading "
        "for a tipping point recovers from small knocks more and more slowly, which makes "
        "its record look smoother, so smoothness reads as danger. In real income data "
        "smoothness means the opposite: steady growers rarely crashed, and the economies "
        "that fell were the jumpy ones, swinging about 9% a year against 2% for the rest. "
        "A method taught the simulated rule applies it backwards.",
    ]),
    ("p", "That is the project's sharpest practical lesson: a forecasting method that works "
          "on simulated data should not be assumed to work on history, even when the "
          "simulation was built carefully and tested honestly."),

    ("h2", "A few terms"),
    ("table", [
        ("Cliodynamics", "The quantitative, model-based study of historical change."),
        ("Dynamical system", "Anything whose state changes over time according to rules."),
        ("Tipping point", "A threshold past which a system shifts suddenly to a new state."),
        ("Critical slowing down", "Slower recovery from small knocks as a tipping point nears."),
        ("Blind test", "Forecasts are locked before the answers are seen."),
        ("Ranking score", "How often a method rates a society that changed as more likely to "
                          "change than one that didn't; 0.5 is a coin flip, 1 is perfect."),
    ]),
]

FIGURES = {
    "fig_landscape.png": fig_landscape,
    "fig_slowing_down.png": fig_slowing_down,
    "fig_examples.png": fig_examples,
    "fig_blind_test.png": fig_blind_test,
    "fig_results.png": fig_results,
}


# --- renderers ----------------------------------------------------------------

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in FIGURES.items():
        make(OUT / name)
        print(f"wrote {OUT / name}")
    render_markdown(OUT / "primer.md", CONTENT)
    print(f"wrote {OUT / 'primer.md'}")
    render_pdf(OUT / "primer.pdf", CONTENT, OUT)
    print(f"wrote {OUT / 'primer.pdf'}")


if __name__ == "__main__":
    main()
