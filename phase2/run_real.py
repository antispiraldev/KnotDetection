"""Phase 2 evaluation on the anonymised Cliopatria windows (`real_v1`).

Three steps, run separately so that the ledger shows them as separate events:

    PYTHONPATH=. .venv/bin/python phase2/run_real.py dev        # grouped CV on dev only
    PYTHONPATH=. .venv/bin/python phase2/run_real.py forecast   # test forecasts, registered
    PYTHONPATH=. .venv/bin/python phase2/run_real.py score      # unseal and score

The methods and hypotheses are fixed in `phase2/PREREGISTRATION.md`. Only "whether" is
scored, so each method here produces one probability per window. Methods fitted on
real data see only the dev half; the simulation-trained ones (M3, M4) see no real data
at all.
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
import zlib
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inflection.eval import blind                                   # noqa: E402
from inflection.eval.leakage import FEATURE_NAMES, features          # noqa: E402
from inflection.methods.base import Record                           # noqa: E402
from inflection.methods.ews import ews_indicators                    # noqa: E402
from inflection.methods.features import FeatureClassifier, _calibrated, physical_features  # noqa: E402
from inflection.methods.hybrid import Hybrid                         # noqa: E402
from inflection.sim.generate import T                                # noqa: E402
from inflection.sim.realism import Realism                           # noqa: E402

TEST_SET = "real_v1"
DEV_DIR = ROOT / "phase2" / "data" / "dev"
TEST_DIR = ROOT / "inflection" / "data" / TEST_SET
FC_DIR = ROOT / "inflection" / "data" / "forecasts" / TEST_SET
OUT = ROOT / "phase2" / "results"
SIM_POOL = ROOT / "inflection" / "notebooks" / "_dev_pool_s102_n100.pkl"
METHODS = ("M0_base_rate", "M1_own_history", "M2_generic_ews", "M3_feature_clf_sim",
           "M4_hybrid_sim", "M5_feature_clf_real", "M6_fragility")


# --- data ---------------------------------------------------------------------

def _load(npz: Path, manifest: dict | None = None) -> list[Record]:
    z = np.load(npz)
    ids = sorted(k for k in z.files if not k.startswith("t_"))
    horizon = _horizon(manifest)
    return [Record(w, z[f"t_{w}"], z[w], 90.0, horizon) for w in ids]


def _horizon(manifest: dict | None) -> float:
    """The forecast horizon on the simulator's time scale: origin + H x 90 / W."""
    m = manifest or json.loads((TEST_DIR / "manifest.json").read_text())
    return 90.0 + float(m["H"]) * 90.0 / float(m["W"])


def load_dev():
    recs = _load(DEV_DIR / "series.npz")
    labels = json.loads((DEV_DIR / "labels.json").read_text())
    y = np.array([labels[r.world_id]["transitioned"] for r in recs], dtype=bool)
    groups = np.array([labels[r.world_id]["group"] for r in recs])
    return recs, y, groups


def load_test():
    manifest = json.loads((TEST_DIR / "manifest.json").read_text())
    return _load(TEST_DIR / "series.npz", manifest)


def n_points() -> int:
    manifest = json.loads((TEST_DIR / "manifest.json").read_text())
    return int(round(float(manifest["W"]) / float(manifest["step_years"])))


# --- methods: each fit(dev recs, dev y) -> predict(recs) -> p ------------------

def _logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


class M0:
    def fit(self, recs, y):
        self.p = float(y.mean()); return self

    def predict(self, recs):
        return np.full(len(recs), self.p)


