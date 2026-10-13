# Saarige

Agentic commute planner for Bengaluru: metro, BMTC buses and autos.
Fares, times and distances always come from tools, never from the LLM.

Status: Phase 0 (setup). See CLAUDE.md for architecture and progress.

## Setup

```bash
uv sync
cp .env.example .env   # then add your keys
uv run pytest
```

## Data and attribution

Transit data is downloaded by `scripts/download_data.py` into `data/raw/` (not committed).
Each download is recorded with its SHA-256 hash in `data/raw/manifest.json`.

- BMTC bus GTFS: [Vonter/bmtc-gtfs](https://github.com/Vonter/bmtc-gtfs), ODbL-1.0. Unofficial; timetables known to be inaccurate.
- Namma Metro GTFS: [Vonter/bmrcl-gtfs](https://github.com/Vonter/bmrcl-gtfs), ODbL-1.0. Unofficial; intermediate-station times are estimated.
