# 76 — Railway 배포를 위한 코드 개선 내역

## 1) 문서 목적

이 문서는 Railway 배포 대응을 위해 코드베이스에 반영된 변경을 **구현 관점**에서 정리합니다.
운영 절차는 `docs/ops/74-railway-deployment-runbook.md`를 따르고, 본 문서는 "무엇이 어떻게 바뀌었는지"에 집중합니다.

---

## 2) 변경 요약

| 범주 | 변경 핵심 | 영향 |
|---|---|---|
| DB 계층 | SQLite 고정에서 SQLite/PostgreSQL 분기 지원 | Railway PostgreSQL 운영 가능 |
| 스키마 관리 | `run_migrations()` + `schema_migrations` 도입 | 시작 시 자동 마이그레이션 |
| 앱 기동 | lifespan에서 `init_db()` + 조건부 seed | 배포 직후 스키마 일관성 확보 |
| 쓰기 쿼리 | `INSERT OR REPLACE` 제거, `ON CONFLICT` 업서트로 통일 | PostgreSQL 호환 |
| 시드 정책 | 콘텐츠 멱등 업서트, 사용자 진척 보존 | 운영 데이터 유실 방지 |
| 배포 설정 | `railway.json`, `Procfile`, `runtime.txt` 추가 | Railway 표준 기동/헬스체크 지원 |
| 운영 스크립트 | migrate/seed/smoke check 스크립트 추가 | 수동 운영 절차 단순화 |
| 검증 | 배포 관련 DB 테스트 추가 | 마이그레이션/시드 안정성 보장 |

---

## 3) 파일별 상세 변경

## 3-1. DB 연결/마이그레이션

대상 파일:
- `apps/api/database.py`
- `apps/api/migrations/001_init.sqlite.sql`
- `apps/api/migrations/001_init.postgres.sql`

핵심 변경:
1. `get_db()`가 `DATABASE_URL` 기반으로 backend를 선택
2. PostgreSQL 연결을 위한 `psycopg` 도입
3. 기존 qmark(`?`) SQL을 PostgreSQL placeholder(`%s`)로 변환하는 호환 계층 추가
4. `run_migrations()` 추가
5. `schema_migrations` 테이블로 적용 이력 관리

운영 영향:
- 앱 시작 시 스키마 생성/적용이 자동화됨
- SQLite local / PostgreSQL Railway를 같은 코드 경로로 유지 가능

확장 시 주의:
- 신규 마이그레이션 추가 시 `*.sqlite.sql`, `*.postgres.sql`을 같은 버전명으로 쌍으로 관리
- raw SQL 작성 시 placeholder 규칙을 혼용하지 않도록 주의

## 3-2. 앱 런타임/환경변수 처리

대상 파일:
- `apps/api/main.py`

핵심 변경:
1. lifespan에서 `init_db()` 실행
2. `SEED_ON_START=true`일 때만 `seed(run_migrations=False)` 실행
3. `CORS_ALLOW_ORIGINS` 콤마 파싱 로직 추가
4. `INSERT OR REPLACE`를 `ON CONFLICT(user_id, step_id) DO UPDATE`로 변경

운영 영향:
- 재배포 시 스키마 누락으로 인한 기동 실패 위험 감소
- 운영 환경에서 seed 자동 실행 여부를 변수로 제어 가능
- PostgreSQL에서 진행 데이터 기록 로직 일관 동작

확장 시 주의:
- 운영 환경은 기본 `SEED_ON_START=false` 유지
- CORS는 `*` 대신 환경별 도메인으로 점진 제한 권장

## 3-3. 시드 정책 변경(데이터 보존)

대상 파일:
- `apps/api/seed.py`

핵심 변경:
1. `seed(run_migrations: bool = True)` 시그니처 도입
2. 콘텐츠 테이블(`stages/modules/steps/options`)만 멱등 업서트
3. `user_progress`, `user_bookmarks` 삭제 로직 제거
4. `order_idx` 기반 업데이트 규칙으로 반복 실행 가능

