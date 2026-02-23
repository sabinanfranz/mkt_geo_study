# Phase 2 세션 핸드오프 문서

> 이 파일은 새 Claude Code 세션에서 Phase 2 개발을 자율적으로 진행하기 위한 안내 문서입니다.
> Part A는 참고용이고, Part B의 코드블록 내용 전체를 새 세션 첫 메시지로 붙여넣으세요.

---

# Part A: 참고 파일 가이드

## 1. 개발 계획 & 백로그 (필수 읽기)

| 파일 | 용도 | 핵심 내용 |
|------|------|----------|
| `docs/strategy/70-content-dev-plan.md` | **Phase 2 개발 계획서** | 비주얼 컴포넌트 6종 설계, Stage 1-2 보강 매핑, Stage 3-5 커리큘럼, 구현 순서, 수치 목표 |
| `docs/engineering/40-backlog.md` | **Phase 2 백로그** (하단 Phase 2 섹션) | US-026~035 (Slice 5~10), 각 AC/DoD 포함. Phase 1 US-001~025 전부 완료 |
| `docs/tracking/80-progress.md` | **진행 현황 트래커** | Phase 1 완료 상태, Phase 2 Slice별 상태, 크롤링 활용 현황 |
| `docs/tracking/90-log.md` | **결정 로그** | D1~D8 결정사항, 세션별 작업 기록, Next Steps |

## 2. 기존 코드 (구현 참고)

| 파일 | 용도 | 줄 수 |
|------|------|-------|
| `apps/api/seed.py` | 현재 콘텐츠 데이터 — add_module/add_step/add_option 패턴 | ~1,014 |
| `apps/web/css/style.css` | 현재 CSS — 비주얼 컴포넌트 추가 위치 | ~1,238 |
| `apps/api/database.py` | DB 스키마 — 6테이블 | ~83 |
| `apps/api/main.py` | API 9개 + Stage 해제 로직 | ~711 |
| `apps/web/js/app.js` | 프론트엔드 SPA (이번 Phase 수정 불필요) | ~1,039 |

## 3. 콘텐츠 소스 (교육 자료 작성용)

| 파일 | 내용 |
|------|------|
| `materials/b2b.fastcampus.co.kr를 위한 GEO 심층 리서치 및 90일 실행 로드맵.md` | L1-L5 GEO, 오프사이트, 측정, 실험 |
| `materials/mentoring_temp.txt` | 인지적 도제 6원리 |
| `materials/geo_guide_temp.txt` | GEO 초보자 가이드 |
| `data/crawled/_report.md` | 크롤링 리포트 (Missing Elements, 링크 맵) |
| `data/crawled/_summary.json` | 크롤링 요약 (10페이지) |
| `data/crawled/*.json` | 개별 페이지 크롤링 데이터 |
| `docs/strategy/60-crawl-analysis-and-stage3-plan.md` | 크롤링 분석 + Stage 3-5 상세 계획 |

---

# Part B: 자율 개발 지시문

아래 코드블록 내용 전체를 새 Claude Code 세션의 첫 메시지로 붙여넣으세요.

