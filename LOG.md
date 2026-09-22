# Research log

Running record of what was tried, what was dropped, what is still open, and ideas
parked as out of scope. Newest entries at the top.

---

## 2026-09-22 — Phase 2 first result: real history, blind (`real_v1`)

Unsealed after the seven forecast files were registered and pushed (`66a4f95`). Test:
300 windows, one per polity, 138 events (base rate 0.46). Scores in
`phase2/results/test_scores.json`; seed, answers, identity key and the subagent's
private log are now released in `inflection/data/released/real_v1/`.

| method | AUC (primary) | AUC, S1 (already-collapsed excluded) | AUC, endings only |
|---|---|---|---|
| M0 base rate | 0.500 | 0.500 | 0.500 |
| M1 own history (trend) | 0.643 [0.593, 0.692] | 0.529 [0.479, 0.584] | 0.501 |
| M2 generic EWS | 0.494 [0.427, 0.564] | 0.473 | 0.468 |
| M3 feature clf., sim-trained | 0.510 [0.445, 0.574] | 0.503 | 0.464 |
| M4 hybrid, sim-trained | 0.515 [0.452, 0.582] | 0.518 | 0.484 |
| M5 feature clf., real-trained | 0.650 [0.586, 0.708] | 0.541 [0.470, 0.611] | 0.504 |
| M6 fragility at rest | 0.651 [0.586, 0.713] | 0.559 [0.490, 0.630] | 0.518 |

**The headline is in the S1 column.** 35 of the 36 already-collapsed windows are
events, so the primary AUCs of about 0.65 mostly reward seeing a collapse that is
already in the record. With those 36 windows removed, every method falls to
0.47–0.56 and every interval includes 0.5.

Against the pre-registered hypotheses:

1. **H1 transfer: confirmed, at the bottom of the predicted range.** Methods trained
   on the simulator score 0.51 and 0.52. Simulated fragility does not transfer to
   5-year territorial step data.
2. **H2 fragility at rest: confirmed in the primary analysis (0.65, predicted
   0.55–0.65), not in S1** (0.56, interval includes chance).
3. **H3 classic warning signs at chance: confirmed** (0.49), as in simulation.
4. **H4 momentum: confirmed** (0.64, predicted 0.55–0.65); S1 0.53.
5. **H5 real-trained best: confirmed but tied.** M5 0.650, M6 0.651, M1 0.643 are
   indistinguishable.

The pre-registered falsification criterion — M6's interval including 0.5 *and* M5 no
better than M1 — is not met in the primary analysis, because M6's primary interval
clears 0.5. In S1 both halves of it hold. So the fragility account survives only in
the analysis that counts already-collapsed polities as forecastable.

**The clearest negative result: nothing forecasts a polity's end.** Every method is
at 0.46–0.52 on windows whose event is the polity ceasing to exist. The signal that
exists is entirely about territory already contracting.

**Caveats.** Territorial snapshots at 5-year sampling are a thin proxy for "fragility".
A polity "ending" in Cliopatria mixes conquest, collapse, merger and renaming. One
dataset, one operationalisation, 300 windows. This does not test whether a richer
record (population, elite numbers, state revenue) would carry more.

---

## 2026-09-22 — `real_v1`: dev check and registered forecasts (before unsealing)

Dev, grouped 5-fold CV by polity, mean AUC over folds. This is a sanity check; the
pre-registered expectations are not revised.

| M0 base | M1 own history | M2 EWS | M3 feat. (sim) | M4 hybrid (sim) | M5 feat. (real) | M6 fragility |
|---|---|---|---|---|---|---|
| 0.500 | 0.667 | 0.515 | 0.547 | 0.564 | 0.683 | 0.672 |

These include the already-collapsed windows, which probably flatter the trend-based
methods; S1 will show how much. Seven test forecast files were then registered in
the ledger and committed before unsealing.

---

## 2026-09-22 — `real_v1` built by the data subagent; one amendment; window robustness

**Data (by the subagent; full record in `phase2/logs/data_prep.md`).**
- **Source:** Cliopatria at commit `ad28a69` (release `v0.2.0-duplicate`), zip sha256
  `d01ae3a2…`. 13,380 polity rows, 1,583 polities.
- **Windows:** 599 polities have eligible windows. Dev has 299 polities and 1,267
  windows (407 events: 219 area loss, 188 endings). Test has 300 polities and 300
  windows, one per polity.
- The fallback design was not needed.
- The name-leak check passed: all 1,583 names were searched across every open file,
  with no hits.
