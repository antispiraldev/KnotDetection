# Forecasting Inflection Points: Research Plan

*Gate 1 draft, 2026-09-19. Gate 1 approved 2026-09-21. Gate 2 approved 2026-09-21, with the amendments marked **[Amended 2026-09-21]** below (see LOG.md). Gate 3 results (blind test set `test_v1`) ready for review 2026-09-21; awaiting approval.*

## 1. Question

How well can we detect and characterize an upcoming inflection point (a regime change in a social system) using only data from before it happens?

This breaks into three sub-questions, roughly in order of difficulty:

1. **Whether.** Will a transition occur within horizon *H*?
2. **When.** Where does the transition fall inside that window?
3. **What.** What kind of regime comes afterward (collapse, oscillation, new equilibrium, mechanism change)?

The goal is **not** to build a model of history. It is to find out which methods work, how well, and under what conditions, using honest, blinded evaluation.

## 2. Scope rules

**In scope**
- Synthetic societies with known, hidden regime changes
- Forecasting methods: statistical, dynamical-systems, and machine learning
- Evaluation protocol and scoring
- Later, with Luca's go-ahead: real historical and conflict datasets

**Out of scope unless Luca signs off**
- Forecasting specific current political events
- Building new historical datasets by hand
- Claims about real societies drawn from synthetic results alone
- Any expansion beyond the three sub-questions above

**Working rule:** if a promising direction falls outside scope, log it under "Parked ideas" instead of pursuing it.

## 3. What's already known (short review)

