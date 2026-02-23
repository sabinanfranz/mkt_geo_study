# 21 — Glossary UX Design (전문용어 설명 3가지 접근법)

## 배경

- **콘텐츠**: 80~100개 핵심 전문용어가 교육 콘텐츠(seed.py)에 산재
- **학습자**: B2B 마케터 (개발 비전문가)
- **문제**: "이 용어 뭐지?" 순간에 1~2초 내에 답을 찾을 수 있어야 함
- **제약**: 기존 CSS 패턴 최대 활용, app.js 최소 변경, 바닐라 HTML/CSS/JS

---

## 전문용어 분류 (참고)

| 카테고리 | 개수 | 예시 |
|---------|------|------|
| 기술/개발 | ~25개 | JSON-LD, Schema, SSR/CSR, HTML, API, Canonical |
| AI/LLM | ~15개 | RAG, LLM, GPT, Perplexity, Citation, Embedding |
| SEO/GEO | ~25개 | SERP, Backlink, E-E-A-T, Hub-Cluster, Rich Result |
| 마케팅/분석 | ~15개 | KPI, CTR, GA4, GSC, UTM, MECE, Conversion |
| Schema 타입 | ~15개 | FAQPage, BreadcrumbList, Article, Event |
| **총합** | **~95개** | — |

---

# 접근법 A: 인라인 용어 하이라이트 + 툴팁

## A-1. 개념

**핵심**: 콘텐츠 내 용어에 점선 밑줄을 긋고, 호버/클릭 시 팝오버 설명 표시

```
마크다운 원문:
"RAG(Retrieval-Augmented Generation)는..."

렌더링 후:
"<span class="glossary-term" data-term="RAG">RAG</span>
  (Retrieval-Augmented Generation)는..."

호버/클릭 시:
┌─────────────────────────┐
│ RAG                     │
├─────────────────────────┤
│ Retrieval-Augmented     │
│ Generation. LLM이 학습  │
│ 데이터에 없는 최신      │
│ 정보를 검색해서 답변    │
│ 생성 시 활용.           │
│ [더 알아보기 →]         │
└─────────────────────────┘
```

## A-2. 텍스트 와이어프레임

### 정상 상태 (용어 없음)

```
┌─────────────────────────────────────────┐
│ 📖 마크다운 읽기 카드                   │
├─────────────────────────────────────────┤
│                                         │
│ GEO 전략의 핵심은 생성 AI 기반          │
│ 검색 엔진 최적화입니다.                 │
│                                         │
│ SERP(검색 결과 페이지)에만 노출         │
│ 되는 것으로는 부족하고, ChatGPT나       │
│ Claude, Gemini 같은 생성 AI 챗봇        │
│ 답변에 나타나야 합니다.                 │
│                                         │
│ 이를 위해 E-E-A-T(경험, 전문성,        │
│ 권위성, 신뢰성) 신호를 강화해야        │
│ 합니다.                                 │
│                                         │
└─────────────────────────────────────────┘
```

### 호버 상태 (용어 하이라이트)

```
┌─────────────────────────────────────────┐
│ 📖 마크다운 읽기 카드                   │
├─────────────────────────────────────────┤
│                                         │
│ GEO 전략의 핵심은 생성 AI 기반          │
│ 검색 엔진 최적화입니다.                 │
│                                         │
│ SERP(검색 결과 페이지)에만 노출 [호버] │
│ ┌─────────────────────────────────────┐│
│ │ SERP                                ││
│ │ Search Engine Results Page          ││
│ │                                     ││
│ │ 사용자가 검색어를 입력할 때         ││
│ │ 나타나는 검색 결과 화면.            ││
│ │                                     ││
│ │ SEO는 여기 상위 노출을,             ││
│ │ GEO는 생성 AI 답변 최적화           ││
│ │ 를 목표로 함.                       ││
│ │                                     ││
│ │ [더 알아보기 →]  [닫기 ✕]           ││
│ └─────────────────────────────────────┘│
│ 되는 것으로는 부족하고, ChatGPT나       │
│ Claude, Gemini 같은 생성 AI 챗봇        │
│ 답변에 나타나야 합니다.                 │
│                                         │
│ ...                                     │
│                                         │
└─────────────────────────────────────────┘
```

### 클릭 후 "더 알아보기" 상태

```
┌─────────────────────────────────────────┐
│ 📖 마크다운 읽기 카드                   │
├─────────────────────────────────────────┤
│                                         │
│ ...                                     │
│                                         │
│ SERP에만 노출되는 것으로는 부족하고...  │
│                                         │
│ ▼ 더 알아보기: SERP                     │
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 📚 SERP의 역할 (검색 결과)          ││
│ │                                     ││
│ │ • 전통 SEO: SERP 상위 클릭유도     ││
│ │                                     ││
│ │ • GEO: 생성 AI 답변 최적화로       ││
│ │   검색자 의도 직접 충족             ││
│ │                                     ││
│ │ • 실제 예시:                        ││
│ │   - SERP: "GEO란" 검색 →            ││
│ │   "패스트캠퍼스는 GEO..." 결과     ││
│ │   - 생성 AI: 같은 쿼리에            ││
│ │   ChatGPT가 직접 정의 생성          ││
│ │                                     ││
│ └─────────────────────────────────────┘│
│                                         │
│ ...                                     │
│                                         │
└─────────────────────────────────────────┘
```

## A-3. 기술 명세

### HTML 구조

```html
<!-- seed.py의 content_md에 auto-link로 추가 -->
<span class="glossary-term" data-term-id="serp" data-term-name="SERP">SERP</span>

<!-- 또는 marked.js 후처리에서 자동 감지 -->
<p>SERP에만 노출되는 것으로는 부족하고...</p>
<!-- → 후처리 단계에서 regex 찾아서 span 래핑 -->
```

