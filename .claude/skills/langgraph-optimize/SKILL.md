---
name: langgraph-optimize
description: "Refactor or generate a LangGraph agent chain that optimizes context vs cost using recency window, brief/contract, artifacts & evidence pack, static-prefix prompts, and JIT retrieval gates."
argument-hint: "PLAN|APPLY <feature spec> [recent_turns=8] [top_k=5] [max_tokens=2400]"
disable-model-invocation: true
context: fork
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash(git *)
  - Bash(python *)
  - Bash(pytest *)
---

# LangGraph Context/Cost Optimizer (Agent Chaining)

You will receive a spec via $ARGUMENTS.

## Parse arguments

- MODE is first token if it's PLAN or APPLY; otherwise MODE=PLAN.
- SPEC is the rest of the arguments (the user's desired agent chain / feature).
- Optional settings (read from SPEC if present, otherwise defaults):
  - recent_turns: default 8 (range 6-12)
  - top_k: default 5 (range 3-8)
  - max_tokens: default 2400 (approx budget for LLM input; use heuristic)

If SPEC is empty: output a single line asking the user to provide 3-10 lines of desired behavior and stop.

## Ground rules (must enforce)

- Separate "stored history" vs "LLM input":
  - Keep full `messages` for audit/debug
  - Build `llm_input_messages` only at model-call time: static prefix + contract + brief + evidence snippets + recent N turns
- NEVER paste raw tool logs or huge retrieval chunks into `messages` used for model input.
  Store raw in artifacts and keep only short summaries + pointers in messages.
- Static prefix must be identical between calls (caching-friendly). No dates, request ids, or random values in prefix.
  Put dynamic data in suffix.
- Brief is rolling summary (8-15 lines max). Contract is "constitution" (structured, stable).
- Only ONE node is allowed to mutate brief/contract directly (Write-ACL):
  - context_updater node updates brief/contract
  - other nodes may only propose `suggested_patch` objects.
- Node outputs standardized as:
  - suggested_patch (for contract/brief)
  - artifact_writes (raw + summary + pointer id)
  - next_needs (what evidence is missing)
  - evidence_pack_updates (structured snippets)
- Retrieval is JIT (only when needed). Default OFF unless the node explicitly requires citations/facts/definitions.

## Where to implement (repo conventions)

- Code:
  - apps/llm/** : LangGraph state, nodes, prompt builder, artifact store
  - apps/api/** : FastAPI routes that call graph.invoke/stream/resume/history/time-travel
- Artifacts directory:
  - meta/langgraph-artifacts/ (raw tool outputs / evidence snapshots)
  - meta/langgraph-artifacts/index.jsonl (append-only pointers)
- Docs:
  - docs/32-langgraph-context-cost.md (policy + how it works)
  - docs/33-langgraph-agent-chain.md (current chain diagram + node IO contracts)

## MODE=PLAN

Create/refresh:

1) docs/32-langgraph-context-cost.md
   - Recency window policy (N=recent_turns)
   - Artifact vs messages rule
   - Static prefix / dynamic suffix rule (with examples)
   - Brief format (4 sections) + update triggers
   - Contract schema (objective, constraints, definitions, decisions, open_questions)
   - Patch schema (contract_patch, brief_patch, next_needs)
   - Evidence Pack schema [{snippet, source_id, score, why_relevant}]
   - JIT retrieval gate rules (ON/OFF cases)
   - Budgeting heuristic (approx tokens) + trimming order

2) docs/33-langgraph-agent-chain.md
   - Your proposed agent chain from SPEC (nodes, edges)
   - Which nodes are "cheap" vs "expensive"
   - Where retrieval runs and why
   - Where context_updater runs

3) Output a compact "apply plan":
   - Files you will create/modify
   - Key functions/classes you will add
   - How to test minimally

PLAN mode must NOT implement substantial code—only docs + a small scaffold file if necessary.

## MODE=APPLY

Goal: Make the repo contain an actual LangGraph implementation that enforces the policies above.

### 1) Create/Update these files (small diffs)

A) apps/llm/context_types.py
- Define TypedDict/dataclasses:
  - Contract (objective, constraints[], definitions{}, decisions[], open_questions[])
  - Brief (fixed 4 sections as strings)
  - EvidenceItem (snippet, source_id, score, why_relevant)
  - ArtifactPointer (id, kind, summary, path, created_at)
  - SuggestedPatch (contract_patch, brief_patch, next_needs[])
- Provide merge helpers:
  - merge_contract(base, patch) (append decisions, dedupe constraints, keep stable definitions)
  - merge_brief(base, patch) (enforce 8-15 lines limit)
  - merge_evidence(base, updates) (cap by top_k; keep highest score)

B) apps/llm/artifacts.py
- Implement artifact store:
  - write_artifact(kind, raw_text, summary, run_id) -> ArtifactPointer
  - store raw under meta/langgraph-artifacts/<run_id>/<id>.txt
  - append pointer to meta/langgraph-artifacts/index.jsonl
- IMPORTANT: messages should only carry pointer id + 1-3 line summary, not raw.

C) apps/llm/prompt_builder.py
- STATIC_PREFIX constant string (rules, output schema, safety)
- build_llm_input_messages(state, user_input, recent_turns, top_k, max_tokens):
  - order: STATIC_PREFIX -> Contract -> Brief -> Evidence snippets -> Recent N messages -> current user_input
  - compute approx tokens (heuristic: chars/4)
  - trimming order if above budget:
    1) drop evidence beyond top_k
    2) shrink recent_turns down to minimum 6
    3) shorten brief (keep headings, drop details)
  - return (llm_input_messages, metrics)

D) apps/llm/graph_app.py
- Build an agent chain with Graph API (StateGraph):
  Required state keys:
    messages (full), brief, contract, evidence_pack, artifacts_index, next_needs, llm_input_messages, metrics, suggested_patch
  Required nodes:
    1) router_node: decide if retrieval needed (JIT gate)
    2) retrieval_node: if needed, create Evidence Pack updates (structured) + artifact pointers
    3) assistant_node: call model (or mock) using llm_input_messages (from prompt_builder)
    4) context_updater_node: ONLY place that mutates brief/contract using suggested_patch
  Required edges:
    START -> router
    router -> retrieval (if needed) else assistant
    retrieval -> assistant
    assistant -> context_updater
    context_updater -> END
- Implement a safe default model:
  - If no API key configured: deterministic mock response that references brief/contract and says it is mock
- Ensure compile() is used and expose:
  - get_graph(checkpointer, store) -> compiled graph

E) apps/api/langgraph_routes.py (or update existing)
- Provide endpoints (minimal):
  - POST /api/assistant/invoke {message, thread_id, user_id}
  - POST /api/assistant/resume {thread_id, user_id, resume}
  - GET /api/assistant/history?thread_id=...
  - GET /api/assistant/state?thread_id=...&checkpoint_id=...
  - POST /api/assistant/time-travel {thread_id, checkpoint_id, values}
- Must pass config={"configurable":{"thread_id":...}} to support persistence.
- For interrupt/resume support:
  - If response contains "__interrupt__" return 202 with payload.

F) docs/32-langgraph-context-cost.md and docs/33-langgraph-agent-chain.md
- Update to match actual code.

### 2) Persistence/Interrupt/Time-travel hooks (skeleton is OK)

- In graph_app.py include placeholders / helpers:
  - interrupt handling path (payload JSON-serializable)
  - resume via Command(resume=...)
  - time travel via get_state_history + update_state + invoke(None, new_config)
- If checkpointer is not configured, warn in logs/docs that interrupt/time-travel require it.

### 3) Minimal tests

- tests/test_prompt_budget.py:
  - verifies build_llm_input_messages enforces max_tokens heuristic and recency window.
- tests/test_artifact_store.py:
  - verifies raw is stored on disk and only pointer is returned.

### 4) Verification commands (safe Bash only)

- python -m compileall apps
- pytest -q (if tests exist)

### 5) Output format at the end

Print ONLY:
- modified/created files list
- how to run locally (uvicorn)
- 2 curl examples: invoke + history
- note how to tune recent_turns/top_k/max_tokens
