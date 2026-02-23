---
name: gemini-grounding-nodes
description: Gemini Google Search Grounding(google_search) 기반 "웹서치(근거획득) + 정리(표준화)" 노드를 표준 패턴(A/B/3step)으로 기획·스캐폴딩한다.
disable-model-invocation: true
context: fork
agent: general-purpose
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Bash(node *), Bash(npm *), Bash(pnpm *), Bash(yarn *), Bash(python *), Bash(pytest *), Bash(uv *), Bash(pip *), Bash(poetry *)
---

# Gemini Grounding Nodes Builder

## 사용법
- 기본(2노드 A): `/gemini-grounding-nodes <prefix>`
- 3단계: `/gemini-grounding-nodes <prefix> pattern=3step`
- 검색-only 대안(B): `/gemini-grounding-nodes <prefix> pattern=B`  (Vertex your-search-api 또는 전통 RAG 스캐폴딩)

## SSOT (반드시 최우선)
- `docs/standard/web-search-vs-summarize.md`
- `reference/gemini-grounding-metadata.md`
- `reference/postprocess-algorithm.md`

## 너의 임무
$ARGUMENTS로 전달된 요구를 바탕으로, repo에 "노드 2개(또는 3~4개)"를 설계/구축한다.

### 0) 입력 해석(질문 최소화, 기본값으로 진행)
- prefix(필수에 가까움): 첫 토큰을 prefix로 사용. 없으면 `Grounding`으로 가정.
- pattern: A(default) | 3step | B
- lang: repo 자동 감지 우선(typescript/node, python). 둘 다 애매하면 TS로 기본.
- outputDir: `src/nodes/`가 있으면 사용, 없으면 `src/nodes/`를 생성.

### 1) 반드시 만드는 것(산출물)
1. 설계 문서: `docs/nodes/<prefix>-grounding-nodes.md`
   - 노드 경계(왜 분리하는지)
   - I/O 계약(JSON schema) + 예시 payload
   - 에러/폴백(groundingMetadata 없음)
   - 캐시/로그(queries, grounded 여부, as_of_date)
   - UI 요구사항(searchEntryPoint 표시)
2. 코드 스캐폴딩:
   - Node A: `<prefix>GroundedGenerate` (Gemini generateContent + google_search enabled)
   - Node B: `<prefix>GroundingPostprocess` (결정적 파서/정리)
   - pattern=3step이면 EntityResolve / VerifySynthesize 추가
   - pattern=B이면 ExternalSearch(API) + Synthesize 노드 스캐폴딩(단, "Gemini google_search로는 검색-only 불가"를 문서에 명시)
3. 스키마:
   - `schemas/grounding/<prefix>.grounded-generate.input.schema.json`
   - `schemas/grounding/<prefix>.grounded-generate.output.schema.json`
   - `schemas/grounding/<prefix>.postprocess.output.schema.json`
4. 최소 테스트:
   - metadata 파싱
   - URL 정규화/중복 제거
   - segment(start/end) ↔ chunkIndices → citations 매핑

### 2) 하드 규칙
- Node B(정리)는 **LLM/네트워크 호출 금지**. 입력 JSON만으로 결정적으로 출력 생성.
- `groundingMetadata`가 없으면 `grounded=false` + 빈 sources/citations 반환.
- `searchEntryPoint.renderedContent`가 있으면 그대로 노출(컴플라이언스/UI용).
- 설계 문서에 "Gemini google_search는 LLM 호출 내부 워크플로우"임을 명시하고, 재사용/캐시 전략을 제안.

### 3) 작업 완료 시 출력
- 생성/변경 파일 목록(tree)
- 각 노드 호출 예시(로컬 실행/단위 테스트)
- 남은 TODO(키 설정, UI 렌더, 캐시 저장소 연결)

주의: API 키/시크릿을 파일에 쓰거나 커밋하지 말고, 문서에는 환경변수 형태로만 안내하라.
