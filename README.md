# CCOS MVP Template

토이 프로젝트를 빠르게 찍어내기 위한 Claude Code 템플릿 레포.

## 빠른 시작

### 1. 실행 (Windows PowerShell)

```powershell
# 방법 1: 스크립트 사용 (기본 포트 8000)
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

# 방법 1-1: 커스텀 포트
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1 -Port 3000

# 방법 1-2: 환경변수로 포트 지정
$env:PORT = 3000
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

# 방법 2: 직접 실행
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn apps.api.main:app --reload --port 8000
```

브라우저에서 **http://127.0.0.1:8000** (또는 지정한 포트) 접속.

### 2. DB 마이그레이션/시드

```bash
# 스키마 마이그레이션
python scripts/db_migrate.py

# 교육 콘텐츠 시드 (멱등 업서트)
python scripts/db_seed.py
```

### 3. 테스트

```bash
python -m pytest tests/ -x -q
```

### 4. MVP 워크플로우 (Claude Code)

```
# 새 MVP 기획 (PLAN)
/mvp-new 반려동물 산책 일지를 기록하고 통계를 보여주는 웹앱

# 백로그 1개 구현 (APPLY)
/mvp-next

# 로컬 실행 & 스모크 테스트
/mvp-demo
```

또는 에이전트 모드로:
```
claude --agent mvp-coordinator
```

## Railway 배포

### 배포 파일

- `railway.json`: Start Command/Health Check 정의
- `runtime.txt`: Python 런타임 버전 고정

### 권장 환경 구성

- `staging` 환경: `staging` 브랜치 자동 배포
- `prod` 환경: `main` 브랜치 자동 배포
- 각 환경은 별도 PostgreSQL을 연결

### 필수 환경변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `DATABASE_URL` | Railway PostgreSQL 연결 문자열 | 로컬에서는 `sqlite:///data/geo_mentor.db` |
| `APP_ENV` | `local`/`staging`/`prod` 구분 | `local` |
| `SEED_ON_START` | 앱 시작 시 seed 실행 여부 | `false` |
| `CORS_ALLOW_ORIGINS` | 허용 Origin 목록(콤마 구분) | `*` |

### 배포 후 스모크 체크

```bash
python scripts/check_deploy.py https://<your-env>.up.railway.app
```

### 운영 권장 정책

- `SEED_ON_START=false` 유지 (운영에서 자동 재시드 방지)
- 콘텐츠 업데이트 시 `python scripts/db_seed.py`를 작업성 배포 잡으로 실행
- 배포 전 `staging`에서 `check_deploy.py` 통과 후 `prod` 반영

## 구조

```
ccos-mvp-template/
├── .claude/
│   ├── agents/       # 7개 서브에이전트 (coordinator, pm, ux, be, fe, llm, qa)
│   └── skills/       # 3개 스킬 (mvp-new, mvp-next, mvp-demo)
├── apps/
│   ├── api/          # FastAPI 백엔드 (main.py)
│   ├── web/          # HTML/CSS/JS 프론트엔드
│   └── llm/          # LangGraph 오케스트레이션 (mock 기본)
├── docs/             # 기획 · 설계 · 테스트 문서
├── tests/            # 테스트 코드
├── data/             # SQLite DB (gitignore 대상)
├── scripts/          # dev.ps1 실행 스크립트
├── requirements.txt  # Python 의존성
├── CLAUDE.md         # 프로젝트 규칙 · 워크플로우
└── README.md
```

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| Frontend | HTML / CSS / JS (바닐라) |
| Backend | FastAPI (Python) |
| Database | SQLite (local) / PostgreSQL (Railway) |
| LLM | LangGraph (mock 기본, 키 설정 시 실제 호출) |

## 에이전트 & 스킬

### 에이전트 (`.claude/agents/`)

| 에이전트 | 역할 |
|----------|------|
| `mvp-coordinator` | 전체 흐름 오케스트레이션 (PLAN/APPLY) |
| `product-manager` | PRD + 백로그 작성 |
| `ux-designer` | UX 플로우 + ASCII 와이어프레임 |
| `backend-dev` | FastAPI + SQLite 구현 |
| `frontend-dev` | HTML/CSS/JS 구현 |
| `llm-engineer` | LangGraph 파이프라인 |
| `qa-tester` | 테스트 계획 + 체크리스트 |

### 스킬 (`.claude/skills/`)

| 스킬 | 용도 |
|------|------|
| `/mvp-new <아이디어>` | MVP 한 줄 → 기획 문서 일괄 생성 |
| `/mvp-next` | 백로그 최상단 1개 구현 |
| `/mvp-demo` | 로컬 실행 + 스모크 체크 |

## LLM 키 설정 (선택)

mock 모드가 기본입니다. 실제 LLM을 사용하려면:

```bash
# .env 파일에 추가
OPENAI_API_KEY=sk-...
# 또는
ANTHROPIC_API_KEY=sk-ant-...
```
