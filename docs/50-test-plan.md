# 50 — Test Plan

GEO 멘토링 학습 시스템 (MVP) 통합 테스트 계획

---

## 발견 이슈 (Code Review Results)

### Critical Issues

1. **Reading Step 완료 처리 불일치** (심각도: Critical)
   - **문제**: `POST /api/steps/{id}/answer` 에서 reading step 완료 시 `{completed: true}` 반환
   - **프론트엔드**: `ReadingCompleteResponse` 모델 정의만 있고, 실제 응답 처리 미구현
   - **영향**: Reading step 진행 후 상태가 업데이트되지 않을 수 있음
   - **수정**: `app.js` 라인 558에서 응답 처리 로직 확인 필요

2. **Module 다음 순서 네비게이션 오류** (심각도: Critical)
   - **문제**: `renderNormalResult()` (라인 696)에서 `nextModuleId = moduleId + 1`로 하드코딩
   - **위험**: Module ID가 연속되지 않으면 다음 모듈 버튼이 존재하지 않는 모듈로 이동
   - **예시**: 모듈 ID가 [1, 2, 5, 6, 7...]인 경우 모듈 2 다음 버튼은 ID 3(없음)으로 이동
   - **수정**: API에서 다음 모듈 ID를 반환하거나 모듈 리스트에서 순서 기반 조회 필요

3. **Stage 해제 로직에서 Quiz Steps 없을 경우 처리** (심각도: Major)
   - **문제**: `_is_stage_unlocked()` (라인 93-98)에서 quiz_steps가 없으면 False 반환하지만, 에러 처리 부재
   - **위험**: Stage 2 종합평가 모듈에 quiz step이 없는 경우 Stage 2 영구 잠금
   - **확인**: Seed 데이터에서 Stage 1 마지막 모듈(order_idx=8)에 quiz step 존재 확인 필요

### Major Issues

