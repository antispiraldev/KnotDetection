# Research log

Running record of what was tried, what was dropped, what is still open, and ideas
parked as out of scope. Newest entries at the top.

---

## 2026-09-21 (later) — What the Gate 2 figures and a second audit draw turned up

The first Gate 2 run passed the leakage gate. Looking at the example trajectories, and
then regenerating, showed that the pass had been partly luck. Five defects, all fixed,
plus two open design questions for Luca.

### 1. `noise_induced` ground truth was wrong

The example figure put the "transition" at t≈118. The series then visibly recovered
to the high state and did not commit to the low one until t≈240. The label used first
passage below the separatrix, and a noisy bistable system crosses, wanders, and comes
back. It now uses the **last departure**, the point after which the system never
returns (`label.separatrix_crossing`). The test that asserted first-passage semantics
was itself wrong, so it was rewritten, and a synthetic dip → recover → commit case was
added.

### 2. The gate was measuring the random draw

After the label fix, the same generator run again scored +0.063 excess, up from
−0.011, and the verdict flipped from PASS to FAIL. The `exogenous_shock` model had not
changed. The label fix alters how many `noise_induced` worlds get rejected, which
shifts the random stream for every type generated afterwards, so these were different
worlds. With 7 classes of 25 worlds each, a fixed 0.05 threshold on cross-validated
accuracy is inside the sampling noise. The gate now builds a **label-permutation
null** for the pool and fails only if the leak is *significant* (p < 0.05) *and*
*material* (more than 0.05 above chance). Either condition alone misfires: size alone
fails small pools on noise, and significance alone fails large pools on leaks too
small to exploit.

### 3. `exogenous_shock` was being made identifiable by selection

The second draw was not only noise, though. The audit singled out `exogenous_shock`
by spread (`sd` AUC 0.80), and the cause turned out to be real. Two routes led to it,
and both are fixed.

- **Selection on a design variable** (diagnosed by a parallel session; see the note
  below). The target CV was redrawn on every retry, so the rejection loop filtered it.
  A loud, near-critical shock world tends to escape on its own before its shock
  arrives, gets rejected, and redraws. Accepted shock worlds ended up with a median
  target CV of **0.045 against an unbiased 0.085**, while every other type sat at
  0.074–0.094. I confirmed this against the pre-fix pool. **Rule adopted: design
  variables are assigned before the rejection loop and held fixed through retries.**
  A variable the gate treats as nuisance must be assigned where selection cannot act
  on it.
- **A corrupted calibration pilot.** When a near-critical pilot escapes inside the
  calibration window, the collapse makes std/median enormous and the noise gets cut
  to the clip. Three of 25 shock worlds arrived that way. `noise_induced` undoes this
  damage itself, because a nearly silent world never escapes and is rejected.
  `exogenous_shock` imposes its transition, so it accepted those worlds with a tenth
  of the proper noise. A pilot that transitions now causes a redraw.

The lesson generalises. Rejection sampling is safe only when nothing it can select
on is something the audit assumes is independent of type. The two types differ in
exactly one respect, whether the transition is emergent or imposed, and that decided
whether the bias corrected itself or survived into the pool.

### 4. Float-dust AUCs in the report

`median` and `log_median` showed up at AUC 0.76. The generator pins both to a
constant, 1 ± 1e-16 and 0 ± 1e-16, so the rank test was finding structure in rounding
error. The fix needs both a relative and an absolute tolerance, because `log_median`
sits at zero: its spread is the same size as its values. Harmless to the verdict, but
it would have misled anyone reading the report.

Also corrected: I had documented the scale-dependent gate as structural throughout.
Only `median`, `log_median` and `n_points` are degenerate by construction. `sd`,
`iqr` and `mad` track the per-world CV, so that half of the gate depends on the
calibration working. Defect 3 is exactly that failure. Tests now check that the CV
lands near its target and that no type sits pinned against the clip.

### 5. Observable onsets were quantised and reported early

The regenerated example figure had every orange onset line at exactly 100, 120 or
140. The detector used non-overlapping 20-step windows and reported the *left edge*
of the first window to depart. A shock landing at t=106 falls in [100, 120) and was
recorded as visible at t=100, six steps before it happened. That is why the
instantaneous types, `exogenous_shock` and `mechanism_change`, showed median lags of
about −5 when their true lag cannot be negative. It also inflated the apparent early
decline of `transcritical`.

This had to be fixed before Gate 2, not after, because `observable_onset` is the
timestamp I am recommending as the "when" target (below). A target with a built-in
early bias of up to 20 steps would have been scored against for the rest of the
project. Onsets are now computed with centred rolling medians at every time step. A
centred median flips only once more than half its window is past a step, so a step
lands where it actually is: a synthetic step at t=106 is now placed at 106–109. The
threshold-crossing definition and its thresholds are unchanged, so this is a
resolution fix, not a redefinition. A test pins it for steps at 106, 113 and 127.

