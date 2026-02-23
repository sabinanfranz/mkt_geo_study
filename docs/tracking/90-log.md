# 90 — Decision Log

## 2026-02-24 | extension_md (더 알아보기) 시각 컴포넌트 개선

### 배경

전체 37개 extension_md 블록 전수조사 결과, 8개 블록이 CSS 컴포넌트로 개선 가능하고, 테이블 스타일 미정의 및 callout 특이도 충돌 CSS 인프라 이슈 2건 발견.

### 수행 작업

**CSS (style.css)**:
1. `.extension-content table/th/td` 스타일 추가 (라이트+다크)
2. `.extension-content .callout` 특이도 충돌 해결 (`color: inherit`)

**seed.py (8개 extension_md 블록 교체)**:
1. S6 M6-2: MD 테이블→`comparison-table` + 코드→`code-example`
2. S4 M4-4: 번호목록→`flow-chart` 5단계 (Knowledge Panel)
3. S5 M5-4: 번호목록→`flow-chart` 5단계 + `callout.warning` (API 자동화)
4. S5 M5-1: 불릿→`layer-box` 3계층 (KPI 대시보드)
5. S4 M4-3: 비교 불릿→`compare-cards` (프레스릴리즈 vs 에디토리얼)
6. S3 M3-5: 순서목록→`callout.warning` (스키마 오용 경고)
7. S3 M3-6: 백틱 코드→`code-example` 래퍼 3개 (스키마 오류 패턴)
8. S5 M5-6: 3섹션 불릿→`hierarchy-box` 3레벨 (월간/분기/연간)

### 검증

- seed 실행 성공 · 62개 테스트 통과
- extension_md에서 CSS 컴포넌트 사용: flow-chart 2, layer-box 1, compare-cards 1, callout 2, code-example 2, hierarchy-box 1, comparison-table 1

---

## 2026-02-23 | Stage 6 시각 컴포넌트 개선 — ASCII Art → HTML 컴포넌트 + 다크모드 수정

### 배경

Stage 6 시드 콘텐츠에서 플로우차트가 `&#8595;` 텍스트 화살표, Hub-Spoke 도식이 `|`/`+--` ASCII 아트, hierarchy-box 안 마크다운 테이블이 raw 텍스트로 렌더링되는 문제 발견. 또한 `.extension-content` 영역에 다크모드 색상 오버라이드 누락으로 글자가 안 보이는 케이스 존재.

### 수행 작업

**seed.py (9개 블록 교체)**:
1. M6-6 Hub-Spoke ASCII 트리 → `tree-diagram` 컴포넌트
2. 5개 flow-chart의 `&#8595;<br>` → `flow-step`/`flow-arrow` 컴포넌트 (M6-1, M6-2, M6-5, M6-7, M6-8)
3. 3개 마크다운 테이블 → HTML `<table class="comparison-table">` (M6-1 RACI, M6-5 KPI, M6-7 스키마)

**style.css (다크모드 수정 5종)**:
1. `.extension-content strong` 다크모드 추가 (`color: #e0e0e0`)
2. `.extension-content h3/h4` 다크모드 추가 (`color: #f0f0f0`)
3. `.extension-content pre/code` 라이트+다크 스타일 추가
4. `.extension-content blockquote` 다크모드 추가
5. 기타 5개 선택자 다크모드 대비 보정 (`.module-status.in-progress`, `.option-label`, `.error`, `.empty`, `.bookmark-module`)

### 검증

- seed 실행 성공: DB 무결성 변동 없음 (6/45/178 stages/modules/steps)
- `&#8595;` 잔여: 0건, ASCII 트리 잔여: 0건
- `flow-arrow` 사용 스텝: 5개, `tree-diagram` 사용: 1개, `comparison-table` 사용: 3개
- **61개 pytest 전부 통과**

### 변경 파일

| 파일 | 변경 | 규모 |
|------|------|------|
| `apps/api/seed.py` | 9개 시각 블록 교체 | ~100줄 변경 |
| `apps/web/css/style.css` | 다크모드 오버라이드 5종 추가 | +80줄 |

---

## 2026-02-23 | Stage 6 시드 재구성 — GEO 액션 플랜 기반 8모듈 순차 과업 가이드

### 배경

기존 Stage 6은 codex가 `docs/archive/deprecated/71-stage6-task-module-strategy.md` 전략에 맞춰 구성한 7모듈/28스텝/84옵션이었으나, `docs/strategy/73-geo-action-plan.md` (1,390줄 GEO 전략 문서) 기반으로 재구성 요청. 핵심: "팀원들이 순차 과업 수행할 수 있는 완전 친절한 가이드".

### 설계 결정

| # | 결정 | 이유 |
|---|------|------|
| D1 | 기능별 7모듈 → Phase-순차 8모듈 | 30/60/90일 순서 그대로 따라야 "순차 과업" 실현 |
| D2 | Reading = SOP 구조 (Why→What→How→Template→DoD) | 학습이 아닌 실행 가이드 |
| D3 | 모듈당 4스텝 일관 유지 | 기존 패턴 호환 + 테스트 단순화 |
| D4 | docs/archive/deprecated/71-stage6-task-module-strategy.md, docs/archive/deprecated/75-stage6-seed-content-preparation.md 폐기 | 새 전략(docs/strategy/73-geo-action-plan.md) 기반으로 전면 교체 |

### 수행 작업

