"""The blinding protocol of RESEARCH_PLAN §4.2, enforced in code.

The person developing the methods and the person holding the test set are the same
agent here, so blinding cannot rest on secrecy alone. It rests on an append-only
ledger (`inflection/data/ledger.jsonl`, tracked in git) that fixes the *order* of
events, and on hashes that let anyone check that order afterwards:

1. `commit_test_seed` draws a secret seed, writes it under the git-ignored `sealed/`
   directory, and records only its salted hash. Committing the ledger to git puts
   an outside timestamp on that hash before any method exists.
2. `build_test_pool` generates the test worlds from that seed. Records -- the
   pre-origin series, under every realism layer -- are written in the open, since
   methods must read them. The truth goes to `sealed/`, and its hash to the
   ledger. The generator's git revision is recorded too, because a seed fixes the
   randomness but not the code.
3. `register_forecasts` records the hash of a forecast file. It refuses once the
   test set has been unsealed.
4. `unseal` is the only function that reads the truth. It records the event first.
5. `check_forecast` passes only a file whose exact bytes were registered before the
   first unseal. The scorer calls it and will not score anything else.

Point 5 of §4.2 -- no tuning after unsealing -- follows: a revised method's
forecasts would be registered after the unseal event and refused, so a revision
needs a fresh seed and a fresh test set.

None of this stops a determined cheat with write access to the ledger. It stops the
ordinary failure, which is not cheating but drift: looking once, adjusting a little,
and forgetting that you looked. And because the ledger is in git, the history would
show any rewrite.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "inflection" / "data"
LEDGER = DATA / "ledger.jsonl"
SEALED = DATA / "sealed"


class BlindingViolation(RuntimeError):
    """An operation would break the order the protocol requires."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git_revision() -> str:
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "inflection/sim"],
                               cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return rev + ("+dirty-sim" if dirty.strip() else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def read_ledger(ledger: Path = LEDGER) -> list[dict]:
    if not ledger.exists():
        return []
    return [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]


def _append(event: dict, ledger: Path = LEDGER) -> dict:
    event = dict(event, time=_now())
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def _events(name: str, kind: str, ledger: Path) -> list[tuple[int, dict]]:
    return [(i, e) for i, e in enumerate(read_ledger(ledger))
            if e.get("test_set") == name and e.get("event") == kind]


def is_unsealed(name: str, ledger: Path = LEDGER) -> bool:
    return bool(_events(name, "unsealed", ledger))


# --- 1. the seed -------------------------------------------------------------

def commit_test_seed(name: str, ledger: Path = LEDGER, sealed: Path = SEALED) -> str:
    """Draw and seal a test seed; record its salted hash. One seed per test-set name."""
    if _events(name, "seed_committed", ledger):
        raise BlindingViolation(f"test set {name!r} already has a committed seed")
    seed, salt = secrets.randbits(63), secrets.token_hex(16)
    sealed.mkdir(parents=True, exist_ok=True)
    (sealed / f"{name}.seed.json").write_text(json.dumps(dict(seed=seed, salt=salt)))
    digest = _sha256_bytes(f"{salt}:{seed}".encode())
    _append(dict(event="seed_committed", test_set=name, seed_sha256=digest), ledger)
    return digest


def _load_seed(name: str, ledger: Path, sealed: Path) -> int:
    committed = _events(name, "seed_committed", ledger)
    if not committed:
        raise BlindingViolation(f"no committed seed for test set {name!r}")
    blob = json.loads((sealed / f"{name}.seed.json").read_text())
    digest = _sha256_bytes(f"{blob['salt']}:{blob['seed']}".encode())
    if digest != committed[0][1]["seed_sha256"]:
        raise BlindingViolation(f"sealed seed for {name!r} does not match its commitment")
    return int(blob["seed"])


# --- 2. the pool -------------------------------------------------------------

def build_test_pool(
    name: str,
    n_per_type: int,
    ledger: Path = LEDGER,
    sealed: Path = SEALED,
    out_root: Path = DATA,
) -> dict:
    """Generate the test worlds; write open records per realism layer and sealed truth.

    Nothing about the worlds is printed or returned beyond counts and hashes.
    """
    from inflection.sim import realism as R
    from inflection.sim.generate import generate_pool, save_pool

    if is_unsealed(name, ledger):
        raise BlindingViolation(f"test set {name!r} is already unsealed; use a fresh one")
    seed = _load_seed(name, ledger, sealed)
    worlds, stats = generate_pool(n_per_type=n_per_type, seed=seed)
    # The generator's world ids hash a string that includes the transition type.
    # Not invertible in practice, but a test record should carry nothing derived
    # from its label, so test worlds are renumbered in their (already shuffled) order.
    for i, w in enumerate(worlds):
        w.world_id = f"{name}-{i:04d}"

    out = out_root / name
    record_hashes = {}
    for i, (layer_name, layer) in enumerate(R.LAYERS.items()):
        d = out / layer_name
        m = save_pool(worlds, stats, d, realism=layer,
                      seed=seed + 1 + i, seal=False, write_truth=False)
        # The generic manifest is for development pools. Here it would publish the
        # seed (`record_seed`, `generation.seed`) and, through per-type failure counts,
        # the class balance of the test set. Keep only what a method may know.
        for secret in ("record_seed", "generation", "truth_sha256"):
            m.pop(secret, None)
        m["test_set"] = name
        (d / "manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True))
        record_hashes[layer_name] = _sha256_bytes((d / "series.npz").read_bytes())

    truth = json.dumps([w.sealed_truth() for w in worlds], indent=2, sort_keys=True)
    truth_hash = _sha256_bytes(truth.encode())
    (sealed / name).mkdir(parents=True, exist_ok=True)
    (sealed / name / "truth.json").write_text(truth)

    summary = dict(
        n_worlds=len(worlds), n_requested=stats["n_requested"],
        layers=sorted(record_hashes),
    )
    _append(dict(event="pool_built", test_set=name, truth_sha256=truth_hash,
                 record_sha256=record_hashes, generator_revision=_git_revision(),
                 **summary), ledger)
    return summary


# --- 3-5. forecasts, unsealing, checking ---------------------------------------

def register_forecasts(path: Path, name: str, method: str, ledger: Path = LEDGER) -> str:
    """Record the hash of a forecast file for test set `name`. Refused after unsealing."""
    if is_unsealed(name, ledger):
        raise BlindingViolation(
            f"test set {name!r} is unsealed; forecasts registered now could have seen the "
            "truth. Commit a fresh seed and build a fresh test set.")
    digest = _sha256_bytes(Path(path).read_bytes())
    _append(dict(event="forecast_registered", test_set=name, method=method,
                 forecast_sha256=digest, file=str(Path(path).name)), ledger)
    return digest


def unseal(name: str, ledger: Path = LEDGER, sealed: Path = SEALED) -> list[dict]:
    """Read the truth for `name`. The event is recorded before the file is opened."""
    built = _events(name, "pool_built", ledger)
    if not built:
        raise BlindingViolation(f"test set {name!r} was never built")
    if not is_unsealed(name, ledger):
        _append(dict(event="unsealed", test_set=name), ledger)
    raw = (sealed / name / "truth.json").read_bytes()
    if _sha256_bytes(raw) != built[-1][1]["truth_sha256"]:
        raise BlindingViolation(f"sealed truth for {name!r} does not match its commitment")
    return json.loads(raw)


def check_forecast(path: Path, name: str, ledger: Path = LEDGER) -> dict:
    """The ledger entry for this exact file, if it was registered before the unseal."""
    digest = _sha256_bytes(Path(path).read_bytes())
    unsealed = _events(name, "unsealed", ledger)
    first_unseal = unsealed[0][0] if unsealed else None
    for i, e in _events(name, "forecast_registered", ledger):
        if e["forecast_sha256"] == digest:
            if first_unseal is not None and i > first_unseal:
                raise BlindingViolation(f"{path} was registered after {name!r} was unsealed")
            return e
    raise BlindingViolation(f"{path} was never registered for {name!r}, or has changed since")


# --- 6. release, after the test set is spent -----------------------------------

RELEASED = DATA / "released"


def release(name: str, ledger: Path = LEDGER, sealed: Path = SEALED,
            released: Path = RELEASED) -> Path:
    """Publish a spent test set's seed and truth, so anyone can check the ledger.

    Refused until the test set has been unsealed: releasing earlier would end the
    blinding. After it, nothing is lost -- the set can no longer score a forecast --
    and the ledger's hashes become checkable by anyone
    (`scripts/verify_blind_tests.py`).
    """
    if not is_unsealed(name, ledger):
        raise BlindingViolation(f"test set {name!r} is still sealed; releasing it would end the blinding")
    seed_blob = (sealed / f"{name}.seed.json").read_bytes()
    truth = (sealed / name / "truth.json").read_bytes()
    _load_seed(name, ledger, sealed)                     # verifies against the commitment
    built = _events(name, "pool_built", ledger)[-1][1]
    if _sha256_bytes(truth) != built["truth_sha256"]:
        raise BlindingViolation(f"sealed truth for {name!r} does not match its commitment")
    out = released / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "seed.json").write_bytes(seed_blob)
    (out / "truth.json").write_bytes(truth)
    if not _events(name, "released", ledger):
        _append(dict(event="released", test_set=name), ledger)
    return out
