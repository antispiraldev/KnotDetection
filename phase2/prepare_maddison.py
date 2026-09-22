"""Build the blinded real-data test set `real_v2` from the Maddison Project Database.

Implements phase2/PREREGISTRATION_v2.md, steps 2-6 of the data-preparation brief:
download, series and windows, split and anonymisation, outputs, logs, sealing.

Usage (from the repository root, PYTHONPATH set to it):

    python phase2/prepare_maddison.py            # dry run: build + validate in memory
    python phase2/prepare_maddison.py --seal     # write every output, validate, seal once

The dry run prints only public, outcome-free facts. `--seal` refuses to run if the
ledger already holds a `pool_built` event for `real_v2`, so the sealed truth and the
open records can never drift apart. No country names, codes or years are hard-coded;
the only years in this file are the ones the pre-registration fixes (the 1950 era cut).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inflection.eval.blind import (  # noqa: E402
    LEDGER, SEALED, _events, seal_external_pool, split_seed,
)

NAME = "real_v2"
URL = "https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx"
ASSET = "mpd2020.xlsx"
DATASET = "Maddison Project Database 2020 (Groningen Growth and Development Centre)"
DATASET_VERSION = "2020"
LICENCE = "CC-BY 4.0"

RAW = ROOT / "phase2" / "raw"
TEST_DIR = ROOT / "inflection" / "data" / NAME
DEV_DIR = ROOT / "phase2" / "data" / "dev_v2"
PUBLIC_LOG = ROOT / "phase2" / "logs" / "data_prep_v2.md"
KEY = SEALED / f"{NAME}_key.json"
PRIVATE_LOG = SEALED / f"{NAME}_private_log.md"

STEP = 1                 # the record is annual
ORIGIN_STEP = 5          # forecast origins are multiples of this
MAIN = dict(W=30, H=15)
FALLBACK = dict(W=20, H=10)
MIN_TEST = 150           # fallback trigger: test half smaller than this
EVENT_FRAC = 0.75        # event: a horizon year below this x the record maximum
NOT_COLLAPSING_FRAC = 0.75   # eligibility: last recorded value at least this x the maximum
SEVERE_FRAC = 0.60       # secondary: horizon minimum below this x the record maximum
ERA_CUT = 1950           # era is "pre1950" if t0 <= ERA_CUT else "post1950"
T_ORIGIN = 90.0          # simulator's origin on its time scale
T_TOTAL = 300.0

# Column roles expected by the pre-registration, and the tokens used to find each one
# if the sheet names it differently. Matching is on the lower-cased, stripped header.
COLUMN_ROLES = {
    "countrycode": ("countrycode", "country code", "iso", "code"),
    "country": ("country", "countryname", "country name", "name"),
    "year": ("year",),
    "gdppc": ("gdppc", "gdp pc", "gdp per capita", "rgdpnapc", "cgdppc"),
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --- step 2: download -------------------------------------------------------------

def download() -> dict:
    """Fetch the workbook (once) and return its provenance."""
    RAW.mkdir(parents=True, exist_ok=True)
    info_path = RAW / "mpd2020_download_info.json"
    path = RAW / ASSET
    if info_path.exists() and path.exists():
        info = json.loads(info_path.read_text())
        if sha256_file(path) == info["sha256"]:
            info["reused_existing_download"] = True
            return info
    req = urllib.request.Request(URL, headers={"User-Agent": "curl/8 (phase2 data prep)"})
    with urllib.request.urlopen(req) as r:
        headers = {k: r.headers.get(k) for k in
                   ("Last-Modified", "ETag", "Content-Length", "Content-Type")}
        body = r.read()
        final_url = r.geturl()
    path.write_bytes(body)
    info = dict(url=URL, final_url=final_url, http_headers=headers,
                download_date=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                sha256=sha256_file(path), size_bytes=path.stat().st_size)
    info_path.write_text(json.dumps(info, indent=2))
    info["reused_existing_download"] = False
    return info


def _role_of(header: str) -> str | None:
    h = str(header).strip().lower()
    for role, tokens in COLUMN_ROLES.items():
        if h in tokens:
            return role
    for role, tokens in COLUMN_ROLES.items():
        if any(tok in h for tok in tokens):
            return role
    return None


def read_panel(path: Path) -> tuple[pd.DataFrame, dict]:
    """Find and read the country-year panel sheet; return it with its provenance.

    The panel sheet is identified structurally, not by name: it is the sheet whose
    header row carries a country column, a year column and a GDP-per-capita column
    (a long, one-row-per-country-year table). The wide year-by-country sheets do not,
    so the choice needs no hard-coded sheet name.
    """
    xl = pd.ExcelFile(path, engine="openpyxl")
    candidates, seen = [], {}
    for sheet in xl.sheet_names:
        head = xl.parse(sheet, nrows=0)
        roles = {}
        for col in head.columns:
            role = _role_of(col)
            if role is not None and role not in roles:
                roles[role] = col
        seen[sheet] = dict(n_columns=len(head.columns), roles=sorted(roles))
        if {"country", "year", "gdppc"} <= set(roles) and len(head.columns) <= 10:
            candidates.append((sheet, roles))
    if len(candidates) != 1:
        raise SystemExit(f"could not identify a unique country-year panel sheet: {seen}")
    sheet, roles = candidates[0]
    df = xl.parse(sheet)
    meta = dict(sheet=sheet, sheet_names=list(xl.sheet_names), sheets_seen=seen,
                columns=[str(c) for c in df.columns],
                column_roles={r: str(c) for r, c in roles.items()},
                renamed=[f"{c} -> {r}" for r, c in roles.items() if str(c) != r])
    df = df[[roles[r] for r in ("countrycode", "country", "year", "gdppc")
             if r in roles]].copy()
    df.columns = [r for r in ("countrycode", "country", "year", "gdppc") if r in roles]
    if "countrycode" not in df.columns:            # fall back on the name as the key
        df["countrycode"] = df["country"]
        meta["renamed"].append("no country-code column; the country name is the key")
    return df, meta


# --- step 3: series and windows ---------------------------------------------------

def build_series(df: pd.DataFrame) -> tuple[dict, dict]:
    """One annual gdppc series per country, NaN where the year has no usable value.

    A year is *recorded* when the panel gives it a finite, strictly positive gdppc.
    Non-positive values are treated as missing rather than as observations: the
    pre-registration already refuses to build a record on them, a non-positive real
    income is not a measurement, and counting one as a fall would manufacture an
    event out of a missing-data code. The rule is applied uniformly, before any
    window or outcome is looked at, and the number of cells it touches is logged.
    """
    df = df.dropna(subset=["countrycode", "country", "year"]).copy()
    df["year"] = df["year"].astype(int)
    stats = Counter()
    stats["rows"] = len(df)
    val = pd.to_numeric(df["gdppc"], errors="coerce")
    stats["cells_missing_gdppc"] = int(val.isna().sum())
    stats["cells_nonpositive_gdppc"] = int((val <= 0).sum())
    df["gdppc"] = val.where(val > 0)
    stats["cells_recorded"] = int(df["gdppc"].notna().sum())
    stats["duplicate_country_years"] = int(df.duplicated(["countrycode", "year"]).sum())

    series = {}
    for code, g in df.groupby("countrycode", sort=True):
        g = g[g["gdppc"].notna()]
        if g.empty:
            stats["countries_with_no_recorded_year"] += 1
            continue
        y0, y1 = int(g["year"].min()), int(g["year"].max())
        v = np.full(y1 - y0 + 1, np.nan)
        v[g["year"].to_numpy(int) - y0] = g["gdppc"].to_numpy(float)
        names = sorted(set(g["country"]))
        if len(names) > 1:
            stats["countries_with_several_names"] += 1
        series[code] = dict(code=code, name=names[0], y0=y0, y1=y1, v=v)
        stats["country_years_in_span_unrecorded"] += int(np.isnan(v).sum())
        stats["country_years_recorded"] += int(np.isfinite(v).sum())
    stats["countries"] = len(series)
    stats["first_year"] = min(s["y0"] for s in series.values())
    stats["last_year"] = max(s["y1"] for s in series.values())
    return series, dict(stats=stats)


def windows_for(s: dict, W: int, H: int):
    """Yield (t0, status, info) for every candidate origin of one country.

    A candidate origin is a multiple of ORIGIN_STEP whose record window [t0-W, t0)
    lies inside the country's first..last recorded year. Candidates are then checked
    in a fixed order and the first failed check is the reason reported, so no
    ineligibility ever depends on the outcome except the one the pre-registration
    makes outcome-aware by design (condition 3, "the outcome is observable").
    """
    y0, y1, v = s["y0"], s["y1"], s["v"]
    cov = np.isfinite(v)
    first = -(-(y0 + W) // ORIGIN_STEP) * ORIGIN_STEP
    last = ((y1 + 1) // ORIGIN_STEP) * ORIGIN_STEP
    for t0 in range(first, last + 1, ORIGIN_STEP):
        rec = slice(t0 - W - y0, t0 - y0)
        if not cov[rec].all():
            yield t0, "ineligible:record_gap", None
            continue
        vals = v[rec]
        if not (vals > 0).all():                 # kept as a guard; see build_series
            yield t0, "ineligible:nonpositive_gdppc", None
            continue
        peak = float(vals.max())
        if vals[-1] < NOT_COLLAPSING_FRAC * peak:
            yield t0, "ineligible:already_in_collapse", None
            continue
        hy = np.arange(t0 + 1, t0 + H + 1)
        inside = (hy >= y0) & (hy <= y1)
        hv = np.full(H, np.nan)
        hv[inside] = v[hy[inside] - y0]
        hcov = np.isfinite(hv)
        below = np.flatnonzero(hcov & (hv < EVENT_FRAC * peak))
        event_year = int(hy[below[0]]) if below.size else None
        if event_year is None and not hcov.all():
            yield t0, "ineligible:outcome_not_observable", None
            continue
        hmin = float(hv[hcov].min())
        info = dict(years=np.arange(t0 - W, t0), vals=vals, peak=peak,
                    event_year=event_year, severe=bool(hmin < SEVERE_FRAC * peak),
                    horizon_years_recorded=int(hcov.sum()),
                    era="pre1950" if t0 <= ERA_CUT else "post1950")
        yield t0, ("event" if event_year is not None else "control"), info


REASONS = ("eligible", "ineligible:record_gap", "ineligible:nonpositive_gdppc",
           "ineligible:already_in_collapse", "ineligible:outcome_not_observable")


def build_windows(series: dict, W: int, H: int):
    n_obs = W // STEP
    elig = defaultdict(list)
    reasons = Counter({k: 0 for k in REASONS})
    for code in sorted(series):
        s = series[code]
        for t0, status, info in windows_for(s, W, H):
            reasons[status if status.startswith("ineligible") else "eligible"] += 1
            if info is not None:
                elig[code].append(dict(code=code, name=s["name"], t0=t0,
                                       transitioned=status == "event", **info))
    return dict(elig), reasons, n_obs


# --- step 4: split and anonymise --------------------------------------------------

def split_and_anonymise(elig: dict, W: int, seed: int):
    """Split countries 50/50, keep every eligible window of both halves, anonymise.

    Unlike `real_v1`, the test half keeps all of its windows (pre-registration:
    later data does not reveal an earlier outcome here), so intervals are
    bootstrapped over countries and both halves carry an anonymised group id.
    """
    rng = np.random.default_rng(seed)
    codes = sorted(elig)
    order = [codes[i] for i in rng.permutation(len(codes))]
    n_dev = len(order) // 2
    dev_codes, test_codes = order[:n_dev], order[n_dev:]
    test = [w for c in test_codes for w in sorted(elig[c], key=lambda w: w["t0"])]
    dev = [w for c in dev_codes for w in sorted(elig[c], key=lambda w: w["t0"])]
    test = [test[i] for i in rng.permutation(len(test))]
    dev = [dev[i] for i in rng.permutation(len(dev))]
    for w in test + dev:
        w["t"] = (w["years"] - (w["t0"] - W)) * T_ORIGIN / W
        w["x"] = w["vals"] / np.median(w["vals"])
    for i, w in enumerate(test):
        w["wid"], w["split"] = f"{NAME}-{i:04d}", "test"
    for i, w in enumerate(dev):
        w["wid"], w["split"] = f"{NAME}-dev-{i:04d}", "dev"
    # One counter for both halves, so a group id is never reused across splits.
    # Ids follow first appearance in the shuffled window order, and therefore
    # carry no information about the country beyond what the shuffle gives.
    groups: dict[str, str] = {}
    for w in test + dev:
        w["group"] = groups.setdefault(w["code"], f"g{len(groups):04d}")
    return dict(test=test, dev=dev, dev_codes=dev_codes, test_codes=test_codes,
                groups=groups, n_countries_eligible=len(codes))


def build(series: dict, seed: int, W: int, H: int):
    elig, reasons, n_obs = build_windows(series, W, H)
    sp = split_and_anonymise(elig, W, seed)
    return dict(elig=elig, reasons=reasons, n_obs=n_obs, W=W, H=H, **sp)


# --- validation --------------------------------------------------------------------

def validate(res: dict, truth: list[dict], test_npz: Path | None, dev_npz: Path | None):
    W, n_obs = res["W"], res["n_obs"]
    expected_t = np.arange(n_obs) * STEP * T_ORIGIN / W
    for w in res["test"] + res["dev"]:
        assert w["x"].shape == (n_obs,) and np.all(np.isfinite(w["x"])) and np.all(w["x"] > 0)
        assert np.allclose(w["t"], expected_t) and w["t"][0] == 0 and w["t"][-1] < T_ORIGIN
        assert len(w["years"]) == n_obs and w["years"][-1] == w["t0"] - 1
    tids = sorted(w["wid"] for w in res["test"])
    assert tids == [f"{NAME}-{i:04d}" for i in range(len(tids))]
    assert [r["world_id"] for r in truth] == tids
    dids = sorted(w["wid"] for w in res["dev"])
    assert dids == [f"{NAME}-dev-{i:04d}" for i in range(len(dids))]
    assert not set(res["dev_codes"]) & set(res["test_codes"])
    assert set(res["dev_codes"]) | set(res["test_codes"]) == set(res["elig"])
    # groups: a bijection with countries, and never shared across splits
    by_group = defaultdict(set)
    for w in res["test"] + res["dev"]:
        by_group[w["group"]].add((w["code"], w["split"]))
    assert all(len(v) == 1 for v in by_group.values())
    assert len(by_group) == len(res["elig"])
    assert len({w["group"] for w in res["test"]}) == len(res["test_codes"])
    assert len({w["group"] for w in res["dev"]}) == len(res["dev_codes"])
    assert not ({w["group"] for w in res["test"]} & {w["group"] for w in res["dev"]})
    for npz, ws in ((test_npz, res["test"]), (dev_npz, res["dev"])):
        if npz is None:
            continue
        z = np.load(npz)
        assert sorted(z.files) == sorted([w["wid"] for w in ws] + [f"t_{w['wid']}" for w in ws])
        for w in ws:
            assert np.array_equal(z[w["wid"]], w["x"]) and np.array_equal(z[f"t_{w['wid']}"], w["t"])
            assert z[w["wid"]].dtype == np.float64


HEX_RUN = re.compile(r"[0-9a-fA-F]+")


def name_leak_check(names: list[str], codes: list[str], files: list[Path]) -> dict:
    """Search every open output for every country name and country code.

    Names are searched case-sensitively, whole-word (no letter either side). Codes
    are short and uppercase, so they are searched case-sensitively with a word
    boundary on both sides (no letter or digit either side), which keeps them from
    matching inside lower-case hex digests. Any hit that nevertheless falls inside a
    run of 32 or more hex characters is reported as such rather than dropped.
    For .npz files the member names (the only strings they hold) are searched and
    every array is checked to be floating point.
    """
    pats = [("name", n, re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])"))
            for n in names]
    pats += [("code", c, re.compile(r"(?<![A-Za-z0-9])" + re.escape(c) + r"(?![A-Za-z0-9])"))
             for c in codes]
    hits, in_hash = [], []
    for f in files:
        if f.suffix == ".npz":
            z = np.load(f)
            assert all(z[k].dtype.kind == "f" for k in z.files), f
            text = "\n".join(z.files)
        else:
            text = f.read_text()
        runs = [(m.start(), m.end()) for m in HEX_RUN.finditer(text) if m.end() - m.start() >= 32]
        for kind, s, p in pats:
            for m in p.finditer(text):
                rec = (str(f.relative_to(ROOT)), kind, s)
                if any(a <= m.start() and m.end() <= b for a, b in runs):
                    in_hash.append(rec)
                else:
                    hits.append(rec)
    return dict(n_names=len(names), n_codes=len(codes), n_files=len(files),
                hits=hits, hits_inside_hashes=in_hash)


# --- logs --------------------------------------------------------------------------

AGENT_COMMANDS = r"""
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
"""

JUDGEMENTS = r"""
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
"""


def public_log(info, pmeta, stats, res, fallback_used, outputs, leak, seal_event=None) -> str:
    d = res["dev"]
    reasons = res["reasons"]
    era = Counter(w["era"] for w in d)
    dev_per_country = Counter(w["code"] for w in d)
    L = [
        "# Data preparation log: `real_v2` (public)",
        "",
        "Written by `phase2/prepare_maddison.py`, run by the data-preparation subagent.",
        "Contains no country names or codes, no country-specific years and nothing about",
        "test outcomes. Identities and test outcomes are only in the sealed key and private",
        "log under `inflection/data/sealed/` (git-ignored).",
        "",
        "## Dataset",
        "",
        f"- Name: {DATASET}, licence {LICENCE}",
        f"- Version: {DATASET_VERSION} (file `{ASSET}`)",
        f"- URL: {info['url']}",
        f"- URL after redirects: {info.get('final_url')}",
        f"- HTTP headers at download: {json.dumps(info.get('http_headers', {}), sort_keys=True)}",
        f"- Download date (UTC): {info['download_date']}",
        f"- `{ASSET}` sha256: `{info['sha256']}` ({info['size_bytes']} bytes)",
        "- The URL given in the brief was checked first and answered 200 with an xlsx",
        "  body, so no alternative GGDC location was needed.",
        "",
        "## Sheet and columns",
        "",
        f"- Sheets in the workbook: {', '.join('`' + s + '`' for s in pmeta['sheet_names'])}",
        f"- Sheet used: `{pmeta['sheet']}` -- the country-year panel (one row per country "
        "and year). It is the only sheet whose header carries a country column, a year",
        "  column and a GDP-per-capita column in a narrow table; the other data sheets are",
        "  wide year-by-country tables of the same numbers, or regional aggregates.",
        f"- Header of the sheet used: {', '.join('`' + c + '`' for c in pmeta['columns'])}",
        f"- Columns taken, by role: {json.dumps(pmeta['column_roles'], sort_keys=True)}",
        f"- Renamings needed: {pmeta['renamed'] or 'none'}",
        "- Only `gdppc` is used, by country and year; `pop` is not read.",
        "",
        "## Contents",
        "",
        f"- Panel rows: {stats['rows']}",
        f"- Countries (distinct country codes with at least one recorded year): {stats['countries']}",
        f"- Duplicate (country, year) rows: {stats['duplicate_country_years']}",
        f"- Panel year range: {stats['first_year']} to {stats['last_year']}",
        f"- Cells with a blank `gdppc`: {stats['cells_missing_gdppc']}",
        f"- Cells with a non-positive `gdppc` (treated as missing, see judgement 4): "
        f"{stats['cells_nonpositive_gdppc']}",
        f"- Recorded country-years (finite, positive `gdppc`): {stats['country_years_recorded']}",
        f"- Country-years inside a country's first..last recorded year with no value (gaps): "
        f"{stats['country_years_in_span_unrecorded']}",
        f"- Countries whose code maps to more than one name: {stats.get('countries_with_several_names', 0)}",
        "",
        "## Windows",
        "",
        f"- Fallback (W=20, H=10) used: **{'yes' if fallback_used else 'no'}** "
        f"(trigger: fewer than {MIN_TEST} test windows)",
        f"- W = {res['W']} years of record, H = {res['H']} years of horizon, step = {STEP} year, "
        f"{res['n_obs']} observations per record",
        f"- Event: a recorded horizon year below {EVENT_FRAC} x the record maximum",
        f"- Candidate origins (multiples of {ORIGIN_STEP} with the record window inside the "
        f"country's recorded span): {sum(reasons.values())}",
    ]
    for k in sorted(reasons):
        L.append(f"  - {k}: {reasons[k]}")
    L += [
        f"- Countries with at least one eligible window: {res['n_countries_eligible']}",
        "",
        "(Class balance over all eligible windows is not reported, since it would bound the",
        "test balance. Neither is the balance of the pre-1950 and post-1950 halves.)",
        "",
        "## Split",
        "",
        "Countries, not windows, are split 50/50 with the seed committed for `real_v2`",
        "before the download. **Both halves keep every eligible window of their countries**",
        "(pre-registration: unlike `real_v1`, a later window's existence does not reveal an",
        "earlier outcome here), so test intervals are bootstrapped over countries and both",
        "halves carry an anonymised group id.",
        "",
        f"- Dev: {len(res['dev_codes'])} countries, {len(d)} windows",
        f"- Test: {len(res['test_codes'])} countries, {len(res['test'])} windows",
        f"- Dev events: {sum(w['transitioned'] for w in d)}; dev controls: "
        f"{sum(not w['transitioned'] for w in d)}",
        f"- Dev windows by era: pre1950 {era.get('pre1950', 0)}, post1950 {era.get('post1950', 0)}",
        f"- Windows per country, dev half: min {min(dev_per_country.values())}, "
        f"median {int(np.median(list(dev_per_country.values())))}, "
        f"max {max(dev_per_country.values())}",
        "",
        "## Judgement calls",
        JUDGEMENTS,
        "## Commands",
        AGENT_COMMANDS,
        "## Validation",
        "",
        "- Every test id is in `series.npz` (values and `t_` times) and in the sealed truth, "
        "and test and dev ids are each contiguous from 0.",
        f"- Every record, test and dev, has exactly {res['n_obs']} finite, positive values, "
        "and times equal the formula, starting at 0 and ending below 90.",
        "- No country is in both splits; every eligible country is in exactly one of them.",
        "- Group ids are a bijection with countries and are never shared between splits.",
        f"- Leak check: {leak['n_names']} country names and {leak['n_codes']} country codes "
        f"searched in {leak['n_files']} open files; hits: {len(leak['hits'])}; "
        f"hits inside hex digests (coincidences, listed in the private log): "
        f"{len(leak['hits_inside_hashes'])}. "
        f"**{'PASSED' if not leak['hits'] else 'FAILED'}**",
        "",
        "## Outputs (sha256)",
        "",
    ]
    for p, h in outputs.items():
        L.append(f"- `{p}`: `{h}`")
    L += [f"- `inflection/data/sealed/{NAME}/truth.json`, "
          f"`inflection/data/sealed/{NAME}_key.json`,",
          f"  `inflection/data/sealed/{NAME}_private_log.md`: sealed, git-ignored; the truth "
          "hash is in the ledger.",
          ""]
    if seal_event is not None:
        L += ["## Ledger event appended by `seal_external_pool` (called once)", "",
              "```json", json.dumps(seal_event, indent=2, sort_keys=True), "```", ""]
    return "\n".join(L)


def private_log(info, pmeta, stats, res, fallback_used, leak, prelim=None) -> str:
    t, d = res["test"], res["dev"]
    L = [f"# Private data-preparation log: `{NAME}` (SEALED, identities and test outcomes)",
         "",
         f"Dataset {DATASET}, version {DATASET_VERSION}, sha256 `{info['sha256']}`, "
         f"downloaded {info['download_date']} from {info['url']}.",
         f"Sheet used: `{pmeta['sheet']}`.",
         "",
         f"Fallback used: {fallback_used}."]
    if prelim is not None:
        L += [f"Main-design (W={MAIN['W']}, H={MAIN['H']}) test size was {prelim} "
              f"(< {MIN_TEST}), hence the fallback."]
    for split, ws in (("test", t), ("dev", d)):
        n_ev = sum(w["transitioned"] for w in ws)
        sev = sum(w["severe"] for w in ws)
        era = Counter(w["era"] for w in ws)
        era_ev = Counter(w["era"] for w in ws if w["transitioned"])
        L += ["", f"## {split.upper()} class balance",
              f"- windows {len(ws)}, events {n_ev}, controls {len(ws) - n_ev}, "
              f"base rate {n_ev / max(len(ws), 1):.3f}",
              f"- severe events (horizon minimum below {SEVERE_FRAC} x the record maximum): {sev}",
              f"- by era: {dict(era)}; events by era: {dict(era_ev)}",
              f"- countries: {len({w['code'] for w in ws})}; windows per country: "
              f"min {min(Counter(w['code'] for w in ws).values())}, "
              f"max {max(Counter(w['code'] for w in ws).values())}"]
    L += ["", "## Test windows",
          "| id | group | countrycode | country | t0 | event_year | severe | era |",
          "|---|---|---|---|---|---|---|---|"]
    for w in sorted(t, key=lambda w: w["wid"]):
        L.append(f"| {w['wid']} | {w['group']} | {w['code']} | {w['name']} | {w['t0']} | "
                 f"{w['event_year']} | {w['severe']} | {w['era']} |")
    L += ["", "## Countries by group id (group: code, name, split, windows, events)"]
    per = defaultdict(list)
    for w in t + d:
        per[(w["group"], w["code"], w["name"], w["split"])].append(w)
    for (gid, code, name, split), ws in sorted(per.items()):
        L.append(f"- {gid}: {code}, {name}, {split}, {len(ws)} windows, "
                 f"events {sum(x['transitioned'] for x in ws)}")
    L += ["", f"Leak-check hits: {leak['hits']}",
          f"Leak-check hits inside hex digests (coincidences): {leak['hits_inside_hashes']}", ""]
    return "\n".join(L)


# --- main ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seal", action="store_true", help="write outputs and seal (once)")
    args = ap.parse_args()

    if _events(NAME, "pool_built", LEDGER):
        sys.exit(f"{NAME} is already sealed in the ledger; refusing to rebuild outputs.")

    info = download()
    df, pmeta = read_panel(RAW / ASSET)
    series, sinfo = build_series(df)
    stats = sinfo["stats"]
    assert stats["duplicate_country_years"] == 0, "duplicate (country, year) rows"
    seed = split_seed(NAME)

    res = build(series, seed, **MAIN)
    fallback_used, prelim = False, None
    if len(res["test"]) < MIN_TEST:
        fallback_used, prelim = True, len(res["test"])
        res = build(series, seed, **FALLBACK)
    assert len(res["test"]) >= 1 and len(res["dev"]) >= 1

    truth = sorted(({"world_id": w["wid"], "transitioned": bool(w["transitioned"]),
                     "severe": bool(w["severe"]), "era": w["era"]} for w in res["test"]),
                   key=lambda r: r["world_id"])
    names = sorted({s["name"] for s in series.values()})
    codes = sorted(series)

    if not args.seal:
        validate(res, truth, None, None)
        print(json.dumps(dict(
            dataset=DATASET_VERSION, sha256=info["sha256"], sheet=pmeta["sheet"],
            fallback_used=fallback_used, W=res["W"], H=res["H"],
            n_countries_eligible=res["n_countries_eligible"],
            dev_countries=len(res["dev_codes"]), test_countries=len(res["test_codes"]),
            dev_windows=len(res["dev"]), test_windows=len(res["test"]),
            dev_events=sum(w["transitioned"] for w in res["dev"]),
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
    gmap = {w["wid"]: w["group"] for w in res["test"]}
    manifest = dict(
        world_ids=tids, origins={wid: T_ORIGIN for wid in tids}, T=T_TOTAL,
        W=res["W"], H=res["H"], step_years=STEP, test_set=NAME,
        groups={wid: gmap[wid] for wid in tids},
        source=dict(dataset=DATASET, version=DATASET_VERSION, url=info["url"],
                    licence=LICENCE))
    (TEST_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    labels = {w["wid"]: {"transitioned": bool(w["transitioned"]), "group": w["group"]}
              for w in sorted(res["dev"], key=lambda w: w["wid"])}
    (DEV_DIR / "labels.json").write_text(json.dumps(labels, indent=2, sort_keys=True) + "\n")

    # ---- sealed key
    SEALED.mkdir(parents=True, exist_ok=True)
    key = {w["wid"]: dict(country=w["name"], countrycode=w["code"], t0=int(w["t0"]),
                          event_year=None if w["event_year"] is None else int(w["event_year"]),
                          split=w["split"], group=w["group"])
           for w in sorted(res["test"] + res["dev"], key=lambda w: w["wid"])}
    KEY.write_text(json.dumps(key, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

    # ---- validate and leak check (the logs are included once written)
    validate(res, truth, test_npz, dev_npz)
    open_files = [test_npz, TEST_DIR / "manifest.json", dev_npz, DEV_DIR / "labels.json",
                  Path(__file__).resolve()]
    outputs = {str(p.relative_to(ROOT)): sha256_file(p) for p in open_files[:4]}
    leak = name_leak_check(names, codes, open_files)
    PUBLIC_LOG.write_text(public_log(info, pmeta, stats, res, fallback_used, outputs, leak))
    leak = name_leak_check(names, codes, open_files + [PUBLIC_LOG])
    PUBLIC_LOG.write_text(public_log(info, pmeta, stats, res, fallback_used, outputs, leak))
    PRIVATE_LOG.write_text(private_log(info, pmeta, stats, res, fallback_used, leak, prelim))
    if leak["hits"]:
        sys.exit(f"leak check FAILED: {len(leak['hits'])} hits; see the private log. Not sealed.")

    # ---- seal, exactly once, after everything else is final
    meta = dict(dataset="Maddison Project Database", dataset_version=DATASET_VERSION,
                dataset_sha256=info["sha256"], sheet=pmeta["sheet"],
                W=res["W"], H=res["H"], n_obs=res["n_obs"],
                n_test_windows=len(res["test"]), n_dev_windows=len(res["dev"]),
                n_test_countries=len(res["test_codes"]), n_dev_countries=len(res["dev_codes"]),
                fallback_used=fallback_used)
    event = seal_external_pool(NAME, test_npz, truth, meta)
    assert event["record_sha256"]["real"] == outputs[str(test_npz.relative_to(ROOT))]

    PUBLIC_LOG.write_text(public_log(info, pmeta, stats, res, fallback_used, outputs, leak, event))
    leak2 = name_leak_check(names, codes, open_files + [PUBLIC_LOG])
    assert not leak2["hits"], leak2
    with PRIVATE_LOG.open("a") as f:
        f.write(f"\n## Seal event\n\n```json\n{json.dumps(event, indent=2, sort_keys=True)}\n```\n"
                f"\nFinal leak check on the public log after appending the seal event: "
                f"{leak2['hits']} (inside hex digests: {leak2['hits_inside_hashes']})\n")
    print(json.dumps(event, indent=2, sort_keys=True))
    print("sealed. public log:", PUBLIC_LOG.relative_to(ROOT))


if __name__ == "__main__":
    main()
