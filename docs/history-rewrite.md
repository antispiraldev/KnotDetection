# History rewrite, 2026-09-29

Every commit in this repository was rewritten once, to change the author and
committer identity. Nothing else changed: the tree at the tip is byte-for-byte the
same object as before the rewrite (`3b72636549686f559f6b569c7e3db59ecee5e672`), and
no file, commit message or date was altered.

The old hashes therefore no longer exist here, and `LOG.md`, `README.md` and
`inflection/data/ledger.jsonl` still cite them. That matters most for the ledger,
which records the exact generator revision used to build each blind test set, and
which `scripts/verify_blind_tests.py --regenerate` checks out to rebuild a test set
from its seed. **The ledger is append-only and was deliberately not edited.** Use the
table below to translate.

## Revisions recorded in the ledger

| test set built at | old revision | new revision |
|---|---|---|
| `test_v1` | `83fe02cbeb` | `162ffb3566` |
| `test_v2` | `d473e564bd` | `2575de89d8` |
| `real_v1` | `3843d818a7` | `32ffbd019f` |
| `real_v2` | `60cffe6588` | `01c58c6bf7` |

## Every commit

| old | new | subject |
|---|---|---|
| `d0427d67e7` | `4f8bbc6da3` | Simulator for the synthetic-society benchmark, with a leakage audit |
| `2ccc61a0f4` | `ff3c26102d` | Check the CV calibration rather than assume it |
| `81fc6a5f22` | `cd977955d4` | Fix three ground-truth and calibration defects the Gate 2 audit exposed |
| `7208fff02e` | `edb07e61d8` | Gate 2: fix onset resolution, record failed designs, add review materials |
| `3f877f67af` | `85508d19cd` | Close Gate 2: record decisions, amend the plan, set the Gate 3 work plan |
| `df4861232b` | `809ac70ed5` | Gate 3 part 1: onset check, four simulator fixes, blinding, first methods |
| `4222bbc997` | `3749b4601e` | Commit the test_v1 seed by salted hash, before any test forecast exists |
| `83fe02cbeb` | `162ffb3566` | Feature-classifier method, scorer and method tests, pre-registered expectations |
| `eed863220e` | `4e67e9ba4c` | Build test_v1: 420 open pre-origin records per layer; truth sealed by hash |
| `d130c0ed98` | `d2473bf776` | Register test_v1 forecasts: 4 methods x 7 layers, hashed before unsealing |
| `3760006428` | `9bf680e5ba` | Gate 3: first blind results on test_v1; stop for review |
| `ba7736d4b4` | `fe0021c0f5` | Robust shock worlds, lead-time layers, and the hybrid method |
| `2df73e575f` | `3a44526fab` | Commit the test_v2 seed by salted hash, before any test_v2 forecast exists |
| `d473e564bd` | `2575de89d8` | Timing-information analysis, larger dev pool results, written expectations for test_v2 |
| `0ce6200724` | `c3269eb22d` | Build test_v2: 420 open records x 9 layers; truth sealed by hash |
| `ad034869a1` | `866d07d8f2` | Register test_v2 forecasts: 5 methods x 9 layers, hashed before unsealing |
| `02432f18ee` | `017a8f1e22` | test_v2: second blind results, compared with written expectations |
| `3d1ae83f0a` | `015451e5ad` | Gate 4: analysis written; stop for review |
| `6419d20a7b` | `67a92341ad` | Add a plain-language project primer (Markdown + PDF, five figures) |
| `fff507b5fc` | `e492a6b442` | Prepare for publication: README, released test answers, verification script |
| `2b53749243` | `91d30b630a` | Phase 2: pre-register the real-data test before downloading anything |
| `f51775a8ac` | `e574b5ae13` | Phase 2 evaluation script; record that test_v2 regenerates exactly from its seed |
| `3843d818a7` | `32ffbd019f` | Fix two defects a dry run exposed in the real-data evaluation, before any data |
| `92faf8866e` | `4a25fe5f46` | real_v1 built and sealed; declare secondary analysis S1; window robustness result |
| `66a4f95f67` | `56ab9998af` | Register real_v1 forecasts (7 methods), committed before unsealing |
| `05bc65ac2a` | `0c26c43916` | Phase 2 first blind result on real history; release real_v1 answers and key |
| `525110d837` | `f6a2da6eaa` | Pre-register real_v2 (Maddison GDP per capita) before downloading it |
| `7b982588b8` | `da3e15536c` | Generalize the real-data evaluation to both test sets |
| `60cffe6588` | `01c58c6bf7` | Extract the shared Markdown/PDF renderer so a second document can reuse it |
| `a0ed20e906` | `9a23cf29e9` | real_v2 built and sealed; forecasts registered before unsealing |
| `740a257909` | `042057ba2d` | real_v2 result: real contractions are forecastable, but the theory's sign is wrong |
| `6002fbf4f3` | `32896480cb` | Write up the findings: a report with figures, and update the README and primer |
| `852a9284be` | `42af951561` | Correct an inverted claim about autocorrelation in the real-data write-ups |
| `9013d6a689` | `c72437f15a` | Pre-register real_v3: does slow recovery show up in calm economies? |
| `689887c61c` | `25fa593445` | Amend real_v3 expectations: the calm-quartile effect fails to replicate |
| `2013e88fd0` | `b7298e73a0` | Add a state-of-play entry at the top of the log, for the next session |
| `bca7d61256` | `914c90af30` | Add a self-narrating plain-language explainer |
| `8478e8dff4` | `c0f1d99170` | Explainer: let the reader choose a voice, and prefer natural ones |
| `eeb516ed04` | `7c442abe42` | Narrate the explainer with the local Kokoro server |

## Verifying that nothing but the identity changed

A copy of the pre-rewrite history was kept as a git bundle outside the repository.
Given that bundle, `git diff <old-sha> <new-sha>` for any corresponding pair returns
nothing, and the commit messages, authored dates and parent structure match.
