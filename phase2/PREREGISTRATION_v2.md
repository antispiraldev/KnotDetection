# Phase 2 pre-registration: real test `real_v2` (Maddison GDP per capita)

Written and committed **before any of this dataset was downloaded or examined**. Only
the file's HTTP headers were checked, to confirm it is reachable. Luca approved a
second real test on an annual dataset on 2026-09-22 ("Yes run the extra test and then
do the writeup").

## Why a second real test

`real_v1` (Cliopatria territory) found no forecastable signal once already-collapsing
polities were excluded, and no transfer from the simulator. Two explanations are
confounded there: history may carry no warning, or territorial snapshots at 5-year
sampling may be too thin a measure. This test uses the densest long-run economic
series available, one value per country per year, which is far closer to what the
simulator produces.

## Question

Do countries about to suffer a large fall in income look different beforehand, in the
recent record of that income? Do methods built and trained on simulated societies see
it?

## Data

**Maddison Project Database 2020** (Groningen Growth and Development Centre),
`mpd2020.xlsx`, licensed CC-BY 4.0. Columns expected: `countrycode`, `country`,
`year`, `gdppc`, `pop`. Only `gdppc` is used, by country and year. If a column is
named differently, the closest equivalent is used and the choice logged.

**Known limits, stated in advance.** Pre-1950 coverage is thin and uneven, and early
figures are reconstructions with wide uncertainty. Country borders change while a
`countrycode` stays fixed. A fall in GDP per capita is an economic contraction, which
is one kind of inflection point and not the same as a regime change.

## Series, windows and outcomes

- **Series per country:** the annual `gdppc` series, in its own units.
- **W = 30 years of record, H = 15 years of horizon**, both annual, so a record is 30
  observations.
- **Origins t0:** every 5 years (multiples of 5). A window is eligible when:
  1. every year of [t0 − W, t0) has a value, and all values are > 0;
  2. **the record is not already in collapse:** the value at the last recorded year is
     at least 0.75 × the record's maximum. This is the `real_v1` artifact, excluded by
     construction this time. It uses only the record, never the outcome;
  3. the outcome in (t0, t0 + H] is observable, meaning either an event occurs in a
     recorded year, or every year of the horizon is recorded.
- **Event:** `gdppc` in some year of (t0, t0 + H] falls below **0.75 × the record's
  maximum over [t0 − W, t0)**: a fall of at least a quarter from the recent peak.
- **Control:** no such year, with the horizon fully recorded.
- **Fallback, fixed in advance:** if the test half has fewer than 150 windows, use
  W = 20, H = 10, origins every 5 years.

## Blinding

As for `real_v1`, and for the same reasons. A subagent downloads, builds and
anonymises; I never see country identities. Windows become `real_v2-NNNN` in shuffled
order, times mapped to t = (year − (t0 − W)) × 90 / W so records span [0, 90) with the
origin at 90, values divided by the record's median. Countries, not windows, are split
50/50 into dev and test with the seed committed for `real_v2` before download. Test
labels are sealed in the ledger; forecasts are registered and pushed before unsealing;
the identity key is released after scoring.

**Unlike `real_v1`, the test half keeps every eligible window of its countries.** There
the event was partly "the polity ends", so a later window's existence revealed the
earlier outcome. Here the event is a fall in GDP, which later data does not reveal,
and each forecast still sees only its own record. Confidence intervals are therefore
**bootstrapped over countries**, not windows.

## Methods

The same seven as `real_v1`, unchanged: M0 base rate, M1 own history (trend
extrapolation, with the event rule above), M2 generic early-warning signals, M3
feature classifier trained on simulation, M4 hybrid trained on simulation, M5 feature
classifier trained on real dev, M6 fragility at rest (lag-1 autocorrelation and
coefficient of variation). Simulation-trained methods see simulated records resampled
to 30 regular points, and no real data.

## Scoring

- **Primary:** "whether" AUC on test windows, 95% intervals bootstrapped by country.
- **Secondary:** Brier skill for the methods fitted on real dev; AUC restricted to
  windows whose event is a fall of at least 40% (a severe collapse); AUC on the
  pre-1950 and post-1950 halves separately.

## Hypotheses and expectations

- **H1, transfer.** M3 and M4 beat chance here, where they did not on territory.
  **Expectation: AUC 0.55–0.65.** This is the cleanest test of transfer in the
  project: dense annual series are what the simulator produces.
- **H2, fragility at rest.** M6 beats chance. **Expectation: 0.58–0.68**, higher than
  `real_v1`'s 0.56 because volatility is measured over 30 annual values rather than
  20 five-yearly ones.
- **H3, classic warning signs.** M2 at chance. **Expectation: 0.50–0.57.** These
  records are still short for a trend test.
- **H4, momentum.** M1 beats chance. **Expectation: 0.55–0.65.**
- **H5, best achievable.** M5 is strongest. **Expectation: 0.62–0.72.**

**What would count against the fragility account:** M6's interval including 0.5. That
would say that, even with dense annual income data and already-collapsing cases
removed, how a country's income fluctuates says nothing about whether a contraction
is coming.

**What would count against the transfer pessimism of `real_v1`:** M3 or M4 clearly
above chance here would show that the earlier failure was the thinness of territorial
data, not a general failure of simulation-trained methods.

## Amendment, 2026-09-22 (after the data were built, before any forecasting or scoring)

The public preparation log reports that record lengths vary a great deal: in the dev
half the median country contributes 5 windows and the largest contributes 138. Test
intervals already cluster by country, but a headline AUC computed over all windows is
still dominated by a few long-record countries.

The primary analysis is unchanged. **Added secondary analysis S2:** the same AUCs on
one window per country, drawn uniformly at random with a fixed seed (`numpy`
default_rng(0), countries in sorted group order). It uses only the group ids in the
open manifest, never the outcome, and gives 74 independent test windows. Written
before any forecast or score existed for this test set.

## Out of scope

Explanations of particular countries' contractions. Forecasts of current economies.
Any use of the identity key before scoring.
