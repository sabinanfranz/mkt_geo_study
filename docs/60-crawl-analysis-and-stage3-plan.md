# 60 — 웹 크롤링 분석 및 Stage 3~5 커리큘럼 계획

**문서 작성일**: 2026-02-22
**대상**: GEO 멘토링 시스템 (Stage 3~5 개발 계획)
**범위**: b2b.fastcampus.co.kr 크롤링 데이터 + 실습 기반 커리큘럼 설계

---

## 목차

1. **Part 1: 크롤링 분석 결과**
2. **Part 2: Stage 3~5 커리큘럼 계획**
3. **Part 3: 크롤링 데이터 활용 맵**
4. **Part 4: 기술 구현 계획**
5. **Part 5: 우선순위 & 로드맵**

---

# Part 1: 크롤링 분석 결과

## 1.1 분석 개요

**크롤링 대상**: b2b.fastcampus.co.kr
**크롤링 일시**: 2026-02-21T22:59:53Z
**페이지 수**: 10개
**수집 항목**: 제목, 메타 설명, 헤딩 구조, 구조화 데이터, 내부/외부 링크, OG 태그

### 크롤링된 페이지 목록

| URL | 상태 | 제목 | 텍스트 길이 |
|-----|------|------|-----------|
| `/` (홈) | 200 | MISSING | 269 chars |
| `/service_custom` | 200 | MISSING | 244 chars |
| `/refer_customer` | 200 | MISSING | 244 chars |
| `/resource_insight_aiforwork` | 200 | O (시티즌 데이터 사이언티스트) | 4797 chars |
| `/resource_seminar_onlinelearning` | 200 | MISSING | 244 chars |
| `/service_aicamp_b2bproposalwai` | 200 | MISSING | 244 chars |
| `/contact` | 200 | O (교육 문의) | 359 chars |
| `/contact_mktg` | 200 | O (기업교육 문의하기) | 350 chars |
| `/info/policies/privacy` | 200 | MISSING | 244 chars |
| `/resource_insight_hrdai` | 200 | O (ChatGPT가 등장한 AI 시대의 디지털 인재 양성) | 4417 chars |

---

## 1.2 핵심 발견사항

### 발견 1: JavaScript 렌더링 문제 (가장 중대)

**문제**: 6개 페이지가 클라이언트 사이드 렌더링(CSR/SPA)으로 구성되어, 봇이 거의 아무 콘텐츠도 볼 수 없음

| 페이지 | 상태 | 문제점 |
|--------|------|--------|
| `/service_custom` | JS-rendered | 244 chars만 수집 (title, meta, H1 MISSING) |
| `/refer_customer` | JS-rendered | 244 chars만 수집 |
| `/resource_seminar_onlinelearning` | JS-rendered | 244 chars만 수집 |
| `/service_aicamp_b2bproposalwai` | JS-rendered | 244 chars만 수집 |
| `/` (홈) | JS-rendered | 269 chars, OG site_name만 O |
| `/info/policies/privacy` | JS-rendered | 244 chars |

**GEO 관점의 영향**:
- **Visibility 신호**: 검색 엔진(특히 Google bot)이 페이지 콘텐츠를 제대로 읽지 못함
- **E-E-A-T 신호**: Title, H1, meta description 부재 → 전문성/신뢰도 신호 약함
- **사용자 신호**: 검색 결과에 나타날 때 클릭률(CTR) 낮음

**교육적 가치**: **Case Study 100점 — "이것을 개선하라" 실습의 완벽한 소재**

---

### 발견 2: SSR 구현 페이지는 뛰어난 상태

4개 페이지만 서버 사이드 렌더링(SSR)으로 구성:

| 페이지 | 콘텐츠 길이 | Title | Meta Desc | H1 | JSON-LD |
|--------|-----------|-------|-----------|----|----|
| `/resource_insight_aiforwork` | 4797 | O | O | O | O (Course) |
| `/resource_insight_hrdai` | 4417 | O | O | O | O (Course) |
| `/contact` | 359 | O | O | O | O (Course) |
| `/contact_mktg` | 350 | O | O | O | O (Course) |

**특징**:
- Canonical URL O
- OG 태그 완전히 구현 (og:title, og:description, og:image, og:url)
- JSON-LD @type: Course 스키마 사용
- 내부 링크 4~5개 (다른 페이지보다 많음)

**교육적 가치**: **"Best Practice" 예시로 활용 가능**

---

### 발견 3: 내부 링크 구조의 극심한 희소성

**전체 내부 링크**: 33개 (10 페이지)
**평균 페이지당 내부 링크**: 3.3개

| 패턴 | 내용 | 문제점 |
|------|------|--------|
| 모든 페이지 공통 링크 | 홈(로고), 문의하기, 개인정보 | Hub이 너무 적음 (3개) |
| 풍부한 연결은 2개만 | `/resource_insight_*` 2개 페이지 | 콘텐츠 허브 미발달 |
| **Hub-Cluster 구조 전무** | — | Stage 2에서 배울 핵심 내용 |

**GEO 관점의 영향**:
- **Authority 신호**: 내부 링크 기반 페이지 순위 결정 미흡
- **Topical Relevance**: 관련 페이지들 간 연결 부족 → 주제 전문성 약함
- **User Journey**: 사용자가 관련 콘텐츠로 자연스럽게 이동 불가

**교육적 가치**: **"내부 링크 재설계" 실습의 라이브 데이터로 활용**

---

### 발견 4: 구조화 데이터 (Structured Data) 부재

| 측정 항목 | 보유 페이지 | 부재 페이지 |
|-----------|-----------|-----------|
| JSON-LD | 4개 | 6개 |
| Microdata | 0개 | 10개 |
| RDFa | 0개 | 10개 |
| BreadcrumbList | 0개 | 10개 |
| Article schema | 0개 | 10개 |
| Event schema | 0개 | 10개 |
| FAQPage schema | 0개 | 10개 |

**문제**: 4개 페이지에만 JSON-LD @type:Course 있으나:
- `/contact`, `/contact_mktg` → **실제로는 "ContactPage"여야 함**
- 템플릿 기본값으로 보임, 의도적 구조화가 아님

**교육적 가치**: **"스키마 오용 수정" 실습의 실제 예시**

---

## 1.3 페이지별 GEO 준비도 채점표

### 평가 기준
- **1점**: 항목 보유 (Yes)
- **0점**: 항목 부재 (No)

| 페이지 | Title | Meta Desc | H1 | Canonical | OG Tags | JSON-LD | 내부링크(3+) | **점수** | 등급 |
|--------|-------|-----------|----|----|---------|---------|-------------|--------|------|
| `/` | 0 | 0 | 0 | 0 | 0.5 | 0 | 0 | **0.5/7** | F |
| `/service_custom` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0/7** | F |
| `/refer_customer` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0/7** | F |
| `/resource_seminar_onlinelearning` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0/7** | F |
| `/service_aicamp_b2bproposalwai` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0/7** | F |
| `/info/policies/privacy` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0/7** | F |
| `/resource_insight_aiforwork` | 1 | 1 | 1 | 1 | 1 | 1 | 1 | **7/7** | A |
| `/contact` | 1 | 1 | 1 | 1 | 1 | 0.5 | 0 | **5.5/7** | B+ |
| `/contact_mktg` | 1 | 1 | 1 | 1 | 1 | 0.5 | 0 | **5.5/7** | B+ |
| `/resource_insight_hrdai` | 1 | 1 | 1 | 1 | 1 | 1 | 1 | **7/7** | A |

**종합 평가**: 평균 2.3/7 (F등급)

---

## 1.4 내부 링크 구조 분석

### 현재 상태: 극도로 단순한 플랫(Flat) 구조

```
┌─────────────────────────────────────────────┐
│            홈 (/)                            │
│     (모든 페이지의 로고링크)                  │
└─────┬────────────────────────────────────┬──┘
      │                                    │
      │                                    │
   문의하기 ◄──────────────────────────── 개인정보처리방침
  (모든 페이지)        (모든 페이지)
      ▲
      │
      │ 단방향 링크 (insight 2개 페이지만)
      │
  insight_aiforwork ←→ insight_hrdai
  (리치 콘텐츠)
```

### 문제점

1. **허브 부족**: 3개 링크(홈, 문의, 개인정보)만이 모든 페이지의 네비게이션
2. **서비스 페이지 고립**: service_custom, service_aicamp 등이 서로 연결 안 됨
3. **사례 허브 부재**: refer_customer(사례 허브)가 다른 사례/콘텐츠 페이지로 연결 안 됨
4. **클러스터 없음**: 관련 주제(예: "AI 교육" 관련 페이지들)가 명시적으로 연결 안 됨

### Stage 2 실습에서 배울 개선안

**대상**: 이 데이터를 바탕으로 "허브-클러스터 맵" 재설계

---

## 1.5 구조화 데이터 현황

### 발견된 JSON-LD 예시

