# 78 — Seed Glossary Jargon Inventory

## Summary

- Scope: `apps/api/seed.py` 내 `<div class="callout glossary">...</div>` 블록만 조사
- Source file: `apps/api/seed.py`
- Glossary blocks: **39**
- Total jargon occurrences: **118**
- Unique jargon terms: **100**
- Duplicated terms (same term, multiple blocks): **4** (`Domain Rating`, `Entity`, `Semantic HTML`, `KPI`)
- Dedup policy: 대표 정의 1개 + 전체 등장 위치 기록

## Method

1. `seed.py` glossary 블록에서 용어(`<strong>...</strong>`)와 출처 라인 추출
2. 시드를 임시 DB에 로드한 뒤, 렌더된 `content_md`에서 용어 뜻(한국어 설명) 추출
3. 동일 용어를 통합하고 최초 정의를 대표 정의로 지정
4. 모든 등장 라인과 블록 번호를 병기

## Jargon Dictionary

| Term | Korean Meaning | Alias / Variant | First Seen | All Occurrences | Glossary Block # | Notes |
|---|---|---|---|---|---|---|
| @context / @type | @context는 Schema.org 어휘 사용을 선언, @type은 데이터 유형을 지정 | @context / @type | `apps/api/seed.py:1771` | `apps/api/seed.py:1771` | 16 | - |
| A/B Test | 두 가지 버전(A: 기존, B: 변경)을 비교하여 어떤 것이 더 효과적인지 검증하는 실험 | A/B Test | `apps/api/seed.py:3741` | `apps/api/seed.py:3741` | 31 | - |
| AI Validator | AI에게 주기적으로 질문하여 우리 콘텐츠가 인용되는지 확인하는 프로세스 | - | `apps/api/seed.py:3622` | `apps/api/seed.py:3622` | 30 | - |
| Anchor Text | 링크가 걸려 있는 클릭 가능한 텍스트 — "자세히 보기"보다 "GEO 전략 가이드"가 좋음 | - | `apps/api/seed.py:1390` | `apps/api/seed.py:1390` | 13 | - |
| Answer-first | 긴 설명 대신 핵심 답변을 문서 맨 앞에 배치하는 콘텐츠 작성법 | - | `apps/api/seed.py:1049` | `apps/api/seed.py:1049` | 10 | - |
| Article / BlogPosting | 뉴스 기사나 블로그 글의 정보를 AI에게 전달하는 스키마 타입 | Article / BlogPosting | `apps/api/seed.py:1896` | `apps/api/seed.py:1896` | 17 | - |
| Attribution | 고객이 전환하기까지 거친 여러 터치포인트 중 각각의 기여도를 측정하는 방법 | - | `apps/api/seed.py:3868` | `apps/api/seed.py:3868` | 32 | - |
| author | 글을 쓴 사람이나 조직 — E-E-A-T 전문성 신호의 핵심 | - | `apps/api/seed.py:1900` | `apps/api/seed.py:1900` | 17 | - |
| Authority | 제3자가 우리 브랜드를 인정하고 인용하는 정도 — E-E-A-T의 A | - | `apps/api/seed.py:2728` | `apps/api/seed.py:2728` | 23 | - |
| Backlink | 다른 사이트가 우리 사이트를 링크로 추천하는 것 | - | `apps/api/seed.py:471` | `apps/api/seed.py:471` | 4 | - |
| Batch | 스포크 페이지를 20개씩 묶어 순차 발행하는 방식 | 배치 발행 | `apps/api/seed.py:3892` | `apps/api/seed.py:3892` | 38 | 新 —Stage 6 M6-6 |
| Breadcrumb | "홈 > 카테고리 > 현재 페이지" 형태로 사용자 위치를 보여주는 네비게이션 | - | `apps/api/seed.py:951` | `apps/api/seed.py:951` | 9 | - |
| BreadcrumbList | "홈 > 카테고리 > 페이지" 경로를 AI에게 알려주는 구조화 데이터 타입 | - | `apps/api/seed.py:1769` | `apps/api/seed.py:1769` | 16 | - |
| Business Profile | Google/네이버에 등록하는 공식 사업체 정보 (주소, 연락처, 영업시간 등) | - | `apps/api/seed.py:2848` | `apps/api/seed.py:2848` | 24 | - |
| Canonical URL | "이 페이지가 원본입니다"라고 검색엔진에 알려주는 태그 | - | `apps/api/seed.py:613` | `apps/api/seed.py:613` | 6 | - |
| Citation | AI가 답변에서 "출처: 우리 사이트"라고 표시하는 것 | - | `apps/api/seed.py:233` | `apps/api/seed.py:233` | 1 | - |
| Citation Rate | AI가 답변할 때 우리 콘텐츠를 출처로 인용하는 비율 | - | `apps/api/seed.py:3251` | `apps/api/seed.py:3251` | 27 | - |
| Control Group | 변경 없이 기존 상태를 유지하는 그룹 — 실험군의 효과를 비교하는 기준 | - | `apps/api/seed.py:3745` | `apps/api/seed.py:3745` | 31 | - |
| Conversion | 방문자가 실제 고객 행동(문의, 가입, 구매)을 하는 것 | - | `apps/api/seed.py:551` | `apps/api/seed.py:551` | 5 | - |
| Crawl | 검색엔진 봇이 웹페이지를 방문해서 내용을 수집하는 과정 | - | `apps/api/seed.py:3371` | `apps/api/seed.py:3371` | 28 | - |
| Crawl Budget | 검색엔진이 한 번에 우리 사이트를 방문할 수 있는 페이지 수 한도 | - | `apps/api/seed.py:1392` | `apps/api/seed.py:1392` | 13 | - |
| CTA | 방문자에게 다음 행동(문의, 다운로드, 가입)을 유도하는 버튼이나 링크 | Call to Action | `apps/api/seed.py:3778` | `apps/api/seed.py:3778` | 35 | 新 —Stage 6 M6-3 |
| CTR | 노출된 횟수 중 실제 클릭한 비율 | - | `apps/api/seed.py:553` | `apps/api/seed.py:553` | 5 | - |
| datePublished / dateModified | 글의 발행일과 수정일 — AI가 콘텐츠의 최신성을 판단하는 근거 | datePublished / dateModified | `apps/api/seed.py:1898` | `apps/api/seed.py:1898` | 17 | - |
| Digital PR | 온라인 매체에 기고, 보도자료, 인터뷰 등을 통해 브랜드를 노출하는 활동 | - | `apps/api/seed.py:2724` | `apps/api/seed.py:2724` | 23 | - |
| DoD | 과업 완료를 판정하는 최소 기준 목록 | Definition of Done | `apps/api/seed.py:3756` | `apps/api/seed.py:3756` | 34 | 新 —Stage 6 M6-2 |
| Domain Rating | 사이트 전체의 신뢰도와 권위를 점수(0~100)로 나타낸 SEO 지표 | - | `apps/api/seed.py:1481` | `apps/api/seed.py:1481`, `apps/api/seed.py:2625` | 14, 22 | 추가 표현 존재 |
| E-E-A-T | 경험·전문성·권위·신뢰 — AI가 콘텐츠를 믿을지 판단하는 4가지 기준 | - | `apps/api/seed.py:400` | `apps/api/seed.py:400` | 3 | - |
| Editorial Link | 전문 매체가 자발적으로 우리 콘텐츠를 인용하며 거는 링크 — 가장 가치 높음 | - | `apps/api/seed.py:2623` | `apps/api/seed.py:2623` | 22 | - |
| Embedding | 텍스트를 AI가 비교할 수 있는 숫자 벡터로 변환하는 기술 | - | `apps/api/seed.py:402` | `apps/api/seed.py:402` | 3 | - |
| Entity | 검색엔진과 AI가 인식하는 고유한 개체 — 사람, 기업, 장소, 제품 등 | - | `apps/api/seed.py:473` | `apps/api/seed.py:473`, `apps/api/seed.py:2846` | 4, 24 | 추가 표현 존재 |
| Event | 세미나, 웨비나, 교육 등 이벤트 정보를 AI에게 전달하는 구조화 데이터 타입 | - | `apps/api/seed.py:2033` | `apps/api/seed.py:2033` | 18 | - |
| FAQ | 고객이 자주 묻는 질문과 답변을 정리한 콘텐츠 | - | `apps/api/seed.py:1169` | `apps/api/seed.py:1169` | 11 | - |
| FAQPage | 자주 묻는 질문 페이지를 AI에게 알려주는 구조화 데이터 타입 | - | `apps/api/seed.py:2170` | `apps/api/seed.py:2170` | 19 | - |
| Fan-out | AI 검색 엔진이 하나의 질문을 여러 하위 질문으로 분해하는 메커니즘 | Query fan-out | `apps/api/seed.py:3888` | `apps/api/seed.py:3888` | 38 | 新 —Stage 6 M6-6 |
| Featured Snippet | 구글 검색 결과 최상단에 박스로 강조 표시되는 요약 답변 | - | `apps/api/seed.py:1051` | `apps/api/seed.py:1051` | 10 | - |
| Funnel | 인식 → 관심 → 검토 → 전환 순으로 고객 여정을 단계별로 나눈 마케팅 프레임워크 | - | `apps/api/seed.py:3866` | `apps/api/seed.py:3866` | 32 | - |
| GA4 | Google이 제공하는 무료 웹 분석 도구 — 방문자 행동, 유입 경로, 전환을 추적 | - | `apps/api/seed.py:3494` | `apps/api/seed.py:3494` | 29 | - |
| GEO | AI 챗봇이 답변할 때 내 콘텐츠를 인용하도록 최적화하는 전략 | - | `apps/api/seed.py:231` | `apps/api/seed.py:231` | 1 | - |
| GPTBot | OpenAI의 모델 학습용 크롤러 | - | `apps/api/seed.py:3750` | `apps/api/seed.py:3750` | 34 | 新 —Stage 6 M6-2 |
| GSC | Google이 무료로 제공하는 웹사이트 검색 성과 분석 도구 | - | `apps/api/seed.py:3367` | `apps/api/seed.py:3367` | 28 | - |
| H1 / H2 / H3 | HTML에서 제목의 중요도를 나타내는 태그 — H1이 가장 큰 대제목 | H1 / H2 / H3 | `apps/api/seed.py:1271` | `apps/api/seed.py:1271` | 12 | - |
| Hero section | 웹페이지 최상단의 대형 배너 영역 | - | `apps/api/seed.py:3780` | `apps/api/seed.py:3780` | 35 | 新 —Stage 6 M6-3 |
| Hub-Cluster | 핵심 주제 페이지(허브)에서 세부 페이지(클러스터)로 체계적으로 연결하는 구조 | - | `apps/api/seed.py:866` | `apps/api/seed.py:866` | 8 | - |
| Hub-Spoke | 중심 허브 페이지에서 스포크 페이지들로 뻗어나가는 사이트 구조 | - | `apps/api/seed.py:3890` | `apps/api/seed.py:3890` | 38 | 복습 —Stage 6 M6-6 |
| Hypothesis | "~하면 ~가 될 것이다"라는 검증 가능한 예측 — 실험의 출발점 | - | `apps/api/seed.py:3743` | `apps/api/seed.py:3743` | 31 | - |
| IA | 웹사이트의 페이지를 체계적으로 분류하고 연결하는 설계 | - | `apps/api/seed.py:864` | `apps/api/seed.py:864` | 8 | - |
| Implied Links | 링크가 없어도 브랜드명 언급만으로 신뢰 신호가 되는 것 — Google 특허 기술 | - | `apps/api/seed.py:2726` | `apps/api/seed.py:2726` | 23 | - |
| Impression | 검색 결과에 우리 페이지가 표시된 횟수 (클릭 여부 무관) | - | `apps/api/seed.py:1479` | `apps/api/seed.py:1479` | 14 | - |
| Index / Noindex | 검색엔진에 페이지를 등록(index)하거나 제외(noindex)하는 설정 | Index / Noindex | `apps/api/seed.py:953` | `apps/api/seed.py:953` | 9 | - |
| Internal Link | 같은 웹사이트 안에서 페이지끼리 연결하는 하이퍼링크 | - | `apps/api/seed.py:1388` | `apps/api/seed.py:1388` | 13 | - |
| Inverted Pyramid | 가장 중요한 정보를 먼저 쓰고 세부 사항을 나중에 쓰는 저널리즘 작성 방식 | - | `apps/api/seed.py:1053` | `apps/api/seed.py:1053` | 10 | - |
| JSON-LD | 검색엔진과 AI가 이해하는 '콘텐츠 이력서' 코드 — Google 공식 권장 포맷 | - | `apps/api/seed.py:1644` | `apps/api/seed.py:1644` | 15 | - |
| Knowledge Graph | Google이 관리하는 거대한 지식 데이터베이스 — 사람, 기업, 장소의 관계를 연결 | - | `apps/api/seed.py:2844` | `apps/api/seed.py:2844` | 24 | - |
| KPI | 목표 달성 여부를 숫자로 측정하는 핵심 성과 지표 | - | `apps/api/seed.py:547` | `apps/api/seed.py:547` | 5 | - |
| KPI-A / KPI-B / KPI-C | Stage 6 전용 3층 측정 체계 — A(ChatGPT 인용), B(Google AI 노출), C(하위 질의 커버리지) | - | `apps/api/seed.py:3838` | `apps/api/seed.py:3838` | 37 | 新 —Stage 6 M6-5 |
| Layer 1 / 2 / 3 | Layer 1(가시성) → Layer 2(행동) → Layer 3(권위) 순으로 성과를 계단식 측정 | Layer 1 / 2 / 3 | `apps/api/seed.py:3249` | `apps/api/seed.py:3249` | 27 | - |
| Link Building | 다른 사이트에서 우리 사이트로의 링크(백링크)를 확보하는 활동 | - | `apps/api/seed.py:2621` | `apps/api/seed.py:2621` | 22 | - |
| ListItem / position | 경로의 각 단계(ListItem)와 그 순서(position)를 나타내는 요소 | ListItem / position | `apps/api/seed.py:1773` | `apps/api/seed.py:1773` | 16 | - |
| LLM | ChatGPT, Claude, Gemini 같은 AI 엔진의 총칭 | - | `apps/api/seed.py:235` | `apps/api/seed.py:235` | 1 | - |
| mainEntity | FAQPage 안에 질문(Question) 목록을 담는 핵심 속성 | - | `apps/api/seed.py:2172` | `apps/api/seed.py:2172` | 19 | - |
| MECE | 겹치지 않으면서 빠짐없이 — 전략을 분류할 때 빈틈 없이 나누는 원칙 | - | `apps/api/seed.py:2501` | `apps/api/seed.py:2501` | 21 | - |
| Mention | 외부 사이트에서 우리 브랜드명이 언급되는 것 (링크 없이 이름만 나와도 해당) | - | `apps/api/seed.py:2503` | `apps/api/seed.py:2503` | 21 | - |
| Meta Description | 검색 결과에서 제목 아래 표시되는 페이지 요약 설명문 | - | `apps/api/seed.py:615` | `apps/api/seed.py:615` | 6 | - |
| Microdata / RDFa | JSON-LD 외에 구조화 데이터를 표현하는 다른 방식 (현재는 JSON-LD가 주류) | Microdata / RDFa | `apps/api/seed.py:1648` | `apps/api/seed.py:1648` | 15 | - |
| NAP | 회사명·주소·전화번호 — 모든 플랫폼에서 동일하게 유지해야 AI가 같은 기업으로 인식 | - | `apps/api/seed.py:3058` | `apps/api/seed.py:3058` | 26 | - |
| OAI-SearchBot | OpenAI의 ChatGPT Search 전용 크롤러 | - | `apps/api/seed.py:3748` | `apps/api/seed.py:3748` | 34 | 新 —Stage 6 M6-2 |
| Off-site | 우리 웹사이트 바깥에서 벌어지는 활동 — 외부 매체, SNS, 리뷰 등 | - | `apps/api/seed.py:2499` | `apps/api/seed.py:2499` | 21 | - |
| offers | 이벤트의 가격, 통화, 구매 URL 등을 담는 속성 | - | `apps/api/seed.py:2037` | `apps/api/seed.py:2037` | 18 | - |
| Open Graph | 카카오톡·슬랙 등에 링크 공유 시 미리보기에 표시되는 정보를 지정하는 태그 | - | `apps/api/seed.py:696` | `apps/api/seed.py:696` | 7 | - |
| Organization | 기업/단체의 공식 정보를 AI에게 전달하는 구조화 데이터 타입 | Schema.org Organization | `apps/api/seed.py:3900` | `apps/api/seed.py:3900` | 39 | 新 —Stage 6 M6-7 |
| Organic Traffic | 광고 없이 검색이나 AI를 통해 자연스럽게 유입되는 방문자 | - | `apps/api/seed.py:321` | `apps/api/seed.py:321` | 2 | - |
| P0 / P1 / P2 | 우선순위 레벨 — P0(즉시 처리), P1(긴급), P2(일반) | Phase / P0 / P1 / P2 | `apps/api/seed.py:3726` | `apps/api/seed.py:3726` | 33 | 新 —Stage 6 M6-1 |
| Perplexity | 출처를 명시하며 답변하는 AI 검색 엔진 — 인용 확인에 가장 유용 | - | `apps/api/seed.py:3626` | `apps/api/seed.py:3626` | 30 | - |
| Phase | 프로젝트 단계 — Phase 1(발명), Phase 2(검증), Phase 3(확장) | Phase / P0 / P1 / P2 | `apps/api/seed.py:3726` | `apps/api/seed.py:3726` | 33 | 新 —Stage 6 M6-1 |
| Proof-first | Answer-first 직하단에 통계·인용·외부 출처 블록을 배치하여 신뢰도를 높이는 전략 | - | `apps/api/seed.py:3782` | `apps/api/seed.py:3782` | 36 | 新 —Stage 6 M6-4 |
| Prompt | AI에게 입력하는 질문이나 명령문 | - | `apps/api/seed.py:3624` | `apps/api/seed.py:3624` | 30 | - |
| Query | 사용자가 검색창에 입력하는 단어나 문장 | - | `apps/api/seed.py:3369` | `apps/api/seed.py:3369` | 28 | - |
| Question / Answer | 각 질문과 답변을 한 쌍으로 묶는 스키마 요소 | Question / Answer | `apps/api/seed.py:2174` | `apps/api/seed.py:2174` | 19 | - |
| RACI | 책임(R), 승인(A), 자문(C), 통보(I) — 과업별 역할 배분 프레임워크 | - | `apps/api/seed.py:3720` | `apps/api/seed.py:3720` | 33 | 新 —Stage 6 M6-1 |
| RAG | AI가 실시간으로 웹을 검색한 뒤 그 결과를 바탕으로 답변을 생성하는 방식 | - | `apps/api/seed.py:398` | `apps/api/seed.py:398` | 3 | - |
| Referrer | 방문자가 어디서 왔는지 — linkedin.com, chatgpt.com 등 출발지 정보 | - | `apps/api/seed.py:2953` | `apps/api/seed.py:2953` | 25 | - |
| Review Signal | 제3자 플랫폼의 고객 리뷰와 평점 — AI가 브랜드 평판을 판단하는 근거 | - | `apps/api/seed.py:3060` | `apps/api/seed.py:3060` | 26 | - |
| Rich Result | 별점, FAQ 펼침, 가격 등이 함께 표시되는 화려한 검색 결과 | - | `apps/api/seed.py:1171` | `apps/api/seed.py:1171` | 11 | - |
| Rich Results Test | Google이 제공하는 무료 도구 — 구조화 데이터가 검색 결과에 잘 표시되는지 확인 | - | `apps/api/seed.py:2305` | `apps/api/seed.py:2305` | 20 | - |
| robots.txt | 검색엔진 봇이 방문할 수 있는 페이지와 없는 페이지를 지정하는 파일 | - | `apps/api/seed.py:3754` | `apps/api/seed.py:3754` | 34 | 복습 —Stage 6 M6-2 |
| Schema Markup Validator | Schema.org 표준에 맞게 코드를 작성했는지 검사하는 도구 | - | `apps/api/seed.py:2307` | `apps/api/seed.py:2307` | 20 | - |
| Schema.org | 전 세계가 합의한 구조화 데이터 표준 단어장 | - | `apps/api/seed.py:1646` | `apps/api/seed.py:1646` | 15 | - |
| Semantic HTML | 의미를 가진 HTML 태그(header, article, nav 등)로 문서 구조를 명확히 하는 것 | - | `apps/api/seed.py:698` | `apps/api/seed.py:698`, `apps/api/seed.py:1273` | 7, 12 | 추가 표현 존재 |
| SEO | 구글 검색 결과 상위에 노출되도록 최적화하는 전통적 방법 | - | `apps/api/seed.py:317` | `apps/api/seed.py:317` | 2 | - |
| SERP | 구글에서 검색하면 나오는 결과 페이지 | - | `apps/api/seed.py:319` | `apps/api/seed.py:319` | 2 | - |
| Share of Voice | 경쟁사 대비 AI 답변에서 우리 브랜드가 차지하는 비율 | - | `apps/api/seed.py:3253` | `apps/api/seed.py:3253` | 27 | - |
| SLA | 과업 승인·검토에 걸리는 최대 시간을 합의한 약속 | Service Level Agreement | `apps/api/seed.py:3724` | `apps/api/seed.py:3724` | 33 | 新 —Stage 6 M6-1 |
| Sitemap | 웹사이트의 모든 페이지 목록을 XML 파일로 정리해 검색엔진에 제출하는 것 | - | `apps/api/seed.py:949` | `apps/api/seed.py:949` | 9 | - |
| Social Signal | SNS에서의 공유, 좋아요, 댓글 등이 브랜드 인지도에 미치는 간접 신호 | - | `apps/api/seed.py:2951` | `apps/api/seed.py:2951` | 25 | - |
| SOP | 표준 운영 절차서 — 반복 과업을 누구나 동일하게 실행할 수 있도록 정리한 문서 | Standard Operating Procedure | `apps/api/seed.py:3752` | `apps/api/seed.py:3752` | 34 | 新 —Stage 6 M6-2 |
| SSR / CSR | 서버가 완성된 HTML을 보내줌(SSR) vs 브라우저가 JavaScript로 직접 화면 조립(CSR) | SSR / CSR | `apps/api/seed.py:611` | `apps/api/seed.py:611` | 6 | - |
| startDate / endDate | 이벤트 시작·종료 일시 — ISO 8601 형식(예: 2025-03-15T14:00:00+09:00)으로 작성 | startDate / endDate | `apps/api/seed.py:2035` | `apps/api/seed.py:2035` | 18 | - |
| Structured Data | AI와 검색엔진이 콘텐츠를 정확히 이해하도록 정리한 코드 형식의 정보 | - | `apps/api/seed.py:469` | `apps/api/seed.py:469` | 4 | - |
| Tier | 출처의 공신력 등급 — Tier 1(정부/학술), Tier 2(산업 리서치), Tier 3(미디어/블로그) | - | `apps/api/seed.py:3784` | `apps/api/seed.py:3784` | 36 | 新 —Stage 6 M6-4 |
| Topic Cluster | 하나의 주제를 중심으로 관련 콘텐츠를 묶어 연결한 콘텐츠 그룹 | - | `apps/api/seed.py:868` | `apps/api/seed.py:868` | 8 | - |
| URL Inspection | Google Search Console에서 URL의 크롤링·렌더링·인덱싱 상태를 확인하는 도구 | - | `apps/api/seed.py:3902` | `apps/api/seed.py:3902` | 39 | 新 —Stage 6 M6-7 |
| UTM Parameter | 링크 끝에 붙이는 추적 태그 — 어디서(source), 어떤 매체(medium), 어떤 캠페인(campaign)으로 유입됐는지 확인 | - | `apps/api/seed.py:3496` | `apps/api/seed.py:3496` | 29 | - |
| utm_source / utm_medium / utm_campaign | 출처(chatgpt), 매체 유형(ai_referral), 캠페인명(geo_tracking)을 지정하는 3대 필수 파라미터 | utm_source / utm_medium / utm_campaign | `apps/api/seed.py:3498` | `apps/api/seed.py:3498` | 29 | - |
| Visibility | AI 답변이나 검색 결과에 우리 콘텐츠가 얼마나 자주 보이는지 | - | `apps/api/seed.py:549` | `apps/api/seed.py:549` | 5 | - |

