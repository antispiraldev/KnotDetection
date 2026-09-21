"""Check the blind tests against their ledger, from the released seeds and answers.

    PYTHONPATH=. .venv/bin/python scripts/verify_blind_tests.py
    PYTHONPATH=. .venv/bin/python scripts/verify_blind_tests.py --regenerate test_v2   # slow

For each released test set this confirms, using only files in the repository:

1. the released seed matches the salted hash committed before the test was built;
2. the released answers match the hash recorded when the test was built;
3. every open record file matches its recorded hash;
4. every forecast file matches a registration, and every registration came before
   the answers were first opened;
5. the ledger events are in the required order.

The ledger is in git, so `git log -p inflection/data/ledger.jsonl` shows when each
line was committed, independently of the timestamps written inside it.

`--regenerate` goes further: it checks out the generator at the revision recorded
when the test was built (in a temporary git worktree), rebuilds the test worlds from
the released seed, and confirms that they reproduce the released answers exactly.
That shows the test set was the one the seed fixed in advance. It takes 15-30 minutes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "inflection" / "data"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def check(name: str, events: list[dict]) -> list[str]:
    fails = []
    ev = [(i, e) for i, e in enumerate(events) if e.get("test_set") == name]
    first = {k: next((i for i, e in ev if e["event"] == k), None)
             for k in ("seed_committed", "pool_built", "unsealed", "released")}
    seed_ev = ev[[i for i, _ in ev].index(first["seed_committed"])][1]
    built = [e for _, e in ev if e["event"] == "pool_built"][-1]

    rel = DATA / "released" / name
    blob = json.loads((rel / "seed.json").read_text())
    if sha(f"{blob['salt']}:{blob['seed']}".encode()) != seed_ev["seed_sha256"]:
        fails.append("seed does not match its commitment")
    if sha((rel / "truth.json").read_bytes()) != built["truth_sha256"]:
        fails.append("answers do not match the hash recorded at build")
    for layer, h in built["record_sha256"].items():
        if sha((DATA / name / layer / "series.npz").read_bytes()) != h:
            fails.append(f"record file {layer} does not match its hash")

    regs = {e["forecast_sha256"]: i for i, e in ev if e["event"] == "forecast_registered"}
    files = sorted((DATA / "forecasts" / name).glob("*.json"))
    for f in files:
        i = regs.get(sha(f.read_bytes()))
        if i is None:
            fails.append(f"forecast {f.name} was never registered")
        elif first["unsealed"] is not None and i > first["unsealed"]:
            fails.append(f"forecast {f.name} was registered after unsealing")

    # Required order: seed committed < pool built < answers opened (< released, if so).
    seq = [first["seed_committed"], first["pool_built"], first["unsealed"]]
    if first["released"] is not None:
        seq.append(first["released"])
    if None in seq or seq != sorted(seq):
        fails.append(f"ledger events out of order: {first}")
    print(f"{name}: seed, answers, {len(built['record_sha256'])} record files and "
          f"{len(files)} forecasts checked; {built['n_worlds']} worlds; "
          f"generator {built['generator_revision'][:10]}")
    return fails


def regenerate(name: str, events: list[dict]) -> list[str]:
    built = [e for e in events if e.get("test_set") == name and e["event"] == "pool_built"][-1]
    rev = built["generator_revision"].split("+")[0]
    n = built["n_requested"] // 7
    seed = json.loads((DATA / "released" / name / "seed.json").read_text())["seed"]
    with tempfile.TemporaryDirectory() as tmp:
        wt = Path(tmp) / "wt"
        subprocess.run(["git", "worktree", "add", "--detach", str(wt), rev], cwd=ROOT,
                       check=True, capture_output=True)
        try:
            code = (
                "import json,hashlib\n"
                "from inflection.sim.generate import generate_pool\n"
                f"w,_=generate_pool(n_per_type={n}, seed={seed})\n"
                f"for i,x in enumerate(w): x.world_id='{name}-'+format(i,'04d')\n"
                "t=json.dumps([x.sealed_truth() for x in w], indent=2, sort_keys=True)\n"
                "print(hashlib.sha256(t.encode()).hexdigest())\n")
            out = subprocess.run([sys.executable, "-c", code], cwd=wt, capture_output=True,
                                 text=True, env={"PYTHONPATH": str(wt)}, check=True).stdout.strip()
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=ROOT,
                           capture_output=True)
    ok = out == built["truth_sha256"]
    print(f"{name}: regenerated from seed at {rev[:10]} -> {'reproduces' if ok else 'DOES NOT reproduce'} the answers")
    return [] if ok else ["regenerated answers differ"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--regenerate", nargs="*", default=[], help="test sets to rebuild from seed")
    args = ap.parse_args()
    events = [json.loads(l) for l in (DATA / "ledger.jsonl").read_text().splitlines() if l.strip()]
    names = sorted(p.name for p in (DATA / "released").iterdir())
    fails = []
    for name in names:
        fails += [f"{name}: {f}" for f in check(name, events)]
    for name in args.regenerate:
        fails += [f"{name}: {f}" for f in regenerate(name, events)]
    print("\nALL CHECKS PASSED" if not fails else "\nFAILED:\n  " + "\n  ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
