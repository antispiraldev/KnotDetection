# Phase 2 pre-registration: real test `real_v1` (Cliopatria territory)

Written and committed **before any real data was downloaded or examined**. Only the
dataset's repository README and licence were read beforehand, to learn the file
format. Luca approved Phase 2 on 2026-09-21: "Go ahead with phase 2. You download. A
script to anonymize data is fine."

## Question

Does the main simulation finding carry over to real history? In simulation,
"whether" skill came from recognising societies that already looked **fragile at
rest**, not from detecting an approaching tipping point. The real-data counterpart:

> Do polities that are about to suffer a territorial collapse or to end look
> different, in their recent territorial record, from polities that are not? Can
> methods built and trained on simulated societies see that difference?

## Data

**Cliopatria** (Seshat Global History Databank), the latest release on GitHub,
`Seshat-Global-History-Databank/cliopatria`, licensed CC-BY 4.0. Each row gives a
polity **Name**, **FromYear**–**ToYear**, **Area** (km², equal-area projection) and
**Type**. Only `Type == POLITY` rows are used. Geometry, Wikipedia, Wikidata and
Seshat ids are discarded, apart from the sealed key.

**Known limits, stated in advance.** Territory is recorded as snapshots, constant
between recorded border changes, so it is not a dense noisy series like the
simulator's. Row boundaries partly reflect historians' and mapmakers' choices. A
polity "ending" in the data can be conquest, collapse, merger or renaming. None of
this can be fixed here. It is why the simulation-trained methods are expected to
transfer poorly (H1).

## Series, windows and outcomes

- **Series per polity:** the yearly step function of Area, which on each year takes
  the value of the row covering that year.
- **Forecast origins t0:** every multiple of 50 years (…, −100, −50, 0, 50, …). A
  window is kept if the polity has rows covering the whole record window
  [t0 − W, t0) and its outcome in (t0, t0 + H] is observable.
- **W = 100 years of record, H = 50 years of horizon.** The record is sampled every
  5 years, giving **20 observations**, all in the window.
- **Event (collapse) in (t0, t0 + H]:** either
  1. Area falls below **50%** of its maximum over [t0 − W, t0) at some year in the
     horizon; or
  2. the polity's last row ends in the horizon, and that year is before 2000 (so a
     dataset end is not counted as an ending).
- **Control:** no event in (t0, t0 + H], and the polity still has rows at t0 + H.
- Windows where Area ≤ 0 anywhere in the record are dropped.
- **Fallback, fixed in advance:** if the test half has fewer than 60 windows, use
  W = 150, H = 75, with 30 observations every 5 years.

## Anonymisation and blinding

- A subagent downloads the data, builds the windows and anonymises them, so the
  analyst (me) never sees identities.
- Each window becomes an id `real_v1-NNNN` in shuffled order. Its times are mapped
  to the simulator's scale, t = (year − (t0 − W)) × 90 / W, so every record spans
  [0, 90) with the forecast origin at 90. Its values are divided by the record's
  median. No names, no years.
- **Split:** polities, not windows, are assigned at random to dev (50%) and test
  (50%), using the seed committed for `real_v1` in the ledger, before download.
- **Test uses one window per polity**, chosen at random (seeded) from its eligible
  origins. Dev keeps every window. Several windows per polity would leak outcomes:
  windows 50 years apart overlap by half their length and could be matched up, and
  the mere existence of a later window proves the polity survived the earlier one's
  horizon.
- **Dev** windows carry labels, for fitting and calibration. **Test** labels are
  sealed with the existing ledger (`inflection/eval/blind.py`). Test forecasts are
  registered and committed before unsealing, exactly as for `test_v1` and `test_v2`.
- The key (window → polity name, t0, event year, event kind) is sealed. It is
  released after scoring, like the simulated test answers.
- The subagent writes a public log of every step, without identities, to
  `phase2/logs/`, and a private log with full detail beside the sealed key.

## Methods (all see only the anonymised record)

| id | Method | Trained on |
|---|---|---|
| M0 | Base rate | real dev |
| M1 | Own history (trend + noise extrapolation), calibrated | real dev (calibration only) |
| M2 | Generic early-warning signals (Kendall tau of AC and variance) → logistic | real dev |
| M3 | Feature classifier, **trained on simulation**, no real data | sim dev pool (seed 102), records resampled to 20 regular points |
| M4 | Hybrid, **trained on simulation** | same as M3 |
| M5 | Feature classifier trained on real dev | real dev |
| M6 | "Fragility at rest": logistic on the record's lag-1 autocorrelation and coefficient of variation | real dev |

M3 and M4 are pure transfer: for them, AUC is the measure (calibration to real base
rates is not expected).

## Scoring

- **Primary:** "whether" AUC on test windows, with 95% bootstrap intervals. Test
  windows are one per polity, so they are independent units.
- **Secondary:** Brier skill for the methods fitted on real dev, and AUC separately
  for the two event kinds (area loss vs ending).
- "When" and "what" are not scored. There are no mechanism labels in real data, and
  timing at 50-year resolution is too coarse.

## Hypotheses and expectations

- **H1, transfer.** Simulation-trained methods (M3, M4) rank test windows above
  chance. **Expectation: little or none, AUC 0.50–0.60.** The simulator's fragility
  signature (slow recovery in dense noisy series) has no counterpart in 5-year step
  data.
- **H2, fragility at rest.** M6 (autocorrelation and variability of the recent
  record) is above chance. **Expectation: modest, AUC 0.55–0.65, driven by
  variability**: polities whose borders were recently volatile are more likely to
  collapse.
- **H3, classic warning signs.** M2 is at chance. **Expectation: AUC ≈ 0.50**, as in
  simulation.
- **H4, momentum.** M1, which extrapolates the recent trend, is above chance.
  **Expectation: AUC ≈ 0.55–0.65.**
- **H5, best achievable here.** M5 is the strongest. **Expectation: AUC ≈ 0.60–0.68.**

**What would count against the fragility account:** M6's interval including 0.5,
*and* M5 no better than M1. That would mean recent trend, not fragility, is all the
record carries.

## Out of scope

Claims about why particular polities fell. Forecasts of present-day states. Any use
of the identity key before scoring.