1. **seed.py Stage 6 전면 교체** (4,411줄 → 5,215줄, +804줄)
   - 8모듈: 킥오프 → 기술인프라 → Answer-first → Proof-first → 측정 → 허브스포크 → 권위자동화 → 종합평가
   - 32스텝 (8R + 9Q + 15P), 96옵션
   - docs/strategy/73-geo-action-plan.md의 §0~§9 콘텐츠 직접 반영 (템플릿, 티켓 테이블, KPI SOP 등)
2. **tests/test_phase2.py 업데이트** (5개 어설션 변경: 7→8모듈, ≥170→≥175스텝, ≥500→≥540옵션)
3. **tests/test_health.py 수정** (영어 placeholder → 한국어 40자+ 피드백)
4. **docs/archive/deprecated/71-stage6-task-module-strategy.md, docs/archive/deprecated/75-stage6-seed-content-preparation.md 폐기 공지** 추가
5. **docs/77 헤더 갱신** (7모듈→8모듈 Phase-순차 구조)

### 검증

- seed 실행 성공: 6 stages / 45 modules / 178 steps / 551 options
- Stage 6: 8 modules / 32 steps / 96 options (8R + 9Q + 15P)
- M6-8 capstone quiz = 2개 (evaluate 엔드포인트 호환)
- **57개 pytest 전부 통과**

### 변경 파일

| 파일 | 변경 | 규모 |
|------|------|------|
| `apps/api/seed.py` | Stage 6 전면 교체 | +804줄 (4,411→5,215줄) |
| `tests/test_phase2.py` | 5개 어설션 업데이트 | ~10줄 |
| `tests/test_health.py` | 영어→한국어 피드백 | ~12줄 |
| `docs/archive/deprecated/71-stage6-task-module-strategy.md` | 폐기 공지 추가 | +3줄 |
| `docs/archive/deprecated/75-stage6-seed-content-preparation.md` | 폐기 공지 추가 | +3줄 |
| `docs/strategy/77-stage6-curriculum-design.md` | 8모듈 구조 헤더 갱신 | ~30줄 |

---

## 2026-02-23 | Railway 코드 개선사항 문서화

### 배경

`docs/ops/74-railway-deployment-runbook.md`는 운영 절차 중심 문서이고,  
Railway 대응 코드가 실제로 어떻게 바뀌었는지(`database.py`, `main.py`, `seed.py`, migrations, scripts)를 한 번에 파악하기 어려웠습니다.

### 수행 작업

1. **신규 문서 작성**: `docs/ops/76-railway-code-changes.md`
   - DB 계층(SQLite/PostgreSQL) 전환 구조
   - 마이그레이션 러너/이력 테이블
   - seed 멱등 업서트 + user_progress 보존 정책
   - 배포 파일(`railway.json`, `Procfile`, `runtime.txt`) 역할
   - 검증 범위(`tests/test_deploy_db.py`)와 미보장 영역
2. **교차 링크 추가**
   - `docs/ops/74-railway-deployment-runbook.md`에 코드 변경 상세 링크 추가
   - `README.md` Railway 섹션에 코드 문서 링크 추가

### 목적

운영 런북(절차)과 구현 문서(코드 변경 근거)를 분리해,  
타 엔지니어/LLM이 문제 발생 시 코드 레벨 진단 지점을 빠르게 찾을 수 있도록 하기 위함.

---

## 2026-02-23 | Stage 6 시드 제작 근거 문서 분리

### 배경

기존 `docs/archive/deprecated/71-stage6-task-module-strategy.md`는 전략-모듈 매핑 중심 문서였고,  
`시드 콘텐츠를 어떤 규칙으로 마련했는지`를 재현 가능한 형태로 전달하기에는 정보가 분산되어 있었습니다.

### 수행 작업

1. **신규 문서 작성**: `docs/archive/deprecated/75-stage6-seed-content-preparation.md`
   - 입력 소스 매핑
   - 전략 → seed 변환 규칙(module/step/option)
   - 품질 규칙(피드백 길이/존댓말)
   - 테스트 연결(`tests/test_phase2.py`)과 재생산 SOP 정리
2. **문서 링크 연결**
   - `docs/archive/deprecated/71-stage6-task-module-strategy.md`에 관련 문서 링크 추가

### 목적

타 LLM이 Stage 6를 개정/확장할 때, 코드 탐색 없이도 제작 근거와 품질 게이트를 그대로 재적용할 수 있도록 하기 위함.

---

## 2026-02-22 | Stage 6 과업 실행 캡스톤 구현

### 배경

기존 커리큘럼은 Stage 5까지 학습 중심으로 완료되었지만, 실제 B2B 팀 실행 과업(운영/배포/검증)을 교육 모듈로 직접 연결하는 Stage 6가 필요했습니다.

### 수행 작업

1. **Stage 6 신규 추가** (`apps/api/seed.py`)
   - Stage 6 INSERT: `id=6`, `unlock_condition={"require_stage_complete": 5, "min_score_pct": 70}`
   - 7개 모듈 추가 (M6-1~M6-7), 모듈당 4스텝
   - 마지막 모듈(M6-7)에 퀴즈 2개 포함하여 `/api/stages/{id}/evaluate` 로직과 호환
2. **문구 정합성 수정**
   - Stage 5 마지막 축하 문구를 Stage 6 진입 안내로 변경
3. **검증 테스트 확장** (`tests/test_phase2.py`)
   - Stage 수 5→6 반영
   - Stage 6 unlock 조건 테스트 추가
   - Stage 6 모듈 수/스텝 수/평가모듈 퀴즈 존재 테스트 추가
   - 총 Steps/Options 최소 기준 상향 (`>=170`, `>=500`)
4. **문서 동기화**
   - `docs/strategy/70-content-dev-plan.md`, `docs/tracking/80-progress.md`에 Stage 6 반영