**파일**: `data/crawled/resource_insight_aiforwork.json`

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "시티즌 데이터 사이언티스트...",
  "description": "일반 사무직 임직원을 위한 AI...",
  "url": "https://b2b.fastcampus.co.kr/resource_insight_aiforwork",
  "provider": {
    "@type": "Organization",
    "name": "패스트캠퍼스 기업교육",
    "sameAs": "https://b2b.fastcampus.co.kr/"
  }
}
```

**문제점**:
- ✓ Course 스키마 구조 O
- ✓ Name, Description, URL O
- ✗ Missing: hasCourseInstance, aggregateRating, courseCode, duration
- ✗ Missing: BreadcrumbList (구조화된 네비게이션 경로 없음)

### 놓친 스키마 타입

| 스키마 | 이상적 사용 페이지 | 현 상태 |
|--------|-----------------|--------|
| **BreadcrumbList** | 모든 페이지 | 0/10 |
| **Article** | insight 페이지 2개 | 0/2 |
| **Event** | 세미나 페이지 | 0/1 |
| **FAQPage** | 홈, 서비스 페이지 | 0/10 |
| **ContactPoint** | 문의 페이지 | 0/2 |
| **LocalBusiness** | 홈 페이지 | 0/1 |

---

## 1.6 놓친 요소 체크리스트

### Critical (필수)

| 항목 | 페이지 수 | 파일 참조 | 개선 방법 |
|------|---------|---------|---------|
| **Title 태그** | 6/10 | JS-rendered 페이지 | SSR로 변경 또는 서버에서 제목 전송 |
| **Meta Description** | 6/10 | JS-rendered 페이지 | 각 페이지의 목적 설명 추가 (120자 이내) |
| **H1 태그** | 6/10 | JS-rendered 페이지 | 페이지별 고유 헤딩 구조 설계 |
| **Canonical URL** | 6/10 | JS-rendered 페이지 | 각 페이지의 정준 URL 명시 |
| **Structured Data** | 6/10 | 모든 JS-rendered 페이지 | BreadcrumbList, 페이지별 맞는 스키마 추가 |

### Important (권장)

| 항목 | 페이지 수 | 개선 효과 |
|------|---------|----------|
| **OG 태그 완성** | 6/10 | SNS 공유 시 미리보기 개선 |
| **내부 링크 증가** | 10/10 | Topic Authority 신호 강화 |
| **BreadcrumbList 추가** | 10/10 | 구조화된 네비게이션 신호 |
| **Article 스키마** | 2/10 | Insight 페이지의 E-E-A-T 신호 |
| **FAQ 스키마** | 서비스 페이지 | 하위 검색(Featured Snippet) 개선 |

---

## 1.7 교육 콘텐츠로서의 가치

### 왜 이 크롤링 데이터가 Stage 3~5 실습에 완벽한가?

#### 1. **"Before & After" 비교 가능**
- **Before** (현재): 무엇이 부족한지 명확히 보임
- **After** (개선안): 각 Stage에서 배운 기법을 적용한 예시 작성 가능
- **실제 사례**: 이론 X, 학생이 접근 가능한 회사(FastCampus B2B) 사이트

#### 2. **여러 GEO 레이어가 결합됨**
- **L1 (IA)**: 내부 링크 구조의 희소성
- **L2 (Page Structure)**: Title, H1, Meta Description 부재
- **L3 (Structured Data)**: Schema 부재 또는 오용
- **L4 (Internal Linking)**: Anchor text 약함, Hub-Cluster 미발달
- **L5 (Technical)**: JS 렌더링 문제

#### 3. **학습자가 직접 검증 가능**
```bash
# 학생이 직접 확인 가능:
curl https://b2b.fastcampus.co.kr/service_custom | grep -i "<title>"
# 결과: 아무것도 안 나옴 (예상대로)
```

#### 4. **측정 가능한 개선 목표**
- 현재: 6개 JS-rendered 페이지 → 0개 (또는 N개 SSR)
- 현재: 내부 링크 33개 → 목표: 50개 (Hub-Cluster 구조 추가)
- 현재: Structured Data 4/10 → 목표: 10/10 (각 페이지별 맞는 스키마)

---

# Part 2: Stage 3~5 커리큘럼 계획

## 개요

### Stage 1 & 2 복습
- **Stage 1**: GEO 세계관 이해 (8 modules)
  - M1-1~M1-8: GEO 정의, RAG, 5대 신호, KPI 등

- **Stage 2**: Technical GEO 기초 실습 (8 modules)
  - M2-1~M2-8: IA, 허브-클러스터, Answer-first, FAQ, 헤딩, 내부 링크

### Stage 3~5 신규 설계 (본 문서의 주제)

---

## 2.1 Stage 3: "구조화데이터 & 스키마 마스터" (7 modules)

**학습 목표**: JSON-LD, BreadcrumbList, Article, Event, FAQPage, Course 스키마를 마스터하고, 실제 b2b.fastcampus.co.kr 페이지들에 적용해보기

**학습 방식**:
- 각 모듈: 스키마 이론 (1~2 Step) + 퀴즈 (1 Step) + 실습 (2~3 Step)
- 실습: "현재 b2b 페이지의 스키마를 보고, 무엇이 빠졌는가" → "개선된 스키마 작성"

### M3-1: JSON-LD 기초 & 구조

**목표**: JSON-LD의 정의, 목적, 문법 이해

**Steps** (5개):

1. **Step 1 (읽기 - 패턴 A)**: JSON-LD란?
   ```markdown
   # JSON-LD란?

   JSON-LD(JSON for Linking Data)는 구조화된 데이터를 웹 페이지에 삽입하는 방식입니다.

   ## 왜 필요한가?
   - 검색 엔진이 페이지의 의미를 이해
   - Rich Result로 검색 결과 개선
   - E-E-A-T 신호 강화

   ## 예시
   <script type="application/ld+json">
   {
     "@context": "https://schema.org",
     "@type": "Course",
     "name": "GEO 완벽 가이드"
   }
   </script>
   ```

2. **Step 2 (읽기)**: @context, @type, 속성들의 역할

3. **Step 3 (퀴즈 - 패턴 B)**: 다음 중 올바른 JSON-LD 구조는?
   - ✓ `{"@context": "...", "@type": "...", "name": "..."}`
   - ✗ `{"context": "...", "type": "...", "name": "..."}`
   - ✗ `[{"@context": "...", "@type": "..."}]` (배열은 안 됨)
   - ✗ `<json-ld>...</json-ld>` (HTML 태그가 아님)

   정답 피드백: "JSON-LD는 @context와 @type이 필수입니다."

4. **Step 4 (실습 - 패턴 C)**:
   - 단계 1: "FastCampus B2B 홈페이지에 필요한 스키마는?"
     - 옵션: LocalBusiness / Organization / NewsMediaOrganization
   - 단계 2: (선택 후) "다음 중 Organization 스키마에 필수로 들어가야 하는 속성은?"
     - 옵션: name / description / url / telephone / logo
   - 결과: "모두 포함해야 합니다. 특히 logo는 검색 결과에 표시됩니다."

5. **Step 5 (읽기)**: 현재 b2b.fastcampus.co.kr의 JSON-LD 분석
   ```markdown
   ## 실제 사례: b2b.fastcampus.co.kr

   **페이지**: /resource_insight_aiforwork

   **현재 JSON-LD**:
   ```json
   {
     "@context": "https://schema.org",
     "@type": "Course",
     "name": "시티즌 데이터 사이언티스트...",
     "provider": {...}
   }
   ```

   **부족한 점**:
   - hasCourseInstance 없음 (실제 수강 정보)
   - aggregateRating 없음 (별점)
   - duration 없음 (학습 시간)
   ```

---

### M3-2: BreadcrumbList 스키마 설계

**목표**: 페이지의 네비게이션 경로를 구조화데이터로 표현

**Steps** (5개):

1. **Step 1 (읽기)**: BreadcrumbList의 목적
   - 검색 결과 breadcrumb 표시 (사용자가 경로 한눈에 파악)
   - 페이지 계층 구조 명시

2. **Step 2 (퀴즈)**: BreadcrumbList는 어디에 넣어야 하나?
   - ✓ `<head>` 또는 `<body>`의 `<script type="application/ld+json">`
   - ✗ HTML 태그 속성에 (itemscope)
   - ✗ CSS 주석에

3. **Step 3 (실습)**: b2b.fastcampus의 현재 상태
   - 데이터: `/resource_insight_aiforwork` 페이지의 크롤 결과
   - 질문: "이 페이지의 Breadcrumb 경로는?"
   - 옵션:
     - 홈 > 리소스 > Insight > 시티즌 데이터 사이언티스트
     - 홈 > 기업교육 > 인재 육성 > 시티즌 데이터 사이언티스트
     - 홈 > 시티즌 데이터 사이언티스트
   - 답: "현재 크롤 데이터에 breadcrumb 정보가 없으므로, 우리가 설계해야 함"

4. **Step 4 (실습)**: BreadcrumbList JSON-LD 작성
   ```markdown
   # 과제: 다음 breadcrumb를 JSON-LD로 변환하세요

   홈 > 리소스 > Insight 기사 > 시티즌 데이터 사이언티스트

   [정답 코드 표시]
   {
     "@context": "https://schema.org",
     "@type": "BreadcrumbList",
     "itemListElement": [
       {"@type": "ListItem", "position": 1, "name": "홈", "item": "https://..."},
       {"@type": "ListItem", "position": 2, "name": "리소스", "item": "https://..."},
       ...
     ]
   }
   ```

5. **Step 5 (읽기)**: Stage 4에서 배울 내용 예고
   - "BreadcrumbList는 내부 링크 구조와 함께 설계됩니다"

---

### M3-3: Article 스키마 (콘텐츠 페이지용)

**목표**: Blog post, news, insight 같은 글 페이지에 Article 스키마 적용

**Steps** (5개):

1. **Step 1 (읽기)**: Article 스키마의 역할
   - "시티즌 데이터 사이언티스트" 페이지는 blog article
   - Article 스키마 사용 시: headline, datePublished, author, articleBody 등 추가 신호

2. **Step 2 (퀴즈)**: Article 스키마의 필수 속성은?
   - ✓ headline, datePublished, author
   - ✗ description만 가능
   - ✗ name만 가능

3. **Step 3 (실습)**: b2b 데이터 분석
   - 파일: `data/crawled/resource_insight_aiforwork.json`
   - 추출 가능한 정보:
     - title → headline
     - published date (메타데이터) → datePublished
     - text_content → articleBody
     - images → image
   - 질문: "현재 데이터로 Article 스키마를 작성할 수 있는가? 무엇이 부족한가?"
     - 답: author, publisher 정보 부족

4. **Step 4 (실습)**: Article 스키마 개선안 작성
   ```markdown
   # FastCampus B2B 콘텐츠를 위한 Article 스키마

   {
     "@context": "https://schema.org",
     "@type": "Article",
     "headline": "시티즌 데이터 사이언티스트...",
     "datePublished": "2023-08-09",
     "author": {
       "@type": "Organization",
       "name": "패스트캠퍼스 기업교육"
     },
     "image": "https://...",
     "articleBody": "..."
   }
   ```

5. **Step 5 (읽기)**: Article과 Course 스키마의 관계
   - "일부 페이지는 Course이면서 동시에 Article일 수 있습니다 (교육 콘텐츠)"

---

### M3-4: Event 스키마 (세미나/웨비나용)

**목표**: `/resource_seminar_onlinelearning` 같은 이벤트 페이지에 Event 스키마 적용

**Steps** (5개):

1. **Step 1 (읽기)**: Event 스키마의 역할
   - 세미나, 워크숍, 컨퍼런스 등의 구조화
   - Google Events 검색 결과 표시

2. **Step 2 (퀴즈)**: Event 스키마의 필수 속성
   - ✓ name, startDate, endDate, location (또는 eventAttendanceMode)
   - ✗ duration만으로 충분

3. **Step 3 (실습)**: b2b 데이터 분석
   - `/resource_seminar_onlinelearning` 크롤 결과: 244 chars (거의 아무것도 없음)
   - 질문: "이 페이지가 온라인 세미나라면, 어떤 정보가 필요한가?"
   - 옵션: 세미나명 / 개최일 / 장소 / 참가비 / 신청 링크
   - 모두 필요

4. **Step 4 (실습)**: Event 스키마 설계
   ```markdown
   # b2b.fastcampus의 온라인 세미나를 위한 Event 스키마

   {
     "@type": "Event",
     "name": "온라인 학습 세미나",
     "startDate": "2026-03-15T14:00:00",
     "endDate": "2026-03-15T15:30:00",
     "eventAttendanceMode": "OnlineEventAttendanceMode",
     "location": {
       "@type": "VirtualLocation",
       "url": "https://..."
     },
     "offers": {
       "@type": "Offer",
       "price": "0",
       "priceCurrency": "KRW"
     }
   }
   ```

5. **Step 5 (읽기)**: Event와 Course의 차이
   - "Course는 지속적인 교육 프로그램"
   - "Event는 일회성 행사"

---

### M3-5: FAQPage 스키마

**목표**: FAQ 섹션을 structured data로 표현

**Steps** (5개):

1. **Step 1 (읽기)**: FAQPage의 가치
   - Featured Snippet (검색 결과 최상위에 표시)
   - 사용자 질문에 직접 답변

2. **Step 2 (퀴즈)**: FAQPage 구조
   - ✓ mainEntity: [FAQPage], itemListElement: [Question/Answer]
   - ✗ FAQPage만 있으면 충분

3. **Step 3 (실습)**: b2b 데이터로 FAQ 작성
   - 데이터: `/contact` 페이지 크롤 결과
   - "이 페이지에서 예상되는 고객 질문은?"
   - 옵션: 비용 / 교육 기간 / 선행학습 요구사항 / 환불 정책
   - 모두 FAQ로 만들 가치 있음

4. **Step 4 (실습)**: FAQPage JSON-LD 작성
   ```markdown
   {
     "@context": "https://schema.org",
     "@type": "FAQPage",
     "mainEntity": [
       {
         "@type": "Question",
         "name": "기업교육 문의는 정말 무료인가요?",
         "acceptedAnswer": {
           "@type": "Answer",
           "text": "네, 패스트캠퍼스의 모든 기업교육 상담은 비용이 들지 않습니다..."
         }
       }
     ]
   }
   ```

5. **Step 5 (읽기)**: FAQPage와 지속적인 업데이트
   - "고객 피드백에서 나온 질문들을 FAQ에 추가"
   - "Stage 5에서 측정할 내용: FAQ 노출 시간, CTR 변화"

---

### M3-6: 스키마 Validation & Rich Results Test

**목표**: 작성한 스키마가 올바른지 Google 도구로 검증

**Steps** (4개):

1. **Step 1 (읽기)**: Schema.org Validator vs Google Rich Results Test
   - 차이점: Schema.org는 문법, Google은 실제 표시 여부

2. **Step 2 (실습)**: 과제 스키마 검증
   - 제시된 잘못된 JSON-LD 4개
   - 각각: "이것의 오류는?" (선택지 제시)
   - 예: Missing @context, Wrong property name, Invalid @type

3. **Step 3 (실습)**: 현재 b2b.fastcampus 데이터 검증
   - `/resource_insight_aiforwork` 스키마를 Google Rich Results Test 결과로 평가
   - "현재 상태에서 Rich Results 표시 여부?"
   - 답: "hasCourseInstance 부재로 일부 정보 미표시"

4. **Step 4 (읽기)**: 검증 워크플로우
   - 개발 → Schema validation → Google test → 배포

---

### M3-7: 종합 실습 & 평가

**목표**: M3-1~M3-6에서 배운 모든 스키마를 실제 페이지에 적용

**Steps** (3개):

1. **Step 1 (실습 - 패턴 C)**: b2b.fastcampus의 "서비스" 페이지 재설계
   - Stage: `/service_custom` (현재 JS-rendered, 콘텐츠 없음)
   - 과제: "이 페이지가 서비스 소개 페이지라면, 어떤 스키마들이 필요한가?"
   - 단계 1: 페이지 타입 선택 (Product / Service / Course / LocalBusiness)
   - 단계 2: 각 타입별 필수 속성 선택
   - 결과: "Product 또는 Service 스키마 추천. 다음과 같은 구조 제안..."

2. **Step 2 (실습 - 패턴 C)**: `/refer_customer` (사례 허브) 재설계
   - 과제: "고객 사례를 모아놓은 페이지로, 어떤 스키마로 구조화할까?"
   - 단계 1: CollectionPage vs ItemList
   - 단계 2: 각 사례(아이템)의 스키마는?
   - 결과: "CollectionPage + Article (각 사례) + AggregateRating"

3. **Step 3 (평가 - 패턴 B)**: 종합 평가 (8개 선택지)
   - "M3에서 배운 7개 스키마 각각의 정의/목적 매칭"
   - 정답율 70% 이상 시 M3 완료

---

## 2.2 Stage 4: "오프사이트 & 멘션 전략" (7 modules)

**학습 목표**: Backlink, Digital PR, 소셜 분산, 리뷰/디렉토리 등 Site 외부의 신호를 이해하고, b2b.fastcampus의 off-site 전략을 설계

**배경**: Stage 2에서 배운 "내부 링크 구조"의 부족함을 보완하기 위해, 외부 링크(backlink)와 멘션(mention)의 중요성

---

### M4-1: Off-site GEO 개요 (MECE 5 Category)

**목표**: Off-site 신호를 5가지로 분류하고 이해

**Steps** (5개):

1. **Step 1 (읽기)**: Off-site GEO란?
   ```markdown
   ## Off-site GEO란?

   Site 외부에서의 신호:
   - Backlink (링크 투표)
   - Brand Mention (브랜드 언급)
   - Social Distribution (소셜 공유)
   - Digital PR (보도/인용)
   - Review/Directory (평가/리스팅)

   이들이 "Authority" 신호를 강화합니다.
   ```

2. **Step 2 (읽기)**: 5 Category 상세 설명
   ```markdown
   ### Category 1: Backlink (하이퍼링크 투표)
   - 다른 사이트가 당신을 링크
   - 신뢰도 + 유입 트래픽 동시 효과

   ### Category 2: Brand Mention (브랜드 명시적 언급)
   - URL 없이 "패스트캠퍼스"라고 쓰여 있음
   - Context가 중요 (좋은 평가인가 vs 부정적인가)

   ### Category 3: Social Distribution (SNS 공유)
   - LinkedIn, Facebook 등에서의 공유 수
   - Direct traffic + 알고리즘 신호

   ### Category 4: Digital PR (보도 & 인용)
   - 매체 기사에 인용
   - 업계 저널, 뉴스레터

   ### Category 5: Review/Directory (평가 & 디렉토리 등재)
   - Google My Business, 업체 평가 사이트
   - 신뢰도 신호 (별점, 리뷰 수)
   ```

3. **Step 3 (퀴즈)**: 5 Category 분류 게임
   - "다음 신호는 어느 카테고리에 속하나?"
   - 예시: "LinkedIn에서 FastCampus 게시물 100회 공유"
     - 정답: Category 3 (Social Distribution)
   - 예시: "업계 뉴스레터 'HR Daily'에서 FastCampus 인용"
     - 정답: Category 4 (Digital PR)

4. **Step 4 (실습)**: b2b.fastcampus의 현재 off-site 신호 분석
   - 크롤 데이터: external_links (43개)
   - 질문: "현재 크롤 데이터에서 backlink 정보가 보이나?"
   - 답: "아니요. 크롤은 outbound만 추적. Inbound(backlink)는 별도 도구(Ahrefs, SEMrush) 필요"
   - 교육적 포인트: "GEO 측정 도구의 한계"

5. **Step 5 (읽기)**: Stage 4 전체 로드맵
   - M4-1: Off-site 개요 (지금)
   - M4-2: Backlink 전략
   - M4-3: Mention 신호
   - M4-4: Social Amplification
   - M4-5: PR & Coverage
   - M4-6: Review & Trust Signals
   - M4-7: 종합 off-site 계획 수립

---

### M4-2: Backlink 전략 & Anchor Text

**목표**: Backlink 품질, anchor text 최적화 이해

**Steps** (5개):

1. **Step 1 (읽기)**: Backlink의 가치
   - "PageRank 모델: 다른 페이지가 링크할수록 중요도 높음"
   - 품질: Domain Authority + Relevance + Placement (위치)

2. **Step 2 (퀴즈)**: 좋은 Backlink의 특징
   - ✓ 높은 도메인 오서리티 + 관련 있는 내용 + 자연스러운 anchor text
   - ✗ 많은 양 (품질 무시)
   - ✗ 모두 "Click here" 같은 Generic anchor text

3. **Step 3 (실습)**: b2b.fastcampus의 "링크 유입 기회" 분석
   - 시나리오: "FastCampus 인사이트 기사가 업계 뉴스레터, 블로그 등에서 인용되려면?"
   - 현재 크롤 데이터: Gartner, Medium (Airbnb) 외부 링크 있음
   - 질문: "Gartner 링크(Citizen Data Scientist 원문)는 FastCampus에 Backlink가 되나?"
   - 답: "아니요. FastCampus는 Gartner 링크만 함. 반대가 필요"

4. **Step 4 (실습 - 패턴 C)**: Anchor text 최적화
   - 시나리오: "FastCampus B2B가 인사이트 기사 2개를 보유"
   - 단계 1: "이 기사들을 링크할 때 최적의 anchor text는?"
     - 옵션: "여기", "클릭", "시티즌 데이터 사이언티스트", "AI 교육 사례"
   - 단계 2: 각 anchor text의 효과 평가
   - 결과: "구체적이고 관련 있는 anchor text 권장"

5. **Step 5 (읽기)**: Backlink 구축 전략
   - "자연스러운 링크 획득의 어려움"
   - "PR + Content Marketing 필요"

---

### M4-3: Brand Mention & Unlinked Mention

**목표**: URL 없이 브랜드명만 언급되는 신호의 가치 이해

**Steps** (5개):

1. **Step 1 (읽기)**: Unlinked Mention의 정의
   ```markdown
   ## Unlinked Mention

   "패스트캠퍼스 기업교육이 이 교육을 제공합니다"
   → "패스트캠퍼스" 글자만 있고 링크는 없음

   Google, Bing이 "mention" 신호로 인식 가능
   → 하지만 backlink보다는 약함
   ```

2. **Step 2 (퀴즈)**: Mention의 문맥(context) 중요성
   - "긍정적 멘션" vs "부정적 멘션"
   - 예: "[회사명] 사기 꼬리" → 부정적 신호
   - 예: "[회사명] 최고의 교육 제공사" → 긍정적 신호

3. **Step 3 (실습)**: b2b.fastcampus의 Mention 찾기
   - 시나리오: "FastCampus 블로그, SNS, 뉴스에서 브랜드 언급"
   - 크롤 데이터: Facebook, Kakao, Naver Blog, LinkedIn 링크 있음
   - 질문: "이 채널들에서 FastCampus B2B 멘션 빈도는?"
   - 답: "크롤 데이터에서는 알 수 없음. SNS 모니터링 도구 필요"

4. **Step 4 (실습 - 패턴 B)**: 멘션 신호 강화 전략
   - "고객 후기에서 FastCampus 브랜드명 노출"
   - "업계 리포트에서 인용"
   - "포럼/커뮤니티에서 추천"

5. **Step 5 (읽기)**: Mention 신호의 미래
   - "구글의 알고리즘 진화: 링크 없는 멘션도 신호화 추세"

---

### M4-4: Social Amplification Strategy

**목표**: SNS를 통한 콘텐츠 확산 전략

**Steps** (5개):

1. **Step 1 (읽기)**: Social Signal의 역할
   - Direct traffic (SNS → 사이트 직접 이동)
   - Indirect signal (SNS 공유 수 → 콘텐츠 품질)

2. **Step 2 (퀴즈)**: 각 SNS별 GEO 효과
   - ✓ LinkedIn (B2B 콘텐츠, 높은 신뢰도)
   - ✓ Facebook (광범위 사용자, 트래픽)
   - ✗ Instagram (링크 추가 어려움)
   - 부분: Twitter/X (실시간 멘션)

3. **Step 3 (실습)**: b2b.fastcampus의 SNS 채널
   - 크롤 데이터에서 발견:
     - Facebook: https://www.facebook.com/b2bfastcampus
     - Kakao: https://pf.kakao.com/_LxbMxnb
     - Naver Blog: https://blog.naver.com/fastcampus
     - LinkedIn: https://www.linkedin.com/showcase/b2bfastcampus
   - 질문: "어느 채널이 B2B 오디언스에 가장 효과적인가?"
   - 답: "LinkedIn > Naver > Facebook > Kakao"

4. **Step 4 (실습 - 패턴 C)**: SNS별 콘텐츠 전략
   - 단계 1: 콘텐츠 타입 선택 (긴 글 vs 짧은 텍스트 vs 이미지)
   - 단계 2: 각 SNS의 특성에 맞는 포맷 추천
   - 결과: "LinkedIn에서는 인사이트 기사 전체 공유 → 높은 engagement"

5. **Step 5 (읽기)**: 소셜 공유 최적화 (OG 태그)
   - Stage 1 크롤 분석에서: OG 태그 5/10 페이지만 완전
   - "OG 태그 개선 → SNS 미리보기 개선 → 클릭율 증가"

---

### M4-5: Digital PR & Press Coverage

**목표**: 매체 보도, 업계 저널 인용 전략

**Steps** (5개):

1. **Step 1 (읽기)**: Digital PR의 정의
   - "온라인 매체, 블로그, 뉴스레터 등에서의 보도"
   - "Earned media (비용 없이 얻는 언급)"

2. **Step 2 (퀴즈)**: PR 기회의 선별
   - ✓ 업계 관련 매체 (HRD 매거진, 기업교육 뉴스)
   - ✗ 무관한 분야 (스포츠, 엔터)

3. **Step 3 (실습)**: b2b.fastcampus의 기존 PR 사례
   - 크롤 데이터: resource_insight_hrdai 페이지
   - "월간인재경영 23년 4월호에 기고한 글" (크롤 데이터의 외부 링크 중)
   - 질문: "이것이 Digital PR의 예시인가?"
   - 답: "네. FastCampus 콘텐츠가 업계 저널(월간인재경영)에 게재 → Earned media"

4. **Step 4 (실습 - 패턴 C)**: PR 기회 식별
   - 단계 1: FastCampus의 고유한 데이터/사례는?
   - 단계 2: 어떤 매체에 피칭할 만한가?
   - 결과: "HR 포럼 → ChatGPT 시대 인재 양성 기사 기획 제안"

5. **Step 5 (읽기)**: PR & Backlink의 연쇄 효과
   - "저널에 게재 → 다른 매체 인용 → 여러 백링크 확보"

---

### M4-6: Review & Directory Listings

**목표**: 평가 사이트, 업체 디렉토리 등재

**Steps** (4개):

1. **Step 1 (읽기)**: Review의 신뢰 신호
   - Google, Naver 지도 리뷰
   - 업계 평가 사이트 (교육 플랫폼 리뷰)

2. **Step 2 (퀴즈)**: Review Rating의 효과
   - High rating + 많은 리뷰 수 → Trust signal 강화

3. **Step 3 (실습)**: b2b.fastcampus의 Review 전략
   - 현재: 크롤 데이터에 리뷰 정보 없음
   - 질문: "기업교육 회사로서, 어디서 리뷰 수집을 우선해야 하나?"
   - 옵션: Google My Business / Naver 지도 / HR 커뮤니티 / 교육 플랫폼 평가
   - 답: "Google My Business (글로벌) + Naver (국내) 우선"

4. **Step 4 (읽기)**: Directory Listing
   - "B2B 디렉토리 (Clutch, G2 등)에 등재"
   - "SEO + Credibility 동시 효과"

---

### M4-7: 종합 Off-site 전략 설계

**목표**: 5 Category를 종합하여 b2b.fastcampus의 off-site 로드맵 작성

**Steps** (2개):

1. **Step 1 (실습 - 패턴 C, 3단계)**: Off-site 기회 분석
   - 단계 1: "당신이 FastCampus 마케팅 담당자라면, 가장 실행 가능한 off-site 신호는?"
     - 옵션: Digital PR / Social Amplification / Review Gathering / Backlink Campaign
   - 단계 2: "선택한 전략의 단계별 실행 계획은?"
     - 옵션들 제시
   - 단계 3: "3개월 안에 측정할 KPI는?"
   - 결과: "구체적인 로드맵 예시 제시"

2. **Step 2 (평가 - 패턴 B)**: 종합 평가
   - "M4-1~M4-6에서 배운 5 Category의 정의, 전략, 우선순위 매칭"
   - 8개 선택지
   - 정답율 70% 이상 시 M4 완료

---

## 2.3 Stage 5: "측정 & 실험 설계 실전" (7 modules)

**학습 목표**: KPI 3-layer, GSC/GA4, AI Validator routine을 이용한 실험 설계 및 측정

**배경**: Stage 3~4에서 개선한 내용들이 실제로 효과가 있는지 검증하는 방법

---

### M5-1: KPI 3-layer Framework

**목표**: Visibility / Behavior / Authority 3층의 KPI 이해

**Steps** (5개):

1. **Step 1 (읽기)**: KPI 3-layer 개요
   ```markdown
   ## KPI 3-layer

   ### Layer 1: Visibility (가시성)
   - 검색 엔진에서 노출되는가?
   - 측정: Impressions, Average Position, Keyword Rankings

   ### Layer 2: Behavior (행동)
   - 사용자가 클릭하고 체류하는가?
   - 측정: CTR, Sessions, Pages/Session, Bounce Rate

   ### Layer 3: Authority (권위)
   - 외부에서 인정하는 신뢰도는?
   - 측정: Backlinks, Domain Rating, Mentions
   ```

2. **Step 2 (읽기)**: 각 Layer의 관계
   - "Visibility ↑ → Behavior ↑ → Authority ↑"
   - "하지만 모두 동시에 일어나지 않음 (시간차)"

3. **Step 3 (퀴즈)**: Layer별 도구 매칭
   - Layer 1 (Visibility) → ?
     - ✓ Google Search Console, SEMrush, Ahrefs
   - Layer 2 (Behavior) → ?
     - ✓ Google Analytics 4, GA
   - Layer 3 (Authority) → ?
     - ✓ Ahrefs, Majestic, Semrush (backlink)

4. **Step 4 (실습)**: b2b.fastcampus 크롤 데이터로 현황 분석
   - 가용 데이터:
     - Text length (콘텐츠 양) → Behavior의 proxy
     - Internal links (내부 링크) → Authority 신호
   - 질문: "현재 데이터로 3-layer 측정이 가능한가?"
   - 답: "부분적. 실제 Visibility/Behavior/Authority는 도구 필요"

5. **Step 5 (읽기)**: Stage 5 전체 로드맵
   - M5-1: KPI 3-layer (지금)
   - M5-2: GSC 활용법
   - M5-3: GA4 분석
   - M5-4: AI Validator Routine
   - M5-5: 실험 설계 (Hypothesis → Test → Measure)
   - M5-6: A/B Testing & Multivariate Testing
   - M5-7: 90일 측정 & 개선 로드맵

---

### M5-2: Google Search Console (GSC) 활용

**목표**: GSC에서 Visibility 데이터 해석

**Steps** (5개):

1. **Step 1 (읽기)**: GSC의 역할
   - "Google이 보는 당신의 사이트"
   - "Search Analytics (Impressions, Clicks, Position)"
   - "Index Coverage (크롤 가능성)"
   - "Core Web Vitals (성능)"

2. **Step 2 (퀴즈)**: GSC 주요 지표
   - Impressions: "검색 결과에 노출된 수"
   - Clicks: "검색 결과에서 클릭한 수"
   - Position: "평균 순위 (1~100)"
   - CTR: Clicks / Impressions

3. **Step 3 (실습)**: b2b.fastcampus의 GSC 가상 시나리오
   - 시나리오: "Stage 3에서 구조화 데이터 추가 후, GSC에서 어떤 변화를 기대하나?"
   - 옵션:
     - Impressions 증가 (새 키워드 인식)
     - CTR 증가 (Rich Result 표시로 매력도 증가)
     - Position 상승
   - 모두 가능 (순차적)

4. **Step 4 (실습 - 패턴 C)**: GSC 데이터 분석
   - 단계 1: "Performance 리포트에서 CTR이 1%라면, 무엇을 개선해야 하나?"
     - 옵션: Title / Meta Description / Content Quality / Backlinks
   - 단계 2: "Position이 20위라면?"
     - 옵션: Title + Meta Desc 개선 / 콘텐츠 확대 / 백링크 추가
   - 결과: "Layer 1 (Visibility) 개선은 주로 Title, Meta, Backlinks"

5. **Step 5 (읽기)**: GSC 알림 설정
   - "Mobile Usability", "Crawl Issues" 등 모니터링

---

### M5-3: Google Analytics 4 (GA4) 활용

**목표**: Behavior 데이터 해석 및 이벤트 추적

**Steps** (5개):

1. **Step 1 (읽기)**: GA4 vs Universal Analytics
   - GA4: "Event-based" (모든 상호작용이 이벤트)
   - UA: "Session-based" (구식)

2. **Step 2 (퀴즈)**: GA4의 주요 이벤트
   - ✓ Page View, Scroll, Click, Form Submit
   - ✗ Bounce (더 이상 기본 이벤트 아님)

3. **Step 3 (실습)**: b2b.fastcampus의 GA4 설정
   - 가상 시나리오: "학습 플랫폼 (Stage 1~2) 도입 후, 측정해야 할 이벤트는?"
   - 옵션:
     - Module Start / Step Completion / Quiz Answer / Stage Unlock
     - Lesson Duration / Scroll Depth / Feedback Click
   - 모두 중요 (학습 행동 추적)

4. **Step 4 (실습 - 패턴 B)**: GA4 이벤트 해석
   - "사용자가 M1-3 Step에서 자주 이탈한다면?"
   - ✓ 콘텐츠 이해도 낮음 / 문제 난이도 높음 / UX 문제
   - "다음 단계: 그 Step의 피드백 개선 or 사전 학습 추가"

5. **Step 5 (읽기)**: GA4 대시보드 설계
   - "학습 플랫폼용 커스텀 대시보드"
   - "Module별 completion rate"
   - "Stage별 pass rate"

---

### M5-4: AI Validator Routine

**목표**: 자동화된 GEO 검증 프로세스 (10개 prompt template)

**Steps** (4개):

1. **Step 1 (읽기)**: AI Validator의 정의
   ```markdown
   ## AI Validator Routine

   주기적(주 1회)으로 사이트의 GEO 상태를 AI(ChatGPT 등)에게 검증하도록 하는 프로세스

   목적:
   - 실수 조기 발견 (Title 누락, H1 중복 등)
   - 콘텐츠 품질 평가
   - 개선 사항 자동 제안
   ```

2. **Step 2 (퀴즈)**: AI Validator의 한계
   - ✓ 구조적 오류 (Missing Title, Duplicate H1) 감지
   - ✗ 랭킹 원인 (순위 직접 예측 불가)
   - ✗ 사용자 의도 완벽 해석 (사람의 검증 필요)

3. **Step 3 (실습)**: 10개 Prompt Template 학습
   - Template 1: "다음 URL의 Title, Meta Description, H1을 추출하고 평가해줘"
   - Template 2: "JSON-LD 스키마를 검증해줘"
   - Template 3: "내부 링크 구조의 문제점을 찾아줘"
   - Template 4: "이 페이지의 E-E-A-T 신호 강도를 평가해줘"
   - ...등 10개 (materials 파일에서 큐레이션)

4. **Step 4 (읽기)**: AI Validator 실행 빈도
   - "주 1회 자동 실행"
   - "월 1회 수동 검토"

---

### M5-5: 실험 설계 (Hypothesis → Test → Measure)

**목표**: GEO 개선을 가설 검증으로 실행

**Steps** (5개):

1. **Step 1 (읽기)**: 실험의 3단계
   ```markdown
   ## 실험 설계의 3단계

   ### Phase 1: Hypothesis (가설)
   "Title에 주요 키워드 추가 → CTR 증가"

   ### Phase 2: Test (실행)
   "10개 페이지의 Title 변경"

   ### Phase 3: Measure (측정)
   "4주 후 GSC에서 CTR 비교"
   ```

2. **Step 2 (퀴즈)**: 좋은 가설의 조건
   - ✓ 실행 가능 + 측정 가능 + 구체적
   - ✗ "순위 올릴 거다" (너무 모호)
   - ✗ "백링크 1000개 만들거다" (비현실적)

3. **Step 3 (실습)**: b2b.fastcampus의 6가지 가설 설계
   - 가설 1: "구조화 데이터 추가 → Rich Result 표시 → CTR +15%"
   - 가설 2: "내부 링크 추가 → 평균 체류 시간 +20%"
   - 가설 3: "Meta Description 최적화 → Impressions 유지, CTR +10%"
   - 가설 4: "Answer-first 구조 → Scroll Depth +30%"
   - 가설 5: "FAQ 스키마 추가 → Featured Snippet 노출 +5개"
   - 가설 6: "Social OG 태그 개선 → SNS 공유율 +25%"

4. **Step 4 (실습 - 패턴 C)**: 가설 우선순위화
   - 단계 1: "가장 구현 간단한 가설 선택"
   - 단계 2: "가장 높은 영향도 가설 선택"
   - 단계 3: "90일 내 실행 가능한 가설 3개 선정"
   - 결과: "Hypothesis 1, 3, 5 우선 시행"

5. **Step 5 (읽기)**: 측정 기간 & 신뢰도
   - "최소 4주 (계절 변동 고려)"
   - "가능하면 12주 (3개월) 이상"

---

### M5-6: A/B Testing & Multivariate Testing

**목표**: 통제된 환경에서 변수 검증

**Steps** (4개):

1. **Step 1 (읽기)**: A/B Test vs Multivariate Test
   - A/B: "변수 1개 변경 (Title 길이: 길게 vs 짧게)"
   - Multivariate: "변수 2개 이상 (Title + Meta Desc)"

2. **Step 2 (퀴즈)**: A/B Test의 조건
   - ✓ 트래픽 충분 (최소 주 100회 이상 impressions)
   - ✓ 충분한 기간 (최소 1주~2주)
   - ✗ 너무 많은 테스트 동시 진행 (간섭 효과)

3. **Step 3 (실습)**: b2b.fastcampus의 A/B Test 설계
   - 시나리오: "Meta Description 길이 테스트"
   - Control: "기존 120자 description (5 페이지)"
   - Variant A: "155자 description (5 페이지)"
   - Variant B: "85자 description (5 페이지)"
   - 측정: "2주 후 CTR 비교"

4. **Step 4 (읽기)**: 통계적 유의성
   - "샘플 수 충분한가?"
   - "차이가 우연의 산물은 아닌가? (p-value < 0.05)"

---

### M5-7: 90일 측정 & 개선 로드맵

**목표**: 4개 Phase로 나눈 90일 실행 계획

**Steps** (2개):

1. **Step 1 (실습 - 패턴 C, 3단계)**: 90일 로드맵 수립
   - 단계 1: "Phase별 우선순위 선택"
     - Phase 1 (0~30일): Visibility (Title, Meta Desc, Schema)
     - Phase 2 (30~60일): Behavior (Content, Internal Links, Page Speed)
     - Phase 3 (60~90일): Authority (PR, Backlinks, Mentions)
   - 단계 2: "각 Phase의 KPI 목표 설정"
     - Phase 1: Impressions 유지, CTR +10%
     - Phase 2: Sessions +20%, Pages/Session +15%
     - Phase 3: Backlinks +5, Mentions +10
   - 단계 3: "주간 점검 (Weekly Review) 계획"
   - 결과: "구체적인 90일 로드맵 문서"

2. **Step 2 (평가 - 패턴 B)**: 종합 평가
   - "M5-1~M5-6에서 배운 측정 방법, 도구, 실험 설계 종합"
   - 8개 선택지
   - 정답율 70% 이상 시 Stage 5 완료

---

# Part 3: 크롤링 데이터 활용 맵

## 개요

각 Stage에서 학습한 내용을 **실제 b2b.fastcampus.co.kr 데이터**와 매핑.

---

## Stage 3: 구조화데이터 & 스키마 마스터

### M3-1: JSON-LD 기초

| 학습 내용 | 크롤 데이터 참조 | Before (현재) | After (개선안) | 실습 파일 |
|----------|-----------------|---------------|-----------------|----------|
| JSON-LD 정의 | 개념 설명 (자료) | — | — | materials/ |
| 예시 이해 | `resource_insight_aiforwork.json` (lines 36~48) | Course schema 1개만 있음 | Course + BreadcrumbList + Article | seed_data/stage3/ |
| @context, @type | `resource_insight_aiforwork.json` | ✓ 있음 | — | quiz_step |
| 속성 이해 | `resource_insight_aiforwork.json` | name, description, url, provider만 있음 | + hasCourseInstance, aggregateRating, duration | practice_step |

**실습 데이터**:
- **파일**: `data/crawled/resource_insight_aiforwork.json` (4797 chars, 완전한 SSR 콘텐츠)
- **Before**: Line 36~48의 JSON-LD (부족함)
- **After**: 개선된 스키마 (students 직접 작성)

### M3-2: BreadcrumbList

| 학습 내용 | Before | After | 파일 |
|----------|--------|-------|------|
| Breadcrumb 정의 | 크롤 데이터에 breadcrumb 정보 없음 | `/` > `/resource` > `/insight` > `/resource_insight_aiforwork` | schema_output/ |
| 경로 설계 | 현재: 3개 링크(홈, 문의, 개인정보)만 | 10개 페이지의 체계적 hierarchical structure | quiz_step |
| JSON-LD 작성 | — | students 직접 작성 | practice_output/ |

**실습 파일**:
- `data/crawled/index.json` (HOME 구조)
- `data/crawled/_summary.json` (10개 페이지 목록)

### M3-3: Article 스키마

| 학습 내용 | Before | After |
|----------|--------|-------|
| 정의 | — | 콘텐츠 기사(insight) 페이지에 필요 |
| 필수 속성 | `resource_insight_aiforwork.json`: text_content만 있음 | headline, datePublished, author, articleBody, image 모두 포함 |
| 예시 | 부재 | `resource_insight_aiforwork.json` 데이터로 개선안 작성 |

**실습**:
```json
// Before (현재 크롤 데이터의 일부)
{
  "title": "시티즌 데이터 사이언티스트...",
  "text_content": "발행 2023년 8월 9일...",
  "json_ld": [{"@type": "Course", ...}]  // Article 스키마 없음!
}

