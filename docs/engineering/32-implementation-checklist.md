# 32 — Implementation Checklist

단계별 CSS 컴포넌트 구현 및 seed.py 마이그레이션 체크리스트.

---

## Phase 1: CSS 클래스 불일치 즉시 수정 (30분)

### 1.1 style.css 수정

#### Task 1.1.1: `.callout-title`, `.callout-body` 정의 추가

**위치:** `/apps/web/css/style.css` 라인 1720 이후

**추가할 CSS:**
```css
/* ---- Callout Subcomponents (optional structure) ---- */
.callout-title {
  font-weight: 700;
  margin-bottom: 8px;
  color: inherit;
}

.callout-body {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.6;
}

.callout-body p {
  margin-bottom: 6px;
}

.callout-body p:last-child {
  margin-bottom: 0;
}
```

**테스트:**
- [ ] CSS 문법 오류 없음 (DevTools 확인)
- [ ] 라이트 모드: 텍스트 가독성
- [ ] 다크 모드: 대비도 확인

---

#### Task 1.1.2: 미정의 클래스 정의 확인

**확인 사항:**
- [ ] `.diagram-content` — 사용 여부 확인 (현재 미정의, seed.py에서 사용 없음)
  - **결정:** CSS 추가 불필요 (기능적 영향 없음)
- [ ] 기타 불명확한 클래스 grep 검색
  ```bash
  grep -r "class=\"[a-z-]*\"" apps/api/seed.py | sort | uniq
  ```

---

### 1.2 seed.py 수정

#### Task 1.2.1: `.browser-header` → `.browser-bar` 교체

**위치:** `/apps/api/seed.py` (grep으로 찾기)
```bash
grep -n "browser-header" apps/api/seed.py
```

**예상 위치:** 라인 약 530, 852, 865 (3곳)

**수정 패턴:**
```python
# Before
'<div class="browser-mockup">\n'
'<div class="browser-header">\n'

# After
'<div class="browser-mockup">\n'
'<div class="browser-bar">\n'
```

**테스트:**
- [ ] grep으로 재검색 (결과 0)
- [ ] 브라우저 렌더링 확인

---

#### Task 1.2.2: `.code-title` → `.code-label` 교체

**위치:** `/apps/api/seed.py` (grep으로 찾기)
```bash
grep -n "code-title" apps/api/seed.py
```

**예상 위치:** 2곳 (라인 약 947, 1377)

**수정 패턴:**
```python
# Before
'<div class="code-example">\n'
'<div class="code-title">JSON</div>\n'

# After
'<div class="code-example">\n'
'<div class="code-label">JSON</div>\n'
```

**테스트:**
- [ ] grep으로 재검색 (결과 0)
- [ ] 코드 레이블 렌더링 확인

---

### 1.3 통합 테스트

#### Task 1.3.1: 페이지 전체 렌더링 확인

**테스트 절차:**
1. 개발 서버 시작: `python -m uvicorn apps.api.main:app --reload`
2. 브라우저: `http://localhost:8000`
3. 각 Stage/Module 탐색
   - [ ] S1 M1-2: browser-mockup 정상
   - [ ] S3 M3-1: code-example 정상
   - [ ] 다른 callout 항목들도 확인

**체크 포인트:**
- [ ] 콘솔 에러 없음
- [ ] 레이아웃 깨짐 없음
- [ ] 색상 조화 확인

---

#### Task 1.3.2: 다크모드 확인

**테스트:**
- [ ] 헤더 theme toggle 버튼 클릭
- [ ] 각 컴포넌트 다크 모드 색상 확인
- [ ] 텍스트 대비도 가독성 (최소 4.5:1)

---

## Phase 2: 신규 CSS 컴포넌트 작성 (2시간)

### 2.1 기본 구조 작성

#### Task 2.1.1: CSS 블록 구성

**위치:** `/apps/web/css/style.css` 라인 1950 이후

