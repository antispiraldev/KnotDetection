# Research log

Running record of what was tried, what was dropped, what is still open, and ideas
parked as out of scope. Newest entries at the top.

---

## 2026-09-21 — Session 2 (beelink). Gate 1 approved; Gate 2 work begins

### Recovering from the power loss

The System76 session ended mid-flight. Recovered state: `RESEARCH_PLAN.md` complete,
`sim/models.py` and `sim/integrate.py` written but never executed, all other package
directories empty, nothing ever committed. No transcript of that session survived, so
the code was reviewed on its own terms rather than against remembered intent.

The `.venv` had been built on the laptop against Python 3.12 and its interpreter
symlink now resolved to the beelink's 3.14, so nothing imported. Rebuilt; Luca
installed `python3-venv` and `python3-pip`. Stack now: numpy 2.5.3, scipy 1.18.1,
statsmodels, ruptures, matplotlib, scikit-learn 1.9.1, pytest. `statsmodels`,
`ruptures` and `torch` were listed in the plan but had never been installed; torch is
still not installed and is not needed until the deep-learning comparison.

Note for future sessions: numpy 2.x removed `ndarray.ptp()`. Use `np.ptp(arr)`.

### The simulator ran, and then the audit found the real problem

Five of the seven transition types produced sensible trajectories on first execution.
Two did not, and chasing those two turned up something considerably more important.

**Calibration problems (the small findings).**

- `noise_induced` escaped almost immediately — first-decile mean 1.81 against a
  starting level of 6.37, with 25% of escapes before t=40, leaving too little
  pre-transition record to forecast from.
- `hopf` showed almost no amplitude growth. With noise switched off entirely, the
  deterministic run's peak-to-peak *fell* from 0.005 to 0.001 across the bifurcation.
  The formula for the critical carrying capacity was correct (`K_c = 2n* + 1/(ah)`,
  verified against the prey-nullcline hump). The trajectory simply starts exactly on
  the equilibrium and follows it as it drifts, so past `K_c` the instability grows
  only from floating-point roundoff. **That is a genuine reproducibility hazard**: the
  length of the delay depends on roundoff, which is not stable across machines or BLAS
  versions — on a project that had just changed machines. Fixed by letting noise seed
  the cycle and giving it time, not by perturbing the initial condition, which decays
  harmlessly while the equilibrium is still strongly attracting.

**The bifurcation delay is real and is now carried as a separate label.** In a swept
supercritical Hopf, amplitude grows like `sqrt(K - K_c)` from whatever seeds it, so
cycles become visible long after the parameter crossing — median lag ~60 time units in
calibration, varying run to run. Scoring "when" against the parameter crossing alone
would charge every method for a delay belonging to the system. Each world now records
both `transition_time` (the mechanism changes) and `observable_onset` (the series
visibly departs), the latter measured from the finished trajectory by
`sim/label.py`, which looks for a sustained level shift *or* a sustained amplitude
shift, because the Hopf moves its variance while leaving its mean alone.

### The finding that mattered: the first simulator was trivially fingerprintable

Prompted by the plan's §8 circularity worry, I asked a narrower question: can a cheap
classifier name the transition type from summary statistics of the *pre-transition*
window, where by construction nothing has happened yet?

It could, at 0.71 accuracy against a 0.143 base rate. Worse, two types were perfectly
separable on a single feature:

| Leak | Feature | AUC | Cause |
|---|---|---|---|
| `noise_induced` | step-to-step noise | 1.000 | the only type with a loud noise range |
| `hopf` | series level | 0.987 | `n* = m/(a(e-mh))` built from constants — *every* hopf world sat at exactly 0.500 |
| `transcritical` | trend | 0.999 | its control parameter swept from t=0 while other types were still flat |

This is the plan's circularity failure mode, but sharper than the plan anticipated.
The plan guards against methods sharing *assumptions* with the simulator. The actual
defect was shared *constants*: a method could score well on sub-question 3 while
detecting nothing whatsoever, by recognising the simulator's parameter ranges. Any
"what" result from the first draft would have been worthless.

**Fixes, each aimed at a cause rather than a symptom:**

1. *Common noise envelope.* All types draw from `models.NOISE_ENVELOPE`.
   `noise_induced` gets its escapes from basin geometry instead — parked at 98.5–99.6%
   of the fold, where the barrier is low. Calibration: at `a/a_c = 0.995` with noise
   0.020, 22 of 30 runs escape with median time 110.
