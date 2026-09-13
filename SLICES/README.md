# Slice convention

A **slice** is one completable unit of work sized for a single LLM session (or less).  
Successor agents must be able to resume from files alone.

## Required frontmatter fields in each `SNNN_*.md`

```yaml
slice: S000
title: ...
status: planned | active | done | blocked
owner: agent-or-human
started: YYYY-MM-DD
updated: YYYY-MM-DD
depends_on: []
produces: []
```

## Body sections (required)

1. **Goal** — one sentence  
2. **In scope** — bullets  
3. **Out of scope** — bullets  
4. **Steps** — ordered, checkable  
5. **Acceptance** — how a stranger knows it’s done  
6. **Artifacts written** — paths touched  
7. **Handoff notes** — decisions, open questions, next slice id  

## Rules

- Prefer docs/design freeze before code.  
- One active slice at a time.  
- On stop: set status, update `HANDOFF.md`, leave next slice id explicit.