// After (학생이 작성해야 할 것)
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "datePublished": "2023-08-09",
  "author": {
    "@type": "Organization",
    "name": "패스트캠퍼스 기업교육"
  },
  "image": "...",
  "articleBody": "..."
}
```

### M3-4: Event 스키마

| 학습 내용 | Before | After |
|----------|--------|-------|
| 대상 페이지 | `/resource_seminar_onlinelearning` (244 chars, JS-rendered) | SSR로 변경 후 Event schema 추가 |
| 필수 정보 | 거의 없음 | name, startDate, endDate, eventAttendanceMode, location, offers |
| 예시 | 부재 | 온라인 세미나의 구체적 JSON-LD 제공 |

**실습**:
```json
// Before: 크롤 실패
// After: 온라인 세미나의 Event 스키마
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "패스트캠퍼스 온라인 기업교육 세미나",
  "startDate": "2026-03-15T14:00:00",
  "eventAttendanceMode": "OnlineEventAttendanceMode",
  ...
}
```

### M3-5: FAQPage 스키마

| 학습 내용 | Before | After |
|----------|--------|-------|
| 대상 페이지 | `/contact`, `/contact_mktg` | FAQ 섹션 추가 + Schema 구현 |
| Q&A 소스 | 크롤 데이터에 없음 | 고객 문의, 사이트 설명 기반 작성 |
| 예시 | 부재 | 실제 문의 페이지용 FAQPage JSON-LD |

**실습 파일**:
- `data/crawled/contact.json` (359 chars, 메타데이터만)
- 학생이 FAQ 콘텐츠 추가 후 FAQPage schema 작성

### M3-6: Schema Validation

| 학습 내용 | 도구 | 검증 대상 | 결과 |
|----------|------|----------|------|
| Schema.org Validator | schema.org 웹사이트 | 작성한 JSON-LD | Valid ✓ / Invalid ✗ |
| Google Rich Results | Google Search Central | 현재 b2b.fastcampus 데이터 | Rich Results 표시 여부 |

**실습**:
- 현재 `/resource_insight_aiforwork.json` (line 36~48) → Google Rich Results Test
- 결과: "Course schema 있지만, hasCourseInstance 부재로 일부 정보 미표시"

### M3-7: 종합 실습

| 페이지 | 현재 상태 | 개선 과제 | 대상 스키마 |
|--------|----------|----------|-----------|
| `/service_custom` | JS-rendered, 244 chars | SSR + 메타 추가 | Product / Service / Course |
| `/refer_customer` | JS-rendered, 244 chars | SSR + 사례 리스트 구조 | CollectionPage + Article |
| `/resource_seminar_onlinelearning` | JS-rendered, 244 chars | SSR + 이벤트 정보 | Event + Offer |
| `/` (홈) | JS-rendered, 269 chars | SSR + 조직 정보 | Organization / LocalBusiness |

---

## Stage 4: 오프사이트 & 멘션 전략

### M4-1: Off-site 개요

| 카테고리 | 크롤 데이터 | 현재 b2b 상태 | 개선 기회 |
|---------|-----------|-------------|---------|
| **Backlink** | External links 43개 (outbound만) | Inbound 미측정 | 매체 기고, 고객 사례 공유 |
| **Mention** | Facebook, Kakao, Naver, LinkedIn 채널 링크 있음 | SNS 멘션 빈도 미측정 | 사원 SNS 공유 강화 |
| **Social** | OG 태그 5/10 페이지만 완전 | SNS 미리보기 부실 | OG 태그 완성 |
| **PR** | resource_insight_hrdai: "월간인재경영 기고" 외부 링크 | 매체 보도 1건 (알려진 것만) | HR 저널, 기업교육 뉴스레터 연계 |
| **Review** | Google, Naver 리뷰 정보 없음 | Review 전략 부재 | 고객 후기 수집 및 등재 |

**실습 데이터**:
- Outbound links: `data/crawled/resource_insight_aiforwork.json` (lines 74~98)
- SNS 채널: `data/crawled/resource_insight_aiforwork.json` (lines 84~96, 사회 미디어 아이콘)

### M4-2: Backlink 전략

| 학습 내용 | 현재 상태 | 개선안 | 파일 |
|----------|----------|--------|------|
| Anchor text | 현재: "기업교육 문의하기", "1:1 무료 상담" 등 제네릭 | "시티즌 데이터 사이언티스트", "AI 시대 인재 양성" 등 구체적 | Internal link map (_report.md lines 280~316) |
| 링크 기회 | Gartner, Medium (Airbnb) 등 관련 매체에 링크만 함 | 역으로 FastCampus 콘텐츠가 인용되도록 PR | resource_insight_aiforwork.json (lines 74~81) |

### M4-3: Mention 신호

| 학습 내용 | 현재 | 개선 |
|----------|------|-----|
| SNS 채널 | Facebook, Kakao, Naver, LinkedIn 있음 | 각 채널에서 "FastCampus" 브랜드 멘션 확대 |
| 커뮤니티 | HR 포럼, 학습 커뮤니티 | 학생 사례 공유, 임직원 추천 활동 |

### M4-4: Social Amplification

| 학습 내용 | 현재 | 개선 |
|----------|------|-----|
| OG 태그 | 5/10 페이지만 완전 | 모든 페이지 OG 태그 완성 (Stage 3과 연계) |
| SNS 채널 전략 | LinkedIn 링크만 있음 | 각 채널별 콘텐츠 최적화 계획 |

**실습**:
- 현재 OG 태그: `data/crawled/resource_insight_aiforwork.json` (lines 10~17)
- 부족한 페이지: `data/crawled/service_custom.json` (OG 태그 거의 없음)

### M4-5: Digital PR

| 학습 내용 | 사례 | 데이터 |
|----------|------|--------|
| 기존 PR | "월간인재경영 23년 4월호 기고" | `resource_insight_hrdai.json` (line 72) |
| 향후 기회 | "HR 포럼", "기업교육 뉴스레터" | 학생이 식별하는 기회 |

### M4-6: Review & Directory

| 학습 내용 | 현재 | 개선 |
|----------|------|-----|
| Google My Business | 데이터 없음 | GBP 등록 + 리뷰 수집 |
| B2B 디렉토리 | 데이터 없음 | Clutch, G2, LinkedIn 등 등재 |

### M4-7: 종합 Off-site 전략

**실습 과제**:
- 현재 b2b.fastcampus의 5 Category 진단
- 3개월 로드맵 수립

---

## Stage 5: 측정 & 실험 설계

### M5-1: KPI 3-layer

| Layer | 크롤 데이터에서 가능한 측정 | 필요한 도구 |
|-------|--------------------------|-----------|
| **Visibility** | 텍스트 길이, 메타데이터 정도 | GSC, SEMrush, Ahrefs |
| **Behavior** | 콘텐츠 구조 (H1, 길이) 추론 | GA4, Hotjar |
| **Authority** | 내부 링크 수, 외부 링크 수 | Ahrefs, Majestic |

### M5-2: GSC 활용

| 측정 항목 | 대상 | 기대 효과 |
|----------|------|----------|
| Impressions | 모든 페이지 | Stage 3의 구조화 데이터 추가 후 변화 추적 |
| CTR | JS-rendered 페이지들 | SSR + Title + Meta Desc 개선 후 증가 기대 |
| Position | 주요 키워드들 | Stage 4 Backlink 전략 후 상승 기대 |

**실습**:
- 현재 b2b.fastcampus의 6개 JS-rendered 페이지 (개선 전)
- 가상 GSC 데이터: "Impressions 0" (색인 불가 또는 표시 안 됨)

### M5-3: GA4 활용

| 이벤트 | 학습 플랫폼 (Stage 1~2) | 측정 지표 |
|--------|----------------------|----------|
| Module Start | 모듈 진입 시 | Module completion rate |
| Step Completion | Step 완료 시 | Average steps per module |
| Quiz Answer | 퀴즈 제출 시 | Accuracy rate |
| Stage Unlock | Stage 2 해제 시 | Stage 2 unlock rate |

**실습**:
- 현재 GEO Mentor 시스템의 GA4 이벤트 설계
- (학습 플랫폼의 Behavior 측정)

### M5-4: AI Validator

| Template | 검증 대상 | 자동화 |
|----------|----------|--------|
| Template 1 | Title, Meta, H1 추출 | ✓ Script 가능 |
| Template 2 | JSON-LD 유효성 검사 | ✓ Schema.org API |
| Template 3 | 내부 링크 구조 | ✓ Crawl + Analysis |
| Template 4 | E-E-A-T 신호 강도 | ✓ ChatGPT Prompt |

**실습**:
- 현재 b2b.fastcampus 데이터에 10개 Prompt 적용
- 자동 리포트 생성 (예: "6개 페이지 Title 부재")

### M5-5: 실험 설계

| 가설 | 변수 | 측정 기간 | KPI |
|-----|------|----------|-----|
| 가설 1: Schema 추가 → CTR +15% | JSON-LD 추가 (10개 페이지) | 4주 | GSC CTR |
| 가설 2: 내부 링크 → 체류시간 +20% | Internal links 증가 | 4주 | GA4 Pages/Session |
| 가설 3: Meta Desc 최적화 → Impressions 유지, CTR +10% | Meta Desc 개선 (6개 페이지) | 4주 | GSC Impressions, CTR |
| 가설 4: Answer-first → Scroll +30% | Content 구조 변경 | 4주 | GA4 Scroll Depth |
| 가설 5: FAQ Schema → Featured Snippet +5 | FAQPage JSON-LD 추가 | 8주 | GSC 노출 |
| 가설 6: OG 태그 → SNS 공유 +25% | OG 태그 완성 (5개 페이지) | 4주 | SNS 공유 수 |

**실습**:
- 각 가설의 우선순위 선정
- 90일 로드맵에 배치

### M5-6: A/B Testing

| 테스트 대상 | Control | Variant A | Variant B |
|-----------|---------|-----------|-----------|
| Meta Description 길이 | 120자 | 155자 | 85자 |
| Title 구조 | "[내용] \| 패스트캠퍼스" | "패스트캠퍼스 \| [내용]" | "[내용] - 패스트캠퍼스" |

### M5-7: 90일 로드맵

| Phase | 기간 | 우선순위 | 개선 영역 | KPI 목표 |
|-------|------|----------|---------|----------|
| Phase 1 | 0~30일 | P0 | Title, Meta, Schema | Impressions 유지, CTR +10% |
| Phase 2 | 30~60일 | P1 | 내부 링크, 콘텐츠 | Sessions +20%, Pages/Session +15% |
| Phase 3 | 60~90일 | P2 | PR, Backlink, SNS | Backlinks +5, Mentions +10 |

---

# Part 4: 기술 구현 계획

## 개요

Stage 3~5 커리큘럼을 **GEO Mentor 학습 플랫폼**에 통합하기 위한 기술 사항

---

## 4.1 데이터 파이프라인: 크롤 → 분석 → Seed 데이터

### 현재 상태

```
b2b.fastcampus.co.kr
        ↓
