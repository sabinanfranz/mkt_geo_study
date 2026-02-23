# 30 — Architecture

## 개요

선택지 기반 GEO 멘토링 학습 시스템의 기술 설계 문서.
LLM 없이 사전 작성된 콘텐츠와 선택지/피드백으로 학습을 제공한다.

---

## 시스템 구성도

```
[Browser SPA]  ──HTTP/JSON──▶  [FastAPI]  ──SQL──▶  [SQLite | PostgreSQL]
  (바닐라 JS)                     │                  (data/geo_mentor.db)
  Hash 라우팅                     │
  marked.js CDN                   ├── /api/stages
                                  ├── /api/modules
                                  ├── /api/steps
                                  ├── /api/progress
                                  └── / (static files)

[apps/llm/]  ← 미사용 (mock 유지, 변경 없음)
```

---

## 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| Frontend | HTML / CSS / JS (바닐라) | SPA 라우팅 (hash-based) |
| Backend | FastAPI (Python) | REST API + Static file serving |
| Database | SQLite / PostgreSQL | local은 SQLite, Railway는 PostgreSQL |
| LLM | 미사용 | `apps/llm/` 디렉토리는 mock 유지, 변경 없음 |

---

## DB 스키마

```sql
-- Stage (1: GEO 세계관 이해, 2: Technical GEO 기초 실습)
CREATE TABLE stages (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    order_idx INTEGER NOT NULL,
    unlock_condition TEXT    -- JSON: {"require_stage_complete": 1, "min_score_pct": 70} 또는 NULL
);

-- 모듈 (Stage 내 학습 단위, 각 Stage당 8개)
CREATE TABLE modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_id INTEGER NOT NULL REFERENCES stages(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    order_idx INTEGER NOT NULL
);

-- Step (모듈 내 개별 화면 = 읽기카드/퀴즈/실습)
CREATE TABLE steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL REFERENCES modules(id),
    type TEXT NOT NULL CHECK(type IN ('reading', 'quiz', 'practice')),
    title TEXT NOT NULL,
    content_md TEXT NOT NULL,   -- 마크다운 본문
    order_idx INTEGER NOT NULL
);

-- 선택지 (퀴즈/실습의 옵션들)
CREATE TABLE options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL REFERENCES steps(id),
    label TEXT NOT NULL,          -- "A", "B", "C", "D"
    content TEXT NOT NULL,        -- 선택지 텍스트
    is_correct INTEGER DEFAULT 0, -- 1=정답
    feedback_md TEXT NOT NULL,    -- 이 옵션 선택 시 보여줄 피드백 마크다운
    order_idx INTEGER NOT NULL
);

-- 사용자 진도
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    step_id INTEGER NOT NULL REFERENCES steps(id),
    selected_option_id INTEGER REFERENCES options(id),
    is_correct INTEGER,            -- 1=정답, 0=오답, NULL=읽기카드
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, step_id)
);
```

### 데이터 관계

```
Stage 1:1──*  Module 1:1──*  Step 1:1──*  Option
                                  │
                            user_progress
```

- Stage → Module: 1:N (각 8개)
- Module → Step: 1:N (평균 5개)
- Step → Option: 1:N (퀴즈/실습만, 3~4개)
- Step → user_progress: 1:1 (user_id + step_id UNIQUE)

---

## API 설계

### 엔드포인트 목록

| Method | Path | 설명 | Request Body | Response |
|--------|------|------|-------------|----------|
| GET | `/api/health` | 헬스체크 | - | `{status: "ok"}` |
| GET | `/api/stages` | Stage 목록 + 잠금 상태 | - | `StageResponse[]` |
| GET | `/api/stages/{id}/modules` | Stage 내 모듈 목록 | - | `ModuleResponse[]` |
| GET | `/api/modules/{id}` | 모듈 상세 (steps 포함) | - | `ModuleDetailResponse` |
| GET | `/api/modules/{id}/steps` | 모듈 내 step 목록 | - | `StepResponse[]` |
| POST | `/api/steps/{id}/answer` | 답변 제출 | `{selected_option_id: int}` | `AnswerResponse` |
| GET | `/api/progress` | 전체 진도 요약 | - | `ProgressResponse` |
| POST | `/api/stages/{id}/evaluate` | Stage 종합평가 점수 계산 | - | `EvaluateResponse` |

### 응답 모델 (Pydantic)

