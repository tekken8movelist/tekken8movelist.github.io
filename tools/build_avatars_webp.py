# -*- coding: utf-8 -*-
"""WebP copies of the portraits, which is what the pages actually load.

The portraits are 512x512 PNGs of 400-540 KB each, and the hub shows all 44:
close to 20 MB before a visitor has picked a fighter. WebP at quality 82 keeps
the dry-brush line work and lands around 40 KB (18.5 MB -> 1.8 MB in all).
The PNGs stay -- og:image and twitter:image point at them, because
link-preview crawlers are the one audience still not guaranteed to read
WebP -- but every <img> on the site loads the WebP.

    python tools/build_avatars_webp.py          # (re)write any stale WebP
    python tools/build_avatars_webp.py --check  # gate: every PNG has a fresh WebP

Freshness is recorded as the SHA-256 of the PNG each WebP was made from
(tools/source/avatar_webp.json), not as file times: a fresh clone gives every
file the same arbitrary mtime, and a time-based check would pass or fail by
luck. Replacing a portrait (workbench/avatar-pipeline) and rerunning this is
the whole update.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent
AVATARS = TOOLS.parent / "docs" / "avatars"
MANIFEST = TOOLS / "source" / "avatar_webp.json"
QUALITY = 82


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict[str, str]:
    if MANIFEST.is_file():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    manifest = load_manifest()
    pngs = sorted(AVATARS.glob("*.png"))
    stale = [
        png for png in pngs
        if not png.with_suffix(".webp").is_file() or manifest.get(png.stem) != digest(png)
    ]
    orphans = sorted(
        webp.name for webp in AVATARS.glob("*.webp")
        if not webp.with_suffix(".png").is_file()
    )
    if args.check:
        problems = [f"stale or missing: {png.with_suffix('.webp').name}" for png in stale]
        problems += [f"no PNG behind: {name}" for name in orphans]
        problems += [f"manifest lists a missing PNG: {slug}"
                     for slug in sorted(set(manifest) - {png.stem for png in pngs})]
        for line in problems:
            print(line)
        print(f"{len(pngs)} portraits, {len(problems)} problems")
        return 1 if problems else 0

    before = after = 0
    for png in stale:
        webp = png.with_suffix(".webp")
        with Image.open(png) as image:
            image.save(webp, "WEBP", quality=QUALITY, method=6)
        manifest[png.stem] = digest(png)
        before += png.stat().st_size
        after += webp.stat().st_size
        print(f"wrote {webp.name} ({webp.stat().st_size // 1024} KB)")
    manifest = {slug: manifest[slug] for slug in sorted(manifest) if (AVATARS / f"{slug}.png").is_file()}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    if stale:
        print(f"{len(stale)} portraits: {before // 1024} KB PNG -> {after // 1024} KB WebP")
    else:
        print(f"all {len(pngs)} WebP portraits are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
