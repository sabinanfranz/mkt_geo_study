---
name: llm-mvp
description: "Plan & scaffold an LLM agent-node MVP using guardrail principles (loose inside/strict boundaries, wire→canonical, bounded retries, observability, golden set, prompt&contract as code)."
argument-hint: "PLAN|APPLY <1-2 paragraph MVP spec>"
disable-model-invocation: true
context: fork
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash(git *)
  - Bash(mkdir *)
  - Bash(python *)
  - Bash(pytest *)
---

# LLM MVP Guardrails Skill

## Input parsing

- MODE is first token if it's PLAN or APPLY; else MODE=PLAN.
- SPEC is the rest ($ARGUMENTS without MODE).
- If SPEC is empty: print one line asking the user to paste 1-2 paragraphs, then stop.

## Core principles you MUST enforce (non-negotiable)

P1) Loose inside, Strict at boundaries
- Inside nodes: freeform allowed, but decisions must be captured in structured state.
- Boundaries (strict): any side-effect, irreversible action, compliance risk, or user-facing final output.
- Boundary action must NEVER execute unless schema/type validation passes.

P2) Wire → Canonical → Business Logic
- Always store raw_output (for audit/debug) separately.
- Implement a SINGLE parse_and_normalize(raw_output)->canonical_object layer.
- Downstream must never read raw_output directly.

P3) Do NOT force JSON everywhere
- Strict schema is only for boundary outputs.
- Internal nodes may be markdown/natural language.

P4) Robust parser first, bounded retries
- Parser repairs first (strip fences, fix commas/quotes/braces, default missing fields).
- If still invalid: 1 self-correction call (max 2 total attempts).
- Still fail: fallback/human-in-loop/safe abort (no boundary execution).

P5) Observability is first-class
- Log: request_id, user_id, prompt_version, model params, token/latency estimates, tool calls, validation results, retry_count, fallback_path, canonical summary, raw_output pointer.

P6) Quality via regression protection
- Maintain golden set (10+ cases) and a simple gate test.
- If schema/contract breaks, fail the gate.

P7) Prompt & contract as code (SSOT)
- Prompts + schemas are versioned files.
- Every run records prompt_version.
- Schema/validation/docs stay in sync.

## Repo conventions (create if missing)

