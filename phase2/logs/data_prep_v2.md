# Data preparation log: `real_v2` (public)

Written by `phase2/prepare_maddison.py`, run by the data-preparation subagent.
Contains no country names or codes, no country-specific years and nothing about
test outcomes. Identities and test outcomes are only in the sealed key and private
log under `inflection/data/sealed/` (git-ignored).

## Dataset

- Name: Maddison Project Database 2020 (Groningen Growth and Development Centre), licence CC-BY 4.0
- Version: 2020 (file `mpd2020.xlsx`)
- URL: https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx
- URL after redirects: https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx
- HTTP headers at download: {"Content-Length": "1764793", "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8", "ETag": "W/\"69d3b691-6299-42fb-90f2-26fa22f186d3-33.36;1605281601766\"", "Last-Modified": "Fri, 13 Nov 2020 15:33:21 GMT"}
- Download date (UTC): 2026-09-22T19:12:32+00:00
- `mpd2020.xlsx` sha256: `d20853c2e0930d6855fb6d8138da11f24fcf313d234e2db9773ea1f551adfec3` (1764793 bytes)
- The URL given in the brief was checked first and answered 200 with an xlsx
  body, so no alternative GGDC location was needed.

## Sheet and columns

- Sheets in the workbook: `Notes`, `Sources`, `Full data`, `GDP pc`, `Population`, `Regional data`
- Sheet used: `Full data` -- the country-year panel (one row per country and year). It is the only sheet whose header carries a country column, a year
  column and a GDP-per-capita column in a narrow table; the other data sheets are
  wide year-by-country tables of the same numbers, or regional aggregates.
- Header of the sheet used: `countrycode`, `country`, `year`, `gdppc`, `pop`
- Columns taken, by role: {"country": "country", "countrycode": "countrycode", "gdppc": "gdppc", "year": "year"}
- Renamings needed: none
- Only `gdppc` is used, by country and year; `pop` is not read.

## Contents

- Panel rows: 21682
- Countries (distinct country codes with at least one recorded year): 169
- Duplicate (country, year) rows: 0
- Panel year range: 1 to 2018
- Cells with a blank `gdppc`: 1976
- Cells with a non-positive `gdppc` (treated as missing, see judgement 4): 2
- Recorded country-years (finite, positive `gdppc`): 19704
- Country-years inside a country's first..last recorded year with no value (gaps): 32054
- Countries whose code maps to more than one name: 0

## Windows

