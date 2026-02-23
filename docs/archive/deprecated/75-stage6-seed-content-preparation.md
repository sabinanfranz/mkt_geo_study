> **⚠️ 이 문서는 폐기되었습니다.** Stage 6은 `docs/strategy/73-geo-action-plan.md` 기반으로 재구성되었습니다.
> 새 설계: `docs/strategy/77-stage6-curriculum-design.md` 참조.

# 75 — Stage 6 시드 콘텐츠 준비 프로세스 (LLM Handoff) — ~~DEPRECATED~~

## 1) 문서 목적

이 문서는 **Stage 6 시드 콘텐츠를 어떻게 마련했는지**를 타 LLM이 재현 가능하게 전달하기 위한 제작 근거 문서다.

- 대상 구현: `apps/api/seed.py`의 Stage 6 (`id=6`) 블록
- 대상 도메인: `b2b.fastcampus.co.kr` 운영형 GEO 과업
- 독자: 다음 차수의 LLM/엔지니어(콘텐츠 개정, 모듈 추가, 테스트 확장 담당)

핵심 질문:
1. 어떤 입력 소스를 어떤 기준으로 선별했는가?
2. 전략 항목을 seed 구조(module/step/option)로 어떻게 변환했는가?
3. 품질 기준과 검증은 어떤 테스트로 보장하는가?

---

## 2) 범위와 비범위

### In Scope
- Stage 6의 제작 입력, 변환 로직, 시드 반영 규칙, 테스트 연결
- Stage 6 구성 단위: 7 modules / 28 steps / 84 options
- 운영형 학습 설계를 위한 품질 규칙(피드백 톤/길이, 평가 호환성)

### Out of Scope
- Stage 1~5 상세 제작 과정
- 프론트엔드 UI 디자인 상세
- Railway 운영 절차 상세

---

## 3) 입력 소스와 선별 기준

### 3-1. 입력 소스 매핑

| 소스 | 추출한 핵심 | Stage 6 반영 위치 |
|---|---|---|
| `materials/b2b.fastcampus.co.kr를 위한 GEO 심층 리서치 및 90일 실행 로드맵.md` | L1~L5 온사이트, 오프사이트, 측정, 90일 로드맵 | M6-2~M6-7 과업 축 |
| `materials/strategy/b2b.fastcampus.co.kr GEO 가시성 극대화 전략서.md` | 실행 우선순위, 페이지/채널 매핑 | M6-2, M6-5, M6-6 |
| `docs/strategy/73-geo-action-plan.md` | 90일 액션 아이템과 KPI 구조 | M6-1 운영 리듬, M6-7 제출물 |
| `data/crawled/*.json`, `_report.md` | 실제 사이트 구조/링크/스키마 이슈 | M6-2~M6-4 실무 시나리오 |
| `docs/archive/deprecated/71-stage6-task-module-strategy.md` | 전략 축과 모듈 매핑 원칙 | Stage 6 모듈 골격 |

### 3-2. 선별 기준

전략 아이템을 seed에 포함할 때 다음 기준을 모두 만족해야 채택했다.

1. **즉시 실행성**: 다음 주 바로 실행 가능한가
2. **운영 반복성**: 주간/월간 루틴으로 반복 가능한가
3. **산출물 명시성**: 결과물이 문서/로그 형태로 남는가
4. **KPI 연결성**: Visibility/Behavior/Authority 중 최소 1개와 연결되는가
5. **검증 가능성**: step/quiz/practice로 판단 기준을 만들 수 있는가

---

## 4) 전략에서 Seed로 변환한 규칙

### 4-1. 전략 축 → 모듈 변환 규칙

Stage 6는 전략 축 7개를 모듈 7개로 1:1 변환했다.

| 전략 축 | 모듈 |
|---|---|
| 운영 거버넌스 | M6-1 운영 킥오프 & 역할 정렬 |
| 페이지 구조 최적화 | M6-2 서비스 페이지 리모델링 과업 |
| 구조화데이터 품질 | M6-3 스키마 구현 & 검증 과업 |
| IA/내부링크 | M6-4 허브-클러스터 내부링크 과업 |
| 오프사이트 실행 | M6-5 오프사이트 배포 & 멘션 과업 |
| 측정/리포팅 루프 | M6-6 AI Validator & KPI 리포팅 과업 |
| 통합 운영 역량 | M6-7 Stage 6 캡스톤 평가 |

### 4-2. 모듈 → Step 변환 규칙

실행형 모듈은 아래 패턴으로 고정했다.

- 일반 모듈(M6-1~M6-6): `1 Reading + 1 Quiz + 2 Practice = 4 steps`
- 평가 모듈(M6-7): `1 Reading + 2 Quiz + 1 Practice = 4 steps`

설계 이유:
- `Reading`: SOP/체크리스트/템플릿 전달
- `Quiz`: 실행 판단 기준 고정
- `Practice`: 우선순위/시나리오 의사결정 훈련

### 4-3. Step → Option 변환 규칙

- `quiz`, `practice`는 기본 4지선다로 구성
- 각 step마다 정답 1개 + 오답 3개를 고정
- 오답은 실무에서 자주 나오는 실패 패턴(순서 오류, 목표-지표 분리, 근거 누락)으로 설계

### 4-4. 운영형 서술 규칙