```python
class StageResponse(BaseModel):
    id: int
    title: str
    description: str
    order_idx: int
    is_unlocked: bool              # 서버에서 계산
    completed_modules: int
    total_modules: int

class ModuleResponse(BaseModel):
    id: int
    stage_id: int
    title: str
    description: str
    order_idx: int
    completed_steps: int
    total_steps: int

class StepResponse(BaseModel):
    id: int
    module_id: int
    type: str                       # 'reading' | 'quiz' | 'practice'
    title: str
    content_md: str
    order_idx: int
    options: list[OptionResponse] | None
    is_completed: bool

class OptionResponse(BaseModel):
    id: int
    label: str
    content: str
    # is_correct, feedback_md는 답변 제출 전까지 숨김

class AnswerRequest(BaseModel):
    selected_option_id: int

class AnswerResponse(BaseModel):
    is_correct: bool
    selected_feedback_md: str
    correct_option: OptionReveal

class OptionReveal(BaseModel):
    id: int
    label: str
    content: str
    feedback_md: str

class ProgressResponse(BaseModel):
    stages: list[StageProgress]

class StageProgress(BaseModel):
    stage_id: int
    title: str
    is_unlocked: bool
    completed_modules: int
    total_modules: int
    score_pct: float | None

class EvaluateResponse(BaseModel):
    score_pct: float
    passed: bool
    total_questions: int
    correct_answers: int
    unlocked_stage_id: int | None
```

### Stage 해제 로직 (서버)

```python
def is_stage_unlocked(stage_id: int, user_id: str = "default") -> bool:
    if stage_id == 1:
        return True  # Stage 1은 항상 해제

    stage = get_stage(stage_id)
    if not stage.unlock_condition:
        return True

    condition = json.loads(stage.unlock_condition)
    required_stage = condition["require_stage_complete"]
    min_score = condition["min_score_pct"]

    # 이전 Stage의 종합평가(마지막 모듈) quiz steps 정답률 계산
    eval_module = get_last_module(required_stage)
    quiz_steps = get_quiz_steps(eval_module.id)
    correct = count_correct(quiz_steps, user_id)

    if not quiz_steps:
        return False

    score_pct = (correct / len(quiz_steps)) * 100
    return score_pct >= min_score
```

---

## 파일 구조

```
apps/
├── api/
│   ├── __init__.py          (기존)
│   ├── main.py              (수정) API 라우트 전면 재작성
│   ├── database.py          (신규) DB 연결 추상화 + migration runner
│   ├── models.py            (신규) Pydantic 응답/요청 모델
│   └── seed.py              (신규) Seed 데이터 삽입 스크립트
├── llm/
│   ├── __init__.py          (기존, 변경 없음)
│   └── graph.py             (기존, 변경 없음 — mock 유지)
└── web/
    ├── index.html           (수정) 멀티 화면 SPA
    ├── css/
    │   └── style.css        (수정) 카드/퀴즈/실습 UI
    └── js/
        └── app.js           (수정) 전체 프론트엔드 로직

data/
└── geo_mentor.db            (런타임 생성) SQLite DB 파일

tests/
├── test_api.py              (수정) API 엔드포인트 테스트
└── test_seed.py             (신규) Seed 데이터 무결성 테스트
```

---

## 프론트엔드 라우팅

### Hash-based SPA

```
#/                    → 대시보드 (Stage 진도 카드)
#/stage/{id}          → 모듈 목록
#/module/{id}         → 학습 화면 (step 순차 진행)
#/module/{id}/result  → 모듈 결과 화면
```

### 렌더링 패턴

| Step.type | 렌더링 |
|-----------|--------|
| `reading` | 마크다운 → HTML 변환 (marked.js) + "다음" 버튼 |
| `quiz` | 질문 + 선택지 라디오버튼 + "정답 확인" → 피드백 → "다음" |
| `practice` | 다단계 선택 + 최종 비교 화면 |

### 마크다운 렌더링

marked.js (CDN)를 사용하여 마크다운 → HTML 변환:
- 헤딩, 볼드, 리스트, 코드블록, 테이블 지원
- XSS 방지를 위한 sanitize 설정

---

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DATABASE_URL` | DB 연결 문자열 (SQLite/PostgreSQL) | `sqlite:///data/geo_mentor.db` |
| `APP_ENV` | 실행 환경 (`local`/`staging`/`prod`) | `local` |
| `SEED_ON_START` | 앱 시작 시 시드 자동 실행 여부 | `false` |
| `CORS_ALLOW_ORIGINS` | 허용 Origin 목록(콤마 구분) | `*` |

> 참고: LLM을 사용하지 않으므로 `OPENAI_API_KEY` 등 LLM 관련 환경 변수는 불필요.

---

## 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. DB 초기화 + Seed 데이터 삽입
python scripts/db_migrate.py
python scripts/db_seed.py

# 3. 서버 시작
uvicorn apps.api.main:app --reload

# 4. 브라우저에서 접속
# http://localhost:8000
```
