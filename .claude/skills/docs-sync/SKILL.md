---
name: docs-sync
description: "Sync docs/*.md to reflect current codebase & git status (API routes, LangGraph, web UI, run instructions, known gaps). Updates only docs and leaves code untouched."
argument-hint: "PLAN|APPLY [scope=all|api|web|llm] [recent_commits=20]"
context: fork
agent: Explore
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash(git *)
  - Bash(mkdir *)
---

# Docs Sync Skill (codebase → docs)

## Live repo context (preloaded)

- Branch/status: !`git status -sb`
- Last commits: !`git log -n 20 --oneline`
- Changed files (working tree): !`git diff --name-only`

## Parse arguments

- MODE: first token if it's PLAN or APPLY; otherwise MODE=PLAN.
- scope: if arguments contain "scope=api|web|llm|all" (default all)
- recent_commits: if arguments contain "recent_commits=N" (default 20)
- If no meaningful arguments, still run with MODE=PLAN, scope=all.

## What "sync" means

You will:
- Read the codebase and infer the *current* behavior.
- Update docs/*.md to match reality.
- Never modify application code in this skill. (docs only)
- Keep tool outputs short in chat. If something is huge, summarize and point to the file.

## Files to maintain (create if missing)

- docs/30-architecture.md
- docs/33-langgraph-agent-chain.md (if LangGraph present)
- docs/50-test-plan.md (light touch: ensure run/test commands align)
- docs/90-log.md (append a short sync note)
- docs/99-status.md (overwrite each run; "single source of current status")

## Stable update strategy (avoid clobbering)

In docs you update, prefer updating ONLY inside these markers. If markers don't exist, add them once:
- <!-- DOCS-SYNC:START -->
- <!-- DOCS-SYNC:END -->

Everything outside markers should be preserved as much as possible.

## Data you must extract from repo

(Use Grep/Glob/Read; do not execute app logic)

A) Project structure snapshot
- Identify key directories present: apps/api, apps/web, apps/llm, docs, tests, scripts

B) Backend API surface (FastAPI)
- Enumerate routes by scanning:
  - apps/api/** for patterns like: @app.get/post/... , APIRouter(), router.get/post, include_router
- Output a compact list:
  - METHOD PATH -> handler file

C) LangGraph usage (if present)
- Scan apps/llm/** for:
  - StateGraph/compile/invoke/stream/checkpointer/thread_id
  - interrupt/resume patterns
  - get_state_history/update_state/time travel
- Summarize:
  - graph entrypoint module
  - major nodes (if declared)
  - how FastAPI endpoints call the graph (if connected)

D) Frontend usage (vanilla web)
- Detect entry HTML (apps/web/index.html etc)
- Detect API calls in JS (fetch("/api/..."))
- Summarize user-visible pages/flows in 5 lines max

E) Run instructions
- Prefer scripts/dev.ps1 if exists
- Otherwise infer minimal run command (uvicorn module path from apps/api/main.py)

F) Development status
- Use git status output:
  - branch name
  - whether working tree is dirty
- From recent commits list (provided above), derive a 3–5 bullet "recent changes" summary.

## MODE=PLAN behavior

1) Do all extraction above, but do not edit docs yet.
2) Write a PLAN report to: docs/98-docs-sync-plan.md (overwrite)
   Include:
   - What you detected (API endpoints, graph entrypoint, UI calls)
   - Which docs files you would update
   - Exactly which sections (markers) would change
3) Print to chat ONLY:
   - list of files you would touch
   - 5-line summary of what's out of sync
   - how to run APPLY

## MODE=APPLY behavior

Safety rule:
- If working tree is dirty (uncommitted changes), DO NOT edit docs.
  Instead, fall back to MODE=PLAN and tell the user to commit/stash or run PLAN explicitly.
- If clean, proceed.

APPLY steps:

1) Ensure docs files exist (create minimal skeletons if missing).

2) Update docs/99-status.md (overwrite) with:
   - Git: branch, last commit (from injected logs), dirty/clean
   - What works now (bullets)
   - API endpoints table
   - LangGraph summary (if present)
   - Frontend summary + which endpoints it calls
   - How to run (commands)
   - Known gaps / TODO (from docs/40-backlog.md unchecked items if file exists; otherwise infer 3 likely gaps)

3) Update docs/30-architecture.md inside markers:
   - Current system diagram (text)
   - Current API list (short)
   - Current DB usage (SQLite path if referenced)
   - Integration points: web ↔ api ↔ langgraph

4) Update docs/33-langgraph-agent-chain.md inside markers (only if apps/llm exists):
   - Chain diagram (nodes/edges in text)
   - State fields (high-level)
   - Persistence/thread_id usage
   - Streaming/interrupt/time-travel support status (implemented vs planned)

5) Update docs/50-test-plan.md inside markers (light touch):
   - Smoke tests that match current endpoints
   - Minimal automated test suggestion aligned with tests/ folder

6) Append to docs/90-log.md:
   - 5 lines max: "docs-sync ran, what changed, next action"

7) Final chat output ONLY:
   - modified docs files list
   - 3 verification commands:
     - git diff --name-only
     - git diff (short advice: inspect docs changes)
     - git status -sb

Remember:
- No code edits, docs only.
- Keep outputs concise; big tables go into docs, not chat.