### CSS (기존 패턴 재활용)

```css
/* 기존 .callout 패턴 재사용 */
.glossary-term {
  border-bottom: 2px dotted #1a73e8;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
}

.glossary-term:hover {
  background: #e8f0fe;
  border-radius: 2px;
}

/* 팝오버 (기존 extension-card 참고) */
.glossary-popover {
  position: absolute;
  z-index: 1000;
  background: #fff;
  border: 1px solid #d0d8f0;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  min-width: 280px;
  max-width: 360px;
  top: 100%;
  left: -50px;
  margin-top: 8px;
  line-height: 1.6;
  font-size: 0.9rem;
  color: #333;
}

.glossary-popover::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50px;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid #d0d8f0;
}

.glossary-popover-title {
  font-weight: 700;
  margin-bottom: 8px;
  color: #222;
}

.glossary-popover-desc {
  font-size: 0.88rem;
  margin-bottom: 12px;
  color: #555;
}

.glossary-popover-action {
  text-align: right;
}

.glossary-popover-action a {
  color: #1a73e8;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.85rem;
}
```

### JS (app.js에 추가)

```javascript
// 1. 용어 감지 & 마킹 (marked.parse 후처리)
const glossaryTerms = {
  'SERP': 'Search Engine Results Page',
  'RAG': 'Retrieval-Augmented Generation',
  'E-E-A-T': 'Experience, Expertise, Authoritativeness, Trustworthiness',
  // ... 95개 용어
};

function markGlossaryTerms(html) {
  let result = html;
  Object.keys(glossaryTerms).forEach(term => {
    const regex = new RegExp(`\\b${term}\\b(?!.*</span>)`, 'g');
    result = result.replace(regex,
      `<span class="glossary-term" data-term="${term}">${term}</span>`
    );
  });
  return result;
}

// 2. 팝오버 토글
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('glossary-term')) {
    const term = e.target.dataset.term;
    toggleGlossaryPopover(e.target, term);
  }
});

function toggleGlossaryPopover(element, term) {
  const existing = document.querySelector('.glossary-popover');
  if (existing) existing.remove();

  const popover = document.createElement('div');
  popover.className = 'glossary-popover';
  popover.innerHTML = `
    <div class="glossary-popover-title">${term}</div>
    <div class="glossary-popover-desc">${glossaryTerms[term]}</div>
    <div class="glossary-popover-action">
      <a href="#" onclick="showGlossaryDetail('${term}'); return false;">더 알아보기 →</a>
    </div>
  `;
  element.appendChild(popover);
}

// 3. 확장 해설 (extension-card 패턴)
function showGlossaryDetail(term) {
  // 현재 reading-card 다음에 extension-card 추가
  const card = document.querySelector('.reading-card');
  const ext = document.createElement('div');
  ext.className = 'extension-card';
  ext.innerHTML = `
    <button class="extension-toggle">▼ 더 알아보기: ${term}</button>
    <div class="extension-content">
      <h4>📚 ${term}의 상세 설명</h4>
      <p>${getExtendedGlossary(term)}</p>
    </div>
  `;
  card.parentNode.insertBefore(ext, card.nextSibling);
}
```

## A-4. 장점

| 항목 | 설명 |
|------|------|
| **학습 흐름 방해 최소** | 용어를 만날 때 즉시 확인 가능, 읽기 멈출 필요 없음 |
| **발견성 높음** | 점선 밑줄로 용어를 시각적으로 강조 |
| **상황 맥락 유지** | 팝오버로 원문 주변 콘텍스트 유지 |
| **선택적 깊이** | "더 알아보기"로 선택적 심화 학습 |
| **CSS 최소** | 기존 callout/extension-card 패턴 재활용 |

## A-5. 단점

| 항목 | 설명 |
|------|------|
| **자동 감지 오류** | "API"처럼 짧은 용어는 오탐 가능 |
| **매뉴얼 마킹 비용** | seed.py 콘텐츠에 span 태그를 일일이 추가해야 함 |
| **포커스 분산** | 매 용어마다 팝오버 클릭 → 학습 흐름 중단 |
| **모바일 호버 어려움** | 하지만 MVP는 데스크톱만이므로 이슈 낮음 |
| **첫 등장만 강조** | 같은 용어 반복 시 계속 강조 (스타일링 피로) |

## A-6. 구현 복잡도

| 항목 | 비용 |
|------|------|
| **CSS 줄 수** | ~150줄 (기존 패턴 활용) |
| **JS 변경량** | marked.js 후처리 + 이벤트 리스너 ~100줄 |
| **seed.py 변경** | 각 콘텐츠에 수작업 span 추가 (1시간/모듈) |
| **총 추정** | **중간** (JS 간단, 데이터 작업 많음) |

---

# 접근법 B: "핵심 용어" 콜아웃 박스

## B-1. 개념

**핵심**: 각 reading/step 상단에 "이 챕터의 핵심 용어" 박스 삽입, 2~4개 용어 + 한 줄 설명

```
┌──────────────────────────────────┐
│ 🔑 핵심 용어 (이 섹션)            │
├──────────────────────────────────┤
│ • SERP: 검색 결과 페이지         │
│ • E-E-A-T: 신뢰성 신호            │
│ • Backlink: 외부 인입 링크        │
│ • Schema: 검색 엔진 이해용 마크업 │
└──────────────────────────────────┘

[이제 읽기 카드 시작]
"SERP에는 전통 SEO 최적화 결과가 나타나고,
E-E-A-T 신호는 Google의 핵심 순위 인자..."
```

