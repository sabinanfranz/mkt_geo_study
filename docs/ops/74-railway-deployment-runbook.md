# 74 — Railway Deployment Runbook

관련 구현 문서:
- Railway 코드 변경 상세: `docs/ops/76-railway-code-changes.md`

## 1) 목표

- 설치 없는 팀 배포를 Railway 상시 URL 배포로 전환
- `staging` 검증 후 `prod` 반영의 2단계 배포 체계 유지
- 콘텐츠 시드 업데이트 시 사용자 학습 진척(`user_progress`) 보존

## 2) 환경 구성

- Railway Project 1개
- Environment 2개
- `staging`
- `prod`
- 각 환경에 PostgreSQL 별도 연결

권장 브랜치 매핑:

- `staging` environment <- `staging` branch
- `prod` environment <- `main` branch

## 3) 필수 변수

| 키 | staging 예시 | prod 예시 |
|---|---|---|
| `APP_ENV` | `staging` | `prod` |
| `DATABASE_URL` | Railway Postgres connection string | Railway Postgres connection string |
| `SEED_ON_START` | `true` | `true` |
| `CORS_ALLOW_ORIGINS` | `https://staging-domain` | `https://prod-domain` |
| `SESSION_SECRET` | 랜덤 긴 문자열 | 랜덤 긴 문자열(필수) |
| `SESSION_TTL_SECONDS` | `604800` | `604800` |

주의:
- `SEED_ON_START=true`이면 배포 시(앱 시작 시) 시드가 자동 실행된다. 멱등 업서트이므로 user_progress는 보존된다.
- `SESSION_SECRET`를 비워두면 개발용 기본값으로 동작하므로, `staging`/`prod`에서는 반드시 설정한다.
- `SESSION_TTL_SECONDS` 기본값은 604800(7일)이며 필요 시 단축한다.

## 4) 배포 절차

1. `staging` 브랜치에 병합/푸시
2. Railway `staging` 자동 배포 완료 대기
3. 스모크 체크 실행
4. 테스트 통과 시 `main`에 반영
5. Railway `prod` 자동 배포 완료 대기
6. 동일 스모크 체크 실행

스모크 체크(인증 포함):

```bash
BASE_URL=https://<env-domain>.up.railway.app

# 1) health
curl -fsS "$BASE_URL/api/health"

# 2) login -> token
TOKEN=$(
  curl -fsS -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"b2b_mkt_1","password":"b2b_mkt_1"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])"
)

# 3) auth-required endpoints
curl -fsS -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/stages" > /dev/null
curl -fsS -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/progress" > /dev/null
```

참고:
- `scripts/check_deploy.py`는 인증 도입 이전 스모크 시나리오 기준이므로, 운영 표준 체크는 위 절차를 사용한다.

## 5) DB 마이그레이션/시드

앱 시작 시 `init_db()`가 마이그레이션을 자동 적용한다.

수동 실행(필요 시):

```bash
python scripts/db_migrate.py
python scripts/db_seed.py
```

최초 1회 시드 실행 전 확인:
- Railway 서비스가 최신 커밋으로 1회 이상 정상 배포 완료
- `DATABASE_URL`이 목표 환경 DB를 가리키는지 확인
- `requirements.txt` 기준 의존성이 설치된 이미지인지 확인(`psycopg` 누락 방지)

시드 정책:

- 콘텐츠 테이블(`stages/modules/steps/options`)은 멱등 업서트
- 사용자 테이블(`user_progress/user_bookmarks`)은 삭제하지 않음
- 퀴즈 정답 라벨은 시드 실행 시 A/B/C 기준으로 균등 재분배되고, 결과 분포가 로그로 출력됨(`D`는 정답 라벨로 배정하지 않음)

## 6) 롤백

증상: 배포 직후 `/api/health` 비정상, 주요 API 5xx

1. Railway에서 직전 성공 Deploy로 롤백
2. `/api/health` 확인
3. `/api/auth/login`으로 토큰 발급 후 `/api/stages`, `/api/progress` 확인
4. 장애 원인 커밋 식별 후 staging에서 재검증

## 7) 트러블슈팅

### 앱은 뜨지만 데이터가 비어 있음

- `DATABASE_URL`이 올바른 환경 DB를 가리키는지 확인
- `python scripts/db_seed.py` 1회 실행

### CORS 에러

- `CORS_ALLOW_ORIGINS` 값에 실제 도메인 포함 확인
- 여러 개는 콤마로 구분

### `/api/stages`, `/api/progress`가 401 반환

- `Authorization: Bearer <token>` 헤더 포함 여부 확인
- `/api/auth/login` 요청 계정이 `b2b_mkt_1`~`b2b_mkt_10` 형식이며, 비밀번호가 동일한지 확인
- `SESSION_SECRET` 변경 직후 기존 토큰은 무효화되므로 재로그인 필요

### 로컬에서 Postgres 테스트 필요

- 로컬 `.env`에 `DATABASE_URL=postgresql://...` 설정
- `python scripts/db_migrate.py` 후 서버 기동

## 8) 운영 체크리스트

- [ ] staging 배포 성공
- [ ] staging 스모크 체크 통과
- [ ] prod 배포 성공
- [ ] prod 스모크 체크 통과
- [ ] 변경 모듈/데이터 영향도 팀 공지