### 검증

- 시드 검증 결과: **6 stages / 44 modules / 174 steps / 539 options**
- `python3 -m pytest -q tests/test_phase2.py` → **26 passed**

### 변경 파일

- `apps/api/seed.py`
- `tests/test_phase2.py`
- `docs/strategy/70-content-dev-plan.md`
- `docs/tracking/80-progress.md`
- `docs/tracking/90-log.md`

---

## 2026-02-22 | 전문용어(Jargon) 쉬운 설명 콜아웃 추가

### 배경

교육 대상인 B2B 마케터는 개발 비전문가. seed.py 콘텐츠에 약 95개 전문용어가 설명 없이 사용 → 학습 도중 이해 장벽 발생.

### 수행 작업

1. **전수조사**: seed.py ~3,800줄 스캔, 8개 카테고리 약 95개 전문용어 발굴
2. **CSS 컴포넌트**: `.callout.glossary` (보라색 테마, 📖 아이콘) + 다크모드 추가
3. **용어 삽입**: 32개 reading 스텝 모두에 "핵심 용어" 콜아웃 박스 삽입
   - 스텝당 2~4개 용어, 한 줄 쉬운 설명 (15~30자)
   - 첫 등장 원칙: 용어가 최초로 나오는 스텝에서만 설명

### 변경 파일

| 파일 | 변경 | 규모 |
|------|------|------|
| `apps/web/css/style.css` | `.callout.glossary` + 다크모드 | +12줄 |
| `apps/api/seed.py` | 32개 reading 스텝에 glossary callout HTML | +~250줄 |

### 검증

- pytest 50개 전체 통과
- DB 무결성 유지 (5/37/146/455)

---

## 2026-02-22 | 어드민 모드 URL 라우팅 컨텍스트 유지

### 문제

`#/admin/content`에서 모듈 클릭 시 `#/module/{id}` (사용자 라우트)로 이동하면서 어드민 컨텍스트가 소실됨. 이후 모든 네비게이션(뒤로가기, 결과 화면, 다음 모듈, 재도전)이 사용자 모드로 돌아감.

### 수정 내용

| # | 변경 | 위치 |
|---|------|------|
| 1 | 어드민 라우트 2개 추가 (`#/admin/module/{id}`, `#/admin/module/{id}/result`) | router() |
| 2 | `learningState.fromAdmin` 플래그 추가 | learningState |
| 3 | `renderLearning(moduleId, isAdmin)` 시그니처 변경 + 상태 보존 | renderLearning |
| 4 | 뒤로가기 링크: 어드민이면 `#/admin/content` | renderCurrentStep |
| 5 | 모듈 클릭: `#/admin/module/${id}` | renderAdminContent |
| 6 | 마지막 스텝 완료: 어드민 프리픽스 | attachStepListeners |
| 7 | `renderResult(moduleId, isAdmin)` 전달 | renderResult |
| 8 | 합격/불합격 네비게이션 어드민 분기 | renderEvalResult |
| 9 | 다음 모듈/목록/대시보드 어드민 분기 | renderNormalResult |
| 10 | 재도전 어드민 경로 유지 | retryModule |

### 변경 파일

- `apps/web/js/app.js`: ~40줄 수정 (라우터 + 네비게이션 7곳)

### 검증

- pytest 50개 전체 통과 (프론트엔드 전용 변경)
- 사용자 모드 기존 플로우 유지 (isAdmin 기본값 false)

---

## 2026-02-22 | 시각화 컴포넌트 업그레이드 — 텍스트 도식 HTML 변환

### 작업 요약

seed.py의 텍스트/ASCII 기반 도식 21개를 구조화된 HTML/CSS 컴포넌트로 변환 완료.

### 4 Slice 실행 결과

| Slice | 작업 | 변경 |
|-------|------|------|
| A | CSS 클래스 불일치 수정 | seed.py 3곳 (browser-header→bar, code-title→label) + style.css 3클래스 추가 (callout-title/body, diagram-content) |
| B | 신규 CSS 컴포넌트 6종 추가 | comparison-table, flow-chart, pyramid-chart, tree-diagram, layer-box, network-diagram (+708줄) |
| C | Stage 1-2 도식 변환 (10개) | 마크다운 테이블→comparison-table, ASCII 플로우→flow-chart, 피라미드→pyramid-chart, 박스→layer-box, 트리→tree-diagram, 링크맵→network-diagram, 비교→compare-cards |
| D | Stage 3-5 도식 변환 (11개) | 마크다운 테이블 5→comparison-table, ASCII 트리 3→tree-diagram, 피라미드→pyramid-chart, 레이어→layer-box, 플로우 2→flow-chart |

### 검증

- pytest 50개 전체 통과
- DB 무결성: 5 stages, 37 modules, 146 steps, 455 options (변화 없음)
- 기존 6종 + 신규 6종 = 총 12종 CSS 비주얼 컴포넌트

### 변경 파일

- `apps/web/css/style.css`: +708줄 (불일치 수정 + 6종 신규 컴포넌트)
- `apps/api/seed.py`: 21개 항목 content_md 인라인 HTML 교체
- `docs/design/31-visual-components-design.md`: 신규 (설계 문서)
- `docs/engineering/32-implementation-checklist.md`: 신규 (구현 체크리스트)
- `docs/design/33-visual-design-summary.md`: 신규 (설계 요약)

---

## 2026-02-21 | PLAN 모드 — 초기 설계 완료

### 결정사항