## B-2. 텍스트 와이어프레임

### Step 시작 (콜아웃 박스)

```
┌─────────────────────────────────────────┐
│ 모듈 1-2: 검색 엔진 최적화의 기초       │
│ Step 1 / 5                             │
│ ███░░░░░░░░░░░░░░░░░░░░░░░░░░░ (20%)  │
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 🔑 이 스텝의 핵심 용어               ││
│ ├─────────────────────────────────────┤│
│ │ • SERP (Search Engine Results Page) ││
│ │   사용자가 검색할 때 보는 결과 페이지││
│ │                                     ││
│ │ • SEO (Search Engine Optimization)  ││
│ │   검색 엔진 최적화 전통 기법         ││
│ │                                     ││
│ │ • Ranking Factors (순위 인자)       ││
│ │   Google이 검색 순서를 결정하는     ││
│ │   200+개 신호                       ││
│ └─────────────────────────────────────┘│
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 📖 SEO 기초 원리                     ││
│ │                                     ││
│ │ SEO(검색 엔진 최적화)는 웹사이트가  ││
│ │ Google, Bing 등 검색 엔진에서       ││
│ │ 자연 검색(organic search) 결과로    ││
│ │ 노출되도록 하는 일련의 기법입니다.  ││
│ │                                     ││
│ │ SERP에서 상위 순위를 차지하기       ││
│ │ 위해, 검색 엔진은 Ranking Factors   ││
│ │ 라는 200개 이상의 신호를 분석합니다.││
│ │                                     ││
│ └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│          [ ← 이전 ]      [ 다음 → ]    │
└─────────────────────────────────────────┘
```

### 중간 Step (용어 맥락)

```
┌─────────────────────────────────────────┐
│ 모듈 1-2: 검색 엔진 최적화의 기초       │
│ Step 2 / 5                             │
│ ██████░░░░░░░░░░░░░░░░░░░░░░░░░░ (40%)│
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 🔑 이 스텝의 핵심 용어               ││
│ ├─────────────────────────────────────┤│
│ │ • E-E-A-T: 경험, 전문성, 권위성,   ││
│ │   신뢰성 (Google의 핵심 순위 신호)  ││
│ │                                     ││
│ │ • Backlink: 외부 사이트에서        ││
│ │   우리 사이트로 가는 링크            ││
│ │   (신뢰성 신호로 활용)              ││
│ └─────────────────────────────────────┘│
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 📖 E-E-A-T와 Backlink의 역할        ││
│ │                                     ││
│ │ Google은 2023년 이후 "신뢰성"을     ││
│ │ 검색 순위의 가장 중요한 신호로      ││
│ │ 지정했습니다.                       ││
│ │                                     ││
│ │ 이를 측정하는 두 가지 지표:         ││
│ │                                     ││
│ │ 1) E-E-A-T: 콘텐츠 자체의 신뢰성   ││
│ │    - 저자 프로필 명확                ││
│ │    - 원본 출처 표시                  ││
│ │    - 최신 정보 유지                  ││
│ │                                     ││
│ │ 2) Backlink: 외부 검증              ││
│ │    - 권위 있는 사이트가 인용        ││
│ │    - 신뢰성 간접 확인                ││
│ │                                     ││
│ └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│          [ ← 이전 ]      [ 다음 → ]    │
└─────────────────────────────────────────┘
```

## B-3. 기술 명세

### 데이터 구조 (seed.py)

```python
# 각 step에 "핵심 용어" 메타데이터 추가
{
  "id": "m1-2-s1",
  "module_id": "1-2",
  "type": "card",
  "title": "SEO 기초 원리",
  "content_md": "## SEO란...",
  "key_terms": [
    {
      "term": "SERP",
      "full_name": "Search Engine Results Page",
      "definition": "사용자가 검색할 때 보는 결과 페이지"
    },
    {
      "term": "SEO",
      "full_name": "Search Engine Optimization",
      "definition": "검색 엔진 최적화 전통 기법"
    },
    # ... 2~4개 용어
  ]
}
```

### HTML 구조

```html
<div class="learning-header">
  <h2 class="module-title">모듈 1-2: 검색 엔진 최적화의 기초</h2>
  <div class="step-counter">Step 1 / 5</div>
  <div class="progress-bar">...</div>
</div>

<!-- 핵심 용어 박스 (콜아웃 패턴 재사용) -->
<div class="key-terms-box callout key-point">
  <div class="callout-title">🔑 이 스텝의 핵심 용어</div>
  <div class="callout-body">
    <ul class="key-terms-list">
      <li>
        <strong>SERP</strong> (Search Engine Results Page)
        <span class="term-definition">사용자가 검색할 때 보는 결과 페이지</span>
      </li>
      <li>
        <strong>SEO</strong> (Search Engine Optimization)
        <span class="term-definition">검색 엔진 최적화 전통 기법</span>
      </li>
      <!-- ... -->
    </ul>
  </div>
</div>

<!-- 읽기 카드 -->
<div class="reading-card">
  <!-- marked.parse 결과 -->
</div>
```

### CSS (기존 .callout 확장)