[웹 크롤러 (Python)]
        ↓
data/crawled/ (10개 JSON)
        ↓
_summary.json, _report.md (분석 리포트)
```

### Stage 3~5 통합

```
data/crawled/ (raw crawl data)
        ↓
[Analysis Script: extract_geo_findings.py]
        ↓
data/analyzed/
├── stage3_schema_issues.json    (JSON-LD 부족한 부분 목록)
├── stage4_backlink_opportunities.json  (PR 기회)
└── stage5_baseline_metrics.json  (현재 상태 KPI)
        ↓
apps/api/seed_data/
├── stage3_modules.sql  (구조화 데이터 모듈 콘텐츠)
├── stage4_modules.sql  (오프사이트 모듈 콘텐츠)
└── stage5_modules.sql  (측정 모듈 콘텐츠)
```

### 구현 상세

**파일**: `scripts/extract_geo_findings.py` (신규 작성)

```python
# 목적: crawled JSON에서 Stage 3~5 교육 자료 자동 추출

import json
import os

def extract_schema_issues(crawl_data):
    """Stage 3용: 각 페이지의 JSON-LD 부족 지점 분석"""
    issues = {}
    for page, data in crawl_data.items():
        issues[page] = {
            'has_json_ld': data.get('json_ld', []) != [],
            'json_ld_types': [item.get('@type') for item in data.get('json_ld', [])],
            'missing_breadcrumb': 'BreadcrumbList' not in str(data.get('json_ld', [])),
            'missing_article': 'Article' not in str(data.get('json_ld', [])),
        }
    return issues