| # | 결정 | 이유 | 트레이드오프 |
|---|------|------|-------------|
| D1 | LLM 영구 미사용, 선택지 기반 | 사용자 요청. 예측 가능한 학습 경험 | 자유도 낮음, 콘텐츠 사전 작성 부담 |
| D2 | MVP 범위 Stage 1~2만 | 빠른 검증. 16개 모듈이면 충분한 학습량 | Stage 3~5(심화/실전)는 추후 |
| D3 | 단일 사용자(default) | 인증 시스템 불필요, MVP 복잡도 축소 | 다중 사용자 지원 시 마이그레이션 필요 |
| D4 | Hash-based SPA 라우팅 | 바닐라 JS로 충분, 빌드 도구 불필요 | 히스토리 API 대비 URL이 덜 깔끔 |
| D5 | SQLite 단일 파일 DB | FastAPI + 파일 기반 = 배포 간단 | 동시 접속 한계 (MVP에선 문제 없음) |
| D6 | marked.js CDN 사용 | 마크다운 렌더링 직접 구현 대비 안정적 | 외부 의존성 1개 추가 |
| D7 | Seed 데이터 2단계 전략 | Slice 1~3은 최소 seed로 구조 검증, Slice 4에서 전체 콘텐츠 | 초기에는 더미 콘텐츠 |

### 이번 세션 요약

1. materials 3개 문서 분석 완료 (멘토링 이론, GEO 로드맵, GEO 초보자 가이드)
2. 인지적 도제 6원리 → 선택지 기반 구현 매핑 설계
3. GEO 스킬 맵 구성 (Stage 1: 개념 5개, Stage 2: 실행 4개)
4. 16개 모듈 상세 학습 플로우 설계
5. 3가지 인터랙션 패턴 정의 (읽기카드 / 선택퀴즈 / 다단계실습)
6. API 8개 엔드포인트 + DB 5테이블 설계
7. 4개 Slice 구현 계획 수립
8. PLAN 모드 문서 6개 작성 완료

---

## 2026-02-21 | APPLY 모드 — Slice 1~3 구현 완료

### 구현 완료 파일

| 파일 | 상태 | 내용 |
|------|------|------|
| `apps/api/database.py` | 신규 | SQLite 연결 + 5 테이블 생성 (init_db) |
| `apps/api/models.py` | 신규 | Pydantic 모델 12개 (Stage/Module/Step/Option/Answer/Progress/Evaluate) |
| `apps/api/main.py` | 재작성 | API 8개 엔드포인트 + Stage 해제 로직 + 정적 파일 서빙 |
| `apps/api/seed.py` | 신규 | 16 모듈 × 3~5 steps = 50 steps + 152 options (실제 GEO 콘텐츠) |
| `apps/web/index.html` | 재작성 | SPA 셸 + marked.js CDN |
| `apps/web/js/app.js` | 재작성 | Hash 라우터 + 4화면 (대시보드/모듈목록/학습/결과) + 3패턴 렌더링 |
| `apps/web/css/style.css` | 재작성 | 카드/퀴즈/피드백/프로그래스바 UI 스타일 |
| `docs/engineering/50-test-plan.md` | 신규 | QA 테스트 계획 (이슈 10개 + 수동 체크 20개 + 자동 테스트 제안) |

### QA 발견 이슈 및 수정

| # | 이슈 | 심각도 | 상태 |
|---|------|--------|------|
| 1 | 다음 모듈 네비게이션: moduleId+1 하드코딩 → 실제 모듈 목록에서 다음 ID 조회 | Critical | 수정 완료 |
| 2 | 종합평가 판정: order_idx=8 하드코딩 → 스테이지 내 마지막 모듈 여부로 판정 | Critical | 수정 완료 |
| 3 | marked.js XSS 방지: setOptions 미설정 | Minor | 수정 완료 |
| 4 | CORS allow_origins="*" | Minor | MVP에서는 유지 (추후 제한) |

### DB 현황

```
Stages: 2개
Modules: 16개 (Stage별 8개)
Steps: 50개 (일반 모듈 3개 + 종합평가 5개)
Options: 152개 (quiz당 4개)
```

### API 테스트 결과

- GET /api/health → ok
- GET /api/stages → Stage 1 해제, Stage 2 잠금
- GET /api/stages/1/modules → 8개 모듈 정상
- GET /api/modules/1/steps → 3 steps (reading 1 + quiz 2) + options 숨김
- POST /api/steps/{id}/answer → 정답/오답 피드백 + user_progress UPSERT
- GET /api/progress → 완료 모듈 수 + Stage 해제 상태
- POST /api/stages/1/evaluate → 점수 계산 + 합격/불합격 판정
- GET / → 프론트엔드 SPA 정상 서빙

### Next Steps

- [x] ~~APPLY Slice 1: DB + Stage/Module API + 대시보드~~
- [x] ~~APPLY Slice 2: Step 학습 화면 (읽기/퀴즈/실습 패턴)~~
- [x] ~~APPLY Slice 3: 진도 관리 + Stage 해제~~
- [x] ~~APPLY Slice 4 (부분): practice step 7개 추가~~
- [ ] **APPLY Slice 4 (잔여)**: Stage 1/2 모듈별 step 수 확대 (~5개씩)
- [ ] QA 발견 Minor 이슈 추가 수정
- [ ] 자동 테스트(pytest) 작성
- [ ] US-019: 피드백 텍스트 품질 검증
- [ ] US-020: 모듈 간 네비게이션 개선
- [ ] US-021: 학습 시간 기록
- [ ] US-022: 북마크 기능

---

## 2026-02-21 | APPLY 모드 — US-018 practice steps 추가

