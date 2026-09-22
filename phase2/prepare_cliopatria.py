"""Build the blinded real-data test set `real_v1` from Cliopatria.

Implements phase2/PREREGISTRATION.md, steps 2-6 of the data-preparation brief:
download, series and windows, split and anonymisation, outputs, logs, sealing.

Usage (from the repository root, PYTHONPATH set to it):

    python phase2/prepare_cliopatria.py            # dry run: build + validate in memory
    python phase2/prepare_cliopatria.py --seal     # write every output, validate, seal once

The dry run prints only public, outcome-free facts. `--seal` refuses to run if the
ledger already holds a `pool_built` event for `real_v1`, so the sealed truth and
the open records can never drift apart. No polity names or years are hard-coded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inflection.eval.blind import (  # noqa: E402
    LEDGER, SEALED, _events, seal_external_pool, split_seed,
)

NAME = "real_v1"
REPO = "Seshat-Global-History-Databank/cliopatria"
ASSET = "cliopatria.geojson.zip"
RAW = ROOT / "phase2" / "raw"
TEST_DIR = ROOT / "inflection" / "data" / NAME
DEV_DIR = ROOT / "phase2" / "data" / "dev"
PUBLIC_LOG = ROOT / "phase2" / "logs" / "data_prep.md"
KEY = SEALED / f"{NAME}_key.json"
PRIVATE_LOG = SEALED / f"{NAME}_private_log.md"

STEP = 5                 # sampling step of the record, years
ORIGIN_STEP = 50         # forecast origins are multiples of this
MAIN = dict(W=100, H=50)
FALLBACK = dict(W=150, H=75)
MIN_TEST = 60            # fallback trigger
ENDING_BEFORE = 2000     # an ending counts only if its year is < this
LOSS_FRAC = 0.5
T_ORIGIN = 90.0          # simulator's origin on its time scale
T_TOTAL = 300.0


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _gh_json(path: str) -> dict:
    try:
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True)
        return json.loads(out.stdout)
    except (OSError, subprocess.CalledProcessError):
        with urllib.request.urlopen(f"https://api.github.com/{path}") as r:
            return json.loads(r.read())


# --- step 2: download -------------------------------------------------------------

def download() -> dict:
    """Fetch the zip of the latest release (once) and return its provenance."""
    RAW.mkdir(parents=True, exist_ok=True)
    info_path = RAW / "download_info.json"
    zpath = RAW / ASSET
    if info_path.exists() and zpath.exists():
        info = json.loads(info_path.read_text())
        if sha256_file(zpath) == info["sha256"]:
            info["reused_existing_download"] = True
            return info
    rel = _gh_json(f"repos/{REPO}/releases/latest")
    tag = rel["tag_name"]
    commit = _gh_json(f"repos/{REPO}/commits/{tag}")["sha"]
    assets = {a["name"]: a["browser_download_url"] for a in rel.get("assets", [])}
    if ASSET in assets:
        url, how = assets[ASSET], "release asset"
    else:
        # The release carries no binary assets; the zip is a tracked file of the
        # tagged tree. Pin the URL to the tag's commit so it cannot move.
        url, how = (f"https://raw.githubusercontent.com/{REPO}/{commit}/{ASSET}",
                    "file in the release tag's tree (release has no assets)")
    urllib.request.urlretrieve(url, zpath)
    info = dict(url=url, how=how, release_tag=tag, release_name=rel.get("name"),
                release_published=rel.get("published_at"), commit_sha=commit,
                download_date=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                sha256=sha256_file(zpath), size_bytes=zpath.stat().st_size)
    info_path.write_text(json.dumps(info, indent=2))
    info["reused_existing_download"] = False
    return info


def read_properties(zpath: Path) -> tuple[list[dict], dict]:
    """Unzip and parse only each feature's `properties` object (geometry skipped)."""
    dec = json.JSONDecoder()
    rows, meta = [], {}
    with zipfile.ZipFile(zpath) as z:
        members = [m for m in z.namelist()
                   if m.endswith(".geojson") and not m.startswith("__MACOSX")]
        assert len(members) == 1, members
        meta["member"] = members[0]
        z.extract(members[0], RAW)
        with z.open(members[0]) as f:
            for line in f:
                s = line.decode("utf-8")
                if s.lstrip().startswith('"name":'):
                    meta["collection_name"] = json.loads("{" + s.strip().rstrip(",") + "}")["name"]
                if '"type": "Feature"' not in s:
                    continue
                i = s.index('"properties":')
                props, _ = dec.raw_decode(s, s.index("{", i))
                rows.append(props)
    return rows, meta


