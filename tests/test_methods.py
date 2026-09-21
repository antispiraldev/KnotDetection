"""Smoke tests: every method fits, forecasts, and stays inside the interface contract."""

from __future__ import annotations

import numpy as np
import pytest

from inflection.methods.base import QUANTILE_LEVELS, Record
from inflection.methods.baselines import BaseRate, OwnHistory
from inflection.methods.ews import GenericEWS
from inflection.methods.features import FeatureClassifier
from inflection.sim import realism as R
from inflection.sim.generate import T, generate_pool
from inflection.sim.models import TRANSITION_TYPES


@pytest.fixture(scope="module")
def tiny():
    worlds, _ = generate_pool(n_per_type=4, seed=5)
    truth = [w.sealed_truth() for w in worlds]
    rng = np.random.default_rng(0)
    recs = {}
    for name in ("clean", "harsh"):
        recs[name] = [Record(w.world_id, *w.record(R.LAYERS[name], rng), w.origin, T)
                      for w in worlds]
    return recs, truth


@pytest.mark.parametrize("cls", [BaseRate, OwnHistory, GenericEWS, FeatureClassifier])
@pytest.mark.parametrize("layer", ["clean", "harsh"])
def test_method_honours_the_forecast_contract(tiny, cls, layer):
    recs, truth = tiny
    fc = cls().fit(recs[layer], truth).forecast_all(recs[layer])
    assert set(fc) == {r.world_id for r in recs[layer]}
    for r in recs[layer]:
        f = fc[r.world_id]
        assert 0.0 <= f["p_transition"] <= 1.0
        q = np.asarray(f["onset_quantiles"])
        assert q.shape == (len(QUANTILE_LEVELS),)
        assert np.all(np.diff(q) >= 0)
        assert r.origin <= q[0] and q[-1] <= r.horizon
        assert set(f["type_probs"]) == set(TRANSITION_TYPES)
        assert sum(f["type_probs"].values()) == pytest.approx(1.0)


def test_methods_never_see_the_truth_at_prediction_time(tiny):
    """`predict` takes a Record, and a Record has no field that carries the answer."""
    fields = set(Record.__dataclass_fields__)
    assert fields == {"world_id", "t", "y", "origin", "horizon"}
