# 31 — Visual Components Design

## 개요

GEO 학습 콘텐츠의 교육용 도식/시각화를 HTML/CSS 컴포넌트로 단계적으로 업그레이드하는 설계 문서.

**현황 요약:**
- 전체 도식 67개 중 40개(완전시각화) + 8개(부분시각화) + 17개(미시각화)
- 기존 6종 CSS 컴포넌트 사용 중
- CSS 클래스 불일치 6건 발견 (렌더링 영향 가능성)

**목표:**
- 신규 6종 CSS 컴포넌트 설계
- CSS 클래스 불일치 즉시 수정
- seed.py와 style.css 동기화

---

## 1. 기존 컴포넌트 현황 (6종)

### 1.1 `.browser-mockup` — 브라우저 화면 시뮬레이션

```html
<div class="browser-mockup">
  <div class="browser-bar">
    <span class="dot r"></span>
    <span class="dot y"></span>
    <span class="dot g"></span>
    <input type="text" class="browser-url" value="https://example.com">
  </div>
  <div class="browser-body">
    <div class="page-title">페이지 제목</div>
    <div class="page-element present">요소명</div>
    <div class="page-element missing">요소명</div>
  </div>
</div>
```

**사용:** 4회 (구글 검색결과 UI, 페이지 요소 분석)

---

### 1.2 `.compare-cards` — Before/After 비교표

```html
<div class="compare-cards">
  <div class="card before">
    <div class="card-header">Before</div>
    <div class="card-body"><ul><li>항목 1</li></ul></div>
  </div>
  <div class="card after">
    <div class="card-header">After</div>
    <div class="card-body"><ul><li>항목 1</li></ul></div>
  </div>
</div>
```

**사용:** 11회 (SEO vs GEO, 개선 전후 비교)

---

### 1.3 `.diagram-box` — 범용 다이어그램

```html
<div class="diagram-box">
  <div class="diagram-title">다이어그램 제목</div>
  <pre>ASCII art or structured text</pre>
</div>
```

**사용:** 9회 (RAG 파이프라인, 피라미드, KPI 계층)

---

### 1.4 `.callout` — 팁/경고/핵심포인트

```html
<div class="callout tip">
  <p>팁 내용...</p>
</div>

<div class="callout warning">
  <p>경고 내용...</p>
</div>

<div class="callout key-point">
  <p>핵심 내용...</p>
</div>

<div class="callout hint">
  <p>힌트 내용...</p>
</div>
```

**클래스:** `tip` | `warning` | `key-point` | `hint`
**사용:** 8회

---

### 1.5 `.code-example` — 코드 스니펫

```html
<div class="code-example">
  <div class="code-label">JSON-LD</div>
  <pre><code>{ "example": "code" }</code></pre>
</div>
```

**사용:** 6회 (스키마마크업, JSON 예시)

---

### 1.6 `.hierarchy-box` — 계층 구조

```html
<div class="hierarchy-box">
  <div class="hierarchy-title">제목</div>
  <div class="level-1">Level 1</div>
  <div class="level-2">Level 2a</div>
  <div class="level-2">Level 2b</div>
  <div class="level-3">Level 3</div>
</div>
```

**사용:** 2회 (헤딩 계층, 구조 맵)

---

## 2. CSS 클래스명 불일치 (즉시 수정사항)

### 2.1 불일치 목록

| # | seed.py 클래스명 | style.css 정의 | 상태 | 수정 방법 |
|----|------------------|-----------------|------|----------|
| 1 | `.callout-title` | 미정의 | 렌더링 깨짐 | HTML 구조 변경 또는 CSS 추가 |
| 2 | `.callout-body` | 미정의 | 렌더링 깨짐 | HTML 구조 변경 또는 CSS 추가 |
| 3 | `.browser-header` | `.browser-bar` | 틀림 | seed.py에서 `.browser-bar` 사용 |
| 4 | `.browser-dot` | `.dot.r/y/g` | 올바름 | 유지 |
| 5 | `.code-title` | `.code-label` | 틀림 | seed.py에서 `.code-label` 사용 |
| 6 | `.diagram-content` | 미정의 | 기능 영향 없음 | CSS 추가하거나 seed.py에서 제거 |

### 2.2 즉시 수정 우선순위