def extract_linking_structure(crawl_data):
    """Stage 4용: 내부/외부 링크 분석"""
    structure = {
        'total_internal_links': crawl_data.get('total_internal_links', 0),
        'total_external_links': crawl_data.get('total_external_links', 0),
        'hub_pages': [],  # Hub 역할하는 페이지
        'cluster_gaps': [],  # 클러스터 구조 부족
    }
    return structure

def extract_baseline_metrics(crawl_data):
    """Stage 5용: 현재 상태 베이스라인"""
    metrics = {
        'js_rendered_pages': 6,  # 크롤 분석에서 도출
        'ssr_pages': 4,
        'pages_with_title': 4,
        'pages_with_meta_desc': 4,
        'pages_with_h1': 4,
        'pages_with_og_tags': 5,
        'avg_text_length': 0,  # 계산
    }
    return metrics

# Main
if __name__ == '__main__':
    crawl_dir = 'data/crawled'
    summary = json.load(open(f'{crawl_dir}/_summary.json'))

    stage3_issues = extract_schema_issues(summary)
    stage4_links = extract_linking_structure(summary)
    stage5_baseline = extract_baseline_metrics(summary)

    # 저장
    json.dump(stage3_issues, open('data/analyzed/stage3_schema_issues.json', 'w'), indent=2, ensure_ascii=False)
    json.dump(stage4_links, open('data/analyzed/stage4_backlink_opportunities.json', 'w'), indent=2, ensure_ascii=False)
    json.dump(stage5_baseline, open('data/analyzed/stage5_baseline_metrics.json', 'w'), indent=2, ensure_ascii=False)