2. *Randomised everything that was constant.* May parameters (`r`, `K`, `h`) and the
   full Rosenzweig–MacArthur parameter set now vary per world.
3. *Shared drift-start window.* Swept types hold their control parameter fixed until a
   drift-start time drawn from one common range that straddles the forecast origin. In
   some worlds the drift is under way when the record is truncated and a trend is there
   to be found; in others it has not begun and there is nothing to see. That spread is
   now a designed feature of benchmark difficulty rather than an accident.
4. *Per-world time scale.* Model families relax at different intrinsic rates, which a
   fixed observation interval converts into a per-type signature. A shared random time
   scale makes the rates overlap, with noise scaled by `sqrt(tau)` so this varies
   relaxation without varying fluctuation size.
5. *Arbitrary units.* The delivered series is divided by the median of the window a
   method is allowed to see. Historical proxies carry no absolute scale anyway, and
   this makes level leakage structurally impossible rather than merely unlikely.
6. *Calibrated fluctuation amplitude.* See below.

### A distinction the audit forced, and it is the useful part

The first audit gated every informative feature. That is wrong, and would have
quietly destroyed the experiment: **rising autocorrelation before a fold is critical
slowing down — the phenomenon under study.** An audit demanding that it carry no
information about type could only be passed by building a simulator in which
early-warning signals do not work, which would answer the research question in
advance and in the wrong direction.

Two attempts at drawing the line:

- *First attempt: static vs temporal.* Gate the levels, measure the changes, on the
  grounds that critical slowing down is a claim about rise rather than level. This
  broke immediately — once the delivered series is normalised by its median, `sd` and
  `cv` are the same number, so the same quantity sat in both tiers.
- *Second attempt, kept: scale-dependent vs physical.* Gate only what changes when the
  series is multiplied by a constant — level, spread, record length. Normalisation
  makes those degenerate *by construction*, so the gate is structural and cannot drift
  back to informative the way a tuned parameter range can. Everything else is physics
  that methods are entitled to use, measured and reported prominently so that nobody
  mistakes benchmark difficulty for a finding.

That leaves relative spread (`cv`) on the physical side, where a problem remained:
`hopf` sat at CV 0.148 against 0.02–0.05 for every other type, while at `K/K_c ≈ 0.7`
— nowhere near its bifurcation. The high variance is not proximity to a threshold; it
is Rosenzweig–MacArthur having weakly damped oscillatory modes. An artifact of the
equations chosen to represent the type, so the generator now calibrates it: each world
draws a target CV from a shared range and a pilot run rescales the noise to hit it.

Two encouraging signs from the same measurements, both by construction and both
confirmed: `null` and `mechanism_change` are statistically indistinguishable before
the change, and so are `noise_induced` and `exogenous_shock`. Those are the two pairs
that *should* be hard, and they are.

### Status

- Simulator: seven types, randomised, audited. `sim/{models,integrate,label,generate}.py`.
- Leakage audit: `eval/leakage.py`, two-tier, with a structural gate.
- Still to do before Gate 2: realism layers, example trajectory figures, tests, and a
  first commit.

### Open questions

- The plan's §4.1 table predicts "little or no" warning signal for `noise_induced`.
  Under the shallow-basin design that is no longer right: a shallow basin is a
  near-critical basin, so variance *is* elevated — but flat rather than rising. The
  prediction should become "elevated but trendless", which also makes it share a
  signature with `fold` and `exogenous_shock` rather than being the odd one out.
  Needs Luca's sign-off as a change to the plan's stated expectations.
- Rejection sampling conditions the escape-time distribution for `noise_induced`
  (currently ~13 attempts per accepted world). That selects which worlds enter the
  benchmark; it does not alter the physics inside any world. Recorded in the manifest,
  but worth stating plainly in any write-up.
- Whether the absolute level of lag-1 autocorrelation should be gated too. Argument
  for: its informativeness depends on the observation interval, which is arbitrary.
  Argument against: unlike variance it is scale-free and interpretable from a single
  record without a reference. Currently on the physical side, reported not gated.

### Parked ideas (out of scope under §2)

- Sweeping the observation interval as a realism layer in its own right — the Hopf
  work suggests the interval relative to system time scale matters more than series
  length does. Interesting, but it is a fourth sub-question.
- The bifurcation delay is itself forecastable in principle: if a method can identify
  the crossing, the lag to visibility is partly predictable from the sweep rate. That
  is a genuinely novel "when" target and it is not in the plan.
