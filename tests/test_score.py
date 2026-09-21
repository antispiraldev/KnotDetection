"""Tests for the scorer: the numbers must mean what the Gate 3 tables will say."""

from __future__ import annotations

import numpy as np
import pytest

from inflection.eval.score import crps_from_quantiles, score
from inflection.methods.base import QUANTILE_LEVELS
from inflection.sim.models import TRANSITION_TYPES


def _truth(n_per_type=10, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for k in TRANSITION_TYPES:
        for i in range(n_per_type):
            on = None if k == "null" else float(rng.uniform(100, 150))
            out.append(dict(world_id=f"{k}{i}", transition_type=k, transitioned=k != "null",
                            observable_onset=on, transition_time=on))
    return out


def _constant(truth, p=0.8, onset=125.0):
    q = list(np.full(len(QUANTILE_LEVELS), onset))
    return {tr["world_id"]: dict(p_transition=p, onset_quantiles=q,
                                 type_probs={k: 1 / 7 for k in TRANSITION_TYPES})
            for tr in truth}


def test_crps_of_a_point_forecast_is_the_absolute_error():
    q = np.full((1, len(QUANTILE_LEVELS)), 10.0)
    assert crps_from_quantiles(q, np.array([13.0]))[0] == pytest.approx(3.0)


def test_a_constant_forecast_sits_at_chance():
    truth = _truth()
    s = score(_constant(truth), truth, n_boot=20)
    assert s["auc"] == pytest.approx(0.5)
    assert s["null_fpr"] == pytest.approx(0.8)
    assert s["brier_skill"] <= 0.0 + 1e-9


def test_a_perfect_forecast_scores_perfectly():
    truth = _truth()
    fc = {}
    for tr in truth:
        on = tr["observable_onset"] or 125.0
        fc[tr["world_id"]] = dict(
            p_transition=float(tr["transitioned"]),
            onset_quantiles=list(np.full(len(QUANTILE_LEVELS), on)),
            type_probs={k: float(k == tr["transition_type"]) for k in TRANSITION_TYPES})
    s = score(fc, truth, n_boot=20)
    assert s["auc"] == 1.0 and s["brier"] == 0.0 and s["null_fpr"] == 0.0
    assert s["mae_onset"] == 0.0 and s["crps_onset"] == pytest.approx(0.0)
    assert s["type_accuracy"] == 1.0 and s["type_accuracy_mechanism_change"] == 1.0


def test_a_missing_forecast_is_an_error_not_a_skip():
    truth = _truth()
    fc = _constant(truth)
    fc.pop(truth[0]["world_id"])
    with pytest.raises(ValueError):
        score(fc, truth, n_boot=10)
