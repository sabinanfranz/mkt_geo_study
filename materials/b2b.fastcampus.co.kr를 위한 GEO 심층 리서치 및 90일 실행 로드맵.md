# b2b.fastcampus.co.kr를 위한 GEO 심층 리서치 및 90일 실행 로드맵

## 역할과 문제 정의

**0) 역할(Role)**  
나는 초보자 전용 **GEO/Technical SEO 튜터 + 리서치 리드 + 실무 코치**로서, “용어만 아는 수준”에서 멈추지 않고 **원리(왜) → 방법(어떻게) → 검증(측정) → 실행(로드맵)**까지 한 번에 연결해 설명한다.

**1) 학습 모드(Teaching Mode) 적용 방식(이 문서가 지키는 규칙)**  
- 모든 핵심 용어를 “한 줄 정의 + 비유 + b2b.fastcampus.co.kr 예시 + 흔한 오해” 형태로 설명한다(아래 용어사전).  
- 각 주제는 “왜 중요한지 → 무엇을 해야 하는지 → 어떻게 확인하는지” 순서로 정리한다.  
- 생성형 AI 인용/언급은 **플랫폼별로 블랙박스**인 면이 있어, “확실한 근거(문서/논문)”와 “업계 추정/가설”을 분리한다. citeturn35view0turn8view0turn10view0turn38view0  
- 예시 URL은 사용자가 지정한 기준 페이지(5개)만 사용한다(필수 조건). citeturn12view0turn12view1turn13view0turn14view0turn13view2  

**2) 내가 이해해야 하는 핵심 질문(Problem Statement)**  
전통 SEO(랭킹→클릭)뿐 아니라, ChatGPT·Gemini·Perplexity·Google AI Overviews 같은 생성형 AI가 답변을 만들 때 **b2b.fastcampus.co.kr의 콘텐츠/브랜드가 인용(cite)·언급(mention)**되도록 만드는 **GEO(Generative Engine Optimization)**를 “MECE”하게 이해·실행하는 것이 목표다. 이때 “온사이트(Technical GEO)”와 “오프사이트(Validation)”를 분리해서가 아니라 **하나의 시스템(입력 신호 → 모델/검색 시스템 처리 → 출력: 인용/유입/전환)**으로 연결해 다룬다. citeturn35view0turn8view0  

**3) 리서치 시작점(Seed Sources) 확인**  
- GEO 논문: https://arxiv.org/pdf/2311.09735 (발행: 2024-06-28, KDD’24 Proceedings 표기: 2024-08) citeturn35view0turn36view0turn36view1turn36view2  
- Google 구조화데이터 소개: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data (업데이트일: 2025-12-10) citeturn1view1  
- Google Breadcrumb: https://developers.google.com/search/docs/appearance/structured-data/breadcrumb (업데이트일: 2025-12-10) citeturn2view0  
- Schema.org BreadcrumbList: https://schema.org/BreadcrumbList (Schema.org 릴리스 표기: 2025-12-08) citeturn3view0  
- Rich Results Test: https://search.google.com/test/rich-results (발행일: 미표기, 확인일: 2026-02-21 / 도구 성격) citeturn4search5turn5view2  

**4) 사용자 입력값(지정된 전제) 반영**  
- 사이트/제품: b2b.fastcampus.co.kr (entity["company","패스트캠퍼스","edtech company, kr"] B2B 기업교육) citeturn12view0turn12view1turn13view0turn14view0turn13view2  
- 타깃: HRD/인사/조직문화/교육기획 + 현업 리더(부서장)  
- 전환 목표: 기업교육 상담/문의(리드) + 자료 다운로드 + 세미나 신청  
- 기준 페이지 5개(이 문서의 모든 실습/예시/검증 기준):  
  - https://b2b.fastcampus.co.kr/service_custom (발행일: 미표기, 확인일: 2026-02-21) citeturn12view0  
  - https://b2b.fastcampus.co.kr/refer_customer (발행일: 미표기, 확인일: 2026-02-21) citeturn12view1  
  - https://b2b.fastcampus.co.kr/resource_insight_aiforwork (발행: 2023-08-09) citeturn13view0  
  - https://b2b.fastcampus.co.kr/resource_seminar_onlinelearning (행사일: 2024-05-08) citeturn14view0  
  - https://b2b.fastcampus.co.kr/service_aicamp_b2bproposalwai (강의일정 표기: 2026-02-06) citeturn13view2  

---

## 한 장 요약

**(1) “한 장 요약” (초보자용)**

### GEO가 뭔지 5줄로 요약
1) GEO는 “검색 결과에서 상위 노출”만이 아니라, **생성형 AI가 답을 만들 때 내 사이트가 ‘근거’로 들어가도록** 콘텐츠를 최적화하는 접근이다. citeturn35view0turn8view0  
2) 생성형 엔진은 여러 문서를 **검색·선별(검색 시스템)**한 뒤, 그 내용을 **요약·조합(생성 모델)**하고, 일부는 **인라인 출처(링크/인용)**로 붙여준다. citeturn35view0turn8view0turn10view0turn38view0  
3) 그래서 GEO의 핵심은 “키워드 많이 넣기”보다 **정의·근거·구조·신뢰**처럼 “인용하기 쉬운 형태”를 만드는 데 있다(논문에서도 키워드 스터핑은 성과가 낮다고 보고). citeturn36view1turn36view2  
4) Google은 AI Overviews/AI Mode에 대해 “추가 특별 최적화는 없고, 기존 SEO 기본기가 그대로 중요”하다고 명시한다(즉, Technical SEO는 GEO의 바닥 공사). citeturn9view0  
5) GEO의 성과는 “순위”만이 아니라 **인용/언급 빈도(Visibility) → 유입/전환(Behavior) → 브랜드·권위(Authority)**로 3층 지표로 본다. citeturn8view0turn37view0  

### SEO와 비교해서 달라지는 점 5개
1) **목표 출력이 다르다**: SEO는 “검색 결과 리스트에서 클릭”을, GEO는 “AI 답변 안에서 인용/언급 + 후속 클릭”을 더 강하게 본다. citeturn35view0turn8view0turn10view0  
2) **‘가시성(Visibility)’의 정의가 확장된다**: GEO 논문은 인용이 답변에서 차지하는 비중(예: 단어 수/위치) 같은 다차원 지표를 제안한다. citeturn35view0turn36view1turn36view2  
3) **콘텐츠 형태(구조)가 더 중요해진다**: AI가 “답변 조립”을 하기 때문에, ‘정의/요약/FAQ/표/근거’처럼 재사용하기 쉬운 구조가 유리하다는 근거가 논문에서 제시된다. citeturn36view1turn36view2  
4) **온사이트 기본기가 ‘필수 전제’로 강화**: Google은 AI 기능 노출도 결국 “인덱싱 + 스니펫 가능 + 기술 요건 충족”이 전제라고 말한다. citeturn9view0turn23search3  
5) **측정이 더 실험적**: AI 인용은 변동성이 커서(트리거/링크 구성 변화 등) 반복 샘플링·로그 기반 관찰이 필요하다. Google도 “AI Overviews는 항상 트리거되지 않는다”는 식으로 변동성을 전제한다. citeturn9view0turn10view0  

### 오늘 당장 할 수 있는 80/20 액션 5개
아래는 “난이도(쉬움/보통/어려움)”과 함께, **반드시 b2b.fastcampus.co.kr 기준 페이지**로만 예시를 든다.

1) **Answer-first 요약 박스 추가 (쉬움)**  
- 예시: https://b2b.fastcampus.co.kr/service_custom 상단(H1 아래)에 “누구에게/무엇을/어떤 결과” 3줄 요약 + 5줄 핵심 포인트 섹션 설계. (발행일: 미표기, 확인일: 2026-02-21) citeturn12view0turn36view1  
- **왜(원리)**: GEO 논문에서 “인용/통계/명확한 문장 구성” 같은 요소가 가시성 개선과 연결됨. citeturn36view1turn36view2  
- **검증**: 변경 전후로 AI Validator 질문군(아래 제공)에서 “service_custom 인용 여부”를 샘플링 기록.

2) **사례 허브에 ‘산업별 목차/앵커’ 추가 (쉬움)**  
- 예시: https://b2b.fastcampus.co.kr/refer_customer 에 “제조/금융/IT…” 구간으로 점프하는 목차(TOC) + URL 해시(#manufacturing 등) 앵커 제공. (발행일: 미표기, 확인일: 2026-02-21) citeturn12view1  
- **왜**: Google은 내부 링크/탐색 가능성이 중요하다고 명시한다(검색/AI 기능 공통). citeturn9view0turn34search2  
- **검증**: GSC URL Inspection에서 “페이지가 제대로 렌더/인덱스되는지” 확인(도구 설명은 Google 문서 기준). citeturn5view0turn5view3  

3) **인사이트 글에 ‘정의문 + FAQ + 서비스 내부링크’ 추가 (보통)**  
- 예시: https://b2b.fastcampus.co.kr/resource_insight_aiforwork 본문 상단에 “시티즌 데이터 사이언티스트 정의(1문단)” + “기업교육 적용 FAQ” + “기업 맞춤형 AI 교육” 앵커로 https://b2b.fastcampus.co.kr/service_custom 연결. (발행: 2023-08-09) citeturn13view0turn34search2  
- **왜**: GEO 논문은 ‘인용/통계/명확한 설명’이 가시성에 기여하고, Google은 링크가 발견/관련성 신호임을 언급. citeturn36view1turn34search2  
- **검증**: GA4에서 해당 내부링크 클릭 이벤트(또는 다음 페이지 이동)로 전환 기여 확인(세팅 방법은 GA 문서 참고). citeturn32view2  

4) **BreadcrumbList(JSON-LD) 연습 과제 착수 (보통)**  
- 예시: https://b2b.fastcampus.co.kr/service_custom 에 BreadcrumbList(JSON-LD)를 설계/삽입 가정 → Rich Results Test로 검증. (발행일: 미표기, 확인일: 2026-02-21) citeturn2view0turn3view0turn5view2  
- **왜**: Breadcrumb는 구조화데이터 입문 과제로 난이도 대비 학습효과가 크고, Google이 지원하는 리치리절트 타입 중 하나. citeturn2view0turn5view1turn3view0  
- **검증**: Rich Results Test + (가능하면) GSC Enhancements의 Breadcrumbs 리포트/URL Inspection 확인. citeturn5view1turn5view2  