- **Early-warning signals work sometimes.** Rising autocorrelation and variance, known as critical slowing down, precede some tipping points (Scheffer et al. 2009). Detrending matters a lot. Some system classes produce warning signals without any transition, and many transitions give no warning (Jäger & Füllsack 2019). A 2023 study found limited applicability to real lake data (O'Brien et al. 2023).
- **There's retrodictive evidence in human societies.** 7 of 9 European Neolithic regional population series showed rising autocorrelation and variance before collapse (Downey et al. 2016). This is retrodiction on reconstructed data, not true forecasting.
- **Machine learning can say something about the "what."** A deep-learning classifier trained on generic bifurcation dynamics produced earlier warnings with fewer false positives, and could predict the *type* of transition, e.g. fold vs. Hopf vs. transcritical (Bury et al. 2021). This is the closest existing work to sub-question 3.
- **Simple hazard models predict "whether" out of sample.** The PITF model flagged 18 of 21 instability onsets from 1995–2004 in its top risk quintile, using data from two years earlier. The dominant predictor was regime type, not demography or economics (Goldstone et al. 2010).
- **Conflict forecasting competitions show how hard the problem is.** In the ViEWS competitions, models beat no-change baselines, but escalation and onset stayed hard. Models relying only on conflict history were often competitive (Vesco et al. 2022; Hegre et al. 2022).
- **Cliodynamics hasn't been tested blind.** Structural-demographic theory has been fitted to history but never evaluated with blind, pre-registered protocols. Seshat began using LLMs for data coding in 2025; LLMs haven't been used for modeling or forecasting there.

**Gap this project targets:** no one has run a blind benchmark comparing methods on all three sub-questions for social-dynamics models, including transitions that change the mechanism itself.

## 4. Phase 1: Synthetic benchmark (fully autonomous)

### 4.1 Simulator

A generator of synthetic "societies," built on a structural-demographic core: population, elite numbers, state fiscal health, and a political-stress index. Each run is randomly assigned one of these transition types:

| Type | Mechanism | Expected warning signal |
|---|---|---|
| Fold (collapse) | Slow parameter drift pushes the system past a threshold | Yes |
| Hopf (cycle onset) | A stable equilibrium turns into secular cycles | Yes |
| Transcritical | Stability passes from one equilibrium to another | Yes |
| Noise-induced | Fluctuations carry a near-critical system out of a shallow basin | Elevated but trendless **[Amended 2026-09-21]** |
| Exogenous shock | Outside forcing, e.g. a climate or pandemic analog | None |
| **Mechanism change** | The equations themselves change, e.g. a technology shock raises carrying capacity | Unknown; this is the interesting case |
| Null | No transition | Should stay quiet |

**Realism layers**, each switchable so their effects can be measured separately:
- observation noise
- sparse or irregular sampling that mimics historical records
- proxy variables instead of true states
- short series lengths

### 4.2 Blinding protocol

This is designed to keep my own knowledge from leaking into the results.

1. Test worlds are generated from seeds that are committed by hash and not inspected until the evaluation step.
2. Methods are developed only on a separate training/validation pool.
3. Test series are truncated at forecast origins before any transition.
4. Forecasts are written to file and hashed **before** the true outcomes are revealed.
5. Methods can't be tuned after the test set is unsealed. A fresh test set is required for any revision.

### 4.3 Methods to compare

- **Baselines:** base rate, and a model that uses only the series' own history
- **Generic early-warning signals:** lag-1 autocorrelation and variance with a significance test, after detrending
- **Changepoint and regime models:** Bayesian online changepoint detection, Markov-switching models
- **Structural hazard model:** transition probability as a function of stress indicators, PITF-style
- **Deep-learning classifier:** in the style of Bury et al., predicting both the transition and its type
- **Hybrid (the new contribution to test):** combine structural stress, which answers "whether," with slowing-down indicators, which answer "when," and a bifurcation-type classifier, which answers "what"

### 4.4 Scoring

- **Whether:** Brier score, AUC, and calibration, plus the false-positive rate on null runs
- **When:** error in predicted transition time, and CRPS on the predicted time distribution
  - **[Amended 2026-09-21]** The primary target is `observable_onset`, the first sustained
    departure of the series, defined the same way for every type. Error against the
    mechanism-change time is reported alongside it. The two differ by type and in both
    directions: transcritical is visible before its bifurcation, while Hopf becomes
    visible long after. Before any method is scored, the onset detector is calibrated
    against an oracle likelihood-ratio detector and the gap between them is reported.
- **What:** accuracy by transition type, reported separately for mechanism-change runs
- Every result is broken down by realism layer, so the question "how much noise or sparsity kills each method?" gets a direct answer

## 5. Phase 2: Real data (needs Luca)

Candidate datasets, which Luca would download or attach:
- Seshat / Cliopatria
- CrisisDB, if released
- Turchin's US instability series (1780–2010)
- Polity / PITF instability onsets
- UCDP conflict data

**Protocol:** pseudo-prospective truncation. To reduce my hindsight bias, series are **anonymized** before I see them: dates, names, and places are stripped and the series rescaled. This test is only partly blind, since I might still recognize famous series. That limitation will be reported openly.

## 6. Phase 3: True prospective test (needs time)

Register forecasts for current series, such as conflict or instability indicators, with hashes and dates. Score them when outcomes arrive. This is the only fully clean test, and it takes months to years.

## 7. Check-in gates

Work stops at each gate until Luca approves.

1. **This plan.** Scope, methods, protocol.
2. **Simulator design.** Equations, transition types, a few example trajectories plotted.
3. **First blind results.** Baselines plus two or three methods on the test set.
4. **Analysis write-up.** What works, what doesn't, and what that implies for cliodynamics.

Between gates, `LOG.md` is updated with what was tried, what was dropped, open questions, and parked ideas.

## 8. Likely failure modes

- **The simulator is too easy.** Results then won't transfer to real data. Mitigation: the realism layers, and reporting results under the harshest settings.
- **Circularity.** Methods may succeed because they share assumptions with the simulator. Mitigation: include transition types the methods weren't designed around, especially mechanism change.
- **Negative results.** Methods may fail on sub-question 3. That's a legitimate finding, and would be reported as such.

## 9. Setup (Claude Code)

```
inflection/
  RESEARCH_PLAN.md   LOG.md
  sim/        # generator, transition types, realism layers
  methods/    # one module per method, common interface
  eval/       # blinding, scoring, reports
  data/       # sealed test sets (hashed), real data later
  notebooks/  # figures for gate reviews
```

**Stack:** Python, numpy/scipy, statsmodels, `ruptures`, a Bayesian online changepoint implementation, and PyTorch for the classifier. Fixed seeds throughout, and git commits at every gate.

## 10. Decisions for Luca

1. Approve scope rules as written?
2. Run Phase 1 in Claude Code on your machine, or here?
3. Time budget before Gate 2: a single session, or a few days of scheduled runs?

## References

- Scheffer et al. 2009, *Nature* 461:53. Early-warning signals for critical transitions.
- Jäger & Füllsack 2019, *PLOS ONE*. Systematically false positives in early warning signal analysis.
- O'Brien et al. 2023, *Nat. Commun.* 14:7942. EWS have limited applicability to empirical lake data.
- Downey, Haas & Shennan 2016, *PNAS* 113:9751. European Neolithic societies showed EWS of population collapse.
- Bury et al. 2021, *PNAS* 118:e2106140118. Deep learning for early warning signals of tipping points.
- Goldstone et al. 2010, *AJPS* 54:190. A global model for forecasting political instability.
- Vesco et al. 2022; Hegre et al. 2022, *International Interactions* 48(4). ViEWS prediction competition.
- Turchin, "Seshat and AI," Cliodynamica, Nov 2025.