#### P1: seed.py 변경 (낮은 난이도)
```
- 3 곳 수정: .browser-header → .browser-bar / .code-title → .code-label
- 예상 변경량: 3줄
- 테스트: 페이지 렌더링 확인
```

#### P2: CSS 추가 (안전한 확장)
```
- .callout-title와 .callout-body를 선택적 서브클래스로 정의
- 기존 .callout 구조와 호환성 유지
- 예상 추가 줄 수: 10줄
```

---

## 3. 미시각화/부분시각화 항목 분석 (21건)

### 3.1 카테고리 A: 마크다운 테이블 → 시각적 비교표/데이터 카드 (9건)

#### A1. SEO vs GEO 5가지 차이 비교표
- **위치:** S1 M1-2 (GEO란 무엇인가)
- **현재:** 마크다운 테이블 (5행 × 3열)
- **추천:** `.comparison-table` 또는 `.data-cards`
- **콘텐츠:**
  - 목표 / 대상 엔진 / 핵심 신호 / 측정 지표 / 콘텐츠 형태

#### A2. 우선순위 매트릭스 (80/20)
- **위치:** S2 M2-7 (내부링크 전략)
- **현재:** 마크다운 테이블 (4행 × 4열)
- **추천:** `.priority-matrix` (임팩트×난이도 2축)
- **콘텐츠:**
  - 액션 / 효과 / 난이도 / 우선순위

#### A3. 포맷 비교표 (JSON-LD vs Microdata vs RDFa)
- **위치:** S3 M3-1 (스키마마크업 기초)
- **현재:** 마크다운 테이블 (3행 × 4열)
- **추천:** `.comparison-table`
- **콘텐츠:**
  - 포맷 / 삽입 위치 / 장점 / 단점

#### A4. Schema.org 주요 타입 테이블
- **위치:** S3 M3-1 ext (확장)
- **현재:** 마크다운 테이블 (4행 × 3열)
- **추천:** `.comparison-table`
- **콘텐츠:**
  - 타입 / 용도 / 예시

#### A5. Article 필수/권장 속성
- **위치:** S3 M3-3 (Article 스키마)
- **현재:** 마크다운 테이블
- **추천:** `.attribute-table` (필수/권장 분류)
- **콘텐츠:**
  - 속성명 / 타입 / 설명 / 필수 여부

#### A6. Event 스키마 핵심 속성
- **위치:** S3 M3-4 (Event 스키마)
- **현재:** 마크다운 테이블
- **추천:** `.attribute-table`
- **콘텐츠:**
  - 속성명 / 타입 / 설명 / 필수 여부

#### A7. AI 리퍼러 패턴표
- **위치:** S5 M5-3 ext (AI 리퍼러 분석)
- **현재:** 마크다운 테이블
- **추천:** `.comparison-table`
- **콘텐츠:**
  - AI 엔진 / 패턴 / 빈도 / 특이사항

#### A8. 인용 점수 계산법 테이블
- **위치:** S5 M5-4 (인용 점수 계산)
- **현재:** 마크다운 테이블
- **추천:** `.calculation-table` (수식 강조)
- **콘텐츠:**
  - 지표 / 가중치 / 예시 / 설명

#### A9. 전통 구조 vs Answer-first 비교
- **위치:** S2 M2-3 (콘텐츠 구조)
- **현재:** 마크다운 테이블
- **추천:** `.compare-cards` (기존 활용)
- **콘텐츠:**
  - 구조명 / 순서 / 장점 / 사용 사례

**카테고리 A 요약:** 9개 테이블 → 3종 신규 컴포넌트 필요

---

### 3.2 카테고리 B: ASCII 플로우차트 → 구조화된 플로우 (5건)

#### B1. RAG 5단계 파이프라인
- **위치:** S1 M1-3 (RAG 프로세스)
- **현재:** ASCII 플로우 (↓, →, ← 화살표)
  ```
  ① 쿼리 이해 → 의도 파악
      ↓
  ② 검색 → 관련 문서 탐색
      ↓
  ③ 랭킹 → 관련성 순위 결정
      ↓
  ④ 컨텍스트 주입 → 프롬프트에 삽입
      ↓
  ⑤ 답변 생성 → 출처 인용 포함
  ```
- **추천:** `.flow-chart` (수직 흐름)
- **특징:** 5단계, 각 단계별 설명

#### B2. 자동화 플로우 5단계
- **위치:** S5 M5-4 ext (자동화 운영)
- **현재:** ASCII 플로우
- **추천:** `.flow-chart`