```css
.key-terms-box {
  margin-bottom: 20px;
  background: #e6f4ea;
  border-left: 4px solid #34a853;
}

.key-terms-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.key-terms-list li {
  padding: 8px 0;
  border-bottom: 1px solid rgba(26, 115, 232, 0.1);
  color: #333;
}

.key-terms-list li:last-child {
  border-bottom: none;
}

.key-terms-list strong {
  color: #1a4a8a;
  font-weight: 700;
}

.term-definition {
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-top: 2px;
  margin-left: 16px;
  font-weight: 400;
}

/* Dark Mode */
[data-theme="dark"] .key-terms-box {
  background: #0a2a1a;
  border-left-color: #34a853;
}

[data-theme="dark"] .key-terms-list li {
  border-bottom-color: rgba(52, 168, 83, 0.2);
  color: #c0d0c0;
}

[data-theme="dark"] .key-terms-list strong {
  color: #a0d8a0;
}

[data-theme="dark"] .term-definition {
  color: #888;
}
```

### JS (app.js 확장)

```javascript
// 1. Step 데이터 로드 시 key_terms 렌더링
async function renderStep(module, step) {
  // ... 기존 코드

  const keyTermsHtml = renderKeyTerms(step.key_terms);
  const stepContent = `
    ${keyTermsHtml}
    <div class="reading-card">
      ${marked.parse(step.content_md)}
    </div>
  `;

  return stepContent;
}

// 2. 용어 박스 렌더
function renderKeyTerms(terms) {
  if (!terms || terms.length === 0) return '';

  const termsList = terms.map(t => `
    <li>
      <strong>${t.term}</strong> (${t.full_name})
      <span class="term-definition">${t.definition}</span>
    </li>
  `).join('');

  return `
    <div class="key-terms-box callout key-point">
      <div class="callout-title">🔑 이 스텝의 핵심 용어</div>
      <div class="callout-body">
        <ul class="key-terms-list">
          ${termsList}
        </ul>
      </div>
    </div>
  `;
}
```

## B-4. 장점

| 항목 | 설명 |
|------|------|
| **사전 예고** | 읽기 전에 미리 용어 준비 → 학습 효율 증가 |
| **맥락 강화** | "이 섹션이 다룰 주제"를 선명하게 제시 |
| **군집화** | 산재된 용어를 한곳에 정리 → 시각적 정돈 |
| **seed.py 간단** | 기존 step 스키마에 key_terms 배열만 추가 |
| **무자동 오류** | 수작업이지만 정확한 용어만 노출 |
| **반복 학습** | 같은 용어 재등장 시 자동 강조됨 |

## B-5. 단점

| 항목 | 설명 |
|------|------|
| **학습 흐름 끊김** | "먼저 용어 읽고 → 다음에 콘텐츠"로 2단계 |
| **초기 인지 부담** | 4개 용어를 한꺼번에 제시 → 과부하 가능 |
| **유연성 부족** | 각 step마다 수동으로 2~4개 선정해야 함 |
| **모듈 개발 지연** | seed.py 구조 변경 필요 → 데이터 재작업 |
| **용어 중복** | 여러 step에서 같은 용어 반복 가능 |

## B-6. 구현 복잡도

| 항목 | 비용 |
|------|------|
| **CSS 줄 수** | ~80줄 (.callout 확장) |
| **JS 변경량** | renderKeyTerms 함수 ~40줄 |
| **seed.py 변경** | 각 step에 key_terms 배열 추가 (30분/모듈) |
| **총 추정** | **낮음~중간** (기술 간단, 콘텐츠 작업 중간) |

---

# 접근법 C: 하이브리드 (A + B + 용어집 페이지)

## C-1. 개념

**핵심**: B의 "핵심 용어" + A의 "인라인 하이라이트" + 전체 용어집 페이지 조합

```
1. 각 step 시작 시 "핵심 용어" 박스 (B)
   ↓
2. 콘텐츠 내 모든 용어에 점선 밑줄 + 팝오버 (A)
   ↓
3. 대시보드에 "용어집" 링크
   ↓
4. 독립된 용어집 페이지로 95개 용어 전체 검색/필터/정렬
```

## C-2. 텍스트 와이어프레임

### (1) Step 시작: 핵심 용어 박스 (B 패턴)

```
┌─────────────────────────────────────────┐
│ 모듈 1-3: 생성 AI와 마케팅              │
│ Step 1 / 5                             │
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 🔑 이 스텝의 핵심 용어               ││
│ ├─────────────────────────────────────┤│
│ │ • RAG: 검색 강화 생성 (LLM 성능 고도화) ││
│ │ • Embedding: 텍스트→숫자 변환       ││
│ │ • Vector DB: 임베딩 저장 검색 DB    ││
│ └─────────────────────────────────────┘│
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 📖 생성 AI의 마케팅 응용             ││
│ │                                     ││
│ │ 생성 AI는 RAG(검색 강화 생성)로    ││
│ │ 더욱 정확한 답변을 생성합니다.     ││
│ │                                     ││
│ │ 이는 Embedding 기술로 텍스트를       ││
│ │ 숫자 벡터로 변환한 후, Vector DB    ││
│ │ 에 저장된 정보를 실시간 검색하는    ││
│ │ 방식입니다.                         ││
│ │                                     ││
│ └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│          [ ← 이전 ]      [ 다음 → ]    │
└─────────────────────────────────────────┘
```

### (2) 콘텐츠 내 용어 상호작용 (A 패턴)

```
[읽기 중...]

"RAG(검색 강화 생성)는... Embedding 기술로..."
  ↑ (호버 시)

  ┌───────────────────────────────┐
  │ RAG                           │
  │ Retrieval-Augmented Generation│
  │                               │
  │ LLM이 학습 데이터에 없는      │
  │ 최신 정보를 검색해서 답변     │
  │ 생성에 활용하는 기법.         │
  │                               │
  │ [더 알아보기 →]  [용어집에서]  │
  └───────────────────────────────┘
```

### (3) 대시보드의 용어집 링크