class M1:
    """Own history: extrapolate the record's trend with AR(1) noise, and count how often it
    falls below half of the record's maximum within the horizon -- the pre-registered
    area-loss event, applied to the record's own extrapolation. Calibrated on real dev.

    The simulator version (`methods.baselines.OwnHistory`) requires a departure to hold
    for 60 time units, but the real horizon is only 45 on the same scale, so it could
    never fire (every forecast came out constant in a dry run on stand-in data). The
    pre-registered event itself needs no hold, so it is used here.
    """

    n_paths = 400

    def raw(self, recs):
        return np.array([self._p(r) for r in recs])

    def _p(self, r):
        rng = np.random.default_rng(zlib.crc32(r.world_id.encode()))
        ly = np.log(np.maximum(r.y, 1e-9))
        t = np.asarray(r.t, dtype=float)
        tc = t - t.mean()
        beta = np.polyfit(tc, ly, 1)
        resid = ly - np.polyval(beta, tc)
        phi = float(np.clip(np.corrcoef(resid[:-1], resid[1:])[0, 1], -0.95, 0.95)) \
            if resid.std() > 0 else 0.0
        phi = 0.0 if not np.isfinite(phi) else phi
        sigma = float(resid.std()) or 1e-6
        n_eff = max(len(resid) * (1 - phi) / (1 + phi), 3.0)
        se = sigma / np.sqrt(np.sum(tc ** 2)) * np.sqrt(len(resid) / n_eff)
        dt = float(np.median(np.diff(t)))
        steps = np.arange(r.origin, r.horizon + 1e-9, dt)
        slopes = beta[0] + se * rng.standard_normal(self.n_paths)
        e = np.full(self.n_paths, resid[-1])
        low = np.full(self.n_paths, np.inf)
        for s_ in steps:
            e = phi * e + sigma * np.sqrt(1 - phi ** 2) * rng.standard_normal(self.n_paths)
            v = beta[1] + slopes * (s_ - t.mean()) + e
            low = np.minimum(low, v)
        p = float(np.mean(low < np.log(0.5 * np.max(r.y))))
        return float(np.clip(p, 0.5 / self.n_paths, 1 - 0.5 / self.n_paths))

    def fit(self, recs, y):
        self.cal = LogisticRegression().fit(_logit(self.raw(recs))[:, None], y); return self

    def predict(self, recs):
        return self.cal.predict_proba(_logit(self.raw(recs))[:, None])[:, 1]


class M2:
    """Generic early-warning signals: Kendall tau of rolling AC and variance -> logistic."""

    def fit(self, recs, y):
        self.m = LogisticRegression().fit(self._x(recs), y); return self

    @staticmethod
    def _x(recs):
        return np.array([ews_indicators(r.t, r.y) for r in recs])

    def predict(self, recs):
        return self.m.predict_proba(self._x(recs))[:, 1]


class _SimTrained:
    """Trained on the simulator's development pool only; the real dev half is ignored."""

    cls = None

    def fit(self, recs, y):
        worlds, _ = pickle.loads(SIM_POOL.read_bytes())
        # Match the real records' sampling: 20 (or 30) regular points over the record.
        layer = Realism(keep_fraction=n_points() / 90.0)
        rng = np.random.default_rng(7)
        sim = [Record(w.world_id, *w.record(layer, rng), w.origin, T) for w in worlds]
        self.m = self.cls().fit(sim, [w.sealed_truth() for w in worlds])
        return self

    def predict(self, recs):
        return np.array([self.m.predict(r).p_transition for r in recs])


class M3(_SimTrained):
    cls = FeatureClassifier


class M4(_SimTrained):
    cls = Hybrid


class M5:
    """The feature classifier's whether-model, trained on the real dev half."""

    def fit(self, recs, y):
        self.m = _calibrated(np.array([physical_features(r) for r in recs]), y); return self

    def predict(self, recs):
        X = np.array([physical_features(r) for r in recs])
        return self.m.predict_proba(X)[:, list(self.m.classes_).index(True)]


class M6:
    """Fragility at rest: lag-1 autocorrelation and coefficient of variation -> logistic."""

    cols = [FEATURE_NAMES.index("lag1_ac"), FEATURE_NAMES.index("cv")]

    def _x(self, recs):
        return np.nan_to_num(np.array([features(r.t, r.y)[self.cols] for r in recs]))

    def fit(self, recs, y):
        self.m = LogisticRegression().fit(self._x(recs), y); return self

    def predict(self, recs):
        return self.m.predict_proba(self._x(recs))[:, 1]


CLASSES = dict(zip(METHODS, (M0, M1, M2, M3, M4, M5, M6)))


# --- steps --------------------------------------------------------------------

