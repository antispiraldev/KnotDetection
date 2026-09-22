# Data preparation log: `real_v1` (public)

Written by `phase2/prepare_cliopatria.py`, run by the data-preparation subagent.
Contains no polity names, no polity-specific years and nothing about test outcomes.
Identities and test outcomes are only in the sealed key and private log under
`inflection/data/sealed/` (git-ignored).

## Dataset

- Name: Cliopatria (Seshat Global History Databank), licence CC-BY 4.0
- Repository: `Seshat-Global-History-Databank/cliopatria`
- Release tag: `v0.2.0-duplicate` ("Re-release v0.2.0 to re-trigger Zenodo after authentication issue", published 2026-05-24T21:54:11Z)
- Commit sha: `ad28a691b7c07c1fca89d0e0636d324667d2a258`
- How obtained: file in the release tag's tree (release has no assets)
- URL: https://raw.githubusercontent.com/Seshat-Global-History-Databank/cliopatria/ad28a691b7c07c1fca89d0e0636d324667d2a258/cliopatria.geojson.zip
- Download date (UTC): 2026-09-22T13:51:27+00:00
- `cliopatria.geojson.zip` sha256: `d01ae3a20d358cc5d54f69d9d725d390767d9c8759ac89ad6f90c58d106f3370` (44231317 bytes)
- Zip member used: `cliopatria_polities_only.geojson` (FeatureCollection name `cliopatria_polities_only_v012`)

## Contents

- Property names: `Area`, `Components`, `FromYear`, `MemberOf`, `Name`, `SeshatID`, `ToYear`, `Type`, `Wikidata`, `Wikipedia`
- Total feature rows: 13765
- Rows by Type: {'POLITY': 13380, 'RELATION': 385}
- POLITY rows kept: 13380; distinct polity names: 1583
- Year range over all POLITY rows: -3400 to 2024 (dataset end used: 2024)
- POLITY rows with Area <= 0 or non-finite: 0; rows with FromYear > ToYear: 0

## Overlapping rows (same polity, same year covered by two rows)

- Polities with any overlap: 0 of 1583
- Overlapping row pairs: 0 (of which with equal FromYear: 0)
- Polity-years covered by two or more rows: 0 of 251045 covered polity-years
- Polity-years inside a polity's first..last year but covered by no row (gaps): 19433

## Windows

- Fallback (W=150, H=75) used: **no**
- W = 100, H = 50, step = 5 years, 20 observations per record
- Candidate origins (multiples of 50 with the record window inside the polity's span): 3309
  - eligible: 2527
  - ineligible:ended_at_or_before_origin: 72
  - ineligible:gap_at_horizon_end: 51
  - ineligible:horizon_past_dataset_end: 22
  - ineligible:record_gap: 637
- Polities with at least one eligible window: 599

(Class balance over all eligible windows is not reported, since it would bound the test balance.)

## Split

- Dev: 299 polities, 1267 windows (all eligible windows of those polities)
- Test: 300 polities, 300 windows (one per polity)
- Dev events: 407; dev controls: 860
- Dev events by kind: area_loss 219, ending 188

## Judgement calls

Judgement calls where the pre-registration is silent or ambiguous (each applied
uniformly, chosen to be independent of outcomes):

1. **Download source.** The latest GitHub release has no binary assets. The zip is a
   file in the tagged tree, so it was fetched from `raw.githubusercontent.com` with the
   URL pinned to the tag's commit sha (immutable).
2. **Parsing.** Only each feature's `properties` object is parsed
   (`json.JSONDecoder.raw_decode` starting at the `"properties":` key on each feature
   line); geometry is never decoded. `RELATION` rows are dropped.
3. **Overlap ties.** The rule "later FromYear wins" is extended, for rows with equal
   FromYear, to "later ToYear wins, then later row in file order".
4. **Coverage and gaps.** A year is covered if some row of the polity has
   FromYear <= year <= ToYear. Years inside a polity's span not covered by any row are
   gaps (no value).
5. **Candidate origins.** A candidate origin is a multiple of 50 whose record window
   [t0-W, t0) lies inside the polity's first..last covered year. Candidates are then
   checked in this fixed order, and the first failed check is the reason logged:
   record gap; non-positive sampled area; horizon past the dataset end; outcome.
6. **Dataset end.** The dataset end is the largest ToYear among POLITY rows. Any window
   with t0+H after it is dropped *before* its outcome is looked at, even if an event
   inside the observed part would be visible: this keeps the exclusion independent of
   outcomes.
7. **Area-loss threshold.** "Max over [t0-W, t0)" uses all covered years of the record
   window (every year, not only the 20 sampled years). Area loss is checked on covered
   years in (t0, t0+H] only; a year t0 itself is neither record nor horizon. The
   definition is followed literally: if Area has already fallen below half of the
   record maximum *within* the record and stays there, the first horizon year counts as
   an area-loss event. (Stated here as a property of the pre-registered definition, as
   checked on synthetic series; no data-derived counts of it are computed.)
8. **Ending year.** The ending year is the final row's ToYear (the last year the polity
   exists). Tie with an area-loss year -> "area_loss", as instructed.
9. **Non-events that are not controls.** Split into three logged reasons: the polity's
   last year is <= t0 (it ends before the horizon starts, so no ending in (t0, t0+H]);
   the last year is inside the horizon but not before 2000 (cannot happen with the
   dataset end used here, kept as a guard); t0+H falls in a gap.
10. **Split details.** The sorted name list is shuffled as `rng.permutation(n)`; dev is
    the first floor(n/2). Test polities, in that shuffled order, each draw one window
    with `rng.integers(k)` from their eligible windows sorted by t0. Then the test list
    and the dev list (dev windows first listed polity by polity in shuffled order, t0
    ascending) are each shuffled with `rng.permutation`, test first. Dev group ids are
    assigned by first appearance in the shuffled dev list. All draws use one
    `np.random.default_rng(split_seed("real_v1"))`; under the fallback, a fresh generator
    from the same seed is used.
