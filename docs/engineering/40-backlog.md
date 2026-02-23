# 40 — Backlog

## 개요

총 25개 유저스토리. Slice 1~4 순서로 P0 → P1 순으로 우선순위 배정.
각 스토리는 **세로 슬라이스(최소 E2E)** 원칙으로 설계하여, 각 Slice 완료 시 작동하는 feature 제공.

### 완료 현황

| 항목 | 상태 | 완료일 |
|------|------|--------|
| US-001 ~ US-007 (Slice 1) | [x] 완료 | 2026-02-21 |
| US-008 ~ US-013 (Slice 2) | [x] 완료 | 2026-02-21 |
| US-014 ~ US-017 (Slice 3) | [x] 완료 | 2026-02-21 |
| US-018 (Slice 4 - practice steps) | [x] 부분 완료 | 2026-02-21 |
| US-019 (피드백 품질 검증) | [x] 완료 | 2026-02-21 |
| US-020 (네비게이션 개선) | [x] 완료 | 2026-02-21 |
| US-021 (학습 시간 기록) | [x] 완료 | 2026-02-21 |
| US-022 (북마크 기능) | [x] 완료 | 2026-02-21 |
| US-023 (확장 미션 카드) | [x] 완료 | 2026-02-21 |
| US-024 (학습 통계 대시보드) | [x] 완료 | 2026-02-21 |
| US-025 (Dark Mode) | [x] 완료 | 2026-02-21 |

---

## P0 — Slice 1: DB + Stage/Module API + 대시보드

### 데이터베이스 및 시딩

#### US-001: 데이터베이스 테이블 설계 및 생성

- **As a** backend engineer
- **I want** SQLite에 stages, modules, steps, options, user_progress 테이블을 생성하고
- **So that** 단계적 학습 구조를 데이터로 표현할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: stages 테이블 (id, title, description, unlock_condition, created_at)
- [ ] AC-2: modules 테이블 (id, stage_id, title, order, created_at)
- [ ] AC-3: steps 테이블 (id, module_id, type[read/quiz/practice], content, order, created_at)
- [ ] AC-4: options 테이블 (id, step_id, text, is_correct, feedback, order)
- [ ] AC-5: user_progress 테이블 (id, stage_id, module_id, step_id, selected_option_id, timestamp)
- [ ] AC-6: 복합 인덱스 생성 (user_id+module_id, stage_id+module_id)
- [ ] AC-7: db/schema.sql 파일 생성, 프로젝트에 포함

**Definition of Done:**
- [ ] SQLite 스키마 검증 (sqlite3 테스트)
- [ ] 초기 마이그레이션 스크립트 실행 확인
- [ ] 관계도(ERD) 문서화
- [ ] 코드 리뷰 완료

**Priority:** P0

**Slice:** 1

---

#### US-002: Stage 1 Seed 데이터 작성 (8개 모듈, ~40개 Step)

- **As a** content curator
- **I want** materials/ 폴더 내 3개 문서에서 GEO 개념을 큐레이션하여 Stage 1의 8개 모듈 정의를 JSON으로 작성하고
- **So that** 학습자가 GEO 세계관을 단계별로 이해할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: M1-1~M1-8 모든 모듈이 modules 테이블에 삽입됨
- [ ] AC-2: 각 모듈당 평균 5개 Step (총 40개 이상) 포함
- [ ] AC-3: 각 Step마다 최소 2개 이상의 선택지(options) 정의
- [ ] AC-4: 정답 선택지에 40~100자 길이의 피드백 작성
- [ ] AC-5: 모든 Step type 포함 (read/quiz/practice 각각 최소 1개)
- [ ] AC-6: M1-8(종합평가) 정답율 계산 로직 정의 (8개 선택지 모두 정답 시 70% 기준 만족)
- [ ] AC-7: seed_data/stage1.json 또는 SQL INSERT 스크립트 준비

**Definition of Done:**
- [ ] 콘텐츠 담당자 검수 완료
- [ ] 모든 Step이 DB에 INSERT됨
- [ ] GET /api/stages/1/modules 요청으로 8개 모듈 확인 가능
- [ ] 링크/이미지 경로 유효성 검사

**Priority:** P0

**Slice:** 1

---

### Backend API

#### US-003: Health Check API 구현

- **As a** frontend developer
- **I want** GET /api/health 엔드포인트가 서버 상태를 반환하고
- **So that** 서버가 정상 작동하는지 빠르게 확인할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: GET /api/health 응답 < 100ms
- [ ] AC-2: 응답 형식: `{"status": "ok", "timestamp": "2026-02-21T10:00:00Z"}`
- [ ] AC-3: 상태 코드 200 반환

**Definition of Done:**
- [ ] curl로 테스트 완료
- [ ] 단위 테스트 작성 (tests/test_health.py)
- [ ] 로깅 추가

**Priority:** P0

**Slice:** 1

---

#### US-004: Stages API 구현

- **As a** frontend developer
- **I want** GET /api/stages 엔드포인트가 모든 Stage 메타데이터와 진도 상태를 반환하고
- **So that** 대시보드에서 Stage 목록과 해제 상태를 표시할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 응답 형식:
  ```json
  {
    "stages": [
      {
        "id": 1,
        "title": "GEO 세계관 이해",
        "description": "...",
        "is_unlocked": true,
        "progress": 0.25,
        "module_count": 8
      }
    ]
  }
  ```
- [ ] AC-2: progress = (완료한 모듈 수 / 전체 모듈 수) × 100
- [ ] AC-3: Stage 1은 기본 해제, Stage 2는 unlock_condition 확인
- [ ] AC-4: 응답 시간 < 500ms

**Definition of Done:**
- [ ] 단위 테스트 작성 (tests/test_stages.py)
- [ ] user_progress 테이블과 조인 쿼리 검증
- [ ] 코드 리뷰 완료

**Priority:** P0

**Slice:** 1

---

#### US-005: Modules API 구현