5) **세미나/오프라인 클래스 페이지에 Event 스키마 적용 (어려움)**  
- 예시 A: https://b2b.fastcampus.co.kr/resource_seminar_onlinelearning (행사일: 2024-05-08, Zoom Live) → Event(online) 스키마 citeturn14view0turn42view0  
- 예시 B: https://b2b.fastcampus.co.kr/service_aicamp_b2bproposalwai (강의일정: 2026-02-06, 장소 표기) → Event(offline) 스키마 citeturn13view2turn42view0  
- **왜**: Google Event 구조화데이터는 이벤트 정보를 더 명확히 전달하는 표준 경로를 제시한다. citeturn42view0  
- **검증**: Rich Results Test → URL Inspection(소유권 있을 때) 순으로 디버깅. citeturn42view0turn5view0turn5view2  

---

## 용어 사전

**(2) “용어 사전(Glossary) + 비유”**  
요청한 용어를 모두 포함한다. 각 항목은 **한 줄 정의 + 비유 + 쉬운 예시(b2b.fastcampus.co.kr) + 흔한 오해**로 구성했다.

> 참고: “초보자에게 쉬운 말”을 위해, 비유는 ‘도서관/요리/네비게이션’ 같은 익숙한 모델을 쓴다.

| 용어 | 한 줄 정의(쉬운 말) | 비유 1개 | 쉬운 예시(b2b.fastcampus.co.kr) | 흔한 오해(주의) |
|---|---|---|---|---|
| GEO | 생성형 AI가 답을 만들 때 **내 페이지가 ‘근거로 채택’**되도록 콘텐츠/구조/신뢰를 최적화 | “요약 보고서에 내 자료가 ‘참고문헌’으로 들어가게 만들기” | “ChatGPT가 ‘기업 맞춤형 생성형 AI 교육’ 질문에 답하면서 https://b2b.fastcampus.co.kr/service_custom 를 출처로 붙이는 상황” (발행일: 미표기, 확인일: 2026-02-21) citeturn12view0turn35view0 | “SEO를 대체한다” → Google은 AI 기능에도 기존 SEO 기본기가 중요하다고 명시. citeturn9view0 |
| Technical GEO | GEO 중에서도 **크롤링/인덱싱/구조화/렌더링** 등 “기술 바닥”을 다루는 영역 | “가게 인테리어 전에 전기·수도 공사하기” | https://b2b.fastcampus.co.kr/refer_customer 를 URL Inspection으로 렌더/인덱스 점검(가이드 문서 기준). (발행일: 미표기, 확인일: 2026-02-21) citeturn12view1turn5view0 | “콘텐츠만 좋으면 기술은 상관없다” → Google 기술 요건(차단/200/인덱서블) 충족이 전제. citeturn23search3 |
| 온페이지/오프페이지 | 온페이지=내 사이트 안에서 바꾸는 것 / 오프페이지=밖에서 ‘평판·검증’을 쌓는 것 | “학교 성적(온페이지) + 추천서/수상(오프페이지)” | 온페이지: https://b2b.fastcampus.co.kr/resource_insight_aiforwork 에 정의·FAQ 추가 / 오프페이지: 외부 글이 “패스트캠퍼스 기업교육”을 언급하며 https://b2b.fastcampus.co.kr/refer_customer 링크(멘션+링크) | “오프페이지=무조건 백링크 구매” → 링크 스팸은 정책 위반 위험(스팸 정책/매뉴얼 액션). citeturn26view1turn34search11 |
| 크롤링 | 검색/AI 시스템이 페이지를 **가져오는(읽으러 오는)** 단계 | “로봇이 책을 ‘서가에서 꺼내오는’ 것” | https://b2b.fastcampus.co.kr/service_custom 이 robots 차단되면(가정) 크롤링이 막힘 → Google은 robots.txt가 ‘보안/비공개’ 수단이 아니라고 안내. citeturn23search0turn23search3 | “robots.txt에 막으면 검색에서 완전히 사라진다” → noindex/비밀번호가 필요할 수 있음. citeturn23search0turn23search3 |
| 인덱싱 | 가져온 페이지를 **검색 DB(색인)**에 넣는 단계 | “도서관 카드에 책 정보를 등록” | https://b2b.fastcampus.co.kr/service_custom 이 200 응답+인덱서블 콘텐츠면 인덱스 대상(최소 기술 요건). citeturn23search3turn12view0 | “사이트맵 제출=즉시 인덱스” → 사이트맵은 힌트이지 보장 아님. citeturn23search2 |
| 랭킹 | 검색 결과에서 어떤 순서로 보여줄지 결정 | “진열대에서 눈높이 칸에 놓을지 결정” | 기업교육 키워드에서 service_custom이 상단에 위치(전통 SEO) vs AI 답변에서 인용(생성형). citeturn35view0turn8view0 | “랭킹만 올리면 GEO도 해결” → GEO는 인용 형태/구조/신뢰가 추가로 작동. citeturn35view0turn36view2 |
| 스키마(Structured Data) | 페이지 내용을 컴퓨터가 읽기 쉽게 **라벨링**하는 표준 포맷 | “택배 상자에 ‘내용물/주소/주의사항’ 라벨 붙이기” | https://b2b.fastcampus.co.kr/service_custom 에 BreadcrumbList(JSON-LD) 넣기(연습 과제). citeturn2view0turn3view0 | “스키마=콘텐츠 대체” → Google은 ‘보이는 내용과 일치’ 필요를 강조. citeturn9view0turn1view1 |
| JSON-LD | 구조화데이터를 넣는 방식 중 하나(보통 `<script type="application/ld+json">`) | “설명서를 ‘별도 종이’로 동봉” | service_custom에 BreadcrumbList JSON-LD 스크립트 삽입 가정 → Rich Results Test로 확인. citeturn5view2turn3view0 | “아무 JSON이면 된다” → Schema.org 문법/컨텍스트가 맞아야 함. citeturn3view0turn29view2 |
| 리치리절트 | 검색 결과에서 카드/별점/이벤트 정보 등 **확장 UI**로 보일 수 있는 형태 | “메뉴판에 사진/뱃지 붙는 것” | 세미나 페이지(onlinelearning)에서 Event 리치리절트 가능성(단, 보장 아님). citeturn42view0turn2view0 | “리치리절트=무조건 노출” → Google은 구조화데이터가 있어도 표시를 보장하지 않는다고 명시. citeturn2view0 |
| BreadcrumbList | 페이지의 **위치(계층)**를 표시하는 구조화데이터 타입 | “내비게이션 ‘현재 위치’ 표시” | service_custom: 홈 > 서비스 > 맞춤형 기업교육(가정) JSON-LD 설계. citeturn2view0turn3view0 | “BreadcrumbList만 하면 AI 인용된다” → 구조화데이터는 신호 중 하나, 콘텐츠/신뢰/기술 요건이 함께 필요. citeturn9view0turn35view0 |
| 헤딩(H1~H6) | 문서의 제목/목차 역할을 하는 구조 | “책의 장/절 제목” | service_custom의 H1은 “기업 생성형AI 교육”(확인). citeturn12view0 | “디자인 글자 크기=헤딩” → HTML 헤딩 태그가 구조 신호. (일반 원칙) citeturn22search2 |
| 정보구조(IA) | 사이트를 **주제별로 묶고 길을 만드는 설계** | “서점에서 ‘분야별 코너’를 만드는 것” | 허브-클러스터: refer_customer(사례 허브) → service_custom(전환) → 관련 리소스(인사이트/세미나). citeturn12view1turn12view0turn13view0turn14view0 | “메뉴만 있으면 IA 끝” → 본문 내 링크/클러스터 구조가 발견성과 관련. citeturn34search2turn9view0 |
| 내부링크 | 같은 도메인 안에서 페이지끼리 연결하는 링크 | “책 안의 ‘관련 페이지로 이동’ 각주” | https://b2b.fastcampus.co.kr/refer_customer(허브) → https://b2b.fastcampus.co.kr/service_custom(전환) 내부링크 설계(앵커텍스트 포함). citeturn12view1turn12view0turn34search2 | “내부링크는 SEO에만” → Google은 AI 기능에도 내부링크가 중요하다고 언급. citeturn9view0 |
| 캐노니컬(canonical) | 중복/유사 페이지가 있을 때 **대표 URL**을 알려주는 힌트 | “같은 내용의 ‘공식본(원본)’ 표시” | UTM 붙은 service_custom?utm_* 같은 변형이 생길 때 대표 URL 정리(개념 예시). citeturn22search1turn22search8turn32view0 | “canonical만 넣으면 Google이 무조건 따른다” → canonicalization은 Google이 대표 URL을 선택하는 ‘과정’이며 보장 아님. citeturn22search1 |
| 백링크 vs 멘션 | 백링크=링크로 이어진 언급 / 멘션=링크 없이 이름만 언급 | “추천서에 연락처(링크)가 있느냐 없느냐” | 외부 글이 “패스트캠퍼스 기업교육”을 언급하며 refer_customer를 링크(멘션+링크) | “멘션은 의미 없다” → 플랫폼별 가중치는 블랙박스라 ‘가설’로 다루되, 평판 신호로 활용 가능(아래 오프사이트 섹션에서 근거/한계 분리). citeturn28view0turn25view0 |
| PR | 언론/협회/업계 채널을 통해 신뢰 가능한 문맥에서 노출되는 활동 | “공식 발표/보도자료로 ‘사회적 증명’ 만들기” | 세미나 모집 글(외부)에 onlinelearning 링크 삽입(예시) | “PR=광고” → 레퍼런스/데이터/전문성 근거가 있을수록 SEO·GEO 모두에 ‘검증 신호’가 될 가능성(부분 가설). citeturn25view0turn28view0 |
| 엔터티(entity) | AI/검색이 “이름=대상”으로 인식하는 개체(회사, 사람, 제품 등) | “인명사전의 ‘항목’” | “패스트캠퍼스 기업교육”을 일관된 명칭/설명으로 반복 노출하고, refer_customer에 근거(사례·수치·고객 유형)를 모아두기 | “엔터티는 스키마만 넣으면 된다” → 구조화데이터는 보조 수단, 실제 콘텐츠/평판/일관성이 같이 필요(근거는 ‘구글은 구조화데이터로 웹/세상 정보 이해’ 수준까지). citeturn1view1turn42view1 |
| 권위/신뢰 신호 | “이 정보 믿어도 되나?”를 판단하게 하는 근거(저자, 출처, 평판, 정책 준수 등) | “논문에 참고문헌/저자 소속이 있는 것” | resource_insight 글에 날짜·출처·근거를 명확히 표기하면 인용 가능성이 올라갈 수 있음(일부는 GEO 논문 근거, 일부는 가설). citeturn13view0turn36view2turn25view0 | “권위=도메인 나이/백링크만” → Google은 ‘사람에게 도움되는 신뢰성’(E‑E‑A‑T 관점)을 강조. citeturn26view0turn28view0 |
| GSC / URL Inspection | GSC=Google 검색 관점의 진단/성과 도구, URL Inspection=특정 URL의 인덱스/라이브 테스트 | “건강검진(사이트) + 정밀검사(특정 URL)” | refer_customer를 URL Inspection으로 ‘구글이 본 HTML/렌더’ 확인(실습). citeturn5view0turn12view1 | “URL Inspection=즉시 랭킹 올리기” → 진단/요청 도구이지 순위 조작 도구 아님. citeturn5view0turn5view3 |
| GA4 / UTM | GA4=행동/전환 측정, UTM=캠페인 출처 태깅 파라미터 | “전단지에 ‘어디서 받았는지’ 도장 찍기” | https://b2b.fastcampus.co.kr/service_custom?utm_source=linkedin&utm_medium=social&utm_campaign=geo_test (발행일: 미표기, 확인일: 2026-02-21) citeturn12view0turn32view0 | “UTM 하나만 붙이면 된다” → GA 문서에서 관련 UTM을 함께 세팅 권고. citeturn32view1 |
| KPI | 목표 달성 여부를 보는 핵심 지표 | “계기판(속도/연료/거리)” | 예: ‘AI 인용 발생률’(Visibility) + ‘문의 전환율’(Behavior) + ‘브랜드 쿼리 증가’(Authority) | “KPI=세션수 하나” → GEO는 인용/언급 같은 상단 지표도 필요. citeturn8view0turn37view0 |

