# Learning Log

In my own words. One entry per session.

---

## Session 1 — 2026-10-12 (Phase 0)

**Chatbot vs agent**
- For a "write a message to my manager" task a chatbot is enough, because it is just text and needs no tool or outside facts. One LLM call does it.
- Simple question does not mean chatbot. If the answer needs real facts (like a fare), it needs a tool or plain code.

**The agent loop**
- The messages list holds the whole conversation, plus every tool call and result, so the agent knows what it did so far and what is left. The LLM is stateless, so we resend the list every call.
- If a tool fails, catch the error and send it back as a tool result. Retry once, then stop with a sorry message. The retry limit lives in code, not in the prompt.

**When not to use an agent**
- Ranking can be done by deterministic code, so there is no need to call the LLM for it.

**Setup**
- requirements.txt without pinned versions does not stop version drift. uv.lock pins every package, including hidden (transitive) ones.

_(Add a few lines of your own here.)_