운영 영향:
- 콘텐츠 갱신과 사용자 학습 진척 보존을 분리해서 운영 가능

확장 시 주의:
- `order_idx`는 사실상 멱등 키이므로 변경 시 영향도 분석 필요
- 모듈/스텝 재배치 작업은 테스트 동반 필수

## 3-4. 배포 구성 파일 추가

대상 파일:
- `railway.json`
- `Procfile`
- `runtime.txt`
- `requirements.txt`
- `.env.example`

핵심 변경:
1. Railway start command/healthcheck 명시
2. Python 런타임 버전 고정
3. `psycopg[binary]` 의존성 추가
4. 환경변수 표준 샘플 제공(`DATABASE_URL`, `APP_ENV`, `SEED_ON_START`, `CORS_ALLOW_ORIGINS`)

운영 영향:
- Railway에서 별도 커맨드 입력 없이 기동 가능
- 환경별 변수 주입 방식 표준화

## 3-5. 운영/검증 스크립트 추가

대상 파일:
- `scripts/db_migrate.py`
- `scripts/db_seed.py`
- `scripts/check_deploy.py`
- `scripts/dev.ps1`

핵심 변경:
1. migrate 전용 스크립트 분리
2. seed 전용 스크립트 분리
3. 배포 후 `/api/health`, `/api/stages`, `/api/progress` 스모크 체크 스크립트 추가
4. 로컬 dev 스크립트에서 DB migrate+seed 자동 실행

운영 영향:
- 배포/장애 대응 시 표준 실행 커맨드가 명확해짐

---

## 4) 공개 인터페이스/환경변수 변화

| 항목 | 이전 | 이후 |
|---|---|---|
| DB backend | SQLite 고정 | SQLite(local) + PostgreSQL(Railway) |
| DB 연결 변수 | 파일 경로 중심 | `DATABASE_URL` 중심 |
| seed 제어 | 수동 실행 위주 | `SEED_ON_START` 조건부 자동 + 수동 병행 |
| CORS 설정 | `*` 고정 | `CORS_ALLOW_ORIGINS` 변수 기반 |

추가된/중요 환경변수:
- `DATABASE_URL`
- `APP_ENV`
- `SEED_ON_START`
- `CORS_ALLOW_ORIGINS`

---

## 5) 테스트 보장 범위

대상 파일:
- `tests/test_deploy_db.py`

보장하는 항목:
1. 마이그레이션 이력 기록(`schema_migrations`) 생성
2. seed 반복 실행 시 콘텐츠 테이블 count 불변(멱등)
3. seed 재실행 후 `user_progress` 보존

현재 미보장 항목:
1. PostgreSQL 실환경에서의 전체 API 회귀
2. 대규모 동시 요청 성능/잠금 시나리오
3. Railway 배포 파이프라인 자체(외부 환경) E2E 자동화

---

## 6) 알려진 리스크와 대응 가이드

리스크 1: `order_idx` 변경 시 기존 콘텐츠 매핑 오염
- 대응: 변경 전 매핑표 작성 + seed 실행 후 샘플 모듈 검증

리스크 2: 운영에서 실수로 `SEED_ON_START=true` 설정
- 대응: prod 변수 정책 체크리스트에 고정값 점검 추가

리스크 3: CORS 과도 허용
- 대응: 환경별 도메인 명시, `*`는 로컬/초기 검증에 한정

---

## 7) 후속 개선 제안

1. PostgreSQL 연결풀/타임아웃 옵션 명시화
2. 배포 후 smoke check를 CI 단계로 자동화
3. Postgres 전용 API 회귀 테스트 세트 분리
4. 마이그레이션 실패 알림 훅(로그/알림 채널) 추가

---

## 8) 관련 문서

- 배포 운영 런북: `docs/ops/74-railway-deployment-runbook.md`
- 아키텍처 문서: `docs/engineering/30-architecture.md`
- 프로젝트 개요/빠른 시작: `README.md`
- 의사결정 로그: `docs/tracking/90-log.md`