- **As a** frontend developer
- **I want** GET /api/stages/{stage_id}/modules 엔드포인트가 특정 Stage 내 모듈 목록을 반환하고
- **So that** 모듈 목록 화면을 렌더링할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 응답 형식:
  ```json
  {
    "stage_id": 1,
    "modules": [
      {
        "id": 101,
        "title": "GEO 정의",
        "order": 1,
        "is_completed": false,
        "step_count": 5
      }
    ]
  }
  ```
- [ ] AC-2: modules는 order 순서로 정렬
- [ ] AC-3: is_completed는 user_progress 테이블 확인
- [ ] AC-4: 응답 시간 < 500ms

**Definition of Done:**
- [ ] 단위 테스트 작성 (tests/test_modules.py)
- [ ] Stage ID 유효성 검사
- [ ] 코드 리뷰 완료

**Priority:** P0

**Slice:** 1

---

### Frontend — 대시보드

#### US-006: 대시보드 화면 구현

- **As a** learner
- **I want** 애플리케이션 진입 시 Stage별 진도 바와 현재 위치를 한눈에 볼 수 있고
- **So that** 다음에 무엇을 학습할지 명확하게 알 수 있다

**Acceptance Criteria:**
- [ ] AC-1: Stage 1 진도 바 표시 (완료한 모듈 비율)
- [ ] AC-2: Stage 2 진도 바 (해제 안 됨 시 "Stage 1 완료 후 해제" 메시지)
- [ ] AC-3: 현재 학습 중인 모듈 표시 (예: "M1-3: RAG 5단계 진행 중")
- [ ] AC-4: "계속하기" 버튼 → 마지막 미완료 Step으로 이동
- [ ] AC-5: "Stage 1 둘러보기" 버튼 → 모듈 목록 화면으로 이동
- [ ] AC-6: 모바일 미지원 배너 (데스크톱 권장)
- [ ] AC-7: 로드 시간 < 1초

**Definition of Done:**
- [ ] HTML/CSS/JS 구현 (앱/웹/index.html)
- [ ] GET /api/progress 호출로 데이터 로드
- [ ] 시각적 디자인 검토 완료
- [ ] 수동 테스트 체크리스트 (tests/manual_dashboard.md)

**Priority:** P0

**Slice:** 1

---

#### US-007: 모듈 목록 화면 구현

- **As a** learner
- **I want** Stage 내 모듈을 목록으로 보고, 각 모듈의 완료 상태를 확인할 수 있으며
- **So that** 원하는 모듈로 직접 이동할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 모듈 리스트 표시 (순서대로, 완료/진행중/잠금 상태 아이콘)
- [ ] AC-2: 잠금된 모듈은 클릭 불가 (시각적 피드백)
- [ ] AC-3: 각 모듈 클릭 → 첫 Step으로 이동
- [ ] AC-4: 뒤로가기 버튼 → 대시보드로 복귀
- [ ] AC-5: GET /api/stages/{stage_id}/modules 호출로 데이터 로드
- [ ] AC-6: 로드 시간 < 500ms

**Definition of Done:**
- [ ] HTML/CSS/JS 구현 (앱/웹/modules.html)
- [ ] 상태 아이콘 디자인 완료
- [ ] 수동 테스트 체크리스트

**Priority:** P0

**Slice:** 1

---

## P0 — Slice 2: Step 학습 화면 (읽기/퀴즈/실습)

### Backend API

#### US-008: Module 상세 API 구현

- **As a** frontend developer
- **I want** GET /api/modules/{module_id} 엔드포인트가 모듈의 모든 Step과 선택지를 반환하고
- **So that** 학습 화면에 콘텐츠를 로드할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 응답 형식 (module + steps + options):
  ```json
  {
    "id": 101,
    "title": "GEO 정의",
    "steps": [
      {
        "id": 1001,
        "type": "read",
        "content": "GEO는...",
        "options": null
      },
      {
        "id": 1002,
        "type": "quiz",
        "content": "GEO는 무엇인가?",
        "options": [
          {"id": 5001, "text": "선택지 A"},
          {"id": 5002, "text": "선택지 B"}
        ]
      }
    ]
  }
  ```
- [ ] AC-2: type이 "read"면 options 없음 (null)
- [ ] AC-3: type이 "quiz" 또는 "practice"면 options 포함 (is_correct 제외)
- [ ] AC-4: steps는 order 순서로 정렬
- [ ] AC-5: 응답 시간 < 500ms

**Definition of Done:**
- [ ] 단위 테스트 작성
- [ ] options 응답에서 is_correct 필터링 확인 (안 보이도록)
- [ ] 코드 리뷰 완료

**Priority:** P0

**Slice:** 2

---

#### US-009: Step 선택지 제출 API 구현

- **As a** frontend developer
- **I want** POST /api/steps/{step_id}/answer 엔드포인트로 선택지를 제출하고 피드백을 받으며
- **So that** 사용자가 선택 후 즉시 피드백을 확인할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 요청 형식: `{"option_id": 5002}`
- [ ] AC-2: 응답 형식:
  ```json
  {
    "is_correct": true,
    "feedback": "정답입니다. GEO는...",
    "explanation": null,
    "next_action": "continue"
  }
  ```
- [ ] AC-3: is_correct = option.is_correct 값 반환
- [ ] AC-4: feedback = option.feedback 반환
- [ ] AC-5: 선택 기록을 user_progress 테이블에 INSERT
- [ ] AC-6: next_action: "continue" (다음 Step 있음) 또는 "complete" (모듈 완료) 또는 "unlock_stage" (Stage 2 해제)
- [ ] AC-7: 응답 시간 < 1000ms

**Definition of Done:**
- [ ] 단위 테스트 작성 (정답/오답 경우 모두)
- [ ] user_progress INSERT 검증
- [ ] 트랜잭션 처리 (중복 제출 방지)
- [ ] 코드 리뷰 완료

**Priority:** P0

**Slice:** 2

---

#### US-010: Progress 조회 API 구현