#### B3. 실험 플로우 5단계
- **위치:** S5 M5-5 (A/B 테스트 설계)
- **현재:** ASCII 플로우
- **추천:** `.flow-chart`

#### B4. 90일 로드맵 4단계
- **위치:** S5 M5-6 (90일 로드맵)
- **현재:** ASCII 플로우
- **추천:** `.timeline-chart` (시간축 강조)
- **특징:** 4주/월 단계별 액션

#### B5. 지속 운영 방안
- **위치:** S5 M5-6 ext (지속 운영)
- **현재:** ASCII 플로우
- **추천:** `.cycle-chart` (순환 구조)

**카테고리 B 요약:** 5개 플로우 → 3종 신규 컴포넌트 필요

---

### 3.3 카테고리 C: ASCII 피라미드/계층 → 구조화된 피라미드/트리 (5건)

#### C1. GEO 5대 신호 피라미드
- **위치:** S1 M1-4 (GEO의 신호)
- **현재:** ASCII 피라미드 (┌, ┴, ┐ 문자)
  ```
         ┌─────────┐
        ┌┴─────────┴┐
       ┌┴───────────┴┐
      ┌┴─────────────┴┐
     ┌┴───────────────┴┐
     └─────────────────┘
  ```
- **추천:** `.pyramid-chart` (5 단계)
- **콘텐츠:** 기초→발전 계층도

#### C2. FAQPage 스키마 중첩 구조 트리
- **위치:** S3 M3-5 (FAQPage 스키마)
- **현재:** 코드블록 내 텍스트 계층도
- **추천:** `.tree-diagram` (계층 표현)
- **특징:** 중첩 들여쓰기

#### C3. MECE 5갈래 오프사이트 전략 트리
- **위치:** S4 M4-1 (오프사이트 전략)
- **현재:** 텍스트 트리 (들여쓰기)
- **추천:** `.tree-diagram`
- **특징:** 5개 가지 분기

#### C4. 백링크 품질 피라미드
- **위치:** S4 M4-2 (백링크 분석)
- **현재:** ASCII 피라미드
- **추천:** `.pyramid-chart`
- **특징:** 품질별 3~4 단계

#### C5. 엔터티 그래프: 브랜드 속성 연결 트리
- **위치:** S4 M4-4 (엔터티 그래프)
- **현재:** 텍스트 트리
- **추천:** `.tree-diagram`
- **특징:** 브랜드 중심 방사형

**카테고리 C 요약:** 5개 계층/피라미드 → 2종 신규 컴포넌트 필요

---

### 3.4 카테고리 D: KPI/적층 박스 → 레이어 컴포넌트 (3건)

#### D1. KPI 3층 적층 박스
- **위치:** S1 M1-5 (GEO 성공 지표)
- **현재:** ASCII 박스 (┌, ├, └ 문자)
  ```
  ┌──────────────────────────────────┐
  │    고객 행동 신호                │
  ├──────────────────────────────────┤
  │  → 클릭, 체류시간, 재방문        │
  ├──────────────────────────────────┤
  │  ← 콘텐츠 개선, UX 최적화       │
  └──────────────────────────────────┘
  ```
- **추천:** `.layer-box` (3~4 단계 수직)
- **특징:** 헤더 + 콘텐츠 + 액션

#### D2. 사이트 링크 구조도
- **위치:** S2 M2-1 (사이트 링크 구조)
- **현재:** 텍스트 + ASCII (│, └ 연결선)
- **추천:** `.tree-diagram` 또는 `.link-diagram`
- **특징:** 부모-자식 연결 시각화

#### D3. 내부링크 맵
- **위치:** S2 M2-6 (내부링크 맵)
- **현재:** ASCII 맵 (←→, ↓ 화살표)
  ```
  [홈] ←→ [문의] ←→ [개인정보]
   ↓      │
  [서비스] ──┘    [인사이트] ←→ [문의_mktg]
  ```
- **추천:** `.network-diagram` (쌍방향 연결)
- **특징:** 네트워크 토폴로지, 문제점 표시

**카테고리 D 요약:** 3개 레이어/구조도 → 2종 신규 컴포넌트 필요

---

### 3.5 카테고리 E: 텍스트 트리 → hierarchy-box (2건)