# --- step 3: series and windows ---------------------------------------------------

def build_series(rows: list[dict]) -> tuple[dict, dict]:
    """Yearly step function of Area per polity; later FromYear wins on overlap.

    Ties in FromYear (not covered by the pre-registration) go to the later
    ToYear, then to the later row in file order: a fixed, outcome-free rule.
    """
    by_name = defaultdict(list)
    for idx, r in enumerate(rows):
        by_name[r["Name"]].append((r["FromYear"], r["ToYear"], idx, float(r["Area"])))
    series, stats = {}, Counter()
    overlap_detail = {}
    for name, rs in by_name.items():
        y0 = min(r[0] for r in rs)
        y1 = max(r[1] for r in rs)
        area = np.full(y1 - y0 + 1, np.nan)
        painted = np.zeros(y1 - y0 + 1, dtype=int)
        for fy, ty, idx, a in sorted(rs):           # ascending: later rows overwrite
            painted[fy - y0: ty - y0 + 1] += 1
            area[fy - y0: ty - y0 + 1] = a
        ov = int((painted > 1).sum())
        pairs = sum(1 for i, a in enumerate(rs) for b in rs[i + 1:]
                    if a[0] <= b[1] and b[0] <= a[1])
        tie = sum(1 for i, a in enumerate(rs) for b in rs[i + 1:]
                  if a[0] <= b[1] and b[0] <= a[1] and a[0] == b[0])
        if ov:
            stats["polities_with_overlap"] += 1
            stats["overlapping_row_pairs"] += pairs
            stats["overlapping_row_pairs_same_fromyear"] += tie
            stats["polity_years_covered_twice_or_more"] += ov
            overlap_detail[name] = dict(pairs=pairs, years=ov, same_from=tie)
        stats["polity_years_covered"] += int(np.isfinite(area).sum())
        stats["polity_years_in_span_uncovered"] += int((~np.isfinite(area)).sum())
        series[name] = dict(y0=y0, y1=y1, area=area, last_year=y1)
    return series, dict(stats=stats, overlap_detail=overlap_detail)


