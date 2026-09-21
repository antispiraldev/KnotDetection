"""The common interface every method implements.

A method sees one record at a time: the pre-origin series of a world, in arbitrary
units, possibly degraded, with its observation times. It returns one `Forecast`
answering the three sub-questions:

- **whether** -- `p_transition`: probability that the world transitions (a sustained,
  visible departure) between the origin and the end of the run. Null worlds do not.
- **when** -- `onset_quantiles`: the method's distribution for `observable_onset`, given
  that a transition happens, as quantiles at `QUANTILE_LEVELS` in absolute time. The
  scorer computes CRPS from them (a quantile-score approximation) and the error of
  the median.
- **what** -- `type_probs`: a distribution over all seven transition types, null
  included. Folding "whether" and "what" together would be tidier, but the plan scores
  them separately and a method may reasonably answer one better than the other.

Methods may `fit` on a labelled development pool. They never see the test pool's
truth: the runner hands them records only, and the scorer reads the truth after the
forecasts are hashed (see `inflection.eval.blind`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from inflection.sim.models import TRANSITION_TYPES

QUANTILE_LEVELS = tuple(np.round(np.arange(0.05, 0.96, 0.05), 2))


@dataclass(frozen=True)
class Record:
    """What a method is given about one world."""
    world_id: str
    t: np.ndarray
    y: np.ndarray
    origin: float           # forecasts are made at this time; every t is < origin
    horizon: float          # end of the run; onsets fall in (origin, horizon]


@dataclass
class Forecast:
    p_transition: float
    onset_quantiles: tuple[float, ...]
    type_probs: dict[str, float] = field(default_factory=dict)

    def validate(self, record: Record) -> "Forecast":
        """Clip and normalise into a well-formed forecast, or raise if hopeless."""
        p = float(np.clip(self.p_transition, 0.0, 1.0))
        q = np.asarray(self.onset_quantiles, dtype=float)
        if q.shape != (len(QUANTILE_LEVELS),) or not np.all(np.isfinite(q)):
            raise ValueError(f"{record.world_id}: need {len(QUANTILE_LEVELS)} finite quantiles")
        q = np.clip(np.maximum.accumulate(q), record.origin, record.horizon)
        probs = np.array([max(0.0, float(self.type_probs.get(k, 0.0))) for k in TRANSITION_TYPES])
        probs = probs / probs.sum() if probs.sum() > 0 else np.full(len(probs), 1 / len(probs))
        return Forecast(p, tuple(q), dict(zip(TRANSITION_TYPES, probs.tolist())))

    def to_json(self) -> dict:
        return dict(p_transition=self.p_transition,
                    onset_quantiles=list(self.onset_quantiles),
                    type_probs=self.type_probs)


class Method:
    """Subclass and implement `predict`; override `fit` if the method learns."""

    name: str = "method"

    def fit(self, records: list[Record], truths: list[dict]) -> "Method":
        return self

    def predict(self, record: Record) -> Forecast:
        raise NotImplementedError

    def forecast_all(self, records: list[Record]) -> dict[str, dict]:
        return {r.world_id: self.predict(r).validate(r).to_json() for r in records}