#### E1. H1>H2>H3 헤딩 계층도
- **위치:** S2 M2-5 (헤딩 구조)
- **현재:** hierarchy-box (존재)
- **상태:** 이미 시각화 완료
- **추천:** 유지

#### E2. 허브-클러스터 구조 다이어그램
- **위치:** S2 M2-2 (허브-클러스터 모델)
- **현재:** 텍스트 코드블록
- **추천:** `.tree-diagram` 업그레이드 또는 `.hub-cluster-diagram`
- **특징:** 중앙 허브 + 위성 클러스터

**카테고리 E 요약:** 1개 추가 필요

---

## 4. 신규 CSS 컴포넌트 설계 (6종)

### 4.1 `.comparison-table` — 다중열 비교표

**용도:** 카테고리 A의 테이블 대체 (9개 항목)

**HTML 구조:**
```html
<div class="comparison-table">
  <div class="comp-header">SEO vs GEO 비교</div>
  <table>
    <thead>
      <tr>
        <th>구분</th>
        <th>SEO</th>
        <th>GEO</th>
      </tr>
    </thead>
    <tbody>
      <tr class="highlight">
        <td class="label">목표</td>
        <td>검색 결과 상위 노출</td>
        <td>AI 답변의 인용 출처</td>
      </tr>
      <tr>
        <td class="label">핵심 신호</td>
        <td>백링크, 키워드</td>
        <td>콘텐츠 구조, 신뢰성</td>
      </tr>
    </tbody>
  </table>
</div>
```

**CSS 주요 규칙:**
```css
.comparison-table {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  margin: 16px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.comparison-table table {
  width: 100%;
  border-collapse: collapse;
}

.comparison-table th {
  background: #1a73e8;
  color: #fff;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.comparison-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  color: #333;
}

.comparison-table td.label {
  font-weight: 600;
  background: #f8f9fa;
  min-width: 100px;
}

.comparison-table tr.highlight td {
  background: #f0fdf4;
}

/* 다크모드 */
[data-theme="dark"] .comparison-table {
  background: #0f3460;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

[data-theme="dark"] .comparison-table th {
  background: #2563eb;
}

[data-theme="dark"] .comparison-table td {
  border-bottom-color: #1a4a7a;
  color: #d0d0d0;
}

[data-theme="dark"] .comparison-table td.label {
  background: #16213e;
  color: #f0f0f0;
}
```

**특징:**
- 행/열 강조 가능
- 모바일: 스크롤 가능 (overflow-x)
- 다크모드: 자동 대응
- 반응형: 너비 제한 없음

---

### 4.2 `.flow-chart` — 수직 플로우 다이어그램

**용도:** 카테고리 B의 플로우차트 (5개 항목)

**HTML 구조:**
```html
<div class="flow-chart">
  <div class="flow-title">RAG 5단계 파이프라인</div>
  <div class="flow-steps">
    <div class="flow-step">
      <div class="step-number">1</div>
      <div class="step-title">쿼리 이해</div>
      <div class="step-desc">사용자 질문 의도 파악</div>
      <div class="arrow">↓</div>
    </div>
    <div class="flow-step">
      <div class="step-number">2</div>
      <div class="step-title">검색</div>
      <div class="step-desc">관련 문서 탐색</div>
      <div class="arrow">↓</div>
    </div>
    <!-- ... 3-5단계 -->
    <div class="flow-step last">
      <div class="step-number">5</div>
      <div class="step-title">답변 생성</div>
      <div class="step-desc">출처 인용 포함</div>
    </div>
  </div>
</div>
```

**CSS 주요 규칙:**
```css
.flow-chart {
  background: #f8f9ff;
  border: 1px solid #d0d8f0;
  border-radius: 10px;
  padding: 20px;
  margin: 16px 0;
}

.flow-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.flow-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.flow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding: 16px 20px;
  background: #fff;
  border: 2px solid #1a73e8;
  border-radius: 8px;
  margin-bottom: 8px;
  text-align: center;
}

.step-number {
  display: inline-block;
  width: 36px;
  height: 36px;
  background: #1a73e8;
  color: #fff;
  border-radius: 50%;
  font-weight: 700;
  line-height: 36px;
  margin-bottom: 8px;
}

.step-title {
  font-weight: 600;
  color: #222;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.85rem;
  color: #666;
}

.arrow {
  font-size: 1.2rem;
  color: #1a73e8;
  margin-top: 8px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flow-step.last .arrow {
  display: none;
}

/* 다크모드 */
[data-theme="dark"] .flow-chart {
  background: #0f1a30;
  border-color: #2a3a5c;
}

[data-theme="dark"] .flow-title {
  color: #f0f0f0;
}

[data-theme="dark"] .flow-step {
  background: #16213e;
  border-color: #3b82f6;
}

[data-theme="dark"] .step-number {
  background: #2563eb;
}

[data-theme="dark"] .step-title {
  color: #f0f0f0;
}

[data-theme="dark"] .step-desc {
  color: #b0b0b0;
}

[data-theme="dark"] .arrow {
  color: #60a5fa;
}
```

