---
name: mvp-demo
description: "로컬 실행 커맨드 + 5단계 스모크 체크리스트 출력"
disable-model-invocation: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /mvp-demo — 로컬 실행 & 스모크 테스트

## 목적

현재 MVP를 **로컬에서 실행**하고, **5단계 스모크 체크리스트**로 동작을 확인한다.

## 실행 절차

### Step 1: 환경 확인

현재 상태를 점검한다:

```bash
python --version
pip --version
```

### Step 2: 로컬 실행 커맨드 출력 (Windows PowerShell)

아래 커맨드를 채팅에 출력한다:

```
🚀 로컬 실행 방법 (Windows PowerShell):

# 방법 1: 스크립트 사용
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

# 방법 2: 직접 실행
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn apps.api.main:app --reload

# 브라우저에서 열기
# http://127.0.0.1:8000
```

### Step 3: 서버 시작 및 스모크 체크

서버를 백그라운드로 시작하고 5단계 체크를 수행한다:

```bash
# 서버 시작 (백그라운드)
cd /c/Users/admin/Desktop/ccos-mvp-template
python -m uvicorn apps.api.main:app --port 8000 &
sleep 3

# 스모크 체크
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/
curl -s -X POST http://127.0.0.1:8000/api/assistant -H "Content-Type: application/json" -d '{"message":"hello"}'
```

### Step 4: 5단계 스모크 체크리스트 출력

```
🔍 스모크 체크리스트:

1. [Health] GET /api/health → {"status":"ok"} 반환?
2. [Web]    GET / → index.html 정상 로딩?
3. [API]    POST /api/assistant → mock 응답 반환?
4. [UI]     입력창에 텍스트 입력 → 응답이 화면에 표시?
5. [Error]  빈 입력 전송 → 에러 메시지 표시?
```

### Step 5: 결과 요약

체크 결과를 요약하여 채팅에 출력한다.

## 출력 (채팅에 표시)

```
🚀 MVP 실행 가이드

📌 실행 커맨드:
  powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
  또는
  uvicorn apps.api.main:app --reload

🌐 접속: http://127.0.0.1:8000

🔍 스모크 체크 (5/5):
  1. ✅ Health check OK
  2. ✅ Web page loaded
  3. ✅ Assistant API responded
  4. ⬜ UI interaction (수동 확인 필요)
  5. ⬜ Error handling (수동 확인 필요)
```

## 규칙

- 코드를 수정하지 않는다. 실행과 확인만 수행한다.
- 서버 프로세스는 확인 후 종료한다.
- 시크릿을 출력하거나 요청하지 않는다.