- **As a** frontend developer
- **I want** GET /api/progress 엔드포인트가 사용자의 현재 진도 상태를 반환하고
- **So that** 대시보드와 학습 화면에 진도 정보를 표시할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 응답 형식:
  ```json
  {
    "current_stage_id": 1,
    "current_module_id": 103,
    "current_step_id": 1005,
    "total_modules": 16,
    "completed_modules": 3,
    "stage_1_progress": 37.5,
    "stage_2_unlocked": false,
    "last_visited": "2026-02-21T14:30:00Z"
  }
  ```
- [ ] AC-2: current_step_id = 가장 최근의 미완료 Step (또는 마지막 완료 Step)
- [ ] AC-3: progress = (completed_modules / total_modules) × 100
- [ ] AC-4: stage_2_unlocked = Stage 1-8 정답율 >= 70%인지 판정
- [ ] AC-5: 응답 시간 < 500ms

**Definition of Done:**
- [ ] 단위 테스트 작성
- [ ] user_progress 집계 쿼리 최적화 (인덱스 활용)
- [ ] 코드 리뷰 완료

**Priority:** P0

**Slice:** 2

---

### Frontend — 학습 화면

#### US-011: Step 읽기 카드 화면 (패턴 A)

- **As a** learner
- **I want** type이 "read"인 Step에서 마크다운 콘텐츠를 읽고 "다음" 버튼을 클릭해 진행하고
- **So that** 이론 콘텐츠를 천천히 학습할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 마크다운 콘텐츠 렌더링 (제목, 텍스트, 불릿 포인트)
- [ ] AC-2: 콘텐츠 위 "모듈: M1-1 / Step 1/5" 표시
- [ ] AC-3: "이전" 버튼 (이전 Step 또는 모듈 목록)
- [ ] AC-4: "다음" 버튼 (다음 Step)
- [ ] AC-5: 버튼 클릭 → GET /api/modules/{module_id}/steps 호출 → 다음 Step 콘텐츠 로드
- [ ] AC-6: 로드 시간 < 1초
- [ ] AC-7: 모바일 반응형 고려하지 않음 (데스크톱만)

**Definition of Done:**
- [ ] HTML/CSS/JS 구현 (앱/웹/learn.html)
- [ ] 마크다운 파서 선택 (marked.js 권장)
- [ ] 수동 테스트 체크리스트 (앞/뒤로 3회 반복)

**Priority:** P0

**Slice:** 2

---

#### US-012: Step 선택 퀴즈 화면 (패턴 B)

- **As a** learner
- **I want** type이 "quiz"인 Step에서 4지선다 또는 O×X를 선택하고 정답 확인 + 피드백을 받으며
- **So that** 이해도를 점검하고 학습을 강화할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 퀴즈 질문 표시
- [ ] AC-2: 선택지 4개를 라디오 버튼 또는 버튼으로 표시
- [ ] AC-3: "제출" 버튼 클릭 → POST /api/steps/{step_id}/answer 호출
- [ ] AC-4: 응답 받으면 선택한 옵션을 하이라이트 + is_correct에 따라 색상 변경 (초록/빨강)
- [ ] AC-5: 피드백 텍스트 표시 (40~100자)
- [ ] AC-6: 정답인 경우: "다음으로" 버튼 활성화
- [ ] AC-7: 오답인 경우: "다시 풀기" 버튼 또는 "피드백 보기" 후 진행 옵션
- [ ] AC-8: 선택지 순서는 랜덤 X (고정 순서)

**Definition of Done:**
- [ ] HTML/CSS/JS 구현
- [ ] 색상 스키마 정의 (정답: 초록, 오답: 빨강)
- [ ] 수동 테스트 (정답/오답 경우 모두)

**Priority:** P0

**Slice:** 2

---

#### US-013: Step 다단계 실습 화면 (패턴 C)

- **As a** learner
- **I want** type이 "practice"인 Step에서 2~3단계로 나누어 선택하고, 조합 결과를 본 후 전문가 분석과 비교하고
- **So that** 단순한 선택이 아닌 실습 경험을 할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: Step 1: 첫 번째 선택지 제시 (예: "다음 중 IA 개념으로 맞는 것은?")
- [ ] AC-2: Step 1 선택 후 조건부 Step 2 표시 (선택에 따라 다른 질문)
- [ ] AC-3: Step 2 선택 후 결과 화면 (조합된 의미 설명)
- [ ] AC-4: 결과 아래 "전문가 분석" 섹션 (모범답안과 나의 답 비교)
- [ ] AC-5: 각 단계마다 선택 기록 (user_progress에 모두 저장)
- [ ] AC-6: "다음으로" 또는 "다시 풀기" 옵션

**Definition of Done:**
- [ ] HTML/CSS/JS 구현 (조건부 렌더링 처리)
- [ ] 다단계 데이터 구조 설계 (nested options)
- [ ] 수동 테스트 (2단계, 3단계 시나리오 모두)

**Priority:** P0

**Slice:** 2

---

## P0 — Slice 3: 진도 관리 + Stage 해제

### Backend API

#### US-014: Stage 평가 API 구현

- **As a** backend engineer
- **I want** POST /api/stages/{stage_id}/evaluate 엔드포인트가 특정 Stage의 종합평가(M-8) 정답율을 계산하고 Stage 해제를 판정하며
- **So that** 학습자의 성취도를 기반으로 다음 Stage 진행을 결정할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 요청 형식: `{"stage_id": 1}`
- [ ] AC-2: 응답 형식:
  ```json
  {
    "stage_id": 1,
    "correct_count": 7,
    "total_count": 8,
    "accuracy": 87.5,
    "passed": true,
    "unlocked_stage_id": 2,
    "message": "축하합니다! Stage 2가 해제되었습니다."
  }
  ```
- [ ] AC-3: accuracy = (correct_count / total_count) × 100
- [ ] AC-4: passed = (accuracy >= 70%) ? true : false
- [ ] AC-5: passed=true이고 stage_id=1이면 unlocked_stage_id=2
- [ ] AC-6: stages 테이블의 unlock_condition 업데이트
- [ ] AC-7: 응답 시간 < 1000ms