- seed.py에 Stage 2 모듈 2-1~2-7에 practice step 7개 추가 (총 steps: 52→59, options: 152→179)
- 모든 practice step은 b2b.fastcampus.co.kr 시나리오 기반 실습 문제
- 기존 24개 pytest 통과 확인

---

## 2026-02-21 | APPLY 모드 — US-019 피드백 품질 검증

- scripts/validate_feedback.py 검증 스크립트 신규 작성
- seed.py 피드백 30개 40자 미만→40자 이상으로 확장 (min 27→42자, avg 52→61자)
- 어조 100% 존댓말 일관성 확인, 177/179 범위 내 (2개 102자는 허용)

---

## 2026-02-21 | APPLY 모드 — US-020 모듈 간 네비게이션 개선

- Stage 2 종합평가(M2-8) 합격 시 "전체 학습 완료!" 메시지 및 축하 UI 추가
- Stage 1 평가 합격(다음 Stage 해제)과 Stage 2 평가 합격(전체 완료) 분기 처리
- result-complete CSS 스타일 추가 (그라데이션 배경 + 초록 테두리)

---

## 2026-02-21 | APPLY 모드 — US-021 학습 시간 기록

- database.py: user_progress에 time_spent_seconds INTEGER 칼럼 추가
- models.py: AnswerRequest에 time_spent_seconds 옵션 필드 추가
- main.py: submit_answer에서 time_spent_seconds DB 저장 로직 추가
- app.js: step 진입 시 타이머 시작, submitAnswer 시 경과 시간 전송

---

## 2026-02-21 | APPLY 모드 — US-022 북마크 기능

- database.py: user_bookmarks 테이블 추가 (user_id, step_id, created_at)
- main.py: POST /api/bookmarks/{step_id} (토글) + GET /api/bookmarks (목록) 엔드포인트 추가
- app.js: 학습 화면에 별 아이콘 북마크 버튼 + 대시보드에 북마크 목록 섹션 추가
- test_health.py: _seed_minimal에 user_bookmarks 클리어 추가 (FK 순서)

---

## 2026-02-21 | APPLY 모드 — US-023 확장 미션 카드

- database.py: steps 테이블에 extension_md TEXT 칼럼 추가 (nullable)
- seed.py: 9개 step에 "더 알아보기" 확장 콘텐츠 추가 (한국어 마크다운)
- app.js: reading/quiz step에 접이식 extension-card 렌더링 (quiz는 답변 후에만 표시)
- style.css: extension-card/toggle/content 스타일 추가
- 25개 테스트 전체 통과

---

## 2026-02-21 | APPLY 모드 — US-024 학습 통계 대시보드 (관리자용)

- models.py: ModuleStats, AdminStatsResponse 모델 추가
- main.py: GET /api/admin/stats 엔드포인트 추가 (전체 진도/정답률/학습시간/모듈별 통계/취약 모듈)
- app.js: #/admin 라우트 + renderAdminStats 함수 + 대시보드에 "학습 통계 보기" 버튼
- style.css: admin-summary 그리드, stat-card, weak-item, admin-table 스타일 추가
- 28개 테스트 전체 통과 (admin stats 테스트 3개 신규)

---

## 2026-02-21 | APPLY 모드 — US-025 Dark Mode 지원

- index.html: header에 theme-toggle 버튼 추가 (달/해 아이콘)
- app.js: initTheme/toggleTheme/updateThemeIcon 함수 추가 (localStorage + prefers-color-scheme 연동)
- style.css: [data-theme="dark"] 선택자로 전체 UI 다크 모드 스타일 약 200줄 추가
- 28개 테스트 전체 통과 (프론트엔드 전용 변경이므로 기존 테스트 회귀 없음)

---

## 2026-02-21 | 전체 백로그 완료

### 최종 현황
- **US-001 ~ US-025: 전체 25개 유저스토리 완료**
- 총 28개 자동 테스트 (pytest) 전체 통과
- API 9개 엔드포인트 운영 중
- 프론트엔드 SPA 5개 화면 (대시보드/모듈목록/학습/결과/관리자통계)

### Next Steps
- 프로덕션 배포 준비 (CORS 제한, 에러 로깅 강화)
- 수동 E2E 테스트 (전체 학습 흐름 1회 시뮬레이션)
- Stage 3+ 콘텐츠 기획 (필요 시)
- 다중 사용자 인증 시스템 (필요 시)

---

## 2026-02-22 | b2b.fastcampus.co.kr 웹크롤링 + Stage 3~5 계획 수립

### 수행 작업

1. **materials/ 폴더 전체 리뷰**: 3개 소스 문서 분석
   - GEO 심층 리서치 및 90일 실행 로드맵 (L1~L5 플레이북, 오프사이트, 측정, 실험 설계)
   - AI 도제식 멘토링 설계 원리 (인지적 도제 6원리, ZPD, 의도적 수련)
   - GEO 초보자 학습 가이드

2. **웹 크롤링 실행**: `scripts/crawl_b2b.py` 작성 + 실행
   - 10개 페이지 크롤링 (6 seed + 4 discovered)
   - 산출물: `data/crawled/` 폴더 (10개 JSON + _summary.json + _report.md)

3. **종합 계획 문서 작성**: `docs/strategy/60-crawl-analysis-and-stage3-plan.md` (2,063줄)

### 핵심 발견사항

| 발견 | 내용 | 교육적 가치 |
|------|------|-----------|
| JS 렌더링 문제 | 6/10 페이지가 CSR → 봇에게 빈 페이지 | "Before & After" 실습 소재 |
| 내부 링크 희소 | 평균 3.3 링크/페이지, Hub-Cluster 전무 | 링크 재설계 실습 |
| 스키마 부재/오용 | BreadcrumbList 0개, Course가 Contact에도 사용 | 스키마 수정 실습 |
| SSR 페이지 우수 | 4개 페이지(insight/contact)는 A등급 | Best Practice 예시 |