def windows_for(name: str, s: dict, W: int, H: int, data_end: int, n_obs: int):
    """Yield (t0, status, info) for every candidate origin of one polity.

    A candidate origin is a multiple of ORIGIN_STEP whose record window
    [t0-W, t0) lies inside the polity's first..last covered year.
    """
    y0, y1, area = s["y0"], s["y1"], s["area"]
    cov = np.isfinite(area)
    first = -(-(y0 + W) // ORIGIN_STEP) * ORIGIN_STEP
    last = ((y1 + 1) // ORIGIN_STEP) * ORIGIN_STEP
    for t0 in range(first, last + 1, ORIGIN_STEP):
        rec = slice(t0 - W - y0, t0 - y0)
        if not cov[rec].all():
            yield t0, "ineligible:record_gap", None
            continue
        years = np.arange(t0 - W, t0, STEP)
        assert len(years) == n_obs
        vals = area[years - y0]
        if not (vals > 0).all():
            yield t0, "ineligible:nonpositive_area", None
            continue
        if t0 + H > data_end:
            # Outcome-independent: any horizon reaching past the dataset end is
            # dropped, whatever happens inside it.
            yield t0, "ineligible:horizon_past_dataset_end", None
            continue
        peak = float(area[rec].max())
        loss_year = None
        for y in range(t0 + 1, t0 + H + 1):
            if y0 <= y <= y1 and cov[y - y0] and area[y - y0] < LOSS_FRAC * peak:
                loss_year = y
                break
        end_year = y1 if (t0 < y1 <= t0 + H and y1 < ENDING_BEFORE) else None
        info = dict(years=years, vals=vals)
        if loss_year is not None or end_year is not None:
            if end_year is None or (loss_year is not None and loss_year <= end_year):
                info.update(kind="area_loss", event_year=loss_year)
            else:
                info.update(kind="ending", event_year=end_year)
            yield t0, "event", info
        elif t0 + H <= y1 and cov[t0 + H - y0]:
            info.update(kind=None, event_year=None)
            yield t0, "control", info
        elif y1 <= t0:
            yield t0, "ineligible:ended_at_or_before_origin", None
        elif y1 < t0 + H:
            yield t0, "ineligible:ended_in_horizon_not_before_cutoff", None
        else:
            yield t0, "ineligible:gap_at_horizon_end", None


def build_windows(series: dict, W: int, H: int, data_end: int):
    n_obs = W // STEP
    elig = defaultdict(list)
    reasons = Counter()
    for name in sorted(series):
        for t0, status, info in windows_for(name, series[name], W, H, data_end, n_obs):
            reasons[status if status.startswith("ineligible") else "eligible"] += 1
            if info is not None:
                elig[name].append(dict(name=name, t0=t0, transitioned=status == "event", **info))
    return dict(elig), reasons, n_obs


# --- step 4: split and anonymise --------------------------------------------------

def split_and_anonymise(elig: dict, W: int, seed: int):
    rng = np.random.default_rng(seed)
    names = sorted(elig)
    order = [names[i] for i in rng.permutation(len(names))]
    n_dev = len(order) // 2
    dev_names, test_names = order[:n_dev], order[n_dev:]
    dev = [w for n in dev_names for w in sorted(elig[n], key=lambda w: w["t0"])]
    test = []
    for n in test_names:                        # in shuffled order
        ws = sorted(elig[n], key=lambda w: w["t0"])
        test.append(ws[int(rng.integers(len(ws)))])
    test = [test[i] for i in rng.permutation(len(test))]
    dev = [dev[i] for i in rng.permutation(len(dev))]
    for w in test + dev:
        w["t"] = (w["years"] - (w["t0"] - W)) * T_ORIGIN / W
        w["x"] = w["vals"] / np.median(w["vals"])
    for i, w in enumerate(test):
        w["wid"], w["split"] = f"{NAME}-{i:04d}", "test"
    groups = {}
    for i, w in enumerate(dev):
        w["wid"], w["split"] = f"{NAME}-dev-{i:04d}", "dev"
        w["group"] = groups.setdefault(w["name"], f"g{len(groups):04d}")
    return dict(test=test, dev=dev, dev_names=dev_names, test_names=test_names,
                n_polities_eligible=len(names))


def build(rows_polity: list[dict], seed: int, data_end: int, W: int, H: int):
    series, ov = build_series(rows_polity)
    elig, reasons, n_obs = build_windows(series, W, H, data_end)
    sp = split_and_anonymise(elig, W, seed)
    return dict(series=series, overlap=ov, elig=elig, reasons=reasons, n_obs=n_obs,
                W=W, H=H, **sp)


# --- validation --------------------------------------------------------------------

def validate(res: dict, truth: list[dict], test_npz: Path | None, dev_npz: Path | None):
    W, n_obs = res["W"], res["n_obs"]
    expected_t = np.arange(n_obs) * STEP * T_ORIGIN / W
    for w in res["test"] + res["dev"]:
        assert w["x"].shape == (n_obs,) and np.all(np.isfinite(w["x"])) and np.all(w["x"] > 0)
        assert np.allclose(w["t"], expected_t) and w["t"][0] == 0 and w["t"][-1] < T_ORIGIN
    tids = sorted(w["wid"] for w in res["test"])
    assert tids == [f"{NAME}-{i:04d}" for i in range(len(tids))]
    assert [r["world_id"] for r in truth] == tids
    assert len({w["name"] for w in res["test"]}) == len(res["test"])
    assert not set(res["dev_names"]) & set(res["test_names"])
    for npz, ws in ((test_npz, res["test"]), (dev_npz, res["dev"])):
        if npz is None:
            continue
        z = np.load(npz)
        assert sorted(z.files) == sorted([w["wid"] for w in ws] + [f"t_{w['wid']}" for w in ws])
        for w in ws:
            assert np.array_equal(z[w["wid"]], w["x"]) and np.array_equal(z[f"t_{w['wid']}"], w["t"])
            assert z[w["wid"]].dtype == np.float64


def name_leak_check(names: list[str], files: list[Path]) -> dict:
    """Search every open output for every polity name (case-sensitive, whole word).

    Text files are searched as text. For .npz files, the member names (the only
    strings they hold) are searched, and every array is checked to be numeric.
    """
    pats = [re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])") for n in names]
    hits = []
    for f in files:
        if f.suffix == ".npz":
            z = np.load(f)
            assert all(z[k].dtype.kind == "f" for k in z.files), f
            text = "\n".join(z.files)
        else:
            text = f.read_text()
        for n, p in zip(names, pats):
            if p.search(text):
                hits.append((str(f.relative_to(ROOT)), n))
    return dict(n_names=len(names), n_files=len(files), hits=hits)


# --- logs --------------------------------------------------------------------------

AGENT_COMMANDS = r"""
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
"""

JUDGEMENTS = r"""
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
"""


def public_log(info, pmeta, stats, res, fallback_used, outputs, leak, seal_event=None) -> str:
    d, ov = res["dev"], res["overlap"]["stats"]
    dk = Counter(w["kind"] for w in d if w["transitioned"])
    reasons = res["reasons"]
    L = [
        "# Data preparation log: `real_v1` (public)",
        "",
        "Written by `phase2/prepare_cliopatria.py`, run by the data-preparation subagent.",
        "Contains no polity names, no polity-specific years and nothing about test outcomes.",
        "Identities and test outcomes are only in the sealed key and private log under",
        "`inflection/data/sealed/` (git-ignored).",
        "",
        "## Dataset",
        "",
        f"- Name: Cliopatria (Seshat Global History Databank), licence CC-BY 4.0",
        f"- Repository: `{REPO}`",
        f"- Release tag: `{info['release_tag']}` (\"{info.get('release_name')}\", published {info.get('release_published')})",
        f"- Commit sha: `{info['commit_sha']}`",
        f"- How obtained: {info['how']}",
        f"- URL: {info['url']}",
        f"- Download date (UTC): {info['download_date']}",
        f"- `{ASSET}` sha256: `{info['sha256']}` ({info['size_bytes']} bytes)",
        f"- Zip member used: `{pmeta['member']}` (FeatureCollection name `{pmeta.get('collection_name')}`)",
        "",
        "## Contents",
        "",
        f"- Property names: {', '.join('`' + k + '`' for k in stats['property_names'])}",
        f"- Total feature rows: {stats['n_rows']}",
        f"- Rows by Type: {dict(stats['types'])}",
        f"- POLITY rows kept: {stats['n_polity_rows']}; distinct polity names: {stats['n_polities']}",
        f"- Year range over all POLITY rows: {stats['min_year']} to {stats['max_year']} "
        f"(dataset end used: {stats['max_year']})",
        f"- POLITY rows with Area <= 0 or non-finite: {stats['n_bad_area']}; rows with FromYear > ToYear: {stats['n_bad_span']}",
        "",
        "## Overlapping rows (same polity, same year covered by two rows)",
        "",
        f"- Polities with any overlap: {ov['polities_with_overlap']} of {stats['n_polities']}",
        f"- Overlapping row pairs: {ov['overlapping_row_pairs']} (of which with equal FromYear: {ov['overlapping_row_pairs_same_fromyear']})",
        f"- Polity-years covered by two or more rows: {ov['polity_years_covered_twice_or_more']} of {ov['polity_years_covered']} covered polity-years",
        f"- Polity-years inside a polity's first..last year but covered by no row (gaps): {ov['polity_years_in_span_uncovered']}",
        "",
        "## Windows",
        "",
        f"- Fallback (W=150, H=75) used: **{'yes' if fallback_used else 'no'}**",
        f"- W = {res['W']}, H = {res['H']}, step = {STEP} years, {res['n_obs']} observations per record",
        f"- Candidate origins (multiples of 50 with the record window inside the polity's span): {sum(reasons.values())}",
    ]
    for k in sorted(reasons):
        L.append(f"  - {k}: {reasons[k]}")
    L += [
        f"- Polities with at least one eligible window: {res['n_polities_eligible']}",
        "",
        "(Class balance over all eligible windows is not reported, since it would bound the test balance.)",
        "",
        "## Split",
        "",
        f"- Dev: {len(res['dev_names'])} polities, {len(d)} windows (all eligible windows of those polities)",
        f"- Test: {len(res['test_names'])} polities, {len(res['test'])} windows (one per polity)",
        f"- Dev events: {sum(w['transitioned'] for w in d)}; dev controls: {sum(not w['transitioned'] for w in d)}",
        f"- Dev events by kind: area_loss {dk.get('area_loss', 0)}, ending {dk.get('ending', 0)}",
        "",
        "## Judgement calls",
        JUDGEMENTS,
        "## Commands",
        AGENT_COMMANDS,
        "## Validation",
        "",
        "- Every test id is in `series.npz` (values and `t_` times) and in the sealed truth, and ids are contiguous.",
        f"- Every record, test and dev, has exactly {res['n_obs']} finite, positive values, and times equal the formula.",
        "- Each test polity contributes exactly one window; no polity is in both splits.",
        f"- Name-leak check: {leak['n_names']} polity names searched in {leak['n_files']} open files; "
        f"hits: {len(leak['hits'])}. **{'PASSED' if not leak['hits'] else 'FAILED'}**",
        "",
        "## Outputs (sha256)",
        "",
    ]
    for p, h in outputs.items():
        L.append(f"- `{p}`: `{h}`")
    L += ["- `inflection/data/sealed/real_v1/truth.json`, `inflection/data/sealed/real_v1_key.json`,",
          "  `inflection/data/sealed/real_v1_private_log.md`: sealed, git-ignored; the truth hash is in the ledger.",
          ""]
    if seal_event is not None:
        L += ["## Ledger event appended by `seal_external_pool` (called once)", "",
              "```json", json.dumps(seal_event, indent=2, sort_keys=True), "```", ""]
    return "\n".join(L)


def private_log(info, stats, res, fallback_used, leak, prelim=None) -> str:
    t, d = res["test"], res["dev"]
    tk = Counter(w["kind"] for w in t if w["transitioned"])
    L = ["# Private data-preparation log: `real_v1` (SEALED, contains identities and test outcomes)", "",
         f"Dataset sha256 `{info['sha256']}`, commit `{info['commit_sha']}`.", "",
         f"Fallback used: {fallback_used}."]
    if prelim is not None:
        L += [f"Main-design (W=100) test size was {prelim} (< {MIN_TEST}), hence fallback."]
    L += ["", "## Test class balance",
          f"- test windows {len(t)}, events {sum(w['transitioned'] for w in t)}, "
          f"controls {sum(not w['transitioned'] for w in t)}, base rate "
          f"{np.mean([w['transitioned'] for w in t]):.3f}",
          f"- test events by kind: {dict(tk)}", "",
          "## Overlaps by polity (name: pairs, years, same-FromYear pairs)"]
    for n, o in sorted(res["overlap"]["overlap_detail"].items()):
        L.append(f"- {n}: {o['pairs']}, {o['years']}, {o['same_from']}")
    L += ["", "## Test windows", "| id | polity | t0 | kind | event_year |", "|---|---|---|---|---|"]
    for w in sorted(t, key=lambda w: w["wid"]):
        L.append(f"| {w['wid']} | {w['name']} | {w['t0']} | {w['kind']} | {w['event_year']} |")
    L += ["", "## Dev polities (group id: name, n windows)"]
    g = defaultdict(list)
    for w in d:
        g[(w["group"], w["name"])].append(w)
    for (gid, n), ws in sorted(g.items()):
        L.append(f"- {gid}: {n}, {len(ws)} windows, events {sum(x['transitioned'] for x in ws)}")
    L += ["", f"Name-leak check hits: {leak['hits']}", ""]
    return "\n".join(L)


# --- main ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seal", action="store_true", help="write outputs and seal (once)")
    args = ap.parse_args()

    if _events(NAME, "pool_built", LEDGER):
        sys.exit(f"{NAME} is already sealed in the ledger; refusing to rebuild outputs.")

    info = download()
    rows, pmeta = read_properties(RAW / ASSET)
    polity = [r for r in rows if r.get("Type") == "POLITY"]
    stats = dict(
        property_names=sorted({k for r in rows for k in r}),
        n_rows=len(rows), types=Counter(r.get("Type") for r in rows),
        n_polity_rows=len(polity), n_polities=len({r["Name"] for r in polity}),
        min_year=min(r["FromYear"] for r in polity), max_year=max(r["ToYear"] for r in polity),
        n_bad_area=sum(1 for r in polity if not (np.isfinite(r["Area"]) and r["Area"] > 0)),
        n_bad_span=sum(1 for r in polity if r["FromYear"] > r["ToYear"]),
    )
    assert stats["n_bad_span"] == 0
    seed = split_seed(NAME)
    data_end = stats["max_year"]

    res = build(polity, seed, data_end, **MAIN)
    fallback_used, prelim = False, None
    if len(res["test"]) < MIN_TEST:
        fallback_used, prelim = True, len(res["test"])
        res = build(polity, seed, data_end, **FALLBACK)
    assert len(res["test"]) >= 1

    truth = sorted(({"world_id": w["wid"], "transitioned": bool(w["transitioned"]),
                     "event_kind": w["kind"]} for w in res["test"]), key=lambda r: r["world_id"])
    names = sorted({r["Name"] for r in polity})

    if not args.seal:
        validate(res, truth, None, None)
        print(json.dumps(dict(
            dataset=info["release_tag"], sha256=info["sha256"], fallback_used=fallback_used,
            W=res["W"], H=res["H"], n_polities_eligible=res["n_polities_eligible"],
            dev_polities=len(res["dev_names"]), test_polities=len(res["test_names"]),
            dev_windows=len(res["dev"]), test_windows=len(res["test"]),
            reasons=dict(res["reasons"])), indent=2))
        print("dry run: validation passed; nothing written. Use --seal to write and seal.")
        return

    # ---- write open outputs
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    DEV_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_LOG.parent.mkdir(parents=True, exist_ok=True)
    test_npz, dev_npz = TEST_DIR / "series.npz", DEV_DIR / "series.npz"
    for path, ws in ((test_npz, res["test"]), (dev_npz, res["dev"])):
        arrs = {}
        for w in sorted(ws, key=lambda w: w["wid"]):
            arrs[w["wid"]] = w["x"].astype(np.float64)
            arrs[f"t_{w['wid']}"] = w["t"].astype(np.float64)
        np.savez(path, **arrs)
    tids = sorted(w["wid"] for w in res["test"])
    manifest = dict(
        world_ids=tids, origins={wid: T_ORIGIN for wid in tids}, T=T_TOTAL,
        W=res["W"], H=res["H"], step_years=STEP, test_set=NAME,
        source=dict(dataset="Cliopatria (Seshat Global History Databank)",
                    version=info["release_tag"], commit=info["commit_sha"],
                    url=info["url"], licence="CC-BY 4.0"))
    (TEST_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    labels = {w["wid"]: {"transitioned": bool(w["transitioned"]), "event_kind": w["kind"],
                         "group": w["group"]}
              for w in sorted(res["dev"], key=lambda w: w["wid"])}
    (DEV_DIR / "labels.json").write_text(json.dumps(labels, indent=2, sort_keys=True) + "\n")

    # ---- sealed key
    SEALED.mkdir(parents=True, exist_ok=True)
    key = {w["wid"]: dict(name=w["name"], t0=int(w["t0"]),
                          event_year=None if w["event_year"] is None else int(w["event_year"]),
                          event_kind=w["kind"], split=w["split"])
           for w in sorted(res["test"] + res["dev"], key=lambda w: w["wid"])}
    KEY.write_text(json.dumps(key, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

    # ---- validate and name-leak check (logs included after writing)
    validate(res, truth, test_npz, dev_npz)
    open_files = [test_npz, TEST_DIR / "manifest.json", dev_npz, DEV_DIR / "labels.json",
                  Path(__file__).resolve()]
    outputs = {str(p.relative_to(ROOT)): sha256_file(p) for p in open_files[:4]}
    leak = name_leak_check(names, open_files)
    PUBLIC_LOG.write_text(public_log(info, pmeta, stats, res, fallback_used, outputs, leak))
    leak = name_leak_check(names, open_files + [PUBLIC_LOG])
    PUBLIC_LOG.write_text(public_log(info, pmeta, stats, res, fallback_used, outputs, leak))
    PRIVATE_LOG.write_text(private_log(info, stats, res, fallback_used, leak, prelim))
    if leak["hits"]:
        sys.exit(f"name-leak check FAILED: {len(leak['hits'])} hits; see private log. Not sealed.")

    # ---- seal, exactly once, after everything else is final
    meta = dict(dataset="Cliopatria", dataset_version=info["release_tag"],
                dataset_commit=info["commit_sha"], dataset_sha256=info["sha256"],
                W=res["W"], H=res["H"], n_obs=res["n_obs"],
                n_test_windows=len(res["test"]), n_dev_windows=len(res["dev"]),
                n_test_polities=len(res["test_names"]), n_dev_polities=len(res["dev_names"]),
                fallback_used=fallback_used)
    event = seal_external_pool(NAME, test_npz, truth, meta)
    assert event["record_sha256"]["real"] == outputs[str(test_npz.relative_to(ROOT))]

    PUBLIC_LOG.write_text(public_log(info, pmeta, stats, res, fallback_used, outputs, leak, event))
    leak2 = name_leak_check(names, open_files + [PUBLIC_LOG])
    assert not leak2["hits"], leak2
    with PRIVATE_LOG.open("a") as f:
        f.write(f"\n## Seal event\n\n```json\n{json.dumps(event, indent=2, sort_keys=True)}\n```\n"
                f"\nFinal name-leak check on the public log after appending the seal event: {leak2['hits']}\n")
    print(json.dumps(event, indent=2, sort_keys=True))
    print("sealed. public log:", PUBLIC_LOG.relative_to(ROOT))


if __name__ == "__main__":
    main()