**특징:**
- 1~6 단계 지원
- 번호 원형 배지
- 화살표 자동 표시
- 마지막 단계에서 화살표 숨김
- 모바일: 수직 유지 (자동 줄 바꿈 없음)

---

### 4.3 `.pyramid-chart` — 피라미드 다이어그램

**용도:** 카테고리 C의 피라미드 (2개 항목)

**HTML 구조:**
```html
<div class="pyramid-chart">
  <div class="pyramid-title">GEO 5대 신호</div>
  <div class="pyramid-container">
    <div class="pyramid-level" style="--level: 1; --total: 5;">
      <div class="level-content">콘텐츠 구조</div>
    </div>
    <div class="pyramid-level" style="--level: 2; --total: 5;">
      <div class="level-content">신뢰성 신호</div>
    </div>
    <div class="pyramid-level" style="--level: 3; --total: 5;">
      <div class="level-content">인용 빈도</div>
    </div>
    <div class="pyramid-level" style="--level: 4; --total: 5;">
      <div class="level-content">사이트 신호</div>
    </div>
    <div class="pyramid-level" style="--level: 5; --total: 5;">
      <div class="level-content">AI 선호도</div>
    </div>
  </div>
</div>
```

**CSS 주요 규칙:**
```css
.pyramid-chart {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  margin: 16px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  text-align: center;
}

.pyramid-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 16px;
}

.pyramid-container {
  display: flex;
  flex-direction: column;
  gap: 0;
  align-items: center;
}

.pyramid-level {
  --width-ratio: calc(1 - (var(--level) - 1) / (var(--total) - 1) * 0.4);
  width: calc(100% * var(--width-ratio));
  padding: 12px 16px;
  background: linear-gradient(135deg, #1a73e8, #3b82f6);
  color: #fff;
  border-radius: 4px;
  margin-bottom: 2px;
  font-weight: 600;
  font-size: 0.88rem;
  position: relative;
}

.pyramid-level:nth-child(2) {
  background: linear-gradient(135deg, #1557b0, #2563eb);
}

.pyramid-level:nth-child(3) {
  background: linear-gradient(135deg, #1a5c99, #1a73e8);
}

.pyramid-level:nth-child(4) {
  background: linear-gradient(135deg, #1d4a82, #1557b0);
}

.pyramid-level:nth-child(5) {
  background: linear-gradient(135deg, #0f3460, #1a3a5c);
  color: #e0e0e0;
}

/* 다크모드 */
[data-theme="dark"] .pyramid-chart {
  background: #0f3460;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

[data-theme="dark"] .pyramid-title {
  color: #f0f0f0;
}

[data-theme="dark"] .pyramid-level {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
}

[data-theme="dark"] .pyramid-level:nth-child(5) {
  background: linear-gradient(135deg, #16213e, #1a2a4e);
  color: #d0d0d0;
}
```

**특징:**
- 3~5 단계 (CSS variables로 동적)
- 상단이 좁고 하단이 넓은 삼각형
- 그라데이션 배경으로 깊이감 표현
- 각 단계별 다른 색상

---

### 4.4 `.tree-diagram` — 계층형 트리 다이어그램

**용도:** 카테고리 C, D, E의 계층 구조 (8개 항목)

**HTML 구조:**
```html
<div class="tree-diagram">
  <div class="tree-title">FAQPage 스키마 구조</div>
  <ul class="tree">
    <li class="tree-item">
      <span class="tree-node">FAQPage</span>
      <ul class="tree">
        <li class="tree-item">
          <span class="tree-node">mainEntity (배열)</span>
          <ul class="tree">
            <li class="tree-item">
              <span class="tree-node">Question</span>
              <ul class="tree">
                <li class="tree-item">
                  <span class="tree-node">name</span>
                </li>
                <li class="tree-item">
                  <span class="tree-node">acceptedAnswer</span>
                  <ul class="tree">
                    <li class="tree-item">
                      <span class="tree-node">text</span>
                    </li>
                  </ul>
                </li>
              </ul>
            </li>
          </ul>
        </li>
      </ul>
    </li>
  </ul>
</div>
```