**Definition of Done:**
- [ ] 단위 테스트 작성 (passed/failed 경우 모두)
- [ ] 데이터 무결성 검증 (잘못된 stage_id 처리)
- [ ] 코드 리뷰 완료

**Priority:** P0

**Slice:** 3

---

### Frontend — 결과 화면 및 진도 관리

#### US-015: 종합평가 결과 화면 구현

- **As a** learner
- **I want** 종합평가(M1-8)를 완료한 후 정답율과 해제 여부를 한눈에 볼 수 있고
- **So that** 성취감을 느끼고 다음 단계로 자연스럽게 진행할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 정답율 큰 숫자로 표시 (예: "75%")
- [ ] AC-2: 결과 메시지 (passed: "축하합니다!" / failed: "다시 한 번 도전해보세요")
- [ ] AC-3: passed=true면 "Stage 2 시작하기" 버튼 활성화
- [ ] AC-4: passed=false면 "M1-8 다시 풀기" 또는 "약한 부분 복습" 버튼
- [ ] AC-5: 정답/오답 항목별 요약 (선택사항, P1)
- [ ] AC-6: 뒤로가기 → 대시보드 복귀

**Definition of Done:**
- [ ] HTML/CSS/JS 구현 (앱/웹/result.html)
- [ ] POST /api/stages/{stage_id}/evaluate 호출
- [ ] 색상 스키마 (passed: 초록, failed: 주황)
- [ ] 수동 테스트

**Priority:** P0

**Slice:** 3

---

#### US-016: Progress 실시간 업데이트 (Frontend)

- **As a** learner
- **I want** 매 Step 선택 후 대시보드로 돌아가도 진도가 자동으로 업데이트되고
- **So that** 학습 중단 후 재개할 때 정확한 위치에서 시작할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: POST /api/steps/{step_id}/answer 성공 → 로컬 상태 업데이트
- [ ] AC-2: 대시보드 재진입 시 GET /api/progress 호출 → 서버 상태 동기화
- [ ] AC-3: user_progress 테이블에 모든 선택이 기록됨 (검증 쿼리)
- [ ] AC-4: 진도 바(progress %) 실시간 반영

**Definition of Done:**
- [ ] 브라우저 로컬스토리지 활용 (또는 서버 상태만)
- [ ] 단위 테스트 (progress 조회)
- [ ] 통합 테스트 (선택 → 대시보드 → 진도 확인)

**Priority:** P0

**Slice:** 3

---

#### US-017: Stage 해제 UI 업데이트

- **As a** learner
- **I want** Stage 2가 해제되면 대시보드에서 "잠금" 상태가 "진행 가능"으로 바뀌고
- **So that** Stage 2 모듈로 바로 진입할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: Stage 2 초기 상태: 진행 불가(회색 + 잠금 아이콘)
- [ ] AC-2: M1-8 정답율 >= 70% → 대시보드 새로고침 시 Stage 2 활성화
- [ ] AC-3: Stage 2 클릭 가능 (모듈 목록 화면 진입)
- [ ] AC-4: Stage 1 진도 바: 100% 표시
- [ ] AC-5: Stage 2 진도 바: 0% 표시 (아직 시작 안 함)

**Definition of Done:**
- [ ] GET /api/progress에서 stage_2_unlocked 값 확인
- [ ] CSS 상태별 스타일 정의 (active/disabled/completed)
- [ ] 수동 테스트 (전체 E2E)

**Priority:** P0

**Slice:** 3

---

## P1 — Slice 4: Seed 데이터 큐레이션 및 콘텐츠 완성

### 콘텐츠 큐레이션

#### US-018: Stage 2 Seed 데이터 작성 (8개 모듈, ~40개 Step)

- **As a** content curator
- **I want** Stage 2의 8개 모듈(M2-1~M2-8)을 Technical GEO 기초 실습으로 설계하고
- **So that** 이론을 기반으로 실무 기초 스킬을 익힐 수 있다

**Acceptance Criteria:**
- [ ] AC-1: M2-1~M2-8 모든 모듈이 modules 테이블에 삽입됨
- [ ] AC-2: 각 모듈당 평균 5개 Step (총 40개 이상)
- [ ] AC-3: 읽기(패턴 A) / 퀴즈(패턴 B) / 실습(패턴 C) 적절히 섞여 있음
- [ ] AC-4: 모든 Step의 피드백 작성 (40~100자)
- [ ] AC-5: M2-8(종합평가) 정의 (실습 기반 8개 선택지)
- [ ] AC-6: seed_data/stage2.json 또는 SQL INSERT 스크립트 준비

**Definition of Done:**
- [ ] 콘텐츠 담당자 검수 완료
- [ ] 모든 Step이 DB에 INSERT됨
- [ ] GET /api/stages/2/modules 요청으로 8개 모듈 확인 가능

**Priority:** P1

**Slice:** 4

---

#### US-019: 피드백 텍스트 품질 검증

- **As a** content curator
- **I want** 모든 Step의 피드백 텍스트가 일관된 수준과 길이를 유지하도록 검증하고
- **So that** 학습자 경험을 균일하게 유지할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 모든 피드백이 40~100자 범위 내 (극단적 길이 피하기)
- [ ] AC-2: 피드백에 핵심 이유 포함 ("~이기 때문에")
- [ ] AC-3: 피드백 어조 일관성 (존댓말 or 반말 통일)
- [ ] AC-4: 오답 피드백도 격려 + 힌트 포함
- [ ] AC-5: 검증 결과 리포트 (피드백 텍스트 분석)

**Definition of Done:**
- [ ] 수동 검수 체크리스트 (tests/feedback_checklist.md)
- [ ] 피드백 통계 (평균 길이, 분포도)
- [ ] 수정 사항 모두 DB에 반영

**Priority:** P1

**Slice:** 4

---

### 추가 기능 (P1)

#### US-020: 모듈 간 네비게이션 개선

