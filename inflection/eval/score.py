"""Scores for the three sub-questions, as RESEARCH_PLAN §4.4 defines them.

`score(forecasts, truth)` takes forecasts keyed by world id (the JSON a method writes)
and the truth list, and returns a flat dict of metrics with bootstrap intervals for
the headline ones. It does not care where the truth came from. `score_blind` is the
test-set entry point: it refuses a forecast file the blinding ledger has not
registered, then unseals and scores.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve

from inflection.methods.base import QUANTILE_LEVELS
from inflection.sim.models import TRANSITION_TYPES

from . import blind

LEVELS = np.asarray(QUANTILE_LEVELS)


def crps_from_quantiles(q: np.ndarray, obs: np.ndarray) -> np.ndarray:
    """CRPS approximated by twice the mean pinball loss over the quantile levels.

    Exact in the limit of a dense, evenly spaced set of levels; with 19 levels from
    0.05 to 0.95 it omits the outer tails, which slightly flatters wide forecasts.
    Every method is scored the same way, so comparisons stand.
    """
    d = obs[:, None] - q
    pinball = np.maximum(LEVELS * d, (LEVELS - 1) * d)
    return 2.0 * pinball.mean(axis=1)


def _ece(p: np.ndarray, y: np.ndarray, bins: int = 5) -> float:
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    return float(sum(abs(p[idx == b].mean() - y[idx == b].mean()) * np.mean(idx == b)
                     for b in range(bins) if np.any(idx == b)))


def _metrics(p, y, q, onset, tstar, trans, probs, types) -> dict:
    out = {}
    out["brier"] = float(np.mean((p - y) ** 2))
    base = y.mean()
    ref = float(np.mean((base - y) ** 2))
    out["brier_skill"] = float(1 - out["brier"] / ref) if ref > 0 else float("nan")
    out["auc"] = float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else float("nan")
    out["ece"] = _ece(p, y)
    # False positives on null worlds, at the operating point that catches 80% of real
    # transitions, read off the ROC curve of null vs transitioning worlds. A fixed
    # p > 0.5 cut is useless here: six of seven worlds transition, so every
    # calibrated forecast sits above 0.5 and the rate is 1.0 for every method. The
    # ROC reading interpolates through tied forecasts, so a constant forecast scores
    # the chance value, 0.80, rather than an artefact of how ties are broken.
    null = types == "null"
    pos = y == 1
    if null.any() and pos.any():
        sel = null | pos
        fpr, tpr, _ = roc_curve(pos[sel], p[sel])
        out["null_fpr"] = float(np.interp(0.80, tpr, fpr))
        out["null_mean_p"] = float(np.mean(p[null]))
    else:
        out["null_fpr"] = out["null_mean_p"] = float("nan")

    m = trans & np.isfinite(onset)
    if m.any():
        out["crps_onset"] = float(np.mean(crps_from_quantiles(q[m], onset[m])))
        med = q[m][:, len(LEVELS) // 2]
        out["mae_onset"] = float(np.mean(np.abs(med - onset[m])))
        out["mae_mechanism"] = float(np.mean(np.abs(med - tstar[m])))
        out["cover90_onset"] = float(np.mean((q[m][:, 0] <= onset[m]) & (onset[m] <= q[m][:, -1])))

    pred = np.array(TRANSITION_TYPES)[probs.argmax(axis=1)]
    mech = types == "mechanism_change"
    out["type_accuracy"] = float(np.mean(pred[~mech] == types[~mech]))
    out["type_accuracy_mechanism_change"] = float(np.mean(pred[mech] == types[mech])) \
        if mech.any() else float("nan")
    ti = np.array([TRANSITION_TYPES.index(k) for k in types])
    out["type_logloss"] = float(-np.mean(np.log(np.clip(probs[np.arange(len(ti)), ti], 1e-6, 1))))
    for k in TRANSITION_TYPES:
        sel = types == k
        if sel.any():
            out[f"recall_{k}"] = float(np.mean(pred[sel] == k))
    return out


HEADLINE = ("brier", "brier_skill", "auc", "null_fpr", "crps_onset", "mae_onset",
            "type_accuracy", "type_accuracy_mechanism_change")


def score(forecasts: dict[str, dict], truth: list[dict], n_boot: int = 500,
          seed: int = 0) -> dict:
    missing = [tr["world_id"] for tr in truth if tr["world_id"] not in forecasts]
    if missing:
        raise ValueError(f"{len(missing)} worlds have no forecast, e.g. {missing[:3]}")
    f = [forecasts[tr["world_id"]] for tr in truth]
    arrays = dict(
        p=np.array([x["p_transition"] for x in f], dtype=float),
        y=np.array([tr["transitioned"] for tr in truth], dtype=float),
        q=np.array([x["onset_quantiles"] for x in f], dtype=float),
        onset=np.array([np.nan if tr["observable_onset"] is None else tr["observable_onset"]
                        for tr in truth], dtype=float),
        tstar=np.array([np.nan if tr["transition_time"] is None else tr["transition_time"]
                        for tr in truth], dtype=float),
        trans=np.array([tr["transitioned"] for tr in truth], dtype=bool),
        probs=np.array([[x["type_probs"].get(k, 0.0) for k in TRANSITION_TYPES] for x in f]),
        types=np.array([tr["transition_type"] for tr in truth]),
    )
    out = _metrics(**arrays)
    out["n"] = len(truth)

    rng = np.random.default_rng(seed)
    boots = {k: [] for k in HEADLINE}
    for _ in range(n_boot):
        i = rng.integers(0, len(truth), len(truth))
        b = _metrics(**{k: v[i] for k, v in arrays.items()})
        for k in HEADLINE:
            if k in b:
                boots[k].append(b[k])
    for k, v in boots.items():
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        if len(v):
            out[f"{k}_ci"] = [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]
    return out


def score_blind(forecast_path: Path, test_set: str, **ledger_paths) -> dict:
    """Score a registered forecast file against the sealed truth of `test_set`."""
    entry = blind.check_forecast(forecast_path, test_set,
                                 **{k: v for k, v in ledger_paths.items() if k == "ledger"})
    forecasts = json.loads(Path(forecast_path).read_text())
    truth = blind.unseal(test_set, **ledger_paths)
    return dict(score(forecasts, truth), method=entry["method"],
                forecast_sha256=entry["forecast_sha256"])