**CSS 주요 규칙:**
```css
.tree-diagram {
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  margin: 16px 0;
}

.tree-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.tree {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.tree-item {
  margin: 4px 0;
  position: relative;
  padding-left: 24px;
}

.tree-item > .tree {
  padding-left: 20px;
  margin-top: 4px;
}

.tree-node {
  display: inline-block;
  padding: 4px 8px;
  background: #e8f0fe;
  border-left: 3px solid #1a73e8;
  border-radius: 0 4px 4px 0;
  font-size: 0.88rem;
  color: #1557b0;
  font-family: monospace;
}

.tree-item::before {
  content: "└ ";
  position: absolute;
  left: 4px;
  color: #ccc;
  font-weight: bold;
}

.tree-item:first-child .tree-item::before {
  content: "├ ";
}

/* 다크모드 */
[data-theme="dark"] .tree-diagram {
  background: #0f1a30;
  border-color: #2a3a5c;
}

[data-theme="dark"] .tree-title {
  color: #f0f0f0;
}

[data-theme="dark"] .tree-node {
  background: #16213e;
  border-left-color: #3b82f6;
  color: #90b8f0;
}
```

**특징:**
- 무한 중첩 지원
- 들여쓰기 자동 계산
- 트리선 자동 렌더링 (::before)
- 각 노드별 강조 스타일

---

### 4.5 `.layer-box` — 수직 레이어 컴포넌트

**용도:** 카테고리 D의 KPI/적층 박스 (3개 항목)

**HTML 구조:**
```html
<div class="layer-box">
  <div class="layer-title">GEO 성공 지표 (KPI)</div>
  <div class="layer">
    <div class="layer-label">고객 행동 신호</div>
    <div class="layer-content">
      <ul>
        <li>클릭률 (CTR)</li>
        <li>페이지 체류시간</li>
        <li>재방문율</li>
      </ul>
    </div>
  </div>
  <div class="layer-arrow">↕</div>
  <div class="layer">
    <div class="layer-label">콘텐츠 최적화</div>
    <div class="layer-content">
      <ul>
        <li>구조화된 마크업</li>
        <li>명확한 헤딩</li>
        <li>인용 가능성 향상</li>
      </ul>
    </div>
  </div>
</div>
```

**CSS 주요 규칙:**
```css
.layer-box {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  margin: 16px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.layer-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.layer {
  background: #f8f9ff;
  border: 2px solid #1a73e8;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}

.layer-label {
  background: #1a73e8;
  color: #fff;
  padding: 10px 16px;
  font-weight: 700;
  font-size: 0.88rem;
}

.layer-content {
  padding: 12px 16px;
  color: #333;
  font-size: 0.88rem;
}

.layer-content ul {
  margin: 0;
  padding-left: 18px;
}

.layer-content li {
  margin-bottom: 4px;
}

.layer-arrow {
  text-align: center;
  color: #1a73e8;
  font-size: 1.2rem;
  margin: 8px 0;
}

/* 다크모드 */
[data-theme="dark"] .layer-box {
  background: #0f3460;
  border-color: #2a3a5c;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

[data-theme="dark"] .layer-title {
  color: #f0f0f0;
}

[data-theme="dark"] .layer {
  background: #16213e;
  border-color: #3b82f6;
}

[data-theme="dark"] .layer-label {
  background: #2563eb;
}

[data-theme="dark"] .layer-content {
  color: #d0d0d0;
}

[data-theme="dark"] .layer-arrow {
  color: #60a5fa;
}
```

**특징:**
- 2~4 레이어 지원
- 레이어 간 연결선 표시
- 헤더 강조
- 내부 리스트 자동 스타일

---

### 4.6 `.network-diagram` — 네트워크 연결 다이어그램

**용도:** 카테고리 D의 내부링크 맵 (1개 항목)

