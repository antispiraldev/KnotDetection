"""Euler-Maruyama integration of a Spec into a trajectory."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .models import Spec


@dataclass
class Run:
    t: np.ndarray
    x: np.ndarray
    state_names: tuple[str, ...]
    transition_type: str
    transition_time: float | None
    primary: int
    params: dict = field(default_factory=dict)

    @property
    def series(self) -> np.ndarray:
        return self.x[:, self.primary]


def simulate(spec: Spec, T: float, dt: float, obs_step: float, rng: np.random.Generator) -> Run:
    n_steps = int(round(T / dt))
    keep_every = int(round(obs_step / dt))
    x = spec.x0.astype(float).copy()
    sqrt_dt = np.sqrt(dt)

    shock_step = None
    if spec.shock is not None:
        shock_step = int(round(spec.shock[0] / dt))

    out_t, out_x = [0.0], [x.copy()]
    for step in range(1, n_steps + 1):
        t = step * dt
        if shock_step is not None and step == shock_step:
            x = spec.shock[1].astype(float).copy()
        drift = spec.rhs(t, x)
        # Multiplicative noise keeps fluctuations proportional to population size,
        # which is what demographic and proxy series actually look like.
        diffusion = spec.noise_scale * x * rng.standard_normal(x.shape) * sqrt_dt
        x = np.maximum(x + drift * dt + diffusion, spec.floor)
        if step % keep_every == 0:
            out_t.append(t)
            out_x.append(x.copy())

    return Run(
        t=np.array(out_t),
        x=np.array(out_x),
        state_names=spec.state_names,
        transition_type=spec.transition_type,
        transition_time=spec.transition_time,
        primary=spec.primary,
        params=dict(spec.params),
    )
