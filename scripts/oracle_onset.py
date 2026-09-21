"""Gate 3, step 1: how far behind an oracle does the fixed onset detector run?

`label.observable_onset` is a model-free threshold detector. Before it becomes the
scoring target for "when", it has to be checked against something that could not do
better: a detector that is *told* each world's true behaviour before and after the
change and only has to decide when the series switched.

The oracle is a two-sided Gaussian likelihood-ratio CUSUM per world:

- pre-change model: mean and sd of the same baseline window the fixed detector uses;
- post-change model: mean and sd of the last `POST` observations, i.e. the regime the
  world ends in. For a Hopf this is the grown cycle (same mean, larger spread), so
  the likelihood ratio is a variance test there and a level test elsewhere;
- threshold: set per world so that the CUSUM false-alarms on at most 5% of AR(1)
  surrogates fitted to that world's own baseline. Raw observations are
  autocorrelated, so a textbook threshold would fire constantly; the surrogates
  carry the autocorrelation and so price it in.

Two oracle times are reported. The *alarm* is when the CUSUM crosses its threshold,
using only past data. The *changepoint* is the last time the statistic was at zero
before the alarm -- the CUSUM's own retrospective estimate of where the change began.
The fixed detector's onset is retrospective too (centred windows, then a hold), so
the changepoint is the like-for-like comparison, and the alarm is shown for scale.

    PYTHONPATH=. .venv/bin/python scripts/oracle_onset.py

Uses the pool cached by `gate2_report.py`.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from inflection.sim import models

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inflection" / "notebooks"
CACHE = OUT / "_pool_cache.pkl"

BASELINE_FRAC = 0.20   # matches label.observable_onset
MIN_BASE = 60
POST = 40
N_SURR = 400
FALSE_ALARM = 0.05


def _gauss_llr(y, mu0, s0, mu1, s1):
    return (np.log(s0 / s1)
            - 0.5 * ((y - mu1) / s1) ** 2
            + 0.5 * ((y - mu0) / s0) ** 2)


def _cusum(llr: np.ndarray) -> np.ndarray:
    """Page's CUSUM along the last axis."""
    g = np.zeros_like(llr)
    acc = np.zeros(llr.shape[:-1])
    for i in range(llr.shape[-1]):
        acc = np.maximum(0.0, acc + llr[..., i])
        g[..., i] = acc
    return g


def oracle(t: np.ndarray, s: np.ndarray, rng: np.random.Generator) -> dict:
    n_base = max(int(len(s) * BASELINE_FRAC), MIN_BASE)
    base, tail = s[:n_base], s[-POST:]
    mu0, s0 = float(base.mean()), float(base.std())
    mu1, s1 = float(tail.mean()), float(tail.std())
    s1 = max(s1, 1e-3 * s0)

    # AR(1) surrogates matched to the baseline: same mean, variance, lag-1 correlation.
    # Each surrogate is a full-length series whose *own* baseline is re-estimated, so
    # the threshold prices in the error of estimating the pre-change model from
    # `n_base` points, not only the autocorrelation. Without that the oracle
    # false-alarmed on 60% of null worlds.
    c = base - mu0
    phi = float(np.clip(np.dot(c[1:], c[:-1]) / np.dot(c, c), -0.99, 0.99))
    n = len(s)
    eps = rng.standard_normal((N_SURR, n)) * s0 * np.sqrt(1 - phi ** 2)
    surr = np.empty((N_SURR, n))
    surr[:, 0] = rng.standard_normal(N_SURR) * s0
    for i in range(1, n):
        surr[:, i] = phi * surr[:, i - 1] + eps[:, i]
    surr += mu0
    m0 = surr[:, :n_base].mean(axis=1, keepdims=True)
    sd0 = surr[:, :n_base].std(axis=1, keepdims=True)
    g_surr = _cusum(_gauss_llr(surr[:, n_base:], m0, sd0, mu1, s1))
    h = float(np.quantile(g_surr.max(axis=1), 1 - FALSE_ALARM))

    g = _cusum(_gauss_llr(s[n_base:], mu0, s0, mu1, s1))
    over = np.where(g > h)[0]
    if len(over) == 0:
        return dict(alarm=None, changepoint=None, threshold=h, phi=phi)
    a = int(over[0])
    zeros = np.where(g[:a] == 0)[0]
    cp = int(zeros[-1]) + 1 if len(zeros) else 0
    return dict(alarm=float(t[n_base + a]), changepoint=float(t[n_base + cp]),
                threshold=h, phi=phi)