4. **Module 상세 조회에서 Stage ID 누락** (심각도: Major)
   - **문제**: `GET /api/modules/{id}` 응답이 stage_id를 반환하지 않음 (모델에 정의 안됨)
   - **프론트엔드 영향**: 라인 347-349에서 module detail 조회 후 stageId 설정 시도하지만 항상 null
   - **결과**: 학습 화면에서 뒤로가기 링크가 항상 대시보드(#/)로만 이동
   - **수정**: `ModuleResponse` 모델에 `stage_id` 필드 추가

5. **Evaluation Module 판정 로직 불명확** (심각도: Major)
   - **문제**: `renderResult()` (라인 599)에서 `isEvalModule = moduleDetail.order_idx === 8`로 판정
   - **위험**: Stage 2 모듈 8도 동일 조건으로 평가 모듈로 인식될 수 있음
   - **권장**: 모듈 ID 또는 별도 플래그로 종합평가 모듈 판정 (stage_id + order_idx 복합 확인)

6. **API Error Handling 부족** (심각도: Major)
   - **문제**: `renderCurrentStep()` 실패 시 단순 에러 메시지만 표시, 복구 불가
   - **예시**: 네트워크 재연결 후 재시도 가능하지만, 사용자 진행 상태 잃을 수 있음
   - **권장**: 마지막 단계 캐싱 또는 세션 복구 로직 추가

### Minor Issues

7. **Option 선택 전 다음 버튼 비활성화** (심각도: Minor)
   - **현황**: 라인 465에서 `selectedOptionId == null`일 때 버튼 비활성화 (정상)
   - **UX**: 선택 전 "정답 확인" 버튼이 비활성 상태로 회색 표시 (권장사항: "선택해주세요" 힌트 표시)

8. **재시도 후 진도 초기화** (심각도: Minor)
   - **문제**: `retryModule()` (라인 718-730)에서 learningState 전체 초기화하지만, DB는 기존 진도 유지
   - **현황**: 기술적으로는 정상 (사용자가 다시 풀 수 있도록 함), 하지만 UI에서 진도 표시 혼동 가능
   - **개선**: 재시도 버튼 클릭 전 확인 다이얼로그 추가

9. **CORS 설정 과도함** (심각도: Minor)
   - **현황**: 라인 50-54 `allow_origins=["*"]`로 모든 도메인 허용
   - **권장**: 실제 배포 시 특정 도메인으로 제한

10. **마크다운 렌더링 XSS 방지 미확인** (심각도: Minor)
    - **문제**: `marked.parse()`를 직접 사용하지만, sanitize 옵션 설정 없음
    - **현황**: Seed 데이터가 신뢰할 수 있는 콘텐츠이므로 즉시 위험은 낮음
    - **권장**: 향후 관리자 UI 추가 시 DOMPurify 같은 라이브러리 사용

---

## 수동 체크리스트 (Smoke Test)

| # | 카테고리 | 체크 항목 | 예상 결과 | 확인사항 | Pass/Fail |
|---|----------|-----------|-----------|---------|-----------|
| 1 | 기본 | 서버 정상 기동 | `uvicorn` 실행 후 터미널에 "Uvicorn running..." 메시지 표시 | http://127.0.0.1:8000/api/health | |
| 2 | 기본 | 헬스체크 API | GET /api/health → 200, `{"status": "ok"}` | 브라우저 또는 curl로 확인 | |
| 3 | 기본 | 메인 페이지 로딩 | http://127.0.0.1:8000 접속 시 "GEO 멘토링 학습" 제목 표시 | 헤더 배지가 "online"으로 변함 | |
| 4 | 대시보드 | Stage 목록 표시 | 2개 Stage 카드 표시 (Stage 1 해제, Stage 2 잠금) | 진도 바 정상 표시 | |
| 5 | 대시보드 | 전체 진도 계산 | 상단 "전체 진도" 진도 바 표시 (초기: 0/16) | 수치가 정확한지 확인 | |
| 6 | 모듈 목록 | Stage 1 모듈 진입 | Stage 1 카드 클릭 → 8개 모듈 목록 표시 | 모듈명, 설명, 상태(미완료) 표시 | |
| 7 | 학습 | Reading Step 진행 | 모듈 1-1 클릭 → 첫 step (마크다운 콘텐츠) 표시 → "다음" 버튼 클릭 | 두 번째 step으로 이동, 진도 바 업데이트 | |
| 8 | 학습 | Quiz Step 정답 제출 | 모듈 1-1 2번째 step (선택 퀴즈) → 정답 선택 → "정답 확인" 버튼 → 초록 피드백 | is_correct=1 선택지가 표시됨 | |
| 9 | 학습 | Quiz Step 오답 제출 | 모듈 1-1 2번째 step → 오답 선택 → "정답 확인" 버튼 → 빨강 피드백 + 정답 공개 | 정답 선택지가 별도 카드로 표시됨 | |
| 10 | 결과 | 모듈 완료 화면 | 모듈 1-1 마지막 step 완료 → 결과 화면 표시 | "모듈 완료!" 타이틀, 완료 메시지, "다음 모듈로" 버튼 표시 | |
| 11 | 결과 | 다음 모듈 네비게이션 | 모듈 완료 후 "다음 모듈로" → 모듈 1-2 학습 화면 진입 | URL #/module/2, 진도 초기화 (Step 1/X) | |
| 12 | 종합평가 | Stage 1 마지막 모듈 (M1-8) | 모듈 1-8 진입 → quiz steps만 표시 | reading step 없음 | |
| 13 | 종합평가 | 70% 이상 통과 | M1-8 모든 quiz step 정답 → 결과 화면 → "축하합니다!" | "합격" 표시, Stage 2 해제 메시지, "대시보드로" 버튼 | |
| 14 | 종합평가 | 70% 미만 불합격 | M1-8에서 50% 정도만 정답 → 결과 화면 → "아쉽습니다." | "불합격" 표시, "다시 도전" 버튼, 취약점 미표시(optional) | |
| 15 | Stage 잠금 | Stage 2 조건부 해제 | Stage 1 M1-8 70% 이상 통과 후 대시보드 → Stage 2 카드 활성화 | Stage 2 카드 클릭 가능, 모듈 목록 표시 | |
| 16 | Stage 잠금 | Stage 2 미해제 | Stage 1 M1-8 70% 미만 → 대시보드 → Stage 2 카드 잠금 상태 | 🔒 아이콘, "이전 Stage 완료 후 해제" 메시지 표시, 클릭 불가 | |
| 17 | 에러 | 네트워크 에러 대시보드 | 서버 종료 후 페이지 새로고침 → 에러 메시지 + "다시 시도" 버튼 | "데이터를 불러올 수 없습니다" 메시지 | |
| 18 | 에러 | 잘못된 모듈 ID | URL #/module/999 직접 입력 → 에러 메시지 | "학습 콘텐츠를 불러올 수 없습니다" 메시지, 복구 버튼 | |
| 19 | 진도 | 모듈 진행 표시 | 모듈 1-1 50% 완료 후 모듈 목록 → "진행 중 (2/4)" 표시 | 모듈 카드 색상 변경 (in-progress 클래스) | |
| 20 | 진도 | 모듈 완료 표시 | 모듈 1-1 완료 후 모듈 목록 → "✓ 완료" 배지 표시 | 모듈 카드 왼쪽 초록 라인 표시 | |

---

## 자동화 테스트 제안

### 1. API 엔드포인트 테스트 (pytest + httpx)

**파일**: `tests/test_api.py` (기존 파일 확장)

**추가 테스트 케이스**:

| 테스트 ID | 엔드포인트 | 테스트 내용 | 도구 | 우선순위 |
|-----------|-----------|-----------|------|---------|
| T1 | GET /api/health | 헬스체크 상태 코드 200 확인 | pytest | P0 |
| T2 | GET /api/stages | Stage 목록 반환 (id, title, is_unlocked 포함) | pytest | P0 |
| T3 | GET /api/stages | Stage 1은 항상 unlocked | pytest | P0 |
| T4 | GET /api/stages | Stage 2는 초기 locked | pytest | P0 |
| T5 | GET /api/stages/{id}/modules | 특정 Stage의 모듈 목록 반환 | pytest | P0 |
| T6 | GET /api/stages/{id}/modules | 모듈의 completed_steps, total_steps 정확성 | pytest | P0 |
| T7 | GET /api/modules/{id} | 모듈 상세 정보 반환 (title, description, stage_id 포함) | pytest | P1 |
| T8 | GET /api/modules/{id} | 존재하지 않는 모듈 ID → 404 에러 | pytest | P0 |
| T9 | GET /api/modules/{id}/steps | 모듈 내 step 목록 반환 (type, options 포함) | pytest | P0 |
| T10 | GET /api/modules/{id}/steps | reading step은 options=None | pytest | P0 |
| T11 | GET /api/modules/{id}/steps | quiz/practice step은 options 포함 (is_correct, feedback_md 제외) | pytest | P0 |
| T12 | GET /api/modules/{id}/steps | step 옵션에 is_correct, feedback_md 미포함 (보안) | pytest | P0 |
| T13 | POST /api/steps/{id}/answer | reading step 제출 → `{completed: true}` 반환 | pytest | P1 |
| T14 | POST /api/steps/{id}/answer | quiz step 정답 제출 → is_correct=true, feedback 포함 | pytest | P0 |
| T15 | POST /api/steps/{id}/answer | quiz step 오답 제출 → is_correct=false, correct_option 공개 | pytest | P0 |
| T16 | POST /api/steps/{id}/answer | option_id 미입력 시 quiz step → 422 에러 | pytest | P0 |
| T17 | POST /api/steps/{id}/answer | 잘못된 option_id → 404 에러 | pytest | P0 |
| T18 | POST /api/steps/{id}/answer | 동일 step 반복 제출 (UPSERT) → 최신 답변만 유지 | pytest | P0 |
| T19 | GET /api/progress | 전체 진도 요약 반환 (stages 배열 포함) | pytest | P0 |
| T20 | GET /api/progress | 각 stage의 score_pct 계산 정확성 | pytest | P1 |
| T21 | POST /api/stages/{id}/evaluate | Stage 1 M1-8 평가 → score_pct 반환 | pytest | P0 |
| T22 | POST /api/stages/{id}/evaluate | 70% 이상 → passed=true, unlocked_stage_id=2 | pytest | P0 |
| T23 | POST /api/stages/{id}/evaluate | 70% 미만 → passed=false, unlocked_stage_id=null | pytest | P0 |
| T24 | POST /api/stages/{id}/evaluate | 정의되지 않은 stage → 404 에러 | pytest | P0 |

**실행 방법**:
```bash
cd /c/Users/admin/Desktop/Mkt\ Geo\ Study
pytest tests/test_api.py -v --tb=short
```

---

### 2. 통합 테스트 (API → DB → Frontend)

**파일**: `tests/test_integration.py` (신규)

**테스트 시나리오**:

| 테스트 ID | 시나리오 | 예상 동작 | 도구 |
|-----------|--------|---------|------|
| I1 | Stage 1 → 모듈 1-1 → 모든 step 완료 | 모듈 1-1 completed_steps = total_steps | pytest |
| I2 | 모듈 1-1 완료 → 모듈 1-2 시작 → Stage 진도 업데이트 | Stage 1 completed_modules 증가 | pytest |
| I3 | Stage 1 M1-8 모든 quiz step 정답 | Stage 2 unlocked=true | pytest |
| I4 | Stage 1 M1-8 일부 오답 (score < 70%) | Stage 2 unlocked=false | pytest |
| I5 | 재시도: 불합격한 M1-8 다시 풀기 | 기존 답변 덮어쓰기, 점수 재계산 | pytest |
| I6 | 동시 요청 처리 | 2개 스텝 동시 제출 → 모두 정상 기록 | pytest + threading |

---

### 3. 프론트엔드 렌더링 테스트 (Playwright 또는 Selenium)

**파일**: `tests/test_frontend.py` (신규)

**테스트 케이스**:

| 테스트 ID | 컴포넌트 | 테스트 내용 | 도구 |
|-----------|----------|-----------|------|
| F1 | Dashboard | 서버 실행 후 #/ 접속 → 2개 Stage 카드 렌더링 | Playwright |
| F2 | Module List | #/stage/1 접속 → 8개 모듈 카드 렌더링 | Playwright |
| F3 | Learning Screen | #/module/1 접속 → Step 1/X 표시, 콘텐츠 로드 | Playwright |
| F4 | Quiz Step | Quiz step 화면 → 4개 선택지 렌더링 | Playwright |
| F5 | Feedback | 정답 선택 후 피드백 박스 표시 (초록) | Playwright |
| F6 | Result Screen | 모듈 완료 후 #/module/X/result → 결과 화면 렌더링 | Playwright |
| F7 | Navigation | "다음 모듈로" 클릭 → #/module/{next_id}로 이동 | Playwright |
| F8 | Error Handling | 네트워크 에러 → 에러 메시지 + 복구 버튼 표시 | Playwright |

**실행 방법**:
```bash
pip install playwright pytest-playwright
python -m playwright install
pytest tests/test_frontend.py -v
```

---

### 4. 데이터 무결성 테스트

**파일**: `tests/test_seed.py` (신규)

**테스트 케이스**:

| 테스트 ID | 대상 | 테스트 내용 |
|-----------|-----|-----------|
| S1 | Seed 데이터 | Stage 2개, 각각 8개 모듈 존재 |
| S2 | 모듈별 Step 개수 | 각 모듈 >= 3개 step (reading + quiz) |
| S3 | Quiz Step 옵션 | 각 quiz step >= 2개 옵션, 정답 1개만 |
| S4 | 외래키 무결성 | 모든 step은 유효한 module_id 참조 |
| S5 | Unlock Condition | Stage 2 unlock_condition JSON 유효성 |
| S6 | 마크다운 콘텐츠 | 모든 step content_md가 유효한 마크다운 |

```python
# tests/test_seed.py 예시 구조
def test_stages_exist():
    conn = get_db()
    stages = conn.execute("SELECT COUNT(*) AS cnt FROM stages").fetchone()["cnt"]
    assert stages == 2

def test_stage1_has_8_modules():
    conn = get_db()
    modules = conn.execute(
        "SELECT COUNT(*) AS cnt FROM modules WHERE stage_id = 1"
    ).fetchone()["cnt"]
    assert modules == 8

def test_all_quiz_steps_have_correct_option():
    conn = get_db()
    quiz_steps = conn.execute(
        "SELECT id FROM steps WHERE type = 'quiz'"
    ).fetchall()
    for step in quiz_steps:
        correct = conn.execute(
            "SELECT COUNT(*) AS cnt FROM options WHERE step_id = ? AND is_correct = 1",
            (step["id"],)
        ).fetchone()["cnt"]
        assert correct == 1, f"Step {step['id']} has {correct} correct options, expected 1"
```

---

## E2E 시나리오 (Happy Path + Edge Cases)

### Happy Path: 학습자 완주 시나리오

**시나리오**: 신규 사용자가 Stage 1을 완료하고 Stage 2로 진입

**단계별 검증**:

1. **초기 상태** (대시보드)
   - [ ] Stage 1 "해제", Stage 2 "잠금" 표시
   - [ ] 전체 진도 0/16

2. **Stage 1 모듈 진행** (모듈 1-1 ~ 1-7)
   - [ ] 각 모듈: reading step 2~3개 + quiz step 1~2개
   - [ ] Reading step 진도 기록 (is_completed=true, is_correct=null)
   - [ ] Quiz step 정답 선택 → 피드백 표시
   - [ ] 모듈 완료 → 다음 모듈 네비게이션
   - [ ] 진도 바 업데이트 (1/8, 2/8, ..., 7/8)

3. **Stage 1 종합평가** (모듈 1-8)
   - [ ] 모든 step이 quiz type (reading 없음)
   - [ ] 총 8개 quiz step 제시
   - [ ] 정답 6개 이상 선택 (75% 이상)
   - [ ] 결과 화면: "축하합니다!" + "합격" + 점수
   - [ ] Stage 2 해제 메시지 표시
   - [ ] "대시보드로" 버튼 → 대시보드 이동

4. **Stage 2 진입** (대시보드)
   - [ ] Stage 2 카드 "해제" 상태 변함
   - [ ] Stage 2 "모듈 목록으로" 클릭
   - [ ] 모듈 2-1 ~ 2-8 표시

5. **Stage 2 한 모듈 완료** (모듈 2-1)
   - [ ] 학습 진행 (reading + quiz)
   - [ ] 결과 화면: "모듈 완료!" + "다음 모듈로"
   - [ ] 모듈 2-2로 네비게이션

---

### Edge Cases

#### E1: 모듈 중단 후 재진입
```
시나리오: 모듈 1-3 Step 2/5에서 브라우저 닫음 → 재진입
기대: Step 2/5부터 계속 (이전 진도 유지)
검증: learningState.currentStepIdx = 1 (completed step 다음)
```

#### E2: 종합평가 재시도
```
시나리오: M1-8 첫 시도 불합격 (65%) → "다시 도전" → 재풀이
기대: 기존 답변 모두 초기화, 최신 답변만 DB 기록
검증: user_progress 테이블에서 최신 답변만 남음
```

#### E3: 네트워크 끊김 복구
```
시나리오: 학습 중 서버 다운 → "다시 시도" 버튼 클릭 → 서버 재시작
기대: 마지막 저장된 진도부터 계속 (손실 없음)
검증: API 요청 재시도 성공, 진도 유지
```

#### E4: 동시 제출
```
시나리오: Quiz step에서 빠르게 "정답 확인" 2회 클릭
기대: 첫 번째 제출만 처리, 두 번째는 무시
검증: user_progress UNIQUE(user_id, step_id) 제약으로 인한 UPSERT
```

#### E5: 잘못된 모듈 ID 직접 입력
```
시나리오: #/module/999 URL 직접 입력
기대: 에러 메시지 + 대시보드로 돌아가기
검증: 404 에러 처리, 사용자 가이드 표시
```

#### E6: Stage 2 해제 직전 불합격
```
시나리오: M1-8 점수 68% (1점 모자람) → 불합격
기대: "아쉽습니다" + "다시 도전" → 재풀이 후 72% 통과
검증: 두 번째 evaluateStage 호출 시 unlocked_stage_id=2 반환
```

#### E7: 다단계 실습 (Practice Step)
```
시나리오: M2-4 practice step (3개 선택)
기대: Step 1 선택 → Step 2 선택 (Step 1 결과 표시) → Step 3 선택 → 비교 화면
검증:
  - Step 1: "타겟 고객층 선택" → 사용자 선택 기록
  - Step 2: 사용자 Step 1 선택에 따른 맞춤형 선택지 제시
  - Step 3: 사용자 Step 1, 2 선택 기반 최종 선택
  - 결과: "당신의 설계 vs 전문가 설계" 비교 표시
```

---

## 릴리스 체크리스트

### 기능 검증 (Functional)

- [ ] **Health Check**: `GET /api/health` → 200, `{status: "ok"}`
- [ ] **Stage 목록**: Stage 1, 2 모두 표시, 초기 Stage 2 잠금
- [ ] **Module 목록**: 각 Stage별 8개 모듈 표시
- [ ] **Step 진행**: reading → quiz 순차 진행, 진도 바 업데이트
- [ ] **정답 판정**: 정답/오답 피드백 정상 표시
- [ ] **진도 저장**: 모든 step 완료 후 is_completed 업데이트
- [ ] **Stage 해제**: M1-8 70% 이상 통과 후 Stage 2 해제
- [ ] **재시도**: 불합격 모듈 재풀이 가능, 점수 재계산
- [ ] **결과 화면**: 모듈/종합평가 결과 정상 렌더링
- [ ] **네비게이션**: 모든 화면 간 이동 정상 (대시보드 ↔ 모듈 목록 ↔ 학습 ↔ 결과)

### 데이터 검증 (Data Integrity)

- [ ] **Seed 데이터**: Stage 2개, 모듈 16개, step >= 80개 확인
- [ ] **Quiz Step 옵션**: 모든 quiz step에 정답 1개 포함
- [ ] **마크다운 렌더링**: 마크다운 콘텐츠 정상 파싱 (헤딩, 리스트, 볼드 등)
- [ ] **외래키 무결성**: 모든 step, option이 유효한 부모 레코드 참조
- [ ] **UNIQUE 제약**: user_progress (user_id, step_id) 중복 방지

### 보안 검증 (Security)

- [ ] **Option 숨김**: GET /api/modules/{id}/steps에서 is_correct, feedback_md 미포함
- [ ] **.env 미노출**: 환경 변수 파일 .gitignore에 포함, 코드에 하드코딩 없음
- [ ] **SQL Injection 방지**: 모든 DB 쿼리가 파라미터화된 쿼리 사용
- [ ] **XSS 방지**: 사용자 입력 없으므로 위험 낮음, 마크다운 렌더링 시 신뢰 가능한 소스만 사용
- [ ] **CORS 설정**: 배포 전 allow_origins을 특정 도메인으로 제한

### UX 검증 (User Experience)

- [ ] **로딩 상태**: 모든 데이터 로딩 시 스피너/스켈레톤 표시
- [ ] **에러 상태**: 네트워크 오류 시 명확한 메시지 + "다시 시도" 버튼
- [ ] **빈 상태**: 콘텐츠 없을 경우 안내 메시지 표시
- [ ] **피드백 명확성**: 정답/오답 피드백 색상 구분 (초록/빨강)
- [ ] **진도 시각화**: 진도 바, Step 카운터 정상 업데이트
- [ ] **뒤로가기**: 모든 화면에서 이전 화면으로 돌아가기 가능
- [ ] **버튼 상태**: 선택 전 "정답 확인" 버튼 비활성화, 로딩 중 "처리 중..." 표시

### 성능 검증 (Performance)

- [ ] **API 응답 시간**: GET 요청 < 500ms, POST 요청 < 1000ms
- [ ] **페이지 로딩**: 첫 렌더링 < 2초
- [ ] **Step 전환**: "다음" 버튼 클릭 후 렌더링 < 500ms

### 호환성 검증 (Compatibility)

- [ ] **브라우저**: Chrome, Firefox, Safari 최신 버전 테스트
- [ ] **DB**: SQLite 정상 작동, data/geo_mentor.db 생성 확인
- [ ] **Python 버전**: Python 3.9+ (FastAPI, Pydantic 호환성)
- [ ] **의존성**: requirements.txt의 모든 패키지 설치 가능

### 운영 체크리스트

- [ ] **README 업데이트**: 실행 방법, 환경 설정 기재
- [ ] **.env.example 생성**: 필요한 환경 변수 예시 (현재 프로젝트는 필요 없음)
- [ ] **테스트 스크립트**: `pytest` 명령으로 전체 테스트 실행 가능
- [ ] **DB 초기화**: `python -m apps.api.seed` 명령으로 Seed 데이터 삽입 가능
- [ ] **로그 설정**: 에러 로그 console 또는 파일로 기록
- [ ] **docs/90-log.md 업데이트**: 구현 이슈, 결정사항, 다음 할 일 기재

---

## 테스트 실행 명령어

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. DB 초기화 (Seed 데이터 삽입)
python -m apps.api.seed

# 3. 서버 시작 (백그라운드)
uvicorn apps.api.main:app --reload &

# 4. 자동 테스트 실행
pytest tests/ -v --tb=short

# 5. 수동 테스트 (브라우저)
# http://localhost:8000 접속 후 위 수동 체크리스트 수행

# 6. 테스트 커버리지
pytest tests/ --cov=apps.api --cov-report=html
```

---

## 주요 리스크 및 완화 방안

| 리스크 | 영향 | 확률 | 완화 방안 |
|--------|------|------|---------|
| **Module ID 연속성 부재** | 다음 모듈 버튼 오류 | 중 | API 응답에 next_module_id 추가, 또는 프론트에서 모듈 리스트로 순서 조회 |
| **Stage 2 모듈 8 평가 판정** | 일반 모듈이 평가 모듈로 인식 | 중 | stage_id + order_idx 복합 확인으로 판정 로직 강화 |
| **Network 불안정성** | 진도 손실 | 낮음 | 마지막 상태 클라이언트 캐싱, 요청 재시도 로직 |
| **Browser 호환성** | 일부 사용자 접근 불가 | 낮음 | 주요 브라우저(Chrome, Firefox, Safari) 테스트 후 배포 |
| **Seed 데이터 부족** | 콘텐츠 완성도 낮음 | 중 | MVP 16개 모듈 + 평균 5개 step 목표, 콘텐츠 담당자와 병렬 진행 |

---

## 요약

**총 수동 테스트 항목**: 20개 (Smoke Test + 기능별 체크)
**총 자동 테스트 케이스**: 60개+ (API 24개 + Integration 6개 + Frontend 8개 + Seed 6개)
**예상 테스트 기간**:
- 자동 테스트: 5~10분
- 수동 테스트: 30~45분
- 전체: 1시간

**배포 기준**:
1. 모든 수동 체크리스트 Pass
2. pytest 전체 통과 (coverage > 80%)
3. 릴리스 체크리스트 전항목 확인
4. docs/90-log.md 최종 업데이트
