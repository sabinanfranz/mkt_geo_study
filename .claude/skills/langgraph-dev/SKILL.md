---
name: langgraph-dev
description: "LangGraph 기반 기능을 PLAN/APPLY 모드로 설계/구현한다. (persistence, streaming, interrupt/resume, time-travel, memory store 포함)"
argument-hint: "PLAN|APPLY <feature spec or brief>"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash
---

# /langgraph-dev — LangGraph 설계/구현 스킬

## 입력 파싱

- `$ARGUMENTS`의 첫 토큰이 `PLAN` 또는 `APPLY`이면 → MODE로 사용, 나머지를 SPEC으로 사용.
- 첫 토큰이 `PLAN`/`APPLY`가 아니면 → MODE=PLAN, SPEC=$ARGUMENTS 전체.
- SPEC이 비어 있으면 아래 한 줄만 출력하고 **즉시 종료**:
  ```
  원하는 LangGraph 기능/흐름을 3~10줄로 적어주세요. 예: /langgraph-dev PLAN 사용자 질문을 받아 검색→요약→답변하는 RAG 파이프라인
  ```

## 안전 규칙

- 작업 전후 `git status -sb` 출력.
- 파괴적 Bash(rm, del, 대규모 이동) 금지. python, pytest만 허용.
- 시크릿(.env, API 키)을 읽거나 출력하지 않는다.

## 공통 선행 (PLAN·APPLY 모두)

1. 컨텍스트 탐색 (있으면 Read):
   - `docs/06-clarified-brief.md` (최우선)
   - 없으면 `docs/00-brief.md`
   - `docs/30-architecture.md` (있으면)
2. 디렉토리 보장 (없으면 생성):
   - `apps/llm/`, `apps/api/`, `docs/`

---

## PLAN 모드 (문서/설계만)

`docs/31-langgraph-design.md`를 생성/갱신한다. 아래 섹션을 **모두** 포함:

```markdown
# LangGraph Design

## 목표
이 LangGraph가 무엇을 자동화하는지.

## API 선택
Graph API vs Functional API — 선택 이유.

## State Schema
| 키 | 타입 | 업데이트 규칙 | 설명 |
|----|------|-------------|------|

## Nodes
| 노드 | 책임 | 입력 | 출력 |
|------|------|------|------|

## Edges / 흐름
조건 분기 포함한 노드 간 연결. 텍스트 다이어그램 권장:
START → node_a → (조건) → node_b / node_c → END

## Streaming 계획
stream_mode 선택: updates | messages | custom — 이유.

## Persistence 계획
checkpointer 종류 + thread_id 기준 설명.

## HITL(Human-in-the-Loop) 계획
interrupt 위치, resume payload 형태.

## Time-travel / 디버깅
get_state_history / update_state / checkpoint_id 사용 계획.

## Memory(장기기억) 계획
store + user_id context namespace 사용 여부/방식.

## Durable Execution
side-effect를 task로 감싸는 정책 (무엇이 side-effect인지).

## Open Questions (최대 8개)
1. ...
```

**PLAN 모드 제약:**
- 코드 파일은 최소 스텁(빈 파일 생성)까지만 허용. 본격 로직 작성 금지.
- 마지막 출력:
  - 생성/수정된 파일 목록
  - `APPLY로 구현하려면: /langgraph-dev APPLY <같은 spec>`

---

## APPLY 모드 (코드 뼈대 + 최소 동작)

목표: FastAPI에서 LangGraph를 호출하는 **최소 실행 가능 코드**를 작은 diff로 구현.

### 생성/수정 파일 목록

#### (1) `apps/llm/langgraph_app.py` — 핵심 그래프