```

---

## 4.2 Frontend: 새로운 Step Type (M3~M5용)

### 기존 Step Type (Stage 1~2)
- `read`: 마크다운 콘텐츠 + "다음" 버튼
- `quiz`: 4지선다 + 정답 확인
- `practice`: 2~3단계 실습

### 신규 Step Type (Stage 3~5)

#### Type: "comparison"
**목적**: 크롤 데이터의 "Before"와 개선안 "After" 비교

```html
<!-- apps/web/components/ComparisonStep.html (신규) -->

<div class="step-comparison">
  <div class="before-container">
    <h3>현재 상태 (Before)</h3>
    <pre><code class="language-json">
      {
        "@type": "Course",
        "name": "...",
        "description": "..."
      }
    </code></pre>
    <p class="issues">부족한 점: hasCourseInstance, aggregateRating, duration</p>
  </div>

  <div class="after-container">
    <h3>개선안 (After)</h3>
    <pre><code class="language-json">
      {
        "@type": "Course",
        "name": "...",
        "hasCourseInstance": [...],
        "aggregateRating": {...},
        "duration": "PT60H"
      }
    </code></pre>
  </div>

  <button onclick="completeStep()">이해했어요</button>
</div>
```

#### Type: "interactive-schema"
**목적**: JSON-LD 구조를 대화형으로 학습

```html
<!-- 신규 컴포넌트 -->

