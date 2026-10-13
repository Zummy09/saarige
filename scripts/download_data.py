"""Download GTFS feeds into data/raw/ and record provenance in data/raw/manifest.json.

Run:  uv run python scripts/download_data.py

Sources (ODbL-1.0, credit required):
  BMTC  bus   — https://github.com/Vonter/bmtc-gtfs
  BMRCL metro — https://github.com/Vonter/bmrcl-gtfs
"""

import hashlib
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

FEEDS = {
    "bmtc": "https://github.com/Vonter/bmtc-gtfs/raw/main/gtfs/bmtc.zip",
    "bmrcl": "https://github.com/Vonter/bmrcl-gtfs/raw/main/gtfs/bmrcl.zip",
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}

    for name, url in FEEDS.items():
        dest = RAW_DIR / f"{name}.zip"
        print(f"Downloading {name} ...")
        urllib.request.urlretrieve(url, dest)

        manifest[name] = {
            "url": url,
            "file": dest.name,
            "size_bytes": dest.stat().st_size,
            "sha256": sha256_of(dest),
            "downloaded_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "license": "ODbL-1.0",
        }
        print(f"  {manifest[name]['size_bytes']:,} bytes  sha256={manifest[name]['sha256'][:12]}...")

    (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Manifest written to {RAW_DIR / 'manifest.json'}")


if __name__ == "__main__":
    main()