```python
"""LangGraph application — compiled graph + helpers."""
from __future__ import annotations
from typing import Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# --- Checkpointer ----------------------------------------------------------
# 기본: InMemorySaver. SQLite가 설치되어 있으면 SqliteSaver 사용 가능.
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
except ImportError:
    checkpointer = InMemorySaver()

# --- State -----------------------------------------------------------------
class GraphState(TypedDict):
    messages: list[dict]  # [{"role":"user"|"assistant", "content":"..."}]
    # 프로젝트별 키를 여기에 추가

# --- Nodes -----------------------------------------------------------------
def process_node(state: GraphState) -> dict:
    """입력 처리 노드. 프로젝트에 맞게 수정."""
    return state

def respond_node(state: GraphState) -> dict:
    """응답 생성 노드. TODO: LLM 호출로 교체."""
    last = state["messages"][-1]["content"] if state["messages"] else ""
    reply = {"role": "assistant", "content": f"[STUB] {last[:80]}"}
    return {"messages": state["messages"] + [reply]}

# --- Durable Execution 참고 ------------------------------------------------
# 외부 API 호출·파일쓰기 등 side-effect는 @task로 감싸면
# 체크포인트 복구 시 중복 실행을 방지할 수 있다.
#
# from langgraph.func import task
# @task                           # 기본 durability="sync"
# def call_external_api(payload):
#     return requests.post(url, json=payload).json()
#
# durability 옵션:
#   "sync"  — task 완료까지 블로킹 (기본, 가장 안전)
#   "async" — fire-and-forget, 실패 시 재시도
#   "exit"  — task 완료 후 그래프를 종료하고 재개 가능

# --- Approval 노드 (HITL 예시, 선택) ---------------------------------------
# from langgraph.types import interrupt, Command
#
# def approval_node(state: GraphState) -> dict:
#     """사람의 승인이 필요한 노드. interrupt payload가 __interrupt__로 반환된다."""
#     decision = interrupt({"question": "승인하시겠습니까?", "options": ["yes","no"]})
#     if decision == "yes":
#         return state
#     return {"messages": state["messages"] + [{"role":"assistant","content":"거부됨"}]}

# --- Graph 구성 ------------------------------------------------------------
builder = StateGraph(GraphState)
builder.add_node("process", process_node)
builder.add_node("respond", respond_node)
builder.add_edge(START, "process")
builder.add_edge("process", "respond")
builder.add_edge("respond", END)

# --- Memory Store (장기 기억, 선택) -----------------------------------------
# from langgraph.store.memory import InMemoryStore
# from dataclasses import dataclass
# from langgraph.config import Context
#
# @dataclass
# class UserContext:
#     user_id: str = ""
#
# store = InMemoryStore()
# graph = builder.compile(checkpointer=checkpointer, store=store, context_schema=UserContext)
#
# 노드에서 장기 기억 접근:
# from langgraph.config import Runtime
# def my_node(state, runtime: Runtime[UserContext]):
#     memories = runtime.store.search(("user", runtime.context.user_id))

graph = builder.compile(checkpointer=checkpointer)

# --- Streaming 헬퍼 --------------------------------------------------------
def stream_graph(inputs: dict, config: dict, mode: str = "updates"):
    """stream_mode=updates|messages 지원 헬퍼."""
    for chunk in graph.stream(inputs, config=config, stream_mode=mode):
        yield chunk

async def astream_graph(inputs: dict, config: dict, mode: str = "updates"):
    """비동기 스트리밍 헬퍼."""
    async for chunk in graph.astream(inputs, config=config, stream_mode=mode):
        yield chunk

# --- Time-travel 헬퍼 ------------------------------------------------------
def get_history(config: dict) -> list[dict]:
    """get_state_history → 핵심 필드만 반환."""
    return [
        {"checkpoint_id": s.config["configurable"]["checkpoint_id"],
         "next": list(s.next), "created_at": str(s.metadata.get("created_at",""))}
        for s in graph.get_state_history(config)
    ]

def get_current_state(config: dict):
    """현재 state snapshot 반환."""
    return graph.get_state(config)

def replay_from_checkpoint(thread_id: str, checkpoint_id: str, values: dict | None = None):
    """checkpoint_id 시점으로 돌아가 update_state 후 재실행."""
    selected = {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
    if values:
        new_config = graph.update_state(selected, values=values)
    else:
        new_config = selected
    return graph.invoke(None, new_config)
```

#### (2) `apps/api/langgraph_routes.py` — FastAPI 라우터

```python
"""LangGraph API routes."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.llm.langgraph_app import graph, get_history, get_current_state, replay_from_checkpoint

router = APIRouter(prefix="/api/assistant", tags=["assistant-lg"])

# --- Request/Response models -----------------------------------------------
class InvokeRequest(BaseModel):
    message: str
    thread_id: str = "default"
    user_id: str = ""

class ResumeRequest(BaseModel):
    thread_id: str
    user_id: str = ""
    resume: Any = None

class TimeTravelRequest(BaseModel):
    thread_id: str
    checkpoint_id: str
    values: dict = {}

# --- Endpoints --------------------------------------------------------------
@router.post("/invoke")
def invoke(req: InvokeRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    inputs = {"messages": [{"role": "user", "content": req.message}]}
    result = graph.invoke(inputs, config=config)
    # interrupt 감지
    if "__interrupt__" in str(result):
        return {"status": "interrupted", "payload": result}, 202  # noqa: will be handled by FastAPI
    return {"status": "ok", "result": result}

@router.post("/resume")
def resume(req: ResumeRequest):
    from langgraph.types import Command
    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke(Command(resume=req.resume), config=config)
    return {"status": "ok", "result": result}

@router.get("/state")
def state(thread_id: str, checkpoint_id: str | None = None):
    config = {"configurable": {"thread_id": thread_id}}
    if checkpoint_id:
        config["configurable"]["checkpoint_id"] = checkpoint_id
    snapshot = get_current_state(config)
    return {"values": snapshot.values, "next": list(snapshot.next),
            "config": snapshot.config}

@router.get("/history")
def history(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    return {"history": get_history(config)}

@router.post("/time-travel")
def time_travel(req: TimeTravelRequest):
    result = replay_from_checkpoint(req.thread_id, req.checkpoint_id, req.values or None)
    return {"status": "ok", "result": result}
```

#### (3) `apps/api/main.py` — 라우터 등록

기존 main.py에 `from apps.api.langgraph_routes import router`와 `app.include_router(router)`를 **최소 diff**로 추가.

#### (4) `docs/31-langgraph-design.md` — APPLY에서도 갱신

#### (5) `requirements.txt` — 선택적 주석 추가

```
# langgraph-checkpoint-sqlite  # SQLite checkpointer (선택: pip install langgraph-checkpoint-sqlite)
```

### APPLY 마지막 출력

- 생성/수정된 파일 목록
- 로컬 실행 방법:
  ```bash
  uvicorn apps.api.main:app --reload
  ```
- curl 예시:
  ```bash
  # invoke
  curl -X POST http://localhost:8000/api/assistant/invoke \
    -H "Content-Type: application/json" \
    -d '{"message":"hello","thread_id":"t1"}'
  # resume
  curl -X POST http://localhost:8000/api/assistant/resume \
    -H "Content-Type: application/json" \
    -d '{"thread_id":"t1","resume":"yes"}'
  ```

---

## 규칙

- 코드 파일은 `apps/llm/`, `apps/api/` 범위에서만 생성/수정.
- 기존 엔드포인트·정적 파일 서빙을 깨뜨리지 않는다.
- 시크릿을 자동 요구/설정하지 않는다.
- 절대 `pip install`을 자동 실행하지 않는다. 설치가 필요하면 안내만 한다.
