---
name: mvp-new
description: "MVP 한 줄 아이디어 → 기획 문서(docs/00~50) 일괄 생성"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Task
---

# /mvp-new — MVP 기획 문서 일괄 생성

## 목적

사용자가 제공한 **MVP 한 줄 아이디어**로부터 기획·설계·테스트 문서를 일괄 생성한다 (PLAN 모드).

## 입력

`$ARGUMENTS` — 사용자가 입력한 MVP 한 줄 아이디어 문자열.

예: `/mvp-new 반려동물 산책 일지를 기록하고 통계를 보여주는 웹앱`

## 실행 절차

1. **Brief 작성**: `$ARGUMENTS`를 `docs/00-brief.md`에 저장한다. 기존 내용이 있으면 덮어쓴다.

2. **PRD 생성**: `product-manager` 에이전트를 Task로 호출하여 `docs/10-prd.md`와 `docs/40-backlog.md`를 생성한다.
   - 프롬프트에 brief 전문을 포함한다.
   - 백로그는 user story + acceptance criteria + DoD 포함.

3. **UX 설계**: `ux-designer` 에이전트를 Task로 호출하여 `docs/20-ux.md`를 생성한다.
   - 프롬프트에 brief + PRD 요약을 포함한다.

4. **아키텍처 초안**: `docs/30-architecture.md`를 직접 작성한다.
   - API 엔드포인트 목록, DB 테이블 스키마, LangGraph 그래프 개요를 포함한다.
   - 기술 스택: FastAPI + SQLite + LangGraph + 바닐라 HTML/CSS/JS.

5. **테스트 계획**: `qa-tester` 에이전트를 Task로 호출하여 `docs/50-test-plan.md`를 생성한다.

6. **로그 기록**: `docs/90-log.md`에 이번 기획 세션의 결정사항을 추가한다.

## 출력 (채팅에 표시)

```
✅ MVP 기획 완료!

📋 백로그: {총 개수}개 유저스토리
⚠️  Top Risks:
  1. {리스크 1}
  2. {리스크 2}
  3. {리스크 3}

👉 다음 추천: /mvp-next 로 첫 번째 백로그 항목을 구현하세요.
```

## 규칙

- 코드 파일(`apps/`)은 생성하지 않는다. 문서만 작성한다.
- 시크릿(.env, API 키)을 출력하거나 요청하지 않는다.
- 결과물은 파일로 저장하고, 채팅에는 위 요약 형식만 출력한다.