def auc_ci(y, p, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    point = float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else float("nan")
    boots = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i):
            boots.append(roc_auc_score(y[i], p[i]))
    return point, [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]


def cmd_dev(_):
    """Grouped 5-fold CV on the dev half. A sanity check, not a result."""
    recs, y, groups = load_dev()
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"dev: {len(recs)} windows, {len(set(groups))} polities, {int(y.sum())} events")
    res = {}
    for name, cls in CLASSES.items():
        # AUC is averaged within folds. Pooling predictions across folds makes even a
        # constant forecast score away from 0.5, because each fold's constant differs
        # (the base rate came out at 0.38 that way in a dry run).
        fold_aucs = []
        sim_model = cls().fit(None, None) if name in ("M3_feature_clf_sim", "M4_hybrid_sim") else None
        for tr, te in GroupKFold(5).split(recs, y, groups):
            m = sim_model or cls().fit([recs[i] for i in tr], y[tr])   # sim models: no real data
            p = m.predict([recs[i] for i in te])
            if 0 < y[te].sum() < len(te):
                fold_aucs.append(roc_auc_score(y[te], p))
        res[name] = dict(auc_fold_mean=float(np.mean(fold_aucs)),
                         auc_fold_sd=float(np.std(fold_aucs)), folds=len(fold_aucs))
        print(f"  {name:22s} dev AUC (mean over grouped folds) {np.mean(fold_aucs):.3f} "
              f"(sd {np.std(fold_aucs):.3f}, {len(fold_aucs)} folds)")
    (OUT / "dev_cv.json").write_text(json.dumps(res, indent=2))


def cmd_forecast(_):
    recs, y, _groups = load_dev()
    test = load_test()
    FC_DIR.mkdir(parents=True, exist_ok=True)
    for name, cls in CLASSES.items():
        p = cls().fit(recs, y).predict(test)
        path = FC_DIR / f"{name}.json"
        path.write_text(json.dumps({r.world_id: dict(p_transition=float(q))
                                    for r, q in zip(test, p)}, sort_keys=True))
        print(f"registered {path.name} {blind.register_forecasts(path, TEST_SET, name)[:12]}")


def cmd_score(_):
    OUT.mkdir(parents=True, exist_ok=True)
    fcs = {}
    for name in METHODS:
        path = FC_DIR / f"{name}.json"
        blind.check_forecast(path, TEST_SET)
        fcs[name] = json.loads(path.read_text())
    truth = {t["world_id"]: t for t in blind.unseal(TEST_SET)}
    ids = sorted(truth)
    y = np.array([truth[w]["transitioned"] for w in ids], dtype=bool)
    kind = np.array([truth[w]["event_kind"] or "none" for w in ids])
    res = dict(n=len(ids), n_events=int(y.sum()), base_rate=float(y.mean()))
    print(f"test: {len(ids)} windows, {int(y.sum())} events (base rate {y.mean():.3f})")
    ref = float(np.mean((y.mean() - y) ** 2))
    for name in METHODS:
        p = np.array([fcs[name][w]["p_transition"] for w in ids])
        auc, ci = auc_ci(y, p)
        row = dict(auc=auc, auc_ci=ci, brier=float(np.mean((p - y) ** 2)))
        row["brier_skill"] = 1 - row["brier"] / ref if ref > 0 else float("nan")
        for k in ("area_loss", "ending"):
            sel = (kind == k) | ~y
            if (kind == k).sum() >= 5:
                row[f"auc_{k}"] = auc_ci(y[sel], p[sel])[0]
        res[name] = row
        print(f"  {name:22s} AUC {auc:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]  Brier skill {row['brier_skill']:+.3f}  "
              + "  ".join(f"{k} {row[k]:.3f}" for k in row if k.startswith("auc_") and k != "auc_ci"))
    (OUT / "test_scores.json").write_text(json.dumps(res, indent=2))
    print(f"wrote {OUT / 'test_scores.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["dev", "forecast", "score"])
    args = ap.parse_args()
    dict(dev=cmd_dev, forecast=cmd_forecast, score=cmd_score)[args.step](args)


if __name__ == "__main__":
    main()