- The seal was called once, so the ledger has one `pool_built` event.
- I read the public log, and it contains no identities. I have not opened the sealed
  key, the truth or the private log.
- **The subagent's own transcript** is saved by Claude Code in this session's
  subagent directory. It contains identities, so I have not read it; it is there for
  Luca.

**Amendment (pre-registration, dated).** The subagent pointed out that the event
definition, applied literally, counts a polity that had *already* fallen below half
its record maximum inside the record as an "event" in the first horizon year. The
primary analysis is unchanged. I added a secondary analysis, S1, which excludes
windows whose last recorded value is below half the record's maximum. That is a
record-only rule. It was written before any forecast or result existed. From the open
records, 36 of 300 test windows and 105 of 1,267 dev windows qualify.

**Window robustness (simulation, development data; `inflection/notebooks/robustness_window.json`).**
With transitions spread over steps 100–210 instead of 100–150 (420 worlds, zero
failures):

| | onset MAE | mechanism MAE | whether AUC |
|---|---|---|---|
| base rate (window prior) | 28.9 | 26.8 | 0.50 |
| feature classifier | 30.2 | 29.9 | 0.68 |
| hybrid | 30.3 | 30.3 | 0.71 |

The flexible-model ceiling on pressure-driven worlds gives onset 30.8 vs 31.3, and
mechanism time 31.6 vs 27.8. **The timing conclusion holds, and is stronger:** with a
wider window, the modest onset gain seen in the narrow window disappears, and nothing
beats the prior. "Whether" also weakens (0.77 → about 0.70), because more worlds are far
from their change at the forecast point.

---

## 2026-09-22 — Phase 2 approved; pre-registration committed before any real data

Luca: "Go ahead with phase 2. You download. A script to anonymize data is fine. If
passing that task off to a subagent helps, you can do that too. Just make sure
everything you or any subagent does is logged for me to see later."

- **Dataset: Cliopatria** (Seshat), polity territory 3400 BCE–2024 CE, CC-BY 4.0.
  Before pre-registering I read only its repository README and licence, to learn the
  format.
- **Pre-registration:** `phase2/PREREGISTRATION.md`. It fixes the windows (100-year
  record, 50-year horizon), the collapse definition, the anonymisation, the
  dev/test split by polity, seven methods and five hypotheses with expected ranges.
- **An outcome leak caught during design, and fixed:** the test half uses one window
  per polity. Overlapping windows from one polity could be matched up, and a later
  window's existence reveals that the polity survived.
- `blind.seal_external_pool()` and `blind.split_seed()` were added, so a real-data
  test set goes through the same ledger. The seal refuses any metadata that would
  reveal outcomes.
- The `real_v1` seed was committed before download. The data work is delegated to a
  subagent, so identities stay hidden from me. Its public log goes to `phase2/logs/`.
  Its private log and the identity key stay sealed until scoring.
- **Two fixes from a dry run, before any real data existed.** I ran
  `phase2/run_real.py` on stand-in windows cut from simulated worlds:
  - M1 (own history) inherited the simulator's rule that a departure must hold for
    60 time units. The real horizon is 45 on that scale, so M1 could never fire.
    It now counts extrapolated paths that fall below half the record's maximum
    within the horizon: the pre-registered area-loss event itself, applied to the
    record's own extrapolation.
  - Dev cross-validation pooled predictions across folds, which gave even the
    constant base rate an AUC of 0.38. AUC is now averaged within folds.
- A Claude Code restart stopped the data subagent early, before it had written
  anything except a probe download. It was resumed from its saved transcript. The
  ledger shows no partial build.
- Also started: `scripts/robustness_window.py`, the Gate 4 robustness check. It
  widens the transition window from steps 100–150 to 100–210 and re-measures timing.
  This is development data only.

---

## 2026-09-21 — Going public: README, released test answers, verification

Luca asked for a public GitHub repository with a README, and for the spent test
answers to be published. He also asked that the README make my role plain, since
this is partly an experiment in how far an AI can direct research with minimal
supervision.

- `blind.release()` publishes a spent test set's seed and answers to
  `inflection/data/released/`, and records a `released` ledger event. It refuses a
  test set that is still sealed.
- `scripts/verify_blind_tests.py` checks, from repository files alone:
  - the seed against its salted hash;
  - the answers against their build hash;
  - every record file and every forecast file against its hash;
  - every forecast registration against the first unsealing;
  - the order of ledger events.

  With `--regenerate`, it also rebuilds a test set from its seed, at the recorded
  generator revision, in a temporary git worktree. The quick checks pass for both
  test sets.
  The full regeneration of `test_v2` also passes: the released seed, at generator
  `d473e56`, reproduces the sealed answers exactly.
