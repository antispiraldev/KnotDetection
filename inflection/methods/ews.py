"""Generic early-warning signals: rising autocorrelation and variance (Scheffer et al. 2009).

The standard recipe (Dakos et al. 2012), applied unchanged to every record:

1. interpolate onto an even grid, and take logs, because the noise is multiplicative;
2. detrend with a Gaussian kernel smoother (bandwidth `bw_frac` of the record);
3. in a rolling window (`win_frac` of the record), compute the lag-1 autocorrelation
   and the variance of the residuals;
4. measure the trend of each indicator by Kendall's tau against time.

The two taus are the method's entire view of the record. The textbook verdict is a
yes/no on whether both are significantly positive. Here they are turned into
probabilities by logistic regressions fitted on the development pool: one for
whether, one multinomial for what. That is the most generous reading of EWS that is
still just EWS -- it lets the data say how much a given tau is worth, but adds
nothing the indicators themselves don't carry. "When" is outside what EWS claim to
answer, so it is the development-pool onset distribution.

Jäger & Füllsack (2019) show that this recipe produces systematic false positives.
The null false-positive rate is scored for exactly that reason.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.stats import kendalltau
from sklearn.linear_model import LogisticRegression

from inflection.sim.models import TRANSITION_TYPES

from .base import Forecast, Method, Record
from .baselines import BaseRate, uniform_grid


def ews_indicators(t: np.ndarray, y: np.ndarray, bw_frac: float = 0.10,
                   win_frac: float = 0.50) -> tuple[float, float]:
    """Kendall tau of rolling lag-1 AC and of rolling variance, after detrending."""
    _, g, _ = uniform_grid(t, y)
    lg = np.log(np.maximum(g, 1e-9))
    if len(lg) < 12:
        return 0.0, 0.0
    resid = lg - gaussian_filter1d(lg, sigma=max(bw_frac * len(lg), 1.0), mode="nearest")
    w = max(int(win_frac * len(resid)), 6)
    win = np.lib.stride_tricks.sliding_window_view(resid, w)
    c = win - win.mean(axis=1, keepdims=True)
    var = (c ** 2).mean(axis=1)
    ac = (c[:, 1:] * c[:, :-1]).sum(axis=1) / np.maximum((c ** 2).sum(axis=1), 1e-12)
    idx = np.arange(len(var))
    tau_ac = kendalltau(idx, ac).statistic
    tau_var = kendalltau(idx, var).statistic
    return float(np.nan_to_num(tau_ac)), float(np.nan_to_num(tau_var))


class GenericEWS(Method):
    name = "generic_ews"

    def fit(self, records, truths):
        X = np.array([ews_indicators(r.t, r.y) for r in records])
        self.fallback = BaseRate().fit(records, truths)
        self.whether = LogisticRegression().fit(X, [tr["transitioned"] for tr in truths])
        self.what = LogisticRegression(max_iter=1000).fit(
            X, [tr["transition_type"] for tr in truths])
        return self

    def predict(self, record: Record) -> Forecast:
        x = np.array([ews_indicators(record.t, record.y)])
        p = float(self.whether.predict_proba(x)[0, list(self.whether.classes_).index(True)])
        probs = dict(zip(self.what.classes_, self.what.predict_proba(x)[0].tolist()))
        return Forecast(p, self.fallback.q, {k: probs.get(k, 0.0) for k in TRANSITION_TYPES})