---

## AI 인용 메커니즘과 GEO 레버

**(3) “메커니즘 이해: AI가 왜/어떻게 인용하는가”**

### 확실한 근거로 말할 수 있는 내용 (A)
아래는 “공식 문서/논문”에 근거해 비교적 확실하게 말할 수 있다.

1) **생성형 검색/답변 시스템은 ‘검색(문서 탐색) + 생성(요약/조합)’을 결합**한다.  
- GEO 논문은 generative engines가 관련 문서를 검색해 응답을 만들고, 출처(인라인 인용)를 통해 검증 가능성을 제공한다고 설명한다. citeturn35view0  
- Google도 AI Overviews가 웹 링크를 제공하며, 기존 검색 시스템(품질/랭킹, Knowledge Graph 등)과 결합해 “근거가 있는 정보”를 제공하려는 설계를 설명한다. (PDF: July 2024) citeturn10view0  

2) **Google 관점에서는 ‘AI 기능 노출’에 별도의 추가 기술 요건이 없고, 기존 SEO 기본기가 그대로 중요**하다고 명시한다.  
- “추가 요구사항/특별한 최적화는 없다” + “인덱싱/스니펫 가능/기술 요건 충족이 전제”라고 안내한다. (https://developers.google.com/search/docs/appearance/ai-features, 업데이트일: 2025-12-10) citeturn9view0turn23search3  

3) **AI Overviews/AI Mode는 ‘query fan-out(관련 쿼리 확장 검색)’ 같은 기법으로 더 넓은 링크 후보를 찾을 수 있음**을 Google이 문서에서 직접 언급한다.  
- 즉, “한 번의 검색”만이 아니라 “관련 하위 주제들을 추가 검색”해 지원 링크를 넓힌다고 밝힌다. citeturn8view0  

4) **Perplexity는 ‘답변에 인용(번호 citation)을 포함’한다고 자사 도움말에 명시**한다.  
- (https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work, 업데이트 표기: ‘Updated yesterday’(확인일: 2026-02-21) → 날짜는 상대 표기) citeturn38view0  

5) **구조화데이터는 검색 엔진이 페이지 내용을 이해하는 데 도움이 되지만, 리치리절트 노출을 보장하진 않는다**(중요 오해 방지).  
- Breadcrumb 문서에서 “구조화데이터를 제공해도 결과 노출은 보장되지 않는다”는 취지의 안내가 포함된다. (https://developers.google.com/search/docs/appearance/structured-data/breadcrumb, 업데이트일: 2025-12-10) citeturn2view0  

### 업계 추정/가설로 분리해야 하는 내용 (B)
아래는 “그럴 가능성은 높지만, 플랫폼이 구체 알고리즘을 공개하지 않거나 상황에 따라 달라서” **가설/추정**으로 분리한다.

1) **“AI가 어떤 사이트를 더 잘 인용하는가”의 정확한 가중치**  
- Google은 “특별한 최적화 불필요”라고 했지만, 실제로 어떤 문서가 선택되는지의 세부 가중치는 공개되지 않는다. citeturn9view0turn10view0  
- 따라서 “권위/평판/엔터티 일관성/링크”가 얼마나 작동하는지는 **관찰 기반 실험(로그)**으로 접근해야 한다(아래 90일 실험 설계). citeturn35view0  

2) **“멘션(비링크 언급)”의 직접 효과 크기**  
- Google 문서에서 “비링크 멘션이 랭킹 신호”라고 단정하기는 어려워 일반화가 위험하다(공식적 단정 근거가 부족).  
- 다만 E‑E‑A‑T 관점에서 “외부에서의 평판/정보”를 참고한다는 방향의 문맥은 rater guide/도움말에서 확인되므로, **멘션을 ‘검증 신호’로 설계**하는 것은 합리적 가설이다. citeturn28view0turn26view0  

3) **“LLM이 선호하는 문장/구조(예: Answer-first, 표, FAQ)의 플랫폼별 차이”**  
- GEO 논문은 특정 기법이 가시성을 높일 수 있다고 실험 결과를 제시하지만, 플랫폼별 모델/UX는 다를 수 있다. citeturn36view1turn36view2  
- Google 또한 AI Overviews 트리거/표시가 항상 같지 않고, AI Mode/Overviews의 모델·기법이 다를 수 있다고 말한다. citeturn8view0  

### 인용/언급이 일어나는 과정 텍스트 다이어그램
```text
사용자 질문
  ↓
(1) 후보 문서 탐색
    - 검색 인덱스에서 관련 문서 찾기
    - (일부 시스템은) query fan-out으로 관련 쿼리 확장
  ↓
(2) 후보 문서 평가
    - 적합성(질문과 맞는가)
    - 신뢰/품질(정확·최신·출처·평판)
    - 구조/추출 용이성(정의/요약/표/FAQ 등)
    - 접근성(크롤 가능, 렌더 가능, 200, noindex 아님)
  ↓
(3) 답변 생성(조합)
    - 여러 문서를 요약/합성
  ↓
(4) 출처 연결
    - 인라인 citation / 링크 박스 / 참고 링크 등
  ↓
(5) 사용자 행동
    - 링크 클릭(유입) 또는 클릭 없이 만족(제로클릭)
  ↓
(6) 성과 측정
    - 인용/언급 빈도, 유입/전환, 브랜드 지표로 관찰
```
(1)의 “query fan-out”과 (2)의 “기술 요건/인덱싱 전제”는 Google 문서에 직접 언급된다. citeturn8view0turn23search3  

### 내가 통제 가능한 신호 5개 카테고리
아래 5개는 사용자가 요구한 카테고리 그대로, 그리고 **여기서부터는 “b2b.fastcampus.co.kr 예시”로만** 설명한다.

#### 콘텐츠 신호(정의/요약/사실/근거/최신성)
- **왜 중요한가(원리)**: GEO 논문에서 인용(출처 추가), 통계 추가, 인용문 추가 같은 “근거 강화/정보 밀도”가 가시성 지표를 개선하는 경향을 보여준다. citeturn36view1turn36view2  
- **무엇을 해야 하나(행동)**:  
  - https://b2b.fastcampus.co.kr/service_custom 에 “누구에게/무엇을/어떤 결과” 3줄 요약 + “기업 맞춤형 생성형 AI 교육”의 정의 1문단 추가. citeturn12view0  
  - https://b2b.fastcampus.co.kr/resource_insight_aiforwork 에 “정의→사례→체크리스트” 구조로 재편(발행일/근거 링크 유지). citeturn13view0  
- **어떻게 확인하나(검증)**: AI Validator 질문군에서 “요약 문장을 답변에 재사용하며 출처로 링크하는지”를 샘플링 로그로 기록(아래 측정 섹션).

#### 구조 신호(헤딩/목차/스키마)
- **왜**: Google은 구조화데이터가 콘텐츠 이해에 도움이라고 설명하며, Breadcrumb는 공식 지원 타입이다. citeturn1view1turn2view0turn3view0  
- **행동**:  
  - refer_customer에 산업별 목차/앵커 + 섹션 H2 구조 정리. citeturn12view1  
  - service_custom에 BreadcrumbList(JSON-LD) 추가(아래 실습에 샘플 제공). citeturn2view0turn3view0  
- **검증**: Rich Results Test(구글 리치 결과 관점) + Schema Markup Validator(스키마 문법 관점) + URL Inspection(구글이 본 렌더/인덱스 관점) 역할을 분리해 확인. citeturn29view0turn29view2turn5view0turn5view2  

#### 접근성 신호(크롤 가능, 속도, 렌더링)
- **왜**: 인덱싱/스니펫 가능/기술 요건 충족이 AI 기능 노출의 전제라고 Google이 명시한다. citeturn9view0turn23search3  
- **행동(가설 포함)**:  
  - https://b2b.fastcampus.co.kr/resource_insight_aiforwork 는 본문 텍스트가 잘 노출되지만, 만약(가정) 중요한 구간이 JS 렌더링 의존이 크다면 SSR/프리렌더를 검토(“JS SEO 기본” 문서 참고). 이 부분은 실제 렌더링 구조를 개발자 도구/URL Inspection으로 확인해야 하므로 “가설”로 둔다. citeturn13view0turn22search3turn5view0  
- **검증**: URL Inspection의 “구글이 수신한 HTML/렌더” 확인 + 기술 요건 체크(200/차단/noindex). citeturn5view0turn23search3  

