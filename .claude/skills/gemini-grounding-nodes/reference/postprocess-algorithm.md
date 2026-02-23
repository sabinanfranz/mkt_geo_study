# GroundingPostprocess deterministic algorithm

입력:
- answer_text (string)
- groundingMetadata (optional)

출력(권장):
- grounded (boolean)
- sources[]: { id, uri, title, domain }
- citations[]: { startIndex, endIndex, text, sourceIds[] }
- webSearchQueries[] (optional)
- searchEntryPointRenderedContent (optional)

규칙:
1) URL 정규화
- fragment(#...) 제거
- querystring은 기본 유지(제품 정책에 따라 옵션)
2) 중복 제거
- canonical uri 기준 dedupe
- 도메인 다양화: 같은 도메인 최대 N개(기본 2)로 캡
3) 인용 매핑
- groundingSupports[].segment (start/end/text) + groundingChunkIndices → sourceIds
- sourceIds는 sources[]의 id로 매핑
4) groundingMetadata 없음
- grounded=false, sources/citations/webSearchQueries 빈 배열