<div class="step-interactive-schema">
  <h4>다음 속성을 올바른 위치에 드래그하세요</h4>

  <div class="schema-template">
    {
      "@context": "https://schema.org",
      "@type": "Course",
      <!-- 학생이 드래그로 추가할 빈 칸 -->
      <div class="drag-zone">[ 속성 드롭 ]</div>
    }
  </div>

  <div class="attribute-list">
    <span class="draggable">name</span>
    <span class="draggable">hasCourseInstance</span>
    <span class="draggable">aggregateRating</span>
  </div>
</div>
```

#### Type: "data-analysis"
**목적**: 크롤링 데이터를 분석하는 실습

```html
<!-- 신규 컴포넌트 -->

<div class="step-data-analysis">
  <h4>다음 b2b.fastcampus 페이지 분석</h4>

  <div class="data-display">
    <h5>/resource_insight_aiforwork</h5>
    <table>
      <tr><td>Title</td><td>✓ O</td></tr>
      <tr><td>Meta Description</td><td>✓ O</td></tr>
      <tr><td>H1</td><td>✓ O</td></tr>
      <tr><td>JSON-LD</td><td>부분 (Course만)</td></tr>
      <tr><td>BreadcrumbList</td><td>✗ X</td></tr>
    </table>
  </div>

  <div class="analysis-question">
    <label>이 페이지의 가장 큰 문제는?</label>
    <input type="radio" name="q1" value="1"> JSON-LD 부재
    <input type="radio" name="q1" value="2"> BreadcrumbList 부재
    <input type="radio" name="q1" value="3"> Internal links 부족
  </div>
</div>
```

---

## 4.3 Backend: 새로운 API

### 기존 API (Stage 1~2)
- `GET /api/health`
- `GET /api/stages`
- `GET /api/modules/{id}`
- `POST /api/steps/{id}/answer`
- `GET /api/progress`

### 신규 API (Stage 3~5)

#### 1. `GET /api/crawl-data/{page_slug}`
**목적**: 특정 b2b 페이지의 크롤 데이터 반환 (Stage 3~5 실습용)

```json
GET /api/crawl-data/resource_insight_aiforwork

Response:
{
  "url": "https://b2b.fastcampus.co.kr/resource_insight_aiforwork",
  "title": "시티즌 데이터 사이언티스트...",
  "meta_description": "...",
  "headings": [{"level": 1, "text": "..."}],
  "json_ld": [{"@type": "Course", ...}],
  "text_length": 4797,
  "internal_links": 5,
  "external_links": 6,
  "images": 11
}
```

#### 2. `GET /api/geo-analysis/{metric}`
**목적**: Stage 5 측정용 현재 상태 데이터

```json
GET /api/geo-analysis/schema-coverage

Response:
{
  "metric": "schema-coverage",
  "pages_with_schema": 4,
  "pages_without_schema": 6,
  "schema_types": ["Course"],
  "missing_types": ["BreadcrumbList", "Article", "Event", "FAQPage"]
}
```

#### 3. `POST /api/steps/{id}/schema-validation`
**목적**: 학생이 작성한 JSON-LD를 검증

```json
POST /api/steps/1234/schema-validation

Request:
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Course",
    "name": "GEO 완벽 가이드"
  }
}

Response:
{
  "is_valid": true,
  "errors": [],
  "warnings": ["hasCourseInstance 없음"],
  "feedback": "JSON-LD 구조는 올바릅니다. 하지만..."
}
```

---

## 4.4 Database: 새로운 스키마

### 신규 테이블

#### `crawled_pages`
```sql
CREATE TABLE crawled_pages (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE,  -- resource_insight_aiforwork
    url TEXT,
    crawled_at TIMESTAMP,
    title TEXT,
    meta_description TEXT,
    h1_count INTEGER,
    json_ld_count INTEGER,
    schema_types TEXT,  -- JSON: ["Course"]
    internal_links INTEGER,
    external_links INTEGER,
    text_length INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `step_analysis_data`
```sql
CREATE TABLE step_analysis_data (
    id INTEGER PRIMARY KEY,
    step_id INTEGER,  -- FK to steps
    analysis_type TEXT,  -- "schema", "linking", "metric"
    crawled_page_slug TEXT,  -- FK to crawled_pages
    before_state TEXT,  -- JSON
    expected_after TEXT,  -- JSON (교육 목표)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `user_schema_submissions`
```sql
CREATE TABLE user_schema_submissions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    step_id INTEGER,
    schema_json TEXT,
    is_valid BOOLEAN,
    validation_errors TEXT,
    submitted_at TIMESTAMP
);
```

---

## 4.5 Seed 데이터 작성

### Stage 3 Seed 데이터 구조

**파일**: `apps/api/seed_data/stage3.sql`

```sql
-- M3-1: JSON-LD 기초
INSERT INTO modules (id, stage_id, title, description, order)
VALUES (301, 3, 'JSON-LD 기초 & 구조', 'JSON-LD의 정의, 목적, 문법 이해', 1);

INSERT INTO steps (id, module_id, type, content, order)
VALUES
  (3010, 301, 'read', '[마크다운] JSON-LD란?...', 1),
  (3011, 301, 'read', '[마크다운] @context, @type의 역할...', 2),
  (3012, 301, 'quiz', 'JSON-LD의 올바른 구조는?', 3),
  (3013, 301, 'practice', '다단계: 스키마 선택 → 속성 선택 → 결과 확인', 4),
  (3014, 301, 'read', '실제 사례: b2b.fastcampus의 현재 JSON-LD 분석', 5);

INSERT INTO options (id, step_id, text, is_correct, feedback)
VALUES
  (30120, 3012, '{"@context": "...", "@type": "...", "name": "..."}', 1, '정답입니다. JSON-LD는...'),
  (30121, 3012, '{"context": "...", "type": "..."}', 0, '틀렸습니다. @ 부호가 필수입니다'),
  (30122, 3012, '[{"@context": "..."}]', 0, '배열 형식은 안 됩니다'),
  (30123, 3012, '<json-ld>...</json-ld>', 0, 'HTML 태그가 아닙니다');

INSERT INTO step_analysis_data (step_id, analysis_type, crawled_page_slug, before_state, expected_after)
VALUES
  (3014, 'schema', 'resource_insight_aiforwork',
   '{"has_json_ld": true, "types": ["Course"], "missing": ["BreadcrumbList", "Article"]}',
   '{"has_json_ld": true, "types": ["Course", "Article", "BreadcrumbList"], "complete": true}');
```

---

## 4.6 Frontend 화면 (Stage 3~5)

### M3-1 Step 4: 실습 화면 (패턴 C - 3단계)

```html
<!-- apps/web/stage3/m3-1-step4.html -->

