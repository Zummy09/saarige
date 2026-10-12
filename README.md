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
