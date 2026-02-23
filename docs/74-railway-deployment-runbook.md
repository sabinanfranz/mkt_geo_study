# 74 — Railway Deployment Runbook

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
| `SEED_ON_START` | `false` | `false` |
| `CORS_ALLOW_ORIGINS` | `https://staging-domain` | `https://prod-domain` |

## 4) 배포 절차

1. `staging` 브랜치에 병합/푸시
2. Railway `staging` 자동 배포 완료 대기
3. 스모크 체크 실행
4. 테스트 통과 시 `main`에 반영
5. Railway `prod` 자동 배포 완료 대기
6. 동일 스모크 체크 실행

스모크 체크:

```bash
python scripts/check_deploy.py https://<env-domain>.up.railway.app
```

## 5) DB 마이그레이션/시드

앱 시작 시 `init_db()`가 마이그레이션을 자동 적용한다.

수동 실행(필요 시):

```bash
python scripts/db_migrate.py
python scripts/db_seed.py
```

시드 정책:

- 콘텐츠 테이블(`stages/modules/steps/options`)은 멱등 업서트
- 사용자 테이블(`user_progress/user_bookmarks`)은 삭제하지 않음

## 6) 롤백

증상: 배포 직후 `/api/health` 비정상, 주요 API 5xx

1. Railway에서 직전 성공 Deploy로 롤백
2. `/api/health` 확인
3. `/api/stages`, `/api/progress` 확인
4. 장애 원인 커밋 식별 후 staging에서 재검증

## 7) 트러블슈팅

### 앱은 뜨지만 데이터가 비어 있음

- `DATABASE_URL`이 올바른 환경 DB를 가리키는지 확인
- `python scripts/db_seed.py` 1회 실행

### CORS 에러

- `CORS_ALLOW_ORIGINS` 값에 실제 도메인 포함 확인
- 여러 개는 콤마로 구분

### 로컬에서 Postgres 테스트 필요

- 로컬 `.env`에 `DATABASE_URL=postgresql://...` 설정
- `python scripts/db_migrate.py` 후 서버 기동

## 8) 운영 체크리스트

- [ ] staging 배포 성공
- [ ] staging 스모크 체크 통과
- [ ] prod 배포 성공
- [ ] prod 스모크 체크 통과
- [ ] 변경 모듈/데이터 영향도 팀 공지