<div class="module-learning">
  <div class="progress-bar">
    <span>M3-1: JSON-LD 기초</span>
    <span>Step 4/5</span>
  </div>

  <div class="practice-container">
    <h3>과제: FastCampus B2B를 위한 Organization 스키마 작성</h3>

    <!-- Phase 1: 스키마 타입 선택 -->
    <div id="phase1" class="practice-phase">
      <p>홈페이지에 필요한 최상위 스키마 타입은?</p>
      <div class="options">
        <button class="option" data-value="Organization" onclick="selectPhase1('Organization')">
          Organization (조직)
        </button>
        <button class="option" data-value="LocalBusiness" onclick="selectPhase1('LocalBusiness')">
          LocalBusiness (지역 사업)
        </button>
        <button class="option" data-value="NewsMediaOrganization" onclick="selectPhase1('NewsMediaOrganization')">
          NewsMediaOrganization (뉴스 매체)
        </button>
      </div>
    </div>

    <!-- Phase 2: 필수 속성 선택 (Phase 1 선택 후 표시) -->
    <div id="phase2" class="practice-phase" style="display:none;">
      <p>다음 중 Organization 스키마에 필수로 들어가야 하는 속성은?</p>
      <div class="options multi-select">
        <label><input type="checkbox" data-attr="name"> name (조직명)</label>
        <label><input type="checkbox" data-attr="url"> url (웹사이트)</label>
        <label><input type="checkbox" data-attr="logo"> logo (로고)</label>
        <label><input type="checkbox" data-attr="description"> description (설명)</label>
      </div>
      <button onclick="submitPhase2()">다음</button>
    </div>

    <!-- Phase 3: 결과 표시 -->
    <div id="phase3" class="practice-result" style="display:none;">
      <h4>당신의 답:</h4>
      <pre><code id="student-schema"></code></pre>

      <h4>전문가 분석:</h4>
      <pre><code>
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "패스트캠퍼스 기업교육",
  "url": "https://b2b.fastcampus.co.kr",
  "logo": "https://...",
  "description": "기업교육 전문 기관",
  "sameAs": [
    "https://www.facebook.com/b2bfastcampus",
    "https://www.linkedin.com/showcase/b2bfastcampus"
  ]
}
      </code></pre>

      <p class="feedback">완벽합니다! 모든 필수 속성을 포함했습니다.</p>
      <button onclick="nextStep()">다음으로</button>
    </div>
  </div>
</div>

<script>
function selectPhase1(schemaType) {
  document.getElementById('phase1').style.display = 'none';
  document.getElementById('phase2').style.display = 'block';
  window.selectedSchema = schemaType;
}

function submitPhase2() {
  const selected = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
    .map(el => el.dataset.attr);

  // 당신의 스키마 생성
  const studentSchema = {
    "@context": "https://schema.org",
    "@type": window.selectedSchema
  };
  selected.forEach(attr => {
    studentSchema[attr] = "...";
  });

  document.getElementById('student-schema').textContent = JSON.stringify(studentSchema, null, 2);
  document.getElementById('phase2').style.display = 'none';
  document.getElementById('phase3').style.display = 'block';
}

function nextStep() {
  // API: POST /api/steps/3013/answer
  fetch('/api/steps/3013/answer', {
    method: 'POST',
    body: JSON.stringify({ option_id: selectedOptionId })
  }).then(res => res.json()).then(data => {
    window.location.href = `/learn/module/301/step/3014`;
  });
}
</script>
```

---

## 4.7 구현 우선순위

| 항목 | Slice | 난이도 | 예상 기간 |
|------|-------|--------|----------|
| Step Type: "comparison" | Slice A | 낮음 | 2일 |
| API: GET /api/crawl-data | Slice A | 낮음 | 2일 |
| Stage 3 Seed 데이터 (M3-1~M3-7) | Slice B | 중간 | 1주 |
| Frontend: M3 모듈 화면 | Slice B | 중간 | 1주 |
| Step Type: "interactive-schema" | Slice C | 높음 | 3일 |
| API: POST /api/steps/{id}/schema-validation | Slice C | 중간 | 3일 |
| Stage 4 Seed 데이터 + 화면 | Slice D | 중간 | 1주 |
| Stage 5 Seed 데이터 + 화면 | Slice E | 높음 | 1.5주 |

---

# Part 5: 우선순위 & 로드맵

## 5.1 Stage 3~5 의존성

```
Stage 2 (기초 실습) [완료]
        ↓
Stage 3 (구조화 데이터) [P0]
        ↓
Stage 4 (오프사이트) [P1]
        ↓
Stage 5 (측정 & 실험) [P1~P2]
```

**해제 조건**:
- Stage 2 완료 → Stage 3 자동 해제
- Stage 3 완료 (M3-8 70% 이상) → Stage 4 해제
- Stage 4 완료 → Stage 5 해제

---

## 5.2 주별 로드맵 (12주)

### Week 1~2: 분석 & 설계 (Slice A)
| 항목 | 담당 | 상태 |
|------|------|------|
| Step Type "comparison" 구현 | frontend-dev | 2일 |
| API /api/crawl-data 구현 | backend-dev | 2일 |
| Stage 3 모듈 아웃라인 작성 | content-curator | 3일 |
| M3-1, M3-2 콘텐츠 상세 작성 | content-curator | 3일 |

### Week 3~4: Stage 3 핵심 구현 (Slice B)
| 항목 | 담당 | 상태 |
|------|------|------|
| Stage 3 Seed 데이터 작성 (M3-1~M3-4) | content-curator | 1주 |
| M3-1, M3-2 화면 구현 | frontend-dev | 4일 |
| API 통합 테스트 | backend-dev | 2일 |
| M3 초기 베타 (3~5명) | qa | 2일 |

### Week 5~6: Stage 3 완성 (Slice B)
| 항목 | 담당 | 상태 |
|------|------|------|
| M3-3~M3-7 콘텐츠 완성 | content-curator | 1주 |
| Interactive Schema UI | frontend-dev | 3일 |
| Schema Validation API | backend-dev | 2일 |
| Stage 3 전체 테스트 | qa | 2일 |

### Week 7: Stage 4 시작 (Slice C~D)
| 항목 | 담당 | 상태 |
|------|------|------|
| Step Type "data-analysis" | frontend-dev | 2일 |
| Stage 4 콘텐츠 상세 작성 (M4-1~M4-3) | content-curator | 3일 |
| M4 Seed 데이터 준비 | content-curator | 2일 |

### Week 8~9: Stage 4 구현 (Slice D)
| 항목 | 담당 | 상태 |
|------|------|------|
| M4-1~M4-4 화면 구현 | frontend-dev | 1주 |
| Stage 4 Seed 데이터 INSERT | content-curator | 3일 |
| Off-site 데이터 API | backend-dev | 3일 |

### Week 10: Stage 4 완성 & Stage 5 시작 (Slice D~E)
| 항목 | 담당 | 상태 |
|-----|------|------|
| M4-5~M4-7 완성 | content-curator | 3일 |
| Stage 5 콘텐츠 상세 작성 | content-curator | 2일 |

### Week 11~12: Stage 5 & 통합 테스트 (Slice E)
| 항목 | 담당 | 상태 |
|------|------|------|
| M5 화면 구현 (KPI, GSC, GA4, AI Validator) | frontend-dev | 1주 |
| Stage 5 Seed 데이터 | content-curator | 4일 |
| 전체 E2E 테스트 (Stage 1~5) | qa | 3일 |
| 배포 & 모니터링 | devops | 2일 |

---

## 5.3 우선순위 및 리스크

### P0 (필수)
- Stage 3 Seed 데이터 작성 (M3-1~M3-7)
- Stage 3 화면 구현 (읽기 + 퀴즈 + 실습)
- Step Type "comparison" 추가

**리스크**: 콘텐츠 큐레이션 지연 → 완화: 주간 진도 체크

### P1 (권장)
- Stage 4 콘텐츠 & 화면
- Schema Validation API
- GA4 통합

**리스크**: 외부 데이터(Backlink, Mention) 미확보 → 완화: 가상 데이터로 시뮬레이션

### P2 (선택)
- Stage 5 고급 실험 설계
- AI Validator 10개 Prompt 전체 구현

---

## 5.4 성공 기준 (Stage 3~5)

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **Stage 3 완료율** | 60% 이상 | DB user_progress (M3-8) |
| **Stage 4 진입율** | Stage 3 완료자 80% | unlock_condition 적용 |
| **Stage 5 시작율** | Stage 4 완료자 70% | unlock_condition 적용 |
| **콘텐츠 품질** | 피드백 텍스트 일관성 (40~100자) | 수동 검수 |
| **실습 만족도** | 학습자 설문 4/5 이상 | Post-course survey |

---

## 5.5 배포 및 모니터링

### 배포 단계

1. **Closed Beta** (주 11): 5~10명 내부 테스터
   - Stage 3만 시작
   - UX 피드백 수집

2. **Open Beta** (주 12): 전사 공개
   - Stage 1~3 전체 활성화
   - Stage 4는 테스트 모드

3. **Production** (이후): 정식 서비스
   - Stage 1~5 모두 활성화
   - 지속적 콘텐츠 업데이트

### 모니터링

**Weekly Dashboard**:
```
- 모듈별 시작 수 / 완료 수 / 통과율
- 단계별 이탈율 (어디서 나가는가?)
- 평균 소요 시간 (Step별, Module별)
- 질문 & 피드백 (커뮤니티 채널)
```

**Monthly Report**:
```
- Stage별 학습 효과 분석
- 콘텐츠 개선 사항
- 다음 월 로드맵 조정
```

---

## 5.6 향후 확장 (Post-MVP)

### Stage 6~8 가능성
- **Stage 6**: "고급 기법 (RankBrain, Core Web Vitals)"
- **Stage 7**: "국제 GEO & 멀티랭귀지"
- **Stage 8**: "케이스 스터디 & 실제 프로젝트 실행"

### 통합 기능
- **Community**: 학습자들 간 질문 & 공유
- **Certification**: Stage 5 완료 시 "GEO Mentor Certified" 배지
- **Mentoring Sessions**: 실시간 Q&A (전문가와)
- **Progress Export**: 학습 기록 PDF 다운로드

---

# 요약

| 항목 | Stage 3 | Stage 4 | Stage 5 |
|------|---------|---------|---------|
| **학습 목표** | JSON-LD, BreadcrumbList, Article, Event, FAQPage, Course 스키마 마스터 | Backlink, Mention, Social, PR, Review 전략 | KPI 3-layer, GSC, GA4, AI Validator, 실험 설계 |
| **모듈 수** | 7 (M3-1~M3-7) | 7 (M4-1~M4-7) | 7 (M5-1~M5-7) |
| **실습 데이터 출처** | b2b.fastcampus 크롤 JSON (6개 페이지의 부족한 schema) | 내부 링크 분석, SNS 채널, 매체 보도 사례 | 현재 상태 메트릭, 가상 GSC/GA4 데이터 |
| **핵심 Step Type** | comparison, quiz, practice | data-analysis, practice | data-analysis, quiz, practice |
| **예상 기간** | 4주 | 3주 | 3주 |
| **우선순위** | P0 | P1 | P1~P2 |

---

**이 문서는 GEO Mentor 시스템의 Stage 3~5 개발을 위한 완전한 기획안입니다.**
**각 Stage는 실제 b2b.fastcampus.co.kr의 크롤링 데이터를 교육 자료로 활용하여, 이론과 실습의 거리를 최소화합니다.**
