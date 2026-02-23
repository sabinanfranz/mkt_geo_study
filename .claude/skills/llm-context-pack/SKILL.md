---
name: llm-context-pack
description: Generate 5–7 compact Markdown context files under docs/llm_context so another LLM can quickly understand and extend this repo (LangGraph + FastAPI + HTML/CSS/JS + SQLite + LLM nodes).
argument-hint: "[5|6|7] [update|refresh] [full|backend|llm|db|frontend]"
disable-model-invocation: true
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(git *), Bash(python *), Bash(sqlite3 *)
---

# LLM Context Pack Generator (docs/llm_context)

## Inputs (via arguments)
- file_count: `$0` ∈ {5,6,7} (default: 6)
- mode: `$1` ∈ {update, refresh} (default: update)
  - update: preserve manual note blocks
  - refresh: overwrite generated sections
- focus: `$2` ∈ {full, backend, llm, db, frontend} (default: full)
- notes: `$ARGUMENTS` (anything else; treat as extra hints)

## Safety & scope (MUST)
- **Only write/edit files under `docs/llm_context/`.** Do not modify application code.
- Do not read or print secrets. Ignore (do not open): `.env`, `secrets/`, `*.pem`, `*.key`, `.aws/`, `.ssh/`, any API keys.
- Avoid destructive shell commands (no rm/mv/cp). Use shell only for safe introspection (git status, rev-parse, sqlite3 schema, etc.).
- Do not invent. If unclear, mark as `❓` and add to Open Questions.

## Output contract (information-dense)
- Use bullets + tables; minimize code dumps (link to file paths instead).
- Every file must start with:
  - Title
  - Generated time (ISO-8601)
  - Git commit short hash + branch (if available)
  - Focus + mode + file_count
- Every file must end with a preserved manual notes block:
  ```
  <!-- MANUAL_NOTES_START -->
  ## Manual notes (keep)
  - (human notes here)
  <!-- MANUAL_NOTES_END -->
  ```
  In update mode, preserve the content inside this block exactly.

## Workflow

### 1) Prepare
- Ensure `docs/llm_context/` exists.
- Collect lightweight repo facts (avoid huge outputs):
  - `git rev-parse --short HEAD`
  - `git branch --show-current` (if fails, omit)
  - `git status --porcelain`
  - Find run commands from README / pyproject / requirements / package.json (only if present).

### 2) Discover (focus on truth from files)
- **FastAPI:**
  - Locate where `FastAPI()` is instantiated, routers included, middleware, dependencies, auth.
  - Summarize endpoints in a table: method | path | purpose | handler file | request/response models.
- **LangGraph / LLM:**
  - Locate graphs and nodes (e.g., `StateGraph`, node funcs, conditional edges).
  - For each LLM node: purpose, inputs/outputs, prompt location, tools, retries/fallbacks, guardrails, cost/latency controls.
- **SQLite:**
  - Identify connection lifecycle, schema/migrations, critical tables/queries/indices, concurrency/locking risks.
- **Frontend (HTML/CSS/JS):**
  - Pages/components, how it calls API (fetch endpoints), state handling, build/dev flow (if any).

### 3) Generate file set

Default 6 files:

| # | File | Content |
|---|------|---------|
| A | `docs/llm_context/00_index.md` | Reading guide + manifest |
| B | `docs/llm_context/01_product_scope.md` | Product scope |
| C | `docs/llm_context/02_architecture.md` | Architecture |
| D | `docs/llm_context/03_api_fastapi.md` | API / FastAPI |
| E | `docs/llm_context/04_llm_langgraph.md` | LLM / LangGraph |
| F | `docs/llm_context/05_db_sqlite.md` | DB / SQLite |

If 7 files: add
| G | `docs/llm_context/06_frontend_web.md` | Frontend / Web |

If 5 files: omit (G) and merge frontend notes into `02_architecture.md`.

#### A) 00_index.md (reading guide + manifest)
Must include:
- Elevator pitch (3 bullets)
- Recommended read order
- "How to use with another LLM" (short, copy-ready prompt block)
- Repo map (top folders + roles)
- Key commands (run/test/migrate if found)
- Glossary (state names, key tables, main routers)
- Open Questions (aggregated)

#### B) 01_product_scope.md
Must include:
- Problem statement / target users
- MVP goals vs non-goals
- Core user flows (step-by-step)
- Constraints (latency, cost, model choice, sqlite limits, etc.)
- Success criteria (measurable)

#### C) 02_architecture.md
Must include:
- Component diagram (ASCII ok)
- Runtime sequence: browser → FastAPI → LangGraph/LLM → SQLite
- Directory responsibilities (key packages/modules)
- Data/state flow boundaries (where state lives, where prompts live)
- Deployment/dev topology (as implemented, else `❓`)

#### D) 03_api_fastapi.md
Must include:
- API structure (routers, prefixes, versioning)
- Endpoint table
- Auth/session (if any)
- Error conventions
- Minimal contract-test suggestions

#### E) 04_llm_langgraph.md
Must include:
- Graph list + entrypoints
- For each graph: state schema, nodes, edges/conditions, termination
- LLM node spec table (inputs/outputs/prompts/tools/retry/guards/cost)
- Context strategy (memory/RAG/db reads if any)
- Safety/guardrails present + gaps

#### F) 05_db_sqlite.md
Must include:
- DB file location + connection lifecycle
- Schema summary (tables, key cols, relations)
- Migration strategy (if any)
- Critical queries/indices notes
- Concurrency/locking risks + mitigations

#### G) 06_frontend_web.md (only if 7)
Must include:
- Pages and main UI pieces
- API endpoints used
- State management approach (vanilla JS etc.)
- Styling approach
- Build/dev workflow (if any)

### 4) Finalize
- After writing, run: `git diff --stat docs/llm_context`
- Return a short summary:
  - created/updated files
  - top 5 facts
  - top 5 open questions