```
┌─────────────────────────────────────────┐
│                GEO 멘토링 시스템         │
├─────────────────────────────────────────┤
│                                         │
│  전체 진도: ████░░░░░░░░░░░░░░░░░░    │
│                                         │
│  [Stage 1 카드 생략...]                │
│                                         │
│  [Stage 2 카드 생략...]                │
│                                         │
├─────────────────────────────────────────┤
│  📚 학습 자료 & 도구                    │
│  • [학습 가이드]                        │
│  • [📖 핵심 용어집 (95개)] ← NEW        │
│  • [진도 다시 설정]                     │
└─────────────────────────────────────────┘
```

### (4) 용어집 페이지 (#/glossary)

```
┌─────────────────────────────────────────┐
│  ← 대시보드로                           │
├─────────────────────────────────────────┤
│                                         │
│  GEO 핵심 용어집                        │
│  ──────────────────                    │
│  총 95개 용어 | 즐겨찾기: 3개          │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ [검색] "RAG" 또는 "생성"        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  카테고리 필터:                         │
│  [전체] [기술/개발] [AI/LLM]           │
│  [SEO/GEO] [마케팅] [Schema]          │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  🔤 A-B                                 │
│  ─────────────────────────────────────  │
│                                         │
│  ★ API (Application Programming        │
│    Interface)                           │
│    정의: 두 소프트웨어 간 통신 규약     │
│    사용처: GEO 시스템에서 데이터 연동  │
│                                         │
│  Alt Text (대체 텍스트)                │
│    정의: 이미지 설명 텍스트             │
│    SEO: 검색 이미지에 노출 중요         │
│                                         │
│  Anchor Text (앵커 텍스트)             │
│    정의: 하이퍼링크의 클릭 가능 텍스트 │
│    SEO: 링크 대상 콘텐츠의 주제 신호   │
│                                         │
│  ──────────────────────────────────────  │
│                                         │
│  🔤 B-C                                 │
│  ─────────────────────────────────────  │
│                                         │
│  ★ Backlink (백링크)                   │
│    정의: 다른 사이트에서 우리 사이트로 │
│          가는 링크                      │
│    중요성: E-E-A-T 신호로 신뢰성 강화 │
│    팁: 품질 높은 사이트의 백링크가     │
│        검색 순위 향상에 더 효과적      │
│                                         │
│  ★ Bot (검색 봇/크롤러)                │
│    정의: 자동으로 웹페이지를 방문하여  │
│          정보를 수집하는 프로그램       │
│    Google Bot: 웹 크롤링 자동화        │
│                                         │
│  [더 보기...↓]                         │
│                                         │
├─────────────────────────────────────────┤
│  최근 검색: [RAG] [SERP] [E-E-A-T]     │
└─────────────────────────────────────────┘
```

## C-3. 기술 명세

### 라우팅 추가

```javascript
// app.js에 새 라우트 추가
const routes = {
  '/': 'dashboard',
  '/stage/:id': 'stage',
  '/module/:id': 'module',
  '/module/:id/result': 'result',
  '/glossary': 'glossary',  // NEW
  '/glossary/:category': 'glossary-filtered', // NEW
};
```

### 용어집 데이터 (seed.py)

```python
# terms.json 또는 database table
glossary_terms = [
  {
    "id": "api-001",
    "term": "API",
    "full_name": "Application Programming Interface",
    "category": "기술/개발",
    "short_def": "두 소프트웨어 간 통신 규약",
    "long_def": "API는...[장문 설명]",
    "use_in_geo": "GEO 시스템에서 데이터 연동...",
    "related_terms": ["JSON-LD", "Schema"],
    "bookmark_count": 12  # 사용자별 추후 추가
  },
  # ... 95개
]
```

### HTML 구조 (용어집 페이지)

```html
<div id="glossary-page">
  <a href="#/" class="back-link">← 대시보드로</a>

  <div class="glossary-header">
    <h1>GEO 핵심 용어집</h1>
    <p class="glossary-meta">
      총 <span id="total-terms">95</span>개 용어 |
      즐겨찾기: <span id="bookmarked-count">0</span>개
    </p>
  </div>

  <!-- 검색 -->
  <div class="glossary-search">
    <input type="text" id="search-input"
           placeholder="'RAG' 또는 '생성'으로 검색"
           class="search-field">
  </div>

  <!-- 카테고리 필터 -->
  <div class="glossary-filters">
    <button class="filter-btn active" data-cat="all">전체</button>
    <button class="filter-btn" data-cat="기술/개발">기술/개발</button>
    <button class="filter-btn" data-cat="AI/LLM">AI/LLM</button>
    <button class="filter-btn" data-cat="SEO/GEO">SEO/GEO</button>
    <button class="filter-btn" data-cat="마케팅">마케팅</button>
    <button class="filter-btn" data-cat="Schema">Schema</button>
  </div>

  <!-- 용어 목록 (알파벳/카테고리 그룹) -->
  <div id="glossary-list" class="glossary-list">
    <!-- JS로 동적 렌더 -->
  </div>
</div>
```

### CSS (용어집 스타일)