```
GEO 멘토링 학습 시스템 Phase 2 개발을 시작합니다.

## 프로젝트 위치
C:\Users\admin\Desktop\Mkt Geo Study

## 현재 상태
- Phase 1 완료: 2 Stages, 16 모듈, 59 스텝, 179 옵션, 28 pytest 통과
- Phase 2 문서화 완료: 개발 계획(docs/70), 백로그(docs/40), 진행현황(docs/80)
- 서버: uvicorn apps.api.main:app --port 8010

## 해야 할 일
docs/engineering/40-backlog.md의 Phase 2 섹션(US-026~035)을 Slice 5→6→7→8→9→10 순서로 구현.
각 Slice 완료 시 docs/tracking/80-progress.md와 docs/tracking/90-log.md를 업데이트.

## 반드시 먼저 읽을 파일 (순서대로)
1. docs/strategy/70-content-dev-plan.md — 전체 개발 계획 (비주얼 컴포넌트 6종, Stage별 보강/신규 매핑)
2. docs/engineering/40-backlog.md — Phase 2 백로그 (US-026~035, 하단 "Phase 2" 섹션)
3. apps/api/seed.py — 현재 콘텐츠 구조 (add_module/add_step/add_option 패턴)
4. apps/web/css/style.css — 현재 CSS (비주얼 컴포넌트 추가 위치 확인)
5. apps/api/database.py — DB 스키마 (Stage 3-5 unlock_condition 지원 확인)

## 구현 순서 (6단계, 끊김 없이 순차 진행)

### Slice 5: US-026 — CSS 비주얼 컴포넌트 (가장 먼저)
- 변경 파일: apps/web/css/style.css
- 작업: style.css 끝에 6종 컴포넌트 CSS ~400줄 추가
  1. .browser-mockup (주소창 dot 3개 + URL + body + page-element present/missing)
  2. .compare-cards (before 빨강 상단 / after 초록 상단 flex 레이아웃)
  3. .diagram-box (중앙 정렬, title + pre)
  4. .callout (tip💡/warning⚠️/key-point🎯/hint🔍 4종, ::before 아이콘)
  5. .code-example (라벨 헤더 + pre 코드)
  6. .hierarchy-box (level-1/2/3 들여쓰기)
- 다크모드: [data-theme="dark"] 오버라이드 ~100줄 추가
- 각 컴포넌트의 상세 CSS 코드는 이 프로젝트의 .claude/plans/pure-wiggling-pinwheel.md 파일 Part 1에 완전한 코드가 있음. 반드시 참조하여 그대로 사용할 것.
- 검증: pytest tests/ 통과 확인

### Slice 6: US-027 + US-028 — Stage 1-2 비주얼 보강
- 변경 파일: apps/api/seed.py
- 작업: 기존 14개 reading 스텝의 content_md에 인라인 HTML 비주얼 삽입
- Stage 1 (M1-1~M1-7): 각 모듈 reading 스텝에 browser-mockup/compare-cards/diagram-box 추가
- Stage 2 (M2-1~M2-7): data/crawled/ 실제 크롤링 데이터 기반 비주얼 추가
- 모듈별 매핑은 docs/strategy/70-content-dev-plan.md "2. Stage 1~2 비주얼 보강" 섹션 참조
- extension_md 없던 스텝에 신규 추가 (9→~21개)
- 주의: quiz/practice 스텝 구조, 옵션, 피드백은 절대 변경하지 않음
- 검증: python -m apps.api.seed && pytest tests/ && 서버 시작 후 브라우저 확인

### Slice 7: US-029 — Stage 3 (구조화데이터 & 스키마 마스터, 7모듈)
- 변경 파일: apps/api/seed.py
- 작업: seed() 함수 내 Stage 2 데이터 뒤에 Stage 3 추가
  - Stage 3 INSERT: id=3, unlock_condition='{"require_stage_complete": 2, "min_score_pct": 70}'
  - M3-1 JSON-LD 기초 (1R+2Q+1P=4스텝)
  - M3-2 BreadcrumbList (4스텝)
  - M3-3 Article & BlogPosting (4스텝)
  - M3-4 Event 스키마 (4스텝)
  - M3-5 FAQPage 스키마 (4스텝)
  - M3-6 스키마 검증 (4스텝)
  - M3-7 종합 평가 (5Q)
- 콘텐츠 소스: materials/b2b.fastcampus.co.kr를 위한 GEO 심층 리서치 및 90일 실행 로드맵.md의 L3 구조화데이터 섹션 + data/crawled/ 스키마 데이터
- 모든 reading 스텝에 code-example/browser-mockup 비주얼 포함
- 모든 quiz/practice 옵션에 피드백 40자 이상 존댓말
- 검증: python -m apps.api.seed && pytest tests/

### Slice 8: US-030 — Stage 4 (오프사이트 & 멘션 전략, 7모듈)
- 변경 파일: apps/api/seed.py
- 작업: Stage 3 데이터 뒤에 Stage 4 추가
  - Stage 4 INSERT: id=4, unlock_condition='{"require_stage_complete": 3, "min_score_pct": 70}'
  - M4-1 오프사이트 GEO 개요 (4스텝)
  - M4-2 백링크 전략 (4스텝)
  - M4-3 브랜드 멘션 & PR (4스텝)
  - M4-4 엔터티 & 권위 신호 (4스텝)
  - M4-5 소셜 유통 & 콘텐츠 확산 (4스텝)
  - M4-6 리뷰 & 디렉토리 (4스텝)
  - M4-7 종합 평가 (5Q)
- 콘텐츠 소스: materials/ 오프사이트 섹션
- 비주얼: diagram-box, compare-cards, callout 활용
- 검증: python -m apps.api.seed && pytest tests/

### Slice 9: US-031 — Stage 5 (측정 & 실험 설계, 7모듈)
- 변경 파일: apps/api/seed.py
- 작업: Stage 4 데이터 뒤에 Stage 5 추가
  - Stage 5 INSERT: id=5, unlock_condition='{"require_stage_complete": 4, "min_score_pct": 70}'
  - M5-1 KPI 3층 프레임워크 (4스텝)
  - M5-2 GSC 활용법 (4스텝)
  - M5-3 GA4 & UTM 추적 (4스텝)
  - M5-4 AI Validator 루틴 (4스텝)
  - M5-5 가설 기반 실험 설계 (4스텝)
  - M5-6 90일 로드맵 설계 (4스텝)
  - M5-7 종합 평가 (5Q)
- 콘텐츠 소스: materials/ 측정/실험/90일 로드맵 섹션
- 검증: python -m apps.api.seed && pytest tests/

### Slice 10: US-032~035 — 검증 & QA
- US-032: Stage 해제 로직 확인 (GET /api/stages → 5개 반환, Stage 1→2→3→4→5 순차 해제)
- US-033: 다크모드에서 모든 비주얼 컴포넌트 CSS 오버라이드 존재 확인
- US-034: 기존 28개 pytest 통과 + Stage 3-5 테스트 추가 (최소 10개)
- US-035: scripts/validate_feedback.py 실행 → 모든 피드백 40자 이상, 존댓말

## 기술 규칙

### seed.py 작성 패턴
- 기존 헬퍼 함수 그대로 사용: add_module(stage_id, title, description, order_idx), add_step(module_id, step_type, title, content_md, order_idx, extension_md=None), add_option(step_id, label, content, is_correct, feedback_md, order_idx)
- Stage INSERT는 수동 ID 지정: conn.execute("INSERT INTO stages (id, title, ...) VALUES (?, ?, ...)", (3, ...))
- 스텝 구성 패턴: 일반 모듈 = 1 reading + 2 quiz + 1 practice = 4스텝, 종합평가 = 5 quiz
- quiz/practice 옵션: 4개씩 (A/B/C/D), is_correct=1인 것 1개
- 피드백: 40자 이상, 존댓말, 오답에도 격려+힌트

### 비주얼 HTML in content_md
- marked.js가 마크다운 내 인라인 HTML을 그대로 렌더링
- 마크다운 텍스트 사이에 HTML 블록 삽입 (빈 줄로 구분)
- 예시:
  "## 제목\n\n일반 텍스트...\n\n"
  '<div class="browser-mockup">'
  '<div class="browser-bar">'
  '<span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>'
  '<span class="browser-url">example.com</span>'
  '</div>'
  '<div class="browser-body">'
  '<div class="page-element present">Title — 있음</div>'
  '<div class="page-element missing">H1 — 없음</div>'
  '</div>'
  '</div>\n\n'
  "다음 텍스트..."

### 파일 소유권
- apps/web/css/style.css → frontend-dev
- apps/api/seed.py → backend-dev
- apps/api/database.py → backend-dev
- tests/ → 각 담당
- docs/ → coordinator

### 검증 루틴 (각 Slice 완료 시)
1. python -m apps.api.seed (DB 재생성)
2. pytest tests/ (기존 테스트 통과)
3. uvicorn apps.api.main:app --port 8010 (서버 시작)
4. 브라우저에서 해당 Stage reading 스텝 확인 (비주얼 렌더링)
5. 다크모드 토글 확인
6. docs/tracking/80-progress.md 해당 Slice 상태 업데이트 (⬜→✅)
7. docs/tracking/90-log.md에 작업 로그 추가

## 주의사항
- app.js는 수정하지 않음 (비주얼은 CSS만으로 처리)
- index.html은 수정하지 않음
- 기존 quiz/practice 스텝의 옵션/피드백은 절대 변경하지 않음
- seed.py가 커지면 Stage별 함수로 분리 가능 (seed_stage3() 등)
- 콘텐츠는 한국어로 작성
- .env, API 키 등 시크릿 절대 출력 금지

## 시작하기
위 파일들을 순서대로 읽은 뒤, Slice 5(US-026)부터 시작하세요.
각 Slice 완료 후 다음 Slice로 자동 진행하고, 전체 완료 시 최종 요약을 출력하세요.
```
