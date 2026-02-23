# 80 — 프로젝트 진행 현황

## 전체 요약

| 항목 | Phase 1 (완료) | Phase 2 (계획) | 최종 목표 |
|------|---------------|---------------|----------|
| Stages | 2 | +4 | **6** |
| Modules | 16 | +28 | **44** |
| Steps | 59 | +115 | **174** |
| Options | 179 | +360 | **539** |
| 자동 테스트 | 28 | +26 | **54** |
| API 엔드포인트 | 9 | 0 (변경 없음) | **9** |
| SPA 화면 | 5 | 0 (변경 없음) | **5** |
| CSS 비주얼 컴포넌트 | 0 | +6종 (~400줄) | **6종** |

---

## Phase 1 — MVP 구현 (완료)

### 타임라인

| 날짜 | 작업 | 상태 |
|------|------|------|
| 2026-02-21 | PLAN 모드: 문서 6개 작성 (brief, PRD, UX, architecture, backlog, test plan) | ✅ 완료 |
| 2026-02-21 | Slice 1: DB + Stage/Module API + 대시보드 (US-001~007) | ✅ 완료 |
| 2026-02-21 | Slice 2: Step 학습 화면 3패턴 (US-008~013) | ✅ 완료 |
| 2026-02-21 | Slice 3: 진도 관리 + Stage 해제 (US-014~017) | ✅ 완료 |
| 2026-02-21 | Slice 4: 콘텐츠 완성 + 추가 기능 (US-018~022) | ✅ 완료 |
| 2026-02-21 | P2 기능: 확장 미션, 관리자 통계, Dark Mode (US-023~025) | ✅ 완료 |

### 구현 산출물

| 카테고리 | 파일 | 설명 |
|---------|------|------|
| Backend | `apps/api/main.py` | FastAPI 9개 엔드포인트 + 정적 파일 서빙 (711줄) |
| Backend | `apps/api/database.py` | SQLite 6테이블 (stages, modules, steps, options, user_progress, user_bookmarks) |
| Backend | `apps/api/models.py` | Pydantic 모델 14개 |
| Backend | `apps/api/seed.py` | 2 Stages, 16 모듈, 59 스텝, 179 옵션 (1,014줄) |
| Frontend | `apps/web/index.html` | SPA 셸 + marked.js CDN (24줄) |
| Frontend | `apps/web/js/app.js` | Hash 라우터 + 5화면 + 3패턴 렌더링 (1,039줄) |
| Frontend | `apps/web/css/style.css` | 카드/퀴즈/피드백/다크모드 UI (1,238줄) |
| Test | `tests/test_health.py` | 28개 pytest (API + seed 무결성) |
| Script | `scripts/crawl_b2b.py` | 웹크롤러 (requests + BeautifulSoup) |
| Script | `scripts/validate_feedback.py` | 피드백 품질 검증 |
| Data | `data/crawled/` | 10개 페이지 크롤링 데이터 (JSON + report) |
| Docs | `docs/00~60` | 문서 7개 + 크롤링 분석 |

### 유저스토리 완료 현황 (25/25)

| 범위 | 유저스토리 | 상태 |
|------|-----------|------|
| Slice 1: DB, API, 대시보드 | US-001 ~ US-007 | ✅ 완료 |
| Slice 2: 학습 화면 3패턴 | US-008 ~ US-013 | ✅ 완료 |
| Slice 3: 평가, 진도, Stage 해제 | US-014 ~ US-017 | ✅ 완료 |
| Slice 4: 콘텐츠, 네비게이션, 시간, 북마크 | US-018 ~ US-022 | ✅ 완료 |
| P2: 확장 미션, 관리자 통계, 다크모드 | US-023 ~ US-025 | ✅ 완료 |

---

## Phase 2 — 콘텐츠 확장 및 비주얼 강화 (진행 중)

### 사전 작업 (완료)

| 날짜 | 작업 | 산출물 | 상태 |
|------|------|--------|------|
| 2026-02-22 | materials/ 3개 소스 문서 분석 | 콘텐츠 매핑 | ✅ 완료 |
| 2026-02-22 | b2b.fastcampus.co.kr 웹크롤링 | `data/crawled/` (10개 JSON) | ✅ 완료 |
| 2026-02-22 | 크롤링 분석 + Stage 3~5 계획서 | `docs/60-crawl-analysis-and-stage3-plan.md` | ✅ 완료 |
| 2026-02-22 | 상세 콘텐츠 개발 계획 | `docs/70-content-dev-plan.md` | ✅ 완료 |
| 2026-02-22 | Phase 2 백로그 작성 (US-026~035) | `docs/40-backlog.md` 업데이트 | ✅ 완료 |
| 2026-02-22 | 진행 현황 문서 작성 | `docs/80-progress.md` | ✅ 완료 |