#### 권위/엔터티 신호(브랜드/저자/멘션/링크)
- **왜(근거+추정 혼합)**:  
  - 근거: Google의 사람-우선 콘텐츠 가이드가 “누가 만들었는지(Who)·어떻게 만들었는지(How)·왜 만들었는지(Why)”와 E‑E‑A‑T 관점의 자기점검을 권한다. citeturn26view0turn28view0  
  - 추정: 생성형 AI 인용은 “검증 가능한 출처”를 선호할 가능성이 높아(특히 Perplexity는 citations를 제공한다고 명시), 권위 신호가 간접적으로 영향을 줄 수 있다. 다만 플랫폼별 가중치는 공개되지 않아 실험 기반으로 접근해야 한다. citeturn38view0turn35view0  
- **행동**:  
  - refer_customer를 “근거 저장소”로 강화: 산업별 사례 요약 + (가능하다면) 수치/성과 정의(단, 검증 가능한 범위에서). citeturn12view1turn25view0  
  - 인사이트 글(예: resource_insight)에 저자/팀(기업교육팀) 역할·전문성 표기(사람-우선 가이드의 “Who” 맥락). citeturn26view0turn13view0  

#### 맥락/의도 신호(검색 의도, 질문-답변 형식)
- **왜**: GEO 논문은 “생성형 엔진의 가시성”이 단순 순위가 아니라, 답변 내에서 얼마나 “영향력 있게” 사용되는지로 확장된다고 말한다. 질문 의도에 맞는 “답변 조각”을 제공해야 인용될 가능성이 커진다. citeturn35view0turn36view2  
- **행동**:  
  - service_custom에 “기업교육 컨설팅이 뭐예요?” 같은 질문에 Answer-first로 답하는 섹션을 추가(정의 1문단 → 5줄 요약 → FAQ). citeturn12view0turn36view1  
- **검증**: 동일 질문군을 월/주 단위로 반복 테스트(아래 AI Validator 루틴)하여 “인용/언급” 발생률 변화를 관찰.

---

## Technical GEO 온사이트 플레이북

**(4) Technical GEO(온사이트) “학습+실행” 플레이북**  
형식은 요구대로 **개념 → 왜 → 체크리스트 → 실습**. 실습 예시는 최소 3개 이상 기준 페이지를 사용한다.

### L1 정보구조(IA)

**개념(쉬운 말)**: IA는 사이트를 “책 목차”처럼 만드는 일이다. 독자(사람)와 로봇(검색/AI)이 **어디에 뭐가 있는지** 빨리 찾게 해준다. citeturn34search2turn8view0  

**왜 중요한가(원리)**  
- Google은 내부 링크를 통해 콘텐츠가 “쉽게 발견 가능”해야 한다고 말한다(검색/AI 기능 공통 기본기). citeturn8view0turn34search2  
- GEO 논문 관점에서도 생성형 엔진이 후보 문서를 찾는 단계가 있으며, 접근 가능한 구조가 전제다. citeturn35view0  

**체크리스트(IA 최소 요건)**  
- 서비스(전환) 페이지가 명확한가? → https://b2b.fastcampus.co.kr/service_custom citeturn12view0  
- 사례(검증) 허브가 있는가? → https://b2b.fastcampus.co.kr/refer_customer citeturn12view1  
- 리소스(학습/유입) 허브가 있는가? → https://b2b.fastcampus.co.kr/resource_insight_aiforwork / https://b2b.fastcampus.co.kr/resource_seminar_onlinelearning citeturn13view0turn14view0  
- 허브(사례/리소스)에서 서비스(전환)로 내부링크가 설계되어 있는가? (없다면 추가) citeturn34search2  

**실습 과제(초보자용)**  
- (과제 1) “허브-클러스터 맵”을 텍스트로 작성해 보기  
  - 허브: refer_customer(사례 허브)  
  - 클러스터: service_custom(맞춤형 기업교육 전환), resource_insight(인사이트), resource_seminar(이벤트)  
  - 각 페이지에서 ‘다음 단계’ 링크 1개씩만 먼저 연결(과도한 링크보다 명확한 경로). citeturn12view1turn12view0turn13view0turn14view0  

### L2 페이지 구조(Answer-first, FAQ, 정의문)

**개념**: 페이지를 “답변 카드”처럼 만든다. AI가 재사용하기 쉬운 ‘짧은 정의/요약/FAQ’가 있으면 인용 조각으로 쓰기 편해진다(이 부분은 GEO 논문 결과를 근거로 삼되, 플랫폼별로 다를 수 있어 실험이 필요). citeturn36view1turn36view2  

**왜(원리)**  
- GEO 논문에서 “Cite sources / Quotation addition / Statistics addition” 같은 신호가 가시성 개선과 연관. 즉, 답변에 쓰기 좋은 “근거 단위”를 제공하는 게 중요. citeturn36view1turn36view2  
- Google의 사람-우선 콘텐츠 가이드는 “누가/어떻게/왜”를 명확히 하고 신뢰 가능한 정보를 만들라고 권한다. citeturn26view0  

**체크리스트(서비스/사례/콘텐츠 공통)**  
- H1이 “사용자 의도(문제/해결)”를 즉시 말해주는가? (예: service_custom H1 확인) citeturn12view0  
- 첫 화면에 “정의 1문단 + 핵심 5줄”이 있는가? (없다면 추가)  
- FAQ가 있는가? (없다면 5~8개부터)  
- “다음 행동(문의/자료/세미나)” CTA가 질문 흐름과 연결되는가? citeturn12view0turn14view0turn13view2  

**실습(페이지 리모델링 예시)**  
- (과제 2) https://b2b.fastcampus.co.kr/service_custom 을 아래 순서로 섹션 리모델링(콘텐츠는 ‘가정’으로 작성 후 실제 데이터로 교체):  
  1) 한 문단 정의: “기업 맞춤형 생성형 AI 교육이란?”  
  2) 5줄 요약: 대상/방식/기간/성과/다음 단계  
  3) FAQ: “폐쇄망에서도 가능한가?”, “직무별로 커스텀 가능한가?” 등  
  4) 사례로 증명: refer_customer로 이동 링크(앵커텍스트 포함) citeturn12view0turn12view1turn34search2  

### L3 구조화데이터(스키마)

**개념**: 구조화데이터는 “컴퓨터용 요약 라벨”이다. 사람에게 보이는 본문을 바꾸지 않고도, 기계가 이해하기 쉽게 정리한다. citeturn1view1  

**왜(원리)**  
- Google은 구조화데이터를 콘텐츠 이해/웹 전반 정보 수집에 활용한다고 설명한다. citeturn1view1  
- 단, 구조화데이터를 제공해도 리치리절트 노출은 보장되지 않는다(초보자 착각 방지). citeturn2view0  
- Google은 2025~2026에 일부 구조화데이터 기능 지원을 축소/중단했음을 공지했다. 따라서 “지원되는 타입 중심, 오남용 금지”가 중요. citeturn41view4turn41view3  

**체크리스트(스키마 기본 원칙)**  
- 보이는 내용과 구조화데이터가 **일치**하는가? citeturn8view0turn1view1  
- Google이 지원/가이드하는 타입인가? (Breadcrumb, Article, Event 등) citeturn2view0turn42view2turn42view0  
- 지원 중단/축소된 타입(Course Info 등)에 의존하지 않는가? citeturn41view4turn41view3  

**실습: 페이지 유형별 “권장 스키마(현실형)”**  
- 서비스 페이지(service_custom): BreadcrumbList + WebPage(기본) *(리치리절트 목적이라기보다 구조 연습/이해 목적)* citeturn2view0turn3view0  
- 인사이트 글(resource_insight): Article/BlogPosting(날짜/작성자/헤드라인/이미지 등) citeturn42view2turn13view0  
- 세미나/오프라인 클래스(resource_seminar, service_aicamp): Event(온라인/오프라인) citeturn42view0turn14view0turn13view2  

### L4 내부링크(허브/클러스터, 앵커텍스트)

**개념**: 내부링크는 “사이트 안 길 안내 표지판”이다. Google은 링크를 **발견(크롤) + 관련성 신호**로 사용한다고 문서에서 말한다. citeturn34search2  

**왜(원리)**  
- 링크는 Google이 새 페이지를 찾고 관련성을 파악하는 데 쓰인다. citeturn34search2  
- AI 기능에도 내부링크가 유효한 기본기라고 Google이 명시한다. citeturn9view0  

**체크리스트(초보자용 내부링크 규칙 7개)**  
- 허브는 “목차” 역할을 하는가? (refer_customer) citeturn12view1  
- 클러스터는 허브로 되돌아오는가? (service_custom, resource_*)  
- 앵커텍스트가 “그 링크를 클릭하면 무엇을 얻는지” 말하는가? (예: “기업 맞춤형 AI 교육”) citeturn34search2  
- ‘여기 클릭’ 같은 모호한 앵커는 줄이는가? citeturn34search2  
- 한 페이지에서 가장 중요한 내부링크 1~3개가 눈에 띄는가?  
- 동일 주제끼리 서로 연결되는가? (insight ↔ service_custom) citeturn13view0turn12view0  
- URL이 변형(UTM 등)될 때 canonical을 고려하는가? citeturn22search1turn32view0  

**실습(요청된 예시 포함)**  
- (과제 3) https://b2b.fastcampus.co.kr/resource_insight_aiforwork → https://b2b.fastcampus.co.kr/service_custom 로 **“기업 맞춤형 AI 교육”** 앵커텍스트 내부링크 1개 삽입. citeturn13view0turn12view0turn34search2  

### L5 기술 접근성(크롤링/렌더링, robots, sitemap, 성능/모바일)

**개념**: 기술 접근성은 “로봇이 들어올 수 있는 문”과 “들어와서 읽을 수 있는 조명”이다.

**왜(원리)**  
- Google Search 기술 요건의 최소 조건: (1) Googlebot 차단 없음 (2) 200 응답 (3) 인덱서블 콘텐츠. citeturn23search3  
- AI 기능도 결국 “인덱싱되고 스니펫으로 노출 가능”해야 지원 링크로 포함될 수 있다고 Google이 말한다. citeturn9view0turn23search3  
- robots.txt는 주로 크롤링 제어이며 “검색 제외”의 보안 장치가 아니라는 점도 Google이 강조한다. citeturn23search0turn23search3  