**구성:**
```css
/* ==============================================================
   NEW: Visual Components (6 components) — Phase 2
   ============================================================== */

/* ---- Component A: Comparison Table ---- */
/* [CSS here] */

/* ---- Component B: Flow Chart ---- */
/* [CSS here] */

/* ---- Component C: Pyramid Chart ---- */
/* [CSS here] */

/* ---- Component D: Tree Diagram ---- */
/* [CSS here] */

/* ---- Component E: Layer Box ---- */
/* [CSS here] */

/* ---- Component F: Network Diagram ---- */
/* [CSS here] */

/* ---- Dark Mode: New Components ---- */
/* [all dark mode rules] */
```

---

#### Task 2.1.2: 각 컴포넌트 CSS 작성

| 컴포넌트 | 라이트 라인 | 다크 라인 | 파일 참고 |
|---------|-----------|---------|---------|
| .comparison-table | 50 | 30 | docs/31 섹션 4.1 |
| .flow-chart | 70 | 40 | docs/31 섹션 4.2 |
| .pyramid-chart | 60 | 35 | docs/31 섹션 4.3 |
| .tree-diagram | 55 | 30 | docs/31 섹션 4.4 |
| .layer-box | 50 | 25 | docs/31 섹션 4.5 |
| .network-diagram | 45 | 25 | docs/31 섹션 4.6 |

**작성 순서:**
1. `.comparison-table` 완성 + 테스트
2. `.flow-chart` 완성 + 테스트
3. 나머지 진행

---

### 2.2 각 컴포넌트 CSS 작성 상세

#### Task 2.2.1: .comparison-table (50+30줄)

**파일:** `/apps/web/css/style.css` 끝에 추가

**라이트 모드 (50줄):**
```css
.comparison-table {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  margin: 16px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.comparison-table .comp-header {
  background: #f8f9ff;
  border-bottom: 1px solid #d0d8f0;
  padding: 12px 16px;
  font-weight: 700;
  font-size: 0.95rem;
  color: #333;
  text-align: center;
}

.comparison-table table {
  width: 100%;
  border-collapse: collapse;
}

.comparison-table thead {
  background: #1a73e8;
}

.comparison-table th {
  color: #fff;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  border-bottom: 2px solid #1a73e8;
}

.comparison-table tbody tr {
  border-bottom: 1px solid #e0e0e0;
  transition: background 0.15s;
}

.comparison-table tbody tr:hover {
  background: #f8f9fa;
}

.comparison-table td {
  padding: 12px 16px;
  color: #333;
  font-size: 0.9rem;
  line-height: 1.5;
}

.comparison-table td.label {
  font-weight: 600;
  background: #f5f5f5;
  min-width: 100px;
}

.comparison-table tr.highlight td {
  background: #f0fdf4;
}

.comparison-table tbody tr:last-child {
  border-bottom: none;
}

/* Responsive */
@media (max-width: 600px) {
  .comparison-table table {
    font-size: 0.85rem;
  }

  .comparison-table th,
  .comparison-table td {
    padding: 10px 12px;
  }
}
```

**다크 모드 (30줄):**
```css
[data-theme="dark"] .comparison-table {
  background: #0f3460;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

[data-theme="dark"] .comparison-table .comp-header {
  background: #16213e;
  border-bottom-color: #2a3a5c;
  color: #f0f0f0;
}

[data-theme="dark"] .comparison-table thead {
  background: #2563eb;
}

[data-theme="dark"] .comparison-table th {
  border-bottom-color: #2563eb;
}

[data-theme="dark"] .comparison-table tbody tr {
  border-bottom-color: #1a4a7a;
}

[data-theme="dark"] .comparison-table tbody tr:hover {
  background: #16213e;
}

[data-theme="dark"] .comparison-table td {
  color: #d0d0d0;
}

[data-theme="dark"] .comparison-table td.label {
  background: #16213e;
  color: #f0f0f0;
}

[data-theme="dark"] .comparison-table tr.highlight td {
  background: #0a3d1a;
}
```

**테스트 체크리스트:**
- [ ] HTML 이미지 없이 CSS만으로 표 렌더링
- [ ] 헤더 배경색 명확함
- [ ] 호버 효과 동작
- [ ] 다크모드 색상 대비도 4.5:1 이상