def main() -> None:
    worlds, _ = pickle.loads(CACHE.read_bytes())
    rng = np.random.default_rng(2026)
    rows = []
    for w in worlds:
        o = oracle(w.t, w.raw, rng)
        rows.append(dict(
            world_id=w.world_id, transition_type=w.transition_type,
            transition_time=w.transition_time, onset=w.observable_onset, **o,
        ))

    types = [t for t in models.TRANSITION_TYPES if t != "null"]
    print("oracle false alarms on null worlds (target <= 5%):",
          f"{np.mean([r['alarm'] is not None for r in rows if r['transition_type'] == 'null']):.2f}")
    for tt in ("mechanism_change", "exogenous_shock"):
        R = [r for r in rows if r["transition_type"] == tt]
        early = np.mean([r["alarm"] is not None and r["alarm"] < r["transition_time"] for r in R])
        print(f"oracle alarms before t* on {tt} (null-like before t*): {early:.2f}")
    print()
    print("gap = fixed onset - oracle changepoint  (positive: the fixed detector is late)")
    print(f"{'type':18s} {'n':>3s} {'missed':>6s}   {'gap p10':>7s} {'p50':>6s} {'p90':>6s}"
          f"   {'alarm-onset p50':>15s}   {'cp - t* p50':>11s}")
    summary = {}
    for tt in types:
        R = [r for r in rows if r["transition_type"] == tt]
        hit = [r for r in R if r["changepoint"] is not None]
        gap = np.array([r["onset"] - r["changepoint"] for r in hit])
        al = np.array([r["alarm"] - r["onset"] for r in hit])
        cpt = np.array([r["changepoint"] - r["transition_time"] for r in hit])
        q = np.percentile(gap, [10, 50, 90]) if len(gap) else [np.nan] * 3
        summary[tt] = dict(n=len(R), missed=len(R) - len(hit),
                           gap_p10=q[0], gap_p50=q[1], gap_p90=q[2],
                           alarm_minus_onset_p50=float(np.median(al)) if len(al) else None,
                           cp_minus_tstar_p50=float(np.median(cpt)) if len(cpt) else None)
        print(f"{tt:18s} {len(R):3d} {len(R) - len(hit):6d}   {q[0]:7.1f} {q[1]:6.1f} {q[2]:6.1f}"
              f"   {np.median(al):15.1f}   {np.median(cpt):11.1f}")

    fig, ax = plt.subplots(figsize=(8, 4))
    data = [[r["onset"] - r["changepoint"] for r in rows
             if r["transition_type"] == tt and r["changepoint"] is not None] for tt in types]
    ax.boxplot(data, tick_labels=types, showfliers=True)
    ax.axhline(0, color="#D62728", lw=1, ls="--")
    ax.set_ylabel("fixed onset − oracle changepoint")
    ax.set_title("How late is the fixed onset detector, against an oracle told the true regimes?")
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "gate3_oracle_gap.png", dpi=140)
    plt.close(fig)

    (OUT / "gate3_oracle.json").write_text(json.dumps(
        dict(summary=summary, rows=rows), indent=2, default=float))
    print(f"\nwrote {OUT / 'gate3_oracle_gap.png'} and gate3_oracle.json")


if __name__ == "__main__":
    main()