- **As a** learner
- **I want** 모듈을 마친 후 자동으로 다음 모듈의 첫 Step으로 이동하거나, "다음 모듈" 버튼으로 쉽게 진입하고
- **So that** 끊김 없이 학습을 계속할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: M1-8 완료 후 자동으로 Stage 2 해제 화면 표시
- [ ] AC-2: 각 모듈 마지막 Step 후 "다음 모듈" 버튼 제공
- [ ] AC-3: 마지막 모듈(M2-8)이면 "완료" 또는 "대시보드"로 이동

**Definition of Done:**
- [ ] 프론트엔드 로직 구현
- [ ] 수동 테스트 (모듈 체이닝)

**Priority:** P1

**Slice:** 4

---

#### US-021: 학습 시간 기록 (선택사항)

- **As a** instructor
- **I want** 각 사용자의 Step별 소요 시간을 기록할 수 있으면
- **So that** 나중에 학습 분석에 활용할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: user_progress에 time_spent_seconds 칼럼 추가
- [ ] AC-2: Step 진입 시 시간 기록, 선택 제출 시 경과시간 계산
- [ ] AC-3: 모듈/Stage별 총 소요 시간 조회 API (추후 대시보드에서 활용)

**Definition of Done:**
- [ ] DB 마이그레이션
- [ ] 프론트엔드 타이머 로직

**Priority:** P1

---

#### US-022: 북마크 / 저장 기능 (선택사항)

- **As a** learner
- **I want** 중요한 Step을 북마크해두고 나중에 다시 찾을 수 있으면
- **So that** 복습이 쉬워진다

**Acceptance Criteria:**
- [ ] AC-1: 각 Step 우측에 별 아이콘 (북마크)
- [ ] AC-2: 북마크한 Step 목록 조회 (대시보드 또는 별도 페이지)
- [ ] AC-3: user_bookmarks 테이블 신규 생성

**Definition of Done:**
- [ ] DB 스키마 확장
- [ ] API 추가 (POST /api/bookmarks, GET /api/bookmarks)
- [ ] 프론트엔드 북마크 UI

**Priority:** P1

---

## P2 — Nice to Have

#### US-023: 확장 미션 카드

- **As a** learner
- **I want** 일부 Step 아래에 "더 알아보기" 같은 확장 미션이 있어서
- **So that** 심화 학습에 관심 있는 사용자가 더 탐구할 수 있다

**Priority:** P2

**Slice:** 이후

---

#### US-024: 학습 통계 대시보드 (관리자용)

- **As a** instructor
- **I want** 모든 사용자의 학습 진도, 정답율, 취약 모듈을 한눈에 볼 수 있는 대시보드가 있으면
- **So that** 사용자별 피드백 및 커리큘럼 개선을 할 수 있다

**Priority:** P2

**Slice:** 이후

---

#### US-025: Dark Mode 지원

- **As a** learner
- **I want** 야간 모드 옵션이 있으면
- **So that** 밤에 편하게 학습할 수 있다

**Priority:** P2

**Slice:** 이후

---

## 우선순위 요약

| Slice | 우선순위 | 유저스토리 | 담당 | 예상 기간 |
|-------|----------|-----------|------|----------|
| 1 | P0 | US-001, US-002, US-003, US-004, US-005, US-006, US-007 | backend-dev, frontend-dev, content-curator | 1주 |
| 2 | P0 | US-008, US-009, US-010, US-011, US-012, US-013 | backend-dev, frontend-dev | 1.5주 |
| 3 | P0 | US-014, US-015, US-016, US-017 | backend-dev, frontend-dev | 1주 |
| 4 | P1 | US-018, US-019, US-020, US-021, US-022 | content-curator, frontend-dev, backend-dev | 1주 |
| — | P2 | US-023, US-024, US-025 | TBD | 이후 |

---

## 요약

**총 25개 유저스토리** (P0: 17개, P1: 8개, P2: 3개)

**P0 주요 경로 (Slice 1~3):**
1. DB 설계 + Seed 데이터 (Stage 1)
2. 5개 API (Stages, Modules, Module Detail, Answer, Progress)
3. 2개 대시보드 화면 (대시보드, 모듈 목록)
4. 3개 학습 화면 (읽기, 퀴즈, 실습)
5. 1개 평가 API + 결과 화면
6. 진도 관리 + Stage 해제

**P1 (Slice 4):**
- Stage 2 Seed 데이터
- 피드백 품질 검증
- 네비게이션 개선, 학습 시간 기록, 북마크 기능

**P2 (이후):**
- 확장 미션, 통계 대시보드, Dark Mode

---

## DoD (Definition of Done) 공통 기준

모든 유저스토리 완료 시:
- [ ] 코드 구현 완료
- [ ] 단위 테스트 작성 및 통과 (backend), 수동 테스트 체크리스트 (frontend)
- [ ] 코드 리뷰 완료
- [ ] 해당 docs 파일 업데이트 (30-architecture.md 등)
- [ ] Git commit 메시지 작성 (US-XXX: [타이틀])

---
---

# Phase 2 — 콘텐츠 확장 및 비주얼 강화

## 개요

Phase 1(US-001~025) 완료 후, Stage 1~2 비주얼 보강 + Stage 3~5 신규 커리큘럼 개발.
총 10개 유저스토리 (US-026 ~ US-035). Slice 5~10 순서로 P0 → P1 배정.

### 완료 현황 (Phase 2)

| 항목 | 상태 | 완료일 |
|------|------|--------|
| US-026 (CSS 비주얼 컴포넌트) | [x] 완료 | 2026-02-22 |
| US-027 (Stage 1 비주얼 보강) | [x] 완료 | 2026-02-22 |
| US-028 (Stage 2 비주얼 보강) | [x] 완료 | 2026-02-22 |
| US-029 (Stage 3 신규) | [x] 완료 | 2026-02-22 |
| US-030 (Stage 4 신규) | [x] 완료 | 2026-02-22 |
| US-031 (Stage 5 신규) | [x] 완료 | 2026-02-22 |
| US-032 (Stage 해제 로직 확장) | [x] 완료 | 2026-02-22 |
| US-033 (비주얼 다크모드 검증) | [x] 완료 | 2026-02-22 |
| US-034 (QA 통합 테스트) | [x] 완료 | 2026-02-22 |
| US-035 (피드백 품질 검증 Phase 2) | [x] 완료 | 2026-02-22 |