## Duplicate Term Audit

| Term | Count | Occurrence Lines |
|---|---:|---|
| Domain Rating | 2 | `apps/api/seed.py:1481`, `apps/api/seed.py:2625` |
| Entity | 2 | `apps/api/seed.py:473`, `apps/api/seed.py:2846` |
| KPI | 2 | `apps/api/seed.py:547`, `apps/api/seed.py:3838` (as KPI-A/KPI-B/KPI-C) |
| Semantic HTML | 2 | `apps/api/seed.py:698`, `apps/api/seed.py:1273` |

## Appendix: Glossary Block Index

| Block # | Start Line | Terms |
|---:|---:|---|
| 1 | `apps/api/seed.py:230` | `GEO`, `Citation`, `LLM` |
| 2 | `apps/api/seed.py:316` | `SEO`, `SERP`, `Organic Traffic` |
| 3 | `apps/api/seed.py:397` | `RAG`, `E-E-A-T`, `Embedding` |
| 4 | `apps/api/seed.py:468` | `Structured Data`, `Backlink`, `Entity` |
| 5 | `apps/api/seed.py:546` | `KPI`, `Visibility`, `Conversion`, `CTR` |
| 6 | `apps/api/seed.py:610` | `SSR / CSR`, `Canonical URL`, `Meta Description` |
| 7 | `apps/api/seed.py:695` | `Open Graph`, `Semantic HTML` |
| 8 | `apps/api/seed.py:863` | `IA`, `Hub-Cluster`, `Topic Cluster` |
| 9 | `apps/api/seed.py:948` | `Sitemap`, `Breadcrumb`, `Index / Noindex` |
| 10 | `apps/api/seed.py:1048` | `Answer-first`, `Featured Snippet`, `Inverted Pyramid` |
| 11 | `apps/api/seed.py:1168` | `FAQ`, `Rich Result` |
| 12 | `apps/api/seed.py:1270` | `H1 / H2 / H3`, `Semantic HTML` |
| 13 | `apps/api/seed.py:1387` | `Internal Link`, `Anchor Text`, `Crawl Budget` |
| 14 | `apps/api/seed.py:1478` | `Impression`, `Domain Rating` |
| 15 | `apps/api/seed.py:1643` | `JSON-LD`, `Schema.org`, `Microdata / RDFa` |
| 16 | `apps/api/seed.py:1768` | `BreadcrumbList`, `@context / @type`, `ListItem / position` |
| 17 | `apps/api/seed.py:1895` | `Article / BlogPosting`, `datePublished / dateModified`, `author` |
| 18 | `apps/api/seed.py:2032` | `Event`, `startDate / endDate`, `offers` |
| 19 | `apps/api/seed.py:2169` | `FAQPage`, `mainEntity`, `Question / Answer` |
| 20 | `apps/api/seed.py:2304` | `Rich Results Test`, `Schema Markup Validator` |
| 21 | `apps/api/seed.py:2498` | `Off-site`, `MECE`, `Mention` |
| 22 | `apps/api/seed.py:2620` | `Link Building`, `Editorial Link`, `Domain Rating` |
| 23 | `apps/api/seed.py:2723` | `Digital PR`, `Implied Links`, `Authority` |
| 24 | `apps/api/seed.py:2843` | `Knowledge Graph`, `Entity`, `Business Profile` |
| 25 | `apps/api/seed.py:2950` | `Social Signal`, `Referrer` |
| 26 | `apps/api/seed.py:3057` | `NAP`, `Review Signal` |
| 27 | `apps/api/seed.py:3248` | `Layer 1 / 2 / 3`, `Citation Rate`, `Share of Voice` |
| 28 | `apps/api/seed.py:3366` | `GSC`, `Query`, `Crawl` |
| 29 | `apps/api/seed.py:3493` | `GA4`, `UTM Parameter`, `utm_source / utm_medium / utm_campaign` |
| 30 | `apps/api/seed.py:3621` | `AI Validator`, `Prompt`, `Perplexity` |
| 31 | `apps/api/seed.py:3740` | `A/B Test`, `Hypothesis`, `Control Group` |
| 32 | `apps/api/seed.py:3865` | `Funnel`, `Attribution` |
| 33 | Stage 6 M6-1 Reading | `RACI`, `SLA`, `Phase / P0·P1·P2` |
| 34 | Stage 6 M6-2 Reading | `OAI-SearchBot`, `GPTBot`, `SOP`, `DoD`, `robots.txt` (복습) |
| 35 | Stage 6 M6-3 Reading | `Answer-first` (복습), `CTA`, `H1` (복습), `Hero section` |
| 36 | Stage 6 M6-4 Reading | `Proof-first`, `Tier`, `Citation` (복습), `E-E-A-T` (복습) |
| 37 | Stage 6 M6-5 Reading | `KPI-A / KPI-B / KPI-C`, `AI Validator` (복습), `A/B Test` (복습), `GA4` (복습) |
| 38 | Stage 6 M6-6 Reading | `Fan-out`, `Hub-Spoke` (복습), `Batch`, `Internal Link` (복습) |
| 39 | Stage 6 M6-7 Reading | `Organization`, `URL Inspection`, `Digital PR` (복습), `FAQPage` (복습) |
