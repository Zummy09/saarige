# CLAUDE.md — Saarige

Read this file and LEARNING_LOG.md at the start of every session. Then tell the user where we are.

## What this is
Saarige: an agentic commute planner for Bengaluru (Namma Metro + BMTC + autos).
Built as a learning project to apply to Namma Yatri (Moving Tech).

## How Claude works here (teacher mode)
- Teacher + senior engineer mentor. Plain style, short sentences, lots of whitespace.
- One block at a time. Concept before code: what, why, example, what breaks without it.
- Explain every file and folder we create.
- User writes core logic (agent loop, tools, fare engine, ranking, eval checkers). Claude writes boilerplate, gives skeletons with TODOs, then reviews critically.
- End every block with one check question. If wrong, re-explain differently.
- Verify libraries, datasets, fares and protocols against current sources before use. Say what was checked.
- User runs system-level installs (Homebrew, Docker) themselves. Claude gives command + source, then verifies.
- End of phase: recap, 3 interview questions, resume bullet with real numbers.

## Hard rules
- Times, distances, fares come from tools, never from the model.
- Every route, stop, time, fare in an answer must trace to a tool output (grounding check in code).
- No dark patterns. Never imply tipping improves pickup. Always show full price breakdown.
- Booking only after explicit user confirmation. Idempotency keys.
- Reliability model is a SIMULATOR. Label it as simulated everywhere.
- Saved places are personal data: local only, never logged in plain text.
- Thin LLM provider interface (swappable).
- Set and measure a p95 latency target for a plan.
- Ranking happens in code. The LLM only explains.

## Architecture principle
Agent only where the path depends on the input (understanding, clarifying, replanning).
Deterministic code for fares, ranking, booking.

## Environment (checked 2026-10-12)
- Apple M5, 16 GB RAM, 405 GB free disk. Homebrew present.
- uv 0.13.0 (Homebrew). Python 3.14.8 via uv (3.15 was 3 days old, skipped).
- Docker: NOT installed yet. Needed in Phase 2.

## Layout
src layout: `src/saarige/`. Add subpackages only when their phase starts:
agent/ tools/ fares/ ranking/ reliability/ memory/ booking/ llm/ ; plus data/ (git-ignored), evals/, docker/.

## Decisions log
- 2026-10-12: uv + pyproject.toml + uv.lock for reproducible installs.
- 2026-10-12: Python 3.14 (mature wheels; 3.15 too new).
- 2026-10-12: src layout, so broken packaging fails locally, not in CI.
- 2026-10-12: Config via pydantic-settings; API key as SecretStr.
- 2026-10-12: GTFS from Vonter community feeds (bmtc 7 Sep 2026, bmrcl 17 Aug 2026). No official maintained BMTC/BMRCL feed found. Re-check before Phase 12. Download via scripts/download_data.py with SHA-256 manifest (data provenance).

## Business framing (for Phase 12 memo)
- 2026-10-13: User asked whether steering users to metro/bus hurts Namma Yatri. Answer: NY earns from flat driver subscriptions (not % commission), and already sells metro tickets via ONDC. Key metric is driver earnings per online hour, not ride length. Multimodal converts cancelled peak trips into completed short feeder rides and adds new demand; some long trips shift to metro. Net effect must be measured (A/B on earnings/hour, trips/hour, cancellation rate). Saarige ranks neutrally by user constraints: no hidden bias toward autos or transit.

- 2026-10-13: Competitors checked. Namma Yatri's own "Namma Transit" (Jul 2025) already does multimodal metro+auto guidance; Tummoc does planning + metro/bus tickets + first/last-mile autos (Jun 2025). No LLM conversational agent found. Reframe Saarige as an AGENT LAYER on top of planners like Namma Transit: natural-language constraints, code ranking, reliability under auto scarcity, replanning, open MCP, evals. Never pitch it as "NY should do multimodal".

## Current status
Phase 1 — The data world (Phase 0 complete).
- Phase 1 done: Block 1 (GTFS file by file, midnight/service-day), Block 2 (feeds downloaded + manifest), Block 3 part 1 (Polars 1.44.2 chosen; loader.py written AND walked through line by line).
- NEXT SESSION START HERE:
  1. Re-ask open check question: if stop_id "0123" were read as int 123, which quality check goes wrong, too many or too few? (Answer: orphan check over-reports when ids mismatch across files; unused-stops too.)
  2. Walk through tests/test_quality.py and the structure of quality.py (helpers, CheckResult) BEFORE user codes.
  3. User implements the 6 checks in src/saarige/gtfs/quality.py (11 tests currently fail on purpose). Then code review.
  4. Run run_all on real BMTC + BMRCL feeds -> data-quality report; decide agent behaviour on bad data.
  5. Pending: update deck (https://claude.ai/artifact/RvjssrmnyH1Yn7dEmqLr5o) with 'agent layer over Namma Transit' framing if user says yes.
- Known BMTC red flags: single calendar service every day, no calendar_dates, no trips past 24:00, zone-based fares, Kannada names in translations.txt.

Phase 0 notes:
- Done: Blocks 1–6 (agent vs chatbot vs workflow, agent loop, when not to use an agent, uv/lock file, repo layout, config + secrets). First commit 64d5e2d pushed to github.com/Zummy09/saarige.
- Phase 0 end quiz: passed with gaps (2026-10-12). Pending: user's own lines in LEARNING_LOG.md. Next: Phase 1 (GTFS data world).
- Weak spots to revisit: AWS basics (env vars / Secrets Manager were new); give reasons, not just labels; loop explanation missed normal stop (no tool call), messages list, loop guard, "LLM requests / code runs". Re-quiz these at start of Phase 3.