**HTML 구조:**
```html
<div class="network-diagram">
  <div class="network-title">내부링크 맵</div>
  <div class="network-canvas">
    <div class="network-node hub">
      <div class="node-label">홈</div>
    </div>
    <div class="network-node">
      <div class="node-label">서비스</div>
    </div>
    <div class="network-node">
      <div class="node-label">문의</div>
    </div>
    <div class="network-node">
      <div class="node-label">개인정보</div>
    </div>
  </div>
  <div class="network-legend">
    <div class="legend-item"><span class="link solid"></span>양방향 링크</div>
    <div class="legend-item"><span class="link broken"></span>누락된 링크</div>
  </div>
</div>
```

**CSS 주요 규칙:**
```css
.network-diagram {
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  margin: 16px 0;
}

.network-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.network-canvas {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
  min-height: 150px;
}

.network-node {
  background: #e8f0fe;
  border: 2px solid #1a73e8;
  border-radius: 8px;
  padding: 12px 16px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50px;
}

.network-node.hub {
  background: #1a73e8;
  color: #fff;
  font-weight: 700;
}

.node-label {
  font-size: 0.9rem;
  font-weight: 600;
}

.network-legend {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
  font-size: 0.85rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.link {
  display: inline-block;
  width: 20px;
  height: 2px;
}

.link.solid {
  background: #34a853;
}

.link.broken {
  background: #ea4335;
  border-bottom: 2px dashed #ea4335;
  height: 0;
}

/* 다크모드 */
[data-theme="dark"] .network-diagram {
  background: #0f1a30;
  border-color: #2a3a5c;
}

[data-theme="dark"] .network-title {
  color: #f0f0f0;
}

[data-theme="dark"] .network-node {
  background: #16213e;
  border-color: #3b82f6;
  color: #d0d0d0;
}

[data-theme="dark"] .network-node.hub {
  background: #2563eb;
  color: #fff;
}

[data-theme="dark"] .network-legend {
  border-top-color: #2a3a5c;
}
```

**특징:**
- 그리드 배치 (4열)
- 중앙 허브 강조
- 양방향/단방향 표시
- 설명 범례 포함

---

## 5. CSS 추가 줄 수 및 작업량 예상

### 5.1 신규 컴포넌트 CSS 추가량

| 컴포넌트 | 라이트 모드 | 다크 모드 | 합계 | 우선순위 |
|---------|-----------|---------|------|---------|
| `.comparison-table` | 50 | 30 | 80 | P2 |
| `.flow-chart` | 70 | 40 | 110 | P2 |
| `.pyramid-chart` | 60 | 35 | 95 | P3 |
| `.tree-diagram` | 55 | 30 | 85 | P3 |
| `.layer-box` | 50 | 25 | 75 | P2 |
| `.network-diagram` | 45 | 25 | 70 | P3 |
| **소계** | **330** | **185** | **515** | — |

### 5.2 CSS 클래스 불일치 수정

| 항목 | 변경 위치 | 변경량 | 우선순위 |
|------|---------|--------|---------|
| `.callout-title/body` 추가 | style.css | +10줄 | P1 |
| `.browser-header` → `.browser-bar` | seed.py | 1줄 | P1 |
| `.code-title` → `.code-label` | seed.py | 2줄 | P1 |
| 기타 미정의 클래스 정정 | style.css | +5줄 | P1 |
| **소계** | — | **18줄** | — |

### 5.3 seed.py 마이그레이션

| 단계 | 작업 | 항목 수 | 시간 예상 |
|------|------|--------|---------|
| P1 | CSS 클래스 정정 | 3개 | 30분 |
| P2 | `.comparison-table` 변환 | 9개 | 2시간 |
| P2 | `.flow-chart` 변환 | 5개 | 1.5시간 |
| P2 | `.layer-box` 변환 | 3개 | 1시간 |
| P3 | `.pyramid-chart` 변환 | 5개 | 1.5시간 |
| P3 | `.tree-diagram` 변환 | 8개 | 2시간 |
| P3 | `.network-diagram` 변환 | 1개 | 30분 |
| **합계** | — | **34개** | **8.5시간** |

---

## 6. 마이그레이션 로드맵

### Phase 1: 즉시 수정 (30분)
```
1. style.css에 .callout-title, .callout-body 정의 추가
2. seed.py에서 .browser-header → .browser-bar 교체
3. seed.py에서 .code-title → .code-label 교체
4. 페이지 렌더링 확인
```