---

## P0 — Slice 5: CSS 비주얼 컴포넌트 시스템

#### US-026: CSS 비주얼 컴포넌트 시스템 구축

- **As a** frontend developer
- **I want** 6종 비주얼 컴포넌트(브라우저 목업, Before/After 비교, 다이어그램, 콜아웃, 코드 예시, 계층구조)의 CSS 클래스를 추가하고
- **So that** seed.py의 content_md에 인라인 HTML을 삽입해 시각적 학습 자료를 렌더링할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: `.browser-mockup` — 주소창(dot 3개 + URL) + body + page-element(present/missing)
- [ ] AC-2: `.compare-cards` — before(빨강 상단) / after(초록 상단) 나란히 비교 레이아웃
- [ ] AC-3: `.diagram-box` — 중앙 정렬 다이어그램 박스 + title + pre 텍스트
- [ ] AC-4: `.callout` — tip/warning/key-point/hint 4종 + ::before 아이콘(💡⚠️🎯🔍)
- [ ] AC-5: `.code-example` — 라벨 헤더 + pre 코드 블록
- [ ] AC-6: `.hierarchy-box` — level-1/2/3 들여쓰기 계층 표시
- [ ] AC-7: `[data-theme="dark"]` 다크모드 오버라이드 전 컴포넌트 적용 (~100줄)
- [ ] AC-8: `.reading-card img { max-width: 100% }` 기본 스타일

**Definition of Done:**
- [ ] `apps/web/css/style.css`에 ~400줄 추가
- [ ] 라이트/다크 모드 모두 렌더링 확인
- [ ] 기존 28개 pytest 회귀 테스트 통과

**Priority:** P0
**Slice:** 5
**변경 파일:** `apps/web/css/style.css`

---

## P0 — Slice 6: Stage 1~2 비주얼 보강

#### US-027: Stage 1 비주얼 콘텐츠 보강 (M1-1 ~ M1-7)

- **As a** learner
- **I want** Stage 1의 7개 reading 스텝에 브라우저 목업, 비교 카드, 다이어그램 등 시각 자료가 포함되어
- **So that** 텍스트만으로는 이해하기 어려운 GEO 개념을 직관적으로 파악할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: M1-1 (GEO란 무엇인가) — 브라우저 목업 2개 ("전통 검색 결과" vs "AI 답변 인용")
- [ ] AC-2: M1-2 (SEO vs GEO) — 비교 카드 (SEO 5요소 vs GEO 5요소)
- [ ] AC-3: M1-3 (RAG 5단계) — 다이어그램 (파이프라인) + 브라우저 목업 (query fan-out)
- [ ] AC-4: M1-4 (5대 신호) — 다이어그램 (피라미드) + 콜아웃 tip (신호별 한줄)
- [ ] AC-5: M1-5 (3층 KPI) — 다이어그램 (Visibility→Behavior→Authority 계단)
- [ ] AC-6: M1-6 (근거 vs 가설) — 비교 카드 (Proven vs Estimated)
- [ ] AC-7: M1-7 (전문가 시연) — 브라우저 목업 (크롤링 0/7점) + 비교 카드 (insight 7/7점)
- [ ] AC-8: 기존 quiz/practice 스텝 구조 변경 없음
- [ ] AC-9: extension_md 신규 추가 5개 이상

**Definition of Done:**
- [ ] `apps/api/seed.py` Stage 1 reading 스텝 content_md에 인라인 HTML 삽입
- [ ] 서버 재시작 후 브라우저에서 비주얼 렌더링 확인
- [ ] 다크모드 비주얼 색상 정상

**Priority:** P0
**Slice:** 6
**변경 파일:** `apps/api/seed.py`
**데이터 소스:** `materials/GEO 초보자 학습 가이드`, `data/crawled/`

---

#### US-028: Stage 2 비주얼 콘텐츠 보강 (M2-1 ~ M2-7)

- **As a** learner
- **I want** Stage 2의 7개 reading 스텝에 b2b.fastcampus.co.kr 실제 크롤링 데이터 기반 비주얼이 포함되어
- **So that** 실무에서 만나는 실제 웹사이트 문제를 시각적으로 이해하고 개선점을 파악할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: M2-1 (IA 개념) — 다이어그램 (현재 사이트 링크 구조, 3.3 링크/페이지)
- [ ] AC-2: M2-2 (허브-클러스터) — Before/After 비교 카드 (플랫 → 허브-클러스터)
- [ ] AC-3: M2-3 (Answer-first) — 브라우저 목업 2개 (Before 빈 페이지 → After 요약 추가)
- [ ] AC-4: M2-4 (FAQ 설계) — 코드 예시 (FAQPage JSON-LD) + 브라우저 목업
- [ ] AC-5: M2-5 (헤딩 재설계) — 비교 카드 + 계층구조 박스 (H1 없음 → 개선)
- [ ] AC-6: M2-6 (내부링크) — 다이어그램 (내부링크 맵) + 콜아웃 warning
- [ ] AC-7: M2-7 (80/20 판단) — 다이어그램 (우선순위 매트릭스) + 콜아웃 key-point
- [ ] AC-8: 기존 quiz/practice 스텝 변경 없음

**Definition of Done:**
- [ ] `apps/api/seed.py` Stage 2 reading 스텝 content_md에 인라인 HTML 삽입
- [ ] 크롤링 데이터(`data/crawled/`) 기반 실제 수치 반영
- [ ] 브라우저에서 Before/After 비주얼 정상 렌더링

**Priority:** P0
**Slice:** 6
**변경 파일:** `apps/api/seed.py`
**데이터 소스:** `data/crawled/_report.md`, `data/crawled/*.json`

---

## P0 — Slice 7: Stage 3 신규 개발

#### US-029: Stage 3 — 구조화데이터 & 스키마 마스터 (7모듈)