- `README.md` describes the project, its results, who did what, the decisions I made
  unprompted, what I got wrong, and how to verify the blind tests.

---

## 2026-09-21 — Gate 4 analysis written; stopping for review

The plain-language Gate 4 analysis is a Claude Doc on claude.ai, "Forecasting
Inflection Points: Gate 4 Analysis". Its main conclusions:

- **Whether** is moderately forecastable (AUC ~0.78 on clean data), but the skill is
  fragility-recognition.
- **What** is somewhat forecastable on good data (0.47 against 0.17) and near
  chance on poor data.
- **When** is not forecastable beyond the transition window.
- **Classic EWS** are at chance.
- Every implication for cliodynamics is stated as a claim about methods and
  testing, not about real history.

My recommendation is Phase 2 (real data), which needs Luca's approval and his help
getting the datasets. The deep-learning classifier and an alternative simulator
design are offered as optional robustness checks.

---

## 2026-09-21 — `test_v2` results (second blind test)

Seed committed at `2df73e5`. Expectations written at `d473e56`. Pool built from
generator `d473e56` (clean tree): 420 worlds, none failed (`0ce6200`). 45 forecasts
(5 methods × 9 layers) registered and committed before unsealing (`ad03486`). Tables
are in `inflection/notebooks/gate3_tables_test_v2.md`, the figure in
`gate3_summary.png` (now for test_v2), and every number in
`gate3_scores_test_v2.json`.

| | clean | harsh | lead_30 |
|---|---|---|---|
| Whether AUC, hybrid | 0.78 [0.73, 0.83] | 0.65 [0.57, 0.73] | 0.77 [0.72, 0.82] |
| Whether AUC, feature clf. | 0.77 [0.72, 0.82] | 0.64 [0.57, 0.72] | 0.75 [0.70, 0.80] |
| Whether AUC, generic EWS | 0.51 | 0.54 | 0.56 |
| Onset MAE: base / feat. / hybrid | 18.2 / 17.1 / 17.0 | 18.2 / 18.2 / 18.1 | 18.2 / 17.4 / 17.3 |
| Type acc.: feat. / hybrid (chance 0.167) | 0.44 / 0.47 | 0.18 / 0.20 | 0.41 / 0.43 |

**Against the written expectations:**

1. **Shock fix works: confirmed.** Mean p for robust shocks is 0.77–0.78, equal
   to null (0.78). Fragile shocks get 0.92. By p alone, methods separate fragile
   from robust shocks at AUC 0.88–0.90. Whether-AUC is 0.77–0.78, inside the
   predicted 0.75–0.78.
2. **Hybrid best on type: confirmed,** but narrowly (0.47 vs 0.44, overlapping
   intervals). The feature classifier did better than predicted. Tied on whether.
3. **Timing gains small: confirmed.** About 1.1 steps on clean, with overlapping
   intervals. Under `harsh` it ties the base rate, where I predicted a small
   loss. The gain comes from the drift-visible types: transcritical 11.4 vs 14.8,
   Hopf 27.7 vs 32.9. Shock and mechanism change stay at the prior, as they must.
   Hopf timing error was 28, not the predicted 23–24.
4. **Slow decay with lead time: confirmed, and slower than predicted.** AUC drops
   0.01–0.03 from clean to `lead_30`, against a predicted 0.03–0.07.
5. **Generic EWS at chance: confirmed** on all 9 layers (AUC 0.49–0.56).

Mechanism change remains unrecognized (mech-vs-null AUC 0.45–0.47).

The two blind tests agree where they overlap: feature-classifier whether-AUC was
0.81 on `test_v1` and 0.77 on `test_v2`, a drop consistent with half the shocks now
being unforeseeable. Type accuracy was 0.39 and 0.44. Timing was base + 1 step both
times.

---

## 2026-09-21 — Gate 3 approved; decisions and the plan toward Gate 4

