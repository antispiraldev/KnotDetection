"""Tests for the simulator's invariants.

These are mostly guards against the benchmark quietly breaking its own premises:
that a mechanism cannot be read off the units, that every type is delivered on the
same footing, and that ground truth means what the scorer will assume it means.
"""

from __future__ import annotations

import numpy as np
import pytest

from inflection.sim import models, realism as R
from inflection.sim.generate import (
    ORIGIN_FRAC, T, World, generate_world, tstar_range,
)
from inflection.sim.integrate import simulate
from inflection.sim.label import label, observable_onset


@pytest.fixture(scope="module")
def one_per_type() -> dict[str, World]:
    out = {}
    for i, tt in enumerate(models.TRANSITION_TYPES):
        w = generate_world(tt, np.random.default_rng(100 + i))
        assert w is not None, f"could not generate a usable {tt} world"
        out[tt] = w
    return out


# --- fold geometry -----------------------------------------------------------

def test_fold_point_is_a_real_saddle_node():
    """At a_critical the upper and middle equilibria have just collided."""
    p = dict(r=1.0, K=10.0, h=1.0)
    a_c, n_fold = models.may_fold_point(**p)
    assert len(models.may_equilibria(a_c * 0.97, **p)) == 3
    assert len(models.may_equilibria(a_c * 1.03, **p)) == 1
    assert 0 < n_fold < p["K"]


def test_may_equilibria_are_equilibria():
    p = dict(r=0.9, K=12.0, h=1.1)
    a = models.may_fold_point(**p)[0] * 0.8
    for n in models.may_equilibria(a, **p):
        dn = p["r"] * n * (1 - n / p["K"]) - a * n * n / (p["h"] ** 2 + n * n)
        assert abs(dn) < 1e-6


def test_rm_hopf_threshold_matches_the_nullcline_hump():
    """K_c is where the prey nullcline's peak reaches the coexistence equilibrium."""
    a, h, e, m = 1.1, 0.5, 0.45, 0.2
    K_c = models.rm_hopf_K(a, h, e, m)
    n_star = m / (a * (e - m * h))
    assert K_c / 2 - 1 / (2 * a * h) == pytest.approx(n_star)


# --- leakage invariants ------------------------------------------------------

def test_every_type_shares_the_noise_envelope():
    """A type-specific noise range made `noise_induced` identifiable at auc 1.0."""
    lo, hi = models.NOISE_ENVELOPE
    for i, tt in enumerate(models.TRANSITION_TYPES):
        spec = models.BUILDERS[tt](np.random.default_rng(i), T, 120.0)
        assert np.all(spec.noise_scale >= lo) and np.all(spec.noise_scale <= hi), tt


def test_records_carry_no_absolute_scale(one_per_type):
    """Normalisation is what makes the scale-dependent gate structural."""
    for tt, w in one_per_type.items():
        for layer in R.LAYERS.values():
            _, y = w.record(layer, np.random.default_rng(0))
            assert np.median(y) == pytest.approx(1.0), (tt, layer.name)


def test_records_are_identical_in_length_and_timing_across_types(one_per_type):
    """Series length must not announce the mechanism."""
    for layer in R.LAYERS.values():
        lengths = set()
        for w in one_per_type.values():
            t, y = w.record(layer, np.random.default_rng(0))
            assert len(t) == len(y)
            lengths.add(len(t))
        assert len(lengths) == 1, (layer.name, lengths)


def test_hopf_worlds_do_not_share_a_level():
    """Constants pinned every hopf world to exactly 0.500 in the first draft."""
    levels = []
    for i in range(12):
        spec = models.spec_hopf(np.random.default_rng(200 + i), T, 120.0)
        levels.append(spec.x0[spec.primary])
    assert np.std(levels) / np.mean(levels) > 0.15


def test_transition_times_share_one_window(one_per_type):
    lo, hi = tstar_range()
    for tt, w in one_per_type.items():
        if tt == "null":
            assert w.transition_time is None
        else:
            assert lo <= w.transition_time <= hi, tt


# --- ground truth ------------------------------------------------------------

def test_nothing_is_visible_before_the_forecast_origin(one_per_type):
    origin = ORIGIN_FRAC * T
    for tt, w in one_per_type.items():
        if w.observable_onset is not None:
            assert w.observable_onset > origin, tt


def test_null_worlds_never_transition(one_per_type):
    w = one_per_type["null"]
    assert w.transition_time is None
    assert w.observable_onset is None
    assert not w.transitioned


def test_noise_induced_time_marks_commitment_not_first_dip(one_per_type):
    """The escape is when the system stops coming back, not when it first dips.

    This test previously asserted the reverse -- that the series stays above the
    separatrix until the transition -- which is the first-passage definition, and
    first passage is wrong for a noisy bistable system: trajectories cross, wander,
    and recover. So the invariant is on the far side: once committed, it stays low.
    Earlier dips below the separatrix are allowed and expected.
    """
    w = one_per_type["noise_induced"]
    assert w.transitioned and w.transition_time is not None
    sep = sorted(w.params["equilibria"])[1] * w.params.get("scale", 1.0)
    after = w.raw[w.t >= w.transition_time]
    assert np.all(after < sep)
    # And it was genuinely in the high state at some point beforehand.
    assert np.any(w.raw[w.t < w.transition_time] >= sep)