11. **Values** are divided by the median of the record's 20 sampled areas; times are
    `(year - (t0-W)) * 90 / W`, i.e. 0, 4.5, ..., 85.5 (0, 3, ..., 87 under the fallback).
12. **Name-leak check.** Case-sensitive whole-word search for every polity name in every
    open text output (manifest, dev labels, this log, the script); for `.npz` files the
    member names are searched and every array is checked to be floating point.

## Commands

Shell and Python commands run by the data-preparation agent, in order (outputs that
would identify polities are not reproduced here):

1. `cat phase2/PREREGISTRATION.md; ls phase2 inflection inflection/data inflection/eval; cat .gitignore`
   -- read the binding pre-registration and the repository layout.
2. `cat inflection/eval/blind.py; tail inflection/data/ledger.jsonl` (via grep/sed) -- read the
   sealing API (`split_seed`, `seal_external_pool`, its forbidden meta keys) and confirmed
   that the ledger holds a `seed_committed` event for `real_v1` and no `pool_built` event.
3. `python -c "np.load('inflection/data/test_v2/irregular/series.npz') ..."` -- confirmed the
   simulator pool layout: one float64 array per world id plus `t_<id>` for its times.
4. `gh api repos/Seshat-Global-History-Databank/cliopatria/releases/latest` and
   `gh api repos/.../releases`, `gh api "repos/.../contents?ref=<tag>"`,
   `gh api repos/.../commits/<tag>` -- found the latest release, that no release has
   binary assets, and that `cliopatria.geojson.zip` is a tracked file of the tagged tree.
   The latest tag, the previous tag and the default branch all point to the same commit.
5. `curl -sSL -o phase2/raw/probe.zip https://raw.githubusercontent.com/.../<commit>/cliopatria.geojson.zip`,
   `sha256sum`, and a short Python probe (`zipfile` + `json.JSONDecoder.raw_decode` on each
   feature line) -- learned the file format: one feature per line, property names, value
   types, that `Area` is always positive and `FromYear <= ToYear` in every row, and the
   dataset's overall year range. The probe printed a handful of polity names (seen only by
   this agent). The probe zip had the same sha256 as the final download and was deleted
   (`rm phase2/raw/probe.zip`); the script downloads afresh.
6. Wrote `phase2/prepare_cliopatria.py` (this pipeline).
7. `PYTHONPATH=. .venv/bin/python phase2/prepare_cliopatria.py` -- dry run: build and
   validate in memory, print only public facts (split sizes, ineligibility counts,
   whether the fallback is needed). It downloaded the zip into `phase2/raw/`.
7b. A Python check of `windows_for` on hand-made synthetic series (constant area with a
   drop; an ending; overlapping rows; a gap; series reaching the dataset end; an ending
   just before 2000) -- confirmed events, event kinds and years, the overlap rule and
   each ineligibility reason behave as specified. No real windows were inspected.
8. `PYTHONPATH=. .venv/bin/python phase2/prepare_cliopatria.py --seal` -- write all
   outputs, validate, run the name-leak check, seal once, append the ledger event below.

## Validation

- Every test id is in `series.npz` (values and `t_` times) and in the sealed truth, and ids are contiguous.
- Every record, test and dev, has exactly 20 finite, positive values, and times equal the formula.
- Each test polity contributes exactly one window; no polity is in both splits.
- Name-leak check: 1583 polity names searched in 6 open files; hits: 0. **PASSED**

## Outputs (sha256)

- `inflection/data/real_v1/series.npz`: `517b3a211b0742f0eda085f9c6c2b995a6ec8ee6676f623baa83084dacc122d0`
- `inflection/data/real_v1/manifest.json`: `dcbde43386e44fb7b26de0f02f22373532b844ae8ec85c48b16a13a378e7dffd`
- `phase2/data/dev/series.npz`: `266823f63016df56ea1bdde75ff5fb20b6516396d357df67a76e4336dd11ff78`
- `phase2/data/dev/labels.json`: `15f58281171bbd049d0491c21a4ac0ad3a7308c32a6ae51eee3b19746621e1dd`
- `inflection/data/sealed/real_v1/truth.json`, `inflection/data/sealed/real_v1_key.json`,
  `inflection/data/sealed/real_v1_private_log.md`: sealed, git-ignored; the truth hash is in the ledger.

## Ledger event appended by `seal_external_pool` (called once)

```json
{
  "H": 50,
  "W": 100,
  "dataset": "Cliopatria",
  "dataset_commit": "ad28a691b7c07c1fca89d0e0636d324667d2a258",
  "dataset_sha256": "d01ae3a20d358cc5d54f69d9d725d390767d9c8759ac89ad6f90c58d106f3370",
  "dataset_version": "v0.2.0-duplicate",
  "event": "pool_built",
  "external": true,
  "fallback_used": false,
  "generator_revision": "3843d818a7583d62d61c2a7ee23f2f9846b45fa6",
  "n_dev_polities": 299,
  "n_dev_windows": 1267,
  "n_obs": 20,
  "n_requested": 300,
  "n_test_polities": 300,
  "n_test_windows": 300,
  "n_worlds": 300,
  "record_sha256": {
    "real": "517b3a211b0742f0eda085f9c6c2b995a6ec8ee6676f623baa83084dacc122d0"
  },
  "test_set": "real_v1",
  "truth_sha256": "a517ec2c0c21f91c0afc126411fe2e9e99a09410c808265f68e58fd81450627e"
}
```