- **As a** learner
- **I want** JSON-LD, BreadcrumbList, Article, Event, FAQPage 등 구조화데이터를 단계별로 학습하고
- **So that** AI 엔진이 콘텐츠를 정확히 이해하도록 스키마를 설계할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: Stage 3 INSERT (`unlock_condition`: Stage 2 완료 + 70%)
- [ ] AC-2: M3-1 JSON-LD 기초 (1R + 2Q + 1P = 4스텝)
- [ ] AC-3: M3-2 BreadcrumbList 실습 (4스텝)
- [ ] AC-4: M3-3 Article & BlogPosting (4스텝)
- [ ] AC-5: M3-4 Event 스키마 (4스텝)
- [ ] AC-6: M3-5 FAQPage 스키마 (4스텝)
- [ ] AC-7: M3-6 스키마 검증 & 디버깅 (4스텝)
- [ ] AC-8: M3-7 종합 평가 (5Q)
- [ ] AC-9: 모든 reading 스텝에 코드 예시/브라우저 목업 비주얼 포함
- [ ] AC-10: 총 29스텝 + ~100옵션, 피드백 40자 이상

**Definition of Done:**
- [ ] `apps/api/seed.py`에 Stage 3 데이터 추가
- [ ] `GET /api/stages` → Stage 3 잠김 상태 반환
- [ ] Stage 2 평가 합격 후 Stage 3 해제 확인
- [ ] 비주얼 컴포넌트 정상 렌더링

**Priority:** P0
**Slice:** 7
**변경 파일:** `apps/api/seed.py`, `apps/api/database.py`
**데이터 소스:** `materials/GEO 심층 리서치 L3`, `data/crawled/` 스키마 데이터

---

## P0 — Slice 8: Stage 4 신규 개발

#### US-030: Stage 4 — 오프사이트 & 멘션 전략 (7모듈)

- **As a** learner
- **I want** 백링크, 브랜드 멘션, PR, 소셜 유통, 리뷰/디렉토리 전략을 체계적으로 학습하고
- **So that** 온사이트 GEO를 넘어 오프사이트 권위 신호를 구축할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: Stage 4 INSERT (`unlock_condition`: Stage 3 완료 + 70%)
- [ ] AC-2: M4-1 오프사이트 GEO 개요 (4스텝) — MECE 5갈래 다이어그램
- [ ] AC-3: M4-2 백링크 전략 (4스텝) — 링크 품질 피라미드
- [ ] AC-4: M4-3 브랜드 멘션 & PR (4스텝) — 멘션 비교 카드
- [ ] AC-5: M4-4 엔터티 & 권위 신호 (4스텝) — 엔터티 그래프
- [ ] AC-6: M4-5 소셜 유통 & 콘텐츠 확산 (4스텝) — UTM 예시
- [ ] AC-7: M4-6 리뷰 & 디렉토리 (4스텝) — B2B 사회적 증명
- [ ] AC-8: M4-7 종합 평가 (5Q)
- [ ] AC-9: 총 29스텝 + ~100옵션

**Definition of Done:**
- [ ] `apps/api/seed.py`에 Stage 4 데이터 추가
- [ ] Stage 3 → 4 해제 로직 검증
- [ ] 비주얼 컴포넌트 정상 렌더링

**Priority:** P0
**Slice:** 8
**변경 파일:** `apps/api/seed.py`
**데이터 소스:** `materials/GEO 심층 리서치 오프사이트 섹션`

---

## P0 — Slice 9: Stage 5 신규 개발

#### US-031: Stage 5 — 측정 & 실험 설계 실전 (7모듈)

- **As a** learner
- **I want** KPI 3층, GSC/GA4 활용, AI Validator, 가설 실험, 90일 로드맵을 실전 수준으로 학습하고
- **So that** GEO 전략의 효과를 측정하고 체계적으로 개선할 수 있다

**Acceptance Criteria:**
- [ ] AC-1: Stage 5 INSERT (`unlock_condition`: Stage 4 완료 + 70%)
- [ ] AC-2: M5-1 KPI 3층 프레임워크 (4스텝) — 계단형 다이어그램
- [ ] AC-3: M5-2 GSC 활용법 (4스텝) — 브라우저 목업 (URL Inspection)
- [ ] AC-4: M5-3 GA4 & UTM 추적 (4스텝) — 코드 예시 + 퍼널 다이어그램
- [ ] AC-5: M5-4 AI Validator 루틴 (4스텝) — 프롬프트 템플릿
- [ ] AC-6: M5-5 가설 기반 실험 설계 (4스텝) — 실험 플로우
- [ ] AC-7: M5-6 90일 로드맵 설계 (4스텝) — 타임라인 다이어그램
- [ ] AC-8: M5-7 종합 평가 (5Q)
- [ ] AC-9: M5-7 합격 시 "전체 과정 수료" 메시지 표시
- [ ] AC-10: 총 29스텝 + ~100옵션

**Definition of Done:**
- [ ] `apps/api/seed.py`에 Stage 5 데이터 추가
- [ ] 전체 Stage 1→5 순차 해제 E2E 확인
- [ ] 최종 수료 화면 정상 표시

**Priority:** P0
**Slice:** 9
**변경 파일:** `apps/api/seed.py`
**데이터 소스:** `materials/GEO 심층 리서치 측정/실험/90일 로드맵`

---

## P1 — Slice 10: 검증 및 품질 보증

#### US-032: Stage 해제 로직 확장 (Stage 3→4→5)

- **As a** backend engineer
- **I want** 기존 Stage 1→2 해제 로직이 Stage 3→4→5로 자동 확장되는지 검증하고 필요시 수정하여
- **So that** 5개 Stage의 순차 해제가 정상 작동한다

**Acceptance Criteria:**
- [ ] AC-1: `GET /api/stages` → 5개 Stage 반환 (Stage 1 해제, 2~5 잠김)
- [ ] AC-2: Stage 2 평가 합격 → Stage 3 해제
- [ ] AC-3: Stage 3 평가 합격 → Stage 4 해제
- [ ] AC-4: Stage 4 평가 합격 → Stage 5 해제
- [ ] AC-5: `POST /api/stages/{id}/evaluate` 모든 Stage에서 동작