```css
.glossary-header {
  margin-bottom: 24px;
}

.glossary-header h1 {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.glossary-meta {
  font-size: 0.9rem;
  color: #666;
}

.glossary-search {
  margin-bottom: 24px;
}

.search-field {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
}

.search-field:focus {
  outline: none;
  border-color: #1a73e8;
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
}

.glossary-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #d0d0d0;
  border-radius: 20px;
  background: #fff;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #1a73e8;
  color: #1a73e8;
}

.filter-btn.active {
  background: #1a73e8;
  color: #fff;
  border-color: #1a73e8;
}

.glossary-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.glossary-group {
  margin-bottom: 16px;
}

.glossary-group-title {
  font-size: 1rem;
  font-weight: 700;
  color: #333;
  border-bottom: 2px solid #1a73e8;
  padding-bottom: 8px;
  margin-bottom: 12px;
}

.glossary-item {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 8px;
  transition: box-shadow 0.2s;
}

.glossary-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.glossary-term-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.glossary-term-text {
  font-weight: 700;
  font-size: 0.95rem;
  color: #222;
}

.glossary-bookmark-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #ccc;
  padding: 4px 8px;
}

.glossary-bookmark-btn.bookmarked {
  color: #f5a623;
}

.glossary-full-name {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 8px;
}

.glossary-short-def {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 8px;
  line-height: 1.5;
}

.glossary-use-in-geo {
  font-size: 0.85rem;
  background: #f8f9ff;
  border-left: 3px solid #1a73e8;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
  color: #444;
  margin-top: 8px;
}

.glossary-related {
  font-size: 0.85rem;
  color: #666;
  margin-top: 8px;
}

.glossary-related strong {
  color: #333;
}

/* Dark Mode */
[data-theme="dark"] .glossary-item {
  background: #0f3460;
  border-color: #2a3a5c;
  color: #d0d0d0;
}

[data-theme="dark"] .glossary-term-text {
  color: #f0f0f0;
}

[data-theme="dark"] .glossary-full-name {
  color: #999;
}

[data-theme="dark"] .glossary-short-def,
[data-theme="dark"] .glossary-related {
  color: #b0b0b0;
}

[data-theme="dark"] .glossary-use-in-geo {
  background: #16213e;
  border-left-color: #3b82f6;
  color: #c0c0d0;
}

[data-theme="dark"] .glossary-group-title {
  color: #f0f0f0;
  border-bottom-color: #2563eb;
}

[data-theme="dark"] .search-field {
  background: #16213e;
  border-color: #2a3a5c;
  color: #d0d0d0;
}

[data-theme="dark"] .search-field:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

[data-theme="dark"] .filter-btn {
  background: #16213e;
  border-color: #2a3a5c;
  color: #d0d0d0;
}

[data-theme="dark"] .filter-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

[data-theme="dark"] .filter-btn.active {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}
```

### JS (용어집 페이지 로직)

```javascript
// 용어집 페이지 렌더
async function renderGlossaryPage() {
  const terms = await apiCall('/api/glossary');

  // 1. 검색 필터
  document.getElementById('search-input').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    filterGlossary(terms, query, currentCategory);
  });

  // 2. 카테고리 필터
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      currentCategory = e.target.dataset.cat;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      filterGlossary(terms, document.getElementById('search-input').value, currentCategory);
    });
  });

  // 3. 초기 렌더
  displayGlossary(terms);
}

function displayGlossary(terms) {
  const list = document.getElementById('glossary-list');
  list.innerHTML = '';

  let currentGroup = '';
  let groupDiv = null;

  terms.forEach(term => {
    const firstLetter = term.term[0].toUpperCase();

    // 그룹 헤더
    if (firstLetter !== currentGroup) {
      currentGroup = firstLetter;
      groupDiv = document.createElement('div');
      groupDiv.className = 'glossary-group';
      const title = document.createElement('div');
      title.className = 'glossary-group-title';
      title.textContent = `🔤 ${currentGroup}`;
      groupDiv.appendChild(title);
      list.appendChild(groupDiv);
    }

    // 용어 아이템
    const item = document.createElement('div');
    item.className = 'glossary-item';
    item.innerHTML = `
      <div class="glossary-term-name">
        <span class="glossary-term-text">${term.term}</span>
        <button class="glossary-bookmark-btn"
                onclick="toggleBookmark('${term.id}')">
          ☆
        </button>
      </div>
      <div class="glossary-full-name">${term.full_name}</div>
      <div class="glossary-short-def">${term.short_def}</div>
      <div class="glossary-use-in-geo">
        <strong>GEO에서의 역할:</strong> ${term.use_in_geo}
      </div>
      ${term.related_terms.length > 0 ? `
        <div class="glossary-related">
          <strong>관련 용어:</strong> ${term.related_terms.join(', ')}
        </div>
      ` : ''}
    `;
    groupDiv.appendChild(item);
  });
}

function filterGlossary(terms, searchQuery, category) {
  let filtered = terms;

  if (category !== 'all') {
    filtered = filtered.filter(t => t.category === category);
  }

  if (searchQuery) {
    filtered = filtered.filter(t =>
      t.term.toLowerCase().includes(searchQuery) ||
      t.full_name.toLowerCase().includes(searchQuery) ||
      t.short_def.toLowerCase().includes(searchQuery)
    );
  }

  displayGlossary(filtered);
}

// 즐겨찾기 (선택적 P1+ 기능)
function toggleBookmark(termId) {
  // localStorage에 저장
  const bookmarked = JSON.parse(localStorage.getItem('bookmarked-terms') || '[]');
  if (bookmarked.includes(termId)) {
    bookmarked.splice(bookmarked.indexOf(termId), 1);
  } else {
    bookmarked.push(termId);
  }
  localStorage.setItem('bookmarked-terms', JSON.stringify(bookmarked));
  location.reload(); // 또는 상태 업데이트
}
```

## C-4. 장점