- Fallback (W=20, H=10) used: **no** (trigger: fewer than 150 test windows)
- W = 30 years of record, H = 15 years of horizon, step = 1 year, 30 observations per record
- Event: a recorded horizon year below 0.75 x the record maximum
- Candidate origins (multiples of 5 with the record window inside the country's recorded span): 9348
  - eligible: 2011
  - ineligible:already_in_collapse: 281
  - ineligible:nonpositive_gdppc: 0
  - ineligible:outcome_not_observable: 447
  - ineligible:record_gap: 6609
- Countries with at least one eligible window: 147

(Class balance over all eligible windows is not reported, since it would bound the
test balance. Neither is the balance of the pre-1950 and post-1950 halves.)

## Split

Countries, not windows, are split 50/50 with the seed committed for `real_v2`
before the download. **Both halves keep every eligible window of their countries**
(pre-registration: unlike `real_v1`, a later window's existence does not reveal an
earlier outcome here), so test intervals are bootstrapped over countries and both
halves carry an anonymised group id.

- Dev: 73 countries, 1030 windows
- Test: 74 countries, 981 windows
- Dev events: 189; dev controls: 841
- Dev windows by era: pre1950 649, post1950 381
- Windows per country, dev half: min 1, median 5, max 138

## Judgement calls

Judgement calls where the pre-registration is silent or ambiguous (each applied
uniformly, chosen to be independent of outcomes):

1. **Sheet choice.** The workbook holds a country-year panel sheet and two wide
   year-by-country sheets (one per variable) besides notes, sources and a regional
   sheet. The panel sheet is picked structurally, not by name: it is the only sheet
   whose header row carries a country column, a year column and a GDP-per-capita
   column in a table of at most ten columns. Its name and all the sheet names are
   logged below. The wide sheets hold the same numbers in a shape that would have to
   be melted, and the regional sheet is aggregates, not countries.
2. **Column names.** The four columns the pre-registration expects are matched on the
   lower-cased header, first exactly and then by substring; any renaming is logged.
3. **Country key.** The country code is the identity key, and the country name is
   carried only into the sealed key. Code and name were checked to be one-to-one in
   this panel. Countries are sorted by code before the shuffle.
4. **What counts as a recorded year.** A year is recorded when the panel gives it a
   finite, strictly positive gdppc. Non-positive cells are treated as missing rather
   than as observations: the pre-registration itself refuses to build a record on
   them, a non-positive real income is not a measurement, and treating one as a fall
   would manufacture an event out of a missing-data code. The rule is applied to
   every country and year before any window is formed, and the number of cells it
   touches is reported under "Contents". Because of it, the "non-positive value in
   the record" ineligibility reason is necessarily zero; the check is kept as a guard.
5. **Candidate origins.** A candidate origin is a multiple of 5 whose record window
   [t0-W, t0) lies inside the country's first..last recorded year. Candidates are then
   checked in this fixed order, and the first failed check is the reason logged:
   a gap in the record; a non-positive value in the record; already in collapse (the
   value at year t0-1 is below 0.75 x the record maximum); the outcome not observable.
6. **The record maximum** is the maximum over the W recorded years of [t0-W, t0).
   With annual sampling every year of the record is used, so "the record" and "the
   sampled record" are the same thing here.
7. **"Last recorded year" of the record** is year t0-1, the last year of the record
   window; the record has no gaps by the time this is checked. The year t0 itself is
   neither record nor horizon, exactly as in `real_v1`.
8. **Outcome observable (condition 3), literally.** A window is an event if some
   recorded year of (t0, t0+H] is below 0.75 x the record maximum, and the event year
   is the first such year, whatever happens later. It is a control only if every year
   of the horizon is recorded and none is below the threshold. Otherwise the outcome
   is not observable and the window is dropped. This is the one eligibility rule that
   looks at the outcome, and it does so because the pre-registration says so: a
   horizon that runs past the end of the data, or over a gap, still counts when the
   fall happened before the data stopped. No extra "horizon past the dataset end"
   rule was added on top of it.
9. **Severity** (a secondary outcome, sealed) is computed as the minimum over the
   *recorded* horizon years, which for a control is the whole horizon. A control can
   never be severe, since its horizon never goes below 0.75 x the maximum.
10. **Era** (also sealed) is "pre1950" if t0 <= 1950 else "post1950", as written.
11. **Split details.** The code list, sorted, is shuffled as `rng.permutation(n)`; dev
    is the first floor(n/2), test the rest. Both halves keep every eligible window of
    their countries. Windows are listed country by country in that shuffled order,
    t0 ascending, and then each list is shuffled with `rng.permutation`, test first,
    then dev. All draws come from one `np.random.default_rng(split_seed("real_v2"))`;
    under the fallback a fresh generator from the same seed is used.
12. **Group ids** are drawn from a single counter over both halves in the order the
    windows appear after shuffling, test list first: no id is ever shared between the
    splits, and an id says nothing about its country beyond the shuffled order.
13. **Values** are divided by the median of the record's W values; times are
    `(year - (t0-W)) * 90 / W`, i.e. 0, 3, ..., 87 (0, 4.5, ..., 85.5 under the
    fallback). The origin sits at t = 90 for every window.
14. **Leak check.** Country names are searched case-sensitively and whole-word; country
    codes case-sensitively with a word boundary on both sides. A hit falling inside a
    run of 32 or more hex characters is reported separately as a hash coincidence
    rather than dropped silently. For `.npz` files the member names are searched and
    every array is checked to be floating point.

## Commands

Shell and Python commands run by the data-preparation agent, in order (outputs that
would identify countries are not reproduced here):

1. `cat phase2/PREREGISTRATION_v2.md`, `cat phase2/prepare_cliopatria.py`,
   `cat phase2/logs/data_prep.md`, `cat .gitignore`, `ls phase2 inflection/data`
   -- read the binding pre-registration and the previous round's script and log.
2. `cat inflection/eval/blind.py; tail inflection/data/ledger.jsonl` -- read the sealing
   API (`split_seed`, `seal_external_pool`, its forbidden meta keys) and confirmed that
   the ledger holds a `seed_committed` event for `real_v2` and no `pool_built` event.
3. `head -40 inflection/data/real_v1/manifest.json; head -c 600 phase2/data/dev/labels.json`
   -- confirmed the output layout to mirror.
4. `curl -sSIL https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx`
   -- verified the official Groningen URL still answers 200 with an xlsx body; no move,
   so no alternative location was needed.
5. `curl -sSL -o <scratchpad>/probe.xlsx <that URL>` plus a short openpyxl/pandas probe
   -- learned the workbook's sheet names and sizes, the panel sheet's header row and
   dtypes, the number of countries, the panel's year range, that country code and
   country name are one-to-one, that no (country, year) pair repeats, that years run
   monotonically within a country, and how many gdppc cells are blank or non-positive.
   The probe printed the country list (seen only by this agent). The probe file has the
   same sha256 as the final download; the script downloads afresh into `phase2/raw/`.
6. Wrote `phase2/prepare_maddison.py` (this pipeline).
7. `PYTHONPATH=. .venv/bin/python phase2/prepare_maddison.py` -- dry run: build and
   validate in memory, print only public facts (split sizes, ineligibility counts,
   whether the fallback is needed). Nothing written but the download.
7b. A Python check of `windows_for` on hand-made synthetic series (a flat series; a
   series already below 0.75 of its own peak at the origin; a drop inside the horizon;
   a drop in a year that is not recorded; a horizon running off the end of the data with
   and without an earlier drop; a gap inside the record) -- confirmed each eligibility
   rule, the event year, the severity flag and every ineligibility reason. No real
   windows were inspected.
8. `PYTHONPATH=. .venv/bin/python phase2/prepare_maddison.py --seal` -- write all
   outputs, validate, run the name-and-code leak check, seal once, append the ledger
   event below.

## Validation

- Every test id is in `series.npz` (values and `t_` times) and in the sealed truth, and test and dev ids are each contiguous from 0.
- Every record, test and dev, has exactly 30 finite, positive values, and times equal the formula, starting at 0 and ending below 90.
- No country is in both splits; every eligible country is in exactly one of them.
- Group ids are a bijection with countries and are never shared between splits.
- Leak check: 169 country names and 169 country codes searched in 6 open files; hits: 0; hits inside hex digests (coincidences, listed in the private log): 0. **PASSED**

## Outputs (sha256)

- `inflection/data/real_v2/series.npz`: `0843fcc5d7e63abb8c621b624e4899ceaf34dc9203c8d23213f5e216f46c6ec2`
- `inflection/data/real_v2/manifest.json`: `f78c72ac18772eae49d4beaffbc0b043266b98200fdf47c524a03734da5b344c`
- `phase2/data/dev_v2/series.npz`: `b64fd6a5d2d81ce577db8304a4f1d9f84182c6d725a76b6b63513a3ff63a794c`
- `phase2/data/dev_v2/labels.json`: `2020f2ac4453491e711c0b4d2b433327f735ee9664fac78290b72e29522ded35`
- `inflection/data/sealed/real_v2/truth.json`, `inflection/data/sealed/real_v2_key.json`,
  `inflection/data/sealed/real_v2_private_log.md`: sealed, git-ignored; the truth hash is in the ledger.

## Ledger event appended by `seal_external_pool` (called once)

```json
{
  "H": 15,
  "W": 30,
  "dataset": "Maddison Project Database",
  "dataset_sha256": "d20853c2e0930d6855fb6d8138da11f24fcf313d234e2db9773ea1f551adfec3",
  "dataset_version": "2020",
  "event": "pool_built",
  "external": true,
  "fallback_used": false,
  "generator_revision": "60cffe65880fd64f07269ce5e34e83608ceb327a",
  "n_dev_countries": 73,
  "n_dev_windows": 1030,
  "n_obs": 30,
  "n_requested": 981,
  "n_test_countries": 74,
  "n_test_windows": 981,
  "n_worlds": 981,
  "record_sha256": {
    "real": "0843fcc5d7e63abb8c621b624e4899ceaf34dc9203c8d23213f5e216f46c6ec2"
  },
  "sheet": "Full data",
  "test_set": "real_v2",
  "truth_sha256": "b4fbd654207fbd1829c9bd0117d0300e01a9e0bf4db96fccf35278d56249b223"
}
```
