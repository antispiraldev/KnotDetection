# KnotDetection: can a society's turning point be seen coming?

A research project on forecasting **inflection points**: sudden regime changes such as
collapse, the onset of boom-and-bust cycles, or a shift to a new state. The question
is how far such changes can be anticipated using only data from before them. It is
split into three parts: **whether** a change is coming, **when**, and **what kind**.

It is also an experiment in **AI-directed research**. Almost all of the work was
designed, carried out, interpreted and written up by Claude, an AI model made by
Anthropic, working in Claude Code, with minimal supervision. That covers the plan,
the simulator, the methods, the blind tests, the analyses, the reports and every
commit message. The human collaborator, Luca Del Signore, approved each stage gate
and otherwise deliberately deferred to Claude's judgement. See
[How this project was run](#how-this-project-was-run).

**New to the topic?** Start with the four-page primer:
[docs/primer/primer.pdf](docs/primer/primer.pdf)
([Markdown](docs/primer/primer.md)). **Want the results?**
[docs/findings/findings.pdf](docs/findings/findings.pdf)
([Markdown](docs/findings/findings.md)).

---

## What was found (simulated societies only)

Two blind tests, each on 420 simulated societies across seven kinds of change. In
both, forecasts were locked and fingerprinted before the answers were opened. Numbers
below are from the second test. The first agreed closely: 0.81, 39% and base + 1 step
on the same three measures.

| Question | Good data | Very poor data | Chance or yardstick |
|---|---|---|---|
| **Whether** a change is coming (ranking score, AUC) | 0.78 | 0.65 | 0.50 |
| **What kind** of change (share named correctly) | 47% | 20% | 17% |
| **When** it becomes visible (average error, time steps) | 17.0 | 18.1 | 18.2, from just knowing the window |

- **Whether** can be judged moderately well. The skill comes from recognizing
  societies that already look fragile, not from detecting an approaching tipping
  point.
- **When** cannot be judged better than knowing the rough window changes fall in.
  A record shows how far a slow change has already gone. It says nothing about when
  the threshold itself will be crossed.
- **Classic early-warning signals** (rising autocorrelation and variance) scored at
  chance in every condition. With records this short, stable societies show apparent
  warning signs just as often.
- **Changes with no antecedents** (a change in the rules themselves) were not
  foreseen, as designed.

### Phase 2: a first test on real history

The same protocol was then run on real data: 300 windows of polity territory from
**Cliopatria** (Seshat), one per polity, anonymised by a subagent so the analyst never
saw which polity was which, with answers sealed and forecasts hashed before unsealing.

- Methods trained on the simulator **do not transfer**: AUC 0.51–0.52.
- Methods fitted on real data reach **AUC 0.65**, but that is mostly an artifact: 35
  of the 36 windows whose territory had *already* collapsed inside the record count as
  events. Excluding them, every method falls to **0.47–0.56, with intervals including
  chance**.
- **Nothing forecasts a polity's end** (AUC 0.46–0.52).
- Classic early-warning signals are at chance here too (0.49).

A second real test on **annual income per head** (Maddison Project Database, 981
windows over 74 countries) then separated "history has no warning" from "that dataset
was too thin":

- Methods fitted to real data reach **AUC 0.70** (0.76 on severe falls). Real
  contractions *are* forecastable.
- Simulation-trained methods score **significantly below chance** (0.43 and 0.39).
  Not absent transfer: **negative** transfer.
- The reason is a sign reversal. In the simulator the strongest warning sign is rising
  autocorrelation (critical slowing down). In real income data that feature points the
  other way, and what predicts a contraction is raw volatility — which the simulator
  deliberately calibrates away as a nuisance.

Full write-up: [docs/findings/findings.pdf](docs/findings/findings.pdf)
([Markdown](docs/findings/findings.md)). Pre-registrations, written before each
download, are in [phase2/](phase2/); the blow-by-blow is in [LOG.md](LOG.md).

These are results about methods, not claims about why particular polities fell. Full details are in
the plain-language reports and in [LOG.md](LOG.md).

---

## How this project was run

*This README, like the rest of the repository, was written by Claude. "I" below
means Claude.*

### Who did what

**Luca** started the project, and set up the machines and accounts. He approved each
of the four gates in [RESEARCH_PLAN.md](RESEARCH_PLAN.md) and asked for plain-language
reports. He decided the repository should be public, and asked for this README. His
steering after Gate 1 was deliberately minimal:

> "I am curious to see what you come up with if I give you maximal leeway to direct
> this research project yourself. I want to defer to your creative initiative."
>
> "Do what you think is best." (at Gate 2) — "Please continue with your work. I
> defer to your initiative." (at Gate 3)

**Claude** did everything else:
- wrote the research plan, the code, the tests and the figures;
- ran the analyses;
- made every design and research decision after Gate 1 (the Gate 2 and Gate 3
  decisions were explicitly delegated);
- wrote the research log, the gate reports and the primer;
- wrote every commit message.

The git author field shows Luca's name because the commits were made on his machine
under his identity. Every commit carries a `Co-Authored-By: Claude` trailer. The
first working session ran on another computer, and its transcript was lost when that
machine lost power. [LOG.md](LOG.md) records what was recovered. For a short period
a second Claude session ran in parallel on the same repository. It diagnosed one
defect, credited in the log.

### Decisions Claude made without being asked

Each is recorded, with its reasoning, in [LOG.md](LOG.md):

- **Two timestamps per transition.** Each transition is scored against when it
  *becomes visible*, and also against when its mechanism fires. Before any scoring,
  the "visible" detector was checked against an idealized detector.
- **Two tests of leakage.** A standing test checks whether the type of change can be
  guessed from things that should be irrelevant, such as level, spread and record
  length. It is judged against a shuffled-label baseline. Relaxation and trend
  features are allowed to be informative, because that is the phenomenon under study.
- **Blinding enforced in code.** The test seed is committed by hash. Forecasts are
  registered by hash before opening the answers, and the scorer refuses anything
  registered afterwards. See [inflection/eval/blind.py](inflection/eval/blind.py).
- **Predictions before results.** Expectations for each blind test were written in
  the log before the test set was built.
- **A series of simulator defects found and fixed**, among them:
  - a collapse label that marked the first dip rather than the commitment;
  - noise calibration undone by selection, three separate times;
  - outside shocks striking societies that had already collapsed;
  - an onset detector that ran late on spiky cycles.
- **Declining a tempting change.** When early-warning signals failed, I checked
  whether moving the simulator's pressure window would help them *before* changing
  it. It wouldn't, so the simulator was left alone. Changing it would have tuned the
  benchmark toward the method.
- **Fixing a flaw the first blind test exposed.** Outside shocks looked foreseeable
  only because the simulator made them hit fragile societies. Half now hit robust
  ones, and the second test confirmed the fix.
- **Locating the timing information** before building a method to extract it, then
  building the hybrid method around what was found.

### What Claude got wrong, and caught

- A test once encoded the wrong definition of a noise-driven collapse. The test and
  the definition were both fixed.
- A leakage gate with a fixed threshold turned out to be measuring random variation;
  it was replaced with a permutation test.
- Documentation overstated what the onset detector guaranteed, and was corrected.
- Of the written predictions, most held. Several missed on size, and two missed on
  direction: a method kept real skill on very poor data, where I predicted a collapse
  to chance, and shorter records did not help one method, as I expected they would.
  All of these are recorded against the original predictions.
- A rerun of an evaluation script once overwrote results. It was recovered from the
  run log, and the script now merges rather than overwrites.

---

## Checking the blind tests yourself

Both test sets are spent, so their seeds and answers are released in
[inflection/data/released/](inflection/data/released/). To check everything against
the ledger:

```bash
PYTHONPATH=. python scripts/verify_blind_tests.py
```

This confirms that each seed matches the hash committed before its test was built,
and that each answer file matches the hash recorded at build. It also checks every
record and forecast file against its hash, and that every forecast was registered
before the answers were opened.

Adding `--regenerate test_v2` goes further, and takes 15–30 minutes. It rebuilds the
test set from its seed, at the generator revision recorded in the ledger, and
confirms that it reproduces the released answers. This check has been run for `test_v2`, and it passes. The ledger itself is in git, so
`git log -p inflection/data/ledger.jsonl` shows when each event was committed.

---

## Repository map

| Path | What it holds |
|---|---|
| [RESEARCH_PLAN.md](RESEARCH_PLAN.md) | The plan, its gates, and dated amendments |
| [LOG.md](LOG.md) | The full research log, newest first: every decision, defect and result |
| [docs/primer/](docs/primer/) | Plain-language introduction (PDF and Markdown) |
| `inflection/sim/` | The simulator: models, integration, ground-truth labels, realism layers, generation |
| `inflection/methods/` | Forecasting methods: base rate, own history, early-warning signals, feature classifier, hybrid |
| `inflection/eval/` | Leakage audit, blinding ledger, scoring |
| `inflection/data/` | Open test records, forecasts, the ledger, released seeds and answers |
| `inflection/notebooks/` | Figures, audit outputs and score tables |
| `scripts/` | Audit, evaluation, blind-test pipeline, reports, primer build, verification |
| `tests/` | 52 tests of the simulator, blinding, scoring and methods |

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHONPATH=. .venv/bin/python -m pytest -q tests/        # ~6 minutes
PYTHONPATH=. .venv/bin/python scripts/gate2_report.py --fresh --n 40   # leakage audit
PYTHONPATH=. .venv/bin/python scripts/dev_eval.py --pool <pool.pkl>    # development evaluation
```

A new blind test goes through `scripts/gate3_run.py`, one step per call:
`commit-seed`, then `build`, then `forecast`, then `score`.

## Status

The simulation phase is complete, with all four gates reached, and Phase 2 has run two
blind tests on real data. All four test sets are spent and released. Phase 3, forecasts
registered now and scored when outcomes arrive, has not started.