| 항목 | 설명 |
|------|------|
| **최강 유연성** | 3가지 진입점: 사전 예고(B) + 인라인(A) + 독립 검색(C) |
| **학습 흐름 자유도** | 학습자가 선택: 먼저 읽을지, 중간에 팝오버 볼지, 나중에 검색할지 |
| **재사용성** | 같은 용어를 여러 모듈에서 사용 → 용어집에서 한 번에 검색 |
| **발견성 최강** | 용어집 페이지로 아직 배우지 않은 용어도 찾을 수 있음 |
| **점진적 확장** | MVP는 용어집 없이 시작 → 나중에 추가 가능 |
| **즐겨찾기 기능** | 자주 쓰는 용어 저장 → 학습자 맞춤화 |

## C-5. 단점

| 항목 | 설명 |
|------|------|
| **개발 복잡도 최고** | 3가지 기능을 모두 구현해야 함 |
| **유지보수 부담** | 95개 용어의 정의/카테고리/관계도 관리 필요 |
| **데이터 용량** | 용어집 전체 로드 → API 응답 지연 가능 |
| **학습 흐름 선택지 과다** | 어느 방식을 사용할지 모호할 수 있음 |
| **모듈 개발 지연** | B처럼 각 step마다 핵심 용어 선정 필요 |
| **성능 최적화** | 용어집 페이지 검색/필터 성능 구현 필요 |

## C-6. 구현 복잡도

| 항목 | 비용 |
|------|------|
| **CSS 줄 수** | ~200줄 (A + B + 용어집 페이지) |
| **JS 변경량** | renderKeyTerms + markGlossaryTerms + 용어집 로직 ~250줄 |
| **seed.py 변경** | 용어 테이블 생성 + 각 step의 key_terms ~2시간 |
| **API 엔드포인트** | GET /api/glossary, /api/glossary/{category} 추가 |
| **총 추정** | **높음** (기술 복잡, 콘텐츠 작업 많음) |

---

# 최종 비교표

| 항목 | A (인라인 + 팝오버) | B (핵심 용어 박스) | C (하이브리드 + 용어집) |
|------|------------------|------------------|----------------------|
| **학습 흐름 방해** | 중간 | 낮음 | 낮음 (선택적) |
| **발견성** | 높음 | 중간 | 최고 |
| **맥락 유지** | 매우 높음 | 높음 | 높음 |
| **구현 난이도** | 중간 | 낮음 | 높음 |
| **CSS 줄 수** | ~150 | ~80 | ~200 |
| **JS 변경** | ~100 | ~40 | ~250 |
| **seed.py 작업** | 높음 (수작업) | 중간 (배열 추가) | 높음 (정의+관계도) |
| **개발 기간** | 2~3일 | 1~2일 | 4~5일 |
| **B2B 마케터 만족도** | 높음 | 높음 | 최고 |
| **MVP 적합도** | 중간 | 높음 | 낮음 (과도) |
| **추후 확장성** | C로 확장 가능 | C로 확장 가능 | 완성된 형태 |

---

# 최종 추천안: 접근법 B + 점진적 A 확장

## 왜 B인가?

### 선택 이유

1. **MVP 시간 절약**: 개발 1~2일, seed.py 데이터 작업 2~3시간으로 가장 빠름
2. **학습 효율 증명**: "사전 예고 → 읽기 → 반복" 인지 심리 활용
3. **콘텐츠 품질 보장**: 각 step마다 2~4개씩만 엄선 → 무음 개념 노출 방지
4. **기존 패턴 재활용**: CSS의 `.callout.key-point` 패턴을 그대로 활용
5. **추후 확장 용이**: 추후 언제든 (A) 인라인 + (C) 용어집 페이지 추가 가능
6. **B2B 마케터 심리**: "이 섹션에서 꼭 알아야 할 용어"라는 명확한 신호 제공

### 구현 로드맵

```
Phase 1 (MVP, 1주) — 접근법 B
├─ seed.py: 각 step에 key_terms 배열 추가 (3시간)
├─ CSS: .key-terms-box, .key-terms-list 스타일 (2시간)
├─ JS: renderKeyTerms 함수 구현 (1시간)
└─ 테스트: 16개 모듈 × 5개 step = 80개 step 점검 (2시간)

Phase 2+ (선택적, 추가 1~2주) — A + C 추가
├─ A: 모든 용어에 인라인 하이라이트 + 팝오버
├─ C: 독립된 용어집 페이지 (검색/필터/즐겨찾기)
└─ 통합: 대시보드에서 "용어집" 링크 추가
```

## B 기반 구현 가이드

### Step 1: seed.py 데이터 구조

```python
# 각 step에 이 필드 추가
{
  "id": "m1-1-s1",
  "module_id": "1-1",
  "step_number": 1,
  "type": "card",
  "title": "GEO의 정의",
  "content_md": "## GEO란...",
  "key_terms": [  # ← NEW
    {
      "term": "GEO",
      "full_name": "Generative Engine Optimization",
      "definition": "생성 AI 기반 검색 엔진 최적화"
    },
    {
      "term": "생성 AI",
      "full_name": "Generative AI",
      "definition": "텍스트, 이미지 등을 생성하는 AI"
    }
  ]
}
```

### Step 2: HTML 마크업

```html
<!-- 읽기 카드 상단에 추가 -->
<div class="key-terms-box callout key-point">
  <div class="callout-title">🔑 이 스텝의 핵심 용어</div>
  <div class="callout-body">
    <ul class="key-terms-list">
      <!-- JS에서 렌더 -->
    </ul>
  </div>
</div>
```

### Step 3: CSS (style.css에 추가)

```css
.key-terms-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.key-terms-list li {
  padding: 8px 0;
  border-bottom: 1px solid rgba(26, 115, 232, 0.1);
  color: #333;
}

.key-terms-list strong {
  color: #1a4a8a;
  font-weight: 700;
}

.term-definition {
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-top: 2px;
  margin-left: 16px;
}
```