### Phase 2: 신규 컴포넌트 CSS 작성 (2시간)
```
1. style.css 끝에 6개 신규 컴포넌트 CSS 추가 (515줄)
2. 각 컴포넌트별 라이트/다크 모드 테스트
3. 반응형 모바일 확인
```

### Phase 3: seed.py 마이그레이션 (6시간)
```
우선순위:
  P2-A: .comparison-table (9개)
  P2-B: .flow-chart (5개)
  P2-C: .layer-box (3개)
  P3-A: .pyramid-chart (5개)
  P3-B: .tree-diagram (8개)
  P3-C: .network-diagram (1개)
```

### Phase 4: 통합 테스트 (1시간)
```
1. 모든 화면에서 도식 렌더링 확인
2. 다크모드 전환 확인
3. 모바일 반응형 확인
```

---

## 7. 기술 고려사항

### 7.1 marked.js와의 통합
- HTML 문자열이 seed.py에 작성되어 marked.js가 렌더링
- CSS는 렌더링된 HTML에 적용됨
- JavaScript 코드는 최소화 (app.js 수정 불필요)

### 7.2 다크모드 대응
- 모든 신규 컴포넌트는 `[data-theme="dark"]` 선택자로 스타일 정의
- 기존 패턴: 컬러 역전 + 대비도 유지
- 테스트: theme toggle 버튼으로 확인

### 7.3 반응형 설계
- 데스크톱(800px) 기준
- 태블릿(600px): 일부 컴포넌트 단일열 전환
  - .comparison-table: 스크롤 유지
  - .network-diagram: 2x2 그리드
  - .pyramid-chart: 100% 너비
- 모바일: MVP에서 제외 (문서 언급)

### 7.4 접근성 (A11y)
- 모든 컴포넌트에 `role` 속성 고려
- 색상 대비 WCAG AA 준수 (모든 텍스트)
- 시맨틱 HTML 사용 (`<table>`, `<ul>`, `<section>` 등)

---

## 8. 체크리스트

### CSS 작성 전
- [ ] 6개 신규 컴포넌트 HTML 구조 확정
- [ ] 다크모드 색상표 준비
- [ ] 모바일 브레이크포인트 정의 (필요시)

### CSS 작성 후
- [ ] 각 컴포넌트 라이트 모드 시각 테스트
- [ ] 각 컴포넌트 다크 모드 시각 테스트
- [ ] 크로스 브라우저 테스트 (Chrome, Firefox, Safari)

### seed.py 마이그레이션 후
- [ ] 각 항목별 렌더링 확인
- [ ] 테이블 데이터 완전성 검증
- [ ] 콘텐츠 문맥 유지 확인

### 통합 테스트
- [ ] 모든 Stage/Module 페이지 로드 확인
- [ ] 다크모드 toggle 확인
- [ ] 스크린 리더 테스트 (선택)
- [ ] 모바일 화면 크기 확인

---

## 9. 다음 단계

1. **설계 검증**: 이 문서를 팀과 공유하고 피드백 수집
2. **프로토타입**: 1~2개 신규 컴포넌트 CSS 선행 작성
3. **구현**: Phase 1부터 순차적 진행
4. **릴리스**: 각 Phase 완료 후 main 브랜치 merge

---

## 부록 A: 신규 컴포넌트 마크다운 작성 가이드

### .comparison-table 예시
```html
<div class="comparison-table">
  <div class="comp-header">SEO vs GEO</div>
  <table>
    <thead>
      <tr><th>구분</th><th>SEO</th><th>GEO</th></tr>
    </thead>
    <tbody>
      <tr class="highlight">
        <td class="label">목표</td>
        <td>검색 결과 상위 노출</td>
        <td>AI 답변 인용 출처</td>
      </tr>
    </tbody>
  </table>
</div>
```

### .flow-chart 예시
```html
<div class="flow-chart">
  <div class="flow-title">5단계 프로세스</div>
  <div class="flow-steps">
    <div class="flow-step">
      <div class="step-number">1</div>
      <div class="step-title">단계 1</div>
      <div class="step-desc">설명...</div>
      <div class="arrow">↓</div>
    </div>
    <!-- ... -->
  </div>
</div>
```

---

**문서 버전:** v1.0
**작성 일자:** 2026-02-22
**담당:** frontend-dev, ux-designer
**상태:** 설계 완료, 구현 준비
