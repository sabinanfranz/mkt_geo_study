---
name: mvp-next
description: "백로그 최상단 미완료 항목 1개를 세로 슬라이스로 구현"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash
  - Task
---

# /mvp-next — 백로그 항목 1개 구현

## 목적

`docs/40-backlog.md`에서 **체크 안 된 최상단 항목 1개**만 골라 세로 슬라이스(최소 E2E)로 구현한다 (APPLY 모드).

## 실행 절차

1. **백로그 읽기**: `docs/40-backlog.md`를 읽고, 체크(`[x]`) 안 된 가장 높은 우선순위 항목 1개를 선택한다.

2. **구현 계획**: 선택한 유저스토리의 Acceptance Criteria를 분석하고, 필요한 변경 범위를 파악한다.
   - 백엔드 변경 → `backend-dev` 에이전트를 Task로 호출 (`apps/api/**`)
   - 프론트엔드 변경 → `frontend-dev` 에이전트를 Task로 호출 (`apps/web/**`)
   - LLM 변경 → `llm-engineer` 에이전트를 Task로 호출 (`apps/llm/**`)

3. **구현**: 각 에이전트에게 소유권 범위와 구체적 요구사항을 전달한다.
   - **작은 diff** 원칙: 한 번에 하나의 백로그 항목만.
   - **세로 슬라이스**: 백엔드 → 프론트 → LLM 순으로 최소 연결.

4. **테스트 실행**: 최소 1개 테스트를 수행한다.
   ```bash
   cd /c/Users/admin/Desktop/ccos-mvp-template && python -m pytest tests/ -x -q
   ```

5. **백로그 업데이트**: 완료한 항목에 `[x]` 체크한다.

6. **로그 업데이트**: `docs/90-log.md`에 아래를 추가한다.
   - 구현한 항목 ID
   - 변경된 파일 목록
   - 트레이드오프 메모

7. **git status 출력**: 마지막에 `git status`를 실행하여 변경 사항을 표시한다.

## 출력 (채팅에 표시)

```
✅ [US-XXX] 구현 완료

변경 파일:
  - apps/api/...
  - apps/web/...

테스트: {통과/실패} ({n}개)

📋 남은 백로그: {n}개
👉 다음: /mvp-next 로 계속하거나, /mvp-demo 로 실행 확인하세요.
```

## 규칙

- 한 번에 **1개 백로그 항목만** 구현한다. 2개 이상 동시에 하지 않는다.
- 소유권 경계를 반드시 지킨다 (에이전트별 담당 디렉토리).
- 시크릿을 출력하거나 요청하지 않는다.
- 테스트가 실패하면 수정 후 재시도한다. 실패 상태로 끝내지 않는다.