### Stage 3~5 커리큘럼 계획 (21개 모듈)

| Stage | 주제 | 모듈 수 | 핵심 내용 |
|-------|------|--------|---------|
| Stage 3 | 구조화데이터 & 스키마 마스터 | 7 | JSON-LD, BreadcrumbList, Article, Event, FAQPage, 검증 |
| Stage 4 | 오프사이트 & 멘션 전략 | 7 | 백링크, 멘션, PR, 소셜, 리뷰/디렉토리 (MECE) |
| Stage 5 | 측정 & 실험 설계 실전 | 7 | KPI 3층, GSC/GA4, AI Validator, 90일 실험 |

### 산출물

| 파일 | 내용 |
|------|------|
| `scripts/crawl_b2b.py` | 웹크롤러 (requests + BeautifulSoup) |
| `data/crawled/*.json` | 10개 페이지 크롤링 데이터 |
| `data/crawled/_summary.json` | 크롤링 요약 |
| `data/crawled/_report.md` | 크롤링 리포트 (Missing Elements 포함) |
| `docs/strategy/60-crawl-analysis-and-stage3-plan.md` | 크롤링 분석 + Stage 3~5 계획서 |

### Next Steps
- [ ] Stage 3 seed 데이터 작성 (7모듈 × 5steps × 4options)
- [ ] 크롤링 데이터를 seed.py에 통합 (비교형 step 타입 추가)
- [ ] Stage 해제 조건 확장 (Stage 2 → 3 → 4 → 5)
- [ ] 주기적 크롤링 자동화 (변경 추적용)

---

## 2026-02-22 | Phase 2 문서화 — 플랜, 백로그, 프로그레스

### 수행 작업

1. **콘텐츠 개발 계획서 작성**: `docs/strategy/70-content-dev-plan.md`
   - 비주얼 컴포넌트 시스템 설계 (6종 CSS 컴포넌트)
   - Stage 1~2 비주얼 보강 계획 (14개 reading 스텝)
   - Stage 3~5 신규 커리큘럼 상세 설계 (21모듈, ~87스텝)
   - 구현 순서, 수치 요약, 리스크 분석

2. **Phase 2 백로그 추가**: `docs/engineering/40-backlog.md`
   - US-026 ~ US-035 (10개 유저스토리) 신규 추가
   - Slice 5~10으로 구성 (CSS → 비주얼보강 → Stage 3 → 4 → 5 → QA)
   - 각 스토리별 Acceptance Criteria + DoD 정의

3. **프로젝트 진행 현황**: `docs/tracking/80-progress.md`
   - Phase 1 완료 현황 (25/25 유저스토리, 28 pytest)
   - Phase 2 계획 현황 (10개 유저스토리, 6 Slice)
   - 크롤링 데이터 활용 현황, 주요 결정사항 요약

### 산출물

| 파일 | 유형 | 내용 |
|------|------|------|
| `docs/strategy/70-content-dev-plan.md` | 신규 | Phase 2 콘텐츠 개발 계획서 (~200줄) |
| `docs/engineering/40-backlog.md` | 수정 | Phase 2 백로그 US-026~035 추가 |
| `docs/tracking/80-progress.md` | 신규 | 전체 프로젝트 진행 현황 트래커 |
| `docs/tracking/90-log.md` | 수정 | 이번 세션 로그 추가 |

### Next Steps

- [x] ~~**Slice 5 실행**: CSS 비주얼 컴포넌트 6종 추가 (US-026)~~
- [x] ~~**Slice 6 실행**: Stage 1-2 비주얼 보강 (US-027, US-028)~~
- [x] ~~**Slice 7 실행**: Stage 3 신규 개발 (US-029)~~
- [x] ~~**Slice 8 실행**: Stage 4 신규 개발 (US-030)~~
- [x] ~~**Slice 9 실행**: Stage 5 신규 개발 (US-031)~~
- [x] ~~**Slice 10 실행**: 검증 + QA (US-032~035)~~

---

## 2026-02-22 | APPLY 모드 — Phase 2 전체 구현 완료 (Slice 5~10)

### 수행 작업

#### Slice 5: US-026 — CSS 비주얼 컴포넌트 (완료)
- `apps/web/css/style.css`에 468줄 추가 (라인 1239→1708)
- 6종 컴포넌트: browser-mockup, compare-cards, diagram-box, callout(4종), code-example, hierarchy-box
- 다크모드 오버라이드 전 컴포넌트 적용 (~130줄)
- 28개 pytest 통과

#### Slice 6: US-027 + US-028 — Stage 1-2 비주얼 보강 (완료)
- `apps/api/seed.py`의 14개 reading 스텝 content_md에 인라인 HTML 비주얼 삽입
- Stage 1 (M1-1~M1-7): compare-cards, diagram-box, browser-mockup, callout 추가
- Stage 2 (M2-1~M2-7): diagram-box, compare-cards, browser-mockup, code-example, hierarchy-box, callout 추가
- extension_md가 없던 스텝에 신규 추가
- quiz/practice 스텝 변경 없음

#### Slice 7: US-029 — Stage 3 구조화데이터 & 스키마 마스터 (완료)
- 7모듈, 29스텝, 92옵션 추가
- M3-1 JSON-LD 기초, M3-2 BreadcrumbList, M3-3 Article/BlogPosting, M3-4 Event, M3-5 FAQPage, M3-6 스키마 검증, M3-7 종합 평가
- 모든 reading에 code-example/browser-mockup/compare-cards 비주얼 포함
- unlock_condition: Stage 2 완료 + 70%