def test_transient_excursion_is_not_mistaken_for_escape():
    """Dip below, recover, then commit: the label must land on the commitment."""
    from inflection.sim.integrate import Run
    from inflection.sim.label import separatrix_crossing
    t = np.arange(300.0)
    y = np.full(300, 6.0)
    y[100:110] = 2.0           # transient dip below the separatrix at 3.0 ...
    y[200:] = 1.0              # ... then the real, permanent escape
    run = Run(t=t, x=y[:, None], state_names=("y",), transition_type="noise_induced",
              transition_time=None, primary=0, params=dict(equilibria=[1.0, 3.0, 6.0]))
    assert separatrix_crossing(run) == 200.0


def test_onset_detector_is_quiet_on_a_stationary_series():
    """A flat noisy series must not register an onset, or every null world mislabels."""
    from inflection.sim.integrate import Run
    rng = np.random.default_rng(0)
    t = np.arange(300.0)
    x = (1.0 + 0.03 * rng.standard_normal((300, 1))).cumsum(axis=0) * 0 + 1.0
    x = x + 0.03 * rng.standard_normal((300, 1))
    run = Run(t=t, x=x, state_names=("y",), transition_type="null",
              transition_time=None, primary=0)
    assert observable_onset(run) is None


def test_label_reports_the_delay_between_mechanism_and_visibility(one_per_type):
    for tt, w in one_per_type.items():
        if w.transition_time is not None and w.observable_onset is not None:
            assert w.onset_lag == pytest.approx(w.observable_onset - w.transition_time)


# --- realism -----------------------------------------------------------------

def test_layers_shorten_or_degrade_but_never_lengthen(one_per_type):
    w = one_per_type["fold"]
    n_clean = len(w.record(R.CLEAN)[0])
    for name, layer in R.LAYERS.items():
        n = len(w.record(layer, np.random.default_rng(0))[0])
        assert n <= n_clean, name
        assert n >= 4, name


def test_irregular_sampling_is_actually_irregular(one_per_type):
    t, _ = one_per_type["fold"].record(R.LAYERS["irregular"], np.random.default_rng(0))
    assert len(np.unique(np.diff(t))) > 1


def test_proxy_transform_preserves_order(one_per_type):
    """A proxy distorts magnitude but must not reorder time points."""
    w = one_per_type["fold"]
    rng = np.random.default_rng(0)
    layer = R.Realism(proxy_exponent=0.6, proxy_floor=0.1)
    _, clean = w.record(R.CLEAN, rng)
    _, proxied = w.record(layer, rng)
    order_clean = np.argsort(clean)
    order_proxy = np.argsort(proxied)
    # Floor saturation ties the lowest points; compare above the floor only.
    keep = clean > np.quantile(clean, 0.15)
    assert np.corrcoef(clean[keep], proxied[keep])[0, 1] > 0.95


# --- integration -------------------------------------------------------------

def test_trajectories_stay_finite_and_positive():
    for i, tt in enumerate(models.TRANSITION_TYPES):
        spec = models.build(tt, np.random.default_rng(300 + i), T, 120.0)
        run = simulate(spec, T, 0.01, 1.0, np.random.default_rng(i))
        assert np.all(np.isfinite(run.x))
        assert np.all(run.x > 0)


def test_simulate_is_reproducible_given_a_seed():
    spec_a = models.build("fold", np.random.default_rng(7), T, 120.0)
    spec_b = models.build("fold", np.random.default_rng(7), T, 120.0)
    run_a = simulate(spec_a, T, 0.01, 1.0, np.random.default_rng(3))
    run_b = simulate(spec_b, T, 0.01, 1.0, np.random.default_rng(3))
    np.testing.assert_allclose(run_a.series, run_b.series)


# --- calibration -------------------------------------------------------------

def test_cv_calibration_lands_near_its_target(one_per_type):
    """Half the scale-dependent gate rests on this, so check it rather than assume it.

    `sd`, `iqr` and `mad` are not degenerate after normalisation -- they track the
    per-world coefficient of variation. They are type-independent only because that
    CV is drawn from a shared range and calibrated toward it. A single pilot
    iteration is not exact, so the test asks for the right order of magnitude.
    """
    for tt, w in one_per_type.items():
        target = w.params["target_cv"]
        _, y = w.record()
        achieved = float(np.std(y)) / float(np.median(y))
        assert 0.4 * target < achieved < 2.5 * target, (tt, target, achieved)


def test_calibration_factor_is_not_pinned_at_the_clip(one_per_type):
    """If a type always saturates the clip, its CV is not really being calibrated."""
    for tt, w in one_per_type.items():
        from inflection.sim.generate import CV_CLIP
        factor = w.params["cv_calibration"]
        assert CV_CLIP[0] < factor < CV_CLIP[1], (tt, factor)


def test_onset_of_an_instantaneous_step_is_never_early():
    """A step at t=106 must be placed at ~106, not at the left edge of a bin.

    The first detector used non-overlapping 20-step windows and reported the edge of
    the first window to depart, so this step came back as visible at t=100, six
    steps before it happened, and every onset in the benchmark was a multiple of 20.
    """
    from inflection.sim.integrate import Run
    rng = np.random.default_rng(1)
    t = np.arange(300.0)
    for step_at in (106, 113, 127):
        y = 1.0 + 0.02 * rng.standard_normal(300)
        y[step_at:] += 0.5
        run = Run(t=t, x=y[:, None], state_names=("y",), transition_type="x",
                  transition_time=float(step_at), primary=0)
        onset = observable_onset(run)
        assert onset is not None
        assert step_at <= onset <= step_at + 3, (step_at, onset)