Stage 6의 reading은 개념 설명보다 운영 실행 요소를 우선 배치했다.

1. 실행 순서
2. 완료 정의(DoD)
3. 주간/월간 산출물
4. 복붙 가능한 템플릿(필요시 extension_md)

---

## 5) Seed 구현 제약과 호환성 규칙

### 5-1. Stage 해제 제약

- Stage 6 unlock 조건:
  - `{"require_stage_complete": 5, "min_score_pct": 70}`
- 반영 위치: `apps/api/seed.py`

### 5-2. 평가 API 호환성 제약

`/api/stages/{id}/evaluate`는 **해당 stage의 마지막 모듈 quiz**를 평가한다.

따라서 Stage 6 마지막 모듈(M6-7)에는 quiz step이 반드시 포함되어야 한다.

### 5-3. 멱등 시드 구조 제약

현재 seed helper는 아래 키로 멱등 업데이트된다.

- `modules`: `(stage_id, order_idx)`
- `steps`: `(module_id, order_idx)`
- `options`: `(step_id, order_idx)`

즉, Stage 6 수정 시에는 `order_idx` 안정성이 가장 중요하다.

---

## 6) 품질 규칙 (콘텐츠/피드백)

### 6-1. 피드백 품질 규칙

Stage 6 포함 전체 옵션 피드백은 아래 규칙을 충족해야 한다.

1. 최소 길이: 40자 이상
2. 존댓말 어미 유지
3. 단순 정오답 통보가 아니라 "왜"와 "어떻게"를 포함

### 6-2. 운영형 문장 규칙

1. 모호한 표현 금지(예: "적절히", "잘")
2. 역할/기한/판단기준 명시형 문장 우선
3. 액션 가능한 동사 사용(확정, 검증, 재측정, 에스컬레이션)

---

## 7) 검증 체계와 테스트 연결

### 7-1. 데이터 수량 기준

실제 시드 기준 Stage 6 수량:
- modules: 7
- steps: 28
- options: 84

### 7-2. 테스트 맵

| 검증 항목 | 테스트 위치 |
|---|---|
| Stage 6 unlock_condition | `tests/test_phase2.py::test_stage6_unlock_condition` |
| Stage 6 모듈 수(7) | `tests/test_phase2.py::test_stage6_has_seven_modules` |
| Stage 6 모듈별 step 수(4) | `tests/test_phase2.py::test_stage6_step_counts` |
| 평가 모듈 quiz 존재 | `tests/test_phase2.py::test_stage6_eval_module_has_quiz_steps` |
| 피드백 최소 길이 | `tests/test_phase2.py::test_all_feedback_min_length` |
| 피드백 존댓말 | `tests/test_phase2.py::test_all_feedback_polite_form` |

---

## 8) 재생산 SOP (다음 LLM용)

Stage 6를 개정/확장할 때 아래 순서를 고정한다.

1. 입력 소스에서 신규 전략 항목 추출
2. 기존 7축과 중복 여부 판단
3. 신규 항목을 기존 모듈에 흡수할지, 신규 모듈로 분리할지 결정
4. 모듈별 step 패턴(Reading/Quiz/Practice)에 맞게 재배치
5. 옵션 4지선다 + 피드백 품질 규칙 반영
6. `seed.py`에서 `order_idx` 충돌 없이 반영
7. `tests/test_phase2.py`에 수량/호환성/품질 검증 추가
8. `docs/archive/deprecated/71-stage6-task-module-strategy.md`, `docs/archive/deprecated/75-stage6-seed-content-preparation.md`, `docs/tracking/90-log.md` 동기화

---

## 9) 자주 발생하는 실패 패턴

1. **전략은 맞지만 실행 단위가 아닌 경우**
- 증상: reading만 길고 quiz/practice가 추상적
- 대응: 산출물/담당/마감/판단기준 문장으로 환원

2. **평가 모듈 호환성 누락**
- 증상: 마지막 모듈에 quiz 없음
- 대응: M6-7의 quiz 최소 1개 이상 유지

3. **order_idx 변경으로 멱등성 깨짐**
- 증상: 기존 step/option이 의도와 다르게 갱신
- 대응: 변경 전에 order_idx 매핑표 작성 후 반영

4. **피드백 품질 규칙 누락**
- 증상: 짧은 문장/반말/근거 없는 피드백
- 대응: 테스트와 수동 리뷰를 동시에 통과하도록 작성

---

## 10) 핸드오프 체크리스트

- [ ] Stage 6 수량(7/28/84) 유지 또는 변경 근거 문서화
- [ ] M6-7 평가 호환성(quiz 포함) 확인
- [ ] 피드백 품질 규칙(길이/존댓말/설명성) 확인
- [ ] 테스트 케이스 업데이트 반영
- [ ] 전략 문서(`docs/archive/deprecated/71-stage6-task-module-strategy.md`)와 제작 근거 문서(`docs/archive/deprecated/75-stage6-seed-content-preparation.md`) 동시 갱신

---

## 한 줄 요약

Stage 6 시드는 "전략 설명"이 아니라 "다음 주 실행 가능한 운영 단위"를 기준으로 구성되었고, 그 결과를 **7개 모듈/28개 스텝/84개 옵션 + 평가/품질 테스트**로 고정한 실행형 캡스톤 데이터셋이다.