#### Slice 8: US-030 — Stage 4 오프사이트 & 멘션 전략 (완료)
- 7모듈, 29스텝, 92옵션 추가
- M4-1 오프사이트 개요, M4-2 백링크, M4-3 멘션/PR, M4-4 엔터티, M4-5 소셜 유통, M4-6 리뷰/디렉토리, M4-7 종합 평가
- diagram-box, compare-cards, callout, code-example 비주얼 활용

#### Slice 9: US-031 — Stage 5 측정 & 실험 설계 (완료)
- 7모듈, 29스텝, 92옵션 추가
- M5-1 KPI 3층, M5-2 GSC, M5-3 GA4/UTM, M5-4 AI Validator, M5-5 가설 실험, M5-6 90일 로드맵, M5-7 종합 평가
- M5-7 마지막 퀴즈에 전체 과정 수료 축하 메시지 포함

#### Slice 10: US-032~035 — 검증 & QA (완료)
- `tests/test_phase2.py` 신규 생성: 22개 테스트
- US-032: Stage 해제 로직 5개 Stage 순차 확인 (5 tests)
- US-033: CSS 비주얼 6종 + 다크모드 오버라이드 존재 확인 (2 tests)
- US-034: Stage 3~5 API/데이터 검증 (9 tests)
- US-035: 피드백 40자 이상 + 존댓말 확인 (2 tests) + 데이터 무결성 (4 tests)
- 전체 50개 pytest 통과

### 최종 DB 현황

| 항목 | Phase 1 | Phase 2 | 합계 |
|------|---------|---------|------|
| Stages | 2 | +3 | **5** |
| Modules | 16 | +21 | **37** |
| Steps | 59 | +87 | **146** |
| Options | 179 | +276 | **455** |
| pytest | 28 | +22 | **50** |
| CSS 추가 | 0 | +468줄 | **468줄** |

### 변경 파일 목록

| 파일 | 변경 유형 | 규모 |
|------|----------|------|
| `apps/web/css/style.css` | 수정 | +468줄 (1239→1708줄) |
| `apps/api/seed.py` | 수정 | +2589줄 (1014→3603줄) |
| `tests/test_phase2.py` | 신규 | ~400줄 (22개 테스트) |
| `docs/engineering/40-backlog.md` | 수정 | Phase 2 완료 현황 업데이트 |
| `docs/tracking/80-progress.md` | 수정 | Slice 5~10 완료 표시 |
| `docs/tracking/90-log.md` | 수정 | Phase 2 작업 로그 추가 |

### Next Steps

- [ ] 프로덕션 배포 준비 (CORS 제한, 에러 로깅)
- [ ] 브라우저 수동 E2E 테스트 (5개 Stage 순차 진행)
- [ ] 다크모드 비주얼 수동 확인 (6종 컴포넌트)
- [ ] seed.py Stage별 함수 분리 리팩토링 (선택)
- [ ] Phase 3 기획 (필요 시)

---

## 2026-02-23 | GEO 액션 플랜 — 강화 크롤링 + 스코어카드 + 전략 문서 완성

### 배경

기존 10페이지 크롤링은 6/10이 JS 렌더링 실패(244자 껍데기)로 분석 가치가 낮았고, 전략서·심층리서치 문서는 전략 프레임워크에 불과해 **실행 가능한 액션아이템 문서**가 없는 상태였다. 추가 크롤링으로 데이터 갭을 해소하고, 모든 소스를 종합한 최종 GEO 전략 + 액션아이템 문서를 작성함.

### 수행 작업 (3 Phase)

#### Phase 1: 강화 크롤링 (데이터 갭 해소)

1. **`scripts/crawl_b2b_enhanced.py` 신규 작성** (1,692줄)
   - Selenium 4.18.1 + Chrome headless fallback (CSR 페이지 렌더링)
   - 추가 수집 항목: robots.txt, sitemap.xml, meta_robots, X-Robots-Tag, hreflang, answer_first_block, img_alt_coverage, word_count, faq_count, response_headers
   - 16 seed URLs (기존 6 + 전략서 상위 타겟 10)
   - 자동 내부링크 탐색 → 추가 9페이지 발견

2. **크롤링 실행 결과**: 25페이지 크롤 성공
   - robots.txt: **404** (미설정 → 모든 봇 기본 허용)
   - sitemap.xml: **404** (미설정 → 검색엔진 인덱싱 사각지대)
   - Selenium: **22/22 CSR 페이지 렌더링 성공** (0 실패)
   - 177개 미크롤 URL 발견 (향후 확장용)

3. **`scripts/analyze_geo_readiness.py` 실행** (기존 스크립트 활용)
   - 27페이지(25 신규 + 2 기존) 5차원 스코어카드 생성
   - 평균 19.3/25 (Selenium 렌더링 후 대폭 상승, 이전 11.2/25)
   - 최저: info_policies_privacy (7/25), 최고: b2b_instructor_apply (24/25)

4. **Go/No-Go 게이트 판정**: 4개 항목 **전부 통과**

| # | 체크포인트 | 결과 |
|---|----------|------|
| G1 | robots.txt 수집 | ✅ 404 확인 → 모든 봇 허용 판별 완료 |
| G2 | 페이지 크롤 ≥15개 | ✅ 25개 |
| G3 | JS 렌더링 | ✅ 22/22 Selenium 성공 |
| G4 | 스코어카드 ≥15개 | ✅ 27개 페이지 점수화 |