---

#### Task 2.2.2: .flow-chart (70+40줄)

**파일:** `/apps/web/css/style.css` 끝에 추가

**기본 구조:**
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
  margin-bottom: 12px;
  text-align: center;
  min-height: 80px;
  justify-content: center;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #1a73e8;
  color: #fff;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.step-title {
  font-weight: 600;
  color: #222;
  margin-bottom: 4px;
  font-size: 0.95rem;
}

.step-desc {
  font-size: 0.85rem;
  color: #666;
  margin: 0;
}

.arrow {
  color: #1a73e8;
  font-size: 1.2rem;
  margin-top: 12px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flow-step.last .arrow {
  display: none;
}

/* Responsive */
@media (max-width: 600px) {
  .flow-step {
    padding: 12px 16px;
    min-height: 70px;
  }

  .step-title {
    font-size: 0.9rem;
  }

  .step-desc {
    font-size: 0.8rem;
  }
}
```

**다크 모드:**
```css
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

---

#### Task 2.2.3~2.2.6: 나머지 컴포넌트

반복적으로 진행:
1. docs/31 섹션 참조하여 CSS 작성
2. 각 컴포넌트별 라이트 + 다크 모드 포함
3. 반응형 미디어쿼리 추가
4. 개발 서버에서 렌더링 테스트

**작업 순서:** pyramid-chart → tree-diagram → layer-box → network-diagram

---

### 2.3 통합 테스트

#### Task 2.3.1: 각 컴포넌트 시각 테스트

**테스트 파일:** 임시 HTML 작성
```html
<!-- /apps/web/component-test.html (임시) -->
<html>
<head>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <!-- 각 컴포넌트 예시 HTML -->
</body>
</html>
```

**체크리스트:**
- [ ] .comparison-table: 테이블 레이아웃, 호버 효과
- [ ] .flow-chart: 번호 원형, 화살표 정렬
- [ ] .pyramid-chart: 삼각형 모양, 색상 그라데이션
- [ ] .tree-diagram: 들여쓰기, 트리선 (::before)
- [ ] .layer-box: 레이어 스택, 화살표
- [ ] .network-diagram: 그리드 배치, 범례

---

#### Task 2.3.2: 다크모드 통합 테스트

**테스트 절차:**
1. DevTools 열기
2. HTML > `<body>` 요소에 `data-theme="dark"` 수동 추가
3. 각 컴포넌트 색상 확인
   - 배경: 충분히 어두운가?
   - 텍스트: 충분히 밝은가?
   - 대비도: WCAG AA (4.5:1)?

**색상 도구:**
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/

---

## Phase 3: seed.py 마이그레이션 (6시간)

### 3.1 마이그레이션 전 준비

#### Task 3.1.1: 기존 항목 목록 작성

**grep으로 마크다운 테이블 위치 찾기:**
```bash
grep -n "^| " apps/api/seed.py | head -20
```

**grep으로 ASCII 흐름도 위치 찾기:**
```bash
grep -n "↓\|→\|←" apps/api/seed.py | head -20
```

**grep으로 ASCII 피라미드 위치 찾기:**
```bash
grep -n "┌\|├\|└" apps/api/seed.py | head -20
```

**결과를 CSV로 정리:**
```csv
위치(라인),모듈,현재형식,변환타겟,카테고리
165-171,S1M1-2,markdown table,.comparison-table,A
243-252,S1M1-3,ASCII flow,.flow-chart,B
317-327,S1M1-4,ASCII pyramid,.pyramid-chart,C
391-400,S1M1-5,ASCII box,.layer-box,D
...
```

---

#### Task 3.1.2: seed.py 백업

```bash
git checkout -b feature/visual-components-phase3
cp apps/api/seed.py apps/api/seed.py.bak
```

---

### 3.2 P2 우선순위 마이그레이션 (4시간)

#### Task 3.2.1: .comparison-table (9개 항목)

**대상 항목:**
1. S1 M1-2: SEO vs GEO 비교 (라인 165-171)
2. S2 M2-3: 전통 vs Answer-first (라인 1212-1218)
3. S2 M2-7: 우선순위 매트릭스 (라인 1212-1218)
4. S3 M3-1: JSON-LD vs Microdata (라인 1371-1375)
5. S3 M3-1 ext: Schema.org 타입 (라인 1417-1422)
6. S3 M3-3: Article 속성 (TBD)
7. S3 M3-4: Event 속성 (TBD)
8. S5 M5-3 ext: AI 리퍼러 패턴 (TBD)
9. S5 M5-4: 인용 점수 계산 (TBD)

**변환 패턴:**

```python
# Before (마크다운 테이블)
"| 구분 | SEO | GEO |\n"
"|------|-----|-----|\n"
"| 목표 | 검색 결과 상위 노출 | AI 답변의 인용 출처 |\n"
...

# After (.comparison-table)
'<div class="comparison-table">\n'
'<div class="comp-header">SEO vs GEO 비교</div>\n'
'<table>\n'
'<thead>\n'
'<tr><th>구분</th><th>SEO</th><th>GEO</th></tr>\n'
'</thead>\n'
'<tbody>\n'
'<tr class="highlight">\n'
'<td class="label">목표</td>\n'
'<td>검색 결과 상위 노출</td>\n'
'<td>AI 답변의 인용 출처</td>\n'
'</tr>\n'
...
'</tbody>\n'
'</table>\n'
'</div>\n'
```

**작업 세부 사항:**

각 항목마다:
1. 라인 번호 찾기 (grep)
2. 마크다운 테이블 추출
3. HTML table로 변환
4. .comparison-table 래퍼 추가
5. seed.py에서 기존 마크다운 제거
6. 새 HTML 삽입
7. 페이지 렌더링 확인

**예시 (S1 M1-2):**

```python
add_step(m, "reading", "GEO와 SEO의 차이", (
    "## SEO와 GEO의 차이\n\n"
    '<div class="comparison-table">\n'
    '<div class="comp-header">SEO vs GEO 비교</div>\n'
    '<table>\n'
    '<thead>\n'
    '<tr><th>구분</th><th>SEO</th><th>GEO</th></tr>\n'
    '</thead>\n'
    '<tbody>\n'
    '<tr class="highlight">\n'
    '<td class="label">목표</td>\n'
    '<td>검색 결과 상위 노출</td>\n'
    '<td>AI 답변의 인용 출처 채택</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td class="label">대상 엔진</td>\n'
    '<td>구글, 네이버 등 검색엔진</td>\n'
    '<td>ChatGPT, Claude, Perplexity 등</td>\n'
    '</tr>\n'
    # ... 더 많은 행
    '</tbody>\n'
    '</table>\n'
    '</div>\n'
))
```

**테스트:** 각 항목 완료 후
- [ ] 페이지 로드: 에러 없음
- [ ] 테이블 렌더링: 올바른 행/열
- [ ] 스타일: 색상, 폰트 적절함
- [ ] 다크모드: 가독성 확인

---

#### Task 3.2.2: .flow-chart (5개 항목)

**대상 항목:**
1. S1 M1-3: RAG 5단계 파이프라인 (라인 243-252)
2. S5 M5-4 ext: 자동화 플로우 (TBD)
3. S5 M5-5: 실험 플로우 (TBD)
4. S5 M5-6: 90일 로드맵 (TBD, timeline으로 변경 가능)
5. S5 M5-6 ext: 지속 운영 (TBD, cycle로 변경 가능)

**변환 패턴:**

```python
# Before (ASCII 플로우)
'① 쿼리 이해  →  의도 파악\n'
'    ↓\n'
'② 검색       →  관련 문서 탐색\n'
...

# After (.flow-chart)
'<div class="flow-chart">\n'
'<div class="flow-title">RAG 5단계 파이프라인</div>\n'
'<div class="flow-steps">\n'
'<div class="flow-step">\n'
'<div class="step-number">1</div>\n'
'<div class="step-title">쿼리 이해</div>\n'
'<div class="step-desc">사용자 질문 의도 파악</div>\n'
'<div class="arrow">↓</div>\n'
'</div>\n'
'<div class="flow-step">\n'
'<div class="step-number">2</div>\n'
'<div class="step-title">검색</div>\n'
'<div class="step-desc">관련 문서 탐색</div>\n'
'<div class="arrow">↓</div>\n'
'</div>\n'
# ... 3-5단계
'<div class="flow-step last">\n'
'<div class="step-number">5</div>\n'
'<div class="step-title">답변 생성</div>\n'
'<div class="step-desc">출처 인용 포함</div>\n'
'</div>\n'
'</div>\n'
'</div>\n'
```

**예시 (S1 M1-3):**

```python
add_step(m, "reading", "RAG 파이프라인", (
    "## RAG(Retrieval-Augmented Generation) 프로세스\n\n"
    '<div class="flow-chart">\n'
    '<div class="flow-title">RAG 5단계 파이프라인</div>\n'
    '<div class="flow-steps">\n'
    '<div class="flow-step">\n'
    '<div class="step-number">1</div>\n'
    '<div class="step-title">쿼리 이해</div>\n'
    '<div class="step-desc">사용자 질문의 의도를 파악합니다</div>\n'
    '<div class="arrow">↓</div>\n'
    '</div>\n'
    '<div class="flow-step">\n'
    '<div class="step-number">2</div>\n'
    '<div class="step-title">검색</div>\n'
    '<div class="step-desc">관련된 문서를 데이터베이스에서 탐색합니다</div>\n'
    '<div class="arrow">↓</div>\n'
    '</div>\n'
    '<div class="flow-step">\n'
    '<div class="step-number">3</div>\n'
    '<div class="step-title">랭킹</div>\n'
    '<div class="step-desc">관련성에 따라 문서 순위를 결정합니다</div>\n'
    '<div class="arrow">↓</div>\n'
    '</div>\n'
    '<div class="flow-step">\n'
    '<div class="step-number">4</div>\n'
    '<div class="step-title">컨텍스트 주입</div>\n'
    '<div class="step-desc">상위 문서들의 콘텐츠를 프롬프트에 삽입합니다</div>\n'
    '<div class="arrow">↓</div>\n'
    '</div>\n'
    '<div class="flow-step last">\n'
    '<div class="step-number">5</div>\n'
    '<div class="step-title">답변 생성</div>\n'
    '<div class="step-desc">LLM이 인용 출처를 포함하여 답변을 생성합니다</div>\n'
    '</div>\n'
    '</div>\n'
    '</div>\n'
))
```

---

#### Task 3.2.3: .layer-box (3개 항목)

**대상 항목:**
1. S1 M1-5: KPI 3층 (라인 391-400)
2. S2 M2-1: 사이트 링크 구조 (TBD, tree-diagram으로 변경)
3. S2 M2-6: 내부링크 맵 (TBD, network-diagram으로 변경)

**예시 (S1 M1-5):**

```python
'<div class="layer-box">\n'
'<div class="layer-title">GEO 성공 지표 (3층 KPI)</div>\n'
'<div class="layer">\n'
'<div class="layer-label">고객 행동 신호</div>\n'
'<div class="layer-content">\n'
'<ul>\n'
'<li>클릭율 (CTR): AI 결과에서의 클릭</li>\n'
'<li>체류시간: 페이지 방문 후 머물러있는 시간</li>\n'
'<li>재방문율: 특정 기간 내 재방문 빈도</li>\n'
'</ul>\n'
'</div>\n'
'</div>\n'
'<div class="layer-arrow">↕</div>\n'
'<div class="layer">\n'
'<div class="layer-label">콘텐츠 최적화</div>\n'
'<div class="layer-content">\n'
'<ul>\n'
'<li>구조화된 마크업: Schema.org 적용</li>\n'
'<li>명확한 헤딩: H1→H2→H3 계층</li>\n'
'<li>인용 가능한 형태: 핵심 답변 선행 배치</li>\n'
'</ul>\n'
'</div>\n'
'</div>\n'
'</div>\n'
```

---

### 3.3 P3 우선순위 마이그레이션 (2시간)

#### Task 3.3.1: .pyramid-chart (5개 항목)

**대상 항목:**
1. S1 M1-4: GEO 5대 신호 (라인 317-327)
2. S3 M3-5: FAQPage 스키마 (TBD, tree-diagram으로)
3. S4 M4-1: MECE 오프사이트 (TBD, tree-diagram으로)
4. S4 M4-2: 백링크 품질 (TBD)
5. S4 M4-4: 엔터티 그래프 (TBD, tree-diagram으로)

**예시 (S1 M1-4):**

```python
'<div class="pyramid-chart">\n'
'<div class="pyramid-title">GEO 5대 신호</div>\n'
'<div class="pyramid-container">\n'
'<div class="pyramid-level" style="--level: 1; --total: 5;">\n'
'<div class="level-content">콘텐츠 구조</div>\n'
'</div>\n'
'<div class="pyramid-level" style="--level: 2; --total: 5;">\n'
'<div class="level-content">신뢰성 신호</div>\n'
'</div>\n'
'<div class="pyramid-level" style="--level: 3; --total: 5;">\n'
'<div class="level-content">인용 빈도</div>\n'
'</div>\n'
'<div class="pyramid-level" style="--level: 4; --total: 5;">\n'
'<div class="level-content">사이트 신호</div>\n'
'</div>\n'
'<div class="pyramid-level" style="--level: 5; --total: 5;">\n'
'<div class="level-content">AI 선호도</div>\n'
'</div>\n'
'</div>\n'
'</div>\n'
```

---

#### Task 3.3.2: .tree-diagram (8개 항목)

**대상 항목:**
1. S2 M2-2: 허브-클러스터
2. S2 M2-5: H1>H2>H3 (이미 hierarchy-box지만 확인)
3. S2 M2-1: 사이트 링크 구조
4. S3 M3-5: FAQPage 스키마
5. S4 M4-1: MECE 오프사이트
6. S4 M4-4: 엔터티 그래프
7. 그 외 계층 구조

**예시:**

```python
'<div class="tree-diagram">\n'
'<div class="tree-title">FAQPage 스키마 계층 구조</div>\n'
'<ul class="tree">\n'
'<li class="tree-item">\n'
'<span class="tree-node">FAQPage</span>\n'
'<ul class="tree">\n'
'<li class="tree-item">\n'
'<span class="tree-node">mainEntity (배열)</span>\n'
'<ul class="tree">\n'
'<li class="tree-item">\n'
'<span class="tree-node">Question</span>\n'
'<ul class="tree">\n'
'<li class="tree-item"><span class="tree-node">name</span></li>\n'
'<li class="tree-item">\n'
'<span class="tree-node">acceptedAnswer</span>\n'
'<ul class="tree">\n'
'<li class="tree-item"><span class="tree-node">text</span></li>\n'
'</ul>\n'
'</li>\n'
'</ul>\n'
'</li>\n'
'</ul>\n'
'</li>\n'
'</ul>\n'
'</li>\n'
'</ul>\n'
'</div>\n'
```

---

#### Task 3.3.3: .network-diagram (1개 항목)

**대상 항목:**
1. S2 M2-6: 내부링크 맵

**예시:**

```python
'<div class="network-diagram">\n'
'<div class="network-title">사이트 내부링크 맵</div>\n'
'<div class="network-canvas">\n'
'<div class="network-node hub">\n'
'<div class="node-label">홈</div>\n'
'</div>\n'
'<div class="network-node">\n'
'<div class="node-label">서비스</div>\n'
'</div>\n'
'<div class="network-node">\n'
'<div class="node-label">문의</div>\n'
'</div>\n'
'<div class="network-node">\n'
'<div class="node-label">개인정보</div>\n'
'</div>\n'
'</div>\n'
'<div class="network-legend">\n'
'<div class="legend-item"><span class="link solid"></span>양방향 연결</div>\n'
'<div class="legend-item"><span class="link broken"></span>누락된 연결</div>\n'
'</div>\n'
'</div>\n'
```

---

## Phase 4: 통합 테스트 및 배포 (1시간)

### 4.1 렌더링 테스트

#### Task 4.1.1: 전체 Stage 순회

**테스트 절차:**
1. 개발 서버 시작
2. 대시보드: 모든 모듈 접근 가능 확인
3. Stage 1:
   - [ ] M1-1: 기본 콘텐츠
   - [ ] M1-2: .comparison-table (SEO vs GEO)
   - [ ] M1-3: .flow-chart (RAG)
   - [ ] M1-4: .pyramid-chart (5대 신호)
   - [ ] M1-5: .layer-box (KPI)
4. Stage 2, 3, 4, 5: 마찬가지로 각 모듈 확인

**체크 포인트:**
- [ ] 콘솔 에러 없음
- [ ] 레이아웃 깨짐 없음
- [ ] 이미지/아이콘 로드 됨
- [ ] 스크롤 성능 (버벅거림 없음)

---

#### Task 4.1.2: 다크모드 검증

**테스트:**
- [ ] 헤더 theme toggle 버튼 클릭
- [ ] 모든 컴포넌트 다크 모드로 전환 확인
- [ ] 텍스트 대비도 검증 (https://webaim.org/resources/contrastchecker/)
  - 최소: 4.5:1 (WCAG AA)
  - 권장: 7:1 (WCAG AAA)

**색상 검증 항목:**
- [ ] 배경: 충분히 어두운가? (충분히 검정색)
- [ ] 텍스트: 충분히 밝은가? (밝은 회색 이상)
- [ ] 구분선: 보이는가? (대비 충분)
- [ ] 강조색: 시각적으로 구분되는가?

---

#### Task 4.1.3: 반응형 테스트 (모바일 미포함, 태블릿 만)

**테스트 환경:**
- DevTools Responsive Design Mode
- 너비: 600px, 768px, 1024px

**체크 포인트:**
- [ ] 600px: 텍스트 읽기 가능? (줄 길이 합리적)
- [ ] 768px: 테이블 스크롤 가능? (overflow-x)
- [ ] 1024px: 원래대로 표시?

---

### 4.2 성능 테스트

#### Task 4.2.1: 페이지 로드 시간

**도구:** DevTools Performance 탭

**테스트:**
```
1. 새로고침 (Ctrl+Shift+Del 후 캐시 비우기)
2. Network 탭에서:
   - Document: < 1초
   - style.css: < 500ms (전체 크기 확인)
   - 총 로드 시간: < 3초
```

**CSS 파일 크기 확인:**
```bash
wc -l apps/web/css/style.css  # 라인 수
du -h apps/web/css/style.css  # 파일 크기
```

**예상:**
- Phase 1 전: ~1950줄
- Phase 2 후: ~2500줄 (+550줄)
- Phase 3 후: 변화 없음 (CSS 추가 안 함)

---

#### Task 4.2.2: 렌더링 성능

**도구:** DevTools Performance 탭 > Recording

**테스트:**
1. M1-2 페이지 로드
2. Recording 시작
3. 다크모드 toggle 클릭
4. Recording 중지
5. 분석:
   - [ ] 레이아웃 쓰레시 없음 (paint 시간 < 100ms)
   - [ ] 장기 작업 없음 (scripting < 100ms)

---

### 4.3 QA 체크리스트

#### Task 4.3.1: 기능 검증

| 기능 | S1 | S2 | S3 | S4 | S5 | 상태 |
|------|----|----|----|----|----|----|
| 비교표 (comparison-table) | ✓ | — | — | — | — | |
| 흐름도 (flow-chart) | ✓ | — | — | — | ✓ | |
| 피라미드 (pyramid-chart) | ✓ | — | — | ✓ | — | |
| 레이어 (layer-box) | ✓ | ✓ | — | — | — | |
| 트리 (tree-diagram) | — | ✓ | ✓ | ✓ | — | |
| 네트워크 (network-diagram) | — | ✓ | — | — | — | |

**체크:**
- [ ] 각 셀에 ✓ 표시 (페이지 로드 + 렌더링 확인)

---

#### Task 4.3.2: 접근성 검증

**도구:** axe DevTools (Chrome 확장)

**테스트:**
1. M1-2 페이지 열기
2. axe DevTools 실행
3. 결과 확인:
   - [ ] 에러 0개
   - [ ] 경고 < 10개

**주요 확인 항목:**
- [ ] 색상 대비도 (WCAG AA)
- [ ] 텍스트 크기 (16px 이상 권장)
- [ ] 스킵 링크 있는가?
- [ ] 키보드 네비게이션 가능?

---

### 4.4 배포 준비

#### Task 4.4.1: Git commit 및 PR

```bash
# 현재 브랜치 확인
git branch

# 변경사항 확인
git status

# 모든 변경 커밋
git add -A
git commit -m "feat: visual components (Phase 1-4 complete)

- Phase 1: Fix CSS class name mismatches
  - .browser-header → .browser-bar
  - .code-title → .code-label
  - Add .callout-title, .callout-body definitions

- Phase 2: Add 6 new CSS components
  - .comparison-table (80줄)
  - .flow-chart (110줄)
  - .pyramid-chart (95줄)
  - .tree-diagram (85줄)
  - .layer-box (75줄)
  - .network-diagram (70줄)
  - Total: 515줄 (라이트 + 다크)

- Phase 3: Migrate 34 visualization items in seed.py
  - 9 markdown tables → .comparison-table
  - 5 ASCII flowcharts → .flow-chart
  - 5 pyramids → .pyramid-chart
  - 3 KPI layers → .layer-box
  - 8 tree structures → .tree-diagram
  - 1 network map → .network-diagram
  - 3 quick fixes

- Phase 4: Full integration testing
  - All stages/modules render correctly
  - Dark mode contrast validated
  - Responsive design checked
  - Performance baseline: <3s page load

Closes #31-visual-components
"

git push origin feature/visual-components-phase3
```

#### Task 4.4.2: PR 생성

**GitHub PR:**
- Title: `[Visual Components] CSS redesign + seed.py migration (Phase 1-4)`
- Description:
  ```markdown
  ## Overview
  Upgrade 21 visualization items in GEO content from text-based to interactive HTML/CSS components.

  ## Changes
  - Phase 1: CSS class fixes (3 changes)
  - Phase 2: 6 new CSS components (515 lines)
  - Phase 3: seed.py migration (34 items)
  - Phase 4: Integration testing (all stages)

  ## Testing
  - [x] All pages render without errors
  - [x] Dark mode validated
  - [x] Responsive design (tablet)
  - [x] Performance baseline met
  - [x] Accessibility checks passed

  ## Checklist
  - [x] CSS follows existing patterns
  - [x] HTML is semantic
  - [x] No breaking changes
  - [x] No new dependencies
  ```

---

### 4.5 배포 후 모니터링

#### Task 4.5.1: 라이브 환경 확인

```bash
# 프로덕션 배포 (CI/CD 또는 수동)
git merge feature/visual-components-phase3

# 라이브 사이트에서:
curl https://geo-mentor.fastcampus.co.kr/api/stages
# → 200 OK
```

**확인 체크리스트:**
- [ ] 페이지 로드: 에러 없음
- [ ] 모든 도식 렌더링: 정상
- [ ] 다크모드: 작동
- [ ] 성능: 지연 없음

---

#### Task 4.5.2: 사용자 피드백 수집

**기간:** 1주일

**모니터링:**
- [ ] 콘솔 에러 로그 확인
- [ ] 페이지 성능 메트릭 (Analytics)
- [ ] 사용자 이탈률 변화 없음

---

## 다음 단계

1. **문서화:** docs/31, 32 검토 및 최종 확인
2. **구현:** Phase 1부터 순차 진행
3. **테스트:** 각 Phase 완료 후 통합 테스트
4. **배포:** main 브랜치 merge 및 라이브 배포

---

**문서 버전:** v1.0
**작성 일자:** 2026-02-22
**담당:** frontend-dev
**상태:** 구현 준비 완료

