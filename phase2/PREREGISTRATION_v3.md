# Phase 2 pre-registration: real test `real_v3` (does slow recovery show up in calm economies?)

Written and committed **before any of this dataset was downloaded or examined**, and
before computing anything about this hypothesis beyond the development-half figure that
produced it. Luca asked for it after reading the `real_v2` correction: "pre-register
that calm-quartile hypothesis as real_v3".

## Where the hypothesis came from, and why it needs a fresh test

`real_v2` (Maddison GDP per capita) found that methods trained on the simulator score
**below** chance on real income data, because the simulator's central warning sign —
rising autocorrelation, the signature of critical slowing down — carries the opposite
sign there. In real income data a smooth record means a steady grower that rarely
contracts, and what marks a coming contraction is raw year-to-year volatility.

While explaining that, I split the development half by volatility and found:

| volatility quartile (dev) | windows | share that contracted | AUC of lag-1 autocorrelation within the band |
|---|---|---|---|
| calmest | 258 | 0.05 | **0.874** |
| second | 257 | 0.10 | 0.420 |
| third | 257 | 0.24 | 0.486 |
| jumpiest | 258 | 0.34 | 0.412 |

So in the calmest quarter of records, and only there, sluggish recovery does go with a
coming contraction — which is what the simulator predicts. It rests on **12 events in
258 windows**, it was found after unsealing, and it was not pre-registered. It is a
hypothesis, not a result, and the development half cannot confirm it. Neither can the
`real_v2` test half, which is spent.

## Hypothesis

> **H1.** Among records in the calmest quartile of year-to-year volatility, higher
> lag-1 autocorrelation predicts a coming contraction: AUC > 0.5, with a 95%
> country-clustered interval that excludes 0.5.

Mechanism, if it holds: critical slowing down is real but readable only where the noise
is small enough not to drown it. Where the series is noisy, volatility dominates and
the autocorrelation signal is lost or reversed.

## Data

**World Bank, World Development Indicators**, series `NY.GDP.PCAP.KD` (GDP per capita,
constant US$), annual, 1960–2024, all economies, fetched from the public API
(`api.worldbank.org`), no key required. Aggregates (regions, income groups) are
excluded using the API's own country list; only entities with a region are kept.

**Overlap, stated in advance.** Maddison 2020 covers many of the same country-years up
to 2018, so this is a **partial replication**, not an independent sample: some of the
same historical episodes will appear. It is a different source, vintage and definition
(market GDP in constant US$ against historical reconstructions in 2011 PPP$), it adds
economies Maddison omits, and its horizons run to 2024, beyond Maddison's end. A fully
independent test would need outcomes that have not happened yet, which is Phase 3.

**Era limit.** These data begin in 1960, so `real_v3` tests the hypothesis in the modern
era only. If the development-half signal came mainly from earlier centuries, a null
result here is ambiguous rather than a refutation. I do not know which era those 12
events came from; establishing it would require the released identity key, which I am
not opening for this purpose.

## Windows and outcomes (unchanged from `real_v2` except where noted)

- **W = 30 years of record, H = 15 years of horizon**, annual, so 30 observations.
- **Origins every 3 years** rather than 5 (the shorter dataset needs the extra windows;
  overlapping windows within a country are handled by clustering, as before).
- **Eligible** when: every record year is present and positive; the last record value is
  at least 0.75 × the record maximum (not already in collapse); and the outcome is
  observable (an event occurs in a recorded horizon year, or the whole horizon is
  recorded).
- **Event:** some horizon year below 0.75 × the record maximum.
- Countries split 50/50 into dev and test by the seed committed for `real_v3` before the
  download; both halves keep all their windows; test intervals bootstrap over countries.
- Anonymised by a subagent exactly as before; identities sealed and released after
  scoring.

## Analysis, fixed in advance

- **Volatility** of a record = standard deviation of its year-to-year log changes.
  **Calm quartile** = the lowest quartile of that quantity *among the test windows*,
  computed from the records alone, with no reference to outcomes.
- **Autocorrelation** = `lag1_ac` as the project already computes it
  (`inflection.eval.leakage.features`), on the same records.
- **Primary:** AUC of `lag1_ac` within the calm quartile, with a 95% bootstrap interval
  clustered by country.
- **Secondary:** the same AUC in each of the other three quartiles; a logistic model with
  volatility, autocorrelation and their interaction, reporting the interaction
  coefficient and its interval; and the AUC of volatility over all test windows, which
  should reproduce `real_v2`'s positive result.
- **Power rule, fixed now:** if the calm quartile holds fewer than 15 events, the test is
  reported as underpowered, and H1 is recorded as neither supported nor refuted.

## Expectations

- **H1: AUC 0.55–0.75.** Lower than the development half's 0.874, which rests on 12
  events and will regress. My honest expectation is that something survives but is much
  weaker; I would not be surprised by a null.
- **Other quartiles: 0.40–0.55**, as in development.
- **Interaction:** negative (autocorrelation matters less, or turns around, as volatility
  rises), with an interval that may well include zero at this sample size.
- **Volatility overall: AUC 0.60–0.75**, replicating `real_v2`'s 0.70.

**What would refute H1:** a calm-quartile AUC whose interval includes 0.5, with at least
15 events. That would say the development-half finding was the 12-event fluctuation it
looks like.

**What would support it:** an interval clearly above 0.5, which would mean the
simulator's warning sign is real in history after all, in the low-noise corner where the
simulator's own conditions most nearly hold — and would make "calm but sluggish" a
sensible thing to watch for.

## Out of scope

Any claim about particular countries. Any use of the identity key before scoring.
Re-testing on `real_v2`, whose test half is spent; a figure computed there after
unsealing is reported, if at all, as exploratory and clearly labelled.