### Step 4: JS (app.js에 추가)

```javascript
async function renderStepWithKeyTerms(module, step) {
  let html = '';

  // 핵심 용어 박스 렌더
  if (step.key_terms && step.key_terms.length > 0) {
    const termsList = step.key_terms.map(t => `
      <li>
        <strong>${t.term}</strong> (${t.full_name})
        <span class="term-definition">${t.definition}</span>
      </li>
    `).join('');

    html += `
      <div class="key-terms-box callout key-point">
        <div class="callout-title">🔑 이 스텝의 핵심 용어</div>
        <div class="callout-body">
          <ul class="key-terms-list">
            ${termsList}
          </ul>
        </div>
      </div>
    `;
  }

  // 본문 콘텐츠
  html += `
    <div class="reading-card">
      ${marked.parse(step.content_md)}
    </div>
  `;

  return html;
}
```

---

# 추후 확장 계획 (Phase 2+)

## 만약 B가 부족하다면?

### 시점: Stage 1 사용자 피드백 수집 후

**피드백 수집 지표**:
- "콘텐츠 읽다가 갑자기 낯선 용어가 나와요" (빈도)
- "용어집이 있으면 좋을 것 같은데" (요청)
- "호버로 빠른 설명만 원해요" (선호)

### Phase 2A: A 추가 (호버 팝오버)

```
B + A 조합:
[핵심 용어] 박스
  ↓
콘텐츠 읽기 중 호버 → 팝오버
```

**추가 비용**: CSS 150줄 + JS 100줄 (약 3~4시간)

### Phase 2B: C 추가 (용어집 페이지)

```
B + A + C 조합:
[핵심 용어] + 호버 팝오버 + 독립 검색 페이지
```

**추가 비용**: CSS 200줄 + JS 250줄 + 데이터 정의 (약 4~5시간)

---

# 결론

## 최종 권장사항

```
┌─────────────────────────────────────────────────┐
│ 접근법 B (핵심 용어 박스)를 선택하세요          │
├─────────────────────────────────────────────────┤
│                                                 │
│ 이유:                                          │
│ 1. MVP 개발 시간 최단 (1~2일)                  │
│ 2. B2B 마케터 심리에 부합                       │
│ 3. 기존 CSS 패턴 재활용 최대화                  │
│ 4. 추후 A/C 추가 확장 용이                      │
│ 5. 학습 효율 입증된 심리학 기법 활용            │
│                                                 │
│ 구현:                                          │
│ 1. seed.py: key_terms 배열 추가                │
│ 2. HTML: .key-terms-box 마크업                 │
│ 3. CSS: 80줄 추가                              │
│ 4. JS: renderKeyTerms 함수 (~40줄)             │
│                                                 │
│ 추후:                                          │
│ • Phase 2A: 호버 팝오버 추가 (선택)            │
│ • Phase 2B: 용어집 페이지 추가 (선택)          │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 첨부: 핵심 용어 예시 (80~100개 매핑)

### 기술/개발 (~25개)

| 용어 | 전체명 | 정의 |
|------|--------|------|
| API | Application Programming Interface | 두 소프트웨어 간 통신 규약 |
| JSON-LD | JSON Linked Data | 검색 엔진이 이해하는 구조화된 데이터 |
| Schema | Schema.org Markup | 웹페이지 콘텐츠의 의미 정의 |
| SSR | Server-Side Rendering | 서버에서 HTML 생성 |
| CSR | Client-Side Rendering | 브라우저에서 JavaScript로 렌더링 |
| HTML | Hypertext Markup Language | 웹페이지 기본 구조 언어 |
| Canonical | Canonical Tag | 중복 페이지 중 대표 페이지 지정 |
| Sitemap | XML Sitemap | 웹사이트 페이지 목록 제공 |
| robots.txt | — | 검색 봇 접근 제어 파일 |
| — | — | — |

### AI/LLM (~15개)

| 용어 | 전체명 | 정의 |
|------|--------|------|
| RAG | Retrieval-Augmented Generation | 외부 정보 검색해서 생성하는 기법 |
| LLM | Large Language Model | 대규모 언어 학습 모델 |
| GPT | Generative Pre-trained Transformer | OpenAI 생성 AI |
| Embedding | Text Embedding | 텍스트를 숫자 벡터로 변환 |
| Vector DB | Vector Database | 임베딩 저장 및 검색 DB |
| Prompt | — | AI에 주는 명령어/질문 |
| Token | — | 텍스트 처리 단위 |
| — | — | — |

### SEO/GEO (~25개)

| 용어 | 전체명 | 정의 |
|------|--------|------|
| SERP | Search Engine Results Page | 검색 결과 페이지 |
| E-E-A-T | Experience, Expertise, Authoritativeness, Trustworthiness | 신뢰성 신호 |
| Backlink | — | 외부에서 우리 사이트로 오는 링크 |
| Hub-Cluster | — | SEO 사이트 구조 설계 방식 |
| Rich Result | — | 일반 검색 결과보다 상세한 형식 |
| Crawl | — | 검색 봇이 웹페이지 수집하는 행위 |
| Index | — | 검색 엔진이 페이지 저장소에 등록 |
| Ranking Factor | — | 검색 순위를 결정하는 신호 |
| — | — | — |

---

**문서 작성**: 2025-02-22
**대상 담당자**: frontend-dev, product-manager
**관련 파일**: `docs/product/10-prd.md`, `docs/design/20-ux.md`, `apps/api/seed.py`, `apps/web/css/style.css`