### 구현 계획

| Slice | 작업 | 유저스토리 | 변경 파일 | 상태 |
|-------|------|-----------|----------|------|
| 5 | CSS 비주얼 컴포넌트 6종 | US-026 | `style.css` | ✅ 완료 (2026-02-22) |
| 6 | Stage 1-2 비주얼 보강 | US-027, US-028 | `seed.py` | ✅ 완료 (2026-02-22) |
| 7 | Stage 3 신규 (구조화데이터, 7모듈) | US-029 | `seed.py` | ✅ 완료 (2026-02-22) |
| 8 | Stage 4 신규 (오프사이트, 7모듈) | US-030 | `seed.py` | ✅ 완료 (2026-02-22) |
| 9 | Stage 5 신규 (측정/실험, 7모듈) | US-031 | `seed.py` | ✅ 완료 (2026-02-22) |
| 10 | 검증 및 QA | US-032~035 | `tests/`, `main.py` | ✅ 완료 (2026-02-22) |
| 11 | Stage 6 과업 캡스톤 신규 + 검증 | US-036 | `seed.py`, `tests/test_phase2.py` | ✅ 완료 (2026-02-22) |

### 핵심 기술 접근법

1. **비주얼 컴포넌트**: `marked.js` 인라인 HTML 렌더링 → CSS만 추가, `app.js` 수정 불필요
2. **6종 컴포넌트**: browser-mockup, compare-cards, diagram-box, callout, code-example, hierarchy-box
3. **다크모드**: `[data-theme="dark"]` CSS 오버라이드 전 컴포넌트 적용
4. **데이터 활용**: `materials/` 원본 + `data/crawled/` 실제 크롤링 → 실전 기반 교육

---

## 크롤링 데이터 활용 현황

### 크롤링 요약

| 항목 | 수치 |
|------|------|
| 크롤링 날짜 | 2026-02-21 |
| 크롤링 페이지 | 10개 (6 seed + 4 discovered) |
| 내부 링크 | 33개 |
| 외부 링크 | 43개 |
| 구조화 데이터 있는 페이지 | 4/10 |
| 구조화 데이터 없는 페이지 | 6/10 |

### 교육적 활용

| 발견사항 | 교육 활용 모듈 | 비주얼 유형 |
|---------|-------------|-----------|
| 6/10 CSR 빈 페이지 (244자) | M1-7, M2-3 | 브라우저 목업 (Before) |
| 내부링크 3.3개/페이지 | M2-1, M2-6 | 다이어그램 |
| 스키마 오용 (Course→Contact) | M3-5, M3-6 | 비교 카드 |
| SSR 페이지 4개 (A등급) | M1-7 | 비교 카드 (After) |
| BreadcrumbList 0개 | M3-2 | 코드 예시 (직접 설계) |
| H1 태그 없음 (6/10) | M2-5 | 계층구조 박스 |

---

## 주요 결정사항 요약

| # | 결정 | 이유 | 시점 |
|---|------|------|------|
| D1 | LLM 미사용, 선택지 기반 | 예측 가능한 학습 경험 | Phase 1 |
| D2 | 단일 사용자 (default) | 인증 불필요, 복잡도 축소 | Phase 1 |
| D3 | Hash-based SPA | 빌드 도구 불필요 | Phase 1 |
| D4 | SQLite 단일 파일 DB | 배포 간단 | Phase 1 |
| D5 | marked.js CDN | 마크다운 렌더링 안정 | Phase 1 |
| D6 | CSS 인라인 HTML 비주얼 | app.js 수정 없이 시각화 | Phase 2 |
| D7 | Stage 순차 해제 (70%) | 학습 동기 + 단계적 진행 | Phase 1 |
| D8 | 크롤링 데이터 교육 활용 | 실전 기반 학습 소재 | Phase 2 |

---

## 다음 단계

### Phase 2 구현 완료

- [x] **Slice 5**: CSS 비주얼 컴포넌트 6종 추가 (US-026) ✅
- [x] **Slice 6**: Stage 1-2 reading 스텝 비주얼 보강 (US-027, US-028) ✅
- [x] **Slice 7**: Stage 3 신규 개발 (US-029) ✅
- [x] **Slice 8**: Stage 4 신규 개발 (US-030) ✅
- [x] **Slice 9**: Stage 5 신규 개발 (US-031) ✅
- [x] **Slice 10**: 검증 + QA (US-032~035) ✅
- [x] **Slice 11**: Stage 6 과업 캡스톤 개발 + 검증 (US-036) ✅

### 향후 고려사항

- 프로덕션 배포 준비 (CORS 제한, 에러 로깅 강화)
- 다중 사용자 인증 시스템 (필요 시)
- 주기적 크롤링 자동화 (변경 추적)
- Stage 7+ 고급 과정 기획 (필요 시)