**체크리스트(초보자용 기술 진단 표준)**  
- 200 상태코드로 접근 가능한가? (브라우저/서버 로그/URL Inspection) citeturn23search3turn5view0  
- noindex가 의도치 않게 들어가 있지 않은가? citeturn23search3turn9view0  
- robots.txt가 중요한 경로를 막고 있지 않은가? citeturn23search0  
- 사이트맵이 있고, 중요한 URL이 포함되는가? (사이트맵은 보장 아님, “도움”임) citeturn23search2  
- JS 렌더링이 핵심 콘텐츠를 가리지 않는가? (JS SEO 기본 문서 참고) citeturn22search3  

**실습(GSC 기준)**  
- (과제 4) https://b2b.fastcampus.co.kr/refer_customer 를 URL Inspection으로 테스트(인덱스 상태/라이브 테스트/렌더 확인). citeturn5view0turn12view1  

### BreadcrumbList가 초보자에게 좋은 연습 과제인 이유
1) **페이지 거의 모든 유형에 적용** 가능(서비스/사례/콘텐츠/이벤트). citeturn2view0turn3view0  
2) 요구 필드가 비교적 단순(리스트+position+name+item URL)해서 “구조화데이터 감”을 잡기 좋다. citeturn3view0  
3) Rich Results Test로 빠르게 피드백을 받을 수 있어 학습 루프가 짧다. citeturn5view2  

**예시 과제(요청된 형태 그대로)**  
- 대상: https://b2b.fastcampus.co.kr/service_custom (발행일: 미표기, 확인일: 2026-02-21) citeturn12view0  
- 목표: BreadcrumbList(JSON-LD) 설계/삽입(가정) → 테스트/검증 절차 작성  
- 검증 절차:  
  1) JSON-LD 작성(아래 샘플)  
  2) Rich Results Test로 “Breadcrumbs” 인식 확인 citeturn5view2turn5view1  
  3) Schema Markup Validator로 문법/그래프 확인 citeturn29view2turn29view0  
  4) (GSC 소유 시) URL Inspection으로 구글이 본 HTML에 JSON-LD가 포함되는지 확인 citeturn5view0  

