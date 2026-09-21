"""Tests for the blinding protocol: the ledger must refuse every out-of-order step."""

from __future__ import annotations

import json

import numpy as np
import pytest

from inflection.eval import blind
from inflection.eval.blind import BlindingViolation


@pytest.fixture
def paths(tmp_path):
    return dict(ledger=tmp_path / "ledger.jsonl", sealed=tmp_path / "sealed")


@pytest.fixture
def built(tmp_path_factory):
    """A tiny fresh test set per test: a seed, then a pool of one world per type."""
    root = tmp_path_factory.mktemp("blind")
    p = dict(ledger=root / "ledger.jsonl", sealed=root / "sealed")
    blind.commit_test_seed("t", **p)
    summary = blind.build_test_pool("t", n_per_type=1, out_root=root, **p)
    return root, p, summary


def test_seed_is_committed_by_hash_only(paths):
    digest = blind.commit_test_seed("t", **paths)
    text = paths["ledger"].read_text()
    seed = json.loads((paths["sealed"] / "t.seed.json").read_text())["seed"]
    assert digest in text
    assert str(seed) not in text


def test_a_test_set_cannot_be_given_a_second_seed(paths):
    blind.commit_test_seed("t", **paths)
    with pytest.raises(BlindingViolation):
        blind.commit_test_seed("t", **paths)


def test_a_tampered_seed_is_refused(paths):
    blind.commit_test_seed("t", **paths)
    f = paths["sealed"] / "t.seed.json"
    blob = json.loads(f.read_text())
    f.write_text(json.dumps(dict(blob, seed=blob["seed"] + 1)))
    with pytest.raises(BlindingViolation):
        blind._load_seed("t", paths["ledger"], paths["sealed"])


def test_open_test_records_carry_no_seed_labels_or_class_balance(built):
    root, p, _ = built
    seed = json.loads((p["sealed"] / "t.seed.json").read_text())["seed"]
    for d in (root / "t").iterdir():
        manifest = (d / "manifest.json").read_text()
        assert str(seed) not in manifest and str(seed + 1) not in manifest
        for word in ("fold", "hopf", "transcritical", "noise_induced",
                     "exogenous_shock", "mechanism_change", "failures"):
            assert word not in manifest, (d.name, word)
        ids = [k for k in np.load(d / "series.npz").files if not k.startswith("t_")]
        assert all(k.startswith("t-") for k in ids)
    assert "failures" not in p["ledger"].read_text()


def test_forecasts_registered_before_unsealing_are_scorable(built, tmp_path):
    root, p, summary = built
    f = tmp_path / "fc.json"
    f.write_text('{"a": 1}')
    blind.register_forecasts(f, "t", "demo", ledger=p["ledger"])
    truth = blind.unseal("t", **p)
    assert len(truth) == summary["n_worlds"]    # a type can fail to generate at n=1
    assert blind.check_forecast(f, "t", ledger=p["ledger"])["method"] == "demo"


def test_after_unsealing_nothing_new_can_be_registered_or_scored(built, tmp_path):
    root, p, _ = built
    blind.unseal("t", **p)
    late = tmp_path / "late.json"
    late.write_text('{"b": 2}')
    with pytest.raises(BlindingViolation):
        blind.register_forecasts(late, "t", "demo", ledger=p["ledger"])
    with pytest.raises(BlindingViolation):
        blind.check_forecast(late, "t", ledger=p["ledger"])
    with pytest.raises(BlindingViolation):
        blind.build_test_pool("t", n_per_type=1, out_root=root, **p)


def test_an_edited_forecast_is_not_the_registered_one(paths, tmp_path):
    f = tmp_path / "fc.json"
    f.write_text('{"a": 1}')
    blind.commit_test_seed("t", **paths)
    blind.register_forecasts(f, "t", "demo", ledger=paths["ledger"])
    f.write_text('{"a": 2}')
    with pytest.raises(BlindingViolation):
        blind.check_forecast(f, "t", ledger=paths["ledger"])


def test_unsealing_is_recorded_before_the_truth_is_read(built):
    root, p, _ = built
    truth = p["sealed"] / "t" / "truth.json"
    original = truth.read_text()
    truth.write_text("[]")              # a truth file that fails its hash check ...
    try:
        with pytest.raises(BlindingViolation):
            blind.unseal("t", **p)
        # ... still counts as opened: the attempt itself is what the protocol records.
        assert blind.is_unsealed("t", p["ledger"])
    finally:
        truth.write_text(original)


def test_release_is_refused_until_the_test_set_is_spent(built, tmp_path):
    root, p, _ = built
    with pytest.raises(BlindingViolation):
        blind.release("t", released=tmp_path / "rel", **p)
    blind.unseal("t", **p)
    out = blind.release("t", released=tmp_path / "rel", **p)
    assert (out / "seed.json").exists() and (out / "truth.json").exists()
