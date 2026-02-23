# Gemini groundingMetadata quick reference

핵심 필드:
- groundingMetadata.webSearchQueries[]: 모델이 실행한 검색 쿼리 목록
- groundingMetadata.searchEntryPoint.renderedContent: "Google Search suggestions" UI용 HTML/CSS (있으면 표시 요구사항 발생)
- groundingMetadata.groundingChunks[]: 출처 목록 (web.uri, web.title)
- groundingMetadata.groundingSupports[]: 텍스트 segment(startIndex/endIndex) → groundingChunkIndices 매핑

파서 구현 팁:
- groundingSupports를 endIndex 내림차순으로 정렬하면, 텍스트 삽입 시 인덱스 쉬프트를 피할 수 있음
- 노드(B)에서는 텍스트를 수정하기보단, citations 배열(세그먼트 범위 + sourceIds)로 별도 반환을 권장