샘플(JSON-LD, **실제 IA에 맞게 name/url 교체 필요**):
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "홈",
      "item": "https://b2b.fastcampus.co.kr/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "서비스",
      "item": "https://b2b.fastcampus.co.kr/service_custom"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "맞춤형 기업교육",
      "item": "https://b2b.fastcampus.co.kr/service_custom"
    }
  ]
}
</script>
```

### 스키마를 넣었을 때 생기는 착각 3가지
1) **“넣으면 무조건 노출된다” 착각**  
- Google은 구조화데이터가 있어도 리치리절트 노출을 보장하지 않는다고 명시한다. citeturn2view0  
2) **“리치리절트=랭킹 상승” 착각**  
- 구조화데이터는 “이해/표현”을 돕는 도구이며, 일부 기능은 지원이 축소될 수 있다(2025~2026 일부 타입 지원 중단 공지). citeturn41view4turn41view3  
3) **“스키마=콘텐츠 대체” 착각**  
- Google은 구조화데이터가 “보이는 내용과 일치”해야 하고, 사람-우선/스팸 정책을 따라야 함을 강조한다. citeturn9view0turn26view1turn1view1  

### 검증 도구 역할 차이
- **Rich Results Test**: “Google 리치리절트 관점에서” 어떤 결과가 생성될 수 있는지 확인. (https://search.google.com/test/rich-results, 발행일 미표기/확인일: 2026-02-21) citeturn5view2turn29view0  
- **Schema Markup Validator**: “Schema.org 문법/그래프 관점” 범용 검증(구글 특화 경고 아님). (https://validator.schema.org, 발행일 미표기/Schema.org 안내: 2021-05-21) citeturn29view1turn29view2  
- **GSC (Enhancements/URL Inspection)**: “구글 인덱스/수집 관점”에서 실제로 인식했는지, 어떤 이슈가 있는지 확인. citeturn5view0turn5view1  

---

## Off-site Validation, 측정, 90일 설계, 근거

## 오프사이트 실행 플레이북

**(5) Off-site Validation(오프사이트) “학습+실행” 플레이북**

### MECE 분류(요청된 5갈래)
아래는 “백링크/멘션/PR/소셜/리뷰”를 **겹치지 않게 정의**해 MECE로 정리한다.

1) **백링크**: 외부 페이지가 내 페이지로 “클릭 가능한 링크” 제공  
2) **멘션(비링크)**: 외부에서 브랜드/서비스명을 텍스트로 언급(링크 없음)  
3) **PR/에디토리얼 노출**: 언론/협회/전문 채널 등 “신뢰 문맥”에서 소개  
4) **소셜 유통**: LinkedIn/블로그/커뮤니티 등에서 콘텐츠 확산(링크 포함 가능)  
5) **리뷰/디렉토리**: 제3자 플랫폼의 평가/프로필/디렉토리(기업/행사/교육 정보)

### 각 채널: 언제 효과적인지 + 근거 수준(High/Med/Low) + 실행 예시 3개
근거 수준은 “검색(전통 SEO)”과 “생성형 인용”을 분리한다.  
- 검색에 대해 “링크가 신호”라는 것은 Google 문서에 직접 근거가 있다. citeturn34search2  
- 생성형 인용에 대한 직접 근거는 제한적이므로, 일부는 GEO 논문/각 플랫폼 문서에서 간접 근거로만 제시하고, 나머지는 가설로 표기한다. citeturn35view0turn38view0turn8view0  

#### 백링크
- 효과 상황: “사례/데이터/정의” 페이지가 외부 글의 근거로 쓰일 때  
- 근거 수준: 검색=High(링크는 신호/발견 수단) / 생성형=Med(출처 링크를 제공하는 시스템에서 간접적 유리 가능) citeturn34search2turn35view0turn10view0  
- 실행 예시(초보자용, b2b 링크 포함):  
  1) 세미나 요약 외부 포스트에 https://b2b.fastcampus.co.kr/resource_seminar_onlinelearning 링크(행사 상세 근거) citeturn14view0  
  2) 기업교육 성공사례 요약 글에서 https://b2b.fastcampus.co.kr/refer_customer 링크(사례 허브) citeturn12view1  
  3) 기업 맞춤형 교육 소개 글에서 https://b2b.fastcampus.co.kr/service_custom 링크(전환) citeturn12view0  

#### 멘션(비링크)
- 효과 상황: “브랜드가 동일 개체로 인지”되도록 일관된 이름/설명/전문성 맥락이 축적될 때(가설)  
- 근거 수준: 검색=Low~Med(공식적 단정 어려움) / 생성형=Low~Med(가설)  
- 왜 가설인가: 멘션의 직접 가중치는 공식 문서로 단정하기 어렵고 블랙박스이기 때문. 대신 E‑E‑A‑T/평판 정보의 중요성은 문서에서 간접 확인 가능. citeturn26view0turn28view0  
- 실행 예시(멘션+가능하면 링크까지 권장):  
  1) 업계 뉴스레터에 “패스트캠퍼스 기업교육” 멘션 + refer_customer 링크 citeturn12view1  
  2) HRD 커뮤니티 후기 글에 멘션 + service_custom 링크 citeturn12view0  
  3) 웨비나 발표자료 공개 페이지에 멘션 + resource_seminar 링크 citeturn14view0  

#### PR/에디토리얼 노출
- 효과 상황: “검증 가능한 사실·데이터·사례”가 있을 때(단순 홍보보다)  
- 근거 수준: 검색=Med(정책 준수 전제) / 생성형=Med(출처로 쓰기 좋은 ‘권위 문맥’ 가설) citeturn26view0turn35view0  
- 실행 예시:  
  1) “기업 생성형 AI 교육 트렌드 리포트” 보도자료형 콘텐츠 제작 후 service_custom 링크 포함 citeturn12view0  
  2) “산업별 사례 모음” 레퍼런스 자료 배포하며 refer_customer 링크 포함 citeturn12view1  
  3) 세미나 recap 기사/블로그에 resource_seminar 링크 포함 citeturn14view0  

#### 소셜 유통
- 효과 상황: 타깃(HRD/리더)이 있는 채널(예: LinkedIn)에서 “질문-답변형 인사이트”를 배포할 때  
- 근거 수준: 검색=Low(직접 랭킹 신호로 단정 어려움) / 생성형=Low~Med(간접 노출/크롤 가능성 가설)  
- 실행 예시:  
  1) LinkedIn 포스트에 UTM 붙여 service_custom 공유: `.../service_custom?utm_source=linkedin&utm_medium=social&utm_campaign=geo_test` citeturn12view0turn32view0  
  2) 산업별 사례 카드뉴스로 refer_customer 링크 공유 citeturn12view1  
  3) 세미나 신청 리마인드로 resource_seminar 링크 공유 citeturn14view0  

#### 리뷰/디렉토리
- 효과 상황: B2B 의사결정에서 “사회적 증명”이 필요한 곳(리뷰·프로필·행사 목록)  
- 근거 수준: 검색=Low~Med / 생성형=Low~Med(가설)  
- 실행 예시:  
  1) 세미나/교육 행사 캘린더에 resource_seminar 등록(링크 포함) citeturn14view0  
  2) 기업교육 솔루션 비교/디렉토리에 service_custom 등록(링크 포함) citeturn12view0  
  3) 사례 허브(refer_customer)를 “실적/검증” 페이지로 소개하는 외부 프로필에 링크 포함 citeturn12view1  

---

## AI Validator 채널 전략(운영 루틴)

**핵심 아이디어**: 생성형 AI 인용은 변동성이 크므로, “1번 보고 결론 내기”가 아니라 **정해진 질문군을 반복 테스트**하고 로그를 쌓아 “추세”를 본다. Google도 AI Overviews가 항상 트리거되지 않는다는 식으로 변동성을 전제한다. citeturn8view0turn10view0  

### 주 1회 루틴(운영자 1명 기준, 30~60분)
- 고정 질문군 10개(아래 제공)으로 ChatGPT/Gemini/Perplexity/Google AI Overviews에서 테스트  
- 결과 기록: “인용 URL / 언급 문장 / 답변에 포함된 핵심 문구 / 클릭 여부(가능하면)”  
- 페이지 개선 액션으로 연결: “인용이 안 되면 → Answer-first/FAQ/근거/내부링크 강화” 식의 규칙

### 월 1회 루틴(팀 단위, 60~120분)
- 질문군 확장(신규 키워드/산업 추가)  
- 상위 5개 페이지(기준 페이지) 점검표 업데이트  
- 오프사이트 실행(한 달 3개 배포) 체크

### 질문군(프롬프트 템플릿) 10개
각 질문은 “b2b.fastcampus.co.kr에서 찾아서 인용”을 명시해 테스트한다(요청사항).  
1) “기업 맞춤형 생성형 AI 교육이 필요한 이유를 설명해줘. 출처는 b2b.fastcampus.co.kr에서 찾아서 인용해줘. 특히 https://b2b.fastcampus.co.kr/service_custom 을 참고해줘.”  
2) “기업교육 컨설팅이 무엇인지 5줄로 정의해줘. 출처는 b2b.fastcampus.co.kr로 제한하고 https://b2b.fastcampus.co.kr/service_custom 을 인용해줘.”  
3) “산업별 생성형 AI 교육 사례를 3개 유형으로 정리해줘. 근거는 https://b2b.fastcampus.co.kr/refer_customer 에서 인용해줘.”  
4) “HRD 담당자가 기업교육 ROI를 설계할 때 체크리스트를 만들어줘. b2b.fastcampus.co.kr에서 인용하고, 가능하면 https://b2b.fastcampus.co.kr/refer_customer 를 포함해줘.”  
5) “시티즌 데이터 사이언티스트(Citizen Data Scientist) 개념을 초보자용으로 설명해줘. 출처는 https://b2b.fastcampus.co.kr/resource_insight_aiforwork 에서 인용해줘.”  
6) “온라인 기업교육에서 수료율을 높이는 방법을 5가지로 정리해줘. 출처는 https://b2b.fastcampus.co.kr/resource_seminar_onlinelearning 에서 인용해줘.”  
7) “B2B 영업 조직을 위한 AI 실전 교육 커리큘럼 예시를 만들어줘. 출처는 https://b2b.fastcampus.co.kr/service_aicamp_b2bproposalwai 에서 인용해줘.”  
8) “폐쇄망 환경에서 가능한 기업 AI 교육 설계 시 고려사항을 정리해줘. b2b.fastcampus.co.kr에서 인용하고 service_custom을 포함해줘.”  
9) “기업교육 담당자가 ‘맞춤형 교육’과 ‘정형화 교육(공통 과정)’ 중 선택할 때 질문해야 할 7가지를 만들어줘. b2b.fastcampus.co.kr를 출처로 인용해줘.”  
10) “패스트캠퍼스 기업교육의 강점(강사진/프로세스/사례)을 ‘근거 기반’으로 요약해줘. 반드시 b2b.fastcampus.co.kr의 URL을 2개 이상 인용해줘.”

> 참고(근거): Perplexity는 citations 제공을 명시하지만, “도메인 제한 요청을 항상 그대로 따를지”는 플랫폼 정책/모드에 따라 달라질 수 있다(따라서 로그 기반 관찰이 필요). citeturn38view0  

### 결과가 나쁘면 어떤 액션으로 연결할지(규칙)
- **인용이 0건**: 해당 질문에 대한 Answer-first 정의 1문단 + FAQ 5개 추가(온사이트). citeturn36view1turn26view0  
- **언급은 있는데 링크가 없음**: 해당 문장을 “근거/수치/사례”가 있는 문단으로 강화 + refer_customer로 검증 링크 추가(온사이트+오프사이트). citeturn12view1turn36view2  
- **잘못된 내용으로 요약됨**: 페이지 상단에 “오해 방지 섹션(What we do / What we don’t)” 추가 + 최신화 날짜 표기(온사이트). citeturn26view0turn10view0  
- **경쟁/일반 정보만 인용**: resource_insight 같은 콘텐츠를 “질문형(FAQ)”으로 재편하고 내부링크로 service_custom에 연결(클러스터 강화). citeturn13view0turn34search2  

---

## 측정(Measurement) — KPI 3층 + 도구 매핑

**(6) 측정(Measurement)**

### KPI 3층 구조(예시는 모두 b2b.fastcampus.co.kr 기반)

#### 1) Visibility(인용/언급/질문군 커버리지)
- 예: “기업 생성형 AI 교육” 질문군에서 **https://b2b.fastcampus.co.kr/service_custom 인용 발생률**(주 1회 10문항 샘플 중 몇 번 인용됐는지) citeturn12view0  
- 예: “시티즌 데이터 사이언티스트” 질문에서 **https://b2b.fastcampus.co.kr/resource_insight_aiforwork**가 출처로 붙는지 citeturn13view0  

#### 2) Behavior(유입/체류/전환)
- 예: **refer_customer → service_custom 이동률**(내부링크 클릭/다음 페이지 전환) citeturn12view1turn12view0turn34search2  
- 예: service_custom에서 “기업교육 상담 문의” 전환(폼 제출/클릭)을 GA4 키 이벤트로 측정(가이드 문서 기준). citeturn32view2turn12view0  

#### 3) Authority(브랜드 검색량/멘션/링크 품질)
- 예: “패스트캠퍼스 기업교육” 브랜드 쿼리 변화  
  - Search Console의 **브랜디드 쿼리 필터**가 제공됨(2025-11-20 공지). https://developers.google.com/search/blog/2025/11/search-console-branded-filter (발행일: 2025-11-20) citeturn37view0  
- 예: 외부 링크/멘션 문서 수(SEO 툴 또는 수동 모니터링)  
  - 링크는 Google이 신호로 사용한다고 설명(링크 베스트 프랙티스). citeturn34search2  

### 도구별 “가능/불가능” 명확화

#### GSC(가능)
- 검색 쿼리/노출/클릭/CTR/평균순위(Performance report) 확인(문서: 발행일 미표기, 확인일: 2026-02-21). citeturn31search2  
- URL Inspection으로 “인덱스된 버전/라이브 테스트/렌더” 확인. citeturn5view0  
- 구조화데이터(리치리절트) 리포트/샘플 확인(리치리절트 리포트는 포괄적 목록이 아니라 샘플을 보여준다고 안내). citeturn5view1  

#### GSC(불가능/제한)
- “ChatGPT/Perplexity가 나를 인용했는지”를 자동 집계해주지 않는다(생성형 플랫폼 외부 데이터).  
- AI Overviews에서 “cited-but-no-click”를 구분한 전용 지표는 제한적이며, Google은 AI 기능 트래픽을 전체 검색 트래픽 안에 포함해 보고한다고 설명한다. citeturn8view0  

#### GA4(가능)
- UTM으로 캠페인 유입 출처를 식별하고(공식 URL Builder 도움말), 전환(리드 폼 제출 등)을 키 이벤트로 측정할 수 있다. citeturn32view0turn32view2  
- 추천 이벤트(generate_lead 등)를 참고해 리드 생성 이벤트를 표준화할 수 있다(개발자 문서, 업데이트일: 2026-02-18). citeturn33view3  

#### GA4(불가능/제한)
- “AI 답변에 내 URL이 인용됨” 자체를 자동 감지하지는 못한다(클릭해서 들어와야 세션으로 잡힘).

### “AI 인용/언급 측정”을 현실적으로 하는 3가지 방식

1) (a) **수동 샘플링**  
- 주 1회 고정 질문군 10개 × 플랫폼 3~4개 = 30~40회 관찰  
- 장점: 빠르고 비용 0  
- 한계: 표본이 작고, 사람이 실수할 수 있음(따라서 템플릿/로그 필요)

2) (b) **스프레드시트 로그**  
- 열(Columns) 권장: 날짜, 플랫폼, 질문, 결과 요약, 인용 URL(있/없), 인용 위치(상/중/하), 클릭 유도 문구, 스크린샷 링크, 후속 액션(콘텐츠 수정 티켓)  
- 장점: 팀 공유/추세 확인 쉬움  
- 한계: 여전히 수동

3) (c) **자동화(가능한 경우만)**  
- 가능 조건: 플랫폼이 API/자동 수집을 허용하고, 정책/요금/레이트리밋을 준수할 수 있을 때  
- 한계: 많은 생성형 플랫폼은 자동 스크래핑을 제한하거나, 결과가 개인화/세션에 따라 달라 재현성이 떨어질 수 있음(그래서 “정책 확인 + 비침해적 방식”이 필요). citeturn8view0turn38view0  

---

## 초보자용 실험 설계(90일)

**(7) 초보자용 실험 설계(90일)**  
원칙: “바꾸는 것(What) → 이유(Why) → 측정(How) → 실패 기준 → 리스크”로 작성한다.

### 가설 6개(모두 b2b.fastcampus.co.kr 기반)

| 가설 | 변경점(What) | 이유(Why) | 측정지표(How) | 실패 기준 | 예상 리스크 |
|---|---|---|---|---|---|
| H1 | service_custom에 “Answer-first 요약 + FAQ” 추가 | GEO 논문에서 ‘정보 구조/근거 단위’가 가시성 개선에 기여 가능. citeturn36view1turn36view2 | (a) AI 인용 발생률(주 1회 10문항) (b) GA4 전환율(문의) | 4주 후 인용 0건 + 전환 변화 없음 | FAQ가 과장/중복되면 품질 저하(사람-우선 가이드 위배 위험) citeturn26view0 |
| H2 | resource_insight_aiforwork에 “정의문 + 내부링크(기업 맞춤형 AI 교육)” 추가 | 링크는 발견/관련성 신호(구글 문서), 클러스터 강화. citeturn34search2 | refer_customer→service_custom 이동률, insight→service_custom 이동률 | 4주 후 이동률 변화 없거나 이탈 상승 | 과도한 내부링크로 UX 악화 |
| H3 | refer_customer에 “산업별 앵커/목차 + 서비스 내부링크” 추가 | 허브 페이지의 탐색성 개선이 발견성에 유리(구글 내부링크 권장). citeturn9view0turn34search2 | (a) AI가 ‘사례’ 질문에서 refer_customer 인용하는지 (b) 허브→전환 이동률 | 4주 후 인용/이동률 변화 없음 | 목차가 실제 콘텐츠 구조와 불일치하면 혼란 |
| H4 | service_custom에 BreadcrumbList(JSON-LD) 추가 | 구조화데이터 학습+구조 신호 강화(Breadcrumb 지원). 단, 노출 보장 아님. citeturn2view0turn3view0 | Rich Results Test에서 Breadcrumb 인식 여부, GSC(가능하면) Breadcrumb 리포트 | 마크업 오류 지속/수정 불가 | “스키마=성과” 착각으로 콘텐츠 개선이 늦어질 위험 citeturn2view0 |
| H5 | resource_seminar_onlinelearning에 Event 스키마 추가 | Google Event 구조화데이터는 이벤트 정보 전달 표준. citeturn42view0 | Rich Results Test 통과 + 검색 노출 변화(가능하면 GSC) | 6주 후에도 이벤트 마크업 인식 0 | 과거 이벤트라(2024-05-08) 노출 기회가 제한될 수 있음(한계) citeturn14view0 |
| H6 | service_aicamp_b2bproposalwai에 Event 스키마 + “다음 차수 알림 신청” CTA 구조화 | 페이지에 일정/장소가 명확(현재 텍스트에 존재). Event 스키마로 기계 이해 강화. citeturn13view2turn42view0 | Rich Results Test 통과 + GA4 전환(알림 신청) | 6주 후 전환 변화 없음 | “모집 마감” 상태라 트래픽 자체가 제한될 수 있음(한계) citeturn13view2 |

### AI 변동성: 통제하기 어려운 요소 vs 관찰 가능한 방식
- 통제 어려움:  
  - AI Overviews 트리거 자체가 조건부이며 항상 발생하지 않음. citeturn8view0turn10view0  
  - 플랫폼별 모델/링크 UI가 변경될 수 있음(최근 링크 표시 개선 같은 변화는 뉴스/공지에서 반복). citeturn7news35turn34news37  
- 관찰 가능:  
  - 동일 질문군을 같은 조건(로그인/지역/언어)에서 반복 샘플링하고, “인용 URL/언급 문장”을 로그로 남겨 추세를 본다. citeturn35view0turn8view0  

---

## 90일 실행 로드맵 + 체크리스트

**(8) 90일 실행 로드맵(초보자용) + 체크리스트)**  
요구한 0~2주 / 3~6주 / 7~10주 / 11~13주로 제시한다.

### 0~2주: 계측/기술부채/핵심 페이지 선정
- 산출물 1: “기준 페이지 5개 진단 표” (아래 템플릿)  
- 산출물 2: AI Validator 질문군 시트 + 주 1회 루틴 캘린더  
- 산출물 3: GA4 이벤트/UTM 네이밍 규칙(간단 표준)

**기준 페이지 5개 진단 표(템플릿)**

| URL | 유형 | Answer-first 요약 | FAQ | 내부링크(허브↔전환) | 스키마(현황/추가) | GSC URL Inspection | 목표 KPI |
|---|---|---|---|---|---|---|---|
| https://b2b.fastcampus.co.kr/service_custom | 서비스/전환 | 없음→추가 | 없음→추가 | refer_customer에서 유입 | BreadcrumbList(추가) | 테스트 | AI 인용률/문의 |
| https://b2b.fastcampus.co.kr/refer_customer | 사례 허브 | 요약 약함→개선 | 섹션형 FAQ | service_custom로 링크 | BreadcrumbList(선택) | 테스트 | 사례 인용/이동률 |
| https://b2b.fastcampus.co.kr/resource_insight_aiforwork | 인사이트 | 있음(본문)→정의 강화 | 없음→추가 | service_custom로 링크 | Article(추가) | 테스트 | 인용/유입 |
| https://b2b.fastcampus.co.kr/resource_seminar_onlinelearning | 세미나 | 섹션 있음 | 일부 Q&A | 서비스/문의 링크 | Event(추가) | 테스트 | 신청/인용 |
| https://b2b.fastcampus.co.kr/service_aicamp_b2bproposalwai | 과정/상품형 | 요약 있음 | 일부 | 관련 서비스 링크 | Event(추가) | 테스트 | 알림 신청 |

(GSC URL Inspection 자체는 “구글 인덱스/라이브 테스트” 진단 도구라는 점을 Google이 설명한다.) citeturn5view0turn23search3  

### 3~6주: 페이지 리모델링(헤딩/요약/스키마/내부링크)
- Week 3~4: service_custom 1차 리모델링(정의→요약→FAQ→사례 링크) citeturn12view0  
- Week 4~5: refer_customer 목차/앵커 + 서비스 내부링크 설계 citeturn12view1  
- Week 5~6: resource_insight 정의/FAQ + 내부링크 + Article 스키마 설계 citeturn13view0turn42view2  
- 검증 산출물: Rich Results Test/Validator 캡처, URL Inspection 결과 메모 citeturn5view2turn29view2turn5view0  

### 7~10주: 오프사이트(멘션/PR/링크) + 검증 루틴
- Month 2~3:  
  - 세미나 기반 홍보 포스트 1~2개 제작(onlinelearning 링크 포함) citeturn14view0  
  - 사례 요약 글 배포(refer_customer 링크 포함) citeturn12view1  
  - 서비스 설명 글 배포(service_custom 링크 포함, UTM 권장) citeturn12view0turn32view0  
- 운영 산출물: “월간 오프사이트 배포 캘린더 + 링크 목록”  

### 11~13주: 리뷰 + 다음 분기 백로그
- 90일 동안의 AI Validator 로그를 요약해 “어떤 질문군에서 인용이 늘었는지” 정리  
- GSC/GA4에서 행동 지표(전환/이동률)를 함께 확인  
- 다음 분기 백로그: 성과가 좋았던 페이지 유형을 확장(예: 사례 허브에 산업별 상세 페이지 추가 등)

---

## 근거 목록 + Evidence Ledger

**(9) 근거 목록(Annotated Bibliography) + Evidence Ledger)**  
최소 15개 출처를 “무엇을 주장하는지(2줄) / 어디에 쓸 건지 / 신뢰도 / 날짜”로 정리한다.

### Annotated Bibliography (최소 15개)

1) GEO 논문(PDF): https://arxiv.org/pdf/2311.09735 (발행: 2024-06-28, KDD’24 표기: 2024-08)  
- 주장: 생성형 엔진에서의 가시성은 “인용/위치/분량” 같은 다차원이며, 특정 최적화(출처/인용문/통계)가 가시성 개선에 기여할 수 있다고 실험. citeturn36view1turn36view2  
- 사용처: “AI가 인용하는 이유/레버”, “실험 설계”, “콘텐츠 신호 설계”  
- 신뢰도: 1차(학술/ACM KDD proceedings)

2) Google AI features 문서: https://developers.google.com/search/docs/appearance/ai-features (업데이트일: 2025-12-10)  
- 주장: AI Overviews/AI Mode는 기존 SEO 기본기가 중요하며, 추가 최적화 요구사항은 없고 인덱싱/스니펫 가능이 전제. citeturn9view0  
- 사용처: “온사이트=필수 전제”, “측정(트래픽 포함)”  
- 신뢰도: 1차(공식 문서)

3) Google “How AI Overviews in Search work” PDF: https://www.google.com/search/howsearchworks/google-about-AI-overviews.pdf (발행: 2024-07)  
- 주장: AI Overviews는 링크로 더 알아볼 수 있게 하며, 기존 검색 품질/랭킹 시스템과 결합해 근거 기반 정보를 제공하려 한다고 설명. citeturn10view0  
- 사용처: “AI 인용/링크의 동기”, “변동성/트리거”  
- 신뢰도: 1차(공식 설명 문서)

4) Structured data 소개: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data (업데이트일: 2025-12-10)  
- 주장: 구조화데이터는 콘텐츠 이해에 도움. citeturn1view1  
- 사용처: “스키마 개념/원리”  
- 신뢰도: 1차(공식 문서)

5) Breadcrumb 문서: https://developers.google.com/search/docs/appearance/structured-data/breadcrumb (업데이트일: 2025-12-10)  
- 주장: Breadcrumb 구조화데이터 가이드 + 노출 보장 아님 같은 주의사항. citeturn2view0  
- 사용처: “BreadcrumbList 실습/오해 방지”  
- 신뢰도: 1차

6) Schema.org BreadcrumbList: https://schema.org/BreadcrumbList (릴리스 표기: 2025-12-08)  
- 주장: BreadcrumbList 타입/필드 정의 및 JSON-LD 예시 제공. citeturn3view0  
- 사용처: “구현 샘플/필드 정의”  
- 신뢰도: 1차(표준 커뮤니티)

7) Schema Markup Validator 발표: https://blog.schema.org/2021/05/21/announcing-schema-markup-validator-validator-schema-org-beta/ (발행: 2021-05-21)  
- 주장: Schema Markup Validator가 SDTT 후속으로 제공됨. citeturn29view1  
- 사용처: “검증 도구 역할 차이”  
- 신뢰도: 1차(표준/공식 블로그)

8) Schema.org validator 문서: https://schema.org/docs/validator.html (릴리스 표기: 2025-12-08)  
- 주장: validator의 기능/한계(스키마 중심, 구글 특화 아님). citeturn29view2  
- 사용처: “검증 도구 역할 차이”  
- 신뢰도: 1차

9) Google Search 기술 요건: https://developers.google.com/search/docs/essentials/technical (발행일: 미표기, 확인일: 2026-02-21 / 문서 내 표기: 기술 요건)  
- 주장: 차단 없음/200/인덱서블 콘텐츠가 최소 요건. citeturn23search3  
- 사용처: “Technical GEO L5”  
- 신뢰도: 1차

10) robots.txt 소개: https://developers.google.com/search/docs/crawling-indexing/robots/intro (발행일: 미표기, 확인일: 2026-02-21)  
- 주장: robots.txt는 주로 크롤링 제어이며 검색 제외 보안 수단이 아님. citeturn23search0  
- 사용처: “기술 접근성/오해 방지”  
- 신뢰도: 1차

11) Sitemap 개요: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview (업데이트일: 2025-12-10)  
- 주장: 사이트맵은 크롤링을 돕지만 크롤/인덱스를 보장하지 않음. citeturn23search2  
- 사용처: “기술 접근성(사이트맵)”  
- 신뢰도: 1차

12) Canonicalization 개요: https://developers.google.com/search/docs/crawling-indexing/canonicalization (업데이트일: 2025-12-10)  
- 주장: canonicalization은 대표 URL을 선택하는 과정이며, 중복 처리와 관련. citeturn22search1  
- 사용처: “UTM/중복 URL 처리”  
- 신뢰도: 1차

13) Link best practices: https://developers.google.com/search/docs/crawling-indexing/links-crawlable (발행일: 미표기, 확인일: 2026-02-21)  
- 주장: Google은 링크를 발견/관련성 신호로 사용하며, 크롤 가능한 링크/앵커텍스트를 권장. citeturn34search2  
- 사용처: “내부링크 설계(허브-클러스터)”  
- 신뢰도: 1차

14) Helpful content(사람-우선): https://developers.google.com/search/docs/fundamentals/creating-helpful-content (업데이트일: 2025-12-10)  
- 주장: 사람에게 유용한 신뢰성 있는 콘텐츠를 만들고 Who/How/Why를 점검하라고 안내. citeturn26view0  
- 사용처: “콘텐츠 신호/권위 신호 설계”  
- 신뢰도: 1차

15) Spam policies: https://developers.google.com/search/docs/essentials/spam-policies (업데이트일: 2025-12-10)  
- 주장: 스팸 행위/조작을 금지하고 위반 시 순위 하락/제외/매뉴얼 액션 가능. citeturn26view1  
- 사용처: “오프사이트 링크/스키마 오남용 리스크 관리”  
- 신뢰도: 1차

16) Search Quality Rater Guidelines overview(PDF): https://services.google.com/fh/files/misc/hsw-sqrg.pdf (발행일: 미표기/문서 내 개요, 확인일: 2026-02-21)  
- 주장: 평가에서 E‑E‑A‑T 같은 기준을 사용하지만, 개별 평가는 직접 랭킹을 바꾸지 않고 집계로 시스템 개선에 쓰인다는 취지. citeturn28view0turn28view1  
- 사용처: “권위/신뢰 신호의 개념적 프레임”  
- 신뢰도: 1차(공식 PDF)

17) Search Console branded filter 공지: https://developers.google.com/search/blog/2025/11/search-console-branded-filter (발행: 2025-11-20)  
- 주장: GSC에서 브랜디드/논브랜디드 쿼리를 분리해 분석 가능. citeturn37view0  
- 사용처: “Authority KPI 측정”  
- 신뢰도: 1차

18) GA4 recommended events: https://developers.google.com/analytics/devguides/collection/ga4/reference/events (업데이트일: 2026-02-18)  
- 주장: generate_lead 등 추천 이벤트 정의 제공. citeturn33view3  
- 사용처: “Behavior KPI의 표준 이벤트 설계”  
- 신뢰도: 1차

19) Perplexity help: https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work (업데이트: 상대 표기, 확인일: 2026-02-21)  
- 주장: 답변에 citations 포함, 웹 검색 후 요약. citeturn38view0  
- 사용처: “생성형 인용 메커니즘(플랫폼 문서 근거)”  
- 신뢰도: 1차(자사 문서)

### Evidence Ledger(표)

| Claim | Evidence(요약) | Source URL | Date | Confidence | Limitations |
|---|---|---|---|---|---|
| AI 기능 노출에 특별 최적화는 없고 기존 SEO 기본기가 중요 | Google 문서에 “no additional requirements / no special optimizations” 취지 명시 | https://developers.google.com/search/docs/appearance/ai-features | 2025-12-10 | High | Google 기준(타 플랫폼 일반화는 제한) citeturn9view0 |
| 생성형 엔진 가시성은 ‘인용/위치/분량’ 등 다차원 | GEO 논문에서 visibility metrics 제안 및 실험 | https://arxiv.org/pdf/2311.09735 | 2024-06-28 | High | 논문 실험 설정/벤치마크 한계 citeturn35view0turn36view1turn36view2 |
| 출처/인용문/통계 추가가 가시성 개선에 도움 될 수 있음 | GEO 논문에서 해당 방법들이 높은 성과로 보고 | https://arxiv.org/pdf/2311.09735 | 2024-06-28 | Med-High | 내 사이트/언어/도메인에 동일하게 적용된다는 보장은 없음 citeturn36view1turn36view2 |
| 구조화데이터는 리치리절트 노출을 보장하지 않음 | Breadcrumb 문서에서 노출 보장 아님 취지 안내 | https://developers.google.com/search/docs/appearance/structured-data/breadcrumb | 2025-12-10 | High | 문구 해석은 도구/상황에 따라 달라질 수 있음 citeturn2view0 |
| robots.txt는 검색 제외(보안) 수단이 아님 | robots.txt 소개 문서에서 noindex/비밀번호 언급 | https://developers.google.com/search/docs/crawling-indexing/robots/intro | (확인일) 2026-02-21 | High | 문서 업데이트일이 별도 표기되지 않을 수 있음 citeturn23search0 |
| 사이트맵은 크롤링을 돕지만 인덱싱을 보장하지 않음 | Sitemap overview 문서에 명시 | https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview | 2025-12-10 | High | 소규모 사이트는 이득이 제한적일 수 있음 citeturn23search2 |
| Google은 링크를 발견/관련성 신호로 사용 | Link best practices 문서에 명시 | https://developers.google.com/search/docs/crawling-indexing/links-crawlable | (확인일) 2026-02-21 | High | “얼마나” 영향은 쿼리/상황별 다름 citeturn34search2 |
| 일부 구조화데이터 타입 지원이 축소/중단될 수 있음 | Google Search Central Blog에서 phasing out 공지 | https://developers.google.com/search/blog/2025/06/simplifying-search-results | 2025-06-12 | High | 향후 추가 변경 가능 citeturn41view4 |
| Perplexity는 답변에 citations를 제공한다고 명시 | Perplexity Help Center 문서 | https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work | (상대 표기, 확인일) 2026-02-21 | Med | 업데이트가 상대 표기라 날짜 확정이 어려움 citeturn38view0 |

---

## 리서치 방법

**(6) 리서치 방법(How to Research) — 추천 검색 쿼리 20개 + 이유**  
요청 형식대로 “왜 검색하는지” 1줄씩 붙였다. (영문/국문 혼합)

1) `site:b2b.fastcampus.co.kr "structured data" OR schema`  
- 왜: 현재 사이트에 스키마 관련 흔적/문구/페이지가 이미 있는지 빠르게 점검

2) `site:b2b.fastcampus.co.kr service_custom breadcrumb JSON-LD`  
- 왜: service_custom에 BreadcrumbList 적용 시 참고할 기존 구현/패턴 확인

3) `site:b2b.fastcampus.co.kr refer_customer "목차" OR "앵커" OR "#"`  
- 왜: refer_customer에 이미 앵커/TOC가 있는지 확인(중복 작업 방지)

4) `site:b2b.fastcampus.co.kr resource_insight_aiforwork FAQ`  
- 왜: 인사이트 콘텐츠에 FAQ 패턴이 이미 있는지 확인

5) `"GEO" "Generative Engine Optimization" 2311.09735 key findings`  
- 왜: 논문 핵심 결과(어떤 최적화가 효과적인지) 재확인

6) `site:developers.google.com "AI features and your website" "no special optimizations"`  
- 왜: Google이 AI 기능에 대해 공식적으로 뭐라고 말하는지 원문 근거 확보

7) `Google Search Central query fan-out AI Overviews AI Mode`  
- 왜: query fan-out 같은 메커니즘 설명 근거 확보

8) `Google Search Central breadcrumb structured data requirements`  
- 왜: Breadcrumb 필수/권장 필드, 테스트 방법 확인

9) `Schema.org BreadcrumbList required properties position itemListElement`  
- 왜: 실제 JSON-LD 작성 시 필드 정의 확인

10) `Rich Results Test validate JSON-LD limitations comments`  
- 왜: Rich Results Test가 JSON-LD 코멘트를 무시하는 등 주의점 확인 citeturn5view2

11) `Schema Markup Validator validator.schema.org difference from Rich Results Test`  
- 왜: 두 도구의 역할 차이(구글 특화 vs 범용) 근거 확보 citeturn29view0turn29view2

12) `Google Search Central "structured data matches visible text"`  
- 왜: 스키마 오남용/불일치 리스크를 공식 근거로 정리 citeturn9view0

13) `Google Search technical requirements Googlebot blocked 200 indexable content`  
- 왜: Technical GEO의 최소 요건을 공식 문서로 확보 citeturn23search3

14) `Google Search Central robots.txt is not a mechanism for keeping a page out of Google`  
- 왜: robots.txt 오해(검색 제외) 바로잡기 citeturn23search0

15) `Google Search Central sitemaps "doesn't guarantee" crawled indexed`  
- 왜: 사이트맵 “보장 아님”을 근거로 명확히 하기 citeturn23search2

16) `Google Search Central link best practices crawlable links anchor text`  
- 왜: 내부링크/앵커텍스트 실무 규칙을 공식 근거로 정리 citeturn34search2

17) `Google canonicalization rel=canonical how to specify consolidate duplicate urls`  
- 왜: UTM/중복 URL 처리 기준 확보 citeturn22search8turn22search1

18) `Google JavaScript SEO basics rendering indexing`  
- 왜: JS 렌더링 의존이 강한 페이지의 리스크/대응 근거 확보 citeturn22search3

19) `GA4 URL builder utm_source utm_medium utm_campaign best practices`  
- 왜: b2b.fastcampus.co.kr 캠페인 측정(UTM) 표준화 근거 확보 citeturn32view0turn32view1

20) `b2b.fastcampus.co.kr service_custom utm_source=linkedin&utm_medium=social&utm_campaign=geo_test`  
- 왜: 실제 적용된 UTM 링크가 리디렉션/캐노니컬/중복 이슈를 만드는지 점검(직접 적용형)

---

## 품질 체크

**(8) 품질 체크(자기검수)**  
- [x] 용어 정의/비유/오해가 포함되었는가? (용어사전 표)  
- [x] 확실한 근거 vs 가설이 분리되었는가? (메커니즘 섹션 A/B)  
- [x] 온사이트/오프사이트/측정이 “연결된 하나의 시스템”으로 설명되었는가? (레버→플레이북→측정→실험→로드맵) citeturn35view0turn9view0  
- [x] 초보자가 따라할 실습 과제가 최소 5개 이상 있는가? (과제 1~4 + AI Validator 루틴 포함)  
- [x] 중요한 주장마다 URL+날짜가 있는가? (주요 공식 문서/논문/블로그에 날짜 표기, 날짜 미표기 문서는 확인일 표기)  
- [x] “예시”로 든 URL/페이지가 모두 b2b.fastcampus.co.kr 인가? (예시 URL은 모두 기준 페이지/UTM 변형 포함)