#### Phase 2: 전략 종합 문서 작성

5. **소스 통합 분석**
   - 전략서 (37p 스코어카드, 7허브/60스포크, 45티켓, Answer-first/Proof-first 템플릿)
   - 심층리서치 (L1~L5, 오프사이트, AI Validator 10프롬프트, 6가설, 90일 주차별)
   - 압축본 (docs/strategy/72-geo-strategy-context-compressed.md)
   - 신규 크롤 데이터 (25페이지 + 스코어카드 + robots/sitemap 분석)

6. **`docs/strategy/73-geo-action-plan.md` 작성** (1,390줄)
   - §0 Executive Summary: 전략 한 줄 + 4레버 + 30/60/90 목표
   - §1 현재 상태 진단: robots/sitemap/JS/스코어카드/내부링크/핵심문제 4가지
   - §2 전략 우선순위: 4레버 프레임워크, 페이지-Phase 매트릭스, 의존성 그래프
   - §3 Phase 1 (30일): 기반 정비 ~28티켓 (기술인프라 5 + Answer-first 10 + Proof 10 + 측정 3)
   - §4 Phase 2 (60일): 팬아웃 확장 ~20티켓 (허브 7 + 스포크 배분 + 사례 6 + 리소스 3)
   - §5 Phase 3 (90일): 권위·자동화 ~11티켓 (구조화데이터 4 + 내부링크 2 + 외부권위 3 + AI Validator 2)
   - §6 전체 백로그: ~59티켓 P0/P1/P2 우선순위 정렬 + 5열 테이블
   - §7 측정·실험: KPI SOP 3개 + 4주 루프 + Top 50 질문 + 6가설(H1~H6)
   - §8 템플릿·부록: Answer-first 3종 + Proof-first + 스포크 + AI Validator 10프롬프트 + 작업요청 + 주간로그

#### Phase 3: 검증

7. **문서 구조 검증 완료**
   - [x] Executive Summary + 4레버 + 30/60/90 목표
   - [x] 현재 상태 진단 (robots/sitemap/JS + 스코어카드 매트릭스)
   - [x] 페이지-Phase 우선순위 매핑 테이블
   - [x] Phase 1~3 구체적 티켓 + 5열 테이블
   - [x] 전체 백로그 ~59티켓 우선순위 정렬
   - [x] Top 50 질문 세트 (5카테고리 × 10개)
   - [x] KPI 측정 SOP
   - [x] 템플릿 섹션 완비

### 핵심 발견사항

| 항목 | 상태 | 영향 |
|------|------|------|
| robots.txt | **404** (미설정) | 모든 봇 기본 허용이나, 의도적 관리 필요 → T-01 |
| sitemap.xml | **404** (미설정) | 검색엔진 전체 URL 인덱싱 불가 → T-02 |
| CSR 비율 | **22/25 (88%)** | AI 봇이 콘텐츠 수집 불가 → T-03 (SSR 전환 권고) |
| Answer-first | **1/25 적용** | 거의 모든 페이지 미적용 → Phase 1 핵심 과제 |
| 구조화데이터 | **25/25 @type:Course** | Contact/Privacy 등 부적절 페이지에도 적용 → T-05 |
| 내부링크 | **평균 3.3개/페이지** | 허브-스포크 구조 전무 → Phase 2 핵심 과제 |

### 산출물

| 파일 | 유형 | 규모 |
|------|------|------|
| `scripts/crawl_b2b_enhanced.py` | 신규 | 1,692줄 |
| `data/crawled/*.json` | 신규/갱신 | 25개 페이지 JSON |
| `data/crawled/_enhanced_summary.json` | 신규 | 크롤 통합 요약 |
| `data/crawled/_enhanced_report.md` | 신규 | 강화 크롤 리포트 |
| `data/crawled/_robots_analysis.json` | 신규 | robots.txt 분석 |
| `data/crawled/_sitemap_urls.json` | 신규 | sitemap 분석 |
| `data/crawled/_geo_scorecard.json` | 갱신 | 27페이지 5차원 스코어카드 |
| `docs/strategy/73-geo-action-plan.md` | 신규 | **1,390줄** (최종 전략 문서) |

### 트레이드오프

| 결정 | 이유 | 트레이드오프 |
|------|------|-------------|
| Selenium fallback 사용 | 22/25 페이지 CSR → requests만으론 콘텐츠 수집 불가 | Chrome 의존성, 크롤링 속도 저하 |
| robots.txt 404 → "모든 봇 허용" 판정 | RFC 9309 기준 올바른 해석 | 사이트 운영팀 의도와 다를 수 있음 |
| ~59티켓 전체 상세화 | 전략서 45 + 추가 14 = 실행 가능 수준 상세 | 문서 1,390줄로 방대 → 핵심은 §2.2 매트릭스 |
| 우선순위 공식 = (25-점수)×전환가중치 | 개선 효과 × 비즈니스 임팩트 동시 반영 | 가중치가 주관적 (추후 데이터 기반 조정 필요) |

### Next Steps

- [ ] **Phase 1 착수**: T-01 robots.txt 확인/수정 → T-02 sitemap.xml 제출
- [ ] **T-03**: 개발팀에 CSR→SSR/ISR 전환 요청 (기술 인프라 최우선)
- [ ] **상위 10 랜딩 Answer-first 적용**: §3.2 티켓 T-06~T-15 순차 실행
- [ ] **측정 체계 세팅**: T-28~T-30 (Top 50 질문 + GA + 주간 로그)
- [ ] **4주 후 Phase 1 Go/No-Go → Phase 2 진행 판정**