**Definition of Done:**
- [ ] `_is_stage_unlocked()` 함수가 Stage 3~5 정상 처리 확인
- [ ] pytest 테스트 추가 (Stage 3~5 해제)

**Priority:** P1
**Slice:** 10
**변경 파일:** `apps/api/main.py`, `apps/api/database.py`

---

#### US-033: 비주얼 컴포넌트 다크모드 검증

- **As a** learner
- **I want** 다크모드에서 모든 비주얼 컴포넌트가 정상 표시되고
- **So that** 야간 학습 시에도 시각 자료를 편하게 볼 수 있다

**Acceptance Criteria:**
- [ ] AC-1: 6종 컴포넌트 모두 `[data-theme="dark"]` CSS 오버라이드 존재
- [ ] AC-2: 라이트↔다크 토글 시 깨지는 컴포넌트 없음
- [ ] AC-3: 텍스트 대비 비율 WCAG AA 기준 충족

**Definition of Done:**
- [ ] 전 Stage reading 스텝 다크모드 수동 확인
- [ ] 이슈 발견 시 CSS 수정

**Priority:** P1
**Slice:** 10
**변경 파일:** `apps/web/css/style.css`

---

#### US-034: QA 통합 테스트 (Phase 2)

- **As a** QA tester
- **I want** Phase 2 변경사항에 대한 자동/수동 테스트를 수행하여
- **So that** 기존 기능 회귀 없이 새 기능이 정상 작동함을 확인한다

**Acceptance Criteria:**
- [ ] AC-1: 기존 28개 pytest 전체 통과
- [ ] AC-2: Stage 3~5 API 테스트 추가 (최소 10개)
- [ ] AC-3: 비주얼 렌더링 수동 체크 (Stage별 1개 reading 스텝)
- [ ] AC-4: 전체 E2E 시뮬레이션 (Stage 1→5 순차 진행)

**Definition of Done:**
- [ ] `tests/` 디렉토리에 신규 테스트 파일 추가
- [ ] `docs/engineering/50-test-plan.md` 업데이트
- [ ] 전체 테스트 통과

**Priority:** P1
**Slice:** 10
**변경 파일:** `tests/`, `docs/engineering/50-test-plan.md`

---

#### US-035: 피드백 텍스트 품질 검증 (Phase 2)

- **As a** content curator
- **I want** Stage 3~6의 신규 옵션 피드백이 일관된 품질 기준을 충족하도록 검증하고
- **So that** 학습자에게 균일한 피드백 경험을 제공한다

**Acceptance Criteria:**
- [ ] AC-1: 모든 피드백 40자 이상
- [ ] AC-2: 존댓말 일관성 100%
- [ ] AC-3: 오답 피드백에 힌트/격려 포함
- [ ] AC-4: `scripts/validate_feedback.py` 실행 → PASS

**Definition of Done:**
- [ ] 검증 스크립트 실행 결과 PASS
- [ ] 미달 피드백 수정 완료

**Priority:** P1
**Slice:** 10
**변경 파일:** `apps/api/seed.py`, `scripts/validate_feedback.py`

---

#### US-036: Stage 6 — B2B GEO 과업 실행 캡스톤 (7모듈)

- **As a** B2B GEO 운영팀
- **I want** 교육 모듈과 실무 과업을 1:1로 연결한 Stage 6 캡스톤을 운영하고
- **So that** Stage 1~5 학습 내용을 실제 분기 실행 계획으로 전환할 수 있다

**Acceptance Criteria:**
- [x] AC-1: Stage 6 INSERT (`unlock_condition`: Stage 5 완료 + 70%)
- [x] AC-2: Stage 6에 7개 모듈(M6-1~M6-7) 추가
- [x] AC-3: 각 모듈 4스텝(Reading/Quiz/Practice 기반) 구성
- [x] AC-4: 마지막 모듈(평가 모듈)에 퀴즈 스텝 포함 (`/api/stages/{id}/evaluate` 호환)
- [x] AC-5: Stage 6 검증 테스트 추가 (unlock condition, 모듈/스텝 수, 평가모듈 퀴즈)

**Definition of Done:**
- [x] `apps/api/seed.py`에 Stage 6 데이터 반영
- [x] `tests/test_phase2.py`에 Stage 6 회귀 테스트 반영
- [x] `python3 -m pytest -q tests/test_phase2.py` 통과

**Priority:** P0
**Slice:** 11
**변경 파일:** `apps/api/seed.py`, `tests/test_phase2.py`, `docs/strategy/70-content-dev-plan.md`

---

## Phase 2 우선순위 요약

| Slice | 우선순위 | 유저스토리 | 주요 변경 파일 | 예상 규모 |
|-------|----------|-----------|---------------|----------|
| 5 | P0 | US-026 | `style.css` | ~400줄 CSS |
| 6 | P0 | US-027, US-028 | `seed.py` | 14개 reading 스텝 비주얼 |
| 7 | P0 | US-029 | `seed.py`, `database.py` | 7모듈+29스텝+~100옵션 |
| 8 | P0 | US-030 | `seed.py` | 7모듈+29스텝+~100옵션 |
| 9 | P0 | US-031 | `seed.py` | 7모듈+29스텝+~100옵션 |
| 10 | P1 | US-032~035 | `main.py`, `style.css`, `tests/` | 검증+QA |
| 11 | P0 | US-036 | `seed.py`, `tests/test_phase2.py` | Stage 6 (7모듈+28스텝+84옵션) |

### Phase 2 총 규모

- **유저스토리**: 11개 (US-026 ~ US-036)
- **신규 모듈**: 28개 (Stage 3: 7, Stage 4: 7, Stage 5: 7, Stage 6: 7)
- **신규 스텝**: ~115개
- **신규 옵션**: ~360개
- **CSS 추가**: ~400줄 (비주얼 컴포넌트 6종 + 다크모드)
- **비주얼 보강**: Stage 1-2 reading 스텝 14개