Luca approved continuing and left the Gate 3 decisions to me ("I defer to your
initiative"). A plain-language report for him is on claude.ai as a Claude Doc,
"Forecasting Inflection Points: Gate 3 Report". I took the three recommendations
made there:

1. **Make shocks fair.** In `test_v2`, half the shock worlds are *robust*: far from
   any threshold, like the null worlds at rest. The flag is drawn once per world,
   before the rejection loop, so selection cannot tilt the mix. After this,
   "whether" can only credit a shock where the world genuinely looks fragile.
2. **Build the hybrid next.** It targets "when", the sub-question nothing answers.
   The idea to test is that a system's recovery rate falls toward zero as it nears
   a threshold (critical slowing down), so a trend in that rate can be extrapolated
   to a crossing time. The deep-learning classifier is parked until after Gate 4.
3. **Lead time, done cheaply.** New generation isn't needed. Two extra layers,
   `lead_15` and `lead_30`, cut the last 15 or 30 steps off the clean record. That is
   the same as forecasting from further back, and all the worlds stay valid.

Next: simulator and layer changes → re-audit on three seeds → hybrid method → dev
evaluation with written expectations → `test_v2` (new seed) → score → Gate 4
write-up.

### Done since (commits `ba7736d`, `2df73e5`)

- **Robust shocks and lead layers in, and re-audited.** Scale-feature excess is
  +0.021, −0.011 and −0.047 on seeds 11–13. All nine layers pass. The closest is
  clean on seed 11: +0.041, p=0.03, significant but under the materiality line.
  That seed's fold worlds are the same draw as before and happen to have low noise
  targets. No design failed on any seed except a single shock on seed 13.
- **Where timing information lives (research pool, 450 pressure-driven worlds, seed
  202).** A flexible model on record summaries predicts the *visible onset* 15%
  better than the window prior (16.2 vs 19.0 steps). It predicts the *mechanism
  time* not at all (13.0 vs 12.6). The gain comes entirely from worlds whose
  forcing began inside the record (17.1 vs 20.9); where forcing starts after the
  record ends, there is none (13.5 vs 13.5). Extrapolating the recovery rate to
  zero was noise. **Conclusion: a record says how far a visible drift has gone, not
  when the threshold will be crossed.** Knowing the type perfectly would only cut
  timing error from 15.7 to 14.3, because shocks, mechanism changes and
  noise-induced escapes are timed by chance, by construction.
- **Hybrid method** (`methods/hybrid.py`) built on that finding.
- **Development pool enlarged** to 700 worlds (public seed 102, zero failures), so
  the learned methods have 350 training worlds per fold. Full nine-layer results
  are in `inflection/notebooks/dev_eval_s102_all_layers.txt`.
- `test_v2` seed committed at `2df73e5`.

### Expectations for `test_v2`, written before it is built

Development pool, two-fold CV:

| layer | method | Brier skill | AUC | onset MAE (base 16.6) | type acc. |
|---|---|---|---|---|---|
| clean | feature clf. | +0.09 | 0.76 | 15.9 | 0.42 |
| clean | hybrid | +0.11 | 0.77 | 15.8 | 0.49 |
| harsh | feature clf. | +0.02 | 0.63 | 17.3 | 0.22 |
| harsh | hybrid | +0.01 | 0.60 | 17.2 | 0.22 |
| lead_30 | feature clf. | +0.04 | 0.70 | 15.7 | 0.36 |
| lead_30 | hybrid | +0.06 | 0.73 | 15.7 | 0.44 |
| any | generic EWS | ≈0 | 0.50–0.58 | = base | ≈ chance |

Mean p(transition) on clean: null 0.78, mechanism change 0.77–0.79, **robust shock
0.80, fragile shock 0.93–0.94**, Hopf 0.94–0.95.

Predictions:

1. **The shock fix works.** Robust shocks get about the same p as null worlds;
   fragile shocks stay high. Overall whether-AUC is a little lower than on
   `test_v1` (0.81), around 0.75–0.78, because half the shocks are now
   unforeseeable.
2. **The hybrid is best on type** (about 0.45–0.50 against 0.40 for the feature
   classifier on clean) and roughly tied on whether.
3. **Timing gains are real but small.** Both learned methods beat the base rate by
   about 0.5–1 step on clean, with overlapping intervals, and lose to it under
   `harsh`. Hopf timing stays worst (about 23–24 steps).
4. **Skill decays with lead time, but slowly.** From clean to `lead_30`, AUC drops
   about 0.03–0.07. Most of what is known 30 steps out is fragility at rest, which
   doesn't depend on the final stretch of the record.
5. **Generic EWS stays at chance** on every layer, including the lead layers.

---

## 2026-09-21 (Gate 3, part 2) — First blind results; stopping for review

### What was run, in order (all in `inflection/data/ledger.jsonl` and git)

1. `test_v1` seed committed by salted hash at 07:12 UTC (`4222bbc`).
2. Expectations written in this log (`83fe02c`).
3. Test pool built at 08:10 UTC: 420 worlds, 60 per type, none failed, from generator
   revision `83fe02c` (clean tree). Open records for 7 layers; truth sealed with
   hash `da50025c…` (`eed8632`).
4. Four methods fitted on the development pool (public seed 101), one fit per
   layer. 28 forecast files registered by hash and committed *before* unsealing
   (`d130c0e`).
5. Unsealed and scored. Tables are in `inflection/notebooks/gate3_tables_test_v1.md`,
   the figure in `gate3_summary.png`, and every number in `gate3_scores_test_v1.json`.

`test_v1` is now spent. Any revised method needs `test_v2`.

### Headline results (95% bootstrap intervals, 420 worlds)

| | clean | harsh |
|---|---|---|
| **Whether — AUC** | | |
| feature classifier | 0.81 [0.77, 0.85] | 0.66 [0.59, 0.74] |
| own history | 0.73 [0.68, 0.78] | 0.56 [0.48, 0.64] |
| generic EWS | 0.47 [0.39, 0.56] | 0.50 [0.43, 0.58] |
| **When — onset MAE (steps)** | | |
| base rate | 18.0 [16.7, 19.3] | 18.0 |
| feature classifier | 17.0 [15.7, 18.3] | 18.0 [16.6, 19.5] |
| own history | 34.1 | 36.4 |
| **What — type accuracy, excl. mechanism change (chance 0.167)** | | |
| feature classifier | 0.39 [0.33, 0.44] | 0.18 [0.15, 0.22] |
| generic EWS | 0.14 | 0.08 |

### Against the expectations written beforehand

1. **Whether: mostly as expected, one miss.** Generic EWS is within noise of chance
   on every layer, as predicted. Own history is in the predicted range. The feature
   classifier *beat* the predicted range on clean (0.81 against 0.65–0.75). My
   prediction that everything collapses under `harsh` was wrong for it: it keeps
   AUC 0.66, with the interval clear of 0.5.
2. **When: as expected.** Nothing beats the base rate. The feature classifier's
   1-step edge is inside the intervals. Own history is roughly twice as bad, because
   straight-line extrapolation dates onsets poorly.
3. **What: as expected.** Only the feature classifier beats chance (0.39 on clean).
   It recognizes Hopf easily (recall 0.85, from the oscillatory autocorrelation
   signature) and the other types weakly (0.25–0.32 against 0.14). Under `harsh` it
   is at chance.
4. **Layers: half right.** Observation noise and irregular sampling do hurt most.
   `short` did *not* help own history: its ranking held (AUC 0.68), but its
   calibration broke (Brier skill −0.01).

### What the numbers mean, and don't

- **Mechanism change is not recognized, as designed.** The feature classifier's 0.38
  on that column is confusion with null. Within null plus mechanism-change worlds it
  separates the two at AUC 0.47. So the plan's "hardest case" is exactly as hard as
  intended: a change with no antecedents is not foreseen.
- **"Whether" skill is mostly fragility-at-rest, and part of that is the benchmark's
  own construction.** Mean p(transition) is 0.77 for null and 0.76 for mechanism
  change, against 0.80–0.95 for near-critical and oscillating worlds. That includes
  **exogenous shocks at 0.92**, which look foreseeable here only because the
  simulator places them in a near-critical state (to match `noise_induced` at
  rest). A real shock can hit a robust society. So this is the circularity risk in
  plan §8, made concrete. The whether-AUC is an upper bound that rests on the
  assumption that societies about to transition look fragile beforehand.
- **Generic EWS failing is a real result for this setting, not a bug.** Dev-pool
  diagnostics show the within-world slowing-down signal is there: before a fold,
  lag-1 AC rises from 0.39 to 0.72. But the Kendall-τ trend statistic on a
  90-point record is too noisy to carry it across worlds. The *level* of
  autocorrelation, which the feature classifier uses, carries more than its trend.
  This matches Jäger & Füllsack (2019) and O'Brien et al. (2023).
- **Timing is the unsolved sub-question.** No method dates the onset better than
  knowing the window it falls in. That is the natural target for the hybrid method.

### Open questions for Gate 3 review

1. Should shock worlds be decoupled from near-criticality in `test_v2` (e.g. half
   near-critical, half robust), so that "whether" stops rewarding a design choice?
2. For "when": the hybrid method in §4.3 is the planned answer. Is it worth building
   next, or should the deep-learning classifier come first?
3. The single forecast origin at 0.3 T fixes one lead time (median 34 steps). A
   lead-time sweep would need several fixed origins, each with its own blind test
   set.

---

## 2026-09-21 (Gate 3, part 1) — Onset check, four simulator defects, blinding, first methods

Gate 3 step 1 was meant to be a quick calibration of the onset detector. Doing it
carefully (looking at individual worlds, then re-auditing each fix across three
seeds) turned up four more defects in the simulator. All are fixed. The pattern
behind three of them is now familiar: **calibration undone by selection**.

### Step 1: the onset detector against an oracle

`scripts/oracle_onset.py`. The oracle is a two-sided Gaussian likelihood-ratio CUSUM
per world. It is told the world's pre-change behaviour (baseline window) and
post-change behaviour (last 40 observations). Its threshold is set per world against
AR(1) surrogates fitted to that world's baseline. Those surrogates re-estimate their
own baseline, which cut false alarms on null worlds from 60% to 3–15%.

- For the level-driven types, the fixed detector is **at or ahead of** the oracle.
  The gap (fixed − oracle) has a median of 0 for mechanism change and between −5 and
  −26 for the rest. A two-point likelihood ratio is not optimal for gradual drifts,
  so "ahead" there says the oracle is weak, not that the detector is clairvoyant.
  For abrupt changes the two agree to within a step.
- **Hopf onsets ran late.** In the worst tenth of worlds the detector was 45+ steps
  behind the oracle, with large cycles plainly visible in plots. The amplitude
  signal was the rolling median of |deviation|. On relaxation-type cycles with long
  flat troughs that median barely moves.
- **Fix:** the amplitude signal is now the rolling IQR (window 30, threshold 3×
  baseline) of the deviation from the local level, *as a fraction of that level*.
  - Using the IQR alone brought back the early-firing defect on steps. Level ×4 with
    multiplicative noise ×4 read as an amplitude change, up to 7 steps before
    `mechanism_change`.
  - Measuring the deviation relative to the level fixes that. A pure level change
    leaves relative spread unchanged, while a Hopf, whose mean doesn't move, shows
    its full amplitude growth.
  - Every non-Hopf onset in the Gate 2 pool is unchanged to the step. The Hopf p90 gap
    fell from +45 to +12, and to +24 on a fresh draw.
  - The remaining tail is mostly the oracle firing on small bumps. Its Gaussian
    surrogates lack heavy tails.
  - Also tried and rejected: other quantiles of |deviation|, rolling range/std/IQR of
    the raw series, IQR of first differences, and a level-attribution rule. Details
    are in this session's transcript, not repeated here.
- **Known limit:** spikes narrower than about 15% of the cycle still escape the IQR,
  which sees a quarter of its window. The models in use don't produce them, and a
  test records the boundary.

### Defect 1: `exogenous_shock` worlds that had already collapsed

Six of 40 shock worlds had escaped on their own, 6 to 57 steps *before* the shock,
because they sit in the same near-critical window as `noise_induced`. The label
dated the transition to the shock, so these were noise-induced escapes carrying the
wrong type and a time that was too late. The shock, which has a fixed target,
actually pushed the collapsed state *up*. Generation now rejects shock worlds that
are below the separatrix at the last observation before the shock
(`label.in_high_state_before`). Oracle alarms before the shock went from 10% to 0.

### Defect 2: accepted runs were quieter than their calibration

With the Gate 2 fixes in, three seeds all showed scale-feature excess of about +0.04
over chance (p ≈ 0.07–0.08 each): below the 0.05 materiality line, but consistent.
Pooling the three draws (829 worlds) located it. Target CVs were balanced across
types, but *delivered* CV was 0.81× target for shock, 0.86× for fold, 0.90× for
noise_induced and ~1.0 for the far-from-critical types. The pilot measures an
unconditioned path, but acceptance conditions the path (no visible departure before
the origin), which excludes exactly the big excursions that near-critical worlds
make. **Fix:** a second calibration pass on the accepted run. If delivered CV is more
than 10% off target, the same noise increments are re-run at the corrected scale,
and the rerun must pass acceptance again. Delivered/target is now 0.96–1.00 for every
type. `gate2_report.py` prints this table from now on.

### Defect 3: `noise_induced` designs failing at both ends of the CV range

Pinning the CV exposed an older problem. `noise_induced` failed 9–11 of 40 designs
per pool: low-CV designs never escaped, and high-CV designs escaped before the
window. Both types drew a/a_c from a fixed window (0.985–0.996) regardless of noise,
but escape is governed by the barrier *in units of the fluctuation size*. At CV
0.025, not one attempt in 120 escaped. The failures were selection on target CV by
the failure route, the same class as the Gate 2 `exogenous_shock` defect.
Widening the a/a_c window did not help; a sweep showed why. **Fix:** both near-
critical types now draw the barrier height (high state to separatrix, relative to
the level) as ρ × target CV, with ρ ~ U(1.5, 3.0) (`models._a_for_barrier`). Quiet
worlds sit nearer the fold, as a noise-driven escape requires. Even the best ρ lands
only 5–15% of escapes in the 50-step window, because escape times are roughly
exponential, so the attempt cap went from 60 to 250. In spot checks, `noise_induced`
failed 0 of 40 designs across CV 0.022–0.145. Shock failed 1 of 40, at CV 0.145 and
a late t*: there a collapse is often too small to clear 6 MADs.

A consequence to keep in view: in `noise_induced` worlds, CV and closeness to the fold
are now linked (quiet worlds show stronger slowing down). That is physics, and it is
what the audit's physical tier is for, but a classifier could learn the joint pattern.

### Defect 4 (averted): changing the drift window to help EWS

Generic EWS came out near chance in development (below), and the drift start is
often after the origin. So I considered moving the drift window earlier. I checked
first: EWS AUC is 0.59–0.64 whether the forcing ran 30–60 steps before the origin or
starts after it. The weakness is the Kendall-τ statistic on 90-point records (null
worlds give τ = ±0.5 by chance, as in Jäger & Füllsack 2019), not missing forcing.
The simulator was left alone. Changing it would have been a researcher degree of
freedom with no justification.

### Step 2: blinding infrastructure — `inflection/eval/blind.py`

An append-only ledger (`inflection/data/ledger.jsonl`, tracked in git) with
salted-hash seed commitment, pool build (with the generator's git revision), forecast
registration, unseal-before-read, and a check that refuses any forecast file not
registered, byte for byte, before the first unseal. Test manifests are stripped of
the seed and per-type failure counts; the generic manifest would have published both.
Test world ids are renumbered, since generator ids hash a string that includes the
type. `.gitignore` now excludes every `sealed/` directory. There are 8 tests.

### Steps 3–5: interface, first methods, scoring

- `methods/base.py`: `Record` → `Forecast`, with p(transition), 19 onset quantiles
  and 7 type probabilities.
- `methods/baselines.py`: `BaseRate`; `OwnHistory`, which extrapolates trend plus
  AR(1) noise and applies the level-departure rule, with its probability calibrated
  by logistic regression on the development pool.
- `methods/ews.py`: the standard recipe (Gaussian detrending, rolling-window lag-1
  AC and variance, Kendall τ), mapped to probabilities by logistic regression.
- `eval/score.py`:
  - **Whether:** Brier, Brier skill, AUC and ECE.
  - **Null false-positive rate:** read off the ROC at 80% sensitivity. A p>0.5 cut
    is 1.0 for every calibrated method, since 6 of 7 worlds transition.
  - **When:** CRPS from quantiles, MAE of the median against the onset and the
    mechanism time, and 90% coverage.
  - **What:** accuracy excluding mechanism change, with mechanism change separate;
    recall by type; log loss.
  - Bootstrap CIs for all of the above.
- `scripts/dev_eval.py`: two-fold CV on a development pool.
- `scripts/gate3_run.py`: seed → build → forecast → score.

**Development results (old Gate 2 pool, clean layer, 2-fold CV):**

| method | Brier skill | AUC | null FPR@80% | onset MAE | type acc. |
|---|---|---|---|---|---|
| base rate | 0.00 | 0.50 | 0.80 | 17.7 | 0.17 |
| own history | +0.13 | 0.77 | 0.58 | 36.8 | 0.17 |
| generic EWS | −0.00 | 0.55 | 0.78 | 17.7 | 0.21 |

Under `harsh`, everything is at chance. The base rate's "when" is good by design,
because onsets cluster in the shared window, so any method's "when" has to beat about
17 steps to count.

### Confirmation across seeds, after all four fixes

| seed | scale-feature excess before fixes | after | p after | failed designs after |
|---|---|---|---|---|
| 11 | +0.043 | +0.025 | 0.18 | shock 1 |
| 12 | +0.036 | −0.022 | 0.80 | shock 1 |
| 13 | +0.040 | −0.021 | 0.85 | none |

All seven realism layers pass on seed 11 (every p ≥ 0.13). The Hopf onset gap
against the oracle is now +8 at p90. Generating a pool takes about 15 minutes,
because `noise_induced` needs ~20 attempts per world.

### A fourth method, and the committed test seed

`methods/features.py`: gradient boosting on the nine *physical* features the audit
measures, excluding the scale features by design. It covers all three questions:
quantile regression for "when", and sigmoid calibration for "whether" and "what",
because uncalibrated it had AUC 0.76 but Brier skill −0.15.

The `test_v1` seed was committed by salted hash at 07:12 UTC (commit `4222bbc`),
before any test forecast existed and before the method set was final. I have not
opened the sealed seed file.

### Expectations for the blind test, written before it is built

Development pool: public seed 101, 280 worlds, zero failed designs. Two-fold CV per
layer (`inflection/notebooks/dev_eval.json`).

| layer | method | Brier skill | AUC | null FPR | onset MAE | type acc. | mech. |
|---|---|---|---|---|---|---|---|
| clean | base rate | 0.00 | 0.50 | 0.80 | 15.7 | 0.17 | 0.00 |
| clean | own history | +0.06 | 0.68 | 0.68 | 32.5 | 0.17 | 0.00 |
| clean | generic EWS | +0.00 | 0.55 | 0.70 | 15.7 | 0.15 | 0.15 |
| clean | feature clf. | +0.06 | 0.73 | 0.53 | 16.8 | 0.35 | 0.42 |
| harsh | own history | +0.00 | 0.60 | 0.73 | 32.3 | 0.17 | 0.00 |
| harsh | generic EWS | −0.02 | 0.50 | 0.85 | 15.7 | 0.13 | 0.10 |
| harsh | feature clf. | −0.00 | 0.57 | 0.75 | 15.8 | 0.23 | 0.07 |

What I expect the test set to show, and would be surprised by otherwise:

1. **Whether:** the feature classifier and own history carry real but modest signal
   on clean records (AUC ~0.65–0.75). Generic EWS is within noise of chance on every
   layer. Everything collapses toward chance under `harsh`.
2. **When:** no method beats the base rate by a meaningful margin. The shared
   transition window is most of the available timing information.
3. **What:** only the feature classifier beats chance, at about 0.3–0.4 on clean.
   Its **mechanism-change "accuracy" is not recognition.** Before the change, those
   worlds are identical to null worlds by construction, so the classifier is
   splitting its guesses between the two. The Gate 3 write-up reads that column
   against null recall.
4. **Realism layers:** observation noise and irregular sampling hurt most. `short`
   hurts least, and helps own history, whose extrapolation is less anchored to the
   distant past.

---

## 2026-09-21 — Gate 2 closed; plan for Gate 3

Luca delegated the three Gate 2 decisions ("Do what you think is best"). Decided:

1. **"When" target:** `observable_onset` is primary and mechanism-time error is
   reported alongside it. RESEARCH_PLAN §4.4 is amended. Condition: calibrate the onset
   detector against an oracle before scoring anything.
2. **§4.1:** the `noise_induced` expectation is amended to "elevated but trendless".
3. **Proceed to Gate 3.**

### Gate 3 work plan, in order

1. **Oracle calibration of `observable_onset`.** Build a likelihood-ratio (CUSUM-style)
   detector that knows each world's true pre- and post-change behaviour, and measure
   how far behind it the fixed detector runs, by type. If the gap is large for Hopf,
   make the amplitude signal more sensitive (e.g. use the rolling IQR of the local
   deviation instead of its median), re-audit, and log the change.
2. **Blinding infrastructure, per §4.2.** Commit the test seed by hash before any
   method exists. Keep the development pool and the sealed test pool apart
   (`save_pool(seal=True)` already writes truth to a git-ignored `sealed/` directory).
   Hash forecasts before unsealing. Add a scorer that refuses to run if the forecast
   hash was committed after the truth file was opened.
3. **Common method interface** in `methods/`: take a record `(t, y)` and return
   `P(transition within H)`, a distribution over onset time, and a distribution over
   type.
4. **First methods:** base-rate and own-history baselines, and generic EWS (detrended
   lag-1 AC and variance with a Kendall-tau trend test). Then, if they are cheap, one
   changepoint method and the PITF-style hazard model.
5. **Scoring:** Brier, AUC and calibration for whether (with the null false-positive
   rate); onset error and CRPS for when; accuracy by type for what, with mechanism
   change reported separately. Every score broken down by realism layer.
6. **Stop at Gate 3** with the first blind results.

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