A general point, since it has now happened three times (the first-passage label, the
float-dust AUCs, and this): **each of these was caught by looking at a picture or a
single world, not by an aggregate statistic.** Every summary number looked plausible.
Before each gate, inspect individual worlds, not only tables.

### Open, for Luca: what "when" should mean

The gap between the mechanism change and the first visible change is a property of
each transition type, and it runs in both directions. Measured on the final 274-world
pool, with the onset-resolution fix in place (lag = observable onset − mechanism
change):

| Type | Median lag | 10th–90th pct | Share negative | Why |
|---|---|---|---|---|
| mechanism_change | +1.4 | +0.6 to +2.4 | 0% | instantaneous; this is the detector's own delay |
| exogenous_shock | +0.8 | −6.5 to +2.3 | 17% | instantaneous, but the shallow basin wanders just before the shock |
| fold | +1.5 | −21.5 to +14.1 | 45% | the upper equilibrium descends before the fold point |
| noise_induced | +9.5 | +2.6 to +23.7 | 3% | commitment, then descent past the detection band |
| transcritical | −8.2 | −39.8 to +1.1 | 88% | a smooth slide; t* marks where it *ends* |
| hopf | +19.6 | −13.9 to +66.6 | 23% | amplitude swells before the Hopf point, then the bifurcation delay |

Fold is catastrophic, transcritical is continuous, and the Hopf is continuous with a
delay. A single mechanism-time target would reward different things for different
types: a method that fires on the first visible change would look early on
transcritical and late on hopf while being right about the series both times.

**Recommendation:** score "when" against `observable_onset`, which is defined the same
way for every type and is what a forecaster can actually aim at, and report
mechanism-time error next to it. This changes §4.4, so it is Luca's decision.

**Caveat on that recommendation.** `observable_onset` is operational: it is when
this fixed, deliberately conservative detector fires (6-MAD level shift or 3.5× amplitude
rise, sustained for 60 steps). It is not literally the earliest any detector could
fire, and the docstrings were overstating that. It is conservative for spiky Hopf
cycles in particular. With sharp peaks over long flat troughs, a median-based
amplitude signal mostly sees the troughs, so in the example world the cycles are
visibly growing by t≈150–175 but the onset is recorded at 186. A method that fires
correctly at 160 would be scored early by 26. If onset becomes the target, I would
first calibrate the detector against an oracle, a likelihood-ratio detector that
knows the true pre- and post-change distributions, and report the gap. The oracle
gives a principled floor, and a fixed threshold only gives an arbitrary one.

### Gate 2 status: ready for review

Final pool: 274 worlds, 40 requested per type, seed 11. Figures and audit table are
in `inflection/notebooks/` (`gate2_examples.png`, `gate2_onset_lag.png`,
`gate2_audit.json`), regenerated after every fix above.

- **Leakage gate: passes.** Scale-dependent accuracy is 0.157 against a permutation
  chance level of 0.141 (p = 0.33), and the gate passes on all seven realism layers.
  The closest call is `short` (p = 0.065, +0.048 over chance). The likely reason is
  that a 40-point record is short enough for pre-origin drift to show up in its
  spread, so arguably that is physics leaking into a nuisance feature rather than a
  fingerprint. It is a watch item.
- **Difficulty floor.** A cheap classifier on physical features names the type at
  0.39 against a 0.146 base rate (clean), falling to 0.18 under `harsh`. Any real
  method has to beat that. The strongest single signal is lag-1 autocorrelation,
  which is critical slowing down: what the benchmark is meant to contain.
- **Generation.** `noise_induced` needs about 13 attempts per accepted world and 6 of
  40 failed outright. The generator now records the design values of failures, but
  that change postdates this pool. The next pool will show directly whether failures
  cluster at particular target CVs. Accepted `noise_induced` worlds show no skew in
  target CV.
- **Tests.** 22 passing.

Decisions needed from Luca at Gate 2:
1. The "when" target (above).
2. §4.1's expectation for `noise_induced`: "little or no" warning under the plan,
   "elevated but trendless" under the shallow-basin design.
3. Whether the simulator design as a whole is approved to move on to blind test-set
   generation and the first methods (Gate 3).

### Coordination note: a second session

Partway through, another process of this same conversation turned out to be editing
the working tree. It shares this session's history, which suggests the conversation
was resumed twice. It diagnosed the target-CV selection effect independently and made
the `generate_world` change. We checked that neither had overwritten the other and
agreed that this session owns `sim/`, `eval/`, `tests/` and this log. The other
session stood down and handed over its notes, which are folded into this entry. Luca
should close one of the two.

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
