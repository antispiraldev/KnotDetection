"""Narrate the explainer with the local Kokoro server, one clip per paragraph.

The page already carries its narration as its own text, so the audio is generated from
the page itself rather than from a second copy that could drift. One clip per paragraph
keeps the page's paragraph highlighting and its skip controls working exactly as they do
with the browser voice.

Needs the Kokoro FastAPI container running (docker: `luca-kokoro-1`, port 8880).

    PYTHONPATH=. .venv/bin/python scripts/build_explainer_audio.py [--voice af_heart] [--speed 1.0]

Writes `docs/explainer/audio/uNN.mp3` and `audio/manifest.json`. Re-run after editing the
page's words; clips whose text is unchanged are kept.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "explainer" / "index.html"
OUT = ROOT / "docs" / "explainer" / "audio"
API = "http://127.0.0.1:8880/v1/audio/speech"


class Narration(HTMLParser):
    """Paragraphs and captions inside each section, in reading order.

    Mirrors the page's own selection (`.body > p`, `figcaption`, `.takeaway p`): every
    <p> and <figcaption> inside a <section class="sec">, and nothing else.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.units: list[dict] = []
        self._section = -1
        self._depth = 0
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and "sec" in (a.get("class") or ""):
            self._section += 1
        elif tag in ("p", "figcaption") and self._section >= 0:
            self._depth = 1
            self._buf = []

    def handle_endtag(self, tag):
        if tag in ("p", "figcaption") and self._depth:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if text:
                self.units.append(dict(section=self._section, text=text))
            self._depth = 0
            self._buf = []

    def handle_data(self, data):
        if self._depth:
            self._buf.append(data)


def speak(text: str, voice: str, speed: float) -> bytes:
    body = json.dumps(dict(model="kokoro", input=text, voice=voice, speed=speed,
                           response_format="mp3")).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--force", action="store_true", help="regenerate even unchanged clips")
    args = ap.parse_args()

    parser = Narration()
    parser.feed(PAGE.read_text())
    units = parser.units
    if not units:
        raise SystemExit("no narration found in the page")

    OUT.mkdir(parents=True, exist_ok=True)
    old = {}
    manifest_path = OUT / "manifest.json"
    if manifest_path.exists() and not args.force:
        prev = json.loads(manifest_path.read_text())
        if prev.get("voice") == args.voice and prev.get("speed") == args.speed:
            old = {u["file"]: u["sha1"] for u in prev["units"]}

    out_units, made, kept, total = [], 0, 0, 0
    for i, u in enumerate(units):
        name = f"u{i:02d}.mp3"
        sha1 = hashlib.sha1(u["text"].encode()).hexdigest()
        path = OUT / name
        if old.get(name) == sha1 and path.exists():
            kept += 1
        else:
            try:
                path.write_bytes(speak(u["text"], args.voice, args.speed))
            except urllib.error.URLError as e:
                raise SystemExit(f"Kokoro unreachable at {API}: {e}\n"
                                 "Is the container running? docker ps | grep kokoro")
            made += 1
        total += path.stat().st_size
        out_units.append(dict(file=name, section=u["section"], sha1=sha1,
                              bytes=path.stat().st_size, text=u["text"][:90]))
        print(f"  {name}  section {u['section'] + 1}  {path.stat().st_size / 1024:6.0f} KB  "
              f"{'generated' if old.get(name) != sha1 else 'kept'}")

    manifest_path.write_text(json.dumps(
        dict(voice=args.voice, speed=args.speed, units=out_units), indent=2))
    print(f"\n{made} generated, {kept} kept, {total / 1e6:.1f} MB total, voice {args.voice}")
    print(f"wrote {manifest_path}")


if __name__ == "__main__":
    main()