- Code:
  - apps/llm/** : agent nodes, schemas, prompts, parser/normalizer, logging, graph wiring
  - apps/api/** : endpoints
- Docs (create if missing):
  - docs/70-llm-mvp-guardrails.md
  - docs/71-boundary-map.md
  - docs/72-canonical-model.md
  - docs/73-observability.md
  - docs/74-golden-set.md
  - docs/75-prompt-contract-ssot.md
- Meta artifacts:
  - meta/llm-raw/ (raw_output files)
  - meta/llm-logs/events.jsonl (append-only)
  - meta/llm-logs/README.md (fields 설명)

## MODE=PLAN (문서/기획 중심)

1) Read inputs if present:
   - docs/06-clarified-brief.md (우선)
   - else docs/00-brief.md
   - plus SPEC
2) Produce/refresh the docs:

A) docs/70-llm-mvp-guardrails.md
- 위 7원칙을 "이 프로젝트에 적용한 규칙"으로 재서술
- 내부(Loose) vs 경계(Strict) 예시를 SPEC 기반으로 6개 이상

B) docs/71-boundary-map.md
- 표로 작성:
  | boundary | why strict | input schema | validation | side effect | fallback |
- 최소 5개 boundary를 정의 (ex: DB write, user-facing publish, email/send, payment/approval, external API action)

C) docs/72-canonical-model.md
- Canonical object 정의(필수 필드만, 작게):
  - objective / user_intent / entities[] / actions[] / output_artifact (optional) / safety_flags[]
- Raw output 저장 위치(pointer) 규칙
- parse_and_normalize 책임 범위 명시

D) docs/73-observability.md
- 최소 로그 스키마 + 저장 위치(meta/llm-logs/events.jsonl)
- request_id 생성 규칙(예: uuid4)
- 어떤 이벤트를 언제 기록하는지(LLM call, validation, retry, boundary 실행)

E) docs/74-golden-set.md
- 골든셋 10개 케이스 형식(JSONL 권장) 정의
- 통과 기준(스키마 통과/금지사항/필드 누락 없음 등)
- "변경 시 실행할 커맨드" 명시

F) docs/75-prompt-contract-ssot.md
- prompts/ 와 schemas/ 버전 규칙
- prompt_version을 로그/응답에 넣는 규칙
- SSOT 파일 목록

3) Produce a small backlog section at the end of docs/70:
- 10개 이내 작업 항목(경계/파서/로그/골든셋/엔드포인트/LLM 노드 등)

4) Chat output (PLAN에서는 이것만):
- created/updated docs list
- top 5 risks (boundary/validation/prompt drift)
- Next step: "/llm-mvp APPLY <same spec>"

## MODE=APPLY (최소 실행 가능한 가드레일 뼈대 구현)

Goal: "노드 기반 LLM MVP" 뼈대를 만들되, 경계에서 strict 검증+관측+재시도 제한을 반드시 포함.

0) Branch safety:
- If possible: `git checkout -b feat/llm-mvp-guardrails` (skip if already on it)

1) Create directories:
- apps/llm/prompts/v1/
- apps/llm/schemas/v1/
- apps/llm/guardrails/
- meta/llm-raw/
- meta/llm-logs/

2) Prompt & schema as code (SSOT)

A) apps/llm/prompts/v1/system.md
- static rules (no secrets, boundaries strict, output expectations)

B) apps/llm/prompts/v1/node_instructions.md
- "내부 노드 loose / 경계 노드 strict" 안내

C) apps/llm/schemas/v1/boundary_output.schema.json
- boundary에서 필요한 최소 필드만:
  - action_type, payload, safety_flags, confidence, canonical_ref

D) apps/llm/schemas/v1/canonical.schema.json
- docs/72에 맞춘 최소 canonical 스키마

E) apps/llm/prompts/manifest.json
- prompt_version="v1" + 파일 목록 + 변경 기록 자리

3) Canonical + Parser/Normalizer (단일 계층)

A) apps/llm/guardrails/canonical.py
- Pydantic models for Canonical + BoundaryOutput (minimal)

B) apps/llm/guardrails/parser.py
- parse_and_normalize(raw_output:str)->Canonical
- repair steps:
  - strip code fences/backticks
  - fix trailing commas
  - attempt json loads with simple repairs
  - default missing required fields
- NEVER raise raw exceptions to boundary layer; return structured error

4) Strict boundary validation

A) apps/llm/guardrails/validate.py
- validate_boundary(boundary_obj)->(ok, errors)
- Use jsonschema or pydantic validation; fail closed
- If invalid: try parser repair first, then (optionally) one LLM self-correction attempt hook placeholder
- Ensure retry cap: max 2 total attempts

5) Observability

A) apps/llm/guardrails/observe.py
- write_event(event:dict) -> append JSONL at meta/llm-logs/events.jsonl
- include required fields:
  request_id, user_id, prompt_version, model_name/params(unknown allowed), token_estimates, latency_ms(if measured), validation_result, retry_count, fallback_path, raw_output_pointer, canonical_summary
- raw_output saved under meta/llm-raw/<request_id>.txt and only pointer is logged

6) Agent nodes (node-based MVP)

A) apps/llm/nodes.py
- draft_node (LOOSE): produces freeform draft and suggested_patch
- canonicalize_node: calls parse_and_normalize on raw_output -> canonical
- boundary_node (STRICT): validates boundary schema; if fail -> fallback safe_abort (no side effect)
- persist_node (STRICT boundary example): writes canonical to SQLite ONLY after validation (stub OK)
- observe_node: logs events

B) apps/llm/graph.py (or integrate with existing graph)
- create minimal LangGraph/flow OR simple orchestrator if LangGraph not present
- The chain order must reflect principles:
  draft(loose) -> canonicalize -> validate(strict) -> boundary action -> observe
- If LangGraph exists in repo, prefer StateGraph compile() entrypoint, but keep it minimal.

7) FastAPI surface (boundary exposure)

A) apps/api/llm_routes.py
- POST /api/mvp/run
  body: { "message": "...", "user_id": "...", "mode": "draft|final" }
  behavior:
    - draft mode: return loose draft + canonical preview (no strict boundary action)
    - final mode: run strict boundary validation; if fails -> safe abort with errors
- Always return request_id and prompt_version

B) apps/api/main.py
- include_router

8) Golden set + gate

A) tests/golden/cases.jsonl (create 10 placeholder cases with minimal fields)
B) tests/test_golden_set.py
- loads cases, runs parse/validate on sample outputs (stub raw ok)
- ensures:
  - canonical schema valid
  - boundary schema valid for boundary cases
  - retry cap respected (simulated)
C) docs/74-golden-set.md update: how to add cases + run pytest

9) Minimal verification (safe)
- python -m compileall apps
- pytest -q (if tests exist)

10) Final output (APPLY에서는 이것만):
- created/modified files list
- how to run locally (uvicorn)
- how to view logs (tail meta/llm-logs/events.jsonl)
- how to run golden gate (pytest -q)
- remind: strict boundary blocks side effects if validation fails

Important constraints:
- Do not require any external API keys.
- Keep everything runnable with mock LLM if no provider configured.
- Small diffs; avoid rewriting unrelated files.
