"""Seed script — populate the database with GEO learning content.

Run with:  python -m apps.api.seed
"""

from __future__ import annotations

from apps.api.database import get_db, init_db


def seed(run_migrations: bool = True) -> None:
    if run_migrations:
        init_db()
    conn = get_db()
    step_type_by_id: dict[int, str] = {}
    option_buffer_by_step: dict[int, list[dict]] = {}

    # ------------------------------------------------------------------
    # Helpers (idempotent content upsert, preserving user progress)
    # ------------------------------------------------------------------
    def add_stage(stage_id, title, description, order_idx, unlock_condition):
        conn.execute(
            "INSERT INTO stages (id, title, description, order_idx, unlock_condition) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET "
            "title = excluded.title, "
            "description = excluded.description, "
            "order_idx = excluded.order_idx, "
            "unlock_condition = excluded.unlock_condition",
            (stage_id, title, description, order_idx, unlock_condition),
        )

    def add_module(stage_id, title, description, order_idx):
        existing = conn.execute(
            "SELECT id FROM modules WHERE stage_id = ? AND order_idx = ?",
            (stage_id, order_idx),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE modules SET title = ?, description = ? WHERE id = ?",
                (title, description, existing["id"]),
            )
            return existing["id"]

        conn.execute(
            "INSERT INTO modules (stage_id, title, description, order_idx) "
            "VALUES (?, ?, ?, ?)",
            (stage_id, title, description, order_idx),
        )
        return conn.execute(
            "SELECT id FROM modules WHERE stage_id = ? AND order_idx = ?",
            (stage_id, order_idx),
        ).fetchone()["id"]

    def add_step(module_id, step_type, title, content_md, order_idx, extension_md=None):
        existing = conn.execute(
            "SELECT id FROM steps WHERE module_id = ? AND order_idx = ?",
            (module_id, order_idx),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE steps SET "
                "type = ?, title = ?, content_md = ?, extension_md = ? "
                "WHERE id = ?",
                (step_type, title, content_md, extension_md, existing["id"]),
            )
            step_id = existing["id"]
            step_type_by_id[step_id] = step_type
            return step_id

        conn.execute(
            "INSERT INTO steps (module_id, type, title, content_md, order_idx, extension_md) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (module_id, step_type, title, content_md, order_idx, extension_md),
        )
        step_id = conn.execute(
            "SELECT id FROM steps WHERE module_id = ? AND order_idx = ?",
            (module_id, order_idx),
        ).fetchone()["id"]
        step_type_by_id[step_id] = step_type
        return step_id

    def add_option(step_id, label, content, is_correct, feedback_md, order_idx):
        buffered = option_buffer_by_step.setdefault(step_id, [])
        for opt in buffered:
            if opt["order_idx"] == order_idx:
                opt.update(
                    {
                        "label": label,
                        "content": content,
                        "is_correct": int(is_correct),
                        "feedback_md": feedback_md,
                    }
                )
                return

        buffered.append(
            {
                "label": label,
                "content": content,
                "is_correct": int(is_correct),
                "feedback_md": feedback_md,
                "order_idx": order_idx,
            }
        )

    def _rebalance_quiz_answer_labels() -> dict[str, int]:
        quiz_step_ids = sorted(
            step_id
            for step_id, step_type in step_type_by_id.items()
            if step_type == "quiz"
        )
        if not quiz_step_ids:
            return {"A": 0, "B": 0, "C": 0, "D": 0}

        total_quiz = len(quiz_step_ids)
        base, rem = divmod(total_quiz, 3)
        remaining_targets = {
            "A": base + (1 if rem > 0 else 0),
            "B": base + (1 if rem > 1 else 0),
            "C": base,
        }

        def _pick_next_correct_label() -> str:
            max_remaining = max(remaining_targets.values())
            for candidate in ("A", "B", "C"):
                if remaining_targets[candidate] == max_remaining:
                    return candidate
            return "A"

        for step_id in quiz_step_ids:
            options = option_buffer_by_step.get(step_id, [])
            if len(options) != 4:
                raise ValueError(
                    f"Quiz step {step_id} must have exactly 4 options, got {len(options)}"
                )

            correct_options = [o for o in options if o["is_correct"] == 1]
            if len(correct_options) != 1:
                raise ValueError(
                    f"Quiz step {step_id} must have exactly 1 correct option, got {len(correct_options)}"
                )

            correct_option = correct_options[0]
            target_label = _pick_next_correct_label()
            correct_option["label"] = target_label
            remaining_targets[target_label] -= 1

            incorrect_options = sorted(
                [o for o in options if o["is_correct"] == 0],
                key=lambda x: x["order_idx"],
            )
            remaining_labels = [l for l in ("A", "B", "C", "D") if l != target_label]
            for opt, label in zip(incorrect_options, remaining_labels):
                opt["label"] = label

            labels = sorted(o["label"] for o in options)
            if labels != ["A", "B", "C", "D"]:
                raise ValueError(f"Quiz step {step_id} labels must be A/B/C/D, got {labels}")

        counts = {"A": 0, "B": 0, "C": 0, "D": 0}
        for step_id in quiz_step_ids:
            options = option_buffer_by_step[step_id]
            correct = next(o for o in options if o["is_correct"] == 1)
            counts[correct["label"]] += 1
        return counts

    def _flush_option_buffer_to_db():
        for step_id in sorted(option_buffer_by_step):
            options = sorted(option_buffer_by_step[step_id], key=lambda x: x["order_idx"])
            for opt in options:
                existing = conn.execute(
                    "SELECT id FROM options WHERE step_id = ? AND order_idx = ?",
                    (step_id, opt["order_idx"]),
                ).fetchone()
                if existing:
                    conn.execute(
                        "UPDATE options SET "
                        "label = ?, content = ?, is_correct = ?, feedback_md = ? "
                        "WHERE id = ?",
                        (
                            opt["label"],
                            opt["content"],
                            opt["is_correct"],
                            opt["feedback_md"],
                            existing["id"],
                        ),
                    )
                else:
                    conn.execute(
                        "INSERT INTO options (step_id, label, content, is_correct, feedback_md, order_idx) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            step_id,
                            opt["label"],
                            opt["content"],
                            opt["is_correct"],
                            opt["feedback_md"],
                            opt["order_idx"],
                        ),
                    )

    # ------------------------------------------------------------------
    # Stages
    # ------------------------------------------------------------------
    add_stage(
        1,
        "GEO 세계관 이해",
        "생성형 AI 시대의 새로운 최적화 전략, GEO의 핵심 개념과 원리를 학습합니다.",
        1,
        None,
    )
    add_stage(
        2,
        "Technical GEO 기초 실습",
        "GEO 이론을 실무에 적용하기 위한 기술적 기초를 실습합니다.",
        2,
        '{"require_stage_complete": 1, "min_score_pct": 70}',
    )

    # ==================================================================
    # STAGE 1: GEO 세계관 이해
    # ==================================================================

    # --- Module 1-1: GEO란 무엇인가 ---
    m = add_module(1, "1-1: GEO란 무엇인가", "GEO의 정의와 등장 배경을 이해합니다.", 1)

    add_step(m, "reading", "GEO의 정의", (
        "## GEO란?\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>GEO</strong> (Generative Engine Optimization)<br>\n"
        "AI 챗봇이 답변할 때 내 콘텐츠를 인용하도록 최적화하는 전략</p>\n"
        "<p><strong>Citation</strong> (인용)<br>\n"
        'AI가 답변에서 "출처: 우리 사이트"라고 표시하는 것</p>\n'
        "<p><strong>LLM</strong> (Large Language Model, 대규모 언어모델)<br>\n"
        "ChatGPT, Claude, Gemini 같은 AI 엔진의 총칭</p>\n"
        "</div>\n\n"
        "**GEO(Generative Engine Optimization)**는 생성형 AI(ChatGPT, Claude, Gemini 등)가 "
        "답변을 생성할 때, 내 콘텐츠가 **인용 출처로 채택**되도록 최적화하는 전략입니다.\n\n"
        "### 핵심 포인트\n\n"
        "- 기존 SEO: 구글 검색 결과 상위 노출이 목표\n"
        "- GEO: AI 답변의 **근거(source)**로 선택되는 것이 목표\n"
        "- AI는 신뢰할 수 있는 콘텐츠를 우선 인용합니다\n\n"
        "### 왜 GEO가 중요한가?\n\n"
        "검색 사용자의 행동이 변하고 있습니다. 점점 더 많은 사람들이 구글 대신 AI에게 직접 질문합니다. "
        "이때 AI가 참고하는 출처에 우리 페이지가 포함되어야 합니다."
        '\n\n'
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">전통 검색 결과</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>광고 3개</li>\n'
        '<li>블로그 링크 10개</li>\n'
        '<li>사용자가 직접 클릭해서 정보를 찾아야 함</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card after">\n'
        '<div class="card-header">AI 답변 (GEO 적용)</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>질문에 대한 직접 답변 제공</li>\n'
        '<li><strong>출처: yoursite.com</strong> 인용 표시</li>\n'
        '<li>사용자가 바로 핵심 정보 획득</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '</div>'
    ), 1, extension_md=(
        "### 더 알아보기\n\n"
        "GEO라는 용어는 2023년 Georgia Tech, Princeton, IIT Delhi 등의 연구진이 발표한 논문 "
        "**\"GEO: Generative Engine Optimization\"**에서 처음 학술적으로 정의되었습니다. "
        "이 연구에서는 9가지 GEO 최적화 방법을 실험했으며, **인용 추가(Citation)**, "
        "**통계 데이터 포함(Statistics)**, **권위 있는 출처 인용(Quotation)**이 "
        "AI 답변에서 콘텐츠 가시성을 가장 크게 높이는 전략임을 밝혔습니다. "
        "기존 SEO가 20년 이상 발전해 온 것처럼, GEO도 향후 빠르게 진화할 분야입니다."
    ))

    s = add_step(m, "quiz", "GEO의 핵심 목표", (
        "다음 중 GEO(Generative Engine Optimization)의 **핵심 목표**로 가장 적절한 것은?"
    ), 2)
    add_option(s, "A", "키워드를 최대한 많이 삽입하는 것", 0,
               "키워드 스터핑은 SEO에서도 이미 비효율적인 전략입니다. GEO는 키워드가 아니라 콘텐츠의 신뢰성과 구조가 핵심입니다.", 1)
    add_option(s, "B", "생성형 AI가 답변 시 내 콘텐츠를 인용 출처로 채택하도록 최적화하는 것", 1,
               "정답입니다! GEO의 핵심은 AI가 답변을 만들 때 내 페이지가 '근거'로 채택되도록 최적화하는 것입니다.", 2)
    add_option(s, "C", "백링크를 최대한 많이 확보하는 것", 0,
               "백링크는 SEO에서 중요한 요소이지만, GEO에서는 콘텐츠 구조와 신뢰성이 더 중요합니다.", 3)
    add_option(s, "D", "웹사이트 로딩 속도를 최적화하는 것", 0,
               "로딩 속도는 기술적 SEO 요소입니다. GEO에서는 AI가 파싱하기 쉬운 콘텐츠 구조가 더 중요합니다.", 4)

    s = add_step(m, "quiz", "GEO가 필요한 이유", (
        "GEO가 중요해진 근본적인 이유는 무엇인가요?"
    ), 3, extension_md=(
        "### 참고 자료\n\n"
        "Gartner는 2025년까지 전통적 검색엔진 트래픽이 약 25% 감소할 것으로 예측했습니다. "
        "실제로 ChatGPT, Perplexity 등 AI 기반 검색의 월간 활성 사용자는 빠르게 증가하고 있으며, "
        "이는 콘텐츠 마케터들이 SEO와 함께 GEO 전략을 병행해야 하는 가장 큰 이유입니다. "
        "특히 B2B 시장에서는 의사결정자들이 AI를 통해 초기 리서치를 수행하는 비율이 높아지고 있어 "
        "GEO의 비즈니스 임팩트가 더욱 커지고 있습니다."
    ))
    add_option(s, "A", "구글 검색 알고리즘이 더 이상 업데이트되지 않아서", 0,
               "구글은 여전히 알고리즘을 업데이트하고 있습니다. GEO가 필요한 이유는 사용자 행동 변화 때문입니다.", 1)
    add_option(s, "B", "사용자들이 AI에게 직접 질문하는 검색 행동 변화가 일어나고 있어서", 1,
               "정답입니다! 점점 더 많은 사용자가 검색엔진 대신 AI에게 직접 질문하고 있으며, 이 트렌드가 GEO의 필요성을 만들었습니다.", 2)
    add_option(s, "C", "SEO가 완전히 사라졌기 때문에", 0,
               "SEO는 사라지지 않았습니다. GEO는 SEO를 대체하는 것이 아니라 보완하는 전략입니다.", 3)
    add_option(s, "D", "AI가 모든 웹사이트를 자동으로 인덱싱하기 때문에", 0,
               "AI는 모든 웹사이트를 자동 인덱싱하지 않습니다. AI는 학습 데이터와 검색을 통해 특정 출처를 선택합니다.", 4)

    # --- Module 1-2: SEO vs GEO 5가지 차이 ---
    m = add_module(1, "1-2: SEO vs GEO 5가지 차이", "SEO와 GEO의 핵심 차이점 5가지를 비교합니다.", 2)

    add_step(m, "reading", "SEO와 GEO 비교", (
        "## SEO vs GEO: 5가지 핵심 차이\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>SEO</strong> (Search Engine Optimization)<br>\n"
        "구글 검색 결과 상위에 노출되도록 최적화하는 전통적 방법</p>\n"
        "<p><strong>SERP</strong> (Search Engine Results Page)<br>\n"
        "구글에서 검색하면 나오는 결과 페이지</p>\n"
        "<p><strong>Organic Traffic</strong> (자연 유입)<br>\n"
        "광고 없이 검색이나 AI를 통해 자연스럽게 유입되는 방문자</p>\n"
        "</div>\n\n"
        '<div class="comparison-table">\n'
        '<div class="comp-header">SEO vs GEO 핵심 비교</div>\n'
        '<table>\n'
        '<thead><tr><th>구분</th><th>SEO</th><th>GEO</th></tr></thead>\n'
        '<tbody>\n'
        '<tr class="highlight"><td class="label">목표</td><td>검색 결과 상위 노출</td><td>AI 답변의 인용 출처 채택</td></tr>\n'
        '<tr><td class="label">대상 엔진</td><td>구글, 네이버 등 검색엔진</td><td>ChatGPT, Claude, Perplexity 등</td></tr>\n'
        '<tr><td class="label">핵심 신호</td><td>백링크, 키워드 밀도</td><td>콘텐츠 구조, 신뢰성, 명확성</td></tr>\n'
        '<tr><td class="label">측정 지표</td><td>순위, CTR, 트래픽</td><td>인용 빈도, 출처 채택률</td></tr>\n'
        '<tr><td class="label">콘텐츠 형태</td><td>키워드 중심 페이지</td><td>답변 가능한 구조화된 콘텐츠</td></tr>\n'
        '</tbody>\n'
        '</table>\n'
        '</div>\n\n'
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">SEO 핵심 요소</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>키워드 밀도 최적화</li>\n'
        '<li>백링크 수 확보</li>\n'
        '<li>메타 태그 최적화</li>\n'
        '<li>페이지 로딩 속도</li>\n'
        '<li>검색 순위 추적</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card after">\n'
        '<div class="card-header">GEO 핵심 요소</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>콘텐츠 구조화 (헤딩, 리스트)</li>\n'
        '<li>Answer-first 형식</li>\n'
        '<li>신뢰성 있는 출처 인용</li>\n'
        '<li>Schema Markup 적용</li>\n'
        '<li>AI 인용 빈도 추적</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n\n'
        "### 핵심 인사이트\n\n"
        "SEO는 '검색엔진의 눈'에 보이는 것이 목표라면, GEO는 'AI의 두뇌'에 신뢰할 수 있는 "
        "근거로 인식되는 것이 목표입니다. 두 전략은 상호 보완적입니다."
    ), 1)

    s = add_step(m, "quiz", "SEO와 GEO의 핵심 차이", (
        "SEO와 GEO의 가장 근본적인 차이는 무엇인가요?"
    ), 2)
    add_option(s, "A", "SEO는 무료이고 GEO는 유료이다", 0,
               "SEO와 GEO 모두 유/무료 방식이 혼합되어 있습니다. 차이의 핵심은 비용이 아닙니다.", 1)
    add_option(s, "B", "SEO는 검색엔진 상위 노출이, GEO는 AI 답변의 인용 출처 채택이 목표이다", 1,
               "정답입니다! SEO의 목표는 검색 결과 페이지에서의 순위이고, GEO의 목표는 AI가 답변을 구성할 때 내 콘텐츠를 근거로 사용하게 하는 것입니다.", 2)
    add_option(s, "C", "SEO는 텍스트만, GEO는 이미지만 최적화한다", 0,
               "두 전략 모두 텍스트와 다양한 미디어를 포괄합니다. 콘텐츠 형태의 차이가 핵심은 아닙니다.", 3)
    add_option(s, "D", "SEO는 한국에서만, GEO는 해외에서만 적용된다", 0,
               "SEO와 GEO 모두 전 세계에서 글로벌하게 적용됩니다. 특정 지역에 제한되는 전략이 아니며, 핵심 차이는 최적화 대상입니다.", 4)

    s = add_step(m, "quiz", "GEO에서 중요한 신호", (
        "GEO에서 SEO 대비 **더 중요해진** 신호는?"
    ), 3)
    add_option(s, "A", "백링크 수", 0,
               "백링크는 SEO에서 중요한 신호입니다. GEO에서는 콘텐츠 자체의 구조와 신뢰성이 더 중요합니다.", 1)
    add_option(s, "B", "콘텐츠의 구조화 정도와 신뢰성", 1,
               "정답입니다! AI는 잘 구조화되고 신뢰할 수 있는 콘텐츠를 우선적으로 인용합니다. 명확한 헤딩, 구조화된 데이터, 전문성 있는 내용이 핵심입니다.", 2)
    add_option(s, "C", "페이지 로딩 속도", 0,
               "페이지 속도는 기술적 SEO 요소입니다. GEO에서는 AI가 콘텐츠를 이해하고 인용할 수 있는지가 더 중요합니다.", 3)
    add_option(s, "D", "메타 태그의 길이", 0,
               "메타 태그는 검색엔진용 요소입니다. AI는 메타 태그보다 본문 콘텐츠의 품질과 구조를 중시합니다.", 4)

    # --- Module 1-3: AI가 인용하는 과정 (RAG 5단계) ---
    m = add_module(1, "1-3: AI가 인용하는 과정 (RAG 5단계)", "AI가 외부 콘텐츠를 검색하고 인용하는 RAG 파이프라인을 이해합니다.", 3)

    add_step(m, "reading", "RAG 파이프라인이란", (
        "## RAG(Retrieval-Augmented Generation) 5단계\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>RAG</strong> (Retrieval-Augmented Generation)<br>\n"
        "AI가 실시간으로 웹을 검색한 뒤 그 결과를 바탕으로 답변을 생성하는 방식</p>\n"
        "<p><strong>E-E-A-T</strong> (Experience, Expertise, Authoritativeness, Trustworthiness)<br>\n"
        "경험·전문성·권위·신뢰 — AI가 콘텐츠를 믿을지 판단하는 4가지 기준</p>\n"
        "<p><strong>Embedding</strong> (임베딩)<br>\n"
        "텍스트를 AI가 비교할 수 있는 숫자 벡터로 변환하는 기술</p>\n"
        "</div>\n\n"
        "AI가 답변을 생성할 때 외부 지식을 활용하는 과정을 **RAG**라고 합니다.\n\n"
        "### 5단계 프로세스\n\n"
        "1. **쿼리 이해**: 사용자의 질문 의도를 파악\n"
        "2. **검색(Retrieval)**: 관련 문서/페이지를 검색 엔진이나 벡터 DB에서 찾음\n"
        "3. **랭킹(Ranking)**: 검색된 문서 중 가장 관련성 높은 것을 순위 매김\n"
        "4. **컨텍스트 주입**: 선별된 문서를 AI의 프롬프트에 포함\n"
        "5. **답변 생성**: AI가 주입된 컨텍스트를 바탕으로 답변을 작성하고 출처를 인용\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">RAG 파이프라인 흐름도</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">쿼리 이해</div><div class="step-desc">사용자 질문의 의도를 파악합니다</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">검색 ★</div><div class="step-desc">관련 문서를 탐색합니다 — GEO 영향 구간</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">랭킹 ★</div><div class="step-desc">관련성 순위를 결정합니다 — GEO 영향 구간</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">컨텍스트 주입</div><div class="step-desc">선별된 문서를 프롬프트에 삽입합니다</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">5</div><div class="step-content"><div class="step-title">답변 생성</div><div class="step-desc">출처를 인용하여 최종 답변을 생성합니다</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'
        "### GEO 관점에서의 시사점\n\n"
        "우리 콘텐츠가 2단계(검색)에서 발견되고, 3단계(랭킹)에서 상위에 위치하며, "
        "5단계(생성)에서 정확히 인용되려면 콘텐츠의 구조와 명확성이 핵심입니다."
    ), 1, extension_md=(
        "### 심화 학습\n\n"
        "RAG 파이프라인을 더 깊이 이해하면 GEO 전략 수립에 큰 도움이 됩니다. "
        "특히 **2단계(검색)**에서는 벡터 임베딩(Vector Embedding) 기술이 활용되는데, "
        "이는 콘텐츠를 수학적 벡터로 변환하여 의미적 유사성을 비교하는 방식입니다. "
        "즉, 키워드가 정확히 일치하지 않아도 의미가 비슷하면 검색됩니다. "
        "이 때문에 GEO에서는 키워드 반복보다 **주제를 포괄적으로 다루는 것**이 중요합니다. "
        "Perplexity AI, Bing Chat 등 주요 AI 검색 엔진들이 RAG 방식을 사용하고 있습니다."
    ))

    s = add_step(m, "quiz", "RAG 파이프라인 순서", (
        "RAG 파이프라인의 올바른 순서는?"
    ), 2)
    add_option(s, "A", "답변 생성 -> 검색 -> 랭킹 -> 쿼리 이해 -> 컨텍스트 주입", 0,
               "순서가 잘못되었습니다. RAG는 사용자 쿼리 이해에서 시작하여 검색, 랭킹, 컨텍스트 주입, 답변 생성 순서로 진행됩니다.", 1)
    add_option(s, "B", "쿼리 이해 -> 검색 -> 랭킹 -> 컨텍스트 주입 -> 답변 생성", 1,
               "정답입니다! RAG는 쿼리 이해부터 시작하여 검색, 랭킹, 컨텍스트 주입을 거쳐 최종 답변을 생성합니다.", 2)
    add_option(s, "C", "검색 -> 쿼리 이해 -> 답변 생성 -> 랭킹 -> 컨텍스트 주입", 0,
               "검색 전에 쿼리 이해가 먼저 이루어져야 합니다. 올바른 순서를 다시 확인해 보세요.", 3)
    add_option(s, "D", "쿼리 이해 -> 답변 생성 -> 검색 -> 랭킹 -> 컨텍스트 주입", 0,
               "답변 생성은 RAG의 마지막 단계입니다. 검색과 랭킹이 먼저 이루어져야 합니다.", 4)

    s = add_step(m, "quiz", "GEO와 RAG의 관계", (
        "GEO 전략이 RAG 파이프라인에서 가장 직접적으로 영향을 미치는 단계는?"
    ), 3)
    add_option(s, "A", "1단계: 쿼리 이해", 0,
               "쿼리 이해는 AI 모델의 내부 프로세스로, 콘텐츠 제작자가 직접 영향을 미치기 어렵습니다.", 1)
    add_option(s, "B", "2단계(검색)와 3단계(랭킹)", 1,
               "정답입니다! GEO는 우리 콘텐츠가 검색에서 발견되고(2단계), 높은 순위를 받도록(3단계) 최적화하는 전략입니다.", 2)
    add_option(s, "C", "4단계: 컨텍스트 주입만", 0,
               "컨텍스트 주입은 AI 시스템이 수행하는 과정입니다. GEO는 그 이전 단계인 검색과 랭킹에 더 직접적으로 영향을 미칩니다.", 3)
    add_option(s, "D", "모든 단계에 동일하게 영향을 미친다", 0,
               "GEO가 모든 단계에 간접적으로 관련되지만, 가장 직접적인 영향은 검색과 랭킹 단계에 미칩니다.", 4)

    # --- Module 1-4: 5대 신호 카테고리 ---
    m = add_module(1, "1-4: 5대 신호 카테고리", "AI가 콘텐츠를 평가할 때 사용하는 5가지 핵심 신호를 학습합니다.", 4)

    add_step(m, "reading", "5대 신호 카테고리 개요", (
        "## AI가 콘텐츠를 평가하는 5대 신호\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Structured Data</strong> (구조화 데이터)<br>\n"
        "AI와 검색엔진이 콘텐츠를 정확히 이해하도록 정리한 코드 형식의 정보</p>\n"
        "<p><strong>Backlink</strong> (백링크)<br>\n"
        "다른 사이트가 우리 사이트를 링크로 추천하는 것</p>\n"
        "<p><strong>Entity</strong> (엔터티)<br>\n"
        "검색엔진과 AI가 인식하는 고유한 개체 — 사람, 기업, 장소, 제품 등</p>\n"
        "</div>\n\n"
        "### 1. 권위성 (Authority)\n"
        "- 저자의 전문성, 사이트의 신뢰도\n"
        "- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)\n\n"
        "### 2. 구조화 (Structure)\n"
        "- 명확한 헤딩 계층 (H1 > H2 > H3)\n"
        "- 리스트, 테이블 등 파싱하기 쉬운 형태\n\n"
        "### 3. 명확성 (Clarity)\n"
        "- 질문에 대한 직접적인 답변 (Answer-first)\n"
        "- 모호함 없는 명확한 서술\n\n"
        "### 4. 독창성 (Originality)\n"
        "- 고유한 데이터, 사례, 분석\n"
        "- 다른 소스에서 찾을 수 없는 인사이트\n\n"
        "### 5. 최신성 (Freshness)\n"
        "- 최근 업데이트된 콘텐츠\n"
        "- 날짜가 명시된 정보\n\n"
        "이 5가지 신호를 모두 강화하면 AI가 우리 콘텐츠를 인용할 확률이 높아집니다."
        '\n\n'
        '<div class="pyramid-chart">\n'
        '<div class="pyramid-title">GEO 5대 신호 피라미드</div>\n'
        '<div class="pyramid-body">\n'
        '<div class="pyramid-level" style="--level: 1; --total: 5;"><span class="pyramid-label">독창성</span><span class="pyramid-detail">고유 데이터/분석</span></div>\n'
        '<div class="pyramid-level" style="--level: 2; --total: 5;"><span class="pyramid-label">권위성</span><span class="pyramid-detail">E-E-A-T, 전문성</span></div>\n'
        '<div class="pyramid-level" style="--level: 3; --total: 5;"><span class="pyramid-label">최신성</span><span class="pyramid-detail">날짜 명시, 업데이트</span></div>\n'
        '<div class="pyramid-level" style="--level: 4; --total: 5;"><span class="pyramid-label">명확성</span><span class="pyramid-detail">Answer-first, 직접 답변</span></div>\n'
        '<div class="pyramid-level" style="--level: 5; --total: 5;"><span class="pyramid-label">구조화</span><span class="pyramid-detail">헤딩, 리스트, 테이블</span></div>\n'
        '</div>\n'
        '</div>\n'
        '\n'
        '<div class="callout tip">\n'
        '<p><strong>실전 팁:</strong> 구조화와 명확성은 즉시 개선 가능한 영역입니다. 피라미드 하단부터 위로 올라가며 순서대로 개선하세요.</p>\n'
        '</div>'
    ), 1, extension_md=(
        "### 더 알아보기\n\n"
        "5대 신호 중 실무에서 가장 빠르게 개선할 수 있는 것은 **구조화**와 **명확성**입니다. "
        "반면, **권위성**과 **독창성**은 시간이 걸리는 장기 투자 영역입니다. "
        "Google의 Search Quality Evaluator Guidelines에서도 E-E-A-T를 강조하는데, "
        "이는 AI 검색 엔진에서도 동일하게 적용됩니다. 특히 YMYL(Your Money, Your Life) 주제 "
        "(금융, 건강, 법률 등)에서는 권위성 신호가 더욱 중요하게 작용합니다. "
        "자사 콘텐츠의 현재 상태를 5대 신호 기준으로 점검해 보면 우선순위가 명확해집니다."
    ))

    s = add_step(m, "quiz", "가장 중요한 신호", (
        "다음 중 GEO에서 '구조화(Structure)' 신호에 해당하는 것은?"
    ), 2)
    add_option(s, "A", "저자의 학력과 경력을 상세히 기재하는 것", 0,
               "이것은 '권위성(Authority)' 신호에 해당합니다. 구조화는 콘텐츠의 형식적 구조를 의미합니다.", 1)
    add_option(s, "B", "명확한 헤딩 계층과 리스트, 테이블을 활용하여 콘텐츠를 정리하는 것", 1,
               "정답입니다! 구조화 신호는 AI가 콘텐츠를 파싱하기 쉽게 헤딩, 리스트, 테이블 등으로 정보를 체계적으로 배치하는 것입니다.", 2)
    add_option(s, "C", "매일 콘텐츠를 업데이트하는 것", 0,
               "이것은 '최신성(Freshness)' 신호에 해당합니다. 구조화는 콘텐츠 형식에 관한 것입니다.", 3)
    add_option(s, "D", "독자적인 연구 데이터를 포함하는 것", 0,
               "이것은 '독창성(Originality)' 신호에 해당합니다. 구조화와는 다른 카테고리입니다.", 4)

    s = add_step(m, "quiz", "5대 신호 적용", (
        "블로그 글에 '2025년 1월 업데이트'라고 날짜를 명시하는 것은 어떤 신호를 강화하는 전략인가요?"
    ), 3)
    add_option(s, "A", "권위성 (Authority)", 0,
               "권위성은 저자의 전문성이나 사이트 신뢰도와 관련됩니다. 날짜 명시는 다른 신호에 해당합니다.", 1)
    add_option(s, "B", "구조화 (Structure)", 0,
               "구조화는 헤딩, 리스트, 테이블 등 콘텐츠의 형식적 배치에 관한 것이며, 날짜 명시와는 다른 카테고리입니다.", 2)
    add_option(s, "C", "최신성 (Freshness)", 1,
               "정답입니다! 날짜를 명시하는 것은 콘텐츠가 최근에 업데이트되었음을 AI에게 알려주는 '최신성' 신호입니다.", 3)
    add_option(s, "D", "독창성 (Originality)", 0,
               "독창성은 고유한 데이터나 인사이트를 제공하는 것과 관련됩니다. 날짜 명시는 최신성 신호에 해당하므로 구분이 필요합니다.", 4)

    # --- Module 1-5: 3층 KPI 프레임워크 ---
    m = add_module(1, "1-5: 3층 KPI 프레임워크", "GEO 성과를 측정하는 3단계 KPI 체계를 학습합니다.", 5)

    add_step(m, "reading", "3층 KPI 프레임워크", (
        "## GEO 성과 측정: 3층 KPI\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>KPI</strong> (Key Performance Indicator)<br>\n"
        "목표 달성 여부를 숫자로 측정하는 핵심 성과 지표</p>\n"
        "<p><strong>Visibility</strong> (가시성)<br>\n"
        "AI 답변이나 검색 결과에 우리 콘텐츠가 얼마나 자주 보이는지</p>\n"
        "<p><strong>Conversion</strong> (전환)<br>\n"
        "방문자가 실제 고객 행동(문의, 가입, 구매)을 하는 것</p>\n"
        "<p><strong>CTR</strong> (Click-Through Rate, 클릭률)<br>\n"
        "노출된 횟수 중 실제 클릭한 비율</p>\n"
        "</div>\n\n"
        "GEO의 효과를 측정하려면 기존 SEO 지표와 다른 체계가 필요합니다.\n\n"
        "### Layer 1: 가시성 지표 (Visibility)\n"
        "- AI 답변에서 브랜드/URL 인용 횟수\n"
        "- 경쟁사 대비 인용 점유율(Share of Voice)\n"
        "- Perplexity, Bing Chat 등에서의 출현 빈도\n\n"
        "### Layer 2: 참여 지표 (Engagement)\n"
        "- AI 답변 내 링크를 통한 유입 트래픽\n"
        "- AI 경유 사용자의 체류 시간, 페이지뷰\n"
        "- 전환율 (AI 트래픽 vs 검색 트래픽)\n\n"
        "### Layer 3: 비즈니스 지표 (Business Impact)\n"
        "- AI 채널을 통한 리드 생성, 매출\n"
        "- 브랜드 인지도 변화\n"
        "- 고객 획득 비용(CAC) 비교\n\n"
        "단계별로 측정하면 GEO 투자의 ROI를 명확히 파악할 수 있습니다."
        '\n\n'
        '<div class="layer-box">\n'
        '<div class="layer-title">GEO KPI 3층 프레임워크</div>\n'
        '<div class="layer" style="--layer-color: #ea4335;"><div class="layer-label">Layer 3: Business Impact</div><div class="layer-desc">매출, 리드, CAC (고객 획득 비용)</div></div>\n'
        '<div class="layer-connector">↕</div>\n'
        '<div class="layer" style="--layer-color: #fbbc04;"><div class="layer-label">Layer 2: Engagement</div><div class="layer-desc">트래픽, 체류시간, 전환율</div></div>\n'
        '<div class="layer-connector">↕</div>\n'
        '<div class="layer" style="--layer-color: #34a853;"><div class="layer-label">Layer 1: Visibility</div><div class="layer-desc">AI 인용 횟수, Share of Voice — 측정은 여기부터 시작하세요</div></div>\n'
        '</div>'
    ), 1)

    s = add_step(m, "quiz", "KPI Layer 구분", (
        "'AI 답변에서 우리 브랜드가 언급된 횟수'는 3층 KPI 중 어느 Layer에 해당하나요?"
    ), 2)
    add_option(s, "A", "Layer 1: 가시성 지표", 1,
               "정답입니다! 브랜드 인용 횟수는 AI에서의 가시성을 직접 측정하는 Layer 1 지표입니다.", 1)
    add_option(s, "B", "Layer 2: 참여 지표", 0,
               "참여 지표는 AI를 통한 트래픽, 체류 시간 등 사용자 행동을 측정합니다. 인용 횟수는 가시성 지표입니다.", 2)
    add_option(s, "C", "Layer 3: 비즈니스 지표", 0,
               "비즈니스 지표(Layer 3)는 매출, 리드 생성 등 최종 비즈니스 성과를 측정하며, 인용 횟수는 가시성 지표(Layer 1)에 해당합니다.", 3)
    add_option(s, "D", "어느 Layer에도 해당하지 않는다", 0,
               "브랜드 인용 횟수는 명확히 Layer 1(가시성 지표)에 해당합니다. 3층 KPI 프레임워크에서 각 지표의 계층을 구분하는 것이 중요합니다.", 4)

    s = add_step(m, "quiz", "KPI 프레임워크 활용", (
        "3층 KPI 프레임워크에서 Layer 2(참여 지표)에 해당하는 것은?"
    ), 3)
    add_option(s, "A", "AI 답변에서의 브랜드 인용 횟수", 0,
               "이것은 Layer 1(가시성 지표)에 해당합니다. Layer 2는 사용자 행동 관련 지표입니다.", 1)
    add_option(s, "B", "AI 답변 내 링크를 통한 유입 트래픽과 체류 시간", 1,
               "정답입니다! AI를 경유하여 유입된 트래픽, 체류 시간, 페이지뷰 등은 Layer 2(참여 지표)입니다.", 2)
    add_option(s, "C", "AI 채널을 통한 매출 증가", 0,
               "매출 증가는 Layer 3(비즈니스 지표)에 해당합니다. Layer 2는 트래픽, 체류 시간 등 사용자 참여 행동을 측정하는 지표입니다.", 3)
    add_option(s, "D", "경쟁사 대비 인용 점유율", 0,
               "인용 점유율(Share of Voice)은 Layer 1(가시성 지표)에 해당합니다. Layer 2 참여 지표와 혼동하지 않도록 주의하세요.", 4)

    # --- Module 1-6: 확실한 근거 vs 가설 ---
    m = add_module(1, "1-6: 확실한 근거 vs 가설", "GEO에서 검증된 사실과 아직 가설 단계인 전략을 구분합니다.", 6)

    add_step(m, "reading", "근거 vs 가설 구분하기", (
        "## GEO: 확실한 근거 vs 가설\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>SSR / CSR</strong> (Server-Side / Client-Side Rendering)<br>\n"
        "서버가 완성된 HTML을 보내줌(SSR) vs 브라우저가 JavaScript로 직접 화면 조립(CSR)</p>\n"
        "<p><strong>Canonical URL</strong> (정규 URL)<br>\n"
        '"이 페이지가 원본입니다"라고 검색엔진에 알려주는 태그</p>\n'
        "<p><strong>Meta Description</strong> (메타 설명)<br>\n"
        "검색 결과에서 제목 아래 표시되는 페이지 요약 설명문</p>\n"
        "</div>\n\n"
        "GEO는 아직 발전 중인 분야이므로, 검증된 사실과 가설을 구분하는 것이 중요합니다.\n\n"
        "### 확실한 근거 (Evidence-based)\n"
        "- AI는 구조화된 콘텐츠를 더 잘 파싱한다\n"
        "- Answer-first 형식이 인용 확률을 높인다\n"
        "- E-E-A-T 신호가 강한 콘텐츠가 더 자주 인용된다\n"
        "- Schema markup이 AI의 콘텐츠 이해를 돕는다\n\n"
        "### 가설 단계 (Hypothesis)\n"
        "- 특정 키워드 패턴이 AI 인용을 높인다\n"
        "- SNS 공유가 AI 인용에 영향을 미친다\n"
        "- 콘텐츠 길이와 인용률의 상관관계\n"
        "- AI별(ChatGPT vs Claude) 최적화 전략 차이\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">확실한 근거 (Proven)</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>구조화된 콘텐츠 → AI 파싱 향상</li>\n'
        '<li>Answer-first → 인용 확률 증가</li>\n'
        '<li>E-E-A-T → 신뢰성 신호 강화</li>\n'
        '<li>Schema Markup → 기계 이해도 향상</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card after">\n'
        '<div class="card-header">가설 단계 (Hypothesis)</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>특정 키워드 패턴 → AI 인용 영향?</li>\n'
        '<li>SNS 공유 → AI 인용 관계?</li>\n'
        '<li>콘텐츠 길이 → 인용률 상관관계?</li>\n'
        '<li>AI별 최적화 전략 차이?</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n\n'
        "### 왜 구분이 중요한가?\n\n"
        "가설을 확실한 전략처럼 실행하면 리소스를 낭비할 수 있습니다. "
        "근거 기반 전략부터 우선 적용하고, 가설은 테스트하며 검증해야 합니다."
    ), 1, extension_md=(
        "### 실전 팁\n\n"
        "가설을 검증하는 가장 효과적인 방법은 **A/B 테스트**입니다. "
        "예를 들어, 동일한 주제의 페이지 두 개를 다른 구조로 작성한 뒤 "
        "각각 ChatGPT와 Perplexity에 관련 질문을 하여 어떤 페이지가 더 자주 인용되는지 비교합니다. "
        "또한, GEO 분야는 AI 모델의 업데이트 주기(보통 3~6개월)에 따라 "
        "유효한 전략이 바뀔 수 있으므로 주기적인 재검증이 필요합니다. "
        "현재 근거로 인정되는 전략도 AI 모델이 바뀌면 가설로 돌아갈 수 있음을 기억하세요."
    ))

    s = add_step(m, "quiz", "근거 vs 가설 판별", (
        "다음 중 GEO에서 **확실한 근거**로 분류되는 것은?"
    ), 2)
    add_option(s, "A", "SNS에서 많이 공유된 콘텐츠가 AI에 더 자주 인용된다", 0,
               "SNS 공유와 AI 인용의 직접적 관계는 아직 검증되지 않은 가설 단계입니다. 근거 기반 전략인 콘텐츠 구조화를 우선 적용하세요.", 1)
    add_option(s, "B", "구조화된 콘텐츠(헤딩, 리스트)가 AI에 더 잘 파싱되어 인용 확률이 높아진다", 1,
               "정답입니다! AI가 구조화된 콘텐츠를 더 잘 파싱한다는 것은 다수의 연구와 실험으로 검증된 사실입니다.", 2)
    add_option(s, "C", "글의 길이가 3,000자 이상이면 인용률이 높아진다", 0,
               "콘텐츠 길이와 인용률의 직접적 상관관계는 아직 가설 단계입니다. 길이보다는 콘텐츠의 구조화와 명확성이 더 중요한 검증된 요소입니다.", 3)
    add_option(s, "D", "ChatGPT와 Claude는 완전히 다른 최적화 전략이 필요하다", 0,
               "ChatGPT와 Claude 등 AI별 최적화 전략의 차이는 아직 체계적으로 검증되지 않은 가설입니다. 공통 원칙인 구조화부터 적용하세요.", 4)

    s = add_step(m, "quiz", "가설 검증 접근법", (
        "GEO에서 가설 단계의 전략을 다루는 올바른 접근법은?"
    ), 3)
    add_option(s, "A", "가설은 무시하고 근거 기반 전략만 실행한다", 0,
               "가설을 완전히 무시하면 새로운 기회를 놓칠 수 있습니다. 체계적으로 테스트하는 것이 바람직합니다.", 1)
    add_option(s, "B", "근거 기반 전략을 우선 적용하고, 가설은 체계적으로 테스트하며 검증한다", 1,
               "정답입니다! 근거가 확실한 전략을 먼저 실행하고, 가설은 A/B 테스트 등으로 검증해 나가는 것이 효율적입니다.", 2)
    add_option(s, "C", "모든 가설을 동시에 실행하여 빠르게 검증한다", 0,
               "모든 가설을 동시에 실행하면 어떤 전략이 효과가 있었는지 파악하기 어렵습니다.", 3)
    add_option(s, "D", "업계 전문가의 의견을 따라 가설을 사실로 받아들인다", 0,
               "전문가 의견도 데이터로 검증해야 합니다. GEO는 빠르게 변화하는 분야이므로 실험이 중요합니다.", 4)

    # --- Module 1-7: 전문가 시연 관찰 (모델링) ---
    m = add_module(1, "1-7: 전문가 시연 관찰", "전문가의 GEO 적용 사례를 관찰하고 패턴을 학습합니다.", 7)

    add_step(m, "reading", "전문가의 GEO 적용 과정", (
        "## 전문가 시연: GEO 적용 워크플로\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Open Graph</strong> (오픈 그래프)<br>\n"
        "카카오톡·슬랙 등에 링크 공유 시 미리보기에 표시되는 정보를 지정하는 태그</p>\n"
        "<p><strong>Semantic HTML</strong> (시맨틱 HTML)<br>\n"
        "의미를 가진 HTML 태그(header, article, nav 등)로 문서 구조를 명확히 하는 것</p>\n"
        "</div>\n\n"
        "실제 전문가가 콘텐츠를 GEO 최적화하는 과정을 관찰해봅시다.\n\n"
        "### Step 1: 타겟 쿼리 선정\n"
        "- AI에 자주 질문되는 주제를 파악\n"
        "- 예: \"GEO란 무엇인가?\", \"SEO와 GEO의 차이\"\n\n"
        "### Step 2: 현재 AI 응답 분석\n"
        "- ChatGPT, Claude에 질문하여 현재 어떤 출처가 인용되는지 확인\n"
        "- 인용되는 콘텐츠의 공통 특성 분석\n\n"
        "### Step 3: 콘텐츠 구조 재설계\n"
        "- Answer-first 형식으로 핵심 답변을 문서 상단에 배치\n"
        "- 명확한 헤딩 계층 적용 (H1 > H2 > H3)\n"
        "- FAQ 섹션 추가\n\n"
        "### Step 4: 신뢰성 강화\n"
        "- 데이터와 출처 인용 추가\n"
        "- 저자 프로필과 전문성 명시\n\n"
        "### Step 5: 모니터링\n"
        "- 정기적으로 AI에 질문하여 인용 여부 확인\n"
        "- 인용되지 않으면 콘텐츠를 추가 개선"
        '\n\n'
        '<div class="browser-mockup">\n'
        '<div class="browser-bar">\n'
        '<span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>\n'
        '<span class="browser-url">b2b.fastcampus.co.kr/service_custom</span>\n'
        '</div>\n'
        '<div class="browser-body">\n'
        '<div class="page-title">크롤링 진단 결과 (AI 봇 관점)</div>\n'
        '<div class="page-element missing">Title 태그 — 없음</div>\n'
        '<div class="page-element missing">Meta Description — 없음</div>\n'
        '<div class="page-element missing">H1 태그 — 없음</div>\n'
        '<div class="page-element missing">구조화 데이터 — 없음</div>\n'
        '<div class="page-element missing">Canonical URL — 없음</div>\n'
        '<div class="page-element present">본문 텍스트 — 244자 (CSR 렌더링)</div>\n'
        '<div class="page-element missing">Open Graph 태그 — 없음</div>\n'
        '</div>\n'
        '</div>\n'
        '\n'
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">CSR 페이지 (6/10개) — 0점</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>봇에게 빈 페이지로 보임 (244자)</li>\n'
        '<li>H1, 스키마, 메타 태그 전무</li>\n'
        '<li>AI 인용 가능성: 거의 없음</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card after">\n'
        '<div class="card-header">SSR 인사이트 페이지 (4/10개) — A등급</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>H1 + H2 헤딩 구조 완비</li>\n'
        '<li>4,000자+ 본문 콘텐츠</li>\n'
        '<li>Schema Markup 적용 (Course)</li>\n'
        '<li>AI 인용 가능성: 높음</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '</div>'
    ), 1, extension_md=(
        "### 크롤링 데이터 해석\n\n"
        "위 진단 결과는 b2b.fastcampus.co.kr의 실제 크롤링 데이터입니다. "
        "6/10 페이지가 CSR(Client-Side Rendering)으로 구축되어 봇에게는 빈 페이지로 보입니다. "
        "반면, SSR로 구축된 인사이트 페이지 4개는 H1, 구조화 데이터, 충분한 본문 텍스트를 갖추고 있어 "
        "AI 인용 가능성이 높습니다. 이러한 Before/After 비교는 GEO 전략의 효과를 직관적으로 보여줍니다."
    ))

    s = add_step(m, "quiz", "전문가 워크플로 순서", (
        "GEO 최적화 워크플로에서 '현재 AI 응답 분석'은 몇 번째 단계인가요?"
    ), 2)
    add_option(s, "A", "1번째 (가장 먼저)", 0,
               "가장 먼저 해야 할 것은 타겟 쿼리를 선정하는 것입니다. AI 응답 분석은 그 다음입니다.", 1)
    add_option(s, "B", "2번째 (타겟 쿼리 선정 이후)", 1,
               "정답입니다! 먼저 타겟 쿼리를 선정한 뒤, 해당 쿼리에 대한 현재 AI 응답을 분석하는 것이 올바른 순서입니다.", 2)
    add_option(s, "C", "4번째 (콘텐츠 재설계 이후)", 0,
               "콘텐츠를 재설계하기 전에 현재 AI 응답 상태를 먼저 파악해야 합니다. 타겟 쿼리 선정 직후 2번째 단계로 분석을 수행합니다.", 3)
    add_option(s, "D", "5번째 (마지막)", 0,
               "마지막 5번째 단계는 모니터링입니다. AI 응답 분석은 타겟 쿼리 선정 직후인 2번째 초기 단계에서 수행해야 합니다.", 4)

    s = add_step(m, "quiz", "Answer-first 원칙", (
        "전문가가 콘텐츠 구조를 재설계할 때 'Answer-first' 형식을 사용하는 이유는?"
    ), 3)
    add_option(s, "A", "글이 짧아져서 사용자가 빨리 읽을 수 있기 때문에", 0,
               "Answer-first는 글의 길이를 줄이는 것이 아니라 핵심 답변을 상단에 배치하는 전략입니다.", 1)
    add_option(s, "B", "AI가 문서 상단의 핵심 답변을 인용할 가능성이 높기 때문에", 1,
               "정답입니다! AI는 문서 상단에 명확하게 제시된 답변을 인용하는 경향이 있습니다. Answer-first 구조는 AI 인용 확률을 높입니다.", 2)
    add_option(s, "C", "SEO 키워드를 상단에 집중시킬 수 있기 때문에", 0,
               "Answer-first의 목적은 키워드 배치가 아니라 핵심 답변을 먼저 제공하는 것입니다.", 3)
    add_option(s, "D", "구글 검색 결과에서 스니펫으로 노출되기 위해서", 0,
               "구글 스니펫도 부수적 효과일 수 있지만, GEO 관점에서 Answer-first의 핵심 이유는 AI 인용률 향상입니다.", 4)

    # --- Module 1-8: Stage 1 종합 평가 (quiz only, 5 steps) ---
    m = add_module(1, "1-8: Stage 1 종합 평가", "Stage 1에서 학습한 내용을 종합적으로 평가합니다.", 8)

    s = add_step(m, "quiz", "종합 Q1: GEO 정의", (
        "GEO(Generative Engine Optimization)에 대한 설명으로 **가장 정확한** 것은?"
    ), 1)
    add_option(s, "A", "검색엔진에서 광고를 최적화하는 기법", 0,
               "GEO는 광고 최적화가 아니라 생성형 AI에서 콘텐츠가 인용되도록 하는 전략입니다.", 1)
    add_option(s, "B", "생성형 AI가 답변 시 내 콘텐츠를 인용 출처로 채택하도록 최적화하는 전략", 1,
               "정답입니다! GEO의 핵심 정의를 정확히 이해하고 있습니다. AI 답변의 인용 출처로 채택되는 것이 GEO의 궁극적 목표입니다.", 2)
    add_option(s, "C", "웹사이트의 디자인을 AI가 좋아하는 스타일로 바꾸는 것", 0,
               "GEO는 디자인이 아니라 콘텐츠의 구조, 신뢰성, 명확성을 최적화하는 것입니다.", 3)
    add_option(s, "D", "AI 챗봇을 웹사이트에 설치하는 것", 0,
               "AI 챗봇 설치는 사용자 인터페이스 기능이며, GEO의 핵심인 콘텐츠 구조화 및 신뢰성 최적화와는 관련이 없는 전략입니다.", 4)

    s = add_step(m, "quiz", "종합 Q2: SEO vs GEO", (
        "SEO와 GEO의 차이에 대한 설명으로 **올바른** 것은?"
    ), 2)
    add_option(s, "A", "SEO는 더 이상 필요하지 않고 GEO로 완전히 대체되었다", 0,
               "SEO는 여전히 중요합니다. GEO는 SEO를 대체하는 것이 아니라 보완하는 전략입니다.", 1)
    add_option(s, "B", "SEO와 GEO의 목표는 완전히 동일하다", 0,
               "SEO의 목표는 검색 결과 순위 향상이고, GEO의 목표는 AI 답변에서 인용 출처로 채택되는 것으로, 최적화 대상이 근본적으로 다릅니다.", 2)
    add_option(s, "C", "SEO는 검색엔진 순위를, GEO는 AI 답변의 인용 출처 채택을 목표로 한다", 1,
               "정답입니다! SEO는 검색엔진 순위를, GEO는 AI 인용 출처 채택을 목표로 한다는 핵심 차이를 정확히 파악했습니다.", 3)
    add_option(s, "D", "GEO는 SEO보다 항상 비용이 많이 든다", 0,
               "비용은 상황에 따라 다릅니다. 핵심 차이는 비용이 아니라 최적화 대상의 차이입니다.", 4)

    s = add_step(m, "quiz", "종합 Q3: RAG 파이프라인", (
        "RAG 파이프라인에서 GEO가 가장 큰 영향을 미치는 단계는?"
    ), 3)
    add_option(s, "A", "쿼리 이해 단계", 0,
               "쿼리 이해는 AI 내부 프로세스로, 콘텐츠 제작자가 직접 영향을 미치기 어렵습니다.", 1)
    add_option(s, "B", "검색(Retrieval)과 랭킹(Ranking) 단계", 1,
               "정답입니다! GEO는 콘텐츠가 검색에서 발견되고 높은 순위를 받도록 최적화하는 전략입니다.", 2)
    add_option(s, "C", "답변 생성 단계만", 0,
               "답변 생성 단계는 AI가 수행하는 과정으로, 콘텐츠 최적화로 간접적으로만 영향을 미칩니다.", 3)
    add_option(s, "D", "컨텍스트 주입 단계만", 0,
               "컨텍스트 주입은 AI 시스템이 수행합니다. GEO는 그 이전 단계에 더 직접적으로 영향을 미칩니다.", 4)

    s = add_step(m, "quiz", "종합 Q4: 5대 신호", (
        "GEO 5대 신호 중 '콘텐츠에 고유한 데이터와 사례를 포함하는 것'은 어떤 신호에 해당하나요?"
    ), 4)
    add_option(s, "A", "권위성 (Authority)", 0,
               "권위성은 저자의 전문성과 사이트의 신뢰도에 관한 신호입니다. 고유한 데이터 포함은 독창성(Originality) 카테고리에 해당합니다.", 1)
    add_option(s, "B", "구조화 (Structure)", 0,
               "구조화는 헤딩, 리스트, 테이블 등 콘텐츠의 형식적 구조에 관한 것입니다. 고유 데이터 포함은 독창성(Originality) 신호입니다.", 2)
    add_option(s, "C", "독창성 (Originality)", 1,
               "정답입니다! 고유한 데이터, 사례, 분석을 포함하는 것은 독창성 신호를 강화하는 전략입니다.", 3)
    add_option(s, "D", "최신성 (Freshness)", 0,
               "최신성은 콘텐츠의 업데이트 시점과 날짜 명시에 관한 신호입니다. 고유 데이터 제공은 독창성(Originality)에 해당합니다.", 4)

    s = add_step(m, "quiz", "종합 Q5: 근거 vs 가설", (
        "다음 중 GEO에서 **가설 단계**에 해당하는 것은?"
    ), 5)
    add_option(s, "A", "구조화된 콘텐츠가 AI에 더 잘 파싱된다", 0,
               "구조화된 콘텐츠의 AI 파싱 효과는 이미 검증된 근거입니다. 다수의 연구와 실험에서 확인된 사실이므로 가설이 아닙니다.", 1)
    add_option(s, "B", "Answer-first 형식이 인용 확률을 높인다", 0,
               "이것도 검증된 근거입니다. AI가 문서 상단의 명확한 답변을 인용하는 경향은 확인되었습니다.", 2)
    add_option(s, "C", "SNS 공유가 AI 인용에 직접적인 영향을 미친다", 1,
               "정답입니다! SNS 공유와 AI 인용의 직접적 관계는 아직 검증되지 않은 가설 단계입니다.", 3)
    add_option(s, "D", "E-E-A-T 신호가 강한 콘텐츠가 더 자주 인용된다", 0,
               "E-E-A-T와 AI 인용의 관계는 여러 분석에서 확인된 근거입니다. 전문성과 신뢰성이 높은 콘텐츠가 인용되는 패턴은 검증되었습니다.", 4)

    # ==================================================================
    # STAGE 2: Technical GEO 기초 실습
    # ==================================================================

    # --- Module 2-1: 정보구조(IA) 개념 ---
    m = add_module(2, "2-1: 정보구조(IA) 개념", "정보구조(Information Architecture)의 기본 개념을 이해합니다.", 1)

    add_step(m, "reading", "정보구조(IA)란", (
        "## 정보구조(Information Architecture)란?\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>IA</strong> (Information Architecture, 정보구조)<br>\n"
        "웹사이트의 페이지를 체계적으로 분류하고 연결하는 설계</p>\n"
        "<p><strong>Hub-Cluster</strong> (허브-클러스터)<br>\n"
        "핵심 주제 페이지(허브)에서 세부 페이지(클러스터)로 체계적으로 연결하는 구조</p>\n"
        "<p><strong>Topic Cluster</strong> (토픽 클러스터)<br>\n"
        "하나의 주제를 중심으로 관련 콘텐츠를 묶어 연결한 콘텐츠 그룹</p>\n"
        "</div>\n\n"
        "**정보구조(IA)**는 웹사이트의 콘텐츠를 체계적으로 조직하고 분류하는 방법론입니다.\n\n"
        "### GEO에서 IA가 중요한 이유\n\n"
        "- AI는 사이트 전체의 구조를 파악하여 전문성을 판단합니다\n"
        "- 잘 조직된 사이트는 크롤링과 인덱싱이 쉬워 AI 검색에서 유리합니다\n"
        "- 주제별 클러스터링이 명확하면 AI가 해당 주제의 권위 있는 출처로 인식합니다\n\n"
        "### IA의 핵심 요소\n\n"
        "1. **조직화 체계**: 콘텐츠를 카테고리와 하위 카테고리로 분류\n"
        "2. **레이블링 체계**: 각 페이지와 섹션에 명확한 이름 부여\n"
        "3. **내비게이션 체계**: 사용자와 AI가 콘텐츠를 찾을 수 있는 경로\n"
        "4. **검색 체계**: 사이트 내 검색 기능과 인덱싱"
        '\n\n'
        '<div class="tree-diagram">\n'
        '<div class="tree-title">b2b.fastcampus.co.kr 현재 링크 구조</div>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node root">홈</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">서비스</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">문의</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '<li class="tree-item"><span class="tree-node">개인정보</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '<p style="font-size:0.85rem;color:#888;margin-top:12px;">평균 내부링크: 3.3개/페이지 | 허브-클러스터 구조: 없음 | 크로스 링크: 최소 수준</p>\n'
        '</div>'
    ), 1, extension_md=(
        "### 실전 팁\n\n"
        "실무에서 IA를 점검할 때는 **사이트맵(XML Sitemap)**부터 확인하세요. "
        "사이트맵은 AI 크롤러가 사이트 구조를 파악하는 첫 번째 진입점입니다. "
        "사이트맵에 모든 중요 페이지가 포함되어 있는지, URL 계층이 논리적인지 확인합니다. "
        "또한 **breadcrumb(빵 부스러기) 내비게이션**을 구현하면 AI가 페이지의 위치를 "
        "사이트 전체 구조 속에서 정확히 파악할 수 있습니다. "
        "Schema.org의 BreadcrumbList 구조화 데이터를 함께 적용하면 효과가 극대화됩니다."
    ))

    s = add_step(m, "quiz", "IA와 GEO의 관계", (
        "정보구조(IA)가 GEO에 중요한 이유로 가장 적절한 것은?"
    ), 2)
    add_option(s, "A", "IA가 좋으면 웹사이트가 더 예쁘게 보이기 때문에", 0,
               "IA는 시각적 디자인이 아니라 콘텐츠의 논리적 구조와 조직화에 관한 것입니다. AI가 사이트의 전문성을 판단하는 핵심 요소입니다.", 1)
    add_option(s, "B", "AI가 사이트 전체의 구조를 파악하여 전문성을 판단하기 때문에", 1,
               "정답입니다! AI는 개별 페이지뿐 아니라 사이트 전체의 구조를 보고 해당 주제에 대한 권위를 판단합니다.", 2)
    add_option(s, "C", "IA가 좋으면 서버 비용이 줄어들기 때문에", 0,
               "IA는 콘텐츠의 논리적 조직화에 관한 것이며, 서버 비용 절감과는 직접적 관련이 없습니다. AI가 사이트 구조를 파악하도록 돕는 것이 IA의 핵심입니다.", 3)
    add_option(s, "D", "검색엔진 광고 비용을 절감하기 위해서", 0,
               "IA는 광고 비용 절감이 아니라 오가닉 콘텐츠의 체계적 구조화에 관한 것입니다. 콘텐츠 조직화를 통해 AI 인용을 높이는 전략입니다.", 4)

    s = add_step(m, "quiz", "IA 핵심 요소", (
        "다음 중 IA(정보구조)의 4가지 핵심 요소에 포함되지 **않는** 것은?"
    ), 3)
    add_option(s, "A", "조직화 체계", 0,
               "조직화 체계는 IA의 핵심 요소입니다. 콘텐츠를 카테고리로 분류하는 방법입니다.", 1)
    add_option(s, "B", "레이블링 체계", 0,
               "레이블링 체계는 IA의 핵심 요소입니다. 각 섹션에 명확한 이름을 부여합니다.", 2)
    add_option(s, "C", "수익화 체계", 1,
               "정답입니다! 수익화 체계는 IA의 핵심 요소가 아닙니다. IA는 조직화, 레이블링, 내비게이션, 검색 체계로 구성됩니다.", 3)
    add_option(s, "D", "내비게이션 체계", 0,
               "내비게이션 체계는 IA의 핵심 요소입니다. 사용자와 AI가 콘텐츠를 찾는 경로입니다.", 4)

    s = add_step(m, "practice", "실습: b2b.fastcampus.co.kr IA 진단", (
        "b2b.fastcampus.co.kr의 주요 페이지 5개(service_custom, service_b2b, refer_customer, resource_insight, about)를 떠올려 보세요.\n\n"
        "현재 사이트의 정보구조(IA)를 진단한다면, 가장 시급하게 개선해야 할 점은?"
    ), 4)
    add_option(s, "A", "페이지 간 주제 클러스터링이 불명확하여 AI가 사이트의 전문 영역을 파악하기 어렵다", 1,
               "정답입니다! 주제별 클러스터링이 명확하지 않으면 AI는 사이트의 주제 전문성(Topical Authority)을 인식하기 어렵습니다. 허브-클러스터 구조로 재편하는 것이 1순위입니다.", 1)
    add_option(s, "B", "페이지 로딩 속도가 느려서 크롤링이 안 된다", 0,
               "페이지 속도는 기술적 SEO 이슈이며, IA 진단의 핵심 포인트는 아닙니다.", 2)
    add_option(s, "C", "디자인이 오래되어 사용자 이탈률이 높다", 0,
               "디자인은 UX 문제이며, IA(정보구조)는 콘텐츠의 논리적 조직에 관한 것입니다.", 3)

    # --- Module 2-2: 허브-클러스터 맵 실습 ---
    m = add_module(2, "2-2: 허브-클러스터 맵 실습", "허브 페이지와 클러스터 콘텐츠를 설계하는 실습을 합니다.", 2)

    add_step(m, "reading", "허브-클러스터 모델이란", (
        "## 허브-클러스터 콘텐츠 모델\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Sitemap</strong> (사이트맵)<br>\n"
        "웹사이트의 모든 페이지 목록을 XML 파일로 정리해 검색엔진에 제출하는 것</p>\n"
        "<p><strong>Breadcrumb</strong> (브레드크럼, 경로 탐색)<br>\n"
        '"홈 &gt; 카테고리 &gt; 현재 페이지" 형태로 사용자 위치를 보여주는 네비게이션</p>\n'
        "<p><strong>Index / Noindex</strong> (인덱스 / 노인덱스)<br>\n"
        "검색엔진에 페이지를 등록(index)하거나 제외(noindex)하는 설정</p>\n"
        "</div>\n\n"
        "**허브-클러스터 모델**은 하나의 핵심 주제(허브)를 중심으로 세부 주제(클러스터)를 "
        "내부 링크로 연결하는 콘텐츠 구조입니다.\n\n"
        "### 구조\n\n"
        '<div class="tree-diagram">\n'
        '<div class="tree-title">허브-클러스터 콘텐츠 모델</div>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node root">허브 페이지</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">클러스터 1</span></li>\n'
        '<li class="tree-item"><span class="tree-node">클러스터 2</span></li>\n'
        '<li class="tree-item"><span class="tree-node">클러스터 3</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</div>\n\n'
        "### 예시: 'GEO' 허브\n"
        "- **허브**: 'GEO 완전 가이드' (종합 개요 페이지)\n"
        "- **클러스터 1**: 'GEO와 SEO의 차이'\n"
        "- **클러스터 2**: 'RAG 파이프라인 이해'\n"
        "- **클러스터 3**: 'GEO KPI 측정법'\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">Before: 현재 플랫 구조</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>페이지들이 독립적으로 존재</li>\n'
        '<li>내부링크 평균 3.3개/페이지</li>\n'
        '<li>주제 간 연결 없음</li>\n'
        '<li>AI가 전문성 인식 불가</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card after">\n'
        '<div class="card-header">After: 허브-클러스터 구조</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>service_custom을 허브로 설정</li>\n'
        '<li>인사이트/사례를 클러스터로 연결</li>\n'
        '<li>양방향 내부링크 강화</li>\n'
        "<li>AI가 '기업교육' 주제 권위 인식</li>\n"
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n\n'
        "### GEO 효과\n\n"
        "- AI가 허브 페이지를 해당 주제의 **권위 있는 종합 출처**로 인식\n"
        "- 클러스터 간 내부 링크가 주제 관련성을 강화\n"
        "- 주제 전문성(Topical Authority) 신호 극대화"
    ), 1)

    s = add_step(m, "quiz", "허브 페이지의 역할", (
        "허브-클러스터 모델에서 **허브 페이지**의 역할로 가장 적절한 것은?"
    ), 2)
    add_option(s, "A", "특정 세부 키워드 하나만 집중 공략하는 페이지", 0,
               "세부 키워드 공략은 클러스터 페이지의 역할입니다. 허브 페이지는 종합 개요 역할을 합니다.", 1)
    add_option(s, "B", "핵심 주제의 종합 개요를 제공하고 클러스터 페이지로 연결하는 중심 페이지", 1,
               "정답입니다! 허브 페이지는 주제 전체를 아우르는 종합 가이드 역할을 하며, 세부 클러스터로 연결됩니다.", 2)
    add_option(s, "C", "방문자 수가 가장 많은 페이지", 0,
               "허브 페이지가 트래픽이 많을 수 있지만, 역할의 정의는 트래픽이 아니라 구조적 중심점입니다.", 3)
    add_option(s, "D", "외부 링크만 모아놓은 리소스 페이지", 0,
               "허브 페이지는 외부 링크가 아니라 자사 클러스터 콘텐츠로 연결되는 내부 구조입니다.", 4)

    s = add_step(m, "quiz", "허브-클러스터와 GEO", (
        "허브-클러스터 모델이 GEO에 효과적인 이유는?"
    ), 3)
    add_option(s, "A", "페이지 수가 많아져서 크롤링 빈도가 높아지기 때문에", 0,
               "단순히 페이지 수가 많다고 크롤링 빈도가 높아지는 것은 아닙니다. 구조적 연결이 핵심입니다.", 1)
    add_option(s, "B", "AI가 체계적으로 연결된 콘텐츠를 통해 주제 전문성(Topical Authority)을 인식하기 때문에", 1,
               "정답입니다! 허브-클러스터 구조는 AI에게 해당 주제에 대한 깊이 있는 전문성을 보여주어 인용 확률을 높입니다.", 2)
    add_option(s, "C", "디자인이 통일되어 사용자 경험이 좋아지기 때문에", 0,
               "디자인 통일은 UX의 장점이지만, GEO 효과의 핵심 이유는 콘텐츠 구조와 주제 전문성입니다.", 3)
    add_option(s, "D", "검색엔진 광고 품질 점수가 높아지기 때문에", 0,
               "광고 품질 점수는 유료 광고(SEM) 영역이며, GEO의 콘텐츠 구조 최적화와는 직접적 관련이 없습니다. 오가닉 전략에 집중하세요.", 4)

    s = add_step(m, "practice", "실습: 허브 페이지 선정", (
        "b2b.fastcampus.co.kr에서 '기업 교육' 주제의 허브-클러스터 맵을 만든다면,\n\n"
        "**허브 페이지**로 가장 적합한 것은?"
    ), 4)
    add_option(s, "A", "resource_insight (블로그/인사이트 페이지)", 0,
               "인사이트 페이지는 개별 콘텐츠를 다루므로 클러스터에 가깝습니다. 허브는 주제의 총론을 다루는 페이지여야 합니다.", 1)
    add_option(s, "B", "service_custom (기업 맞춤형 교육 서비스 페이지)", 1,
               "정답입니다! service_custom은 '기업 교육'이라는 핵심 주제의 총론을 다루므로 허브 페이지로 가장 적합합니다. 나머지 페이지들은 세부 주제를 다루는 클러스터 역할을 합니다.", 2)
    add_option(s, "C", "about (회사 소개 페이지)", 0,
               "회사 소개는 일반적인 기업 정보를 다루는 페이지이며, '기업 교육'이라는 특정 주제의 허브로는 적합하지 않습니다. 허브는 주제의 총론을 다루어야 합니다.", 3)
    add_option(s, "D", "refer_customer (고객 사례 페이지)", 0,
               "고객 사례는 증거/신뢰성을 보여주는 클러스터 콘텐츠입니다. 허브는 주제의 종합적 개요를 제공해야 합니다.", 4)

    # --- Module 2-3: Answer-first 요약 설계 ---
    m = add_module(2, "2-3: Answer-first 요약 설계", "AI 인용에 최적화된 Answer-first 구조를 실습합니다.", 3)

    add_step(m, "reading", "Answer-first 원칙", (
        "## Answer-first 콘텐츠 설계\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Answer-first</strong> (답변 우선 구조)<br>\n"
        "긴 설명 대신 핵심 답변을 문서 맨 앞에 배치하는 콘텐츠 작성법</p>\n"
        "<p><strong>Featured Snippet</strong> (추천 스니펫)<br>\n"
        "구글 검색 결과 최상단에 박스로 강조 표시되는 요약 답변</p>\n"
        "<p><strong>Inverted Pyramid</strong> (역피라미드 구조)<br>\n"
        "가장 중요한 정보를 먼저 쓰고 세부 사항을 나중에 쓰는 저널리즘 작성 방식</p>\n"
        "</div>\n\n"
        "**Answer-first**는 사용자의 질문에 대한 핵심 답변을 문서 최상단에 배치하는 원칙입니다.\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">전통적 구조 (Bottom-up)</div>\n'
        '<div class="card-body">\n'
        '<ol>\n'
        '<li>배경 설명</li>\n'
        '<li>상세 분석</li>\n'
        '<li>결론 (답변)</li>\n'
        '</ol>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card after">\n'
        '<div class="card-header">Answer-first 구조 (Top-down)</div>\n'
        '<div class="card-body">\n'
        '<ol>\n'
        '<li><strong>핵심 답변</strong> (1-2문장)</li>\n'
        '<li>근거와 설명</li>\n'
        '<li>상세 분석</li>\n'
        '<li>추가 참고사항</li>\n'
        '</ol>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n\n'
        "### 왜 Answer-first인가?\n\n"
        "- AI는 문서 상단의 명확한 답변을 인용할 가능성이 높습니다\n"
        "- 사용자도 핵심 정보를 빠르게 파악할 수 있습니다\n"
        "- Featured Snippet에 선정될 확률도 높아집니다\n\n"
        "### 실전 팁\n\n"
        "- 첫 문단에 질문에 대한 직접적 답변을 넣으세요\n"
        "- '~란?' 형태의 질문이면 정의를 먼저 제시하세요\n"
        "- 숫자나 리스트로 답변하면 AI가 인용하기 쉽습니다"
        '\n\n'
        '<div class="browser-mockup">\n'
        '<div class="browser-bar">\n'
        '<span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>\n'
        '<span class="browser-url">b2b.fastcampus.co.kr/service_custom (Before)</span>\n'
        '</div>\n'
        '<div class="browser-body">\n'
        '<div class="page-title">현재 상태: CSR 빈 페이지</div>\n'
        '<div class="page-element missing">본문 텍스트 — 244자만 렌더링</div>\n'
        '<div class="page-element missing">Answer-first 요약 — 없음</div>\n'
        '<div class="page-element missing">핵심 정보 — JavaScript 로딩 후에만 표시</div>\n'
        '</div>\n'
        '</div>\n'
        '\n'
        '<div class="browser-mockup">\n'
        '<div class="browser-bar">\n'
        '<span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>\n'
        '<span class="browser-url">b2b.fastcampus.co.kr/service_custom (After)</span>\n'
        '</div>\n'
        '<div class="browser-body">\n'
        '<div class="page-title">개선 후: Answer-first 적용</div>\n'
        '<div class="page-element present">H1: 기업 맞춤형 AI 교육 프로그램</div>\n'
        '<div class="page-element present">Answer-first 요약 2문장 — 있음</div>\n'
        '<div class="page-element present">핵심 정보 — SSR로 즉시 표시</div>\n'
        '<div class="page-element present">구조화된 콘텐츠 — 4,000자+</div>\n'
        '</div>\n'
        '</div>'
    ), 1, extension_md=(
        "### 더 알아보기\n\n"
        "Answer-first 원칙은 저널리즘의 **역피라미드(Inverted Pyramid)** 구조에서 유래했습니다. "
        "뉴스 기사가 가장 중요한 정보를 첫 문단에 배치하는 것과 동일한 원리입니다. "
        "실제로 Perplexity AI는 답변 생성 시 문서의 첫 200단어를 가장 높은 가중치로 분석한다는 "
        "분석 결과가 있습니다. 이를 활용하려면 페이지의 메타 디스크립션(meta description)도 "
        "Answer-first 형식으로 작성하는 것이 좋습니다. "
        "AI가 검색 결과에서 페이지를 선택하기 전 메타 디스크립션을 먼저 참고하기 때문입니다."
    ))

    s = add_step(m, "quiz", "Answer-first 구조 판별", (
        "다음 중 Answer-first 원칙에 가장 부합하는 문서 구조는?"
    ), 2)
    add_option(s, "A", "서론 -> 역사적 배경 -> 다양한 관점 소개 -> 결론에서 답변 제시", 0,
               "이것은 전통적인 Bottom-up 구조입니다. Answer-first는 답변을 맨 앞에 배치합니다.", 1)
    add_option(s, "B", "핵심 답변(1-2문장) -> 근거 설명 -> 상세 분석 -> 추가 참고사항", 1,
               "정답입니다! Answer-first는 핵심 답변을 문서 최상단에 배치하고, 그 뒤에 근거와 상세 내용을 서술합니다.", 2)
    add_option(s, "C", "목차 -> 각 섹션별 상세 설명 -> FAQ -> 결론", 0,
               "이것은 체계적이지만 Answer-first 구조는 아닙니다. 핵심 답변이 맨 앞에 와야 합니다.", 3)
    add_option(s, "D", "관련 키워드 나열 -> 본문 -> 요약", 0,
               "키워드를 단순 나열하는 것은 Answer-first 원칙과 관련이 없습니다. 핵심 답변을 자연스러운 문장으로 최상단에 배치하는 것이 핵심입니다.", 4)

    s = add_step(m, "quiz", "Answer-first 실전 적용", (
        "'GEO란 무엇인가?'라는 질문에 Answer-first 원칙을 적용한 첫 문단으로 가장 적절한 것은?"
    ), 3)
    add_option(s, "A", "최근 AI 기술이 빠르게 발전하면서 마케팅 업계에 큰 변화가 일어나고 있습니다.", 0,
               "이것은 배경 설명으로 시작하는 전통적 구조입니다. Answer-first는 정의를 먼저 제시해야 합니다.", 1)
    add_option(s, "B", "GEO(Generative Engine Optimization)는 생성형 AI가 답변 시 내 콘텐츠를 인용 출처로 채택하도록 최적화하는 전략입니다.", 1,
               "정답입니다! 질문에 대한 직접적인 정의를 첫 문장에 제시하는 것이 Answer-first 원칙입니다.", 2)
    add_option(s, "C", "이 글에서는 GEO에 대해 알아보겠습니다. 먼저 역사부터 살펴봅시다.", 0,
               "이것은 서론 중심의 전통적 구조입니다. Answer-first는 서론 없이 바로 핵심 답변을 첫 문장에 제시하는 원칙입니다.", 3)
    add_option(s, "D", "목차: 1. GEO 정의 2. GEO 역사 3. GEO 방법론 4. 결론", 0,
               "목차는 구조화에 도움이 되지만, Answer-first의 핵심은 첫 문단에 답변을 배치하는 것입니다.", 4)

    s = add_step(m, "practice", "실습: Answer-first 요약문 작성", (
        "service_custom 페이지 상단에 들어갈 Answer-first 요약문을 설계합니다.\n\n"
        "'패스트캠퍼스 기업 맞춤형 교육은 어떤 서비스인가요?'라는 질문에 대해\n"
        "가장 효과적인 Answer-first 요약문은?"
    ), 4)
    add_option(s, "A", "패스트캠퍼스는 2013년에 설립된 교육 기업으로, 다양한 분야의 강의를 제공합니다.", 0,
               "이것은 회사 소개이지 Answer-first 요약이 아닙니다. Answer-first는 질문에 대한 직접적 답변을 1-2문장으로 제시해야 합니다.", 1)
    add_option(s, "B", "패스트캠퍼스 기업 맞춤형 교육은 HRD/교육기획 담당자를 위해, 생성형 AI 등 기업별 니즈에 맞춘 커리큘럼을 설계하여 실무 역량을 강화하는 B2B 교육 서비스입니다.", 1,
               "정답입니다! 누구에게(HRD 담당자), 무엇을(맞춤 커리큘럼), 어떤 결과(실무 역량 강화)를 모두 포함하는 완성된 Answer-first 요약입니다.", 2)
    add_option(s, "C", "자세한 내용은 아래를 참고하세요.", 0,
               "이것은 답변을 회피하는 문장입니다. Answer-first는 핵심 답변을 먼저 제시해야 합니다.", 3)
    add_option(s, "D", "기업교육, 맞춤교육, B2B교육, 직무교육, AI교육", 0,
               "키워드 나열은 Answer-first가 아닙니다. 자연스러운 문장으로 핵심 답변을 작성해야 합니다.", 4)

    # --- Module 2-4: FAQ 설계 실습 ---
    m = add_module(2, "2-4: FAQ 설계 실습", "AI 인용에 최적화된 FAQ 섹션을 설계합니다.", 4)

    add_step(m, "reading", "FAQ가 GEO에 중요한 이유", (
        "## FAQ 설계와 GEO\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>FAQ</strong> (Frequently Asked Questions, 자주 묻는 질문)<br>\n"
        "고객이 자주 묻는 질문과 답변을 정리한 콘텐츠</p>\n"
        "<p><strong>Rich Result</strong> (리치 결과)<br>\n"
        "별점, FAQ 펼침, 가격 등이 함께 표시되는 화려한 검색 결과</p>\n"
        "</div>\n\n"
        "FAQ(Frequently Asked Questions) 섹션은 GEO에서 매우 효과적인 콘텐츠 형태입니다.\n\n"
        "### FAQ가 AI에 잘 인용되는 이유\n\n"
        "1. **질문-답변 구조**: AI가 사용자 질문에 매칭하기 쉬움\n"
        "2. **명확한 형식**: 질문(H3)과 답변(본문)이 명확히 구분됨\n"
        "3. **Schema Markup**: FAQPage 구조화 데이터 적용 가능\n"
        "4. **Long-tail 쿼리 대응**: 구체적인 질문에 직접 답변\n\n"
        "### 좋은 FAQ 설계 원칙\n\n"
        "- **실제 사용자 질문 기반**: 검색 데이터에서 추출한 실제 질문 사용\n"
        "- **Answer-first 적용**: 각 답변의 첫 문장이 핵심 답변\n"
        "- **적정 길이**: 답변은 2-4문장으로 간결하게\n"
        "- **구조화 데이터**: FAQPage schema 적용\n\n"
        "### 나쁜 FAQ 패턴\n\n"
        "- 회사 소개를 FAQ 형식으로 포장한 것\n"
        "- 너무 일반적이거나 뻔한 질문\n"
        "- 답변이 없이 '문의하세요'로 끝나는 것"
        '\n\n'
        '<div class="code-example">\n'
        '<div class="code-label">FAQPage JSON-LD 예시</div>\n'
        '<pre><code>{\n'
        '  "@context": "https://schema.org",\n'
        '  "@type": "FAQPage",\n'
        '  "mainEntity": [{\n'
        '    "@type": "Question",\n'
        '    "name": "기업 맞춤형 교육의 최소 수강 인원은?",\n'
        '    "acceptedAnswer": {\n'
        '      "@type": "Answer",\n'
        '      "text": "최소 10명부터 가능하며, 기업 규모에 맞춰 유연하게 조정됩니다."\n'
        '    }\n'
        '  }]\n'
        '}</code></pre>\n'
        '</div>\n'
        '\n'
        '<div class="callout tip">\n'
        '<p><strong>팁:</strong> JSON-LD를 HTML의 &lt;head&gt; 또는 &lt;body&gt;에 &lt;script type="application/ld+json"&gt;으로 삽입하면 AI가 FAQ 구조를 정확히 파싱합니다.</p>\n'
        '</div>'
    ), 1, extension_md=(
        "### 심화 학습\n\n"
        "FAQ Schema Markup(FAQPage)을 적용하면 검색엔진과 AI가 질문-답변 구조를 "
        "기계적으로 정확히 파싱할 수 있습니다. JSON-LD 형식으로 구현하는 것이 권장되며, "
        "Google의 Rich Results Test 도구로 올바르게 구현되었는지 검증할 수 있습니다. "
        "FAQ 질문을 발굴하는 실전 방법으로는 Google Search Console의 검색어 보고서, "
        "AnswerThePublic, AlsoAsked 같은 도구를 활용하면 사용자들이 실제로 검색하는 "
        "Long-tail 질문을 효과적으로 수집할 수 있습니다. "
        "수집된 질문을 AI에 직접 입력해 보면 현재 어떤 출처가 인용되는지도 파악 가능합니다."
    ))

    s = add_step(m, "quiz", "좋은 FAQ 설계", (
        "GEO에 효과적인 FAQ 설계 원칙으로 **올바른** 것은?"
    ), 2)
    add_option(s, "A", "질문을 최대한 짧게, 답변을 최대한 길게 작성한다", 0,
               "답변은 2-4문장으로 간결하게 작성하는 것이 효과적입니다. 너무 긴 답변은 AI가 핵심을 파악하기 어렵습니다.", 1)
    add_option(s, "B", "실제 사용자 질문을 기반으로 하고, 각 답변의 첫 문장에 핵심 답변을 배치한다", 1,
               "정답입니다! 실제 검색 데이터 기반 질문과 Answer-first 원칙을 결합하면 AI 인용에 최적화됩니다.", 2)
    add_option(s, "C", "모든 답변을 '자세한 내용은 문의하세요'로 끝낸다", 0,
               "모든 답변을 '문의하세요'로 끝내는 것은 나쁜 FAQ 패턴입니다. AI는 직접적이고 구체적인 답변이 있는 콘텐츠를 우선적으로 인용합니다.", 3)
    add_option(s, "D", "회사 소개 내용을 FAQ 형식으로 변환한다", 0,
               "회사 소개를 FAQ로 포장하는 것은 사용자의 실제 질문과 무관하여 효과가 떨어집니다.", 4)

    s = add_step(m, "quiz", "FAQ Schema Markup", (
        "FAQ에 FAQPage Schema Markup을 적용하는 이유는?"
    ), 3, extension_md=(
        "### 참고 자료\n\n"
        "FAQPage Schema Markup은 JSON-LD 형식으로 구현하는 것이 가장 권장됩니다. "
        "구현 예시: `<script type=\"application/ld+json\">{\"@context\": \"https://schema.org\", "
        "\"@type\": \"FAQPage\", \"mainEntity\": [{...}]}</script>` 형태로 "
        "HTML의 `<head>` 또는 `<body>` 섹션에 삽입합니다. "
        "Schema.org 공식 문서와 Google의 구조화 데이터 가이드에서 상세 스펙을 확인할 수 있으며, "
        "구현 후 반드시 Google의 Rich Results Test로 오류 여부를 검증하세요."
    ))
    add_option(s, "A", "웹사이트 디자인을 자동으로 개선해주기 때문에", 0,
               "Schema Markup은 시각적 디자인과 관련이 없습니다. 기계 판독성을 높이는 것이 목적입니다.", 1)
    add_option(s, "B", "AI가 FAQ 구조를 기계적으로 파싱하고 질문-답변을 정확히 매칭할 수 있기 때문에", 1,
               "정답입니다! Schema Markup은 AI가 콘텐츠의 구조를 정확히 이해하도록 도와 인용 확률을 높입니다.", 2)
    add_option(s, "C", "구글 검색 결과에서 항상 1위를 보장하기 때문에", 0,
               "Schema Markup은 순위를 보장하지 않습니다. 다만 AI와 검색엔진의 이해도를 높입니다.", 3)
    add_option(s, "D", "페이지 로딩 속도를 향상시키기 때문에", 0,
               "Schema Markup은 로딩 속도와 관련이 없습니다. 구조화된 데이터를 제공하는 것이 목적입니다.", 4)

    s = add_step(m, "practice", "실습: FAQ 질문 설계", (
        "service_custom 페이지에 FAQ 섹션을 추가합니다.\n\n"
        "다음 중 GEO에 가장 효과적인 FAQ 질문은?"
    ), 4)
    add_option(s, "A", "패스트캠퍼스는 좋은 회사인가요?", 0,
               "이것은 주관적이고 모호한 질문입니다. FAQ는 구체적이고 실용적인 질문이어야 AI가 답변으로 인용할 수 있습니다.", 1)
    add_option(s, "B", "기업 맞춤형 교육의 최소 수강 인원과 교육 기간은 어떻게 되나요?", 1,
               "정답입니다! 구체적인 실무 질문이며, HR 담당자가 실제로 궁금해할 내용입니다. AI는 이런 구체적 Q&A를 답변 소스로 인용할 확률이 높습니다.", 2)
    add_option(s, "C", "교육이란 무엇인가요?", 0,
               "너무 일반적인 질문입니다. FAQ는 해당 서비스에 특화된 구체적 질문이어야 합니다.", 3)
    add_option(s, "D", "왜 패스트캠퍼스를 선택해야 하나요?", 0,
               "마케팅 문구에 가깝습니다. GEO에 효과적인 FAQ는 사용자의 실제 정보 탐색 질문이어야 합니다.", 4)

    # --- Module 2-5: 헤딩(H1~H3) 재설계 ---
    m = add_module(2, "2-5: 헤딩(H1~H3) 재설계", "AI 파싱에 최적화된 헤딩 계층을 설계합니다.", 5)

    add_step(m, "reading", "헤딩 계층의 중요성", (
        "## 헤딩(Heading) 재설계 가이드\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>H1 / H2 / H3</strong> (제목 태그)<br>\n"
        "HTML에서 제목의 중요도를 나타내는 태그 — H1이 가장 큰 대제목</p>\n"
        "<p><strong>Semantic HTML</strong> (시맨틱 HTML)<br>\n"
        "의미를 가진 태그(header, nav, article 등)로 문서 구조를 명확히 표현하는 것</p>\n"
        "</div>\n\n"
        "헤딩 태그(H1~H6)는 AI가 문서의 구조를 파악하는 가장 기본적인 신호입니다.\n\n"
        "### 올바른 헤딩 계층\n\n"
        '<div class="tree-diagram">\n'
        '<div class="tree-title">올바른 헤딩 계층 구조</div>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node root">H1: 페이지 주제 (1개만)</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">H2: 주요 섹션</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">H3: 하위 섹션</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '<li class="tree-item"><span class="tree-node">H2: 주요 섹션</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">H3: 하위 섹션</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</div>\n\n'
        "### GEO를 위한 헤딩 설계 원칙\n\n"
        "1. **H1은 질문 형태**: 사용자가 AI에 물어볼 법한 질문으로 작성\n"
        "2. **H2는 핵심 하위 주제**: 답변의 주요 구성 요소를 명확히 구분\n"
        "3. **H3는 세부 포인트**: 구체적인 항목이나 단계\n"
        "4. **키워드 자연 포함**: 헤딩에 검색/질문 키워드를 자연스럽게 포함\n"
        "5. **건너뛰기 금지**: H1 → H3 건너뛰기는 구조 혼란을 초래\n\n"
        "### 나쁜 예 vs 좋은 예\n\n"
        "**나쁜 예**: H1: 소개 / H2: 본론 / H3: 결론\n"
        "**좋은 예**: H1: GEO란 무엇인가? / H2: GEO의 5가지 핵심 원칙 / H3: 1. 구조화된 콘텐츠"
        '\n\n'
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">Before: 헤딩 없는 페이지 (6/10)</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>H1 태그 — 없음</li>\n'
        '<li>H2 태그 — 없음</li>\n'
        '<li>문서 구조 파악 불가</li>\n'
        '<li>AI가 주제를 인식할 수 없음</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card after">\n'
        '<div class="card-header">After: 올바른 헤딩 구조</div>\n'
        '<div class="card-body">\n'
        '<ul>\n'
        '<li>H1: 페이지 핵심 주제 (1개)</li>\n'
        '<li>H2: 주요 섹션 구분</li>\n'
        '<li>H3: 세부 항목</li>\n'
        '<li>AI가 문서 구조 정확히 파악</li>\n'
        '</ul>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '\n'
        '<div class="hierarchy-box">\n'
        '<div class="hierarchy-title">올바른 헤딩 계층 예시 (service_custom)</div>\n'
        '<div class="level level-1">H1: 기업 맞춤형 AI 교육 프로그램</div>\n'
        '<div class="level level-2">H2: 교육 과정 소개</div>\n'
        '<div class="level level-3">H3: 생성형 AI 실무 과정</div>\n'
        '<div class="level level-3">H3: 데이터 분석 과정</div>\n'
        '<div class="level level-2">H2: 교육 진행 방식</div>\n'
        '<div class="level level-3">H3: 온라인 교육</div>\n'
        '<div class="level level-3">H3: 오프라인 교육</div>\n'
        '<div class="level level-2">H2: 고객 사례 및 후기</div>\n'
        '</div>'
    ), 1)

    s = add_step(m, "quiz", "헤딩 설계 원칙", (
        "GEO를 위한 H1 태그 작성 원칙으로 가장 적절한 것은?"
    ), 2)
    add_option(s, "A", "H1에 회사명만 넣는다", 0,
               "회사명만으로는 AI가 페이지 주제를 파악하기 어렵습니다. 사용자 질문 형태가 더 효과적입니다.", 1)
    add_option(s, "B", "사용자가 AI에 물어볼 법한 질문 형태로 작성한다", 1,
               "정답입니다! H1을 질문 형태로 작성하면 AI가 해당 페이지가 그 질문에 답하는 콘텐츠임을 쉽게 인식합니다.", 2)
    add_option(s, "C", "H1을 여러 개 사용하여 다양한 키워드를 넣는다", 0,
               "H1은 페이지당 1개만 사용해야 합니다. 여러 H1을 사용하면 AI가 페이지의 핵심 주제를 파악하기 어려워 구조 혼란을 초래합니다.", 3)
    add_option(s, "D", "H1을 비워두고 이미지로 대체한다", 0,
               "AI는 이미지보다 텍스트 기반 헤딩을 더 잘 파싱합니다. H1은 반드시 텍스트로 작성해야 합니다.", 4)

    s = add_step(m, "quiz", "헤딩 계층 오류", (
        "다음 헤딩 구조에서 잘못된 부분은?\n\nH1: GEO 가이드\n  H3: GEO란?\n  H2: SEO와의 차이"
    ), 3)
    add_option(s, "A", "H1이 질문 형태가 아닌 것", 0,
               "H1이 질문 형태가 아닌 것도 개선할 수 있지만, 가장 큰 문제는 헤딩 계층 건너뛰기입니다.", 1)
    add_option(s, "B", "H1 바로 아래에 H3가 와서 H2를 건너뛴 것", 1,
               "정답입니다! H1 다음에는 H2가 와야 합니다. H2를 건너뛰고 H3를 사용하면 AI가 문서 구조를 잘못 파싱할 수 있습니다.", 2)
    add_option(s, "C", "H2가 사용된 것", 0,
               "H2 사용 자체는 문제가 없습니다. 문제는 헤딩 계층이 순서대로 사용되지 않은 것입니다.", 3)
    add_option(s, "D", "헤딩이 3개뿐인 것", 0,
               "헤딩 개수는 콘텐츠 양에 따라 유동적입니다. 여기서 핵심 문제는 개수가 아니라 H1 다음에 H2를 건너뛰고 H3를 사용한 계층 순서 오류입니다.", 4)

    s = add_step(m, "practice", "실습: 헤딩 구조 개선", (
        "service_custom 페이지의 현재 H1이 '기업 맞춤형 교육'입니다.\n\n"
        "GEO 관점에서 더 효과적인 H1은?"
    ), 4)
    add_option(s, "A", "패스트캠퍼스", 0,
               "브랜드명만으로는 페이지의 주제를 전달하기 어렵습니다. AI는 H1에서 해당 페이지의 핵심 주제를 파악합니다.", 1)
    add_option(s, "B", "기업 맞춤형 생성형 AI 교육 - 실무 역량 강화 프로그램 | 패스트캠퍼스", 1,
               "정답입니다! 핵심 키워드(기업 맞춤형 + 생성형 AI 교육)와 가치(실무 역량 강화)를 포함하여 AI가 페이지 주제를 명확히 파악할 수 있습니다.", 2)
    add_option(s, "C", "최고의 교육을 제공합니다", 0,
               "주관적 표현이며 구체적 주제를 포함하지 않습니다. H1은 페이지의 핵심 주제를 명확히 전달해야 합니다.", 3)
    add_option(s, "D", "기업교육 맞춤교육 B2B교육 AI교육 직무교육", 0,
               "키워드 나열은 스팸으로 인식될 수 있습니다. H1은 자연스러운 문장으로 핵심 주제를 표현해야 합니다.", 4)

    # --- Module 2-6: 내부링크 설계 ---
    m = add_module(2, "2-6: 내부링크 설계", "GEO에 효과적인 내부 링크 전략을 학습합니다.", 6)

    add_step(m, "reading", "내부링크와 GEO", (
        "## 내부링크 설계 전략\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Internal Link</strong> (내부 링크)<br>\n"
        "같은 웹사이트 안에서 페이지끼리 연결하는 하이퍼링크</p>\n"
        "<p><strong>Anchor Text</strong> (앵커 텍스트)<br>\n"
        '링크가 걸려 있는 클릭 가능한 텍스트 — "자세히 보기"보다 "GEO 전략 가이드"가 좋음</p>\n'
        "<p><strong>Crawl Budget</strong> (크롤 예산)<br>\n"
        "검색엔진이 한 번에 우리 사이트를 방문할 수 있는 페이지 수 한도</p>\n"
        "</div>\n\n"
        "**내부링크**는 같은 웹사이트 내에서 페이지 간을 연결하는 하이퍼링크입니다.\n\n"
        "### GEO에서 내부링크가 중요한 이유\n\n"
        "1. **주제 관련성 강화**: 관련 콘텐츠를 연결하면 AI가 주제 클러스터를 인식\n"
        "2. **크롤링 효율**: AI 크롤러가 관련 페이지를 발견하기 쉬워짐\n"
        "3. **권위 전파**: 허브 페이지의 권위가 클러스터 페이지로 전파됨\n"
        "4. **컨텍스트 제공**: 앵커 텍스트가 링크된 페이지의 주제를 AI에게 설명\n\n"
        "### 내부링크 설계 원칙\n\n"
        "- **설명적 앵커 텍스트**: '여기를 클릭' 대신 '허브-클러스터 모델 가이드' 사용\n"
        "- **맥락에 자연스럽게**: 본문 흐름에 자연스럽게 삽입\n"
        "- **양방향 링크**: 허브 -> 클러스터, 클러스터 -> 허브 양방향 연결\n"
        "- **관련 콘텐츠만**: 무관한 페이지로의 링크는 주제 신호를 약화시킴\n"
        "- **적정 수량**: 한 페이지에 3-10개 내부링크가 적정"
        '\n\n'
        '<div class="network-diagram">\n'
        '<div class="network-title">b2b.fastcampus.co.kr 내부링크 맵</div>\n'
        '<div class="network-grid">\n'
        '<div class="net-node hub"><div class="node-label">홈</div></div>\n'
        '<div class="net-edge">←→</div>\n'
        '<div class="net-node"><div class="node-label">문의</div></div>\n'
        '<div class="net-edge">←→</div>\n'
        '<div class="net-node"><div class="node-label">개인정보</div></div>\n'
        '</div>\n'
        '<div class="network-grid">\n'
        '<div class="net-node"><div class="node-label">서비스</div></div>\n'
        '<div class="net-edge" style="opacity:0.3">✕</div>\n'
        '<div class="net-node"><div class="node-label">인사이트</div></div>\n'
        '<div class="net-edge">←→</div>\n'
        '<div class="net-node"><div class="node-label">문의_mktg</div></div>\n'
        '</div>\n'
        '<div class="network-issues">\n'
        '<div class="net-issue">⚠ 서비스→인사이트 연결 없음</div>\n'
        '<div class="net-issue">⚠ 인사이트→서비스 역방향 링크 없음</div>\n'
        '<div class="net-issue">⚠ 대부분 페이지가 [문의]로만 연결</div>\n'
        '</div>\n'
        '</div>\n'
        '\n'
        '<div class="callout warning">\n'
        "<p><strong>주의:</strong> 현재 사이트의 앵커 텍스트 대부분이 '기업교육 문의하기'로 동일합니다. AI는 다양하고 설명적인 앵커 텍스트를 통해 페이지 간 관계를 더 정확히 파악합니다.</p>\n"
        '</div>'
    ), 1)

    s = add_step(m, "quiz", "앵커 텍스트 설계", (
        "GEO에 효과적인 내부링크 앵커 텍스트로 가장 적절한 것은?"
    ), 2)
    add_option(s, "A", "'여기를 클릭하세요'", 0,
               "'여기를 클릭하세요'는 범용적 표현으로, AI에게 링크된 페이지의 주제를 전혀 알려주지 못합니다. 설명적 앵커 텍스트를 사용하세요.", 1)
    add_option(s, "B", "'GEO 5대 신호 카테고리 상세 가이드'", 1,
               "정답입니다! 설명적 앵커 텍스트는 AI에게 링크된 페이지의 주제를 명확히 전달합니다.", 2)
    add_option(s, "C", "'더보기'", 0,
               "'더보기'는 범용적 표현으로 AI에게 링크된 페이지의 주제나 내용에 대한 의미 있는 컨텍스트를 제공하지 못합니다.", 3)
    add_option(s, "D", "'링크'", 0,
               "'링크'라는 단어만으로는 연결된 페이지의 주제나 내용에 대한 어떤 정보도 AI에게 전달하지 못합니다. 설명적 앵커 텍스트가 필요합니다.", 4)

    s = add_step(m, "quiz", "내부링크 전략", (
        "내부링크 설계 시 피해야 할 패턴은?"
    ), 3)
    add_option(s, "A", "관련 주제 페이지 간 양방향 링크 연결", 0,
               "양방향 링크는 좋은 패턴입니다. 허브와 클러스터 간 양방향 연결을 강화합니다.", 1)
    add_option(s, "B", "주제와 무관한 페이지로의 내부링크를 대량으로 삽입", 1,
               "정답입니다! 무관한 페이지로의 과도한 링크는 주제 신호를 약화시키고 AI의 주제 판단을 혼란스럽게 합니다.", 2)
    add_option(s, "C", "설명적 앵커 텍스트 사용", 0,
               "설명적 앵커 텍스트는 GEO에 매우 효과적인 좋은 패턴입니다. 피해야 할 패턴이 아니라 적극 활용해야 할 전략입니다.", 3)
    add_option(s, "D", "허브 페이지에서 클러스터 페이지로 연결", 0,
               "허브에서 클러스터로의 연결은 허브-클러스터 모델의 기본 패턴이며, 주제 권위를 강화하는 매우 효과적인 전략입니다.", 4)

    s = add_step(m, "practice", "실습: 앵커 텍스트 설계", (
        "resource_insight 블로그 글에서 service_custom 페이지로의 내부링크를 추가합니다.\n\n"
        "가장 효과적인 앵커 텍스트는?"
    ), 4)
    add_option(s, "A", "여기를 클릭하세요", 0,
               "'여기를 클릭'은 AI에게 링크 대상의 내용을 전달하지 못합니다. 설명적 앵커 텍스트가 필요합니다.", 1)
    add_option(s, "B", "패스트캠퍼스 기업 맞춤형 AI 교육 프로그램 상세 보기", 1,
               "정답입니다! 링크 대상 페이지의 핵심 주제를 포함하는 설명적 앵커 텍스트로, AI가 페이지 간 관계를 명확히 이해할 수 있습니다.", 2)
    add_option(s, "C", "https://b2b.fastcampus.co.kr/service_custom", 0,
               "URL 자체를 앵커 텍스트로 사용하면 AI가 맥락을 파악하기 어렵습니다. 자연스러운 설명문이 효과적입니다.", 3)
    add_option(s, "D", "더 보기", 0,
               "'더 보기'는 범용적 표현으로 AI에게 링크 대상 페이지의 내용에 대한 충분한 맥락을 제공하지 못합니다. 구체적 주제를 포함하세요.", 4)

    # --- Module 2-7: 80/20 액션 종합 판단 ---
    m = add_module(2, "2-7: 80/20 액션 종합 판단", "최소 노력으로 최대 GEO 효과를 내는 핵심 액션을 선별합니다.", 7)

    add_step(m, "reading", "80/20 법칙과 GEO", (
        "## GEO 80/20 법칙: 최소 노력, 최대 효과\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Impression</strong> (노출, 임프레션)<br>\n"
        "검색 결과에 우리 페이지가 표시된 횟수 (클릭 여부 무관)</p>\n"
        "<p><strong>Domain Rating</strong> (도메인 등급, DR)<br>\n"
        "사이트 전체의 신뢰도와 권위를 점수(0~100)로 나타낸 SEO 지표</p>\n"
        "</div>\n\n"
        "모든 GEO 전략을 동시에 실행하기는 어렵습니다. "
        "파레토 법칙(80/20)을 적용하여 가장 효과적인 액션부터 실행합시다.\n\n"
        "### Top 5 GEO 액션 (80% 효과)\n\n"
        "1. **Answer-first 구조 적용**: 모든 페이지 상단에 핵심 답변 배치\n"
        "2. **헤딩 계층 정리**: H1 > H2 > H3 올바른 구조로 재설계\n"
        "3. **FAQ 섹션 추가**: 주요 페이지에 5-10개 FAQ 추가\n"
        "4. **허브-클러스터 구축**: 핵심 주제 3-5개에 대해 허브 페이지 생성\n"
        "5. **내부링크 최적화**: 설명적 앵커 텍스트로 관련 페이지 연결\n\n"
        "### 우선순위 매트릭스\n\n"
        '<div class="comparison-table">\n'
        '<div class="comp-header">GEO 80/20 우선순위 매트릭스</div>\n'
        '<table>\n'
        '<thead><tr><th>액션</th><th>효과</th><th>난이도</th><th>우선순위</th></tr></thead>\n'
        '<tbody>\n'
        '<tr class="highlight"><td class="label">Answer-first</td><td>높음</td><td>낮음</td><td>1순위</td></tr>\n'
        '<tr class="highlight"><td class="label">헤딩 정리</td><td>높음</td><td>낮음</td><td>1순위</td></tr>\n'
        '<tr><td class="label">FAQ 추가</td><td>높음</td><td>중간</td><td>2순위</td></tr>\n'
        '<tr><td class="label">허브-클러스터</td><td>매우 높음</td><td>높음</td><td>2순위</td></tr>\n'
        '<tr><td class="label">내부링크</td><td>중간</td><td>낮음</td><td>3순위</td></tr>\n'
        '</tbody>\n'
        '</table>\n'
        '</div>\n\n'
        '<div class="callout key-point">\n'
        '<p><strong>당장 실행할 5가지 GEO 액션:</strong></p>\n'
        '<p>1. 모든 페이지에 H1 태그 추가 (현재 6/10 없음)</p>\n'
        '<p>2. 주요 서비스 페이지에 Answer-first 요약문 삽입</p>\n'
        '<p>3. FAQ 섹션 5개 이상 + FAQPage Schema 적용</p>\n'
        '<p>4. service_custom을 허브로 하는 클러스터 구조 구축</p>\n'
        '<p>5. 설명적 앵커 텍스트로 내부링크 재설계</p>\n'
        '</div>\n\n'
        "### 핵심 원칙\n\n"
        "난이도가 낮고 효과가 높은 액션부터 시작하세요. "
        "Answer-first와 헤딩 정리는 기존 콘텐츠를 수정만 하면 되므로 즉시 실행 가능합니다."
    ), 1, extension_md=(
        "### 실행 우선순위 가이드\n\n"
        "80/20 법칙의 핵심은 **완벽보다 실행**입니다. 위 5가지 액션 중 "
        "H1 태그 추가와 Answer-first 요약문은 30분 이내에 완료할 수 있습니다. "
        "이 두 가지만으로도 AI가 페이지를 인식하고 인용할 가능성이 크게 높아집니다. "
        "FAQ 섹션과 허브-클러스터 구조는 1-2주에 걸쳐 점진적으로 구축하세요. "
        "매주 1-2개 FAQ를 추가하고, 새 콘텐츠를 허브에 연결하는 습관을 들이면 "
        "3개월 후에는 견고한 GEO 기반이 완성됩니다."
    ))

    s = add_step(m, "quiz", "우선순위 판단", (
        "GEO 80/20 법칙에 따라 **가장 먼저** 실행해야 할 액션은?"
    ), 2)
    add_option(s, "A", "전체 사이트의 디자인을 리뉴얼한다", 0,
               "디자인 리뉴얼은 난이도가 높고 GEO 직접 효과가 제한적입니다. 콘텐츠 구조 개선이 우선입니다.", 1)
    add_option(s, "B", "기존 콘텐츠에 Answer-first 구조를 적용하고 헤딩 계층을 정리한다", 1,
               "정답입니다! Answer-first와 헤딩 정리는 난이도가 낮고 효과가 높아 가장 먼저 실행해야 할 액션입니다.", 2)
    add_option(s, "C", "새로운 SNS 채널을 개설한다", 0,
               "SNS 채널 개설은 GEO와 직접적 관련이 적습니다. 기존 콘텐츠 최적화가 우선입니다.", 3)
    add_option(s, "D", "AI 챗봇을 웹사이트에 설치한다", 0,
               "AI 챗봇 설치는 사용자 편의 기능이지 GEO 전략이 아닙니다. GEO는 콘텐츠 구조와 품질을 최적화하여 AI 인용을 높이는 것이 핵심입니다.", 4)

    s = add_step(m, "quiz", "효과적인 GEO 전략 조합", (
        "다음 중 GEO 효과가 가장 높은 전략 조합은?"
    ), 3)
    add_option(s, "A", "키워드 스터핑 + 메타 태그 최적화 + 백링크 구매", 0,
               "이것은 오래된 SEO 전략이며, GEO에서는 효과가 없거나 오히려 역효과가 날 수 있습니다.", 1)
    add_option(s, "B", "Answer-first + 헤딩 정리 + FAQ 추가 + 허브-클러스터 구축", 1,
               "정답입니다! 이 조합은 GEO의 핵심 신호(구조화, 명확성, 권위성)를 동시에 강화하는 최적의 전략 조합입니다.", 2)
    add_option(s, "C", "페이지 속도 최적화 + 모바일 반응형 + AMP 적용", 0,
               "이것은 기술적 SEO 전략입니다. GEO에서는 콘텐츠 구조와 품질이 더 중요합니다.", 3)
    add_option(s, "D", "SNS 마케팅 + 인플루언서 협업 + 유료 광고", 0,
               "SNS 마케팅과 인플루언서 협업은 브랜드 인지도에는 도움이 되지만, AI가 콘텐츠를 인용하는 GEO와는 직접적 관련이 적습니다.", 4)

    s = add_step(m, "practice", "실습: 우선순위 판단", (
        "service_custom 페이지를 개선할 시간이 2시간만 있습니다.\n\n"
        "GEO 80/20 법칙에 따라 가장 먼저 해야 할 작업은?"
    ), 4)
    add_option(s, "A", "전체 디자인을 리뉴얼한다", 0,
               "디자인 리뉴얼은 시간이 많이 걸리고 GEO 효과는 제한적입니다. 콘텐츠 구조 개선이 우선입니다.", 1)
    add_option(s, "B", "H1 재작성 + Answer-first 요약문 추가", 1,
               "정답입니다! H1 재작성과 Answer-first 요약문 추가는 30분 이내 가능하며, AI 인용 확률을 가장 크게 높이는 핵심 액션입니다.", 2)
    add_option(s, "C", "백링크를 10개 확보한다", 0,
               "백링크 확보는 2시간 안에 하기 어렵고, GEO에서는 콘텐츠 자체의 구조가 더 중요합니다.", 3)
    add_option(s, "D", "SNS에 페이지 링크를 공유한다", 0,
               "SNS 공유는 트래픽 유입에는 도움되지만, 페이지 자체의 GEO 최적화와는 거리가 있습니다.", 4)

    # --- Module 2-8: Stage 2 종합 평가 (quiz only, 5 steps) ---
    m = add_module(2, "2-8: Stage 2 종합 평가", "Stage 2에서 학습한 Technical GEO 기초를 종합적으로 평가합니다.", 8)

    s = add_step(m, "quiz", "종합 Q1: IA와 허브-클러스터", (
        "정보구조(IA)에서 허브-클러스터 모델의 핵심 효과는?"
    ), 1)
    add_option(s, "A", "페이지 로딩 속도가 빨라진다", 0,
               "허브-클러스터 모델은 페이지 속도와 직접적 관련이 없습니다. 콘텐츠 구조화가 핵심입니다.", 1)
    add_option(s, "B", "AI가 체계적 콘텐츠 구조를 통해 해당 주제의 전문성(Topical Authority)을 인식한다", 1,
               "정답입니다! 허브-클러스터 모델은 주제 전문성을 체계적으로 보여주어 AI의 인용 확률을 높입니다.", 2)
    add_option(s, "C", "광고 수익이 증가한다", 0,
               "허브-클러스터 모델의 핵심 목적은 광고 수익 증대가 아니라 주제 전문성(Topical Authority)을 체계적으로 보여주어 AI 인용을 높이는 것입니다.", 3)
    add_option(s, "D", "서버 비용이 절감된다", 0,
               "서버 비용 절감은 인프라 영역이며, 허브-클러스터 모델의 목적인 콘텐츠 구조화 및 주제 권위 강화와는 관련이 없습니다.", 4)

    s = add_step(m, "quiz", "종합 Q2: Answer-first", (
        "Answer-first 구조에서 문서 최상단에 위치해야 하는 것은?"
    ), 2)
    add_option(s, "A", "목차와 서론", 0,
               "목차는 유용하지만 Answer-first의 핵심은 핵심 답변을 최상단에 배치하는 것입니다.", 1)
    add_option(s, "B", "질문에 대한 핵심 답변 1-2문장", 1,
               "정답입니다! Answer-first는 핵심 답변을 문서 최상단에 배치하여 AI가 즉시 인용할 수 있게 합니다.", 2)
    add_option(s, "C", "저자 소개와 자격 증명", 0,
               "저자 정보는 권위성 강화에 도움되지만, Answer-first의 최상단에는 핵심 답변이 와야 합니다.", 3)
    add_option(s, "D", "관련 키워드 목록", 0,
               "키워드 목록을 나열하는 것은 Answer-first 구조와 관련이 없습니다. 문서 최상단에는 질문에 대한 핵심 답변이 자연스러운 문장으로 와야 합니다.", 4)

    s = add_step(m, "quiz", "종합 Q3: FAQ 설계", (
        "GEO에 효과적인 FAQ 설계에 대한 설명으로 **올바른** 것은?"
    ), 3)
    add_option(s, "A", "FAQ는 오래된 형식이므로 GEO에 효과가 없다", 0,
               "FAQ는 질문-답변 구조 덕분에 AI가 파싱하기 쉬워 GEO에서 매우 효과적인 콘텐츠 형태입니다. 오래된 형식이 아니라 AI 시대에 더 중요해졌습니다.", 1)
    add_option(s, "B", "실제 사용자 질문 기반 + Answer-first 적용 + Schema Markup으로 AI 인용에 최적화된다", 1,
               "정답입니다! 이 세 가지 요소를 결합하면 AI가 FAQ를 정확히 파싱하고 인용할 확률이 크게 높아집니다.", 2)
    add_option(s, "C", "FAQ는 10개 이하로만 작성해야 한다", 0,
               "FAQ 개수에 절대적 제한은 없습니다. 사용자 질문에 따라 적정량을 결정하면 됩니다.", 3)
    add_option(s, "D", "FAQ의 답변은 한 단어로만 작성해야 한다", 0,
               "한 단어 답변은 AI가 인용하기에 충분한 컨텍스트를 제공하지 못합니다. FAQ 답변은 2-4문장으로 간결하면서도 핵심 정보를 담아야 합니다.", 4)

    s = add_step(m, "quiz", "종합 Q4: 헤딩과 내부링크", (
        "헤딩 계층과 내부링크에 대한 설명으로 **올바른** 것은?"
    ), 4)
    add_option(s, "A", "H1은 페이지당 여러 개 사용하면 SEO/GEO 모두 좋다", 0,
               "H1은 페이지당 1개만 사용해야 합니다. 여러 H1을 사용하면 AI가 문서의 핵심 주제를 파악하지 못하여 구조가 혼란스러워집니다.", 1)
    add_option(s, "B", "내부링크의 앵커 텍스트는 '여기를 클릭'이 가장 효과적이다", 0,
               "'여기를 클릭'은 AI에게 링크 대상 페이지의 주제에 관한 의미 있는 컨텍스트를 제공하지 못합니다. 설명적 앵커 텍스트를 사용하세요.", 2)
    add_option(s, "C", "H1 > H2 > H3 순서를 지키고, 내부링크에 설명적 앵커 텍스트를 사용해야 한다", 1,
               "정답입니다! 올바른 헤딩 계층과 설명적 앵커 텍스트는 AI의 콘텐츠 이해를 크게 향상시킵니다.", 3)
    add_option(s, "D", "헤딩은 디자인용이며 AI는 헤딩을 무시한다", 0,
               "AI는 헤딩을 문서 구조를 파악하는 핵심 신호로 활용합니다. 절대 무시하지 않습니다.", 4)

    s = add_step(m, "quiz", "종합 Q5: 80/20 우선순위", (
        "GEO 80/20 법칙에 따른 올바른 우선순위는?"
    ), 5)
    add_option(s, "A", "허브-클러스터 구축 -> 전체 디자인 리뉴얼 -> SNS 마케팅", 0,
               "디자인 리뉴얼과 SNS 마케팅은 GEO 우선순위가 낮습니다. 콘텐츠 구조 개선이 먼저입니다.", 1)
    add_option(s, "B", "Answer-first + 헤딩 정리(1순위) -> FAQ + 허브-클러스터(2순위) -> 내부링크(3순위)", 1,
               "정답입니다! 난이도가 낮고 효과가 높은 액션부터 순서대로 실행하는 것이 80/20 법칙의 핵심입니다.", 2)
    add_option(s, "C", "백링크 구매 -> 키워드 스터핑 -> 메타 태그 최적화", 0,
               "백링크 구매와 키워드 스터핑은 오래된 SEO 전략이며, AI 인용 최적화를 목표로 하는 GEO와는 관련이 없습니다.", 3)
    add_option(s, "D", "모든 전략을 동시에 실행한다", 0,
               "모든 전략을 동시에 실행하면 리소스가 분산되고 효과 측정이 어렵습니다. 우선순위가 중요합니다.", 4)

    # ==================================================================
    # STAGE 3: 구조화데이터 & 스키마 마스터
    # ==================================================================
    add_stage(
        3,
        "구조화데이터 & 스키마 마스터",
        "JSON-LD 기반 구조화 데이터를 설계하여 AI의 콘텐츠 이해도를 높입니다.",
        3,
        '{"require_stage_complete": 2, "min_score_pct": 70}',
    )

    # --- Module 3-1: JSON-LD 기초 ---
    m = add_module(3, "3-1: JSON-LD 기초", "JSON-LD 구조화 데이터의 기본 개념과 구조를 학습합니다.", 1)

    add_step(m, "reading", "JSON-LD 구조화 데이터란", (
        "## JSON-LD 구조화 데이터란?\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>JSON-LD</strong> (JSON for Linked Data)<br>\n"
        "검색엔진과 AI가 이해하는 '콘텐츠 이력서' 코드 — Google 공식 권장 포맷</p>\n"
        "<p><strong>Schema.org</strong> (스키마닷오알지)<br>\n"
        "전 세계가 합의한 구조화 데이터 표준 단어장</p>\n"
        "<p><strong>Microdata / RDFa</strong><br>\n"
        "JSON-LD 외에 구조화 데이터를 표현하는 다른 방식 (현재는 JSON-LD가 주류)</p>\n"
        "</div>\n\n"
        "**JSON-LD(JSON for Linked Data)**는 웹페이지의 콘텐츠를 "
        "기계가 이해할 수 있는 형태로 표현하는 구조화 데이터 포맷입니다.\n\n"
        "### 왜 JSON-LD가 필요한가?\n\n"
        "AI와 검색엔진은 HTML 텍스트만으로는 콘텐츠의 **의미**를 정확히 파악하기 어렵습니다. "
        "예를 들어, '패스트캠퍼스'라는 텍스트가 회사명인지, 브랜드인지, 제품명인지 구분하지 못합니다. "
        "JSON-LD를 사용하면 이러한 정보를 **명시적으로** 기계에게 전달할 수 있습니다.\n\n"
        "### JSON-LD의 핵심 구성 요소\n\n"
        "1. **@context**: 어휘(vocabulary)의 출처를 지정합니다 (보통 https://schema.org)\n"
        "2. **@type**: 데이터의 유형을 지정합니다 (Organization, Article, Event 등)\n"
        "3. **속성(properties)**: 해당 타입의 구체적 정보를 담습니다\n\n"
        "### JSON-LD vs Microdata vs RDFa\n\n"
        '<div class="comparison-table">\n'
        '<div class="comp-header">구조화 데이터 포맷 비교</div>\n'
        '<table>\n'
        '<thead><tr><th>포맷</th><th>삽입 위치</th><th>장점</th><th>단점</th></tr></thead>\n'
        '<tbody>\n'
        '<tr class="highlight"><td class="label">JSON-LD</td><td>script 태그 (분리)</td><td>HTML과 독립, 유지보수 용이</td><td>별도 코드 필요</td></tr>\n'
        '<tr><td class="label">Microdata</td><td>HTML 속성 내</td><td>기존 HTML에 직접</td><td>복잡, 유지보수 어려움</td></tr>\n'
        '<tr><td class="label">RDFa</td><td>HTML 속성 내</td><td>유연함</td><td>학습 곡선 높음</td></tr>\n'
        '</tbody>\n'
        '</table>\n'
        '</div>\n\n'
        "Google은 **JSON-LD를 공식 권장**하고 있으며, GEO 관점에서도 JSON-LD가 가장 효과적입니다.\n\n"
        '<div class="code-example">\n'
        '<div class="code-label">JSON-LD 기본 구조</div>\n'
        "<pre><code>"
        '&lt;script type="application/ld+json"&gt;\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "Organization",\n'
        '  "name": "패스트캠퍼스",\n'
        '  "url": "https://b2b.fastcampus.co.kr",\n'
        '  "logo": "https://b2b.fastcampus.co.kr/logo.png"\n'
        "}\n"
        "&lt;/script&gt;"
        "</code></pre>\n"
        "</div>\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">Before: 스키마 없는 페이지</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>AI가 콘텐츠 유형을 추측해야 함</li>\n"
        "<li>검색 결과에 일반 텍스트만 표시</li>\n"
        "<li>리치 리절트 없음</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">After: 스키마 적용 페이지</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>AI가 콘텐츠 유형을 정확히 파악</li>\n"
        "<li>검색 결과에 리치 스니펫 표시</li>\n"
        "<li>AI 인용 확률 증가</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### Schema.org 주요 타입\n\n"
        "Schema.org는 수백 개의 타입을 정의하고 있지만, "
        "GEO에서 가장 자주 사용되는 핵심 타입은 다음과 같습니다.\n\n"
        "| 타입 | 용도 | 예시 |\n"
        "|------|------|------|\n"
        "| Organization | 회사/단체 정보 | 패스트캠퍼스 회사 정보 |\n"
        "| Article / BlogPosting | 블로그/뉴스 기사 | 인사이트 블로그 글 |\n"
        "| Event | 이벤트/세미나 | 온라인 교육 세미나 |\n"
        "| FAQPage | FAQ 페이지 | 자주 묻는 질문 |\n"
        "| BreadcrumbList | URL 경로 표시 | 사이트 네비게이션 |\n"
        "| Course | 교육 과정 | 교육 프로그램 정보 |\n\n"
        "각 타입마다 필수 속성과 권장 속성이 있으며, "
        "Google의 구조화 데이터 가이드에서 상세 스펙을 확인할 수 있습니다."
    ))

    s = add_step(m, "quiz", "JSON-LD 삽입 방법", (
        "JSON-LD를 HTML 페이지에 삽입하는 올바른 방법은?"
    ), 2)
    add_option(s, "A", "HTML body 텍스트에 직접 JSON 코드를 넣는다", 0,
               "JSON을 body에 직접 텍스트로 넣으면 사용자에게 코드가 그대로 보입니다. JSON-LD는 반드시 script 태그 안에 삽입해야 브라우저가 올바르게 처리합니다.", 1)
    add_option(s, "B", '<script type="application/ld+json"> 태그 안에 JSON-LD를 삽입한다', 1,
               "정답입니다! JSON-LD는 script 태그 내에 삽입하며, type 속성을 application/ld+json으로 지정하여 브라우저와 AI가 구조화 데이터임을 인식합니다.", 2)
    add_option(s, "C", "CSS 파일에 JSON-LD 코드를 포함시킨다", 0,
               "CSS 파일은 스타일 정보만 담는 곳입니다. JSON-LD는 HTML 문서의 script 태그에 삽입해야 검색엔진과 AI가 읽을 수 있습니다.", 3)
    add_option(s, "D", "이미지 alt 속성에 JSON-LD를 작성한다", 0,
               "alt 속성은 이미지 대체 텍스트용입니다. JSON-LD는 별도의 script 태그에 삽입해야 하며, 다른 HTML 속성에 넣으면 파싱되지 않습니다.", 4)

    s = add_step(m, "quiz", "@context의 역할", (
        "JSON-LD에서 @context 속성의 역할은 무엇인가요?"
    ), 3)
    add_option(s, "A", "웹페이지의 언어(한국어/영어)를 지정한다", 0,
               "언어 설정은 HTML의 lang 속성이 담당합니다. @context는 구조화 데이터의 어휘 출처를 지정하는 역할을 합니다.", 1)
    add_option(s, "B", "Schema.org 어휘를 참조한다는 것을 명시한다", 1,
               "정답입니다! @context는 JSON-LD에서 사용하는 용어(타입, 속성)가 Schema.org 표준을 따른다는 것을 선언하는 역할을 합니다.", 2)
    add_option(s, "C", "데이터의 생성 날짜를 기록한다", 0,
               "날짜 정보는 datePublished, dateCreated 등의 속성이 담당합니다. @context는 어휘 표준의 출처를 명시하는 메타 속성입니다.", 3)
    add_option(s, "D", "페이지의 URL 주소를 설정한다", 0,
               "URL 주소는 url 속성이 담당합니다. @context는 JSON-LD에서 사용되는 어휘(vocabulary)의 출처를 지정하는 핵심 선언입니다.", 4)

    s = add_step(m, "practice", "실습: Organization 스키마 완성", (
        "패스트캠퍼스 B2B 사이트에 Organization 스키마를 추가하려 합니다.\n\n"
        "다음 중 올바른 Organization 스키마 구성은?"
    ), 4)
    add_option(s, "A", '@type을 "Website"로 설정하고 title 속성만 추가한다', 0,
               "회사 정보를 표현하려면 @type은 Organization이어야 합니다. Website는 웹사이트 자체를 설명하는 별도 타입이니, 목적에 맞는 타입을 선택하세요.", 1)
    add_option(s, "B", '@type을 "Organization"으로 설정하고 name, url, logo, description 속성을 포함한다', 1,
               "정답입니다! Organization 타입에 name, url, logo, description을 포함하면 AI가 회사 정보를 정확히 파악할 수 있는 완전한 스키마가 됩니다.", 2)
    add_option(s, "C", '@type 없이 name과 url만 JSON 형태로 작성한다', 0,
               "@type은 JSON-LD에서 데이터의 유형을 정의하는 필수 요소입니다. @type이 없으면 AI가 이 데이터가 무엇을 의미하는지 파악할 수 없습니다.", 3)
    add_option(s, "D", '@type을 "Person"으로 설정하고 회사 정보를 넣는다', 0,
               "Person은 개인 정보를 표현하는 타입입니다. 회사 정보에는 Organization 타입을 사용해야 AI가 올바르게 분류할 수 있습니다.", 4)

    # --- Module 3-2: BreadcrumbList 실습 ---
    m = add_module(3, "3-2: BreadcrumbList 실습", "BreadcrumbList 스키마로 사이트 구조를 AI에 전달하는 방법을 학습합니다.", 2)

    add_step(m, "reading", "BreadcrumbList 스키마", (
        "## BreadcrumbList 스키마\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>BreadcrumbList</strong> (브레드크럼리스트)<br>\n"
        '"홈 &gt; 카테고리 &gt; 페이지" 경로를 AI에게 알려주는 구조화 데이터 타입</p>\n'
        "<p><strong>@context / @type</strong> (JSON-LD 필수 속성)<br>\n"
        "@context는 Schema.org 어휘 사용을 선언, @type은 데이터 유형을 지정</p>\n"
        "<p><strong>ListItem / position</strong><br>\n"
        "경로의 각 단계(ListItem)와 그 순서(position)를 나타내는 요소</p>\n"
        "</div>\n\n"
        "**BreadcrumbList**는 웹사이트의 URL 계층 구조를 구조화 데이터로 표현하는 스키마입니다. "
        "사용자가 현재 어떤 위치에 있는지 보여주는 '이동 경로'를 기계가 읽을 수 있게 합니다.\n\n"
        "### BreadcrumbList의 역할\n\n"
        "1. **URL 계층 명시**: 홈 > 카테고리 > 하위 페이지 구조를 명확히 전달\n"
        "2. **리치 리절트**: 검색 결과에 경로가 표시되어 클릭률 향상\n"
        "3. **AI 이해도 향상**: AI가 사이트 구조와 페이지 위치를 정확히 파악\n\n"
        "### 핵심 구조\n\n"
        "BreadcrumbList는 `itemListElement` 배열 안에 각 경로 항목을 `ListItem`으로 나열합니다. "
        "각 ListItem에는 `position`(순서), `name`(이름), `item`(URL)이 포함됩니다.\n\n"
        '<div class="code-example">\n'
        '<div class="code-label">BreadcrumbList JSON-LD 예시</div>\n'
        "<pre><code>"
        '&lt;script type="application/ld+json"&gt;\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "BreadcrumbList",\n'
        '  "itemListElement": [\n'
        "    {\n"
        '      "@type": "ListItem",\n'
        '      "position": 1,\n'
        '      "name": "홈",\n'
        '      "item": "https://b2b.fastcampus.co.kr"\n'
        "    },\n"
        "    {\n"
        '      "@type": "ListItem",\n'
        '      "position": 2,\n'
        '      "name": "리소스",\n'
        '      "item": "https://b2b.fastcampus.co.kr/resource"\n'
        "    },\n"
        "    {\n"
        '      "@type": "ListItem",\n'
        '      "position": 3,\n'
        '      "name": "인사이트",\n'
        '      "item": "https://b2b.fastcampus.co.kr/resource_insight"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "&lt;/script&gt;"
        "</code></pre>\n"
        "</div>\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">URL 계층 없음 (현재)</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>검색 결과: b2b.fastcampus.co.kr/resource_insight_aiforwork</li>\n"
        "<li>AI가 페이지 위치를 알 수 없음</li>\n"
        "<li>사이트 구조 파악 불가</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">BreadcrumbList 적용 후</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>검색 결과: 홈 > 리소스 > 인사이트 > AI for Work</li>\n"
        "<li>AI가 페이지의 사이트 내 위치를 정확히 인식</li>\n"
        "<li>콘텐츠 맥락 이해도 향상</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### b2b.fastcampus.co.kr의 BreadcrumbList 현황\n\n"
        "현재 b2b.fastcampus.co.kr에는 BreadcrumbList 스키마가 **0개** 적용되어 있습니다. "
        "이는 AI가 사이트의 URL 계층 구조를 전혀 파악할 수 없다는 의미입니다.\n\n"
        "#### 직접 설계 가이드\n\n"
        "1. 사이트의 주요 경로를 정의하세요:\n"
        "   - 홈 > 서비스 > 맞춤형 교육\n"
        "   - 홈 > 리소스 > 인사이트 > [개별 글]\n"
        "   - 홈 > 문의\n"
        "2. 각 페이지에 해당 경로의 BreadcrumbList JSON-LD를 추가하세요\n"
        "3. position 값은 반드시 1부터 순차적으로 부여하세요\n"
        "4. 마지막 항목(현재 페이지)에도 item URL을 포함하는 것이 권장됩니다"
    ))

    s = add_step(m, "quiz", "itemListElement와 position", (
        "BreadcrumbList의 itemListElement 배열에서 position 속성의 역할은?"
    ), 2)
    add_option(s, "A", "각 항목의 글자 크기를 지정한다", 0,
               "position은 시각적 스타일과 관련이 없습니다. BreadcrumbList에서 position은 URL 계층의 순서를 나타내는 숫자 값입니다.", 1)
    add_option(s, "B", "URL 계층에서의 순서를 반영하여 사이트 구조를 나타낸다", 1,
               "정답입니다! position 값은 1부터 시작하여 URL 계층의 깊이를 순서대로 나타냅니다. AI는 이 순서를 통해 페이지 간 계층 관계를 파악합니다.", 2)
    add_option(s, "C", "검색 결과에서의 노출 순위를 결정한다", 0,
               "position은 검색 순위와 무관합니다. BreadcrumbList의 position은 사이트 내 URL 경로의 계층적 순서를 표현하는 것이 목적입니다.", 3)
    add_option(s, "D", "항목의 중요도를 1~10 점수로 매긴다", 0,
               "position은 중요도 점수가 아닙니다. 홈(1) > 카테고리(2) > 하위 페이지(3) 처럼 URL 계층에서의 순서를 1부터 순차적으로 지정합니다.", 4)

    s = add_step(m, "quiz", "BreadcrumbList와 AI", (
        "BreadcrumbList 스키마가 AI에 도움이 되는 가장 큰 이유는?"
    ), 3)
    add_option(s, "A", "페이지의 디자인을 자동으로 개선해준다", 0,
               "BreadcrumbList는 디자인과 관련이 없습니다. 사이트 구조 정보를 기계 판독 가능한 형태로 제공하는 것이 핵심 역할입니다.", 1)
    add_option(s, "B", "사이트 구조와 페이지 위치를 기계가 판독할 수 있는 형태로 제공한다", 1,
               "정답입니다! BreadcrumbList는 AI에게 해당 페이지가 사이트 내 어떤 위치에 있는지를 명확히 알려주어 콘텐츠의 맥락 이해를 돕습니다.", 2)
    add_option(s, "C", "페이지 로딩 속도를 빠르게 해준다", 0,
               "BreadcrumbList는 성능 최적화와 관련이 없습니다. AI가 사이트 구조를 이해할 수 있도록 계층 정보를 제공하는 것이 목적입니다.", 3)
    add_option(s, "D", "백링크 수를 자동으로 늘려준다", 0,
               "BreadcrumbList는 백링크와 무관합니다. 사이트 내 URL 계층 구조를 구조화 데이터로 표현하여 AI의 사이트 이해도를 높이는 것이 핵심입니다.", 4)

    s = add_step(m, "practice", "실습: BreadcrumbList 설계", (
        "b2b.fastcampus.co.kr/resource_insight_aiforwork 페이지의\n"
        "BreadcrumbList를 설계합니다.\n\n"
        "올바른 breadcrumb 경로는?"
    ), 4)
    add_option(s, "A", "인사이트 > 홈 > 리소스 (역순으로 배치)", 0,
               "BreadcrumbList의 position은 홈에서 시작하여 현재 페이지까지 순차적으로 나열해야 합니다. 역순 배치는 AI가 계층 구조를 잘못 파악하게 합니다.", 1)
    add_option(s, "B", "홈 > 리소스 > 인사이트 (홈부터 현재 페이지까지 순서대로)", 1,
               "정답입니다! 홈(position:1) > 리소스(position:2) > 인사이트(position:3)로 URL 계층을 정확히 반영하는 올바른 구조입니다.", 2)
    add_option(s, "C", "홈 > AI for Work (중간 계층 생략)", 0,
               "중간 계층을 생략하면 AI가 사이트 구조를 정확히 파악할 수 없습니다. 모든 계층을 빠짐없이 포함하는 것이 중요합니다.", 3)
    add_option(s, "D", "resource_insight_aiforwork (URL만 단독 표시)", 0,
               "URL만 나열하는 것은 BreadcrumbList의 목적에 맞지 않습니다. 사람이 읽을 수 있는 이름(name)과 계층 순서(position)를 포함해야 합니다.", 4)

    # --- Module 3-3: Article & BlogPosting 스키마 ---
    m = add_module(3, "3-3: Article & BlogPosting 스키마", "Article 계열 스키마로 블로그/뉴스 콘텐츠를 구조화합니다.", 3)

    add_step(m, "reading", "Article & BlogPosting 스키마", (
        "## Article & BlogPosting 스키마\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Article / BlogPosting</strong> (아티클 / 블로그포스팅)<br>\n"
        "뉴스 기사나 블로그 글의 정보를 AI에게 전달하는 스키마 타입</p>\n"
        "<p><strong>datePublished / dateModified</strong><br>\n"
        "글의 발행일과 수정일 — AI가 콘텐츠의 최신성을 판단하는 근거</p>\n"
        "<p><strong>author</strong> (저자)<br>\n"
        "글을 쓴 사람이나 조직 — E-E-A-T 전문성 신호의 핵심</p>\n"
        "</div>\n\n"
        "**Article** 스키마는 뉴스 기사, 블로그 글 등 콘텐츠를 구조화 데이터로 표현하는 타입입니다. "
        "AI와 검색엔진이 글의 제목, 저자, 발행일, 이미지 등을 정확히 파악할 수 있게 합니다.\n\n"
        "### Article의 필수 및 권장 속성\n\n"
        '<div class="comparison-table">\n'
        '<div class="comp-header">Article 스키마 속성</div>\n'
        '<table>\n'
        '<thead><tr><th>속성</th><th>필수/권장</th><th>설명</th></tr></thead>\n'
        '<tbody>\n'
        '<tr class="highlight"><td class="label">headline</td><td>필수</td><td>기사/글의 제목</td></tr>\n'
        '<tr class="highlight"><td class="label">author</td><td>필수</td><td>저자 (Person 또는 Organization)</td></tr>\n'
        '<tr><td class="label">datePublished</td><td>권장</td><td>발행일 (ISO 8601 형식)</td></tr>\n'
        '<tr><td class="label">dateModified</td><td>권장</td><td>수정일 (ISO 8601 형식)</td></tr>\n'
        '<tr><td class="label">image</td><td>권장</td><td>대표 이미지 URL</td></tr>\n'
        '<tr><td class="label">publisher</td><td>권장</td><td>발행 조직</td></tr>\n'
        '<tr><td class="label">description</td><td>권장</td><td>글 요약</td></tr>\n'
        '</tbody>\n'
        '</table>\n'
        '</div>\n\n'
        "### Article 하위 타입\n\n"
        "- **Article**: 일반 기사 (가장 범용적)\n"
        "- **NewsArticle**: 뉴스 기사\n"
        "- **BlogPosting**: 블로그 글\n"
        "- **TechArticle**: 기술 문서\n\n"
        "패스트캠퍼스 인사이트 블로그에는 **BlogPosting**이 가장 적합합니다.\n\n"
        '<div class="code-example">\n'
        '<div class="code-label">Article JSON-LD 전체 예시</div>\n'
        "<pre><code>"
        '&lt;script type="application/ld+json"&gt;\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "BlogPosting",\n'
        '  "headline": "AI 시대, 기업 교육의 변화",\n'
        '  "author": {\n'
        '    "@type": "Organization",\n'
        '    "name": "패스트캠퍼스"\n'
        "  },\n"
        '  "datePublished": "2025-01-15",\n'
        '  "dateModified": "2025-02-10",\n'
        '  "image": "https://b2b.fastcampus.co.kr/images/ai-edu.jpg",\n'
        '  "publisher": {\n'
        '    "@type": "Organization",\n'
        '    "name": "패스트캠퍼스",\n'
        '    "logo": {\n'
        '      "@type": "ImageObject",\n'
        '      "url": "https://b2b.fastcampus.co.kr/logo.png"\n'
        "    }\n"
        "  },\n"
        '  "description": "생성형 AI가 기업 교육에 가져온 변화와 효과적인 도입 전략을 소개합니다."\n'
        "}\n"
        "&lt;/script&gt;"
        "</code></pre>\n"
        "</div>\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">스키마 없는 블로그 글</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>검색 결과에 일반 텍스트만 표시</li>\n"
        "<li>저자, 날짜 정보 불명확</li>\n"
        "<li>AI가 콘텐츠 신선도 판단 불가</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">Article 스키마 적용 후</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>리치 리절트에 저자, 날짜, 이미지 표시</li>\n"
        "<li>AI가 콘텐츠 신뢰도와 신선도를 판단</li>\n"
        "<li>인용 시 정확한 출처 정보 제공</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### NewsArticle vs BlogPosting vs Article 차이\n\n"
        "- **NewsArticle**: 시의성이 중요한 뉴스 기사에 적합합니다. "
        "Google News에 노출되려면 NewsArticle 타입이 필요합니다.\n"
        "- **BlogPosting**: 블로그 형식의 글에 적합합니다. "
        "개인 또는 기업 블로그 콘텐츠에 가장 많이 사용됩니다.\n"
        "- **Article**: 가장 범용적인 타입으로, 위 두 가지에 해당하지 않는 "
        "일반 기사나 콘텐츠에 사용합니다.\n\n"
        "패스트캠퍼스 인사이트 블로그(resource_insight)는 기업 교육 관련 "
        "인사이트를 다루는 블로그이므로 BlogPosting이 가장 적합합니다. "
        "시사 뉴스가 아니므로 NewsArticle은 적절하지 않습니다."
    ))

    s = add_step(m, "quiz", "Article 필수 속성", (
        "Article 스키마에서 Google이 필수로 요구하는 속성 조합은?"
    ), 2)
    add_option(s, "A", "url과 image", 0,
               "url과 image는 권장 속성이지만 필수는 아닙니다. Article 스키마에서 가장 핵심적인 필수 속성은 headline과 author입니다.", 1)
    add_option(s, "B", "headline과 author", 1,
               "정답입니다! headline(제목)과 author(저자)는 Article 스키마에서 반드시 포함해야 하는 필수 속성이며, AI가 콘텐츠를 식별하는 핵심 정보입니다.", 2)
    add_option(s, "C", "color와 font", 0,
               "color와 font는 Schema.org Article 타입의 속성이 아닙니다. 구조화 데이터는 시각적 스타일이 아닌 콘텐츠의 의미 정보를 담습니다.", 3)
    add_option(s, "D", "width와 height", 0,
               "width와 height는 ImageObject 등에 사용되는 속성이며, Article 스키마의 필수 속성이 아닙니다. headline과 author가 핵심입니다.", 4)

    s = add_step(m, "quiz", "datePublished 형식", (
        "Article 스키마에서 datePublished의 올바른 형식은?"
    ), 3)
    add_option(s, "A", "2025년 1월 15일 (한국어 날짜 표기)", 0,
               "한국어 날짜 표기는 사람에게는 읽기 쉽지만, 기계 판독에는 ISO 8601 형식이 필요합니다. 구조화 데이터에서는 표준 형식을 사용해야 합니다.", 1)
    add_option(s, "B", "ISO 8601 형식 (YYYY-MM-DD, 예: 2025-01-15)", 1,
               "정답입니다! ISO 8601 형식은 국제 표준 날짜 포맷으로, AI와 검색엔진이 날짜를 정확히 파싱하고 콘텐츠의 신선도를 판단할 수 있게 합니다.", 2)
    add_option(s, "C", "01/15/2025 (미국식 날짜 표기)", 0,
               "미국식 날짜 표기는 지역마다 해석이 달라 혼란을 줄 수 있습니다. 구조화 데이터에서는 전 세계 공통인 ISO 8601 형식을 사용해야 합니다.", 3)
    add_option(s, "D", "1705276800 (Unix 타임스탬프)", 0,
               "Unix 타임스탬프는 시스템 내부에서 사용되는 형식입니다. Schema.org 구조화 데이터에서는 사람과 기계 모두 읽을 수 있는 ISO 8601 형식을 표준으로 사용합니다.", 4)

    s = add_step(m, "practice", "실습: 인사이트 블로그에 Article 스키마 적용", (
        "패스트캠퍼스 인사이트 블로그 글에 적용할 스키마를 설계합니다.\n\n"
        "가장 적절한 스키마 구성은?"
    ), 4)
    add_option(s, "A", '@type을 "NewsArticle"로 설정하고 author를 문자열로 넣는다', 0,
               "인사이트 블로그는 뉴스 기사가 아니므로 NewsArticle보다 BlogPosting이 적합합니다. 또한 author는 문자열이 아닌 Person 또는 Organization 객체로 작성해야 합니다.", 1)
    add_option(s, "B", '@type을 "BlogPosting"으로 설정하고 author를 Organization 객체로, datePublished를 ISO 8601로 포함한다', 1,
               "정답입니다! 패스트캠퍼스 인사이트는 기업 블로그이므로 BlogPosting + Organization author + ISO 8601 날짜가 최적의 조합입니다.", 2)
    add_option(s, "C", '@type을 "Article"로 설정하고 headline만 포함한다', 0,
               "Article도 사용 가능하지만 BlogPosting이 더 구체적이고 적합합니다. 또한 headline만으로는 불충분하며, author와 datePublished도 함께 포함해야 합니다.", 3)
    add_option(s, "D", '@type을 "WebPage"로 설정하고 모든 정보를 description에 넣는다', 0,
               "WebPage는 블로그 글보다는 일반 페이지에 적합한 타입입니다. 블로그 콘텐츠에는 BlogPosting을 사용하고, 각 속성을 개별적으로 구분하여 작성해야 합니다.", 4)

    # --- Module 3-4: Event 스키마 ---
    m = add_module(3, "3-4: Event 스키마", "Event 스키마로 세미나/교육 이벤트를 구조화합니다.", 4)

    add_step(m, "reading", "Event 스키마 활용", (
        "## Event 스키마 활용\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Event</strong> (이벤트 스키마)<br>\n"
        "세미나, 웨비나, 교육 등 이벤트 정보를 AI에게 전달하는 구조화 데이터 타입</p>\n"
        "<p><strong>startDate / endDate</strong><br>\n"
        "이벤트 시작·종료 일시 — ISO 8601 형식(예: 2025-03-15T14:00:00+09:00)으로 작성</p>\n"
        "<p><strong>offers</strong> (제안/가격 정보)<br>\n"
        "이벤트의 가격, 통화, 구매 URL 등을 담는 속성</p>\n"
        "</div>\n\n"
        "**Event** 스키마는 세미나, 교육, 컨퍼런스 등 이벤트 정보를 구조화 데이터로 표현합니다. "
        "AI와 검색엔진이 이벤트의 일시, 장소, 가격 등을 정확히 파악할 수 있게 합니다.\n\n"
        "### Event 스키마의 핵심 속성\n\n"
        '<div class="comparison-table">\n'
        '<div class="comp-header">Event 스키마 속성</div>\n'
        '<table>\n'
        '<thead><tr><th>속성</th><th>설명</th><th>예시</th></tr></thead>\n'
        '<tbody>\n'
        '<tr class="highlight"><td class="label">name</td><td>이벤트 이름</td><td>생성형 AI 실무 세미나</td></tr>\n'
        '<tr><td class="label">startDate</td><td>시작 일시 (ISO 8601)</td><td>2025-03-15T14:00:00+09:00</td></tr>\n'
        '<tr><td class="label">endDate</td><td>종료 일시 (ISO 8601)</td><td>2025-03-15T17:00:00+09:00</td></tr>\n'
        '<tr><td class="label">location</td><td>장소 (Place 또는 VirtualLocation)</td><td>온라인</td></tr>\n'
        '<tr><td class="label">organizer</td><td>주최자</td><td>패스트캠퍼스</td></tr>\n'
        '<tr><td class="label">offers</td><td>가격/티켓 정보</td><td>무료/유료</td></tr>\n'
        '<tr><td class="label">eventAttendanceMode</td><td>참석 방식</td><td>Online/Offline/Mixed</td></tr>\n'
        '</tbody>\n'
        '</table>\n'
        '</div>\n\n'
        "### 온라인 이벤트 표현\n\n"
        "온라인 세미나나 웨비나의 경우 location을 **VirtualLocation**으로, "
        "eventAttendanceMode를 **OnlineEventAttendanceMode**로 설정합니다.\n\n"
        '<div class="code-example">\n'
        '<div class="code-label">Event JSON-LD (온라인 세미나)</div>\n'
        "<pre><code>"
        '&lt;script type="application/ld+json"&gt;\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "Event",\n'
        '  "name": "생성형 AI 기업 교육 세미나",\n'
        '  "startDate": "2025-03-15T14:00:00+09:00",\n'
        '  "endDate": "2025-03-15T17:00:00+09:00",\n'
        '  "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",\n'
        '  "eventStatus": "https://schema.org/EventScheduled",\n'
        '  "location": {\n'
        '    "@type": "VirtualLocation",\n'
        '    "url": "https://b2b.fastcampus.co.kr/seminar"\n'
        "  },\n"
        '  "organizer": {\n'
        '    "@type": "Organization",\n'
        '    "name": "패스트캠퍼스",\n'
        '    "url": "https://b2b.fastcampus.co.kr"\n'
        "  },\n"
        '  "offers": {\n'
        '    "@type": "Offer",\n'
        '    "price": "0",\n'
        '    "priceCurrency": "KRW",\n'
        '    "availability": "https://schema.org/InStock",\n'
        '    "url": "https://b2b.fastcampus.co.kr/seminar/register"\n'
        "  }\n"
        "}\n"
        "&lt;/script&gt;"
        "</code></pre>\n"
        "</div>\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">일반 검색 결과</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>제목과 설명만 표시</li>\n"
        "<li>일시, 장소 정보 없음</li>\n"
        "<li>AI가 이벤트임을 인식 못함</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">리치 이벤트 결과</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>날짜, 시간, 장소가 별도 표시</li>\n"
        "<li>가격 및 예약 가능 여부 표시</li>\n"
        "<li>AI가 이벤트 정보를 정확히 답변</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### 온라인 이벤트(VirtualLocation) 구현 방법\n\n"
        "코로나 이후 온라인 이벤트가 크게 증가했습니다. "
        "Schema.org는 세 가지 참석 방식을 지원합니다.\n\n"
        "1. **OnlineEventAttendanceMode**: 완전 온라인 (Zoom, 웨비나 등)\n"
        "2. **OfflineEventAttendanceMode**: 오프라인 (물리적 장소)\n"
        "3. **MixedEventAttendanceMode**: 하이브리드 (온/오프라인 동시)\n\n"
        "온라인 이벤트의 location은 VirtualLocation 타입을 사용하며, "
        "url 속성에 참여 링크를 넣습니다. 오프라인이라면 Place 타입에 "
        "address(PostalAddress)를 포함시킵니다."
    ))

    s = add_step(m, "quiz", "Event location 표현", (
        "Event 스키마에서 장소(location)를 표현하는 올바른 타입은?"
    ), 2)
    add_option(s, "A", "String 타입으로 장소명만 문자열로 입력한다", 0,
               "장소명만 문자열로 넣으면 AI가 온라인인지 오프라인인지 구분할 수 없습니다. Place 또는 VirtualLocation 타입을 사용하여 정확한 정보를 제공해야 합니다.", 1)
    add_option(s, "B", "Place 타입(오프라인) 또는 VirtualLocation 타입(온라인)을 사용한다", 1,
               "정답입니다! 오프라인 이벤트에는 Place와 address를, 온라인 이벤트에는 VirtualLocation과 url을 사용하여 AI가 이벤트 참석 방식을 정확히 파악할 수 있게 합니다.", 2)
    add_option(s, "C", "GPS 좌표만 숫자로 입력한다", 0,
               "GPS 좌표만으로는 장소의 이름이나 주소 정보가 부족합니다. Place 타입 안에 address와 함께 geo 속성을 포함하는 것이 올바른 방법입니다.", 3)
    add_option(s, "D", "location 속성은 필수가 아니므로 생략한다", 0,
               "location은 필수는 아니지만, AI와 사용자에게 이벤트 참석 방법을 알려주는 매우 중요한 속성입니다. 가능하면 항상 포함하는 것이 권장됩니다.", 4)

    s = add_step(m, "quiz", "온라인 이벤트 attendanceMode", (
        "온라인으로 진행되는 교육 세미나의 eventAttendanceMode 값은?"
    ), 3)
    add_option(s, "A", "OfflineEventAttendanceMode", 0,
               "OfflineEventAttendanceMode는 물리적 장소에서 진행되는 오프라인 이벤트에 사용합니다. 온라인 세미나에는 Online 모드를 사용해야 합니다.", 1)
    add_option(s, "B", "OnlineEventAttendanceMode", 1,
               "정답입니다! 온라인 세미나, 웨비나 등 인터넷을 통해 참석하는 이벤트에는 OnlineEventAttendanceMode를 사용하며, location은 VirtualLocation으로 설정합니다.", 2)
    add_option(s, "C", "HybridAttendanceMode", 0,
               "하이브리드 이벤트에는 MixedEventAttendanceMode를 사용합니다. 순수 온라인 이벤트에는 OnlineEventAttendanceMode가 올바른 값입니다.", 3)
    add_option(s, "D", "RemoteEventMode", 0,
               "RemoteEventMode는 Schema.org에 정의되지 않은 값입니다. 온라인 이벤트의 공식 값은 OnlineEventAttendanceMode입니다.", 4)

    s = add_step(m, "practice", "실습: 온라인 세미나 Event 스키마 적용", (
        "패스트캠퍼스에서 '생성형 AI 업무 혁신 세미나'를 온라인으로 개최합니다.\n\n"
        "가장 적절한 스키마 구성은?"
    ), 4)
    add_option(s, "A", '@type을 "Course"로 설정하고 location을 문자열 "온라인"으로 입력한다', 0,
               "세미나는 Course(교육 과정)가 아닌 Event 타입이 적합합니다. 또한 location은 문자열이 아닌 VirtualLocation 객체로 작성해야 AI가 정확히 파싱합니다.", 1)
    add_option(s, "B", '@type을 "Event"로 설정하고 eventAttendanceMode를 OnlineEventAttendanceMode, location을 VirtualLocation으로 구성한다', 1,
               "정답입니다! Event 타입에 OnlineEventAttendanceMode와 VirtualLocation을 조합하면 AI가 온라인 세미나의 모든 정보를 정확히 파악하고 답변에 활용할 수 있습니다.", 2)
    add_option(s, "C", '@type을 "Event"로 설정하되 location과 attendanceMode는 생략한다', 0,
               "location과 attendanceMode를 생략하면 AI가 이벤트의 참석 방식을 파악할 수 없습니다. 온라인 이벤트의 핵심 정보이므로 반드시 포함해야 합니다.", 3)
    add_option(s, "D", '@type을 "WebPage"로 설정하고 이벤트 정보를 description에 모두 넣는다', 0,
               "WebPage는 이벤트를 표현하기에 적합하지 않습니다. Event 타입을 사용하고 각 속성을 구분하여 작성해야 AI가 일시, 장소, 가격 등을 개별적으로 파싱할 수 있습니다.", 4)

    # --- Module 3-5: FAQPage 스키마 ---
    m = add_module(3, "3-5: FAQPage 스키마", "FAQPage 스키마를 올바르게 구현하고 오용 사례를 학습합니다.", 5)

    add_step(m, "reading", "FAQPage 스키마 실전", (
        "## FAQPage 스키마 실전\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>FAQPage</strong> (FAQ페이지 스키마)<br>\n"
        "자주 묻는 질문 페이지를 AI에게 알려주는 구조화 데이터 타입</p>\n"
        "<p><strong>mainEntity</strong> (메인 엔터티)<br>\n"
        "FAQPage 안에 질문(Question) 목록을 담는 핵심 속성</p>\n"
        "<p><strong>Question / Answer</strong><br>\n"
        "각 질문과 답변을 한 쌍으로 묶는 스키마 요소</p>\n"
        "</div>\n\n"
        "**FAQPage** 스키마는 자주 묻는 질문(FAQ) 페이지를 구조화 데이터로 표현합니다. "
        "질문(Question)과 답변(Answer)의 중첩 구조로, AI가 Q&A 쌍을 정확히 파싱할 수 있게 합니다.\n\n"
        "### FAQPage 구조\n\n"
        "FAQPage는 `mainEntity` 속성 안에 Question 객체 배열을 포함합니다. "
        "각 Question은 `name`(질문 텍스트)과 `acceptedAnswer`(Answer 객체)를 가집니다.\n\n"
        '<div class="tree-diagram">\n'
        '<div class="tree-title">FAQPage 스키마 계층 구조</div>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node root">FAQPage</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">mainEntity: [ ]</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">Question</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">name: 질문 텍스트</span></li>\n'
        '<li class="tree-item"><span class="tree-node">acceptedAnswer</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">Answer</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">text: 답변 텍스트</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</div>\n\n'
        "### Google 가이드라인\n\n"
        "1. **실제 FAQ만** 사용: 마케팅 문구를 FAQ로 포장하면 안 됨\n"
        "2. **중복 금지**: 같은 질문을 여러 페이지에 중복 사용하지 않기\n"
        "3. **답변 충실**: 답변에 실질적이고 완전한 정보 포함\n"
        "4. **페이지당 1개**: 한 페이지에 FAQPage 스키마는 1개만\n\n"
        '<div class="code-example">\n'
        '<div class="code-label">FAQPage JSON-LD 예시</div>\n'
        "<pre><code>"
        '&lt;script type="application/ld+json"&gt;\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "FAQPage",\n'
        '  "mainEntity": [\n'
        "    {\n"
        '      "@type": "Question",\n'
        '      "name": "기업 맞춤형 교육의 최소 인원은?",\n'
        '      "acceptedAnswer": {\n'
        '        "@type": "Answer",\n'
        '        "text": "최소 10명부터 교육이 가능하며, 교육 인원에 따라 커리큘럼을 맞춤 설계합니다."\n'
        "      }\n"
        "    },\n"
        "    {\n"
        '      "@type": "Question",\n'
        '      "name": "교육 기간은 얼마나 걸리나요?",\n'
        '      "acceptedAnswer": {\n'
        '        "@type": "Answer",\n'
        '        "text": "기본 과정은 4주이며, 심화 과정은 8주입니다. 기업 일정에 맞춰 조정 가능합니다."\n'
        "      }\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "&lt;/script&gt;"
        "</code></pre>\n"
        "</div>\n\n"
        '<div class="callout warning">\n'
        "<p><strong>오용 주의:</strong> b2b.fastcampus.co.kr에서 발견된 실제 오용 사례입니다. "
        "Contact(문의) 페이지에 Course(교육 과정) 타입 스키마를 적용한 경우가 있습니다. "
        "이는 페이지의 실제 내용과 스키마 타입이 불일치하여 AI가 혼란을 겪으며, "
        "Google에서 스팸으로 판정될 수 있습니다.</p>\n"
        "</div>"
    ), 1, extension_md=(
        "### FAQ 스키마 오용 주의\n\n"
        "b2b.fastcampus.co.kr에서 발견된 스키마 오용 사례를 분석합니다.\n\n"
        '<div class="callout warning">\n'
        "<strong>사례: Contact 페이지에 Course 타입 적용</strong><br><br>\n"
        "문의 페이지의 실제 내용은 연락처 정보와 문의 양식인데, "
        "스키마에는 Course(교육 과정) 타입이 적용되어 있었습니다. "
        "이는 다음과 같은 문제를 일으킵니다:<br><br>\n"
        "1. <strong>AI 혼란</strong>: 페이지 내용(문의)과 스키마(교육 과정)가 불일치<br>\n"
        "2. <strong>신뢰도 하락</strong>: 부정확한 스키마는 사이트 전체 신뢰도를 떨어뜨림<br>\n"
        "3. <strong>패널티 위험</strong>: Google이 의도적 오용으로 판단하면 리치 리절트 제거\n"
        "</div>\n\n"
        "스키마는 반드시 페이지의 **실제 콘텐츠**와 일치하는 타입을 사용해야 합니다."
    ))

    s = add_step(m, "quiz", "FAQPage의 Question 타입", (
        "FAQPage 스키마에서 각 질문을 감싸는 타입은 무엇인가요?"
    ), 2)
    add_option(s, "A", "ListItem", 0,
               "ListItem은 BreadcrumbList 등 목록형 스키마에서 사용됩니다. FAQPage에서 각 질문은 Question 타입으로 감싸야 AI가 Q&A 구조를 정확히 파싱합니다.", 1)
    add_option(s, "B", "Question", 1,
               "정답입니다! FAQPage의 mainEntity 배열 안에 각 질문은 Question 타입으로, 답변은 그 안에 acceptedAnswer > Answer 타입으로 중첩됩니다.", 2)
    add_option(s, "C", "FAQItem", 0,
               "FAQItem은 Schema.org에 정의되지 않은 타입입니다. FAQPage에서 각 질문은 공식 타입인 Question을 사용하고, 답변은 Answer 타입으로 작성합니다.", 3)
    add_option(s, "D", "HowToStep", 0,
               "HowToStep은 HowTo(방법 설명) 스키마에서 사용되는 타입입니다. FAQ의 질문에는 Question 타입을 사용해야 AI가 Q&A 쌍으로 인식합니다.", 4)

    s = add_step(m, "quiz", "FAQ 스키마 오용 사례", (
        "다음 중 FAQ 스키마 오용 사례에 해당하는 것은?"
    ), 3)
    add_option(s, "A", "FAQ 페이지에 FAQPage 스키마를 적용한 경우", 0,
               "FAQ 페이지에 FAQPage 스키마를 적용하는 것은 올바른 사용법입니다. 스키마는 페이지의 실제 내용과 일치할 때 가장 효과적입니다.", 1)
    add_option(s, "B", "Contact(문의) 페이지에 Course(교육 과정) 타입을 적용한 경우", 1,
               "정답입니다! 페이지의 실제 콘텐츠(문의 양식)와 스키마 타입(Course)이 불일치하는 대표적인 오용 사례이며, AI 혼란과 Google 패널티의 원인이 됩니다.", 2)
    add_option(s, "C", "블로그 글에 BlogPosting 스키마를 적용한 경우", 0,
               "블로그 글에 BlogPosting 스키마를 적용하는 것은 올바른 사용법입니다. 콘텐츠 유형과 스키마 타입이 일치합니다.", 3)
    add_option(s, "D", "이벤트 페이지에 Event 스키마를 적용한 경우", 0,
               "이벤트 페이지에 Event 스키마를 적용하는 것은 올바른 사용법입니다. 페이지 내용과 스키마가 정확히 매칭됩니다.", 4)

    s = add_step(m, "practice", "실습: service_custom FAQ 스키마 작성", (
        "service_custom 페이지에 3개 FAQ를 포함한 FAQPage 스키마를 작성합니다.\n\n"
        "올바른 FAQ 스키마 구조는?"
    ), 4)
    add_option(s, "A", "Question 없이 답변 텍스트만 나열한 구조", 0,
               "FAQPage 스키마에서 각 질문은 반드시 Question 타입으로 감싸고, 답변은 acceptedAnswer > Answer 구조로 중첩해야 AI가 Q&A 쌍을 정확히 파싱합니다.", 1)
    add_option(s, "B", "FAQPage > mainEntity 배열에 Question + acceptedAnswer(Answer) 3쌍을 포함한 구조", 1,
               "정답입니다! FAQPage의 mainEntity에 Question/Answer 쌍을 올바르게 중첩하면 AI가 각 질문과 답변을 정확히 매칭하여 인용할 수 있습니다.", 2)
    add_option(s, "C", "3개 FAQ를 각각 별도의 FAQPage 스키마로 분리한 구조", 0,
               "FAQPage 스키마는 페이지당 1개만 사용해야 합니다. 3개 FAQ는 하나의 FAQPage 안에 mainEntity 배열로 모두 포함하는 것이 올바른 구조입니다.", 3)
    add_option(s, "D", "Course 타입 안에 FAQ를 넣은 구조", 0,
               "FAQ는 Course가 아닌 FAQPage 타입으로 작성해야 합니다. Course 안에 FAQ를 넣으면 스키마 타입 불일치로 AI가 올바르게 파싱하지 못합니다.", 4)

    # --- Module 3-6: 스키마 검증 & 디버깅 ---
    m = add_module(3, "3-6: 스키마 검증 & 디버깅", "스키마 검증 도구를 활용하여 오류를 찾고 수정하는 방법을 학습합니다.", 6)

    add_step(m, "reading", "스키마 검증 도구와 디버깅", (
        "## 스키마 검증 도구와 디버깅\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Rich Results Test</strong> (리치 결과 테스트)<br>\n"
        "Google이 제공하는 무료 도구 — 구조화 데이터가 검색 결과에 잘 표시되는지 확인</p>\n"
        "<p><strong>Schema Markup Validator</strong> (스키마 검증기)<br>\n"
        "Schema.org 표준에 맞게 코드를 작성했는지 검사하는 도구</p>\n"
        "</div>\n\n"
        "구조화 데이터를 작성한 후에는 반드시 **검증 도구**로 오류 여부를 확인해야 합니다. "
        "오류가 있는 스키마는 리치 리절트에 표시되지 않을 뿐 아니라, AI가 잘못된 정보를 파싱할 수 있습니다.\n\n"
        "### 주요 검증 도구 3종\n\n"
        "1. **Google Rich Results Test**: 리치 리절트 적격 여부를 검사합니다\n"
        "   - URL: https://search.google.com/test/rich-results\n"
        "   - Google 검색 결과에서의 표시 미리보기 제공\n\n"
        "2. **Schema Markup Validator**: Schema.org 표준 준수 여부를 검사합니다\n"
        "   - URL: https://validator.schema.org\n"
        "   - 모든 Schema.org 타입에 대한 상세 검증\n\n"
        "3. **Google Search Console**: 실제 사이트의 구조화 데이터 현황을 모니터링합니다\n"
        "   - 사이트 전체의 스키마 오류/경고를 한눈에 확인\n"
        "   - 시간별 추이 파악 가능\n\n"
        "### 흔한 스키마 오류 5가지\n\n"
        "1. **@type 누락**: 타입 미지정 시 데이터 해석 불가\n"
        "2. **필수 속성 누락**: name, headline 등 required 속성 빠짐\n"
        "3. **잘못된 데이터 형식**: 날짜를 ISO 8601이 아닌 형식으로 입력\n"
        "4. **타입 불일치**: 페이지 내용과 다른 스키마 타입 적용\n"
        "5. **중첩 구조 오류**: 객체가 아닌 곳에 문자열 사용 (예: author를 문자열로)\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">오류 있는 스키마</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>@type 누락으로 데이터 해석 불가</li>\n"
        "<li>필수 속성(name) 누락</li>\n"
        "<li>날짜 형식 오류</li>\n"
        "<li>리치 리절트 표시 안 됨</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">검증 완료된 스키마</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>모든 필수 속성 포함</li>\n"
        "<li>올바른 데이터 형식 사용</li>\n"
        "<li>Rich Results Test 통과</li>\n"
        "<li>리치 리절트 정상 표시</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n\n"
        '<div class="callout tip">\n'
        "<p><strong>검증 도구 활용 팁:</strong></p>\n"
        "<p>1. <strong>Google Rich Results Test</strong>: 코드 스니펫이나 URL을 입력하여 즉시 테스트 가능</p>\n"
        "<p>2. <strong>Schema Markup Validator</strong>: JSON-LD 코드를 붙여넣기하여 상세 검증</p>\n"
        "<p>3. <strong>Search Console</strong>: 배포 후 지속적 모니터링으로 새로운 오류 감지</p>\n"
        "</div>"
    ), 1, extension_md=(
        "### 흔한 스키마 오류 패턴 상세\n\n"
        "#### 1. @type 누락\n\n"
        '<div class="code-example">'
        '<div class="code-label">잘못된 JSON-LD 예시</div>'
        '<pre><code>{ "@context": "https://schema.org", "name": "패스트캠퍼스" }</code></pre>'
        "</div>\n\n"
        "@type이 없으면 이 데이터가 Organization인지 Person인지 알 수 없습니다.\n\n"
        "#### 2. 필수 속성 누락\n\n"
        "Article에서 headline 없이 description만 있으면 검증 오류가 발생합니다.\n\n"
        "#### 3. 잘못된 날짜 형식\n\n"
        '`"datePublished": "2025년 1월"` 대신 `"datePublished": "2025-01-15"`를 사용하세요.\n\n'
        "#### 4. 타입과 내용 불일치\n\n"
        "문의 페이지에 Course 타입을 적용하면 AI가 혼란을 겪습니다.\n\n"
        "#### 5. 중첩 구조 실수\n\n"
        '<div class="code-example">'
        '<div class="code-label">잘못된 중첩</div>'
        '<pre><code>"author": "패스트캠퍼스"</code></pre>'
        "</div>\n\n"
        '<div class="code-example">'
        '<div class="code-label">올바른 중첩</div>'
        '<pre><code>"author": {"@type": "Organization", "name": "패스트캠퍼스"}</code></pre>'
        "</div>"
    ))

    s = add_step(m, "quiz", "스키마 검증 도구", (
        "구조화 데이터가 Google 리치 리절트에 적격한지 확인하는 도구는?"
    ), 2)
    add_option(s, "A", "Google PageSpeed Insights", 0,
               "PageSpeed Insights는 페이지 성능(로딩 속도)을 측정하는 도구입니다. 구조화 데이터 검증에는 Google Rich Results Test를 사용해야 합니다.", 1)
    add_option(s, "B", "Google Rich Results Test", 1,
               "정답입니다! Google Rich Results Test는 JSON-LD 등 구조화 데이터가 리치 리절트에 표시될 수 있는지 검증하고, 오류와 경고를 상세히 보여줍니다.", 2)
    add_option(s, "C", "Google Analytics", 0,
               "Google Analytics는 웹사이트 방문자 분석 도구입니다. 구조화 데이터의 유효성 검증에는 Rich Results Test나 Schema Markup Validator를 사용하세요.", 3)
    add_option(s, "D", "Google Ads Keyword Planner", 0,
               "Keyword Planner는 광고 키워드 조사 도구입니다. 구조화 데이터 검증과는 무관하며, Rich Results Test가 올바른 도구입니다.", 4)

    s = add_step(m, "quiz", "흔한 스키마 오류", (
        "스키마 검증에서 가장 흔하게 발생하는 오류 유형은?"
    ), 3)
    add_option(s, "A", "JSON-LD 코드의 글꼴이 잘못된 경우", 0,
               "글꼴은 스키마 오류와 관련이 없습니다. JSON-LD는 텍스트 데이터이므로 글꼴에 영향받지 않습니다. 가장 흔한 오류는 필수 속성 누락입니다.", 1)
    add_option(s, "B", "name, description 등 required 속성이 누락된 경우", 1,
               "정답입니다! 필수 속성 누락은 가장 흔한 스키마 오류이며, 검증 도구에서 즉시 감지됩니다. 각 타입의 필수 속성을 반드시 확인하세요.", 2)
    add_option(s, "C", "JSON-LD 파일의 크기가 너무 큰 경우", 0,
               "파일 크기는 일반적으로 스키마 오류의 원인이 아닙니다. 필수 속성 누락, 데이터 형식 오류, 타입 불일치가 훨씬 더 흔한 오류 패턴입니다.", 3)
    add_option(s, "D", "JSON-LD를 여러 언어로 번역한 경우", 0,
               "다국어 지원 자체는 스키마 오류가 아닙니다. 가장 흔한 오류는 필수 속성 누락이며, 올바른 구조와 형식을 갖추는 것이 중요합니다.", 4)

    s = add_step(m, "practice", "실습: 오류 있는 JSON-LD 디버깅", (
        "다음 JSON-LD에서 오류를 찾으세요.\n\n"
        "```json\n"
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "name": "패스트캠퍼스 B2B",\n'
        '  "url": "https://b2b.fastcampus.co.kr"\n'
        "}\n"
        "```\n\n"
        "이 JSON-LD의 핵심 오류는?"
    ), 4)
    add_option(s, "A", "url 속성이 잘못되었다", 0,
               "url 속성 자체는 올바른 형식입니다. 이 JSON-LD의 핵심 문제는 @type이 누락되어 AI가 이 데이터의 유형을 판별할 수 없다는 점입니다.", 1)
    add_option(s, "B", '@type 속성이 누락되어 데이터 유형을 알 수 없다', 1,
               "정답입니다! @type이 없으면 이 데이터가 Organization인지, Person인지, WebSite인지 AI가 판별할 수 없습니다. @type은 JSON-LD에서 가장 기본적인 필수 요소입니다.", 2)
    add_option(s, "C", "@context가 잘못되었다", 0,
               '@context는 "https://schema.org"로 올바르게 설정되어 있습니다. 이 JSON-LD의 핵심 문제는 @type 속성이 누락된 것입니다.', 3)
    add_option(s, "D", "name이 한국어로 되어 있어서 오류이다", 0,
               "Schema.org 속성 값은 어떤 언어로든 작성 가능합니다. 한국어 사용은 전혀 문제가 없습니다. 핵심 오류는 @type이 빠져 있다는 점입니다.", 4)

    # --- Module 3-7: Stage 3 종합 평가 ---
    m = add_module(3, "3-7: Stage 3 종합 평가", "Stage 3에서 학습한 구조화 데이터와 스키마 지식을 종합적으로 평가합니다.", 7)

    s = add_step(m, "quiz", "종합 Q1: JSON-LD vs Microdata", (
        "JSON-LD와 Microdata의 가장 큰 차이점은?"
    ), 1)
    add_option(s, "A", "JSON-LD는 유료이고 Microdata는 무료이다", 0,
               "두 포맷 모두 무료로 사용할 수 있는 오픈 표준입니다. 비용 차이는 없으며, 핵심 차이는 삽입 방식에 있습니다.", 1)
    add_option(s, "B", "JSON-LD는 script 태그에 분리 삽입하고, Microdata는 HTML 속성에 직접 삽입한다", 1,
               "정답입니다! JSON-LD는 별도의 script 태그에 삽입하여 HTML과 분리되므로 유지보수가 용이하고, Google도 이 방식을 공식 권장합니다.", 2)
    add_option(s, "C", "Microdata가 JSON-LD보다 성능이 좋다", 0,
               "성능 차이는 거의 없습니다. 두 포맷의 핵심 차이는 삽입 방식입니다. JSON-LD는 script 태그에 분리하고, Microdata는 HTML 속성에 직접 삽입합니다.", 3)
    add_option(s, "D", "JSON-LD는 영어만 지원한다", 0,
               "JSON-LD는 모든 언어를 지원합니다. 언어 제한은 없으며, 핵심 차이는 HTML과의 분리 여부(script 태그 vs HTML 속성)에 있습니다.", 4)

    s = add_step(m, "quiz", "종합 Q2: BreadcrumbList position", (
        "BreadcrumbList에서 position 속성이 나타내는 것은?"
    ), 2)
    add_option(s, "A", "페이지의 검색 순위", 0,
               "position은 검색 순위와 무관합니다. BreadcrumbList의 position은 사이트 URL 계층에서 해당 항목의 순서를 나타내며, 1부터 시작합니다.", 1)
    add_option(s, "B", "URL 계층에서의 순서 (홈=1, 카테고리=2, 하위 페이지=3 ...)", 1,
               "정답입니다! position은 홈에서 시작하여 현재 페이지까지의 URL 계층 순서를 1부터 순차적으로 나타냅니다. AI는 이를 통해 사이트 구조를 파악합니다.", 2)
    add_option(s, "C", "페이지의 중요도 점수", 0,
               "position은 중요도 점수가 아닙니다. URL 경로에서의 계층적 순서를 표현하는 값으로, 홈(1) > 카테고리(2) > 페이지(3) 순서입니다.", 3)
    add_option(s, "D", "페이지의 생성 순서", 0,
               "position은 페이지 생성 순서와 무관합니다. 사이트의 URL 계층 구조에서 홈부터 현재 페이지까지의 경로 순서를 나타내는 값입니다.", 4)

    s = add_step(m, "quiz", "종합 Q3: Article author 타입", (
        "Article 스키마에서 author 속성의 권장 타입은?"
    ), 3)
    add_option(s, "A", "단순 문자열 (예: 'author': '홍길동')", 0,
               "문자열로도 동작은 하지만, Google은 author를 객체 타입으로 작성할 것을 권장합니다. Person 또는 Organization 타입을 사용하면 더 풍부한 정보를 제공할 수 있습니다.", 1)
    add_option(s, "B", "Person 또는 Organization 타입 객체", 1,
               "정답입니다! author를 Person이나 Organization 객체로 작성하면 이름, URL, 소속 등 상세 정보를 포함할 수 있어 AI가 저자 정보를 더 정확히 파악합니다.", 2)
    add_option(s, "C", "URL 문자열 (예: 'author': 'https://example.com')", 0,
               "URL만으로는 저자가 누구인지 알 수 없습니다. Person 또는 Organization 타입 객체를 사용하여 name, url 등 속성을 포함하는 것이 권장됩니다.", 3)
    add_option(s, "D", "숫자형 ID (예: 'author': 12345)", 0,
               "숫자 ID는 내부 시스템용이며, 구조화 데이터에서는 의미가 없습니다. Person 또는 Organization 타입으로 사람이 읽을 수 있는 정보를 제공해야 합니다.", 4)

    s = add_step(m, "quiz", "종합 Q4: FAQPage 오용 주의", (
        "FAQPage 스키마 사용 시 반드시 지켜야 할 원칙은?"
    ), 4)
    add_option(s, "A", "가능한 많은 페이지에 FAQPage 스키마를 적용한다", 0,
               "모든 페이지에 FAQPage를 적용하면 오용으로 간주될 수 있습니다. FAQPage는 실제 FAQ 콘텐츠가 있는 페이지에만 적용해야 하며, 페이지 내용과 스키마가 일치해야 합니다.", 1)
    add_option(s, "B", "실제 FAQ가 아닌 콘텐츠에 FAQPage 스키마를 적용하면 안 된다", 1,
               "정답입니다! FAQPage 스키마는 실제 사용자 질문과 답변이 있는 페이지에만 적용해야 합니다. 마케팅 문구를 FAQ로 포장하거나 다른 콘텐츠에 적용하면 Google 패널티를 받을 수 있습니다.", 2)
    add_option(s, "C", "FAQPage는 홈페이지에만 적용해야 한다", 0,
               "FAQPage는 홈페이지뿐 아니라 실제 FAQ 콘텐츠가 있는 모든 페이지에 적용할 수 있습니다. 핵심은 페이지 내용과 스키마의 일치 여부입니다.", 3)
    add_option(s, "D", "FAQPage는 3개 미만의 질문만 포함해야 한다", 0,
               "질문 개수에 특별한 제한은 없습니다. 핵심 원칙은 실제 사용자 질문에 기반한 진정한 FAQ 콘텐츠에만 FAQPage 스키마를 적용하는 것입니다.", 4)

    s = add_step(m, "quiz", "종합 Q5: 스키마 검증 후 조치", (
        "스키마를 작성한 후 배포 전에 반드시 해야 할 일은?"
    ), 5)
    add_option(s, "A", "스키마 코드를 SNS에 공유한다", 0,
               "SNS 공유는 스키마 검증과 무관합니다. 배포 전에는 반드시 검증 도구로 오류가 없는지 확인하고, 문제를 수정한 후 배포해야 합니다.", 1)
    add_option(s, "B", "Rich Results Test에서 에러 0개를 확인한 후 배포한다", 1,
               "정답입니다! Google Rich Results Test에서 모든 에러를 해결하고 0개 에러 상태를 확인한 후 배포하면, 리치 리절트에 정상 표시되고 AI가 정확히 파싱할 수 있습니다.", 2)
    add_option(s, "C", "검증 없이 바로 배포하여 빠르게 적용한다", 0,
               "검증 없이 배포하면 오류가 있는 스키마가 적용되어 리치 리절트에 표시되지 않거나, 잘못된 정보가 AI에 전달될 수 있습니다. 반드시 검증 후 배포하세요.", 3)
    add_option(s, "D", "스키마 코드를 별도 파일로 저장해둔다", 0,
               "코드 관리는 좋은 습관이지만, 배포 전 핵심 단계는 검증 도구로 오류 여부를 확인하는 것입니다. Rich Results Test에서 에러가 0개인지 반드시 확인하세요.", 4)

    # ==================================================================
    # STAGE 4: 오프사이트 & 멘션 전략
    # ==================================================================
    add_stage(
        4,
        "오프사이트 & 멘션 전략",
        "백링크, 브랜드 멘션, PR, 소셜 유통 등 오프사이트 GEO 전략을 학습합니다.",
        4,
        '{"require_stage_complete": 3, "min_score_pct": 70}',
    )

    # --- Module 4-1: 오프사이트 GEO 개요 ---
    m = add_module(4, "4-1: 오프사이트 GEO 개요", "온사이트와 오프사이트 GEO의 차이를 이해하고 MECE 5갈래 전략을 학습합니다.", 1)

    add_step(m, "reading", "오프사이트 GEO란", (
        "## 오프사이트 GEO란?\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Off-site</strong> (오프사이트)<br>\n"
        "우리 웹사이트 바깥에서 벌어지는 활동 — 외부 매체, SNS, 리뷰 등</p>\n"
        "<p><strong>MECE</strong> (Mutually Exclusive, Collectively Exhaustive)<br>\n"
        "겹치지 않으면서 빠짐없이 — 전략을 분류할 때 빈틈 없이 나누는 원칙</p>\n"
        "<p><strong>Mention</strong> (멘션)<br>\n"
        "외부 사이트에서 우리 브랜드명이 언급되는 것 (링크 없이 이름만 나와도 해당)</p>\n"
        "</div>\n\n"
        "**오프사이트 GEO**는 자사 웹사이트 외부에서 AI와 검색엔진의 "
        "신뢰/권위 신호를 구축하는 전략입니다.\n\n"
        "### 온사이트 vs 오프사이트 GEO\n\n"
        "지금까지 학습한 **온사이트 GEO**는 자사 사이트의 콘텐츠, 구조, 스키마를 최적화하는 것이었습니다. "
        "반면 **오프사이트 GEO**는 외부 매체, 플랫폼, 커뮤니티 등에서 "
        "브랜드의 존재감과 신뢰도를 높이는 활동을 의미합니다.\n\n"
        "AI 모델은 학습 데이터에서 특정 브랜드가 **얼마나 자주, 어떤 맥락에서** "
        "언급되는지를 파악합니다. 따라서 오프사이트에서의 활동이 "
        "AI의 브랜드 인식에 직접적인 영향을 미칩니다.\n\n"
        "### MECE 5갈래 오프사이트 전략\n\n"
        "오프사이트 GEO는 다음 5가지 영역으로 나뉩니다:\n\n"
        "1. **백링크** — 외부 사이트에서 자사로 연결되는 링크 확보\n"
        "2. **멘션** — 링크 유무와 관계없이 브랜드가 언급되는 빈도 증가\n"
        "3. **PR (디지털 PR)** — 언론/전문 매체를 통한 공식적 노출\n"
        "4. **소셜** — 소셜 미디어를 통한 콘텐츠 확산과 브랜드 인지도 확대\n"
        "5. **리뷰/디렉토리** — 제3자 플랫폼에서의 평판과 정보 일관성 확보\n\n"
        "이 5가지를 **MECE(Mutually Exclusive, Collectively Exhaustive)** 관점에서 "
        "균형 있게 추진하면, AI가 브랜드를 다방면에서 인식하게 됩니다.\n\n"
        '<div class="tree-diagram">\n'
        '<div class="tree-title">MECE 5갈래 오프사이트 전략</div>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node root">오프사이트 GEO</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">백링크</span> — 링크 품질</li>\n'
        '<li class="tree-item"><span class="tree-node">멘션</span> — 빈도</li>\n'
        '<li class="tree-item"><span class="tree-node">PR</span> — 매체</li>\n'
        '<li class="tree-item"><span class="tree-node">소셜</span> — 확산</li>\n'
        '<li class="tree-item"><span class="tree-node">리뷰/디렉토리</span> — 일관성</li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</div>\n\n'
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">온사이트 GEO</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>자사 사이트 내부 최적화</li>\n"
        "<li>콘텐츠 구조, 스키마, 기술 SEO</li>\n"
        "<li>직접 통제 가능</li>\n"
        "<li>AI의 콘텐츠 이해도 향상</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">오프사이트 GEO</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>외부 플랫폼/매체 활용</li>\n"
        "<li>백링크, 멘션, PR, 소셜, 리뷰</li>\n"
        "<li>간접 영향 (제3자 활동)</li>\n"
        "<li>AI의 브랜드 신뢰/권위 구축</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### 오프사이트 신호가 AI에 영향을 미치는 메커니즘\n\n"
        "AI 언어 모델(GPT, Gemini 등)은 방대한 웹 데이터로 학습됩니다. "
        "이 과정에서 다음과 같은 오프사이트 신호를 흡수합니다:\n\n"
        "1. **빈도 효과**: 특정 브랜드가 여러 소스에서 반복 언급되면 "
        "AI가 해당 브랜드를 더 중요하고 신뢰할 수 있는 존재로 인식합니다.\n"
        "2. **맥락 효과**: 브랜드가 전문 매체, 학술 자료 등 권위 있는 소스에서 "
        "언급되면 해당 분야의 전문가로 인식됩니다.\n"
        "3. **일관성 효과**: 여러 소스에서 브랜드 정보가 일관되면 "
        "AI가 해당 정보를 사실로 받아들일 확률이 높아집니다.\n"
        "4. **링크 그래프**: 권위 있는 사이트에서의 백링크는 "
        "전통적 SEO뿐 아니라 AI 검색에서도 신뢰 신호로 작용합니다.\n\n"
        "따라서 오프사이트 GEO는 단순한 SEO 전략이 아니라, "
        "AI 시대의 브랜드 디지털 존재감을 구축하는 핵심 활동입니다."
    ))

    s = add_step(m, "quiz", "오프사이트 GEO 정의", (
        "오프사이트 GEO의 가장 정확한 정의는?"
    ), 2)
    add_option(s, "A", "자사 웹사이트의 HTML 구조를 개선하는 전략", 0,
               "HTML 구조 개선은 온사이트 GEO에 해당합니다. 오프사이트 GEO는 자사 사이트 외부에서 AI의 신뢰/권위 신호를 구축하는 전략을 의미합니다.", 1)
    add_option(s, "B", "자사 사이트 외부에서 AI의 신뢰/권위 신호를 구축하는 전략", 1,
               "정답입니다! 오프사이트 GEO는 백링크, 멘션, PR, 소셜, 리뷰 등 외부 활동을 통해 AI가 브랜드를 신뢰하고 권위 있게 인식하도록 만드는 전략입니다.", 2)
    add_option(s, "C", "소셜 미디어 광고를 집행하는 마케팅 전략", 0,
               "소셜 미디어는 오프사이트 GEO의 일부이지만, 광고 집행만을 의미하지는 않습니다. 오프사이트 GEO는 외부에서 AI의 신뢰 신호를 구축하는 포괄적 전략입니다.", 3)
    add_option(s, "D", "경쟁사 사이트를 분석하는 전략", 0,
               "경쟁사 분석은 별도의 활동입니다. 오프사이트 GEO는 자사 사이트 외부에서 백링크, 멘션, PR 등을 통해 AI에 대한 브랜드 신뢰도를 높이는 전략입니다.", 4)

    s = add_step(m, "quiz", "MECE 5갈래 전략 판별", (
        "다음 중 오프사이트 GEO의 MECE 5갈래 전략에 포함되지 않는 것은?"
    ), 3)
    add_option(s, "A", "백링크 확보 전략", 0,
               "백링크는 오프사이트 GEO 5갈래 전략 중 하나입니다. MECE 5갈래에 포함되지 않는 것은 키워드 스터핑으로, 이는 오프사이트가 아닌 온사이트의 부정적 기법입니다.", 1)
    add_option(s, "B", "디지털 PR 전략", 0,
               "디지털 PR은 오프사이트 GEO 5갈래 전략 중 하나입니다. 포함되지 않는 것은 키워드 스터핑으로, 이는 구식 온사이트 기법이자 Google이 패널티를 부과하는 스팸 행위입니다.", 3)
    add_option(s, "C", "키워드 스터핑", 1,
               "정답입니다! 키워드 스터핑은 오프사이트 GEO 전략이 아닙니다. 이는 구식 온사이트 기법으로 Google 패널티 대상입니다. MECE 5갈래는 백링크, 멘션, PR, 소셜, 리뷰/디렉토리입니다.", 2)
    add_option(s, "D", "리뷰/디렉토리 등록 전략", 0,
               "리뷰/디렉토리 등록은 오프사이트 GEO 5갈래 전략 중 하나입니다. 포함되지 않는 것은 키워드 스터핑으로, 이는 오프사이트 전략이 아닌 구식 온사이트 스팸 기법입니다.", 4)

    s = add_step(m, "practice", "실습: 오프사이트 전략 우선순위 판단", (
        "B2B 기업교육 회사가 오프사이트 GEO를 시작하려 합니다.\n\n"
        "가장 효과적인 첫 번째 전략은?"
    ), 4)
    add_option(s, "A", "모든 소셜 미디어에 동시에 계정을 만들고 홍보한다", 0,
               "모든 채널에 동시에 진출하면 리소스가 분산됩니다. B2B 기업교육의 경우, 먼저 업계 전문 매체에 기고하여 에디토리얼 링크를 확보하는 것이 신뢰 구축에 더 효과적입니다.", 1)
    add_option(s, "B", "업계 전문 매체에 기고 + 링크 확보", 1,
               "정답입니다! B2B 기업교육 분야에서는 HRD, 인재개발 등 업계 전문 매체에 사례 기고를 통해 에디토리얼 백링크를 확보하는 것이 가장 높은 신뢰 신호를 만듭니다.", 2)
    add_option(s, "C", "블로그 댓글에 링크를 대량으로 남긴다", 0,
               "댓글 스팸은 Google 패널티의 대상이며, AI 신뢰도에도 부정적 영향을 미칩니다. 업계 전문 매체에 기고하여 정당한 에디토리얼 링크를 확보하는 것이 올바른 접근입니다.", 3)
    add_option(s, "D", "경쟁사의 백링크를 그대로 복제한다", 0,
               "경쟁사 백링크를 분석하는 것은 참고가 되지만, 단순 복제는 불가능하고 비효과적입니다. 자사만의 전문성을 보여주는 기고와 PR을 통해 고유한 백링크를 확보하세요.", 4)

    # --- Module 4-2: 백링크 전략 ---
    m = add_module(4, "4-2: 백링크 전략", "GEO 시대의 백링크 품질 기준과 효과적인 백링크 확보 방법을 학습합니다.", 2)

    add_step(m, "reading", "GEO 시대의 백링크 전략", (
        "## GEO 시대의 백링크 전략\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Link Building</strong> (링크 빌딩)<br>\n"
        "다른 사이트에서 우리 사이트로의 링크(백링크)를 확보하는 활동</p>\n"
        "<p><strong>Editorial Link</strong> (에디토리얼 링크)<br>\n"
        "전문 매체가 자발적으로 우리 콘텐츠를 인용하며 거는 링크 — 가장 가치 높음</p>\n"
        "<p><strong>Domain Rating</strong> (도메인 등급, DR)<br>\n"
        "사이트 전체의 신뢰도와 권위를 점수(0~100)로 나타낸 지표</p>\n"
        "</div>\n\n"
        "**백링크**는 외부 웹사이트에서 자사 사이트로 연결되는 링크입니다. "
        "전통적 SEO에서도 핵심이었지만, GEO 시대에는 그 중요성이 더욱 커졌습니다.\n\n"
        "### 백링크 품질 피라미드\n\n"
        "모든 백링크가 동일한 가치를 가지지는 않습니다. "
        "품질에 따라 4단계로 나눌 수 있습니다:\n\n"
        "1. **에디토리얼 링크** (최상위) — 언론/전문 매체가 자발적으로 인용하는 링크\n"
        "2. **게스트포스트 링크** — 외부 매체에 기고하여 획득하는 링크\n"
        "3. **디렉토리 링크** — 비즈니스 디렉토리 등록을 통한 링크\n"
        "4. **스팸 링크** (최하위) — 댓글, PBN 등 부자연스러운 링크\n\n"
        "### 링크 품질 판단 기준\n\n"
        "- **관련성**: 링크를 제공하는 사이트가 자사 분야와 관련이 있는가?\n"
        "- **권위도**: 링크 제공 사이트의 도메인 권위(DA/DR)는 높은가?\n"
        "- **자연스러움**: 맥락상 자연스러운 링크인가, 인위적인가?\n"
        "- **앵커 텍스트**: 링크에 사용된 텍스트가 적절하고 다양한가?\n\n"
        "AI 모델은 학습 데이터에서 이러한 링크 패턴을 파악하여 "
        "브랜드의 신뢰도와 권위를 판단합니다.\n\n"
        '<div class="pyramid-chart">\n'
        '<div class="pyramid-title">백링크 품질 피라미드</div>\n'
        '<div class="pyramid-body">\n'
        '<div class="pyramid-level" style="--level: 1; --total: 4;"><span class="pyramid-label">에디토리얼 링크</span><span class="pyramid-detail">최고 품질</span></div>\n'
        '<div class="pyramid-level" style="--level: 2; --total: 4;"><span class="pyramid-label">게스트 포스트</span><span class="pyramid-detail">양호</span></div>\n'
        '<div class="pyramid-level" style="--level: 3; --total: 4;"><span class="pyramid-label">디렉토리 링크</span><span class="pyramid-detail">보통</span></div>\n'
        '<div class="pyramid-level" style="--level: 4; --total: 4;"><span class="pyramid-label">스팸 링크</span><span class="pyramid-detail">위험 ⚠</span></div>\n'
        '</div>\n'
        '</div>\n\n'
        '<div class="callout warning">\n'
        '<div class="callout-title">스팸 링크 위험 경고</div>\n'
        '<div class="callout-body">\n'
        "댓글 스팸, PBN(Private Blog Network), 링크 구매 등은 "
        "Google 수동 조치(Manual Action) 패널티의 대상입니다. "
        "한 번 패널티를 받으면 복구에 수개월이 걸리며, "
        "AI 검색에서도 브랜드 신뢰도가 크게 하락합니다. "
        "절대 사용하지 마세요.\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### DR/DA 지표 해석\n\n"
        "**DR(Domain Rating)**과 **DA(Domain Authority)**는 "
        "도메인의 백링크 프로필 강도를 0~100으로 나타내는 지표입니다.\n\n"
        "- **Ahrefs DR**: 해당 도메인으로 향하는 백링크의 양과 품질 기반\n"
        "- **Moz DA**: 링크 프로필, 도메인 나이, 트래픽 등 복합 요소 기반\n\n"
        "#### 실무 활용법\n\n"
        "- DR/DA 50 이상인 사이트에서의 백링크는 높은 가치를 가집니다.\n"
        "- 자사와 관련 분야의 고DR 사이트를 식별하여 기고/PR 대상으로 선정하세요.\n"
        "- Ahrefs의 'Link Intersect' 기능으로 경쟁사에는 링크가 있지만 "
        "자사에는 없는 사이트를 찾을 수 있습니다.\n"
        "- SEMrush의 'Backlink Gap' 도구도 유사한 기능을 제공합니다.\n\n"
        "단, DR/DA는 절대적 기준이 아닌 참고 지표로 활용하세요. "
        "관련성이 높은 DR 30 사이트의 링크가 관련 없는 DR 80 사이트보다 "
        "더 가치 있을 수 있습니다."
    ))

    s = add_step(m, "quiz", "백링크 품질 판단", (
        "다음 중 가장 높은 품질의 백링크 유형은?"
    ), 2)
    add_option(s, "A", "블로그 댓글에 남긴 링크", 0,
               "블로그 댓글 링크는 대부분 nofollow이며 스팸으로 간주됩니다. 가장 높은 품질의 백링크는 언론/전문 매체가 자발적으로 인용하는 에디토리얼 링크입니다.", 1)
    add_option(s, "B", "에디토리얼 링크 (언론/전문 매체의 자발적 인용)", 1,
               "정답입니다! 에디토리얼 링크는 제3자 전문 매체가 콘텐츠를 인용하며 자발적으로 삽입하는 링크로, 가장 높은 신뢰 신호를 전달합니다. AI도 이런 맥락적 인용을 중요하게 반영합니다.", 2)
    add_option(s, "C", "유료 링크 구매를 통한 링크", 0,
               "유료 링크 구매는 Google 가이드라인 위반이며 패널티 대상입니다. 자연스러운 에디토리얼 링크가 가장 높은 품질을 가집니다. 기고나 PR을 통해 정당하게 확보하세요.", 3)
    add_option(s, "D", "소셜 미디어 프로필의 링크", 0,
               "소셜 프로필 링크는 기본적인 온라인 존재감 표시이지만, 대부분 nofollow이고 SEO 가치가 제한적입니다. 에디토리얼 링크가 가장 높은 품질의 백링크입니다.", 4)

    s = add_step(m, "quiz", "스팸 백링크의 위험성", (
        "스팸 백링크(댓글 스팸, PBN 등)가 초래하는 가장 심각한 결과는?"
    ), 3)
    add_option(s, "A", "백링크 수가 증가하여 단기적으로 유리하다", 0,
               "스팸 백링크가 단기적으로 수를 늘릴 수 있지만, Google이 이를 감지하면 수동 조치 패널티를 부과합니다. 결과적으로 검색 순위 하락과 AI 신뢰도 저하를 초래합니다.", 1)
    add_option(s, "B", "Google 패널티 + AI 신뢰도 하락", 1,
               "정답입니다! 스팸 백링크는 Google 수동 조치(Manual Action) 패널티를 유발하고, AI 모델도 이러한 부자연스러운 링크 패턴을 감지하여 브랜드 신뢰도를 낮춥니다.", 2)
    add_option(s, "C", "별다른 영향이 없다", 0,
               "스팸 백링크는 심각한 결과를 초래합니다. Google 패널티로 검색 순위가 급락하고, AI 모델도 부자연스러운 링크 패턴으로 브랜드 신뢰도를 낮게 평가합니다.", 3)
    add_option(s, "D", "경쟁사에게만 피해가 간다", 0,
               "스팸 백링크의 피해는 자사에 직접 돌아옵니다. Google 패널티와 AI 신뢰도 하락이라는 이중 타격을 받게 되며, 복구에 수개월이 소요될 수 있습니다.", 4)

    s = add_step(m, "practice", "실습: B2B 교육 기업의 백링크 확보", (
        "B2B 기업교육 회사(패스트캠퍼스 B2B)가 "
        "고품질 백링크를 확보하려 합니다.\n\n"
        "가장 효과적인 방법은?"
    ), 4)
    add_option(s, "A", "다양한 블로그 댓글에 링크를 남긴다", 0,
               "댓글 스팸은 Google 패널티 대상이며 브랜드 이미지도 손상됩니다. HRD 전문 매체에 기업교육 성과 사례를 기고하여 에디토리얼 링크를 확보하는 것이 올바른 방법입니다.", 1)
    add_option(s, "B", "HRD 전문 매체에 기업교육 사례 기고", 1,
               "정답입니다! HRD, 인재개발 전문 매체에 실제 기업교육 성과 사례를 기고하면 관련성 높은 에디토리얼 백링크를 확보할 수 있고, 업계 전문가로서의 권위도 구축됩니다.", 2)
    add_option(s, "C", "링크 교환 네트워크에 가입한다", 0,
               "링크 교환 네트워크는 Google이 명시적으로 금지하는 링크 스킴에 해당합니다. 업계 전문 매체에 진정한 전문성을 보여주는 기고를 통해 자연스럽게 백링크를 확보하세요.", 3)
    add_option(s, "D", "자동 프로그램으로 대량 백링크를 생성한다", 0,
               "자동 백링크 생성은 가장 위험한 스팸 기법입니다. Google 패널티와 AI 신뢰도 하락을 초래합니다. HRD 전문 매체에 기고하여 정당한 에디토리얼 링크를 확보하세요.", 4)

    # --- Module 4-3: 브랜드 멘션 & PR ---
    m = add_module(4, "4-3: 브랜드 멘션 & PR", "브랜드 멘션과 디지털 PR이 GEO에 미치는 영향을 학습합니다.", 3)

    add_step(m, "reading", "브랜드 멘션과 디지털 PR", (
        "## 브랜드 멘션과 디지털 PR\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Digital PR</strong> (디지털 PR)<br>\n"
        "온라인 매체에 기고, 보도자료, 인터뷰 등을 통해 브랜드를 노출하는 활동</p>\n"
        "<p><strong>Implied Links</strong> (암시적 링크)<br>\n"
        "링크가 없어도 브랜드명 언급만으로 신뢰 신호가 되는 것 — Google 특허 기술</p>\n"
        "<p><strong>Authority</strong> (권위성)<br>\n"
        "제3자가 우리 브랜드를 인정하고 인용하는 정도 — E-E-A-T의 A</p>\n"
        "</div>\n\n"
        "**브랜드 멘션**은 외부 매체나 플랫폼에서 자사 브랜드가 언급되는 것을 말합니다. "
        "링크가 포함된 멘션과 링크 없는 멘션 모두 GEO에 중요합니다.\n\n"
        "### 링크 있는 멘션 vs 링크 없는 멘션\n\n"
        "- **링크 있는 멘션**: 백링크와 멘션의 이중 효과. 검색엔진과 AI 모두에게 "
        "직접적 신뢰 신호를 전달합니다.\n"
        "- **링크 없는 멘션**: 링크는 없지만 AI가 텍스트를 분석하여 "
        "브랜드 인지도와 권위를 간접적으로 인식합니다.\n\n"
        "Google은 2014년부터 **Implied Links(암시적 링크)** 특허를 보유하고 있으며, "
        "링크 없는 멘션도 신뢰 신호로 활용하고 있습니다.\n\n"
        "### E-E-A-T와의 관계\n\n"
        "E-E-A-T(Experience, Expertise, Authoritativeness, Trustworthiness)에서 "
        "오프사이트 활동은 특히 **Authoritativeness(권위성)**를 강화합니다. "
        "제3자가 브랜드를 인정하고 언급하는 것은 자기 주장보다 훨씬 강력한 권위 신호입니다.\n\n"
        "### 디지털 PR 전략\n\n"
        "1. **프레스 릴리즈**: 뉴스 배포 채널을 통한 공식 발표\n"
        "2. **기고 (바이라인 기사)**: 전문 매체에 전문가 명의로 기사 게재\n"
        "3. **인터뷰/코멘트**: 기자의 취재에 전문가 인터뷰 제공\n"
        "4. **데이터 PR**: 자사 데이터 기반 리서치 발표\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">링크 있는 멘션</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>백링크 + 멘션 이중 효과</li>\n"
        "<li>검색엔진 직접 신뢰 신호</li>\n"
        "<li>AI 학습 데이터에서 링크 관계 파악</li>\n"
        "<li>레퍼럴 트래픽 유입</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">링크 없는 멘션</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>AI가 텍스트 분석으로 브랜드 인식</li>\n"
        "<li>멘션 빈도로 브랜드 인지도 파악</li>\n"
        "<li>Google Implied Links 특허 활용</li>\n"
        "<li>브랜드 인지도 확산 효과</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n\n"
        '<div class="callout tip">\n'
        '<div class="callout-title">E-E-A-T와 오프사이트의 관계</div>\n'
        '<div class="callout-body">\n'
        "E-E-A-T 중 Authoritativeness(권위성)는 주로 오프사이트 활동에 의해 결정됩니다. "
        "자사 사이트에서 스스로를 전문가라고 주장하는 것보다, "
        "제3자 전문 매체에서 인용되고 멘션되는 것이 훨씬 강력한 권위 신호입니다.\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### 프레스 릴리즈 vs 에디토리얼의 차이\n\n"
        '<div class="compare-cards">\n'
        "<div>\n"
        "<strong>프레스 릴리즈</strong><br>\n"
        "- 기업이 직접 작성하여 뉴스와이어를 통해 배포<br>\n"
        "- 배포 비용 발생 (뉴스와이어 서비스 이용료)<br>\n"
        "- 많은 매체에 동일 내용 게재 가능<br>\n"
        "- 링크는 대부분 nofollow<br>\n"
        "- 멘션 효과는 있으나 에디토리얼보다 가치 낮음\n"
        "</div>\n"
        "<div>\n"
        "<strong>에디토리얼 기사</strong><br>\n"
        "- 기자/편집자가 판단하여 작성하는 기사<br>\n"
        "- 비용 없음 (뉴스 가치 기반)<br>\n"
        "- 해당 매체의 독자에게 노출<br>\n"
        "- 링크가 dofollow인 경우 높은 백링크 가치<br>\n"
        "- AI가 더 높은 신뢰 신호로 인식\n"
        "</div>\n"
        "</div>\n\n"
        "B2B 기업교육 분야에서는 프레스 릴리즈로 기본적인 멘션을 확보하고, "
        "동시에 업계 전문 매체와의 관계를 구축하여 에디토리얼 기사를 목표로 하는 "
        "투트랙 전략이 효과적입니다."
    ))

    s = add_step(m, "quiz", "링크 없는 멘션의 GEO 효과", (
        "링크 없는 브랜드 멘션이 GEO에 미치는 효과는?"
    ), 2)
    add_option(s, "A", "링크가 없으므로 GEO에 전혀 영향이 없다", 0,
               "링크가 없어도 AI는 텍스트를 분석하여 브랜드 멘션을 인식합니다. Google도 Implied Links 특허를 통해 링크 없는 멘션을 신뢰 신호로 활용하고 있습니다.", 1)
    add_option(s, "B", "AI가 멘션 빈도로 브랜드 권위를 간접 인식", 1,
               "정답입니다! AI 모델은 학습 데이터에서 특정 브랜드가 여러 소스에서 반복 언급되는 것을 파악합니다. 링크 없이도 멘션 빈도와 맥락으로 브랜드의 인지도와 권위를 간접 인식합니다.", 2)
    add_option(s, "C", "링크 없는 멘션은 부정적 효과만 있다", 0,
               "링크 없는 멘션도 긍정적 효과가 있습니다. AI는 텍스트 분석을 통해 멘션 빈도로 브랜드 인지도를 파악하고, 맥락에 따라 권위를 간접적으로 인식합니다.", 3)
    add_option(s, "D", "백링크보다 더 높은 SEO 가치를 가진다", 0,
               "링크 없는 멘션은 가치가 있지만, 직접적인 백링크보다는 효과가 제한적입니다. 멘션 빈도를 통해 AI가 브랜드 권위를 간접 인식하는 보조적 신호로 작용합니다.", 4)

    s = add_step(m, "quiz", "E-E-A-T와 오프사이트", (
        "E-E-A-T 중 오프사이트 활동으로 가장 직접적으로 강화할 수 있는 요소는?"
    ), 3)
    add_option(s, "A", "Experience (경험)", 0,
               "Experience는 주로 온사이트 콘텐츠에서 직접 경험을 보여주는 것으로 강화됩니다. 오프사이트에서 가장 직접적으로 강화되는 것은 Authoritativeness(권위성)입니다.", 1)
    add_option(s, "B", "Authoritativeness (권위성)", 1,
               "정답입니다! Authoritativeness는 제3자가 브랜드를 인정하고 인용하는 것으로 구축됩니다. 전문 매체의 멘션, 백링크, PR 활동이 모두 권위성 강화에 직접 기여합니다.", 2)
    add_option(s, "C", "Expertise (전문성)", 0,
               "Expertise는 주로 콘텐츠의 전문적 깊이로 보여주며 온사이트에서도 강화 가능합니다. 오프사이트에서 가장 직접적으로 강화되는 것은 제3자 인정에 기반한 Authoritativeness입니다.", 3)
    add_option(s, "D", "Trustworthiness (신뢰성)", 0,
               "Trustworthiness는 중요하지만 온사이트의 보안(HTTPS), 개인정보 정책 등으로도 강화됩니다. 오프사이트에서 가장 직접적으로 강화되는 것은 Authoritativeness(권위성)입니다.", 4)

    s = add_step(m, "practice", "실습: 패스트캠퍼스 B2B의 PR 전략 설계", (
        "패스트캠퍼스 B2B가 기업교육 시장에서 "
        "브랜드 권위를 높이기 위한 PR 전략을 수립하려 합니다.\n\n"
        "가장 효과적인 PR 전략은?"
    ), 4)
    add_option(s, "A", "유료 광고 기사를 대량으로 배포한다", 0,
               "유료 광고 기사(Advertorial)는 AI가 광고성 콘텐츠로 식별하여 신뢰도가 낮습니다. 실제 기업교육 성과 사례를 HR 전문 매체에 기고하는 것이 더 효과적입니다.", 1)
    add_option(s, "B", "기업교육 성과 사례를 HR 전문 매체에 기고", 1,
               "정답입니다! 실제 기업교육 성과 데이터를 기반으로 HR/인재개발 전문 매체에 기고하면, 에디토리얼 품질의 멘션과 백링크를 동시에 확보할 수 있어 AI 권위 신호를 극대화합니다.", 2)
    add_option(s, "C", "소셜 미디어에서 인플루언서 광고를 집행한다", 0,
               "인플루언서 광고도 효과가 있지만, B2B 기업교육에서는 업계 전문 매체의 기고가 더 직접적인 권위 신호를 만듭니다. HR 전문 매체에 성과 사례를 기고하는 것이 우선입니다.", 3)
    add_option(s, "D", "자사 블로그에 보도자료를 게시한다", 0,
               "자사 블로그 게시는 온사이트 활동이지 오프사이트 PR이 아닙니다. 기업교육 성과 사례를 HR 전문 매체에 기고하여 제3자 권위 신호를 확보하는 것이 효과적입니다.", 4)

    # --- Module 4-4: 엔터티 & 권위 신호 ---
    m = add_module(4, "4-4: 엔터티 & 권위 신호", "엔터티 기반 권위 구축과 Knowledge Graph 활용법을 학습합니다.", 4)

    add_step(m, "reading", "엔터티 기반 권위 구축", (
        "## 엔터티 기반 권위 구축\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Knowledge Graph</strong> (지식 그래프)<br>\n"
        "Google이 관리하는 거대한 지식 데이터베이스 — 사람, 기업, 장소의 관계를 연결</p>\n"
        "<p><strong>Entity</strong> (엔터티)<br>\n"
        "AI와 검색엔진이 고유하게 인식하는 개체 — 예: '패스트캠퍼스' = 교육 기업</p>\n"
        "<p><strong>Business Profile</strong> (비즈니스 프로필)<br>\n"
        "Google/네이버에 등록하는 공식 사업체 정보 (주소, 연락처, 영업시간 등)</p>\n"
        "</div>\n\n"
        "**엔터티(Entity)**란 검색엔진과 AI가 인식하는 고유한 개체입니다. "
        "사람, 장소, 조직, 개념 등이 모두 엔터티가 될 수 있습니다.\n\n"
        "### Knowledge Graph와 엔터티\n\n"
        "Google Knowledge Graph는 수십억 개의 엔터티와 그 관계를 저장하는 데이터베이스입니다. "
        "브랜드가 Knowledge Graph에 등록되면, Google과 AI가 "
        "해당 브랜드를 **고유한 존재**로 인식합니다.\n\n"
        "### 엔터티 인식의 주요 소스\n\n"
        "1. **위키피디아**: 가장 강력한 엔터티 소스. AI 학습 데이터의 핵심.\n"
        "2. **위키데이터**: 구조화된 엔터티 데이터베이스. Knowledge Graph에 직접 연동.\n"
        "3. **공식 웹사이트 스키마**: Organization 스키마로 엔터티 속성 명시.\n"
        "4. **비즈니스 프로필**: Google/네이버 비즈니스 프로필 등록.\n\n"
        "### 브랜드 엔터티 강화 방법\n\n"
        "1. **Organization 스키마 구현**: 공식 웹사이트에 구조화 데이터 추가\n"
        "2. **비즈니스 프로필 등록**: Google, 네이버 등 주요 플랫폼에 등록\n"
        "3. **일관된 NAP 정보**: Name, Address, Phone이 모든 곳에서 동일하게 유지\n"
        "4. **위키피디아 등재**: 주목할만한 기업이라면 위키피디아 문서 작성\n"
        "5. **sameAs 속성**: 스키마에서 공식 소셜/프로필 URL 연결\n\n"
        '<div class="tree-diagram">\n'
        '<div class="tree-title">엔터티 그래프: 브랜드 속성 연결</div>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node root">패스트캠퍼스</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">@type</span> → Organization</li>\n'
        '<li class="tree-item"><span class="tree-node">name</span> → 패스트캠퍼스</li>\n'
        '<li class="tree-item"><span class="tree-node">url</span> → 웹사이트</li>\n'
        '<li class="tree-item"><span class="tree-node">sameAs</span> → 소셜 프로필\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">LinkedIn</span></li>\n'
        '<li class="tree-item"><span class="tree-node">블로그</span></li>\n'
        '<li class="tree-item"><span class="tree-node">YouTube</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</div>'
    ), 1, extension_md=(
        "### Google Knowledge Panel 확보 방법\n\n"
        "Google Knowledge Panel은 검색 결과 우측에 표시되는 정보 패널입니다. "
        "이를 확보하면 브랜드의 엔터티 인식이 확인된 것입니다.\n\n"
        "#### Knowledge Panel 확보 단계\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">Knowledge Panel 확보 프로세스</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">Google 비즈니스 프로필 등록</div><div class="step-desc">사업자 정보를 정확히 입력하고 우편 인증을 완료합니다.</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">Organization 스키마 구현</div><div class="step-desc">공식 웹사이트에 name, url, logo, description, sameAs 등 핵심 속성을 포함합니다.</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">위키데이터 항목 생성</div><div class="step-desc">위키데이터에 조직 항목을 생성하고 공식 웹사이트 URL, 설립일, 소재지 등 속성을 추가합니다.</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">소셜 프로필 일관성 확보</div><div class="step-desc">모든 소셜 미디어 프로필에서 동일한 이름, 로고, 설명을 사용합니다.</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">5</div><div class="step-content"><div class="step-title">외부 멘션 확보</div><div class="step-desc">신뢰할 수 있는 매체에서 브랜드가 언급되면 Knowledge Panel 생성 확률이 높아집니다.</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'
        "Knowledge Panel이 생성되면 Google Search Console에서 "
        "'클레임(Claim)'하여 관리 권한을 확보할 수 있습니다."
    ))

    s = add_step(m, "quiz", "AI의 엔터티 인식 소스", (
        "AI가 브랜드를 엔터티로 인식하는 주요 소스로 올바른 조합은?"
    ), 2)
    add_option(s, "A", "개인 블로그, 커뮤니티 댓글, SNS 게시물", 0,
               "개인 블로그나 SNS 게시물은 엔터티 인식의 핵심 소스가 아닙니다. AI가 엔터티를 인식하는 주요 소스는 위키피디아, 위키데이터, Knowledge Graph입니다.", 1)
    add_option(s, "B", "위키피디아, 위키데이터, Knowledge Graph", 1,
               "정답입니다! 위키피디아는 AI 학습 데이터의 핵심 소스이고, 위키데이터는 구조화된 엔터티 데이터베이스이며, Knowledge Graph는 Google의 엔터티 인식 체계입니다. 이 세 가지가 AI 엔터티 인식의 핵심입니다.", 2)
    add_option(s, "C", "유료 광고 플랫폼, 이메일 마케팅, 전화번호부", 0,
               "광고 플랫폼이나 이메일은 엔터티 인식 소스가 아닙니다. AI가 엔터티를 인식하는 주요 소스는 위키피디아, 위키데이터, Knowledge Graph와 같은 구조화된 지식 소스입니다.", 3)
    add_option(s, "D", "Google Ads, 네이버 검색광고, 카카오 광고", 0,
               "광고 플랫폼은 노출을 위한 것이지 엔터티 인식 소스가 아닙니다. AI가 브랜드를 엔터티로 인식하는 주요 소스는 위키피디아, 위키데이터, Knowledge Graph입니다.", 4)

    s = add_step(m, "quiz", "엔터티 강화의 첫 단계", (
        "브랜드의 엔터티 인식을 강화하기 위한 가장 기본적인 첫 단계는?"
    ), 3)
    add_option(s, "A", "소셜 미디어에 광고를 집행한다", 0,
               "소셜 미디어 광고는 인지도에 도움이 되지만, 엔터티 인식 강화의 첫 단계는 아닙니다. 먼저 공식 웹사이트에 Organization 스키마를 구현하여 기계가 읽을 수 있는 엔터티 정보를 제공하세요.", 1)
    add_option(s, "B", "공식 웹사이트에 Organization 스키마 구현", 1,
               "정답입니다! Organization 스키마로 name, url, logo, sameAs 등 엔터티 속성을 명시하면, 검색엔진과 AI가 브랜드를 고유한 엔터티로 인식하는 기초가 마련됩니다.", 2)
    add_option(s, "C", "경쟁사의 엔터티 정보를 복사한다", 0,
               "경쟁사 정보를 복사하면 오히려 혼란을 초래합니다. 자사의 고유한 Organization 스키마를 공식 웹사이트에 구현하여 정확한 엔터티 정보를 제공하는 것이 첫 단계입니다.", 3)
    add_option(s, "D", "위키피디아에 바로 문서를 작성한다", 0,
               "위키피디아 등재는 중요하지만, 주목할만한 기업 요건을 충족해야 하고 검증이 까다롭습니다. 먼저 Organization 스키마와 비즈니스 프로필 등록으로 기초를 다지는 것이 올바른 순서입니다.", 4)

    s = add_step(m, "practice", "실습: 패스트캠퍼스의 엔터티 강화 전략", (
        "패스트캠퍼스가 AI와 검색엔진에서 "
        "브랜드 엔터티를 강화하려 합니다.\n\n"
        "가장 효과적인 첫 번째 조합은?"
    ), 4)
    add_option(s, "A", "유료 광고만 대량으로 집행한다", 0,
               "유료 광고는 트래픽에 도움이 되지만, 엔터티 인식에는 직접적 효과가 제한적입니다. Organization 스키마 구현과 네이버/구글 비즈니스 프로필 등록이 엔터티 강화의 기초입니다.", 1)
    add_option(s, "B", "Organization 스키마 + 네이버/구글 비즈니스 프로필 등록", 1,
               "정답입니다! Organization 스키마로 구조화된 엔터티 정보를 제공하고, 네이버/구글 비즈니스 프로필에 등록하면 주요 플랫폼에서 일관된 브랜드 엔터티가 확보됩니다.", 2)
    add_option(s, "C", "블로그에 회사 소개 글만 작성한다", 0,
               "블로그 글만으로는 구조화된 엔터티 정보가 전달되지 않습니다. Organization 스키마를 구현하고 네이버/구글 비즈니스 프로필에 등록하여 기계가 읽을 수 있는 엔터티를 만드세요.", 3)
    add_option(s, "D", "소셜 미디어 계정만 만든다", 0,
               "소셜 미디어 계정은 엔터티 구축에 보조적 역할을 합니다. 먼저 Organization 스키마와 비즈니스 프로필 등록으로 핵심 엔터티 기초를 마련하고, 소셜은 sameAs로 연결하세요.", 4)

    # --- Module 4-5: 소셜 유통 & 콘텐츠 확산 ---
    m = add_module(4, "4-5: 소셜 유통 & 콘텐츠 확산", "소셜 미디어를 활용한 콘텐츠 확산과 UTM 추적 방법을 학습합니다.", 5)

    add_step(m, "reading", "소셜 미디어와 콘텐츠 확산", (
        "## 소셜 미디어와 콘텐츠 확산\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Social Signal</strong> (소셜 신호)<br>\n"
        "SNS에서의 공유, 좋아요, 댓글 등이 브랜드 인지도에 미치는 간접 신호</p>\n"
        "<p><strong>Referrer</strong> (리퍼러, 유입 출처)<br>\n"
        "방문자가 어디서 왔는지 — linkedin.com, chatgpt.com 등 출발지 정보</p>\n"
        "</div>\n\n"
        "소셜 미디어는 GEO에 **간접적이지만 중요한** 영향을 미칩니다. "
        "소셜에서의 공유, 토론, 멘션은 콘텐츠의 확산과 브랜드 인지도를 높이며, "
        "이는 다시 백링크와 멘션 기회를 만듭니다.\n\n"
        "### 소셜 신호의 간접 효과\n\n"
        "Google은 소셜 신호가 직접적인 랭킹 요소가 아니라고 밝혔지만, "
        "소셜 활동의 간접 효과는 분명합니다:\n\n"
        "- **콘텐츠 발견**: 소셜 공유를 통해 더 많은 사람이 콘텐츠를 발견\n"
        "- **백링크 기회**: 콘텐츠를 본 블로거/기자가 자연스럽게 링크\n"
        "- **브랜드 멘션**: 소셜 토론에서 브랜드가 언급\n"
        "- **AI 학습 데이터**: 일부 AI 모델은 소셜 데이터도 학습에 활용\n\n"
        "### UTM 파라미터를 활용한 추적\n\n"
        "소셜에서 공유하는 URL에 UTM 파라미터를 추가하면, "
        "Google Analytics 4(GA4)에서 유입 경로를 정확히 추적할 수 있습니다.\n\n"
        "### B2B에서 LinkedIn의 중요성\n\n"
        "B2B 기업에서 가장 효과적인 소셜 채널은 **LinkedIn**입니다. "
        "기업 의사결정자(C-level, HR 담당자 등)가 집중되어 있어, "
        "전문 콘텐츠가 실제 구매 결정에 영향을 미칠 수 있습니다.\n\n"
        '<div class="code-example">\n'
        '<div class="code-label">UTM URL 예시</div>\n'
        "<pre><code>"
        "https://b2b.fastcampus.co.kr/insight/geo-guide\n"
        "  ?utm_source=linkedin\n"
        "  &amp;utm_medium=social\n"
        "  &amp;utm_campaign=geo_guide\n"
        "  &amp;utm_content=carousel_post\n\n"
        "utm_source   = 유입 채널 (linkedin, facebook, twitter)\n"
        "utm_medium   = 매체 유형 (social, email, cpc)\n"
        "utm_campaign = 캠페인 이름 (geo_guide)\n"
        "utm_content  = 콘텐츠 구분 (carousel_post, text_post)"
        "</code></pre>\n"
        "</div>\n\n"
        '<div class="callout key-point">\n'
        '<div class="callout-title">B2B에서 LinkedIn의 중요성</div>\n'
        '<div class="callout-body">\n'
        "B2B 마케팅에서 LinkedIn은 의사결정자 도달률이 가장 높은 채널입니다. "
        "기업교육 담당자, HR 리더, C-level 임원이 활발히 활동하며, "
        "전문적인 인사이트 콘텐츠에 대한 반응도가 높습니다. "
        "LinkedIn 기업 페이지와 개인 프로필을 모두 활용하세요.\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### 콘텐츠 시딩 전략\n\n"
        "**콘텐츠 시딩(Content Seeding)**은 핵심 콘텐츠를 다양한 채널에 "
        "전략적으로 배포하는 활동입니다.\n\n"
        "#### 인플루언서 시딩\n\n"
        "- 업계 전문가/인플루언서에게 콘텐츠를 사전 공유합니다.\n"
        "- 그들의 피드백을 반영하고, 공유를 요청합니다.\n"
        "- B2B에서는 LinkedIn에서 영향력 있는 HR/교육 전문가가 핵심 대상입니다.\n\n"
        "#### 커뮤니티 시딩\n\n"
        "- 관련 온라인 커뮤니티(네이버 카페, 페이스북 그룹 등)에 콘텐츠를 공유합니다.\n"
        "- 단순 링크 투하가 아닌, 가치 있는 토론을 유도하는 형태로 공유합니다.\n"
        "- 커뮤니티 규칙을 준수하고, 지나친 자기 홍보는 피합니다.\n\n"
        "#### 이메일 시딩\n\n"
        "- 기존 고객/리드에게 뉴스레터로 핵심 콘텐츠를 전달합니다.\n"
        "- UTM 파라미터로 이메일 유입을 별도 추적합니다.\n"
        "- utm_medium=email로 설정하여 소셜과 구분합니다."
    ))

    s = add_step(m, "quiz", "UTM 파라미터의 목적", (
        "소셜 미디어에서 공유하는 URL에 UTM 파라미터를 추가하는 주된 목적은?"
    ), 2)
    add_option(s, "A", "URL을 더 길게 만들어 신뢰감을 준다", 0,
               "URL 길이와 신뢰감은 관련이 없습니다. UTM 파라미터의 목적은 GA4(Google Analytics 4)에서 트래픽 유입 경로를 정확히 추적하기 위한 것입니다.", 1)
    add_option(s, "B", "트래픽 유입 경로를 GA4에서 추적하기 위해", 1,
               "정답입니다! UTM 파라미터(utm_source, utm_medium, utm_campaign 등)를 추가하면 GA4에서 어떤 소셜 채널, 어떤 캠페인에서 유입되었는지 정확히 추적할 수 있습니다.", 2)
    add_option(s, "C", "검색엔진 순위를 직접 높이기 위해", 0,
               "UTM 파라미터는 검색 순위에 직접적인 영향을 미치지 않습니다. 주된 목적은 GA4에서 트래픽 유입 경로(소스, 매체, 캠페인)를 정확히 추적하는 것입니다.", 3)
    add_option(s, "D", "소셜 미디어 알고리즘에 유리하게 작용한다", 0,
               "UTM 파라미터는 소셜 미디어 알고리즘과 무관합니다. 이 파라미터는 오직 GA4에서 유입 경로를 추적하기 위한 용도입니다. 어떤 채널이 효과적인지 데이터로 파악할 수 있습니다.", 4)

    s = add_step(m, "quiz", "B2B 소셜 채널 선택", (
        "B2B 기업교육 회사에서 가장 효과적인 소셜 미디어 채널은?"
    ), 3)
    add_option(s, "A", "TikTok (짧은 동영상 중심)", 0,
               "TikTok은 B2C 마케팅에 강점이 있지만, B2B 기업교육의 의사결정자 도달에는 제한적입니다. B2B에서는 의사결정자가 집중된 LinkedIn이 가장 효과적입니다.", 1)
    add_option(s, "B", "LinkedIn (의사결정자 집중)", 1,
               "정답입니다! LinkedIn은 기업 의사결정자(C-level, HR 담당자, 교육 담당자)가 가장 많이 활동하는 플랫폼입니다. 전문 콘텐츠의 반응도가 높아 B2B 마케팅에 최적입니다.", 2)
    add_option(s, "C", "Instagram (이미지 중심)", 0,
               "Instagram은 시각적 콘텐츠에 강점이 있지만, B2B 기업교육의 핵심 의사결정자가 모여 있지 않습니다. LinkedIn에서 전문 콘텐츠를 배포하는 것이 더 효과적입니다.", 3)
    add_option(s, "D", "Pinterest (핀보드 중심)", 0,
               "Pinterest는 라이프스타일/디자인 분야에 적합하며, B2B 기업교육과의 적합성이 낮습니다. 의사결정자가 집중된 LinkedIn이 B2B에서 가장 효과적인 채널입니다.", 4)

    s = add_step(m, "practice", "실습: UTM 링크 설계", (
        "패스트캠퍼스 B2B 인사이트 블로그의 GEO 가이드 글을 "
        "LinkedIn에 공유하려 합니다.\n\n"
        "올바른 UTM 파라미터 조합은?"
    ), 4)
    add_option(s, "A", "utm_source=google&utm_medium=cpc&utm_campaign=ads", 0,
               "이 조합은 Google 유료 광고(CPC)용입니다. LinkedIn 소셜 공유에는 utm_source=linkedin, utm_medium=social, utm_campaign=geo_guide가 올바른 조합입니다.", 1)
    add_option(s, "B", "utm_source=linkedin&utm_medium=social&utm_campaign=geo_guide", 1,
               "정답입니다! utm_source는 유입 채널(linkedin), utm_medium은 매체 유형(social), utm_campaign은 캠페인 이름(geo_guide)으로 설정하면 GA4에서 정확히 추적할 수 있습니다.", 2)
    add_option(s, "C", "utm_source=social&utm_medium=linkedin&utm_campaign=blog", 0,
               "source와 medium이 뒤바뀌었습니다. utm_source에는 구체적 채널(linkedin)을, utm_medium에는 매체 유형(social)을 넣는 것이 GA4의 표준 규칙입니다.", 3)
    add_option(s, "D", "UTM 파라미터 없이 원본 URL만 공유한다", 0,
               "UTM 없이 공유하면 GA4에서 유입 경로를 정확히 구분할 수 없습니다. utm_source=linkedin&utm_medium=social&utm_campaign=geo_guide를 추가하여 추적하세요.", 4)

    # --- Module 4-6: 리뷰 & 디렉토리 ---
    m = add_module(4, "4-6: 리뷰 & 디렉토리", "B2B 디렉토리 등록과 리뷰 관리를 통한 사회적 증명 구축 방법을 학습합니다.", 6)

    add_step(m, "reading", "리뷰와 디렉토리 전략", (
        "## 리뷰와 디렉토리 전략\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>NAP</strong> (Name, Address, Phone)<br>\n"
        "회사명·주소·전화번호 — 모든 플랫폼에서 동일하게 유지해야 AI가 같은 기업으로 인식</p>\n"
        "<p><strong>Review Signal</strong> (리뷰 신호)<br>\n"
        "제3자 플랫폼의 고객 리뷰와 평점 — AI가 브랜드 평판을 판단하는 근거</p>\n"
        "</div>\n\n"
        "**리뷰와 디렉토리**는 제3자 플랫폼에서의 브랜드 평판을 관리하고, "
        "AI가 참조하는 외부 소스에 일관된 정보를 제공하는 전략입니다.\n\n"
        "### B2B 디렉토리 등록\n\n"
        "B2B 기업에게 중요한 디렉토리 플랫폼:\n\n"
        "- **Google 비즈니스 프로필**: 검색 결과와 Knowledge Panel에 노출\n"
        "- **네이버 비즈니스**: 국내 검색 시장 점유율 1위 플랫폼\n"
        "- **LinkedIn 회사 페이지**: B2B 네트워킹의 핵심 플랫폼\n"
        "- **Clutch / G2**: 글로벌 B2B 서비스 리뷰 플랫폼\n"
        "- **크레딧잡 / 잡플래닛**: 국내 기업 정보/리뷰 플랫폼\n\n"
        "### 사회적 증명의 힘\n\n"
        "제3자 리뷰와 평가는 **사회적 증명(Social Proof)**으로 작용합니다. "
        "AI는 다양한 소스에서 브랜드에 대한 평가를 수집하고, "
        "이를 답변 생성 시 참조합니다.\n\n"
        "### AI의 리뷰 데이터 활용\n\n"
        "AI 모델은 리뷰 데이터를 다음과 같이 활용합니다:\n\n"
        "1. **긍정/부정 판단**: 전반적인 브랜드 평판 파악\n"
        "2. **강점/약점 식별**: 구체적인 서비스 특성 이해\n"
        "3. **비교 판단**: 경쟁 브랜드와의 비교 시 참조\n"
        "4. **신뢰도 보완**: 다양한 소스의 일관된 평가로 신뢰도 확보\n\n"
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">디렉토리 등록 전</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>AI가 브랜드 정보를 파편적으로 수집</li>\n"
        "<li>검색 결과에 공식 정보 부재</li>\n"
        "<li>경쟁사 대비 존재감 부족</li>\n"
        "<li>사회적 증명 없음</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">디렉토리 등록 후</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>AI가 일관된 브랜드 정보 확보</li>\n"
        "<li>검색 결과에 공식 프로필 노출</li>\n"
        "<li>다양한 플랫폼에서 브랜드 발견 가능</li>\n"
        "<li>리뷰 기반 사회적 증명 구축</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n\n"
        '<div class="callout key-point">\n'
        '<div class="callout-title">B2B 사회적 증명의 중요성</div>\n'
        '<div class="callout-body">\n'
        "B2B 구매 결정에서 사회적 증명은 매우 중요합니다. "
        "기업 담당자는 구매 전 반드시 리뷰와 사례를 확인하며, "
        "AI에게 추천을 요청할 때도 리뷰가 좋은 서비스를 우선 추천받습니다. "
        "따라서 디렉토리 등록과 적극적인 리뷰 수집은 필수입니다.\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### 리뷰 수집 자동화 방법\n\n"
        "리뷰를 체계적으로 수집하기 위한 자동화 전략:\n\n"
        "#### 1. 이메일 자동화\n\n"
        "- 서비스 이용 후 일정 기간(예: 교육 종료 후 1주) 후 자동 이메일 발송\n"
        "- 리뷰 작성 링크를 직접 포함하여 진입 장벽을 낮춤\n"
        "- 리뷰 작성 시 소정의 인센티브 제공 (단, 긍정 리뷰 유도는 금지)\n\n"
        "#### 2. NPS(Net Promoter Score) 연동\n\n"
        "- NPS 조사 결과에서 9-10점(Promoter)을 준 고객에게 리뷰 요청\n"
        "- 이미 만족도가 높은 고객이므로 긍정적 리뷰 확률이 높음\n"
        "- 자연스러운 리뷰 수집으로 플랫폼 정책 준수\n\n"
        "#### 3. CRM 연동\n\n"
        "- 고객 관리 시스템(CRM)에 리뷰 요청 트리거 설정\n"
        "- 프로젝트 완료, 재구매 시점 등 적절한 타이밍에 자동 요청\n"
        "- 각 디렉토리별 리뷰 URL을 관리하여 분산 수집"
    ))

    s = add_step(m, "quiz", "B2B 디렉토리 등록의 GEO 효과", (
        "B2B 디렉토리에 등록하는 것이 GEO에 미치는 주된 효과는?"
    ), 2)
    add_option(s, "A", "직접적인 검색 순위 상승", 0,
               "디렉토리 등록이 직접적으로 검색 순위를 올리지는 않습니다. 주된 GEO 효과는 다양한 외부 소스에서 브랜드 정보의 일관성을 확보하여 AI의 신뢰도를 높이는 것입니다.", 1)
    add_option(s, "B", "다양한 외부 소스에서 브랜드 정보 일관성 확보", 1,
               "정답입니다! 여러 디렉토리에 일관된 브랜드 정보(이름, 주소, 설명 등)를 등록하면, AI가 다양한 소스에서 동일한 정보를 확인하여 브랜드 신뢰도를 높게 평가합니다.", 2)
    add_option(s, "C", "유료 광고 비용 절감", 0,
               "디렉토리 등록은 광고 비용과 직접 관련이 없습니다. 핵심 효과는 다양한 외부 소스에서 브랜드 정보의 일관성을 확보하여 AI가 브랜드를 신뢰할 수 있게 만드는 것입니다.", 3)
    add_option(s, "D", "소셜 미디어 팔로워 증가", 0,
               "디렉토리 등록과 소셜 팔로워는 직접적 관련이 없습니다. 디렉토리의 GEO 효과는 다양한 외부 소스에서 브랜드 정보 일관성을 확보하여 AI 신뢰도를 높이는 것입니다.", 4)

    s = add_step(m, "quiz", "리뷰와 AI 답변의 관계", (
        "리뷰 데이터가 AI 답변에 영향을 미치는 방식은?"
    ), 3)
    add_option(s, "A", "AI는 리뷰 데이터를 전혀 참조하지 않는다", 0,
               "AI 모델은 웹에서 수집한 리뷰 데이터를 학습에 활용합니다. 제3자 평가를 신뢰성 신호로 반영하여 브랜드의 강점, 약점, 평판을 파악합니다.", 1)
    add_option(s, "B", "AI가 제3자 평가를 신뢰성 신호로 활용", 1,
               "정답입니다! AI 모델은 리뷰 데이터에서 긍정/부정 평가, 구체적 강점/약점을 파악합니다. 다양한 소스의 일관된 긍정적 리뷰는 강력한 신뢰성 신호로 작용합니다.", 2)
    add_option(s, "C", "부정적 리뷰만 AI에 반영된다", 0,
               "AI는 긍정적, 부정적 리뷰를 모두 참조합니다. 전반적인 평판을 종합적으로 판단하며, 다양한 소스의 제3자 평가를 신뢰성 신호로 활용합니다.", 3)
    add_option(s, "D", "리뷰 수가 많을수록 검색 순위가 직접 상승한다", 0,
               "리뷰 수와 검색 순위는 직접적 관계가 아닙니다. AI에 대한 리뷰의 효과는 제3자 평가로서의 신뢰성 신호이며, 평가의 일관성과 진정성이 핵심입니다.", 4)

    s = add_step(m, "practice", "실습: B2B 디렉토리 등록 우선순위", (
        "기업교육 B2B 서비스의 디렉토리 등록을 시작하려 합니다.\n\n"
        "가장 높은 우선순위의 디렉토리 조합은?"
    ), 4)
    add_option(s, "A", "해외 디렉토리만 대량 등록한다", 0,
               "해외 디렉토리만 등록하면 국내 시장에서의 존재감이 부족합니다. 먼저 네이버 비즈니스, 구글 비즈니스, LinkedIn 회사 페이지에 등록하여 핵심 플랫폼을 확보하세요.", 1)
    add_option(s, "B", "네이버 비즈니스 + 구글 비즈니스 + LinkedIn 회사 페이지", 1,
               "정답입니다! 국내 검색 1위인 네이버 비즈니스, 글로벌 검색 및 Knowledge Panel의 구글 비즈니스, B2B 네트워킹의 LinkedIn 회사 페이지가 가장 높은 우선순위입니다.", 2)
    add_option(s, "C", "개인 블로그에 회사 정보만 게시한다", 0,
               "개인 블로그는 공식 디렉토리가 아니므로 신뢰도가 낮습니다. 네이버 비즈니스, 구글 비즈니스, LinkedIn 등 공인된 플랫폼에 등록하는 것이 우선입니다.", 3)
    add_option(s, "D", "소규모 지역 디렉토리에만 등록한다", 0,
               "소규모 디렉토리도 도움이 되지만 우선순위가 아닙니다. 먼저 네이버/구글 비즈니스와 LinkedIn 회사 페이지에 등록하여 핵심 플랫폼에서 브랜드 존재감을 확보하세요.", 4)

    # --- Module 4-7: Stage 4 종합 평가 ---
    m = add_module(4, "4-7: Stage 4 종합 평가", "Stage 4에서 학습한 오프사이트 GEO 전략을 종합적으로 평가합니다.", 7)

    s = add_step(m, "quiz", "종합 Q1: 가장 직접적인 신뢰 신호", (
        "오프사이트 GEO 5갈래 전략 중 AI에게 가장 직접적인 신뢰 신호를 전달하는 것은?"
    ), 1)
    add_option(s, "A", "소셜 미디어 팔로워 수 증가", 0,
               "소셜 팔로워 수는 간접적 지표일 뿐 직접적 신뢰 신호는 아닙니다. 가장 직접적인 신뢰 신호는 제3자 전문 매체가 자발적으로 인용하는 에디토리얼 백링크입니다.", 1)
    add_option(s, "B", "에디토리얼 백링크 (제3자 전문 매체 인용)", 1,
               "정답입니다! 에디토리얼 백링크는 권위 있는 제3자 매체가 자발적으로 브랜드를 인용하는 것으로, AI가 가장 직접적으로 인식하는 신뢰/권위 신호입니다.", 2)
    add_option(s, "C", "디렉토리 등록 수", 0,
               "디렉토리 등록은 정보 일관성에 도움이 되지만, 가장 직접적인 신뢰 신호는 아닙니다. 제3자 전문 매체의 에디토리얼 백링크가 가장 강력한 신뢰 신호입니다.", 3)
    add_option(s, "D", "UTM 파라미터가 포함된 URL 수", 0,
               "UTM은 분석용 추적 파라미터일 뿐 AI의 신뢰 신호와 무관합니다. 가장 직접적인 신뢰 신호는 제3자 전문 매체가 자발적으로 인용하는 에디토리얼 백링크입니다.", 4)

    s = add_step(m, "quiz", "종합 Q2: 링크 없는 멘션의 효과", (
        "외부 매체에서 링크 없이 브랜드만 언급된 경우의 GEO 효과는?"
    ), 2)
    add_option(s, "A", "링크가 없으므로 GEO에 전혀 효과 없다", 0,
               "링크 없는 멘션도 GEO에 효과가 있습니다. AI는 텍스트 분석을 통해 브랜드 멘션 빈도를 파악하고, 이를 바탕으로 브랜드 인지도와 권위를 간접적으로 평가합니다.", 1)
    add_option(s, "B", "AI가 브랜드 인지도와 권위를 간접 파악하는 데 활용", 1,
               "정답입니다! AI 모델은 학습 데이터에서 브랜드 멘션 빈도와 맥락을 분석합니다. 링크 없이도 다양한 소스에서 반복 언급되면 브랜드의 인지도와 권위를 간접적으로 높게 평가합니다.", 2)
    add_option(s, "C", "백링크보다 더 큰 효과를 가진다", 0,
               "링크 없는 멘션도 가치가 있지만, 직접적인 백링크보다 효과가 크지는 않습니다. AI가 브랜드 인지도와 권위를 간접적으로 파악하는 보조 신호로 작용합니다.", 3)
    add_option(s, "D", "Google이 자동으로 링크를 생성해준다", 0,
               "Google이 자동으로 링크를 생성하지는 않습니다. 그러나 Google은 Implied Links 특허를 통해 링크 없는 멘션도 신뢰 신호로 활용하며, AI도 멘션을 통해 브랜드 권위를 간접 인식합니다.", 4)

    s = add_step(m, "quiz", "종합 Q3: 엔터티 구축의 첫 단계", (
        "브랜드의 엔터티 인식을 강화하기 위한 가장 올바른 첫 단계 조합은?"
    ), 3)
    add_option(s, "A", "소셜 미디어 광고만 집행한다", 0,
               "소셜 광고는 인지도에 도움이 되지만, 엔터티 구축의 첫 단계는 아닙니다. Organization 스키마를 구현하고 공식 프로필을 등록하여 기계가 읽을 수 있는 엔터티 정보를 먼저 제공하세요.", 1)
    add_option(s, "B", "Organization 스키마 + 공식 프로필 등록", 1,
               "정답입니다! Organization 스키마로 구조화된 엔터티 정보를 제공하고, Google/네이버 비즈니스 프로필에 등록하면 AI와 검색엔진이 브랜드를 고유한 엔터티로 인식하는 기초가 마련됩니다.", 2)
    add_option(s, "C", "위키피디아에 바로 문서를 작성한다", 0,
               "위키피디아 등재는 강력하지만 주목할만한 기업 요건이 필요합니다. 먼저 Organization 스키마와 공식 프로필 등록으로 기초 엔터티를 구축하는 것이 올바른 순서입니다.", 3)
    add_option(s, "D", "블로그에 회사 소개 글을 작성한다", 0,
               "블로그 글은 온사이트 활동이며 구조화된 엔터티 정보를 전달하지 못합니다. Organization 스키마를 구현하고 공식 프로필을 등록하여 엔터티 기초를 마련하세요.", 4)

    s = add_step(m, "quiz", "종합 Q4: B2B 소셜 전략 핵심", (
        "B2B 기업교육 회사의 소셜 미디어 전략에서 가장 핵심적인 활동은?"
    ), 4)
    add_option(s, "A", "모든 소셜 채널에 동일 콘텐츠를 동시에 게시한다", 0,
               "모든 채널에 동일 콘텐츠를 뿌리는 것은 비효율적입니다. B2B 기업교육에서는 LinkedIn에서 의사결정자(HR, C-level)를 대상으로 전문 콘텐츠를 배포하는 것이 핵심입니다.", 1)
    add_option(s, "B", "LinkedIn에서 의사결정자 대상 전문 콘텐츠 배포", 1,
               "정답입니다! B2B 기업교육에서 LinkedIn은 HR 담당자, 교육 담당자, C-level 등 의사결정자가 집중된 최적의 채널입니다. 전문적인 인사이트 콘텐츠로 이들에게 도달하는 것이 핵심입니다.", 2)
    add_option(s, "C", "TikTok에서 짧은 영상을 대량 제작한다", 0,
               "TikTok은 B2C에 적합하며, B2B 기업교육의 의사결정자 도달에는 한계가 있습니다. LinkedIn에서 의사결정자 대상 전문 콘텐츠를 배포하는 것이 더 효과적입니다.", 3)
    add_option(s, "D", "소셜 미디어는 B2B에 효과가 없으므로 하지 않는다", 0,
               "소셜 미디어, 특히 LinkedIn은 B2B 마케팅에서 매우 효과적입니다. 의사결정자가 집중된 LinkedIn에서 전문 콘텐츠를 배포하면 브랜드 인지도와 리드 확보에 기여합니다.", 4)

    s = add_step(m, "quiz", "종합 Q5: 온사이트 + 오프사이트 통합", (
        "온사이트 GEO와 오프사이트 GEO를 통합할 때 가장 효과적인 접근법은?"
    ), 5)
    add_option(s, "A", "오프사이트만 집중하면 온사이트는 필요 없다", 0,
               "오프사이트만으로는 완전한 GEO 전략이 아닙니다. 온사이트 콘텐츠의 품질과 구조가 먼저 확보되어야 오프사이트 확산이 효과를 발휘합니다. 두 가지를 통합적으로 추진하세요.", 1)
    add_option(s, "B", "온사이트 콘텐츠 품질 확보 후 오프사이트 확산이 효과적", 1,
               "정답입니다! 먼저 온사이트에서 고품질 콘텐츠와 기술적 최적화를 확보한 후, 이 콘텐츠를 오프사이트 채널로 확산하면 시너지 효과가 극대화됩니다. 탄탄한 기초 위에 확산 전략을 쌓으세요.", 2)
    add_option(s, "C", "온사이트와 오프사이트를 완전히 별개로 관리한다", 0,
               "온사이트와 오프사이트는 별개가 아니라 유기적으로 연결됩니다. 온사이트 콘텐츠 품질이 확보되어야 오프사이트 확산 시 링크와 멘션의 가치가 높아집니다. 통합적 접근이 필수입니다.", 3)
    add_option(s, "D", "온사이트를 무시하고 오프사이트 링크 구매에 집중한다", 0,
               "링크 구매는 Google 가이드라인 위반이며 패널티 대상입니다. 올바른 접근은 온사이트 콘텐츠 품질을 먼저 확보하고, 그 위에 자연스러운 오프사이트 확산 전략을 추진하는 것입니다.", 4)

    # ==================================================================
    # STAGE 5: 측정 & 실험 설계 실전
    # ==================================================================
    add_stage(
        5,
        "측정 & 실험 설계 실전",
        "GEO 성과를 측정하고 체계적 실험을 설계하여 지속적으로 개선합니다.",
        5,
        '{"require_stage_complete": 4, "min_score_pct": 70}',
    )

    # --- Module 5-1: KPI 3층 프레임워크 ---
    m = add_module(5, "5-1: KPI 3층 프레임워크", "GEO KPI 3층 프레임워크를 실전 수준으로 확장합니다.", 1)

    add_step(m, "reading", "GEO KPI 3층 프레임워크 실전", (
        "## GEO KPI 3층 프레임워크 실전\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Layer 1 / 2 / 3</strong> (KPI 3층 구조)<br>\n"
        "Layer 1(가시성) → Layer 2(행동) → Layer 3(권위) 순으로 성과를 계단식 측정</p>\n"
        "<p><strong>Citation Rate</strong> (인용률)<br>\n"
        "AI가 답변할 때 우리 콘텐츠를 출처로 인용하는 비율</p>\n"
        "<p><strong>Share of Voice</strong> (점유율)<br>\n"
        "경쟁사 대비 AI 답변에서 우리 브랜드가 차지하는 비율</p>\n"
        "</div>\n\n"
        "Stage 1에서 배운 3층 KPI를 실전 수준으로 확장합니다. "
        "각 층별로 구체적인 측정 지표, 도구, 벤치마크를 설정하여 "
        "GEO 전략의 성과를 체계적으로 추적할 수 있습니다.\n\n"
        "### Layer 1: Visibility (가시성)\n\n"
        "AI 답변에서 브랜드가 얼마나 노출되는지를 측정합니다.\n\n"
        "- **AI 인용 횟수**: ChatGPT, Gemini 등에서 브랜드/URL이 인용된 횟수\n"
        "- **Share of Voice**: 타겟 쿼리 대비 자사 인용 비율 (경쟁사 대비)\n"
        "- **인용 위치**: 답변 상단 vs 하단, 직접 링크 vs 텍스트 멘션\n\n"
        "### Layer 2: Behavior (행동)\n\n"
        "AI 인용이 실제 사용자 행동으로 이어지는지 측정합니다.\n\n"
        "- **AI 경유 트래픽**: AI 플랫폼에서 유입된 방문자 수\n"
        "- **체류 시간**: AI 경유 방문자의 평균 페이지 체류 시간\n"
        "- **페이지 뷰**: AI 경유 방문자의 평균 페이지 뷰 수\n\n"
        "### Layer 3: Authority (권위)\n\n"
        "장기적 브랜드 신뢰도와 권위를 측정합니다.\n\n"
        "- **도메인 평판 점수**: Moz DA, Ahrefs DR 등\n"
        "- **E-E-A-T 점수**: 경험, 전문성, 권위, 신뢰도 종합 평가\n"
        "- **브랜드 검색량**: 브랜드명 직접 검색 트렌드\n\n"
        '<div class="layer-box">\n'
        '<div class="layer-title">GEO KPI 3층 계단 구조</div>\n'
        '<div class="layer" style="--layer-color: #ea4335;"><div class="layer-label">Layer 3: Authority</div><div class="layer-desc">도메인 평판, E-E-A-T 종합 평가</div></div>\n'
        '<div class="layer-connector">↓</div>\n'
        '<div class="layer" style="--layer-color: #fbbc04;"><div class="layer-label">Layer 2: Behavior</div><div class="layer-desc">AI 경유 트래픽, 체류 시간</div></div>\n'
        '<div class="layer-connector">↓</div>\n'
        '<div class="layer" style="--layer-color: #34a853;"><div class="layer-label">Layer 1: Visibility</div><div class="layer-desc">AI 인용 횟수, Share of Voice</div></div>\n'
        '</div>\n\n'
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">SEO KPI</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>검색 순위 (SERP 포지션)</li>\n"
        "<li>오가닉 트래픽</li>\n"
        "<li>클릭률 (CTR)</li>\n"
        "<li>키워드 커버리지</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">GEO KPI</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>AI 인용 빈도 (Citation Rate)</li>\n"
        "<li>AI 경유 트래픽</li>\n"
        "<li>Share of Voice in AI</li>\n"
        "<li>E-E-A-T / 도메인 권위</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### KPI 대시보드 구성 예시\n\n"
        "효과적인 GEO KPI 대시보드는 다음과 같이 구성합니다:\n\n"
        '<div class="layer-box">\n'
        '<div class="layer" style="--layer-color: #1a73e8"><div class="layer-label">상단 영역</div><div class="layer-title">핵심 지표 요약</div><div class="layer-desc">이번 주 AI 인용 횟수 / 지난 주 대비 변화율 · AI 경유 트래픽 수 / 전체 대비 비율 · Share of Voice 스코어 / 경쟁사 대비 순위</div></div>\n'
        '<div class="layer-connector"></div>\n'
        '<div class="layer" style="--layer-color: #34a853"><div class="layer-label">중단 영역</div><div class="layer-title">트렌드 차트</div><div class="layer-desc">주간 AI 인용 횟수 추이 (최근 12주) · AI 경유 트래픽 추이 · 경쟁사 비교 Share of Voice 추이</div></div>\n'
        '<div class="layer-connector"></div>\n'
        '<div class="layer" style="--layer-color: #ea4335"><div class="layer-label">하단 영역</div><div class="layer-title">상세 데이터</div><div class="layer-desc">인용된 페이지별 상세 (URL, 인용 횟수, 인용 맥락) · 쿼리별 인용 현황 · E-E-A-T 세부 점수 변화</div></div>\n'
        '</div>'
    ))

    s = add_step(m, "quiz", "Visibility 핵심 지표", (
        "GEO KPI Layer 1(Visibility)의 핵심 지표는 무엇인가요?"
    ), 2)
    add_option(s, "A", "웹사이트의 Google 검색 순위", 0,
               "Google 검색 순위는 전통적 SEO의 핵심 지표입니다. GEO Layer 1(Visibility)의 핵심 지표는 AI 답변에서의 브랜드/URL 인용 횟수입니다. AI가 우리를 얼마나 자주 인용하는지가 가시성의 핵심입니다.", 1)
    add_option(s, "B", "AI 답변에서의 브랜드/URL 인용 횟수", 1,
               "정답입니다! Layer 1 Visibility의 핵심은 AI가 답변을 생성할 때 우리 브랜드나 URL을 얼마나 자주 인용하는지입니다. Share of Voice와 함께 AI 시대의 가시성을 측정하는 가장 기본적인 지표입니다.", 2)
    add_option(s, "C", "소셜 미디어 팔로워 수", 0,
               "소셜 미디어 팔로워 수는 오프사이트 지표이며, GEO KPI Layer 1의 핵심 지표는 아닙니다. AI 답변에서의 브랜드/URL 인용 횟수가 Visibility의 핵심입니다.", 3)
    add_option(s, "D", "월간 페이지뷰 수", 0,
               "월간 페이지뷰는 전통적 웹 분석 지표입니다. GEO Layer 1(Visibility)의 핵심은 AI 답변에서의 브랜드/URL 인용 횟수로, AI가 우리를 인용하는 빈도를 측정합니다.", 4)

    s = add_step(m, "quiz", "SEO KPI와 GEO KPI 차이", (
        "SEO KPI와 GEO KPI의 가장 근본적인 차이는 무엇인가요?"
    ), 3)
    add_option(s, "A", "SEO는 유료 광고, GEO는 무료 트래픽이 핵심이다", 0,
               "SEO도 무료 오가닉 트래픽을 목표로 합니다. 근본적인 차이는 SEO는 검색 순위(SERP 포지션)가, GEO는 AI 인용 빈도(Citation Rate)가 핵심 지표라는 점입니다.", 1)
    add_option(s, "B", "SEO는 검색 순위, GEO는 AI 인용 빈도가 핵심이다", 1,
               "정답입니다! SEO의 궁극적 목표는 검색 결과 상위 노출(SERP 순위)인 반면, GEO의 목표는 AI가 답변을 생성할 때 우리 콘텐츠를 인용하는 빈도를 높이는 것입니다. 측정 대상 자체가 다릅니다.", 2)
    add_option(s, "C", "SEO는 모바일 전용, GEO는 데스크톱 전용이다", 0,
               "SEO와 GEO 모두 디바이스에 제한되지 않습니다. 핵심 차이는 SEO는 검색 순위(SERP 포지션)를, GEO는 AI 인용 빈도(Citation Rate)를 핵심 지표로 삼는다는 점입니다.", 3)
    add_option(s, "D", "둘 사이에 차이는 없으며 동일한 KPI를 사용한다", 0,
               "SEO와 GEO는 상호 보완적이지만 핵심 KPI가 다릅니다. SEO는 검색 순위를, GEO는 AI 인용 빈도를 핵심으로 측정합니다. 둘의 차이를 이해해야 올바른 전략을 수립할 수 있습니다.", 4)

    s = add_step(m, "practice", "실습: B2B 기업교육 GEO KPI 대시보드 설계", (
        "B2B 기업교육 서비스(예: 패스트캠퍼스)의 GEO 성과를 측정하기 위한 "
        "KPI 대시보드를 설계하려 합니다.\n\n"
        "3층 프레임워크를 모두 포함하는 가장 올바른 대시보드 구성은?"
    ), 4)
    add_option(s, "A", "Layer 1 인용 추적만 포함하면 충분하다", 0,
               "Layer 1만으로는 불완전합니다. GEO 성과를 종합적으로 파악하려면 Layer 1 인용 추적, Layer 2 AI 경유 트래픽, Layer 3 리드 전환까지 3층을 모두 포함해야 합니다.", 1)
    add_option(s, "B", "Layer 1 인용 추적 + Layer 2 AI 경유 트래픽 + Layer 3 리드 전환", 1,
               "정답입니다! Layer 1에서 AI 인용 횟수와 Share of Voice를 추적하고, Layer 2에서 AI 경유 트래픽과 체류 시간을 측정하며, Layer 3에서 리드 전환율과 도메인 권위를 확인하면 GEO 성과를 입체적으로 파악할 수 있습니다.", 2)
    add_option(s, "C", "웹사이트 총 트래픽과 매출만 추적한다", 0,
               "총 트래픽과 매출은 비즈니스 지표이지 GEO 전용 KPI가 아닙니다. Layer 1 인용 추적, Layer 2 AI 경유 트래픽, Layer 3 리드 전환을 모두 포함하는 3층 대시보드가 필요합니다.", 3)
    add_option(s, "D", "경쟁사 분석만 대시보드에 포함한다", 0,
               "경쟁사 분석은 Share of Voice 비교에 유용하지만, 그것만으로는 부족합니다. Layer 1 인용 추적, Layer 2 AI 경유 트래픽, Layer 3 리드 전환의 3층 구조를 포함해야 합니다.", 4)

    # --- Module 5-2: GSC 활용법 ---
    m = add_module(5, "5-2: GSC 활용법", "Google Search Console을 활용한 GEO 측정 방법을 학습합니다.", 2)

    add_step(m, "reading", "Google Search Console로 GEO 측정", (
        "## Google Search Console로 GEO 측정\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>GSC</strong> (Google Search Console)<br>\n"
        "Google이 무료로 제공하는 웹사이트 검색 성과 분석 도구</p>\n"
        "<p><strong>Query</strong> (검색어, 쿼리)<br>\n"
        "사용자가 검색창에 입력하는 단어나 문장</p>\n"
        "<p><strong>Crawl</strong> (크롤링)<br>\n"
        "검색엔진 봇이 웹페이지를 방문해서 내용을 수집하는 과정</p>\n"
        "</div>\n\n"
        "**Google Search Console(GSC)**은 무료 웹마스터 도구로, "
        "GEO 관점에서 필수적인 진단 도구입니다.\n\n"
        "### 1. URL 검사 (URL Inspection)\n\n"
        "개별 URL이 Google에 올바르게 인덱싱되었는지 확인합니다.\n\n"
        "- **인덱싱 상태**: 페이지가 인덱스에 포함되어 있는지\n"
        "- **크롤링 정보**: 마지막 크롤링 날짜, 크롤링 허용 여부\n"
        "- **모바일 사용성**: 모바일 환경에서의 접근성\n"
        "- **리치 결과**: 구조화 데이터 인식 여부\n\n"
        "AI 봇도 Google 인덱스를 참조하므로, 인덱싱이 안 되면 AI 검색에서도 제외될 가능성이 높습니다.\n\n"
        "### 2. 성능 보고서 (Performance)\n\n"
        "검색 결과에서의 노출, 클릭, CTR, 평균 순위를 확인합니다.\n\n"
        "- GEO 관련 쿼리 필터링 (예: '추천', '비교', '어떤 것이 좋은지')\n"
        "- 페이지별 성능 비교로 GEO 최적화 대상 선정\n\n"
        "### 3. 인덱스 커버리지 (Coverage)\n\n"
        "전체 사이트의 인덱싱 현황을 파악합니다.\n\n"
        "- **유효**: 정상 인덱싱된 페이지\n"
        "- **경고 포함 유효**: 인덱싱되었지만 문제가 있는 페이지\n"
        "- **오류**: 인덱싱 실패 페이지\n"
        "- **제외**: 의도적 또는 비의도적으로 제외된 페이지\n\n"
        "### 4. 구조화 데이터 리포트\n\n"
        "Schema.org 마크업의 유효성을 검증합니다.\n\n"
        "- 유효/경고/오류 상태 확인\n"
        "- 필수 속성 누락 여부\n"
        "- 리치 결과 적격 여부\n\n"
        '<div class="browser-mockup">\n'
        '<div class="browser-bar">\n'
        '<span class="browser-dot red"></span>\n'
        '<span class="browser-dot yellow"></span>\n'
        '<span class="browser-dot green"></span>\n'
        '<span class="browser-url">search.google.com/search-console</span>\n'
        "</div>\n"
        '<div class="browser-body">\n'
        '<div class="log-example">\n'
        "<pre>\n"
        "URL Inspection Result\n"
        "---------------------\n"
        "URL: https://b2b.fastcampus.co.kr/training\n"
        "Status: URL is on Google\n"
        "Coverage: Indexed, not submitted in sitemap\n"
        "Crawled: 2026-02-18\n"
        "Rich Results: FAQ detected (valid)\n"
        "</pre>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n\n"
        '<div class="callout tip">\n'
        '<div class="callout-title">GSC로 할 수 있는 것 vs 할 수 없는 것</div>\n'
        '<div class="callout-body">\n'
        "<strong>할 수 있는 것:</strong>\n"
        "<ul>\n"
        "<li>인덱싱 상태 확인 및 수동 인덱싱 요청</li>\n"
        "<li>구조화 데이터 유효성 검증</li>\n"
        "<li>검색 성능 데이터 분석</li>\n"
        "<li>크롤링 오류 진단</li>\n"
        "</ul>\n"
        "<strong>할 수 없는 것:</strong>\n"
        "<ul>\n"
        "<li>AI 인용 횟수 직접 측정</li>\n"
        "<li>ChatGPT/Claude 등 LLM의 인용 현황 파악</li>\n"
        "<li>경쟁사 사이트 분석</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### Bing Webmaster Tools 병행 활용\n\n"
        "GSC와 함께 Bing Webmaster Tools도 활용하면 GEO 측정 범위를 넓힐 수 있습니다.\n\n"
        "#### 왜 Bing Webmaster Tools인가?\n\n"
        "- Microsoft의 Copilot(구 Bing Chat)은 Bing 인덱스를 직접 참조합니다\n"
        "- Bing에서 인덱싱이 잘 되어 있으면 Copilot에서의 인용 가능성이 높아집니다\n"
        "- GSC에서 감지하지 못하는 Bing 전용 크롤링 이슈를 발견할 수 있습니다\n\n"
        "#### 핵심 활용 포인트\n\n"
        "1. **URL 제출**: Bing에 사이트맵을 별도로 제출\n"
        "2. **인덱스 탐색기**: Bing 인덱스 내 페이지 상태 확인\n"
        "3. **SEO 보고서**: Bing 관점의 SEO 권장사항 확인\n"
        "4. **Adaptive URL**: Bing이 URL 구조를 이해하는 방식 확인"
    ))

    s = add_step(m, "quiz", "GSC에서 GEO 핵심 확인 항목", (
        "GSC에서 GEO 관점으로 가장 먼저 확인해야 할 핵심 항목의 조합은?"
    ), 2)
    add_option(s, "A", "소셜 미디어 연동 상태 + 광고 성과", 0,
               "GSC는 소셜 미디어나 광고 성과를 다루지 않습니다. GEO 관점에서 가장 핵심적인 확인 항목은 인덱스 상태와 구조화 데이터 유효성입니다. 이 두 가지가 AI 검색 노출의 기반입니다.", 1)
    add_option(s, "B", "인덱스 상태 + 구조화 데이터 유효성", 1,
               "정답입니다! 인덱스에 포함되지 않으면 AI가 참조할 수 없고, 구조화 데이터가 유효하지 않으면 AI의 콘텐츠 이해도가 떨어집니다. 이 두 가지가 GEO 측정의 가장 기본적인 출발점입니다.", 2)
    add_option(s, "C", "페이지 로딩 속도 + 이미지 최적화", 0,
               "로딩 속도와 이미지는 UX에 중요하지만 GEO의 핵심 확인 항목은 아닙니다. 인덱스 상태와 구조화 데이터 유효성이 AI 검색 노출의 기반이므로 이를 먼저 확인하세요.", 3)
    add_option(s, "D", "백링크 수 + 도메인 권위 점수", 0,
               "백링크와 도메인 권위는 오프사이트 지표이며 GSC에서 직접 확인하기 어렵습니다. GSC에서 GEO 관점으로 가장 먼저 확인해야 할 것은 인덱스 상태와 구조화 데이터 유효성입니다.", 4)

    s = add_step(m, "quiz", "URL 검사 결과 해석", (
        "GSC의 URL 검사에서 '페이지를 사용할 수 없음' 결과가 나왔습니다. "
        "이것이 GEO에 미치는 영향은?"
    ), 3)
    add_option(s, "A", "문제없다, AI는 인덱싱과 무관하게 모든 페이지를 읽는다", 0,
               "AI도 대부분 검색 인덱스를 참조하므로, 인덱싱되지 않은 페이지는 AI 검색에서도 제외될 가능성이 높습니다. 봇이 해당 페이지를 인덱싱하지 못하면 AI 인용 기회를 잃게 됩니다.", 1)
    add_option(s, "B", "봇이 해당 페이지를 인덱싱하지 못해 AI 검색에서 제외된다", 1,
               "정답입니다! URL 검사에서 페이지를 사용할 수 없다는 것은 Google 봇이 해당 페이지를 인덱싱하지 못했다는 뜻입니다. AI 검색도 인덱스를 참조하므로, 해당 페이지는 AI 답변의 출처로 선택될 수 없습니다.", 2)
    add_option(s, "C", "검색 순위만 낮아지고 AI 인용에는 영향 없다", 0,
               "인덱싱 실패는 검색 순위뿐 아니라 AI 인용에도 직접 영향을 미칩니다. 봇이 페이지를 인덱싱하지 못하면 AI가 해당 콘텐츠를 참조할 수 없어 AI 검색에서 제외됩니다.", 3)
    add_option(s, "D", "모바일에서만 문제가 발생한다", 0,
               "인덱싱 실패는 디바이스 유형과 무관하게 발생합니다. 봇이 페이지를 인덱싱하지 못하면 데스크톱, 모바일 모두에서 AI 검색 결과에서 제외됩니다. 인덱싱 문제를 먼저 해결하세요.", 4)

    s = add_step(m, "practice", "실습: GSC 진단 순서 설계", (
        "b2b.fastcampus.co.kr 사이트의 GEO 최적화 상태를 "
        "GSC로 진단하려 합니다.\n\n"
        "가장 효과적인 진단 순서는?"
    ), 4)
    add_option(s, "A", "구조화 데이터 → 성능 보고서 → URL 검사 순", 0,
               "구조화 데이터부터 시작하면 전체 그림을 파악하기 어렵습니다. 먼저 인덱스 커버리지로 전체 현황을 파악한 후, URL 검사로 개별 페이지를 확인하고, 구조화 데이터 리포트로 마무리하는 것이 효율적입니다.", 1)
    add_option(s, "B", "인덱스 커버리지 → URL 검사 → 구조화 데이터 리포트 순", 1,
               "정답입니다! 먼저 인덱스 커버리지에서 전체 사이트의 인덱싱 현황을 파악하고, 문제가 있는 개별 URL을 URL 검사로 심층 분석한 후, 구조화 데이터 리포트에서 스키마 유효성을 확인합니다. 전체에서 개별로, 거시에서 미시로 진단하는 순서입니다.", 2)
    add_option(s, "C", "성능 보고서만 확인하면 충분하다", 0,
               "성능 보고서만으로는 인덱싱 상태와 구조화 데이터 유효성을 파악할 수 없습니다. 인덱스 커버리지 → URL 검사 → 구조화 데이터 리포트 순서로 체계적으로 진단해야 합니다.", 3)
    add_option(s, "D", "URL 검사를 모든 페이지에 대해 하나씩 실행한다", 0,
               "수백 개의 페이지를 하나씩 검사하는 것은 비효율적입니다. 먼저 인덱스 커버리지에서 전체 현황을 파악하고, 문제가 있는 페이지만 URL 검사로 확인한 후 구조화 데이터 리포트를 확인하세요.", 4)

    # --- Module 5-3: GA4 & UTM 추적 ---
    m = add_module(5, "5-3: GA4 & UTM 추적", "GA4와 UTM을 활용한 AI 트래픽 추적 방법을 학습합니다.", 3)

    add_step(m, "reading", "GA4와 UTM으로 AI 트래픽 추적", (
        "## GA4와 UTM으로 AI 트래픽 추적\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>GA4</strong> (Google Analytics 4)<br>\n"
        "Google이 제공하는 무료 웹 분석 도구 — 방문자 행동, 유입 경로, 전환을 추적</p>\n"
        "<p><strong>UTM Parameter</strong> (UTM 파라미터)<br>\n"
        "링크 끝에 붙이는 추적 태그 — 어디서(source), 어떤 매체(medium), 어떤 캠페인(campaign)으로 유입됐는지 확인</p>\n"
        "<p><strong>utm_source / utm_medium / utm_campaign</strong><br>\n"
        "출처(chatgpt), 매체 유형(ai_referral), 캠페인명(geo_tracking)을 지정하는 3대 필수 파라미터</p>\n"
        "</div>\n\n"
        "**Google Analytics 4(GA4)**와 **UTM 파라미터**를 활용하여 "
        "AI 경유 트래픽을 체계적으로 추적하고 분석합니다.\n\n"
        "### 1. AI 경유 트래픽 식별\n\n"
        "AI 플랫폼(ChatGPT, Gemini 등)에서 유입된 트래픽을 식별하는 방법:\n\n"
        "- **리퍼러 분석**: GA4에서 세션 소스/매체를 확인하여 AI 플랫폼 리퍼러 필터링\n"
        "- **UTM 태깅**: AI 관련 캠페인에 UTM 파라미터를 부여하여 정확히 추적\n"
        "- **이벤트 트래킹**: AI 경유 방문자의 특정 행동(문의, 다운로드)을 이벤트로 기록\n\n"
        "### 2. UTM 파라미터 설계 체계\n\n"
        "UTM에는 5가지 파라미터가 있습니다:\n\n"
        '<div class="comparison-table">\n'
        '<div class="comp-header">UTM 파라미터 체계</div>\n'
        '<table>\n'
        '<thead><tr><th>파라미터</th><th>용도</th><th>예시</th></tr></thead>\n'
        '<tbody>\n'
        '<tr class="highlight"><td class="label">utm_source</td><td>트래픽 출처</td><td>chatgpt, gemini, perplexity</td></tr>\n'
        '<tr class="highlight"><td class="label">utm_medium</td><td>유입 매체</td><td>ai_referral, ai_citation</td></tr>\n'
        '<tr><td class="label">utm_campaign</td><td>캠페인 이름</td><td>geo_tracking, q1_2026</td></tr>\n'
        '<tr><td class="label">utm_term</td><td>키워드 (선택)</td><td>corporate_training</td></tr>\n'
        '<tr><td class="label">utm_content</td><td>콘텐츠 구분 (선택)</td><td>faq_page, blog_post</td></tr>\n'
        '</tbody>\n'
        '</table>\n'
        '</div>\n\n'
        "### 3. 전환 퍼널 분석\n\n"
        "AI 경유 트래픽의 전환 퍼널을 설정하여 비즈니스 성과를 측정합니다.\n\n"
        '<div class="code-example">\n'
        '<div class="code-label">UTM + GA4 이벤트 코드 예시</div>\n'
        '<pre><code class="language-html">\n'
        "&lt;!-- AI 경유 트래픽 추적용 URL --&gt;\n"
        "https://b2b.fastcampus.co.kr/training\n"
        "  ?utm_source=chatgpt\n"
        "  &amp;utm_medium=ai_referral\n"
        "  &amp;utm_campaign=geo_tracking\n\n"
        "&lt;!-- GA4 이벤트 트래킹 --&gt;\n"
        "&lt;script&gt;\n"
        "gtag('event', 'ai_referral_visit', {\n"
        "  'source': 'chatgpt',\n"
        "  'page_type': 'training_page',\n"
        "  'campaign': 'geo_tracking'\n"
        "});\n"
        "&lt;/script&gt;\n"
        "</code></pre>\n"
        "</div>\n\n"
        '<div class="diagram-box">\n'
        '<div class="diagram-title">전환 퍼널: AI 경유 트래픽</div>\n'
        '<div class="diagram-content">\n'
        "<pre>\n"
        "  [방문]          100%   AI에서 링크 클릭\n"
        "    |                    \n"
        "  [열람]           60%   페이지 30초 이상 체류\n"
        "    |                    \n"
        "  [문의]           15%   문의 폼 작성\n"
        "    |                    \n"
        "  [전환]            5%   실제 구매/계약\n"
        "</pre>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### AI 트래픽 소스 식별 방법 (referrer 분석)\n\n"
        "AI 플랫폼에서 유입된 트래픽의 리퍼러를 분석하는 방법입니다.\n\n"
        "#### 주요 AI 플랫폼 리퍼러 패턴\n\n"
        "| AI 플랫폼 | 리퍼러 패턴 |\n"
        "|-----------|-------------|\n"
        "| ChatGPT | chat.openai.com, chatgpt.com |\n"
        "| Gemini | gemini.google.com |\n"
        "| Perplexity | perplexity.ai |\n"
        "| Copilot | copilot.microsoft.com |\n"
        "| Claude | claude.ai |\n\n"
        "#### GA4에서 AI 트래픽 세그먼트 만들기\n\n"
        "1. GA4 > 탐색 > 새 탐색 생성\n"
        "2. 세그먼트 추가 > 세션 세그먼트\n"
        "3. 조건: 세션 소스에 위 리퍼러 패턴 포함\n"
        "4. 저장하여 AI 트래픽 전용 세그먼트로 활용\n\n"
        "#### 주의사항\n\n"
        "- 일부 AI 플랫폼은 리퍼러를 전달하지 않을 수 있음 (direct 트래픽으로 분류)\n"
        "- UTM 태깅과 리퍼러 분석을 병행하면 더 정확한 추적 가능\n"
        "- 정기적으로 새로운 AI 플랫폼 리퍼러 패턴을 업데이트"
    ))

    s = add_step(m, "quiz", "AI 경유 트래픽 식별 방법", (
        "AI 경유 트래픽을 GA4에서 가장 정확하게 식별하는 방법은?"
    ), 2)
    add_option(s, "A", "웹사이트 총 트래픽에서 직접 트래픽을 빼면 된다", 0,
               "직접 트래픽에는 AI 경유 외에도 다양한 소스가 포함됩니다. 가장 정확한 방법은 리퍼러 분석과 utm_source 태깅을 병행하여 AI 플랫폼에서의 유입을 명확히 구분하는 것입니다.", 1)
    add_option(s, "B", "리퍼러 분석 + utm_source 태깅을 병행한다", 1,
               "정답입니다! 리퍼러 분석으로 chat.openai.com 등 AI 플랫폼 유입을 감지하고, utm_source=chatgpt 등의 태깅으로 캠페인별 추적을 병행하면 가장 정확하게 AI 경유 트래픽을 식별할 수 있습니다.", 2)
    add_option(s, "C", "GA4의 기본 보고서에 AI 트래픽이 자동으로 분류된다", 0,
               "GA4는 아직 AI 트래픽을 자동 분류하지 않습니다. 리퍼러 분석과 utm_source 태깅을 직접 설정하여 AI 플랫폼에서의 유입을 식별해야 합니다.", 3)
    add_option(s, "D", "페이지뷰 수만 보면 AI 트래픽을 파악할 수 있다", 0,
               "페이지뷰만으로는 트래픽 소스를 구분할 수 없습니다. 리퍼러 분석과 utm_source 태깅을 병행해야 AI 경유 트래픽을 정확하게 식별할 수 있습니다.", 4)

    s = add_step(m, "quiz", "UTM 파라미터: 캠페인 이름", (
        "UTM 파라미터 중 캠페인 이름을 지정하는 것은 무엇인가요?"
    ), 3)
    add_option(s, "A", "utm_source", 0,
               "utm_source는 트래픽 출처(예: chatgpt, google)를 지정하는 파라미터입니다. 캠페인 이름을 지정하는 것은 utm_campaign입니다. 각 파라미터의 역할을 구분해서 기억하세요.", 1)
    add_option(s, "B", "utm_campaign", 1,
               "정답입니다! utm_campaign은 특정 캠페인의 이름을 지정하는 파라미터입니다. 예를 들어 utm_campaign=geo_tracking으로 설정하면 GEO 추적 캠페인의 성과를 별도로 분석할 수 있습니다.", 2)
    add_option(s, "C", "utm_medium", 0,
               "utm_medium은 유입 매체(예: ai_referral, email)를 지정하는 파라미터입니다. 캠페인 이름을 지정하려면 utm_campaign을 사용해야 합니다.", 3)
    add_option(s, "D", "utm_content", 0,
               "utm_content는 동일 캠페인 내 콘텐츠를 구분하는 파라미터입니다. 캠페인 이름 자체를 지정하려면 utm_campaign을 사용하세요.", 4)

    s = add_step(m, "practice", "실습: AI 경유 트래픽 측정용 UTM 설계", (
        "AI 경유 트래픽을 체계적으로 측정하기 위한 UTM 설계를 하려 합니다.\n\n"
        "ChatGPT에서 유입되는 GEO 추적용 URL에 가장 적절한 UTM 구성은?"
    ), 4)
    add_option(s, "A", "utm_source=google&utm_medium=organic", 0,
               "이것은 Google 자연 검색용 UTM 설정입니다. AI 경유 트래픽을 추적하려면 utm_source=chatgpt&utm_medium=ai_referral&utm_campaign=geo_tracking으로 설정하여 AI 소스를 명확히 구분하세요.", 1)
    add_option(s, "B", "utm_source=chatgpt&utm_medium=ai_referral&utm_campaign=geo_tracking", 1,
               "정답입니다! utm_source에 AI 플랫폼(chatgpt)을, utm_medium에 유입 유형(ai_referral)을, utm_campaign에 캠페인 목적(geo_tracking)을 지정하면 AI 경유 트래픽을 체계적으로 추적하고 분석할 수 있습니다.", 2)
    add_option(s, "C", "utm_campaign=chatgpt만 설정하면 충분하다", 0,
               "utm_campaign만으로는 소스와 매체를 구분할 수 없어 불완전합니다. utm_source=chatgpt&utm_medium=ai_referral&utm_campaign=geo_tracking으로 3가지 파라미터를 모두 설정해야 합니다.", 3)
    add_option(s, "D", "UTM 없이 리퍼러만 분석하면 된다", 0,
               "리퍼러만으로는 캠페인별 구분이 불가능하고, 일부 AI 플랫폼은 리퍼러를 전달하지 않을 수 있습니다. utm_source=chatgpt&utm_medium=ai_referral&utm_campaign=geo_tracking으로 UTM을 설정하세요.", 4)

    # --- Module 5-4: AI Validator 루틴 ---
    m = add_module(5, "5-4: AI Validator 루틴", "AI Validator 루틴을 구축하여 인용 현황을 정기적으로 확인합니다.", 4)

    add_step(m, "reading", "AI Validator 루틴 구축", (
        "## AI Validator 루틴 구축\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>AI Validator</strong> (AI 검증기)<br>\n"
        "AI에게 주기적으로 질문하여 우리 콘텐츠가 인용되는지 확인하는 프로세스</p>\n"
        "<p><strong>Prompt</strong> (프롬프트)<br>\n"
        "AI에게 입력하는 질문이나 명령문</p>\n"
        "<p><strong>Perplexity</strong> (퍼플렉시티)<br>\n"
        "출처를 명시하며 답변하는 AI 검색 엔진 — 인용 확인에 가장 유용</p>\n"
        "</div>\n\n"
        "**AI Validator**는 주기적으로 AI에게 타겟 쿼리를 질문하여 "
        "자사 콘텐츠의 인용 여부를 확인하는 체계적 프로세스입니다.\n\n"
        "### 왜 AI Validator가 필요한가?\n\n"
        "AI 모델은 지속적으로 업데이트되며, 인용 결과도 변합니다. "
        "오늘 인용되던 페이지가 내일 인용되지 않을 수 있으므로 "
        "정기적인 모니터링이 필수입니다.\n\n"
        "### 프롬프트 템플릿 (핵심 5개)\n\n"
        "1. **직접 추천 쿼리**: \"B2B 기업교육 추천 서비스 알려줘\"\n"
        "2. **비교 쿼리**: \"패스트캠퍼스 vs 다른 기업교육 서비스 비교\"\n"
        "3. **문제 해결 쿼리**: \"직원 역량 강화를 위한 교육 방법은?\"\n"
        "4. **리뷰 쿼리**: \"기업교육 서비스 리뷰 알려줘\"\n"
        "5. **가격 쿼리**: \"B2B 기업교육 비용 비교\"\n\n"
        "### 인용 점수 계산법\n\n"
        "각 쿼리에 대해 다음 요소를 점수화합니다:\n\n"
        "| 요소 | 점수 |\n"
        "|------|------|\n"
        "| 인용 빈도 (10회 쿼리 중 인용 횟수) | 0-10점 |\n"
        "| 인용 위치 (상단 +3, 중간 +2, 하단 +1) | 1-3점 |\n"
        "| 직접 링크 포함 여부 (+2) | 0-2점 |\n"
        "| 총점 | 최대 15점 |\n\n"
        "### 경쟁사 비교\n\n"
        "같은 쿼리에 대해 경쟁사의 인용 현황도 함께 기록하여 "
        "Share of Voice를 계산합니다.\n\n"
        '<div class="browser-mockup">\n'
        '<div class="browser-bar">\n'
        '<span class="browser-dot red"></span>\n'
        '<span class="browser-dot yellow"></span>\n'
        '<span class="browser-dot green"></span>\n'
        '<span class="browser-url">chatgpt.com</span>\n'
        "</div>\n"
        '<div class="browser-body">\n'
        '<div class="log-example">\n'
        "<pre>\n"
        "Q: B2B 기업교육 추천 서비스 알려줘\n\n"
        "A: B2B 기업교육 서비스를 추천드리겠습니다.\n\n"
        "1. 패스트캠퍼스 B2B\n"
        "   - 실무 중심 커리큘럼\n"
        "   - 맞춤형 기업교육 설계\n"
        "   - [출처: b2b.fastcampus.co.kr]  &lt;-- 인용 확인!\n\n"
        "2. ...\n"
        "</pre>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n\n"
        '<div class="callout key-point">\n'
        '<div class="callout-title">프롬프트 템플릿 핵심 5가지</div>\n'
        '<div class="callout-body">\n'
        "<ol>\n"
        "<li><strong>직접 추천</strong>: 서비스/제품 추천을 직접 요청</li>\n"
        "<li><strong>비교</strong>: 경쟁사 대비 비교 요청</li>\n"
        "<li><strong>문제 해결</strong>: 고객 문제 기반 솔루션 요청</li>\n"
        "<li><strong>리뷰/평판</strong>: 서비스 평가 요청</li>\n"
        "<li><strong>가격/비용</strong>: 비용 정보 요청</li>\n"
        "</ol>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### 자동화 방법 (API 활용)\n\n"
        "AI Validator 루틴을 자동화하면 수동 작업 부담을 크게 줄일 수 있습니다.\n\n"
        "#### 기본 자동화 플로우\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">AI Validator 자동화 파이프라인</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">쿼리 목록 관리</div><div class="step-desc">스프레드시트나 DB에 타겟 쿼리 목록 관리</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">API 호출</div><div class="step-desc">OpenAI API 등을 통해 각 쿼리에 대한 답변 자동 수집</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">인용 분석</div><div class="step-desc">답변 텍스트에서 자사 브랜드/URL 키워드 자동 검색</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">점수 기록</div><div class="step-desc">인용 점수를 자동 계산하여 DB에 저장</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">5</div><div class="step-content"><div class="step-title">알림</div><div class="step-desc">점수 변동이 크면 Slack/이메일로 알림</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'
        '<div class="callout warning">\n'
        "<strong>주의사항</strong><br>\n"
        "- API 비용이 발생하므로 쿼리 수와 빈도를 적절히 설정하세요.<br>\n"
        "- AI 답변은 비결정적이므로 같은 쿼리에 여러 번 질문하여 평균을 계산하세요.<br>\n"
        "- AI 모델 버전이 바뀌면 결과가 크게 달라질 수 있으므로 모델 버전도 기록하세요.\n"
        "</div>"
    ))

    s = add_step(m, "quiz", "AI Validator 루틴의 핵심", (
        "AI Validator 루틴의 가장 핵심적인 활동은 무엇인가요?"
    ), 2)
    add_option(s, "A", "AI에게 자사 홍보 글을 작성해달라고 요청한다", 0,
               "AI에게 홍보 글 작성을 요청하는 것은 콘텐츠 생성 활동이지 Validator 활동이 아닙니다. AI Validator의 핵심은 타겟 쿼리에 대해 AI 답변에서 자사 인용 여부를 정기적으로 확인하는 것입니다.", 1)
    add_option(s, "B", "타겟 쿼리에 대해 AI 답변에서 자사 인용 여부를 정기 확인한다", 1,
               "정답입니다! AI Validator의 핵심은 미리 정한 타겟 쿼리 목록을 가지고 정기적으로 AI에게 질문하여, 자사 브랜드/URL이 답변에 인용되는지 모니터링하는 것입니다. 이를 통해 GEO 전략의 효과를 지속적으로 추적합니다.", 2)
    add_option(s, "C", "경쟁사 웹사이트의 트래픽을 분석한다", 0,
               "경쟁사 트래픽 분석은 별도의 경쟁 분석 활동입니다. AI Validator의 핵심은 타겟 쿼리에 대해 AI 답변에서 자사가 인용되는지 정기적으로 확인하는 것입니다.", 3)
    add_option(s, "D", "AI 모델의 학습 데이터를 직접 수정한다", 0,
               "AI 모델의 학습 데이터는 직접 수정할 수 없습니다. AI Validator는 타겟 쿼리에 대해 AI 답변에서 자사 인용 여부를 정기적으로 확인하여 GEO 효과를 모니터링하는 활동입니다.", 4)

    s = add_step(m, "quiz", "인용 점수 계산 요소", (
        "AI Validator에서 인용 점수를 계산할 때 포함되는 요소의 올바른 조합은?"
    ), 3)
    add_option(s, "A", "페이지 로딩 속도 + 이미지 수 + 글자 수", 0,
               "이것들은 온사이트 기술 지표이며 인용 점수 계산 요소가 아닙니다. 인용 점수는 인용 빈도, 인용 위치(상단/하단), 직접 링크 여부의 조합으로 계산합니다.", 1)
    add_option(s, "B", "인용 빈도 + 인용 위치(상단/하단) + 직접 링크 여부", 1,
               "정답입니다! 인용 점수는 세 가지 요소로 구성됩니다. 인용 빈도(10회 쿼리 중 몇 번 인용되는지), 인용 위치(상단/중간/하단), 직접 링크 포함 여부를 종합하여 최대 15점으로 계산합니다.", 2)
    add_option(s, "C", "소셜 미디어 좋아요 수 + 댓글 수 + 공유 수", 0,
               "소셜 미디어 지표는 인용 점수에 포함되지 않습니다. AI Validator의 인용 점수는 인용 빈도, 인용 위치(상단/하단), 직접 링크 여부로 계산합니다.", 3)
    add_option(s, "D", "도메인 권위 + 백링크 수 + 페이지 권위", 0,
               "이것들은 오프사이트 SEO 지표입니다. AI Validator의 인용 점수는 AI 답변에서의 인용 빈도, 인용 위치(상단/하단), 직접 링크 포함 여부를 기반으로 계산합니다.", 4)

    s = add_step(m, "practice", "실습: 기업교육 AI Validator 설계", (
        "기업교육 키워드 5개에 대한 AI Validator 루틴을 설계하려 합니다.\n\n"
        "가장 체계적인 AI Validator 설계는?"
    ), 4)
    add_option(s, "A", "키워드 1개만 선정하여 한 달에 한 번 확인한다", 0,
               "키워드 1개와 월 1회 확인은 너무 빈도가 낮아 변화를 감지하기 어렵습니다. 쿼리 목록(5개 이상)을 만들고, 주간 체크를 하며, 인용 점수를 기록하는 체계적 루틴이 필요합니다.", 1)
    add_option(s, "B", "쿼리 목록(5개) + 주간 체크 + 인용 점수 기록", 1,
               "정답입니다! 5개 이상의 타겟 쿼리 목록을 만들고, 최소 주 1회 체크하며, 인용 빈도/위치/링크 여부를 점수화하여 기록하면 GEO 전략의 효과를 체계적으로 모니터링할 수 있습니다.", 2)
    add_option(s, "C", "AI에게 우리 회사를 추천해달라고만 반복 요청한다", 0,
               "자사 추천만 요청하면 편향된 결과를 얻게 됩니다. 다양한 유형의 쿼리 목록(추천/비교/문제해결 등)을 만들고, 주간 체크와 인용 점수 기록을 병행하는 체계적 루틴이 필요합니다.", 3)
    add_option(s, "D", "경쟁사 모니터링 없이 자사 인용만 확인한다", 0,
               "경쟁사 비교 없이는 Share of Voice를 파악할 수 없습니다. 쿼리 목록을 만들고 주간 체크를 하되, 경쟁사 인용 현황도 함께 기록하여 인용 점수를 종합적으로 관리하세요.", 4)

    # --- Module 5-5: 가설 기반 실험 설계 ---
    m = add_module(5, "5-5: 가설 기반 실험 설계", "GEO 전략의 가설 수립과 체계적 실험 설계를 학습합니다.", 5)

    add_step(m, "reading", "GEO 가설 기반 실험 설계", (
        "## GEO 가설 기반 실험 설계\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>A/B Test</strong> (A/B 테스트)<br>\n"
        "두 가지 버전(A: 기존, B: 변경)을 비교하여 어떤 것이 더 효과적인지 검증하는 실험</p>\n"
        "<p><strong>Hypothesis</strong> (가설)<br>\n"
        '"~하면 ~가 될 것이다"라는 검증 가능한 예측 — 실험의 출발점</p>\n'
        "<p><strong>Control Group</strong> (대조군)<br>\n"
        "변경 없이 기존 상태를 유지하는 그룹 — 실험군의 효과를 비교하는 기준</p>\n"
        "</div>\n\n"
        "GEO 전략의 효과를 검증하려면 체계적인 **가설 기반 실험**이 필수입니다. "
        "감에 의존하지 않고, 데이터로 증명하는 과학적 접근법을 학습합니다.\n\n"
        "### 실험 플로우\n\n"
        "1. **가설 수립**: 측정 가능하고 구체적인 가설 작성\n"
        "2. **실험 설계**: 대조군/실험군, 변수 통제, 측정 지표 결정\n"
        "3. **실행**: 실험을 일정 기간 동안 실행\n"
        "4. **측정**: 사전에 정한 KPI로 결과 수집\n"
        "5. **결론**: 가설 채택/기각 판단 및 다음 실험 설계\n\n"
        "### 좋은 가설의 조건\n\n"
        "- **구체적**: \"GEO를 잘 하면 좋아진다\" (X) → "
        "\"H1에 질문형 키워드를 추가하면 AI 인용이 10% 증가한다\" (O)\n"
        "- **측정 가능**: 수치로 측정할 수 있는 변수와 결과\n"
        "- **시간 제한**: 실험 기간이 명시 (예: 4주간)\n"
        "- **변수 명시**: 독립 변수(변경할 것)와 종속 변수(측정할 것)\n\n"
        "### A/B 테스트 방법\n\n"
        "- **대조군(A)**: 기존 상태를 유지하는 그룹\n"
        "- **실험군(B)**: 변경 사항을 적용하는 그룹\n"
        "- **통제 변수**: 실험 대상 외 다른 요소는 동일하게 유지\n"
        "- **기간**: 최소 2-4주 (AI 모델 업데이트 주기 고려)\n\n"
        "### 유의미한 결과 판단\n\n"
        "- 결과 차이가 우연에 의한 것인지, 실험 변수에 의한 것인지 판단\n"
        "- 충분한 샘플 크기와 기간을 확보해야 신뢰할 수 있는 결론\n"
        "- 여러 번 반복하여 일관된 결과가 나오는지 확인\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">GEO 실험 플로우</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">가설 수립</div><div class="step-desc">"H1 변경 시 인용 10% 증가"</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">실험 설계</div><div class="step-desc">대조군 5페이지 / 실험군 5페이지</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">실행</div><div class="step-desc">4주간 실험 진행</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">측정</div><div class="step-desc">AI Validator로 인용 점수 비교</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">5</div><div class="step-content"><div class="step-title">결론</div><div class="step-desc">가설 채택 또는 기각</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'
        '<div class="compare-cards">\n'
        '<div class="card before">\n'
        '<div class="card-header">실험 전 (대조군)</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>H1: 기업교육 서비스 안내</li>\n"
        "<li>인용 점수: 평균 5.2점</li>\n"
        "<li>AI 인용 빈도: 10회 중 3회</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="card after">\n'
        '<div class="card-header">실험 후 (실험군)</div>\n'
        '<div class="card-body">\n'
        "<ul>\n"
        "<li>H1: 기업교육 서비스 어떻게 선택하나요?</li>\n"
        "<li>인용 점수: 평균 7.8점</li>\n"
        "<li>AI 인용 빈도: 10회 중 6회</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        "</div>"
    ), 1, extension_md=(
        "### 통계적 유의성 기초 개념\n\n"
        "실험 결과를 해석할 때 통계적 유의성을 이해하면 "
        "더 신뢰할 수 있는 결론을 내릴 수 있습니다.\n\n"
        "#### p-value란?\n\n"
        "- 관찰된 차이가 우연에 의해 발생할 확률\n"
        "- 일반적으로 p < 0.05이면 통계적으로 유의미하다고 판단\n"
        "- GEO 실험에서는 p < 0.10도 의미 있는 신호로 볼 수 있음\n\n"
        "#### 주의사항\n\n"
        "- GEO 실험은 전통적 A/B 테스트보다 통제하기 어려움\n"
        "- AI 모델 업데이트, 경쟁사 변화 등 외부 변수가 많음\n"
        "- 따라서 정량적 데이터와 정성적 판단을 함께 활용\n"
        "- 한 번의 실험으로 결론 내리기보다 반복 실험 권장"
    ))

    s = add_step(m, "quiz", "좋은 GEO 실험 가설의 조건", (
        "좋은 GEO 실험 가설이 갖추어야 할 가장 중요한 조건은?"
    ), 2)
    add_option(s, "A", "가능한 한 광범위하고 추상적인 목표를 설정한다", 0,
               "광범위하고 추상적인 가설은 측정과 검증이 불가능합니다. 좋은 가설은 측정 가능하고 구체적인 변수(예: H1 태그)와 기대 결과(예: 인용 10% 증가)를 명시해야 합니다.", 1)
    add_option(s, "B", "측정 가능하고 구체적인 변수와 기대 결과를 명시한다", 1,
               "정답입니다! 좋은 가설은 독립 변수(변경할 것), 종속 변수(측정할 것), 기대 결과를 구체적으로 명시해야 합니다. 예를 들어 'H1에 질문형 키워드를 추가하면(독립 변수) AI 인용이 10% 증가한다(종속 변수+기대 결과)'가 좋은 가설입니다.", 2)
    add_option(s, "C", "결과를 미리 정하고 그에 맞는 데이터만 수집한다", 0,
               "결과를 미리 정하면 확증 편향에 빠집니다. 좋은 가설은 측정 가능하고 구체적인 변수와 기대 결과를 명시하되, 결과가 기대와 다를 수 있음을 열어 두어야 합니다.", 3)
    add_option(s, "D", "실험 기간을 정하지 않고 원하는 결과가 나올 때까지 진행한다", 0,
               "기간 미설정은 실험 설계의 기본 원칙에 어긋납니다. 좋은 가설은 측정 가능하고 구체적인 변수, 기대 결과와 함께 실험 기간도 명시해야 합니다.", 4)

    s = add_step(m, "quiz", "A/B 테스트의 통제 변수", (
        "GEO A/B 테스트에서 '통제 변수'란 무엇인가요?"
    ), 3)
    add_option(s, "A", "실험에서 변경하려는 핵심 변수를 말한다", 0,
               "변경하려는 핵심 변수는 '독립 변수'입니다. 통제 변수는 실험 대상 외 다른 요소를 동일하게 유지하여, 결과 차이가 독립 변수에 의한 것임을 보장하는 것입니다.", 1)
    add_option(s, "B", "실험 대상 외 다른 요소를 동일하게 유지하는 것", 1,
               "정답입니다! 통제 변수란 실험에서 변경하는 요소(독립 변수) 외에 나머지 조건을 동일하게 유지하는 것입니다. 예를 들어 H1만 변경하는 실험이라면 본문, 이미지, 내부 링크 등은 동일하게 유지해야 합니다.", 2)
    add_option(s, "C", "실험 결과를 측정하는 지표를 의미한다", 0,
               "결과 측정 지표는 '종속 변수'입니다. 통제 변수는 실험 대상 외 다른 요소를 동일하게 유지하여 결과의 신뢰성을 확보하는 것을 의미합니다.", 3)
    add_option(s, "D", "실험을 관리하는 담당자를 말한다", 0,
               "통제 변수는 사람이 아니라 실험 조건을 가리킵니다. 실험 대상(독립 변수) 외 다른 요소를 동일하게 유지하여, 관찰된 차이가 실험 변수에 의한 것임을 보장하는 개념입니다.", 4)

    s = add_step(m, "practice", "실습: H1 태그 변경 실험 설계", (
        "H1 태그에 질문형 키워드를 추가하면 AI 인용이 증가하는지 "
        "실험하려 합니다.\n\n"
        "가장 체계적인 실험 설계는?"
    ), 4)
    add_option(s, "A", "모든 페이지의 H1을 한꺼번에 변경하고 결과를 확인한다", 0,
               "모든 페이지를 한꺼번에 변경하면 대조군이 없어 효과를 검증할 수 없습니다. 가설을 명시하고 대조군/실험군을 분리하여 비교 실험을 진행해야 합니다.", 1)
    add_option(s, "B", "가설(H1에 질문형 키워드 추가 시 AI 인용 10% 증가) + 대조군/실험군 설정", 1,
               "정답입니다! 구체적인 가설을 수립하고, 기존 H1을 유지하는 대조군과 질문형 H1으로 변경한 실험군을 분리하여 4주간 인용 점수를 비교하면 체계적인 실험이 됩니다.", 2)
    add_option(s, "C", "H1 변경 없이 AI에게 우리 사이트를 추천해달라고 요청한다", 0,
               "AI에게 추천을 요청하는 것은 실험이 아닙니다. H1 변경의 효과를 검증하려면 구체적 가설을 세우고 대조군/실험군을 설정하여 인용 점수 변화를 비교해야 합니다.", 3)
    add_option(s, "D", "H1을 변경하고 당일 결과를 바로 확인한다", 0,
               "AI 모델의 인덱싱과 반영에는 시간이 필요합니다. 최소 2-4주의 실험 기간을 두고, 가설과 대조군/실험군을 설정하여 충분한 데이터를 수집해야 합니다.", 4)

    # --- Module 5-6: 90일 로드맵 설계 ---
    m = add_module(5, "5-6: 90일 로드맵 설계", "GEO 전략의 90일 실행 로드맵을 설계합니다.", 6)

    add_step(m, "reading", "GEO 90일 실행 로드맵", (
        "## GEO 90일 실행 로드맵\n\n"
        '<div class="callout glossary">\n'
        "<p><strong>Funnel</strong> (퍼널, 깔때기)<br>\n"
        "인식 → 관심 → 검토 → 전환 순으로 고객 여정을 단계별로 나눈 마케팅 프레임워크</p>\n"
        "<p><strong>Attribution</strong> (어트리뷰션, 기여도 분석)<br>\n"
        "고객이 전환하기까지 거친 여러 터치포인트 중 각각의 기여도를 측정하는 방법</p>\n"
        "</div>\n\n"
        "GEO 전략을 체계적으로 실행하기 위한 **90일(약 13주) 로드맵**입니다. "
        "4단계로 나누어 단계별 핵심 활동과 목표를 설정합니다.\n\n"
        "### 1단계: 진단 & 기반 구축 (0-2주)\n\n"
        "현재 상태를 정확히 파악하고 GEO 기반을 마련합니다.\n\n"
        "- **현황 진단**: GSC 인덱싱 상태, 구조화 데이터 현황, AI Validator 초기 점수\n"
        "- **기반 구축**: Schema.org 마크업 적용, 헤딩 구조 정리, sitemap/robots.txt 최적화\n"
        "- **목표 설정**: 3층 KPI 베이스라인 설정, 90일 목표 수치 결정\n\n"
        "### 2단계: 온사이트 최적화 (3-6주)\n\n"
        "자사 사이트의 콘텐츠를 GEO에 최적화합니다.\n\n"
        "- **Answer-first 콘텐츠**: 주요 페이지에 질문-답변 형태의 콘텐츠 추가\n"
        "- **FAQ 페이지**: 핵심 키워드별 FAQ 페이지 생성 및 FAQPage 스키마 적용\n"
        "- **헤딩 최적화**: H1-H3에 질문형/답변형 키워드 배치\n"
        "- **내부 링크**: 토픽 클러스터 기반 내부 링크 구조 강화\n\n"
        "### 3단계: 오프사이트 확장 (7-10주)\n\n"
        "외부에서 브랜드 인지도와 신뢰를 구축합니다.\n\n"
        "- **백링크**: 전문 매체, 블로그, 파트너사로부터 에디토리얼 링크 확보\n"
        "- **멘션**: 업계 커뮤니티, 포럼, Q&A에서 브랜드 자연 멘션 활성화\n"
        "- **PR**: 보도자료, 전문가 기고, 인터뷰 등 디지털 PR 활동\n\n"
        "### 4단계: 측정 & 개선 (11-13주)\n\n"
        "성과를 측정하고 지속적 개선 루틴을 정착시킵니다.\n\n"
        "- **AI Validator 정기 실행**: 주간 인용 점수 추적\n"
        "- **KPI 리뷰**: 3층 KPI 대비 달성률 분석\n"
        "- **실험 계획**: 다음 90일 실험 가설 및 우선순위 수립\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">GEO 90일 로드맵 4단계</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">진단 &amp; 기반 구축 (0-2주)</div><div class="step-desc">GSC 진단, 스키마 적용, KPI 베이스라인</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">온사이트 최적화 (3-6주)</div><div class="step-desc">Answer-first, FAQ 페이지, 헤딩 최적화</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">오프사이트 확장 (7-10주)</div><div class="step-desc">백링크, 멘션, PR 활동</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">측정 &amp; 개선 (11-13주)</div><div class="step-desc">AI Validator 정기 실행, KPI 리뷰, 실험 계획</div></div></div>\n'
        '</div>\n'
        '</div>'
    ), 1, extension_md=(
        "### 90일 이후 지속 운영 방안\n\n"
        "90일 로드맵 완료 후에도 GEO는 지속적으로 운영해야 합니다.\n\n"
        '<div class="hierarchy-box">\n'
        '<div class="level-1"><strong>월간 루틴</strong><br>\n'
        "- 주 1회 AI Validator 실행 및 인용 점수 기록<br>\n"
        "- 월 1회 3층 KPI 리뷰 미팅<br>\n"
        "- 월 1-2건 새로운 콘텐츠(블로그, FAQ) 발행<br>\n"
        "- 월 1건 이상 오프사이트 활동 (기고, PR 등)</div>\n"
        '<div class="level-2"><strong>분기별 활동</strong><br>\n'
        "- 분기별 GEO 전략 리뷰 및 방향 조정<br>\n"
        "- 경쟁사 Share of Voice 비교 분석<br>\n"
        "- 새로운 AI 플랫폼/모델 업데이트 대응<br>\n"
        "- 다음 분기 실험 가설 수립</div>\n"
        '<div class="level-3"><strong>연간 활동</strong><br>\n'
        "- 연간 GEO 전략 보고서 작성<br>\n"
        "- ROI 분석 (투입 자원 대비 AI 인용 비즈니스 성과)<br>\n"
        "- 다음 연도 GEO 전략 및 예산 수립</div>\n"
        "</div>"
    ))

    s = add_step(m, "quiz", "90일 로드맵 1단계 핵심", (
        "GEO 90일 로드맵의 1단계(0-2주)에서 수행하는 핵심 활동은?"
    ), 2)
    add_option(s, "A", "대규모 콘텐츠 제작 및 소셜 미디어 캠페인 실행", 0,
               "대규모 콘텐츠 제작과 소셜 캠페인은 이후 단계의 활동입니다. 1단계(0-2주)에서는 현재 상태 진단과 GEO 기반 구축(스키마, 헤딩 구조 등)에 집중해야 합니다.", 1)
    add_option(s, "B", "현재 상태 진단 + GEO 기반 구축 (스키마, 헤딩 등)", 1,
               "정답입니다! 1단계에서는 GSC로 인덱싱 상태를 진단하고, AI Validator 초기 점수를 설정하며, Schema.org 마크업과 헤딩 구조를 정리하여 GEO의 기반을 마련합니다. 진단 없이 실행하면 방향을 잃을 수 있습니다.", 2)
    add_option(s, "C", "백링크 대량 구매 및 PR 보도자료 배포", 0,
               "백링크와 PR은 3단계(7-10주) 활동입니다. 1단계(0-2주)에서는 먼저 현재 상태를 진단하고 스키마, 헤딩 등 기반을 구축해야 합니다.", 3)
    add_option(s, "D", "AI Validator 결과 분석 및 최종 보고서 작성", 0,
               "최종 분석과 보고서는 4단계(11-13주) 활동입니다. 1단계(0-2주)에서는 현재 상태 진단과 GEO 기반 구축(스키마, 헤딩 등)에 집중합니다.", 4)

    s = add_step(m, "quiz", "90일 로드맵 3단계 핵심", (
        "GEO 90일 로드맵의 3단계(7-10주)에서 수행하는 핵심 활동은?"
    ), 3)
    add_option(s, "A", "사이트 기술 진단 및 스키마 마크업 적용", 0,
               "기술 진단과 스키마 적용은 1단계(0-2주)의 활동입니다. 3단계(7-10주)에서는 백링크, 멘션, PR 등 오프사이트 확장 활동에 집중합니다.", 1)
    add_option(s, "B", "오프사이트 확장 (백링크, 멘션, PR)", 1,
               "정답입니다! 3단계(7-10주)에서는 1-2단계에서 구축한 온사이트 기반 위에 외부 활동을 확장합니다. 전문 매체 백링크, 업계 커뮤니티 멘션, 디지털 PR 등을 통해 브랜드의 오프사이트 존재감을 높입니다.", 2)
    add_option(s, "C", "FAQ 페이지 생성 및 Answer-first 콘텐츠 작성", 0,
               "FAQ와 Answer-first 콘텐츠는 2단계(3-6주)의 활동입니다. 3단계(7-10주)에서는 외부로 확장하여 백링크, 멘션, PR 등 오프사이트 활동에 집중합니다.", 3)
    add_option(s, "D", "90일 전체 성과 보고서 작성", 0,
               "성과 보고서는 4단계(11-13주) 활동입니다. 3단계(7-10주)에서는 백링크, 멘션, PR 등 오프사이트 확장 활동에 집중해야 합니다.", 4)

    s = add_step(m, "practice", "실습: b2b.fastcampus.co.kr 90일 로드맵 설계", (
        "b2b.fastcampus.co.kr의 GEO 전략 90일 로드맵을 설계합니다.\n\n"
        "4단계를 올바른 순서로 배치한 로드맵은?"
    ), 4)
    add_option(s, "A", "오프사이트부터 시작하여 온사이트를 나중에 한다", 0,
               "오프사이트부터 시작하면 기반이 없어 효과가 떨어집니다. 올바른 순서는 1단계 진단/스키마 → 2단계 Answer-first/FAQ → 3단계 PR/링크 → 4단계 AI Validator/개선입니다.", 1)
    add_option(s, "B", "1단계 진단/스키마 - 2단계 Answer-first/FAQ - 3단계 PR/링크 - 4단계 AI Validator/개선", 1,
               "정답입니다! 먼저 진단과 기반 구축(스키마, 헤딩)으로 시작하고, 온사이트 콘텐츠(Answer-first, FAQ)를 최적화한 후, 오프사이트(PR, 백링크)로 확장하고, 마지막으로 AI Validator와 KPI 리뷰로 성과를 측정합니다. 기초에서 확장으로, 내부에서 외부로 나아가는 체계적 순서입니다.", 2)
    add_option(s, "C", "4단계를 모두 동시에 병렬로 진행한다", 0,
               "모든 단계를 동시에 진행하면 자원이 분산되고 기반 없이 확장하게 됩니다. 1단계 진단/스키마 → 2단계 Answer-first/FAQ → 3단계 PR/링크 → 4단계 AI Validator/개선 순서로 진행하세요.", 3)
    add_option(s, "D", "측정/개선부터 시작하고 진단은 마지막에 한다", 0,
               "측정할 기반이 없으면 개선할 수 없습니다. 올바른 순서는 1단계 진단/스키마 → 2단계 Answer-first/FAQ → 3단계 PR/링크 → 4단계 AI Validator/개선입니다.", 4)

    # --- Module 5-7: Stage 5 종합 평가 ---
    m = add_module(5, "5-7: Stage 5 종합 평가", "Stage 5에서 학습한 측정과 실험 설계를 종합적으로 평가합니다.", 7)

    s = add_step(m, "quiz", "종합 Q1: 가장 먼저 측정해야 할 KPI 층", (
        "GEO KPI 3층에서 가장 먼저 측정해야 할 층은?"
    ), 1)
    add_option(s, "A", "Layer 3 Authority (도메인 평판)", 0,
               "Authority는 장기적 지표로, 가장 먼저 측정하기에는 시간이 오래 걸립니다. 가장 먼저 측정해야 할 것은 Layer 1 Visibility, 즉 AI 인용 횟수입니다. 인용이 있어야 이후 행동과 권위로 이어집니다.", 1)
    add_option(s, "B", "Layer 1 Visibility (AI 인용 횟수)", 1,
               "정답입니다! AI 인용 횟수(Visibility)가 가장 기본적인 출발점입니다. AI가 우리를 인용하지 않으면 트래픽(Behavior)도 권위(Authority)도 의미가 없습니다. Layer 1에서 시작하여 위로 올라가는 것이 올바른 순서입니다.", 2)
    add_option(s, "C", "Layer 2 Behavior (AI 경유 트래픽)", 0,
               "AI 경유 트래픽은 중요하지만, 인용이 먼저 있어야 트래픽이 발생합니다. 가장 먼저 측정해야 할 것은 Layer 1 Visibility, 즉 AI 답변에서의 인용 횟수입니다.", 3)
    add_option(s, "D", "세 층을 동시에 측정할 필요 없이 하나만 선택하면 된다", 0,
               "세 층 모두 측정해야 하지만 우선순위가 있습니다. 가장 먼저 Layer 1 Visibility(AI 인용 횟수)를 측정하고, 그 위에 Layer 2, Layer 3을 순차적으로 쌓아 올리세요.", 4)

    s = add_step(m, "quiz", "종합 Q2: GSC 구조화 데이터 오류 확인", (
        "GSC에서 구조화 데이터의 오류를 확인하는 가장 정확한 방법은?"
    ), 2)
    add_option(s, "A", "성능 보고서에서 클릭률을 확인한다", 0,
               "클릭률은 검색 성능 지표이며, 구조화 데이터 오류와 직접 관련이 없습니다. 구조화 데이터 리포트에서 유효/경고/오류 상태를 확인하는 것이 가장 정확한 방법입니다.", 1)
    add_option(s, "B", "구조화 데이터 리포트에서 유효/경고/오류를 확인한다", 1,
               "정답입니다! GSC의 구조화 데이터 리포트에서 각 스키마 유형별로 유효, 경고, 오류 상태를 확인할 수 있습니다. 오류가 있으면 해당 스키마가 리치 결과에 반영되지 않으며, AI의 콘텐츠 이해에도 영향을 미칩니다.", 2)
    add_option(s, "C", "사이트맵에서 URL 목록을 확인한다", 0,
               "사이트맵은 URL 제출 현황을 보여주며, 구조화 데이터 오류와는 다릅니다. 구조화 데이터 리포트에서 유효/경고/오류 상태를 직접 확인하세요.", 3)
    add_option(s, "D", "모바일 사용성 보고서를 확인한다", 0,
               "모바일 사용성 보고서는 모바일 환경 관련 이슈를 다루며, 구조화 데이터와 별개입니다. 구조화 데이터 리포트에서 유효/경고/오류를 확인하는 것이 정확한 방법입니다.", 4)

    s = add_step(m, "quiz", "종합 Q3: AI Validator 실행 주기", (
        "AI Validator의 권장 실행 주기는?"
    ), 3)
    add_option(s, "A", "분기에 한 번 (3개월마다)", 0,
               "분기별 확인은 너무 간격이 길어 중요한 변화를 놓칠 수 있습니다. AI Validator는 최소 주 1회, 이상적으로는 AI 모델 업데이트 시에도 추가로 실행하여 변화를 빠르게 감지해야 합니다.", 1)
    add_option(s, "B", "최소 주 1회 (이상적으로 AI 모델 업데이트 시 추가)", 1,
               "정답입니다! AI 모델은 수시로 업데이트되며, 인용 결과도 변할 수 있습니다. 최소 주 1회 정기적으로 실행하고, AI 모델의 주요 업데이트가 있을 때 추가로 실행하면 변화를 신속하게 감지할 수 있습니다.", 2)
    add_option(s, "C", "연 1회 연말에 실행하면 충분하다", 0,
               "연 1회로는 AI의 빠른 변화를 전혀 추적할 수 없습니다. 최소 주 1회 실행하고, AI 모델 업데이트 시 추가 실행하여 인용 현황의 변화를 지속적으로 모니터링하세요.", 3)
    add_option(s, "D", "AI가 자동으로 알려주므로 별도 실행이 불필요하다", 0,
               "AI는 인용 변경을 자동으로 알려주지 않습니다. AI Validator를 최소 주 1회 직접 실행하고, AI 모델 업데이트 시 추가로 실행하여 인용 현황을 능동적으로 모니터링해야 합니다.", 4)

    s = add_step(m, "quiz", "종합 Q4: 90일 로드맵 2단계 핵심", (
        "GEO 90일 로드맵 2단계(3-6주)의 핵심 활동은?"
    ), 4)
    add_option(s, "A", "GSC 진단 및 스키마 마크업 적용", 0,
               "GSC 진단과 스키마 적용은 1단계(0-2주) 활동입니다. 2단계(3-6주)의 핵심은 온사이트 콘텐츠 최적화, 즉 Answer-first 콘텐츠, FAQ 페이지 생성, 헤딩 최적화입니다.", 1)
    add_option(s, "B", "온사이트 콘텐츠 최적화 (Answer-first, FAQ, 헤딩)", 1,
               "정답입니다! 2단계에서는 1단계에서 구축한 기반 위에 실제 콘텐츠를 최적화합니다. 주요 페이지에 Answer-first 형태의 콘텐츠를 추가하고, FAQ 페이지를 생성하며, H1-H3 헤딩에 질문형/답변형 키워드를 배치합니다.", 2)
    add_option(s, "C", "백링크 확보 및 디지털 PR 활동", 0,
               "백링크와 PR은 3단계(7-10주) 활동입니다. 2단계(3-6주)에서는 온사이트 콘텐츠를 최적화하여 Answer-first, FAQ, 헤딩 구조를 개선하는 것이 핵심입니다.", 3)
    add_option(s, "D", "AI Validator 분석 및 성과 보고서 작성", 0,
               "성과 분석과 보고서는 4단계(11-13주) 활동입니다. 2단계(3-6주)의 핵심은 온사이트 콘텐츠 최적화(Answer-first, FAQ, 헤딩)입니다.", 4)

    s = add_step(m, "quiz", "종합 Q5: GEO 전략의 궁극적 성공 지표", (
        "전체 GEO 전략의 궁극적인 성공 지표는 무엇인가요?"
    ), 5)
    add_option(s, "A", "AI 인용 횟수만 최대한 높이는 것", 0,
               "AI 인용 횟수는 Layer 1 지표로 중요하지만, 궁극적인 성공 지표는 아닙니다. GEO의 최종 목표는 AI 인용을 통해 실제 비즈니스 성과(리드 확보, 매출 증가)를 달성하는 것입니다.", 1)
    add_option(s, "B", "AI 인용을 통한 비즈니스 성과 (리드, 매출) 달성", 1,
               "정답입니다! 축하합니다! Stage 5를 수료하셨습니다. 다음 Stage 6에서는 우리 B2B 팀이 실제로 수행할 GEO 과업을 주차 단위 실행 모듈로 완성하게 됩니다. GEO의 궁극적 목표는 단순한 AI 인용이 아니라, 인용을 통해 트래픽을 유도하고 실제 비즈니스 성과(리드 확보, 매출 증가)로 이어지게 하는 것입니다.", 2)
    add_option(s, "C", "경쟁사보다 더 많은 백링크를 확보하는 것", 0,
               "백링크는 오프사이트 GEO의 한 수단이지 궁극적 목표가 아닙니다. GEO 전략의 최종 성공 지표는 AI 인용을 통해 비즈니스 성과(리드, 매출)를 달성하는 것입니다.", 3)
    add_option(s, "D", "웹사이트 트래픽을 최대한 높이는 것", 0,
               "트래픽은 중간 지표(Layer 2)이며, 궁극적 성공 지표는 아닙니다. GEO 전략의 최종 목표는 AI 인용을 기반으로 실제 비즈니스 성과(리드 확보, 매출 증가)를 달성하는 것입니다.", 4)

    # ==================================================================
    # STAGE 6: GEO 액션 플랜 실행 가이드
    # ==================================================================
    add_stage(
        6,
        "GEO 액션 플랜 실행 가이드",
        "docs/strategy/73-geo-action-plan.md의 59개 티켓을 30/60/90일 Phase별로 순차 실행하는 과업 가이드입니다.",
        6,
        '{"require_stage_complete": 5, "min_score_pct": 70}',
    )

    # ----------------------------------------------------------------
    # Module 6-1: 킥오프 & 현황 진단
    # ----------------------------------------------------------------
    m = add_module(6, "6-1: 킥오프 & 현황 진단",
                   "GEO 현재 상태를 이해하고, 팀 역할/주간 리듬/KPI 베이스라인을 첫 주에 고정합니다.", 1)

    # -- M6-1 Reading --
    add_step(m, "reading", "GEO 현황 브리핑 & 킥오프 체크리스트", (
        "## GEO 현황 브리핑 & 킥오프 체크리스트\n\n"
        "### 왜 킥오프가 필요한가?\n\n"
        "Stage 6는 학습이 아니라 **실행 과업 운영 단계**입니다. "
        "첫 주에 팀 역할, 승인 흐름, 주간 리듬, KPI 베이스라인을 확정하지 않으면 "
        "과업이 밀리고 우선순위가 흔들립니다.\n\n"

        '<div class="callout glossary">\n'
        "<p><strong>RACI</strong><br>\n"
        "책임(R), 승인(A), 자문(C), 통보(I) — 과업별 역할 배분 프레임워크. "
        "킥오프에서 가장 먼저 확정해야 할 구조입니다.</p>\n"
        "<p><strong>SLA</strong> (Service Level Agreement)<br>\n"
        "과업 승인·검토에 걸리는 최대 시간을 합의한 약속. "
        "예: 콘텐츠 48시간, 스키마 24시간.</p>\n"
        "<p><strong>Phase / P0·P1·P2</strong><br>\n"
        "90일 로드맵의 실행 단계와 티켓 우선순위. "
        "P0 = Phase 1(30일, 28 tickets), P1 = Phase 2(60일, 20 tickets), P2 = Phase 3(90일, 11 tickets).</p>\n"
        "<p><strong>KPI</strong> (복습)<br>\n"
        "목표 달성 여부를 숫자로 측정하는 핵심 성과 지표. "
        "Stage 6에서는 KPI-A(ChatGPT 인용), KPI-B(Google AI 노출), KPI-C(하위 질의 커버리지) 3층 구조로 확장됩니다.</p>\n"
        "</div>\n\n"

        "### 전략 한 줄\n\n"
        "<div class='callout'>\n"
        "<strong>b2b.fastcampus.co.kr을 AI 검색(ChatGPT Search + Google AI Overviews/AI Mode)에서 "
        "더 자주 인용되게 만들기 위해, 상단 정답문장 + 근거블록 + 팬아웃 콘텐츠 + 측정 루프를 "
        "90일간 반복 실행한다.</strong>\n"
        "</div>\n\n"

        "### 4대 실행 레버\n\n"
        "1. **Answer-first**: 페이지 상단 2~6문장으로 정의/대상/제공형태/산출물/도입조건을 고정\n"
        "2. **Proof-first**: 통계/인용/외부 출처(3~7개) 블록을 Answer 바로 아래에 표준화\n"
        "3. **Fan-out 클러스터**: 허브 7개 + 스포크 60개 1차 발행으로 하위 질의 커버리지 확대\n"
        "4. **측정 실험 루프**: Top 50 질문 세트로 주간 인용률/커버리지 추적 및 4주 단위 실험\n\n"

        "### 현재 상태 진단 요약\n\n"
        "<div class='callout warning'>\n"
        "<strong>핵심 문제 4가지</strong><br>\n"
        "1. <strong>기술 인프라 미비</strong>: robots.txt 404, sitemap.xml 404 -- 봇 정책 불명확<br>\n"
        "2. <strong>Answer-first 부재</strong>: 24/25 페이지(96%)가 상단 정답 문장 없음<br>\n"
        "3. <strong>구조화데이터 오용</strong>: 25개 페이지 모두 @type:Course (ContactPage도 Course로 표기)<br>\n"
        "4. <strong>Fan-out 약함</strong>: 허브-스포크 아키텍처 전무, 평면형 내부링크 구조\n"
        "</div>\n\n"

        "**기술 현황 상세**\n\n"
        "- **CSR 비율**: 22/25 페이지(88%) -- JS 렌더링 미지원 봇은 콘텐츠 읽기 불가\n"
        "- **JSON-LD**: 25개 페이지 모두 @type:Course 마크업 (100%) -- 템플릿 기본값 오용\n"
        "- **필수 스키마 부재**: BreadcrumbList 0/25, Organization 0/25, Event 0/25\n"
        "- **내부 링크**: 총 1,028개(페이지당 평균 41개)이나 모두 홈/문의/개인정보로만 수렴\n\n"

        "### GEO 준비도 스코어카드\n\n"
        "<div class='hierarchy-box'>\n"
        "<strong>5차원 평가 (각 0~5점, 총 25점)</strong><br>\n"
        "- Answerability: 3.0/5 (60%) -- 24개 페이지 상단 정답 문장 부재<br>\n"
        "- Proof: 4.3/5 (86%) -- 비교적 양호<br>\n"
        "- Fan-out: 3.4/5 (68%) -- 하위 질문 커버리지 미흡<br>\n"
        "- Crawlability: 4.8/5 (96%) -- 양호<br>\n"
        "- Trust: 3.7/5 (74%) -- 중간<br>\n"
        "<strong>평균: 19.3/25 (C+ 등급)</strong>\n"
        "</div>\n\n"

        "### 30/60/90일 마일스톤\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">30/60/90일 마일스톤</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">Phase 1 (30일)</div><div class="step-desc">상위 10 랜딩 Answer-first/Proof-first + 기술 인프라 + 측정 체계 — 28 tickets (P0)</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">Phase 2 (60일)</div><div class="step-desc">허브 7개 구축 + 스포크 60개 1차 발행 + 자산 표준화 — 20 tickets (P1)</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">Phase 3 (90일)</div><div class="step-desc">구조화데이터 정착 + 내부링크 재설계 + 외부 권위 확보 — 11 tickets (P2)</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'

        "### RACI 표 (권장 역할)\n\n"
        '<div class="hierarchy-box">\n'
        '<table class="comparison-table"><thead><tr><th>역할</th><th>담당자</th><th>책임 범위</th></tr></thead>\n'
        '<tbody>\n'
        '<tr><td>Owner (A)</td><td>B2B 마케팅 리드</td><td>최종 의사결정, 승인 SLA</td></tr>\n'
        '<tr><td>Responsible (R)</td><td>콘텐츠 담당, 웹 운영 담당</td><td>페이지 개선, 배포, 스키마</td></tr>\n'
        '<tr><td>Consulted (C)</td><td>데이터 분석, 세일즈 운영</td><td>KPI 해석, 사례 데이터</td></tr>\n'
        '<tr><td>Informed (I)</td><td>경영진, 영업 리더</td><td>주간/월간 리포트 수신</td></tr>\n'
        '</tbody></table>\n'
        '</div>\n\n'

        "### 주간 리듬 (권장)\n\n"
        "- **월요일**: KPI/이슈 리뷰 30분\n"
        "- **화~목**: 페이지 개선 + 배포 과업 실행\n"
        "- **금요일**: AI Validator 점검 + 다음 주 백로그 확정\n\n"

        "### 킥오프 체크리스트 (첫 주 산출물)\n\n"
        "1. RACI 표 1부 작성 (Owner/R/C/I 확정)\n"
        "2. 기준 페이지 5개 확정 (service_custom, refer_customer, resource_report, service_online, index)\n"
        "3. KPI 3층 베이스라인 입력 (KPI-A: ChatGPT 인용, KPI-B: Google AI 노출, KPI-C: 하위 질의 커버리지)\n"
        "4. 승인 SLA 합의 (예: 콘텐츠 48시간, 스키마 24시간)\n"
        "5. 4주 실행 캘린더 1부 작성\n"
        "6. 우선순위 백로그 Top 10 확정\n\n"

        "### 자주 하는 실수\n\n"
        "<div class='callout warning'>\n"
        "- 역할을 정하지 않고 과업부터 시작하면 승인 대기로 2~3일씩 밀립니다\n"
        "- KPI 없이 페이지 개선을 시작하면 성과를 증명할 기준이 없습니다\n"
        "- 킥오프를 생략하고 바로 콘텐츠 작업에 들어가면 Phase 2에서 재작업이 발생합니다\n"
        "</div>"
    ), 1, extension_md=(
        "### 복붙용 주간 운영 템플릿\n\n"
        "```text\n"
        "[GEO 주간 운영 템플릿]\n"
        "- Week: YYYY-WW\n"
        "- Owner: [이름]\n"
        "- 이번 주 목표 KPI:\n"
        "  - KPI-A 목표: \n"
        "  - KPI-B 목표: \n"
        "  - KPI-C 목표: \n"
        "- 이번 주 핵심 과업 3개:\n"
        "  1. \n"
        "  2. \n"
        "  3. \n"
        "- 리스크 및 차단 이슈: \n"
        "- 의사결정 필요 항목: \n"
        "- 금주 결과(인용/유입/전환): \n"
        "- 다음 주 우선순위 변경사항: \n"
        "```\n\n"
        "### 킥오프 회의 어젠다 템플릿\n\n"
        "```text\n"
        "[GEO 킥오프 회의 어젠다]\n"
        "1. 프로젝트 목표 공유 (5분)\n"
        "2. 현황 진단 결과 브리핑 (10분)\n"
        "3. RACI 역할 합의 (10분)\n"
        "4. 기준 페이지 5개 확정 (5분)\n"
        "5. KPI 베이스라인 입력 방법 안내 (5분)\n"
        "6. 승인 SLA 합의 (5분)\n"
        "7. 주간 리듬 확정 (5분)\n"
        "8. Q&A (5분)\n"
        "```\n\n"
        "초기 2주에는 속도보다 **운영 습관 고정**이 더 중요합니다. "
        "킥오프 완료 전에는 다음 모듈로 진행하지 마세요."
    ))

    # -- M6-1 Quiz --
    s = add_step(m, "quiz", "핵심 문제 우선순위 판단", (
        "현재 b2b.fastcampus.co.kr의 4가지 핵심 문제(기술 인프라 미비, Answer-first 부재, "
        "구조화데이터 오용, Fan-out 약함) 중 가장 먼저 해결해야 하는 것은 무엇인가요?"
    ), 2)
    add_option(s, "A", "기술 인프라 미비 (robots.txt/sitemap.xml 404 상태)", 1,
               "정답입니다! robots.txt와 sitemap.xml이 404 상태이면 봇이 크롤링 정책을 파악할 수 없고, "
               "이후 콘텐츠 개선 효과도 봇에게 전달되지 않습니다. 기술 인프라가 다른 모든 작업의 전제 조건입니다.", 1)
    add_option(s, "B", "Answer-first 부재 (24/25 페이지)", 0,
               "Answer-first는 매우 중요하지만, robots.txt가 404이면 봇이 업데이트된 콘텐츠를 제대로 수집하지 못합니다. "
               "기술 인프라를 먼저 정비해야 콘텐츠 개선 효과가 전달됩니다.", 2)
    add_option(s, "C", "구조화데이터 오용 (Course 스키마 100%)", 0,
               "구조화데이터 수정도 중요하지만, 크롤링 기반이 없으면 스키마 변경 자체가 봇에게 반영되지 않습니다. "
               "robots.txt와 sitemap.xml 설정이 최우선입니다.", 3)
    add_option(s, "D", "Fan-out 약함 (허브-스포크 아키텍처 전무)", 0,
               "Fan-out 확장은 Phase 2(60일) 과업입니다. Phase 1에서는 기술 기반과 상위 10 페이지 "
               "콘텐츠 개선에 집중해야 합니다. 기술 인프라가 1순위입니다.", 4)

    # -- M6-1 Practice 1 --
    s = add_step(m, "practice", "킥오프 완료 기준 판정", (
        "다음 중 GEO 킥오프를 '완료'로 볼 수 있는 최소 조건 조합은 무엇인가요?"
    ), 3)
    add_option(s, "A", "담당자 명단만 작성하고 즉시 배포 시작", 0,
               "담당자 명단만으로는 실행 조건이 충족되지 않습니다. 승인 SLA, 기준 페이지, KPI 입력까지 "
               "완료되어야 운영이 안정적으로 시작됩니다.", 1)
    add_option(s, "B", "RACI 확정 + 기준 페이지 5개 선정 + KPI 베이스라인 입력 + 승인 SLA 합의", 1,
               "정답입니다! 이 4가지가 고정되어야 과업 실행, 성과 리뷰, 의사결정이 같은 기준으로 "
               "돌아갑니다. 킥오프 완료 조건으로 가장 실무적인 조합입니다.", 2)
    add_option(s, "C", "주간 회의 시간만 합의하고 과업 시작", 0,
               "회의 시간 합의만으로는 실행이 시작되지 않습니다. 역할과 지표, 대상 페이지를 동시에 "
               "정의해야 과업 품질이 확보됩니다.", 3)
    add_option(s, "D", "성과 목표 없이 과업 목록만 작성", 0,
               "성과 목표 없이 과업만 나열하면 우선순위가 흔들립니다. 최소한 KPI 베이스라인과 "
               "승인 구조를 함께 확정해야 합니다.", 4)

    # -- M6-1 Practice 2 --
    s = add_step(m, "practice", "Phase별 우선순위 배치", (
        "다음 과업들을 30/60/90일 Phase에 올바르게 배치한 것은 무엇인가요?\n\n"
        "과업 목록: (1) robots.txt 작성, (2) 허브 7개 구축, (3) 외부 권위 확보(리포트/케이스)"
    ), 4)
    add_option(s, "A", "robots.txt -> Phase 2, 허브 -> Phase 1, 외부 권위 -> Phase 3", 0,
               "robots.txt는 봇 크롤링의 전제 조건이므로 Phase 1(30일)에서 가장 먼저 처리해야 합니다. "
               "Phase 2로 미루면 콘텐츠 개선 효과가 지연됩니다.", 1)
    add_option(s, "B", "robots.txt -> Phase 1, 허브 -> Phase 2, 외부 권위 -> Phase 3", 1,
               "정답입니다! Phase 1에서 기술 기반(robots.txt, sitemap.xml)과 상위 10 랜딩 콘텐츠를 정비하고, "
               "Phase 2에서 허브-스포크를 확장하며, Phase 3에서 외부 권위를 확보하는 것이 올바른 순서입니다.", 2)
    add_option(s, "C", "모든 과업을 Phase 1에 집중", 0,
               "59개 티켓을 30일에 모두 처리하는 것은 비현실적입니다. P0(28개) -> P1(20개) -> P2(11개) "
               "순서로 나누어 실행해야 품질과 일정을 모두 관리할 수 있습니다.", 3)
    add_option(s, "D", "외부 권위 -> Phase 1, robots.txt -> Phase 3, 허브 -> Phase 2", 0,
               "외부 권위 확보는 내부 콘텐츠와 기술 기반이 정비된 후에야 효과가 있습니다. "
               "기술 인프라가 Phase 1의 최우선 과업입니다.", 4)

    # ----------------------------------------------------------------
    # Module 6-2: 기술 인프라 정비 (P0-1~5)
    # ----------------------------------------------------------------
    m = add_module(6, "6-2: 기술 인프라 정비",
                   "robots.txt 작성, sitemap.xml 생성, 구조화데이터 감사, ChatGPT 유입 추적을 설정합니다.", 2)

    # -- M6-2 Reading --
    add_step(m, "reading", "기술 인프라 5대 과업 SOP", (
        "## 기술 인프라 5대 과업 SOP\n\n"
        "### 왜 기술 인프라가 최우선인가?\n\n"
        "robots.txt와 sitemap.xml이 404 상태이면 검색 봇(OAI-SearchBot, GoogleBot)이 "
        "크롤링 정책을 파악할 수 없습니다. 콘텐츠를 아무리 개선해도 봇이 수집하지 못하면 "
        "AI 검색 결과에 반영되지 않습니다.\n\n"

        '<div class="callout glossary">\n'
        "<p><strong>OAI-SearchBot</strong><br>\n"
        "OpenAI의 ChatGPT Search 전용 크롤러. "
        "이 봇을 robots.txt에서 차단하면 ChatGPT 검색 결과에서 완전히 제외됩니다.</p>\n"
        "<p><strong>GPTBot</strong><br>\n"
        "OpenAI의 모델 학습용 크롤러. OAI-SearchBot과 별개이며, 선택적 허용이 가능합니다.</p>\n"
        "<p><strong>SOP</strong> (Standard Operating Procedure)<br>\n"
        "표준 운영 절차서. 반복 과업을 누구나 동일하게 실행할 수 있도록 정리한 문서입니다.</p>\n"
        "<p><strong>DoD</strong> (Definition of Done)<br>\n"
        "과업 완료를 판정하는 최소 기준 목록. '배포했다'가 아니라 '검증까지 끝났다'를 뜻합니다.</p>\n"
        "<p><strong>robots.txt</strong> (복습)<br>\n"
        "검색엔진 봇에게 크롤링 허용/제외 범위를 알려주는 텍스트 파일. "
        "현재 b2b.fastcampus.co.kr은 이 파일이 404(Not Found) 상태입니다.</p>\n"
        "</div>\n\n"

        "### 5대 과업 실행 순서\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">기술 인프라 5대 과업</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">P0-1</div><div class="step-desc">robots.txt 작성</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">P0-2</div><div class="step-desc">sitemap.xml 생성 + 제출</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">P0-3</div><div class="step-desc">구조화데이터 감사</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">P0-4</div><div class="step-desc">Organization/BreadcrumbList JSON-LD 템플릿</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">5</div><div class="step-content"><div class="step-title">P0-5</div><div class="step-desc">ChatGPT utm_source 추적 설정</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'

        "### P0-1: robots.txt 작성\n\n"
        "<div class='callout warning'>\n"
        "<strong>현재 상태</strong>: robots.txt가 404 (Not Found)입니다. "
        "모든 봇에 대해 허용/제외 정책이 명문화되어 있지 않습니다.\n"
        "</div>\n\n"
        "**작성 예시:**\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n\n"
        "# AI Search Bots\n"
        "User-agent: OAI-SearchBot\n"
        "Allow: /\n\n"
        "User-agent: GPTBot\n"
        "Allow: /\n\n"
        "User-agent: Google-Extended\n"
        "Allow: /\n\n"
        "Sitemap: https://b2b.fastcampus.co.kr/sitemap.xml\n"
        "</code></pre>\n"
        "</div>\n\n"
        "**핵심 규칙**: OAI-SearchBot은 ChatGPT Search의 크롤러이므로 **반드시 Allow**해야 합니다. "
        "GPTBot은 학습용 크롤러로 선택적 허용이 가능하지만, 인용 최적화를 위해 허용을 권장합니다.\n\n"
        "**DoD**: 파일 배포 후 24시간 내 반영 확인 (크롤 로그 검증)\n\n"

        "### P0-2: sitemap.xml 생성 + 제출\n\n"
        "- 177개 전체 URL을 포함하는 XML 사이트맵 생성\n"
        "- XML 유효성 검증 (W3C Validator)\n"
        "- Google Search Console + Bing Webmaster Tools에 제출\n"
        "- **우선 등록 대상**: 전환 상위 10개 페이지 + 허브 후보 페이지\n\n"
        "**DoD**: XML 유효성 검증 통과 + GSC/Bing 제출 완료\n\n"

        "### P0-3: 구조화데이터 감사\n\n"
        "현재 25개 페이지 모두 @type:Course 마크업이 적용되어 있으나, "
        "이는 템플릿 기본값의 오용입니다.\n\n"
        "**수정 필요 사항**:\n"
        "- `/contact`, `/contact_mktg` -> @type:ContactPage로 변경\n"
        "- 서비스 페이지 -> 조건부 Course 유지 (실제 교육 콘텐츠인 경우만)\n"
        "- 인사이트 페이지 -> @type:Article\n"
        "- 세미나 페이지 -> @type:Event\n\n"
        "**DoD**: 모든 페이지 JSON-LD 검증 결과 리포트 + 수정 계획 수립\n\n"

        "### P0-4: Organization/BreadcrumbList JSON-LD 템플릿\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        '&lt;script type=\"application/ld+json\"&gt;\n'
        "{\n"
        '  \"@context\": \"https://schema.org\",\n'
        '  \"@type\": \"Organization\",\n'
        '  \"name\": \"패스트캠퍼스 B2B\",\n'
        '  \"url\": \"https://b2b.fastcampus.co.kr\",\n'
        '  \"logo\": \"https://b2b.fastcampus.co.kr/logo.png\",\n'
        '  \"contactPoint\": {\n'
        '    \"@type\": \"ContactPoint\",\n'
        '    \"telephone\": \"+82-...\",\n'
        '    \"contactType\": \"sales\"\n'
        "  }\n"
        "}\n"
        "&lt;/script&gt;\n"
        "</code></pre>\n"
        "</div>\n\n"
        "**DoD**: 템플릿 문서 작성 + 3개 페이지 파일럿 적용\n\n"

        "### P0-5: ChatGPT 유입 추적 설정\n\n"
        "ChatGPT Search가 링크를 생성할 때 `utm_source=chatgpt.com`이 자동 부착됩니다.\n"
        "GA4에서 이 파라미터로 필터링하여 ChatGPT 유입 트래픽을 분리 추적합니다.\n\n"
        "**설정 절차**:\n"
        "1. GA4 > 데이터 스트림 > 이벤트 설정 확인\n"
        "2. utm_source=chatgpt.com 필터 생성\n"
        "3. 테스트: ChatGPT에서 자사 링크 클릭 후 GA4 반영 확인\n\n"
        "**DoD**: GA4 필터 설정 완료 + ChatGPT 링크 테스트 통과\n\n"

        "### 자주 하는 실수\n\n"
        "<div class='callout warning'>\n"
        "- robots.txt에서 OAI-SearchBot을 Disallow하면 ChatGPT Search에서 완전히 제외됩니다\n"
        "- sitemap.xml에 404 페이지를 포함하면 크롤 예산이 낭비됩니다\n"
        "- Contact 페이지에 Course 스키마를 그대로 두면 Google이 페이지 의도를 오해합니다\n"
        "</div>"
    ), 1, extension_md=(
        "### robots.txt 봇별 상세 설명\n\n"
        '<table class="comparison-table"><thead><tr>'
        "<th>봇 이름</th><th>소속</th><th>용도</th><th>권장 정책</th>"
        "</tr></thead><tbody>\n"
        "<tr><td>OAI-SearchBot</td><td>OpenAI</td><td>ChatGPT Search 크롤링</td><td><strong>Allow (필수)</strong></td></tr>\n"
        "<tr><td>GPTBot</td><td>OpenAI</td><td>모델 학습용 크롤링</td><td>Allow (권장)</td></tr>\n"
        "<tr><td>Google-Extended</td><td>Google</td><td>Gemini 학습용</td><td>Allow (권장)</td></tr>\n"
        "<tr><td>Googlebot</td><td>Google</td><td>일반 검색 크롤링</td><td><strong>Allow (필수)</strong></td></tr>\n"
        "<tr><td>Bingbot</td><td>Microsoft</td><td>Bing 검색 크롤링</td><td><strong>Allow (필수)</strong></td></tr>\n"
        "</tbody></table>\n\n"
        "### BreadcrumbList JSON-LD 템플릿\n\n"
        '<div class="code-example">'
        '<div class="code-label">BreadcrumbList JSON-LD</div>'
        "<pre><code>"
        '{\n'
        '  "@context": "https://schema.org",\n'
        '  "@type": "BreadcrumbList",\n'
        '  "itemListElement": [\n'
        '    {"@type": "ListItem", "position": 1, "name": "홈", "item": "https://b2b.fastcampus.co.kr/"},\n'
        '    {"@type": "ListItem", "position": 2, "name": "서비스", "item": "https://b2b.fastcampus.co.kr/service"},\n'
        '    {"@type": "ListItem", "position": 3, "name": "맞춤형 교육"}\n'
        '  ]\n'
        '}'
        "</code></pre></div>\n\n"
        "배포 전 반드시 Google Rich Results Test와 Schema Markup Validator로 검증하세요."
    ))

    # -- M6-2 Quiz --
    s = add_step(m, "quiz", "robots.txt 봇 허용 정책", (
        "robots.txt에서 ChatGPT Search 인용을 위해 반드시 Allow해야 하는 봇은 무엇인가요?"
    ), 2)
    add_option(s, "A", "GPTBot만 Allow하면 충분하다", 0,
               "GPTBot은 OpenAI의 모델 학습용 크롤러입니다. ChatGPT Search 결과에 노출되려면 "
               "OAI-SearchBot을 반드시 Allow해야 합니다. GPTBot 허용만으로는 검색 인용이 보장되지 않습니다.", 1)
    add_option(s, "B", "OAI-SearchBot을 반드시 Allow해야 한다", 1,
               "정답입니다! OAI-SearchBot은 ChatGPT Search 전용 크롤러입니다. "
               "이 봇이 차단되면 ChatGPT Search 결과에서 완전히 제외됩니다. "
               "GPTBot은 학습용이므로 별도로 판단할 수 있지만, OAI-SearchBot은 필수입니다.", 2)
    add_option(s, "C", "모든 봇을 Disallow하고 Google만 Allow하면 된다", 0,
               "Google만 허용하면 ChatGPT Search와 Bing에서 완전히 제외됩니다. "
               "AI 검색 최적화를 위해서는 OAI-SearchBot과 Googlebot 모두 Allow해야 합니다.", 3)
    add_option(s, "D", "robots.txt 없이 기본 상태로 두면 모든 봇이 크롤링한다", 0,
               "robots.txt가 404이면 대부분의 봇이 모든 페이지를 크롤링하지만, "
               "명시적 허용 정책이 없으면 봇마다 해석이 다를 수 있습니다. 명확한 정책 명문화가 필요합니다.", 4)

    # -- M6-2 Practice 1 --
    s = add_step(m, "practice", "구조화데이터 오용 수정", (
        "현재 b2b.fastcampus.co.kr의 /contact 페이지에 @type:Course 마크업이 적용되어 있습니다. "
        "이 문제를 가장 올바르게 해결하는 방법은 무엇인가요?"
    ), 3)
    add_option(s, "A", "Course 마크업을 그대로 유지한다", 0,
               "/contact는 교육 콘텐츠 페이지가 아니므로 Course 스키마는 부적절합니다. "
               "Google은 페이지 의도와 스키마가 불일치하면 신뢰 신호를 감점할 수 있습니다.", 1)
    add_option(s, "B", "@type:ContactPage로 변경한다", 1,
               "정답입니다! /contact 페이지의 실제 의도는 문의 접수이므로 ContactPage가 "
               "정확한 스키마 타입입니다. 각 페이지의 실제 목적에 맞는 스키마를 적용해야 "
               "Google과 AI 검색 엔진이 페이지를 올바르게 이해합니다.", 2)
    add_option(s, "C", "모든 스키마를 제거한다", 0,
               "스키마를 완전히 제거하면 AI 검색 엔진이 페이지를 이해하기 더 어려워집니다. "
               "제거가 아니라 올바른 타입으로 수정하는 것이 정답입니다.", 3)
    add_option(s, "D", "@type:WebPage로 통일한다", 0,
               "WebPage는 가장 일반적인 타입이므로, ContactPage나 Course 같은 구체적 타입의 "
               "이점을 잃게 됩니다. 페이지 의도에 맞는 구체적 타입을 선택하세요.", 4)

    # -- M6-2 Practice 2 --
    s = add_step(m, "practice", "sitemap.xml 우선 등록 대상", (
        "177개 URL이 있는 사이트에서 sitemap.xml에 우선 등록해야 할 페이지 조합은 무엇인가요?"
    ), 4)
    add_option(s, "A", "관리자 페이지와 API 엔드포인트를 포함한 전체 URL", 0,
               "관리자 페이지와 API 엔드포인트는 공개 콘텐츠가 아니므로 사이트맵에 포함하면 "
               "크롤 예산이 낭비됩니다. 공개 콘텐츠 URL만 포함해야 합니다.", 1)
    add_option(s, "B", "전환 상위 10개 페이지 + 허브 후보 페이지를 우선 등록", 1,
               "정답입니다! 전환 기여도가 높은 페이지와 허브 후보를 우선 등록하면 "
               "봇이 중요한 페이지를 먼저 크롤링합니다. 이후 나머지 공개 페이지를 추가하여 "
               "전체 커버리지를 확보하세요.", 2)
    add_option(s, "C", "홈페이지 URL 1개만 등록", 0,
               "홈페이지만 등록하면 하위 페이지의 크롤링 우선순위가 낮아집니다. "
               "핵심 랜딩 페이지를 명시적으로 포함해야 AI 검색에서 인용될 가능성이 높아집니다.", 3)
    add_option(s, "D", "404 에러 페이지를 포함하여 모든 URL을 등록", 0,
               "404 페이지를 사이트맵에 포함하면 크롤 예산이 낭비되고 사이트 품질 신호가 저하됩니다. "
               "유효한 공개 페이지만 포함해야 합니다.", 4)

    # ----------------------------------------------------------------
    # Module 6-3: Answer-first 콘텐츠 전환 (P0-6~15)
    # ----------------------------------------------------------------
    m = add_module(6, "6-3: Answer-first 콘텐츠 전환",
                   "상위 10개 랜딩 페이지에 H1 직하단 2~6문장 정답 블록을 적용합니다.", 3)

    # -- M6-3 Reading --
    add_step(m, "reading", "Answer-first 3종 템플릿 & 적용 SOP", (
        "## Answer-first 3종 템플릿 & 적용 SOP\n\n"
        "### 왜 Answer-first인가?\n\n"
        "AI 검색 엔진(ChatGPT Search, Google AI Overviews)은 페이지 상단에서 "
        "명확한 정답 문장을 찾아 인용합니다. 현재 b2b.fastcampus.co.kr의 24/25 페이지(96%)에는 "
        "상단 정답 문장이 없어 AI가 인용할 텍스트를 찾지 못하고 있습니다.\n\n"

        '<div class="callout glossary">\n'
        "<p><strong>Answer-first</strong> (복습)<br>\n"
        "페이지 상단(H1 직하단)에 핵심 답변을 2~6문장으로 배치하는 콘텐츠 작성법. "
        "AI 검색 엔진이 정답으로 인용할 텍스트를 먼저 제공합니다.</p>\n"
        "<p><strong>CTA</strong> (Call to Action)<br>\n"
        "방문자에게 다음 행동(문의, 다운로드, 가입)을 유도하는 버튼이나 링크. "
        "Answer-first 5줄의 마지막 문장이 CTA 역할을 합니다.</p>\n"
        "<p><strong>H1</strong> (복습)<br>\n"
        "HTML에서 가장 큰 대제목 태그. AI 검색 엔진이 페이지 주제를 파악하는 1차 신호이며, "
        "Answer-first 블록은 반드시 H1 바로 아래에 배치합니다.</p>\n"
        "<p><strong>Hero section</strong><br>\n"
        "웹페이지 최상단의 대형 배너 영역. 첫 화면에 보이는 가장 눈에 띄는 섹션으로, "
        "/index 페이지 재구성 시 핵심 대상입니다.</p>\n"
        "</div>\n\n"

        "### 배치 원칙\n\n"
        "<div class='callout'>\n"
        "Answer-first 블록은 반드시 <strong>H1 직하단</strong>에 배치합니다.<br>\n"
        "길이: <strong>2~6문장</strong> (한국어 350~650자)<br>\n"
        "순서: <strong>정의 -> 대상 -> 방식 -> 성과 -> 행동(CTA)</strong>\n"
        "</div>\n\n"

        "### 대상 페이지 10개\n\n"
        "| # | 페이지 | 현재 Answer 점수 | 목표 | 핵심 액션 |\n"
        "|---|--------|-----------------|------|-----------|\n"
        "| P0-6 | /service_custom | 3 | 5 | Answer-first 2~6문장 + 목업 |\n"
        "| P0-7 | /service_online | 3 | 5 | LMS 정의/기능/운영 Answer |\n"
        "| P0-8 | /service_online_enterprise | 3 | 5 | 스킬진단->IDP->성과 플로우 |\n"
        "| P0-9 | /refer_customer | 3 | 5 | Hub 상단 스펙 정의 문장 |\n"
        "| P0-10 | /resource_report | 3 | 5 | Report 허브 방법론 Answer |\n"
        "| P0-11 | /resource_bizletter | 3 | 5 | Newsletter 허브 Answer |\n"
        "| P0-12 | /contact_mktg | 2 | 4 | Contact FAQ 상단 요약 |\n"
        "| P0-13 | /index | 3 | 5 | Hero 섹션 재구성 |\n"
        "| P0-14 | /resource_insight_25trend | 4 | 5 | Answer-first 강화 |\n"
        "| P0-15 | /service_aicamp | 3 | 5 | 교육 대상/결과물 Answer |\n\n"

        "### 템플릿 1: 서비스 페이지용\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "## [서비스명] 개요\n\n"
        "[서비스명]은(는) [대상 조직/직무]가 [비즈니스 목표]를 달성하도록 돕는\n"
        "[서비스 유형: 교육/컨설팅/플랫폼]입니다.\n"
        "[제공 방식: 온라인/오프라인/블렌디드]으로 진행되며,\n"
        "[기간/시수/운영 방식]을 [조직 상황]에 맞춰 설계합니다.\n\n"
        "도입 시 [사전 진단/인터뷰] 이후 [커리큘럼/실습 예제]를 확정하고,\n"
        "운영 중에는 [학습관리/참여 관리/성과 측정]을 제공합니다.\n"
        "산출물은 [커리큘럼/실습자료/운영 리포트]이며,\n"
        "[보안/폐쇄망] 등 제약조건도 반영합니다.\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### 템플릿 2: 사례(레퍼런스) 페이지용\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "## [사례 제목] 사례 요약\n\n"
        "이 사례는 [산업/조직 유형]의 [대상]을 대상으로 [주제] 교육을\n"
        "[방식]으로 운영한 결과를 요약합니다.\n"
        "운영 스펙은 [총 시수].[기간].[인원]이며,\n"
        "평균 만족도는 [점수]입니다(측정 기준: [설문 기준]).\n"
        "핵심 설계는 [사전 진단/직무 인터뷰]를 통해 [현업 문제]를 해결하는\n"
        "실습 중심으로 구성했습니다.\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### 템플릿 3: 리소스(리포트/가이드) 페이지용\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "## [자료명] 개요\n\n"
        "이 자료는 [주제]에 대해 [대상]에게 필요한 [산출물 유형]\n"
        "체크리스트를 [분량]으로 정리한 [가이드/리포트]입니다.\n"
        "핵심 내용은 [핵심 항목 3개]이며,\n"
        "각 항목은 [적용 레벨]별로 바로 실행할 수 있도록 구성했습니다.\n"
        "본문에는 [통계/사례/정의]가 포함되어 있으며,\n"
        "근거는 [출처 레벨] 자료를 우선 인용했습니다.\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### /service_custom Answer-first 초안 예시\n\n"
        "<div class='browser-mockup'>\n"
        "<strong>[Before]</strong> H1 아래 바로 기능 목록 나열<br><br>\n"
        "<strong>[After]</strong> H1 아래 5줄 Answer-first:<br>\n"
        "1. 기업 맞춤형 생성형 AI 교육은 조직의 직무별 AI 활용 역량을 높이는 교육 서비스입니다.<br>\n"
        "2. 임원/관리자/실무자 등 대상별로 커리큘럼을 분리 설계합니다.<br>\n"
        "3. 온라인/오프라인/블렌디드 방식으로 4~12주간 운영합니다.<br>\n"
        "4. 교육 후 직무 적용도와 만족도를 측정하여 성과 리포트를 제공합니다.<br>\n"
        "5. 도입 상담은 문의 폼에서 신청하실 수 있습니다.\n"
        "</div>\n\n"

        "### 작성 규칙\n\n"
        "<div class='compare-cards'>\n"
        "<div><strong>좋은 예</strong><br>\n"
        "- 정의 -> 대상 -> 방식 -> 성과 -> CTA 순서 준수<br>\n"
        "- 구체적 숫자 포함 (4~12주, 만족도 4.7/5)<br>\n"
        "- 1문장 25~45자 유지</div>\n"
        "<div><strong>나쁜 예</strong><br>\n"
        "- 회사 소개부터 시작 (정의 누락)<br>\n"
        "- 모호한 표현 ('최고의 교육', '혁신적인')<br>\n"
        "- 6문장 초과 (너무 긴 블록은 AI가 요약 시 핵심을 놓침)</div>\n"
        "</div>\n\n"

        "### DoD (완료 기준)\n\n"
        "- 2~6문장 (한국어 350~650자)\n"
        "- 정의 -> 대상 -> 제공 형태 -> 산출물 -> 도입조건 순서\n"
        "- 5인 이상 리뷰 (마케팅/편집/운영 각 1인)\n"
        "- 스크린샷 + 코드 커밋 완료\n"
        "- QA: 페이지 상단 가시성 확인 (모바일/데스크톱)"
    ), 1, extension_md=(
        "### 페이지별 Answer-first 작성 가이드\n\n"
        "**서비스 페이지 (/service_custom, /service_online, /service_aicamp)**:\n"
        "- 서비스명 1회 이상 포함, 과도하게 반복하지 않기\n"
        "- 대상 -> 목표 -> 방식 -> 산출물 -> 조건 순서 고수\n"
        "- 2~4문장 권장 (총 350~450자)\n\n"
        "**사례 페이지 (/refer_customer)**:\n"
        "- 숫자(시수/만족도) 필수 포함\n"
        "- 현업 문제 -> 설계 방법 -> 재사용 포인트 순서\n"
        "- 2~4문장 권장 (총 350~500자)\n\n"
        "**리소스 페이지 (/resource_report, /resource_bizletter)**:\n"
        "- 핵심 항목 3개 명시\n"
        "- 활용 시나리오를 구체적으로 제시\n"
        "- 2~4문장 권장 (총 350~500자)\n\n"
        "### 금지 사항\n\n"
        "- 과장 표현 ('업계 최고', '혁신적인', '획기적인')\n"
        "- 정의 없이 기능만 나열\n"
        "- CTA 없이 끝나는 블록"
    ))

    # -- M6-3 Quiz --
    s = add_step(m, "quiz", "Answer-first 배치 원칙", (
        "Answer-first 블록의 올바른 배치 위치와 구성 원칙은 무엇인가요?"
    ), 2)
    add_option(s, "A", "페이지 최하단에 10문장 이상의 상세 설명을 배치", 0,
               "Answer-first는 상단 배치가 핵심입니다. 최하단에 배치하면 AI 크롤러가 해당 텍스트를 "
               "정답으로 인식하지 못합니다. H1 직하단에 2~6문장으로 간결하게 배치해야 합니다.", 1)
    add_option(s, "B", "H1 직하단에 2~6문장, 정의->대상->방식->성과->행동 순서", 1,
               "정답입니다! AI 검색 엔진은 H1 바로 아래의 텍스트를 가장 먼저 인용 후보로 평가합니다. "
               "2~6문장으로 핵심 정보를 정의->대상->방식->성과->CTA 순서로 구성하면 "
               "인용 확률이 가장 높아집니다.", 2)
    add_option(s, "C", "사이드바에 키워드 목록으로 배치", 0,
               "사이드바는 본문 콘텐츠로 인식되지 않을 수 있습니다. Answer-first는 반드시 "
               "본문 영역의 H1 직하단에 자연스러운 문장으로 작성해야 합니다.", 3)
    add_option(s, "D", "이미지 alt 속성에만 텍스트를 삽입", 0,
               "alt 속성은 이미지 설명용이며, AI 검색 엔진이 정답 인용 텍스트로 사용하지 않습니다. "
               "본문 HTML에 직접 텍스트를 배치해야 인용 가능성이 생깁니다.", 4)

    # -- M6-3 Practice 1 --
    s = add_step(m, "practice", "/service_custom Answer-first 초안 배치", (
        "/service_custom 페이지의 Answer-first 5줄 요약에서 올바른 순서는 무엇인가요?"
    ), 3)
    add_option(s, "A", "CTA -> 성과 -> 방식 -> 대상 -> 정의 (역순)", 0,
               "역순으로 배치하면 AI가 맥락 없이 CTA부터 읽게 됩니다. 정의부터 시작해야 "
               "서비스의 본질을 먼저 파악할 수 있습니다.", 1)
    add_option(s, "B", "정의 -> 대상 -> 방식 -> 성과 -> CTA", 1,
               "정답입니다! '무엇인가 -> 누구를 위한가 -> 어떻게 진행되는가 -> 어떤 성과가 있는가 "
               "-> 다음 행동은 무엇인가' 순서가 AI와 사용자 모두에게 가장 자연스러운 흐름입니다.", 2)
    add_option(s, "C", "성과 -> 성과 -> 성과 -> CTA -> CTA (성과 반복)", 0,
               "성과만 반복하면 정의와 대상이 빠져 AI가 서비스의 본질을 파악하지 못합니다. "
               "5줄 각각이 서로 다른 정보를 담아야 합니다.", 3)
    add_option(s, "D", "회사소개 -> 연혁 -> 수상 -> 파트너 -> 문의", 0,
               "회사 소개는 Answer-first가 아닙니다. Answer-first는 '이 서비스가 무엇인가'에 대한 "
               "직접적인 답변이어야 합니다.", 4)

    # -- M6-3 Practice 2 --
    s = add_step(m, "practice", "/refer_customer Answer-first 판단", (
        "/refer_customer(사례 허브) 페이지에 적용할 Answer-first 템플릿은 3종 중 어떤 것인가요?"
    ), 4)
    add_option(s, "A", "서비스 페이지용 템플릿 (서비스 정의/대상/방식)", 0,
               "/refer_customer는 서비스 소개가 아니라 교육 사례를 모아둔 허브 페이지입니다. "
               "사례 템플릿을 적용해야 산업/대상/성과 정보가 자연스럽게 드러납니다.", 1)
    add_option(s, "B", "사례(레퍼런스) 페이지용 템플릿", 1,
               "정답입니다! /refer_customer는 교육 사례를 모아둔 허브이므로 사례 템플릿이 적합합니다. "
               "'산업/조직 유형 -> 대상 -> 주제 -> 방식 -> 운영 스펙 -> 만족도' 순서로 "
               "작성하면 AI가 사례 정보를 정확하게 인용할 수 있습니다.", 2)
    add_option(s, "C", "리소스(리포트/가이드) 페이지용 템플릿", 0,
               "리소스 템플릿은 다운로드 가능한 자료(리포트, 가이드)에 적합합니다. "
               "/refer_customer는 사례 모음 페이지이므로 사례 템플릿이 맞습니다.", 3)
    add_option(s, "D", "템플릿 없이 자유 형식으로 작성", 0,
               "자유 형식은 품질 편차를 만들고, 10개 페이지에 일관성 있게 적용하기 어렵습니다. "
               "3종 템플릿 중 페이지 유형에 맞는 것을 선택하세요.", 4)

    # ----------------------------------------------------------------
    # Module 6-4: Proof-first 신뢰 강화 (P0-16~25)
    # ----------------------------------------------------------------
    m = add_module(6, "6-4: Proof-first 신뢰 강화",
                   "상위 10개 랜딩 페이지에 통계/인용/외부 출처 블록을 표준화합니다.", 4)

    # -- M6-4 Reading --
    add_step(m, "reading", "Proof-first 블록 구성법 & 출처 신뢰도 기준", (
        "## Proof-first 블록 구성법 & 출처 신뢰도 기준\n\n"
        "### 왜 Proof-first인가?\n\n"
        "Answer-first로 정답 문장을 배치한 후, 바로 아래에 **근거(Proof) 블록**을 추가하면 "
        "AI 검색 엔진이 '출처 있는 주장'으로 인식하여 인용 우선순위가 높아집니다.\n\n"

        '<div class="callout glossary">\n'
        "<p><strong>Proof-first</strong><br>\n"
        "Answer-first 직하단에 통계·인용·외부 출처 블록을 배치하여 주장의 신뢰도를 높이는 전략. "
        "Answer-first와 짝을 이루는 GEO 핵심 기법입니다.</p>\n"
        "<p><strong>Tier</strong> (출처 신뢰도 계층)<br>\n"
        "출처의 공신력 등급. Tier 1(정부/학술 기관), Tier 2(산업 리서치/글로벌 컨설팅), "
        "Tier 3(미디어/블로그). Proof 블록에는 Tier 1~2 출처를 우선 사용합니다.</p>\n"
        "<p><strong>Citation</strong> (복습)<br>\n"
        "AI가 답변에서 '출처: 우리 사이트'라고 표시하는 것. "
        "Proof 블록이 있으면 AI가 신뢰할 수 있는 출처로 인식하여 인용 확률이 높아집니다.</p>\n"
        "<p><strong>E-E-A-T</strong> (복습)<br>\n"
        "경험·전문성·권위·신뢰 — AI가 콘텐츠를 믿을지 판단하는 4가지 기준. "
        "Proof-first는 E-E-A-T 중 '신뢰(Trust)' 신호를 직접 강화합니다.</p>\n"
        "</div>\n\n"

        "### Proof 3요소\n\n"
        "<div class='hierarchy-box'>\n"
        "<strong>1. 핵심 통계</strong>: 수치 + 기간 + 표본 + 정의 + 출처 링크<br>\n"
        "<strong>2. 핵심 인용</strong>: 신뢰할 수 있는 기관/저자의 원문 발췌 (2~3문장)<br>\n"
        "<strong>3. 근거 출처</strong>: 3~7개 외부 링크 (크롤링 가능한 공개 페이지)\n"
        "</div>\n\n"

        "### 출처 신뢰도 Tier\n\n"
        "<div class='hierarchy-box'>\n"
        "<strong>Tier 1 (최우선)</strong>: 정부 기관, 학술 연구, 국제 표준 기구<br>\n"
        "예: 고용노동부, OECD, IEEE, Nature<br><br>\n"
        "<strong>Tier 2 (권장)</strong>: 산업 리서치, 글로벌 컨설팅 리포트<br>\n"
        "예: Gartner, McKinsey, Deloitte, IDC<br><br>\n"
        "<strong>Tier 3 (보조)</strong>: 미디어, 기업 블로그, 뉴스 기사<br>\n"
        "예: Forbes, TechCrunch, 기업 공식 블로그\n"
        "</div>\n\n"

        "### Proof-first 템플릿\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "## 근거 (Proof Block)\n\n"
        "### 핵심 통계\n"
        "- **[지표A]**: [수치] ([기간], [표본], [정의])\n"
        "  -- 출처: [링크]\n"
        "- **[지표B]**: [수치] ([기간], [표본])\n"
        "  -- 출처: [링크]\n\n"
        "### 핵심 인용\n"
        "> \"[원문 텍스트 발췌, 2~3문장]\"\n"
        "> -- [기관/저자명], [연도]\n\n"
        "### 근거 출처 (3~7개)\n"
        "1. [1차 가이드/표준] -- [설명]\n"
        "2. [리서치/서베이] -- [설명]\n"
        "3. [케이스/벤치마크] -- [설명]\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### 10개 페이지 Proof 유형 매핑\n\n"
        "| 페이지 | 필요 Proof 유형 | 핵심 통계 예시 |\n"
        "|--------|-----------------|----------------|\n"
        "| /service_custom | 외부 교육 효과/기업 트렌드 | AI 교육 도입률, ROI |\n"
        "| /service_online | LMS 선택 근거 (보안/운영) | LMS 시장 규모, 도입 표준 |\n"
        "| /refer_customer | 사례 통계 (만족도/시수) | 내부 데이터 요약 |\n"
        "| /resource_report | Report 방법론 (표본/기간) | 서베이 방법론 |\n"
        "| /index | 브랜드 신뢰도 (고객사/수료자) | 수료자 통계 |\n\n"

        "### 통계 작성 규칙\n\n"
        "<div class='compare-cards'>\n"
        "<div><strong>좋은 통계</strong><br>\n"
        "- 기간/표본/정의를 함께 명시<br>\n"
        "- 출처 URL이 크롤링 가능한 공개 페이지<br>\n"
        "- Tier 1~2 출처 우선 사용</div>\n"
        "<div><strong>나쁜 통계</strong><br>\n"
        "- '많은 기업이 도입하고 있다' (수치 없음)<br>\n"
        "- 출처 링크 없는 수치 인용<br>\n"
        "- 5년 이상 된 오래된 데이터</div>\n"
        "</div>\n\n"

        "### DoD (완료 기준)\n\n"
        "- 통계 2~3개 (출처 확인)\n"
        "- 인용문 1개 (신뢰도 Tier 1~2 우선)\n"
        "- 외부 링크 5~7개 (크롤링 가능 확인)\n"
        "- 페이지 본문과 일치도 검증\n"
        "- QA: 출처 링크 모두 유효성 확인"
    ), 1, extension_md=(
        "### Proof 블록 품질 체크리스트\n\n"
        "- [ ] 통계에 기간, 표본, 정의가 모두 명시되어 있는가?\n"
        "- [ ] 인용문의 출처가 Tier 1~2인가?\n"
        "- [ ] 외부 링크가 모두 접속 가능한가?\n"
        "- [ ] 2차 출처(뉴스 기사)에는 1차 출처 링크가 함께 있는가?\n"
        "- [ ] Answer-first 바로 아래에 배치되어 있는가?\n\n"
        "### 출처 검증 방법\n\n"
        "1. 각 링크를 직접 접속하여 200 응답 확인\n"
        "2. robots.txt에서 차단되지 않았는지 확인\n"
        "3. 콘텐츠가 인용한 통계/문장과 일치하는지 확인\n"
        "4. 발행일이 2년 이내인지 확인 (가능하면 1년 이내)\n"
        "5. 월 1회 전체 출처 유효성 재검증"
    ))

    # -- M6-4 Quiz --
    s = add_step(m, "quiz", "출처 선정 기준", (
        "Proof 블록에 사용할 출처를 선정할 때 가장 올바른 기준은 무엇인가요?"
    ), 2)
    add_option(s, "A", "가장 최근에 발행된 블로그 글을 무조건 선택", 0,
               "블로그 글은 Tier 3 출처로 보조적 역할에 적합합니다. Proof 블록의 핵심 통계에는 "
               "정부/학술(Tier 1)이나 산업 리서치(Tier 2) 출처를 우선 사용해야 신뢰도가 높아집니다.", 1)
    add_option(s, "B", "Tier 1~2 출처 우선, 기간/표본/정의를 함께 명시", 1,
               "정답입니다! 정부/학술 기관(Tier 1)이나 산업 리서치(Tier 2)의 데이터를 우선 사용하고, "
               "통계에는 반드시 기간, 표본 크기, 정의를 함께 명시해야 AI 검색 엔진이 "
               "신뢰할 수 있는 근거로 인식합니다.", 2)
    add_option(s, "C", "출처 없이 자체 데이터만 사용", 0,
               "자체 데이터도 유효하지만, 외부 제3자 출처가 함께 있어야 신뢰도 신호가 강화됩니다. "
               "자체 데이터 + 외부 출처 조합이 가장 효과적입니다.", 3)
    add_option(s, "D", "출처 링크 없이 기관명만 텍스트로 언급", 0,
               "기관명만 언급하고 링크가 없으면 AI 엔진이 출처를 검증할 수 없습니다. "
               "반드시 크롤링 가능한 공개 URL을 함께 제공해야 합니다.", 4)

    # -- M6-4 Practice 1 --
    s = add_step(m, "practice", "Proof 블록 구성", (
        "/service_custom의 Proof 블록에 사용할 통계 3개의 출처 조합으로 가장 적절한 것은 무엇인가요?"
    ), 3)
    add_option(s, "A", "자사 블로그 3개 (모두 Tier 3)", 0,
               "동일 출처 Tier의 자사 콘텐츠만으로는 제3자 신뢰도를 확보하기 어렵습니다. "
               "Tier 1~2 외부 출처를 반드시 포함해야 합니다.", 1)
    add_option(s, "B", "학술 연구 1개(Tier 1) + 산업 리서치 1개(Tier 2) + 자체 조사 1개", 1,
               "정답입니다! Tier 1(학술)로 공신력을 확보하고, Tier 2(산업 리서치)로 시장 맥락을 보강하며, "
               "자체 조사로 고유 데이터를 제공하는 조합이 가장 설득력 있습니다.", 2)
    add_option(s, "C", "경쟁사 웹사이트 3개에서 수치 인용", 0,
               "경쟁사 웹사이트는 독립적 출처로 인정받기 어렵고, 데이터 정확성을 검증하기도 곤란합니다. "
               "제3자 기관의 공식 데이터를 사용하세요.", 3)
    add_option(s, "D", "출처 없이 '업계에 따르면' 표현만 사용", 0,
               "출처가 명시되지 않은 통계는 AI 엔진이 신뢰할 수 없는 주장으로 분류합니다. "
               "반드시 구체적인 기관명과 링크를 함께 제공해야 합니다.", 4)

    # -- M6-4 Practice 2 --
    s = add_step(m, "practice", "출처 신뢰도 평가", (
        "다음 4개 출처 후보 중 /service_custom Proof 블록에 가장 적합한 2개 조합은 무엇인가요?\n\n"
        "(1) 고용노동부 '2025 기업교육 현황 조사' (Tier 1)\n"
        "(2) Gartner '2025 Enterprise AI Training Report' (Tier 2)\n"
        "(3) 개인 블로거의 교육 후기 (Tier 3)\n"
        "(4) 출처 불명의 인포그래픽 (Tier 없음)"
    ), 4)
    add_option(s, "A", "(3) + (4): 블로거 후기와 인포그래픽", 0,
               "Tier 3과 출처 불명 자료는 핵심 통계의 근거로 부적합합니다. "
               "Proof 블록의 신뢰도를 높이려면 Tier 1~2 출처를 우선 선택해야 합니다.", 1)
    add_option(s, "B", "(1) + (2): 고용노동부(Tier 1) + Gartner(Tier 2)", 1,
               "정답입니다! 정부 기관(Tier 1)과 글로벌 리서치(Tier 2)의 조합은 "
               "공신력과 시장 맥락을 동시에 제공합니다. AI 검색 엔진이 가장 선호하는 "
               "출처 조합입니다.", 2)
    add_option(s, "C", "(1) + (3): 정부 데이터와 개인 블로그", 0,
               "정부 데이터(Tier 1)는 적합하지만, 개인 블로그(Tier 3)보다는 "
               "산업 리서치(Tier 2)를 함께 사용하는 것이 더 균형 잡힌 근거를 제공합니다.", 3)
    add_option(s, "D", "(2) + (4): Gartner와 출처 불명 인포그래픽", 0,
               "Gartner(Tier 2)는 적합하지만, 출처 불명 자료는 신뢰도를 오히려 떨어뜨립니다. "
               "출처가 명확한 Tier 1~2 자료만 사용하세요.", 4)

    # ----------------------------------------------------------------
    # Module 6-5: 측정 체계 & 실험 설계 (P0-26~28)
    # ----------------------------------------------------------------
    m = add_module(6, "6-5: 측정 체계 & 실험 설계",
                   "KPI 3종 정의, Top 50 질문 세트, 주간 인용 로그, 4주 실험 루프를 설계합니다.", 5)

    # -- M6-5 Reading --
    add_step(m, "reading", "측정 체계 SOP & 실험 설계 가이드", (
        "## 측정 체계 SOP & 실험 설계 가이드\n\n"
        "### 왜 측정 체계가 필요한가?\n\n"
        "'무엇이 인용되는가'를 주간 단위로 추적해야 실험과 개선이 빠릅니다. "
        "측정 없는 콘텐츠 개선은 방향을 잃기 쉽습니다.\n\n"

        '<div class="callout glossary">\n'
        "<p><strong>KPI-A / KPI-B / KPI-C</strong><br>\n"
        "Stage 6 전용 3층 측정 체계. KPI-A = ChatGPT Search 인용 빈도(주 2회 측정), "
        "KPI-B = Google AI Overviews 노출(주 1회), KPI-C = 하위 질의 커버리지(주 1회).</p>\n"
        "<p><strong>AI Validator</strong> (복습)<br>\n"
        "AI에게 주기적으로 질문하여 우리 콘텐츠가 인용되는지 확인하는 프로세스. "
        "Stage 6에서는 Top 50 질문 세트로 주간 인용률을 추적합니다.</p>\n"
        "<p><strong>A/B Test</strong> (복습)<br>\n"
        "두 가지 버전(A: 기존, B: 변경)을 비교하여 어떤 것이 더 효과적인지 검증하는 실험. "
        "Stage 6에서는 4주 실험 루프로 Answer-first 길이, Proof 위치 등을 테스트합니다.</p>\n"
        "<p><strong>GA4</strong> (복습)<br>\n"
        "Google이 제공하는 무료 웹 분석 도구. "
        "utm_source=chatgpt.com 필터로 AI 검색 유입 트래픽을 분리 추적합니다.</p>\n"
        "</div>\n\n"

        "### KPI 3종 정의\n\n"
        '<div class="hierarchy-box">\n'
        '<table class="comparison-table"><thead><tr><th>KPI</th><th>정의</th><th>측정 빈도</th><th>도구</th><th>목표</th></tr></thead>\n'
        '<tbody>\n'
        '<tr><td>KPI-A</td><td>ChatGPT Search 인용 빈도</td><td>주 2회 (화/금 10:00)</td><td>수동 SERP + utm GA4</td><td>30일 +20% → 90일 +150~200%</td></tr>\n'
        '<tr><td>KPI-B</td><td>Google AI Overviews 노출</td><td>주 1회 (수 14:00)</td><td>Google Search 수동</td><td>30일 기준선 → 90일 +80%</td></tr>\n'
        '<tr><td>KPI-C</td><td>하위 질의 커버리지</td><td>주 1회 (목)</td><td>수동 평가 + AI Validator</td><td>30일 35% → 90일 85%+</td></tr>\n'
        '</tbody></table>\n'
        '</div>\n\n'

        "### KPI-A 측정 SOP\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "주 2회 (화/금 10:00)\n"
        "1. Top 50 질문 세트의 각 질문을 ChatGPT Search에 입력\n"
        "2. 상위 3개 출처 확인 (클릭 가능한 출처)\n"
        "3. b2b.fastcampus 노출 여부 기록\n"
        "4. 인용된 텍스트 스크린샷 + 출처 문장 로깅\n"
        "5. 해당 페이지 URL + 인용 블록 식별\n"
        "6. 주간 리포트: 노출 페이지/질문/인용문 요약\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### Top 50 질문 세트 (5카테고리 x 10)\n\n"
        "**카테고리 1: 기업 AI 교육 도입** -- 필요성, 시작법, 커리큘럼 설계, 역량 평가, 보안, 비용, 담당자 역할, 온/오프라인, 효과 측정, 직무별 차이\n\n"
        "**카테고리 2: 직무별 AI 활용** -- 영업, HR, 마케팅, 기획, 재무/회계, 법무, 운영, 고객 서비스, 데이터 분석, 경영진\n\n"
        "**카테고리 3: 스킬 진단 및 HRD** -- 진단 방법, 결과 반영, IDP 수립, 이점, 역량 모델, 매트릭스, 레벨 평가, 도구 선택, 실패 패턴, 로드맵\n\n"
        "**카테고리 4: 교육 효과 측정 및 ROI** -- ROI 계산, 지표, 수료율, 업무 적용도, 리포트 내용, 데이터 수집, 학습 경로, 비용 효과, KPI, 실무 활용\n\n"
        "**카테고리 5: 플랫폼 선택 및 보안** -- LMS 선택, LMS vs LXP, 보안 점검, RFP, 추천 기능, 마이그레이션, SaaS vs 자체구축, 폐쇄망, 채택률, 정보보안\n\n"

        "### 주간 인용 로그 양식\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "[주간 AI Validator 인용 로그]\n"
        "기간: YYYY-MM-DD ~ YYYY-MM-DD (Week XX)\n\n"
        "KPI-A: ChatGPT Search 인용\n"
        "| 질문 | 노출여부 | 위치 | 인용URL | 인용텍스트 | 스크린샷 |\n\n"
        "KPI-B: Google AI Overviews 노출\n"
        "| 질문 | 노출여부 | URL | 링크위치 | 스니펫 |\n\n"
        "KPI-C: 커버리지 평가\n"
        "3점(Answer+Proof): __개/50개 = __%\n"
        "2점(Answer만): __개\n"
        "1점(관련만): __개\n"
        "0점(커버없음): __개\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### AI Validator 핵심 프롬프트 (10개 중 5개)\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "Prompt 1: ChatGPT Search 인용 빈도 평가\n"
        "- Top 50 질문 -> ChatGPT Search -> b2b.fastcampus 노출 여부 기록\n\n"
        "Prompt 3: 상위 10 랜딩 Answer-first 평가 (0~5점)\n"
        "- 0점:없음 / 3점:요소불완전 / 5점:정의->대상->형태->산출물->조건 순서 완전\n\n"
        "Prompt 4: Proof 블록 신뢰도 평가\n"
        "- 통계 개수, 인용문 유무, 외부 링크 수, 출처 Tier 평가\n\n"
        "Prompt 7: 구조화 데이터 검증\n"
        "- Organization/BreadcrumbList/Event/Article/FAQPage 적용 여부\n\n"
        "Prompt 10: 주간 KPI 종합 리포트\n"
        "- KPI-A/B/C 통합, 트렌드, 다음주 액션 3개\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### 4주 실험 루프\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">4주 실험 루프</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">W1</div><div class="step-content"><div class="step-title">1주차: Answer-first 길이</div><div class="step-desc">2문장 vs 4문장 vs 6문장 — 5개 A/B 페이지 쌍</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">W2</div><div class="step-content"><div class="step-title">2주차: Proof 블록 위치</div><div class="step-desc">Answer 직하 vs 본문 중간</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">W3</div><div class="step-content"><div class="step-title">3주차: 스포크 길이</div><div class="step-desc">600자 vs 1,000자 vs 1,200자</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">W4</div><div class="step-content"><div class="step-title">4주차: 내부 링크 수</div><div class="step-desc">1개 vs 3개 vs 5개</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">✓</div><div class="step-content"><div class="step-title">주간 리뷰</div><div class="step-desc">가설 검증 결과 리포트 → 승자 테크닉 전사 적용</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'

        "### 6개 실험 가설 (H1~H6)\n\n"
        "- **H1**: Answer-first 적용 시 인용 빈도 +20% (30일, 5페이지 쌍)\n"
        "- **H2**: Answer+Proof 조합 시 인용률 추가 +15%\n"
        "- **H3**: 스포크 1,000자 전후에서 최고 인용 효율\n"
        "- **H4**: 허브 스포크 링크 7개 그룹이 3개보다 커버율 +30%\n"
        "- **H5**: Trust 신호(작성자/발행일) 명시 시 인용 안정성 +10%\n"
        "- **H6**: BreadcrumbList+Organization 적용 시 Google AI 노출 +25%"
    ), 1, extension_md=(
        "### Top 50 질문 전체 리스트 (발췌)\n\n"
        "**카테고리 1 예시**:\n"
        "1. 기업에서 생성형 AI 교육이 필요한 이유는 무엇인가\n"
        "2. 기업 AI 교육은 어떻게 시작해야 하는가\n"
        "3. 기업 AI 교육 커리큘럼은 어떻게 설계하는가\n"
        "...(총 10개)\n\n"
        "**주간 인용 로그 구글 시트 운영 팁**:\n"
        "- 매주 화/금 업데이트\n"
        "- 스크린샷은 별도 폴더에 날짜별 저장\n"
        "- 주간 집계: 노출 페이지 수, 신규 노출, 손실된 노출\n\n"
        "### H1 실험 설계 상세\n\n"
        "- What: Answer-first 블록 유무 (적용 vs 미적용)\n"
        "- Experiment: /service_custom 등 5개 페이지 (Answer 적용)\n"
        "- Control: 유사 주제 5개 (미적용)\n"
        "- Duration: 30일\n"
        "- Pass: A그룹 인용 빈도가 B보다 20% 이상 높음"
    ))

    # -- M6-5 Quiz --
    s = add_step(m, "quiz", "KPI 측정 주기와 방법", (
        "GEO KPI 측정의 올바른 주기와 방법은 무엇인가요?"
    ), 2)
    add_option(s, "A", "월 1회 자동 리포트만 확인", 0,
               "월 1회로는 AI 인용의 빠른 변동을 추적할 수 없습니다. KPI-A는 주 2회(화/금), "
               "KPI-B는 주 1회(수), KPI-C는 주 1회(목)로 측정해야 적시 대응이 가능합니다.", 1)
    add_option(s, "B", "주 2회(화/금 10:00) Top 50 수동 측정 + utm GA4 필터 추적", 1,
               "정답입니다! ChatGPT Search 인용은 주 2회 수동 SERP 관찰과 utm_source=chatgpt.com "
               "GA4 트래픽 추적을 병행해야 정확한 인용 빈도를 파악할 수 있습니다.", 2)
    add_option(s, "C", "분기 1회 외부 업체에 의뢰", 0,
               "분기 1회는 너무 느립니다. 4주 실험 루프를 운영하려면 최소 주간 단위 데이터가 필요합니다. "
               "내부 팀이 직접 주간 측정을 수행해야 합니다.", 3)
    add_option(s, "D", "GA4 전체 트래픽만 확인하고 AI 인용은 추적하지 않음", 0,
               "GA4 전체 트래픽에는 AI 검색 유입이 구분되지 않습니다. "
               "utm_source=chatgpt.com 필터와 수동 SERP 관찰을 함께 사용해야 AI 인용 효과를 측정할 수 있습니다.", 4)

    # -- M6-5 Practice 1 --
    s = add_step(m, "practice", "주간 인용 로그 해석", (
        "주간 인용 로그에서 특정 질문의 ChatGPT 인용이 0건으로 나타났습니다. "
        "가장 적절한 대응 순서는 무엇인가요?"
    ), 3)
    add_option(s, "A", "해당 질문을 목록에서 삭제하고 다른 질문으로 교체", 0,
               "질문을 삭제하면 추적 연속성이 깨집니다. 먼저 해당 질문에 대응하는 페이지의 "
               "Answer-first 적용 여부를 확인하고, 미적용이면 P0로 에스컬레이션해야 합니다.", 1)
    add_option(s, "B", "Answer-first 적용 확인 -> 미적용이면 P0 에스컬레이션", 1,
               "정답입니다! 인용 0건의 가장 흔한 원인은 해당 질문에 대응하는 페이지에 "
               "Answer-first 블록이 없는 것입니다. 적용 여부를 먼저 확인하고, "
               "미적용이면 즉시 P0 티켓으로 에스컬레이션해야 합니다.", 2)
    add_option(s, "C", "아무 조치 없이 다음 주까지 관망", 0,
               "2주 이상 방치하면 경쟁사에 인용 위치를 빼앗길 수 있습니다. "
               "인용 0건은 즉시 원인을 파악하고 대응해야 합니다.", 3)
    add_option(s, "D", "외부 링크를 대량으로 구매하여 해결", 0,
               "외부 링크 구매는 GEO 전략과 무관하며 오히려 품질 신호를 떨어뜨릴 수 있습니다. "
               "온사이트 콘텐츠(Answer-first, Proof) 보강이 1순위입니다.", 4)

    # -- M6-5 Practice 2 --
    s = add_step(m, "practice", "실험 가설 설계", (
        "H1(Answer-first 효과 검증) A/B 테스트의 올바른 구성은 무엇인가요?"
    ), 4)
    add_option(s, "A", "1개 페이지만 테스트, 7일간 관찰", 0,
               "1개 페이지로는 통계적 유의성을 확보하기 어렵습니다. "
               "최소 5개 페이지 쌍으로 30일간 추적해야 신뢰할 수 있는 결과를 얻을 수 있습니다.", 1)
    add_option(s, "B", "5개 페이지 쌍(적용 vs 미적용), 30일간 추적", 1,
               "정답입니다! 5개 비교 페이지 쌍을 30일간 추적하면 Answer-first 적용 효과를 "
               "통계적으로 검증할 수 있습니다. Pass 기준은 A그룹 인용 빈도가 B보다 20% 이상 높은 것입니다.", 2)
    add_option(s, "C", "전체 페이지에 동시 적용, 이전 데이터와 비교", 0,
               "전체 적용은 대조군이 없어 다른 변수(시즌, 경쟁사)의 영향을 분리할 수 없습니다. "
               "반드시 A/B 비교 구조로 테스트해야 합니다.", 3)
    add_option(s, "D", "테스트 없이 바로 전사 적용", 0,
               "테스트 없이 전사 적용하면 효과가 없을 경우 리소스 낭비가 큽니다. "
               "먼저 소규모 실험으로 효과를 검증한 후 확산하는 것이 안전합니다.", 4)

    # ----------------------------------------------------------------
    # Module 6-6: 허브-스포크 팬아웃 확장 (P1-1~20)
    # ----------------------------------------------------------------
    m = add_module(6, "6-6: 허브-스포크 팬아웃 확장",
                   "7개 허브 구축, 60개 스포크 1차 발행, 사례/리소스 표준화, 내부링크를 설계합니다.", 6)

    # -- M6-6 Reading --
    add_step(m, "reading", "허브-스포크 구축 & 내부링크 SOP", (
        "## 허브-스포크 구축 & 내부링크 SOP\n\n"
        "### 왜 허브-스포크 구조인가?\n\n"
        "AI 검색 엔진의 query fan-out 메커니즘은 하위 질의별로 전문 페이지를 찾습니다. "
        "허브-스포크 구조를 통해 하위 질의 커버리지를 확대하면 인용 기회가 크게 늘어납니다.\n\n"

        '<div class="callout glossary">\n'
        "<p><strong>Fan-out</strong> (Query fan-out)<br>\n"
        "AI 검색 엔진이 하나의 질문을 여러 하위 질문으로 분해하여, "
        "각각에 대해 전문 페이지를 찾아 종합 답변을 생성하는 메커니즘입니다.</p>\n"
        "<p><strong>Hub-Spoke</strong> (복습: Hub-Cluster)<br>\n"
        "핵심 주제 페이지(허브)에서 세부 페이지(스포크)로 체계적으로 연결하는 사이트 구조. "
        "허브는 상위 질문에 대한 개요와 네비게이션을, 스포크는 하위 질문에 대한 집중 답변을 제공합니다.</p>\n"
        "<p><strong>Batch</strong> (배치 발행)<br>\n"
        "대량의 스포크 페이지를 한꺼번에 발행하지 않고, 20개씩 묶어 순차 발행하는 방식. "
        "Batch 1에는 Top 50 질문 커버리지가 높은 스포크를 우선 배치합니다.</p>\n"
        "<p><strong>Internal Link</strong> (복습)<br>\n"
        "같은 웹사이트 안에서 페이지끼리 연결하는 하이퍼링크. "
        "Hub→Spoke, Spoke→Hub, Spoke↔Spoke 3종으로 구분하여 표준화합니다.</p>\n"
        "</div>\n\n"

        "### 7개 허브 목록\n\n"
        '<div class="tree-diagram">\n'
        '<div class="tree-title">허브-스포크 아키텍처 (7 Hubs)</div>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node root">홈 (Index)</span>\n'
        '<ul class="tree">\n'
        '<li class="tree-item"><span class="tree-node">Hub 1: 기업 생성형 AI 교육 도입 가이드 (스포크 10개)</span></li>\n'
        '<li class="tree-item"><span class="tree-node">Hub 2: 스킬 진단/스킬 기반 HRD (스포크 8개)</span></li>\n'
        '<li class="tree-item"><span class="tree-node">Hub 3: 교육 ROI/러닝 애널리틱스 (스포크 10개)</span></li>\n'
        '<li class="tree-item"><span class="tree-node">Hub 4: 기업교육 플랫폼(LMS/LXP) 선택 (스포크 9개)</span></li>\n'
        '<li class="tree-item"><span class="tree-node">Hub 5: 직무별 AI 활용 시나리오 (스포크 8개)</span></li>\n'
        '<li class="tree-item"><span class="tree-node">Hub 6: 폐쇄망/보안 환경 AI 교육 (스포크 7개)</span></li>\n'
        '<li class="tree-item"><span class="tree-node">Hub 7: 벤치마크/사례 라이브러리 (스포크 8개)</span></li>\n'
        '</ul>\n'
        '</li>\n'
        '</ul>\n'
        '</div>\n\n'

        "### 스포크 페이지 포맷 (600~1,200자)\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "# [스포크 페이지 타이틀]\n"
        "*발행일: YYYY-MM-DD | 카테고리: [허브명]*\n\n"
        "## 개요 (Answer-first, 2~4문장)\n"
        "[Answer-first 템플릿 적용]\n\n"
        "## 단계별 실행 (3~7 steps)\n"
        "### 1단계: [단계명] -- [설명]\n"
        "### 2단계: [단계명] -- [설명]\n\n"
        "## 체크리스트 (10~20 items)\n"
        "- [ ] [항목 1]\n"
        "- [ ] [항목 2]\n\n"
        "## 자주 묻는 질문 (5~8 Q&A)\n"
        "### Q1. [질문]\n"
        "[답변 1~2문장]\n\n"
        "## 근거 (Proof Block)\n"
        "[Proof-first 템플릿 적용]\n"
        "</code></pre>\n"
        "</div>\n\n"

        "### 내부링크 3종 규칙\n\n"
        "1. **Hub -> Spoke**: 허브 본문에 최소 3개 스포크 링크 (설명적 앵커)\n"
        "2. **Spoke -> Hub**: 스포크 상단에 상위 허브 역링크 1개\n"
        "3. **Spoke <-> Spoke**: '다음 읽기' 박스에 관련 스포크 3~5개\n\n"

        "### 앵커 텍스트 가이드\n\n"
        "<div class='compare-cards'>\n"
        "<div><strong>좋은 앵커</strong><br>\n"
        "- 'IDP(개인별 학습계획) 템플릿 다운로드'<br>\n"
        "- '스킬 매트릭스 작성 가이드'<br>\n"
        "- '조직 전환 단계별 로드맵'</div>\n"
        "<div><strong>나쁜 앵커</strong><br>\n"
        "- '여기를 클릭하세요'<br>\n"
        "- '더보기'<br>\n"
        "- '링크'</div>\n"
        "</div>\n\n"

        "### DoD\n\n"
        "- 허브 7개 페이지 배포 (Answer-first + Proof-first)\n"
        "- 스포크 60개 1차 발행 (600~1,200자)\n"
        "- 허브-스포크 내부 링크 맵 완료\n"
        "- 사례/리포트/뉴스레터 자산 표준화 완료"
    ), 1, extension_md=(
        "### 허브 1 스포크 예시 (10개)\n\n"
        "1. 기업 생성형 AI 교육 도입 체크리스트 30\n"
        "2. 생성형 AI 교육 RFP 템플릿\n"
        "3. 기업용 ChatGPT 교육에서 꼭 정해야 하는 7가지\n"
        "4. 직무별 AI 교육 니즈 수집 설문 문항 25\n"
        "5. 사내 AI 활용 가이드라인 초안 구성 예시\n"
        "6. 생성형 AI 교육 커리큘럼을 '업무 결과물' 기준으로 설계하는 법\n"
        "7. 전사 교육 vs 직무 특화 교육: 언제 무엇이 효과적인가\n"
        "8. 1일 AI 워크숍 설계 템플릿\n"
        "9. AI 교육 강사 역량 모델\n"
        "10. 기업 AI 교육 도입 로드맵: 3/6/12개월\n\n"
        "### 내부링크 QA 체크리스트\n\n"
        "- [ ] 모든 허브가 홈에서 네비게이션 가능\n"
        "- [ ] 모든 스포크가 상위 허브로 역링크\n"
        "- [ ] 스포크 간 상호링크 3개 이상\n"
        "- [ ] 앵커 텍스트 100% 설명적 (단어 3개 이상)\n"
        "- [ ] 404 링크 0개"
    ))

    # -- M6-6 Quiz --
    s = add_step(m, "quiz", "허브-스포크 아키텍처 원리", (
        "허브-스포크 아키텍처에서 허브와 스포크의 올바른 역할 구분은 무엇인가요?"
    ), 2)
    add_option(s, "A", "허브와 스포크 모두 동일한 상세 콘텐츠를 담는다", 0,
               "허브와 스포크의 역할이 동일하면 구조적 차별화가 없어집니다. "
               "허브는 상위 질문에 대한 개요와 네비게이션을, 스포크는 하위 질문에 대한 집중 답변을 제공해야 합니다.", 1)
    add_option(s, "B", "허브는 상위 질문 + 네비게이션, 스포크는 하위 질문 집중 답변", 1,
               "정답입니다! 허브는 '기업 AI 교육 도입이란?'처럼 상위 질문에 대한 Answer-first와 "
               "스포크로의 네비게이션을 제공하고, 스포크는 'AI 교육 RFP 작성법'처럼 "
               "구체적 하위 질문에 600~1,200자로 집중 답변합니다.", 2)
    add_option(s, "C", "허브는 링크 목록만, 스포크는 전체 사이트의 모든 정보를 담는다", 0,
               "허브가 링크 목록만 제공하면 자체 인용 가능성이 없어집니다. "
               "허브도 Answer-first + Proof-first를 갖추고, 스포크는 하위 질문에 집중해야 합니다.", 3)
    add_option(s, "D", "모든 페이지를 하나의 허브에 연결한다", 0,
               "하나의 허브에 모든 페이지를 연결하면 주제 전문성 신호가 약해집니다. "
               "7개 주제별 허브로 분리하여 각각의 전문성을 강화해야 합니다.", 4)

    # -- M6-6 Practice 1 --
    s = add_step(m, "practice", "허브 페이지 설계", (
        "Hub 1(기업 생성형 AI 교육 도입 가이드)에 연결할 스포크 10개 중 "
        "우선 발행할 3개를 선정하는 기준으로 가장 적절한 것은 무엇인가요?"
    ), 3)
    add_option(s, "A", "작성하기 가장 쉬운 3개를 먼저 발행", 0,
               "작성 용이성보다 전환 기여도가 우선입니다. Top 50 질문에서 자주 등장하고 "
               "전환에 직접 기여하는 스포크를 먼저 발행해야 KPI 개선 효과가 빠릅니다.", 1)
    add_option(s, "B", "전환 기여도가 높은 순서대로 3개 선정", 1,
               "정답입니다! 전환 기여도가 높은 스포크를 먼저 발행하면 Phase 2 초반부터 "
               "KPI-C(하위 질의 커버리지) 개선 효과를 확인할 수 있습니다. "
               "Top 50 질문 세트에서 빈도가 높은 하위 질문을 커버하는 스포크를 우선하세요.", 2)
    add_option(s, "C", "알파벳 순서로 3개 선정", 0,
               "알파벳 순서는 비즈니스 우선순위와 무관합니다. "
               "전환 기여도와 Top 50 질문 커버리지를 기준으로 선정해야 합니다.", 3)
    add_option(s, "D", "경쟁사가 작성하지 않은 주제 3개 선정", 0,
               "경쟁사 분석도 참고할 수 있지만, 1순위 기준은 자사 전환 기여도입니다. "
               "전환에 직접 연결되는 스포크를 먼저 발행하고, 경쟁 차별화는 2순위로 고려하세요.", 4)

    # -- M6-6 Practice 2 --
    s = add_step(m, "practice", "스포크 발행 우선순위", (
        "60개 스포크를 3개 배치(Batch)로 나누어 발행할 때 가장 적절한 기준은 무엇인가요?"
    ), 4)
    add_option(s, "A", "모든 허브에서 균등하게 배분 (각 허브 약 3개씩)", 0,
               "균등 배분은 공정해 보이지만, Top 50 질문 커버리지와 Phase 1 관련성을 고려하지 않습니다. "
               "우선순위가 높은 허브의 스포크를 먼저 발행해야 합니다.", 1)
    add_option(s, "B", "Top 50 질문 커버리지 + Phase 1 관련 스포크를 Batch 1에 우선 배치", 1,
               "정답입니다! Batch 1(20개)에는 Top 50 질문에서 빈도가 높은 하위 질문을 커버하는 "
               "스포크와 Phase 1에서 개선한 상위 10 랜딩과 직접 관련된 스포크를 우선 배치합니다. "
               "이렇게 하면 측정 체계와 연동되어 효과를 즉시 확인할 수 있습니다.", 2)
    add_option(s, "C", "가장 긴 콘텐츠부터 먼저 발행", 0,
               "콘텐츠 길이는 발행 우선순위 기준이 아닙니다. 스포크는 600~1,200자로 통일하고, "
               "비즈니스 임팩트가 큰 것부터 발행해야 합니다.", 3)
    add_option(s, "D", "랜덤으로 20개씩 나누어 발행", 0,
               "랜덤 배분은 전략적 의미가 없습니다. 각 배치가 KPI 개선에 기여할 수 있도록 "
               "우선순위 기반으로 구성해야 합니다.", 4)

    # ----------------------------------------------------------------
    # Module 6-7: 권위 구축 & AI Validator 자동화 (P2-1~11)
    # ----------------------------------------------------------------
    m = add_module(6, "6-7: 권위 구축 & AI Validator 자동화",
                   "구조화데이터 전사 적용, 외부 권위 확보, AI Validator 주간 루틴을 자동화합니다.", 7)

    # -- M6-7 Reading --
    add_step(m, "reading", "Phase 3 권위/자동화 SOP", (
        "## Phase 3 권위/자동화 SOP\n\n"
        "### 왜 Phase 3가 중요한가?\n\n"
        "Phase 1~2에서 콘텐츠와 구조를 정비했다면, Phase 3에서는 **외부 권위 신호**와 "
        "**자동화 루틴**으로 지속 가능한 GEO 운영 체계를 완성합니다.\n\n"

        '<div class="callout glossary">\n'
        "<p><strong>Organization</strong> (스키마 타입)<br>\n"
        "기업/단체의 공식 정보(이름, URL, 로고, 연락처)를 AI에게 전달하는 구조화 데이터 타입. "
        "모든 페이지에 필수 적용해야 합니다.</p>\n"
        "<p><strong>URL Inspection</strong><br>\n"
        "Google Search Console에서 실제 URL의 크롤링·렌더링·인덱싱 상태를 확인하는 도구. "
        "스키마 4단계 검증 파이프라인의 마지막 단계입니다.</p>\n"
        "<p><strong>Digital PR</strong> (복습)<br>\n"
        "온라인 매체에 기고, 보도자료, 인터뷰 등을 통해 브랜드를 노출하고 역링크를 확보하는 활동. "
        "Phase 3에서 외부 권위를 구축하는 핵심 수단입니다.</p>\n"
        "<p><strong>FAQPage</strong> (복습)<br>\n"
        "자주 묻는 질문 페이지를 AI에게 알려주는 구조화 데이터 타입. "
        "스포크 FAQ 섹션에 적용하면 리치 리절트 노출 기회가 늘어납니다.</p>\n"
        "</div>\n\n"

        "### 구조화데이터 전사 적용 (P2-1~5)\n\n"
        '<div class="hierarchy-box">\n'
        '<table class="comparison-table"><thead><tr><th>스키마</th><th>대상 페이지</th><th>우선순위</th></tr></thead>\n'
        '<tbody>\n'
        '<tr><td>Organization</td><td>모든 페이지</td><td>필수 (P2-1)</td></tr>\n'
        '<tr><td>BreadcrumbList</td><td>허브-스포크 네비</td><td>필수 (P2-2)</td></tr>\n'
        '<tr><td>Event</td><td>세미나 페이지</td><td>조건부 (P2-3)</td></tr>\n'
        '<tr><td>Article</td><td>인사이트 페이지</td><td>조건부 (P2-4)</td></tr>\n'
        '<tr><td>FAQPage</td><td>스포크 FAQ</td><td>권장 (P2-5)</td></tr>\n'
        '</tbody></table>\n'
        '</div>\n\n'

        "### 외부 권위 3축\n\n"
        "1. **오리지널 리포트**: 연 2회 발행 (표본/방법론 투명화) -- P2-9\n"
        "2. **고객사 공동 케이스**: 3건 (협력사 기고 + 상호 링크) -- P2-10\n"
        "3. **협회/미디어 기고**: 분기 2~3건 (역링크 수집) -- P2-11\n\n"
        "<div class='callout'>\n"
        "<strong>핵심 원칙</strong>: '자사 주장 반복'이 아니라, '제3자 출처가 b2b.fastcampus.co.kr로 "
        "링크하는 구조'를 만들어야 합니다. Google AI Overviews는 '다양한 출처 범위'를 선호합니다.\n"
        "</div>\n\n"

        "### AI Validator 주간 루틴\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">AI Validator 주간 루틴</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">매주 수요일</div><div class="step-desc">AI Validator 10개 프롬프트 자동 실행</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">결과 자동 로깅</div><div class="step-desc">구글 시트에 KPI-A/B/C 기록</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">이상 탐지</div><div class="step-desc">인용 급감(-20% 이상) 시 자동 알림</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">매주 금요일</div><div class="step-desc">주간 종합 리포트 생성 + 다음주 액션 확정</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'

        "### 인용 이상 대응 룰\n\n"
        "- **인용 0건 (2주 연속)**: Answer-first 존재 확인 -> 없으면 P0 작성, 있으면 Proof 강화\n"
        "- **경쟁사만 인용**: 해당 질문의 스포크 존재 확인 -> 없으면 스포크 작성, 있으면 콘텐츠 강화\n"
        "- **인용 텍스트 왜곡**: 오해 방지 문장 추가 + Answer-first 명확화\n\n"

        "### 90일 후 기대 상태\n\n"
        "- **KPI-A**: ChatGPT 인용 +150~200% (2~3배)\n"
        "- **KPI-B**: Google AI 주간 노출 80% 이상\n"
        "- **KPI-C**: 60개 스포크 + 허브 확장으로 500+ 하위 질의 커버\n"
        "- **기술**: robots/sitemap/구조화데이터 정책 명문화 + 자동 검증\n"
        "- **콘텐츠**: 77개 페이지가 Answer-first/Proof-first 기준 달성\n"
        "- **권위**: 리포트 1건 + 케이스 2건 + 기고 1건"
    ), 1, extension_md=(
        "### 스키마 조건부 적용 가이드\n\n"
        "- **세미나 페이지**: Event 스키마 (startDate + location 필수)\n"
        "- **인사이트 페이지**: Article 스키마 (author + datePublished 필수)\n"
        "- **스포크 FAQ**: FAQPage 스키마 (Question + acceptedAnswer 구조)\n"
        "- **모든 페이지**: Organization + BreadcrumbList 필수\n\n"
        "### AI Validator 자동화 스크립트 요구사항\n\n"
        "- 10개 프롬프트를 순차 실행\n"
        "- 결과를 구글 시트 API로 자동 기록\n"
        "- 인용 급감(-20%) 시 Slack 알림\n"
        "- 주간 종합 리포트 자동 생성"
    ))

    # -- M6-7 Quiz --
    s = add_step(m, "quiz", "구조화데이터 조건부 적용", (
        "다음 페이지 유형별로 올바른 구조화데이터 스키마 매핑은 무엇인가요?\n\n"
        "세미나 페이지 / 인사이트 페이지 / 스포크 FAQ 페이지"
    ), 2)
    add_option(s, "A", "모든 페이지에 Course 스키마를 동일하게 적용", 0,
               "현재 상태가 바로 이 문제입니다. 25개 페이지 모두 Course를 적용한 것이 "
               "구조화데이터 오용의 원인입니다. 페이지 유형별로 적합한 스키마를 구분해야 합니다.", 1)
    add_option(s, "B", "세미나 -> Event, 인사이트 -> Article, 스포크FAQ -> FAQPage", 1,
               "정답입니다! 세미나 페이지는 Event(startDate, location 필수), "
               "인사이트 페이지는 Article(author, datePublished 필수), "
               "스포크 FAQ 페이지는 FAQPage(Question+acceptedAnswer 구조)가 "
               "각각 올바른 스키마 매핑입니다.", 2)
    add_option(s, "C", "세미나 -> Article, 인사이트 -> Event, 스포크 -> Course", 0,
               "스키마 타입이 페이지 의도와 불일치합니다. 세미나는 시간/장소가 있는 이벤트이므로 Event, "
               "인사이트는 글 형태이므로 Article이 맞습니다.", 3)
    add_option(s, "D", "스키마를 모두 제거하고 Organization만 남김", 0,
               "Organization은 필수이지만, 추가 스키마(Event, Article, FAQPage)를 함께 적용해야 "
               "리치 리절트 노출 기회가 늘어납니다.", 4)

    # -- M6-7 Practice 1 --
    s = add_step(m, "practice", "AI Validator 인용 이상 대응", (
        "AI Validator 실행 결과, '기업 AI 교육 비용' 질문에서 경쟁사만 인용되고 "
        "b2b.fastcampus.co.kr은 노출되지 않았습니다. 가장 적절한 대응은 무엇인가요?"
    ), 3)
    add_option(s, "A", "경쟁사에 항의 메일을 보낸다", 0,
               "AI 검색 결과는 경쟁사가 통제하는 것이 아닙니다. 자사 콘텐츠를 강화하여 "
               "인용 경쟁력을 높이는 것이 올바른 대응입니다.", 1)
    add_option(s, "B", "해당 질문의 스포크 존재 확인 -> 없으면 작성, 있으면 콘텐츠 강화", 1,
               "정답입니다! 먼저 '기업 AI 교육 비용'에 대응하는 스포크 페이지가 있는지 확인합니다. "
               "없으면 즉시 스포크를 작성하고, 있으면 Answer-first와 Proof 블록을 강화하여 "
               "경쟁사보다 더 명확하고 신뢰할 수 있는 답변을 제공해야 합니다.", 2)
    add_option(s, "C", "해당 질문을 Top 50에서 제외한다", 0,
               "검색량이 높은 질문을 제외하면 커버리지가 줄어듭니다. "
               "오히려 이 질문에 대한 콘텐츠를 강화하여 인용을 확보해야 합니다.", 3)
    add_option(s, "D", "광고를 집행하여 해당 키워드에 노출시킨다", 0,
               "유료 광고는 AI 검색 인용과 별개입니다. AI 검색 엔진은 콘텐츠 품질과 "
               "출처 신뢰도를 기준으로 인용을 결정하므로 콘텐츠 강화가 정답입니다.", 4)

    # -- M6-7 Practice 2 --
    s = add_step(m, "practice", "외부 권위 우선순위", (
        "90일 내에 외부 권위 자산을 확보할 때, 실행 우선순위로 가장 적절한 것은 무엇인가요?"
    ), 4)
    add_option(s, "A", "기고 -> 리포트 -> 공동 케이스 (가장 쉬운 것부터)", 0,
               "실행 용이성보다 권위 신호 효과가 큰 순서로 진행해야 합니다. "
               "공동 케이스는 고객사 협력이 필요하지만 역링크와 신뢰도 효과가 가장 크므로 먼저 착수해야 합니다.", 1)
    add_option(s, "B", "공동 케이스 -> 리포트 -> 기고 순서", 1,
               "정답입니다! 고객사 공동 케이스(P2-10)는 역링크 + 제3자 신뢰도를 동시에 확보할 수 있어 "
               "가장 높은 ROI를 제공합니다. 오리지널 리포트(P2-9)는 브랜드 권위를 높이고, "
               "협회/미디어 기고(P2-11)는 장기적 역링크를 확보합니다.", 2)
    add_option(s, "C", "리포트만 집중하고 나머지는 생략", 0,
               "리포트만으로는 '다양한 출처 범위' 신호를 충분히 확보하기 어렵습니다. "
               "케이스, 리포트, 기고를 조합하여 다각적 권위를 구축해야 합니다.", 3)
    add_option(s, "D", "외부 권위 없이 내부 콘텐츠만 강화", 0,
               "내부 콘텐츠 강화는 Phase 1~2에서 이미 진행했습니다. Phase 3에서는 "
               "외부 제3자가 자사를 인용/링크하는 구조를 만들어야 AI 검색에서의 신뢰도가 올라갑니다.", 4)

    # ----------------------------------------------------------------
    # Module 6-8: 종합 평가 (Capstone)
    # ----------------------------------------------------------------
    m = add_module(6, "6-8: 종합 평가 (Capstone)",
                   "90일 전체 실행 계획을 통합 점검하고 다음 분기 우선순위를 확정합니다.", 8)

    # -- M6-8 Reading --
    add_step(m, "reading", "캡스톤 가이드: 90일 실행 통합 체크리스트", (
        "## 캡스톤 가이드: 90일 실행 통합 체크리스트\n\n"
        "### Stage 6 학습 경로 회고\n\n"
        '<div class="flow-chart">\n'
        '<div class="flow-title">Stage 6 학습 경로</div>\n'
        '<div class="flow-steps">\n'
        '<div class="flow-step"><div class="step-number">1</div><div class="step-content"><div class="step-title">M6-1 킥오프</div><div class="step-desc">RACI, KPI 베이스라인, 주간 리듬</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">2</div><div class="step-content"><div class="step-title">M6-2 기술 인프라</div><div class="step-desc">robots.txt, sitemap, 구조화데이터</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">3</div><div class="step-content"><div class="step-title">M6-3 Answer-first</div><div class="step-desc">상위 10 랜딩 콘텐츠 전환</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">4</div><div class="step-content"><div class="step-title">M6-4 Proof-first</div><div class="step-desc">통계/인용/출처 신뢰 강화</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">5</div><div class="step-content"><div class="step-title">M6-5 측정 체계</div><div class="step-desc">KPI, Top 50, 4주 실험 루프</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">6</div><div class="step-content"><div class="step-title">M6-6 허브-스포크</div><div class="step-desc">7허브, 60스포크 팬아웃 확장</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">7</div><div class="step-content"><div class="step-title">M6-7 권위 구축</div><div class="step-desc">AI Validator 자동화</div></div></div>\n'
        '<div class="flow-arrow">↓</div>\n'
        '<div class="flow-step"><div class="step-number">8</div><div class="step-content"><div class="step-title">M6-8 종합 평가</div><div class="step-desc">캡스톤 — 지금 여기</div></div></div>\n'
        '</div>\n'
        '</div>\n\n'

        "### 59개 티켓 체크리스트\n\n"
        "**Phase 1 (P0, 30일): 28 tickets**\n"
        "- [ ] P0-1~5: 기술 인프라 (robots.txt, sitemap, 구조화데이터, 추적)\n"
        "- [ ] P0-6~15: 상위 10 랜딩 Answer-first 적용\n"
        "- [ ] P0-16~25: 상위 10 랜딩 Proof-first 적용\n"
        "- [ ] P0-26~28: 측정 체계 (Top 50, 인용 로그, 추적 루틴)\n\n"
        "**Phase 2 (P1, 60일): 20 tickets**\n"
        "- [ ] P1-1~7: 허브 7개 구축\n"
        "- [ ] P1-8~10: 스포크 60개 발행 (3 Batches)\n"
        "- [ ] P1-11~15: 사례/리소스/세미나 표준화\n"
        "- [ ] P1-16~20: 내부링크 구축 + 구조화데이터 확장\n\n"
        "**Phase 3 (P2, 90일): 11 tickets**\n"
        "- [ ] P2-1~5: 구조화데이터 전사 적용\n"
        "- [ ] P2-6~8: 내부링크 그래프 재설계 + 외부 권위\n"
        "- [ ] P2-9~11: 오리지널 리포트 + 공동 케이스 + AI Validator 자동화\n\n"

        "### Phase별 완료 기준\n\n"
        "<div class='callout'>\n"
        "<strong>Phase 1 완료 기준</strong>:<br>\n"
        "- robots.txt + sitemap.xml 배포 완료<br>\n"
        "- 상위 10 랜딩 Answer-first/Proof-first 적용 완료<br>\n"
        "- Top 50 질문 세트 정의 + 주간 인용 로그 첫 2주 기록<br><br>\n"
        "<strong>Phase 2 완료 기준</strong>:<br>\n"
        "- 허브 7개 + 스포크 60개 1차 발행<br>\n"
        "- 사례/리소스 표준화 완료<br>\n"
        "- 허브-스포크 내부 링크 맵 완료<br><br>\n"
        "<strong>Phase 3 완료 기준</strong>:<br>\n"
        "- 구조화데이터 전사 적용 (Organization/BreadcrumbList 필수)<br>\n"
        "- 외부 권위 자산 발행 (리포트 1건 + 케이스 2건)<br>\n"
        "- AI Validator 자동화 루틴 정착\n"
        "</div>\n\n"

        "### 90일 후 기대 상태\n\n"
        "- **기술**: robots/sitemap/구조화데이터 정책 명문화 + 자동화 검증\n"
        "- **콘텐츠**: 77개 페이지가 Answer-first/Proof-first 기준 달성\n"
        "- **권위**: 연 1회 리포트 + 고객사 케이스 2건 + 미디어 기고 1건\n"
        "- **측정**: Top 50 질문 주간 추적 체계 정착 + 4주 실험 루프 운영 중\n\n"

        "### GEO 작업 요청 템플릿 (복붙 가능)\n\n"
        "<div class='code-example'>\n"
        "<pre><code>\n"
        "# GEO 작업 요청서\n"
        "- 작업명: [예: Answer-first 적용 - /service_custom]\n"
        "- 요청자: [이름]\n"
        "- 요청일: YYYY-MM-DD\n"
        "- 완료 기한: YYYY-MM-DD (최소 5일 여유)\n"
        "- 목표 KPI: KPI-A +20%, KPI-B 주간 3회, KPI-C 5개 하위질의 추가\n"
        "- 대상 URL: [URL 목록]\n"
        "- 요청 산출물: Answer-first 초안 / Proof 블록 / FAQ / 내부링크\n"
        "- DoD: 배포 + 출처 검증 + 5인 리뷰 + 스크린샷\n"
        "</code></pre>\n"
        "</div>"
    ), 1, extension_md=(
        "### 분기별 우선순위 (Q2 2026 이후)\n\n"
        "- **Q2**: 스포크 추가 발행 (총 150개 목표) + 외부 권위 자산 확대\n"
        "- **Q3**: 허브 추가 (총 12개) + Event/Article/FAQPage 정착\n"
        "- **Q4**: 국제 언어 확장 (영문/중문) 고려 + 연 2회 리포트\n\n"
        "### 최종 KPI 목표 (90일 후)\n\n"
        "- KPI-A (ChatGPT 인용): +150~200% (2~3배)\n"
        "- KPI-B (Google AI 노출): 주간 노출 130개 질문 중 80% 이상\n"
        "- KPI-C (하위 질의 커버리지): 500+ 하위 질의 커버"
    ))

    # -- M6-8 Quiz 1 --
    s = add_step(m, "quiz", "Phase 1 완료 기준 통합 판단", (
        "다음 중 Phase 1(30일) 완료 기준을 모두 충족한 상태는 무엇인가요?"
    ), 2)
    add_option(s, "A", "robots.txt만 배포하고 나머지는 진행 중", 0,
               "robots.txt 배포는 P0-1 하나의 티켓만 완료한 상태입니다. Phase 1 완료에는 "
               "Answer-first 10개 라이브 + 측정 체계 세팅까지 포함되어야 합니다.", 1)
    add_option(s, "B", "Answer-first 10개 라이브 + robots.txt 허용 + Top 50 베이스라인 수립", 1,
               "정답입니다! Phase 1의 3대 완료 기준은 (1) 상위 10 랜딩 Answer-first/Proof-first 적용, "
               "(2) 기술 인프라(robots.txt + sitemap) 배포, (3) 측정 체계(Top 50 질문 + 인용 로그) "
               "세팅입니다. 이 세 가지가 모두 갖추어져야 Phase 2로 진행할 수 있습니다.", 2)
    add_option(s, "C", "허브 7개만 구축하고 Answer-first는 미적용", 0,
               "허브 구축은 Phase 2(60일) 과업입니다. Phase 1에서는 상위 10 랜딩의 "
               "Answer-first/Proof-first 적용과 기술 인프라 정비가 완료되어야 합니다.", 3)
    add_option(s, "D", "AI Validator 자동화만 완료", 0,
               "AI Validator 자동화는 Phase 3(90일)의 P2-12 티켓입니다. "
               "Phase 1에서는 수동 측정 루틴(주 2회 화/금) 확립이 목표입니다.", 4)

    # -- M6-8 Quiz 2 --
    s = add_step(m, "quiz", "실패 상황 대응 전략", (
        "30일 후 KPI-A(ChatGPT 인용 빈도)가 전혀 개선되지 않았습니다. "
        "가장 적절한 대응 순서는 무엇인가요?"
    ), 3)
    add_option(s, "A", "전체 계획을 폐기하고 새로운 전략 수립", 0,
               "30일은 아직 Phase 1 단계이므로 전체 폐기는 과도한 대응입니다. "
               "먼저 기술 차단 여부를 확인하고, 콘텐츠 품질을 점검한 후 점진적으로 조정해야 합니다.", 1)
    add_option(s, "B", "기술 차단 확인 -> Answer-first 품질 점검 -> 실험 W1 분석", 1,
               "정답입니다! KPI-A 미개선 시 대응 순서는 (1) robots.txt에서 OAI-SearchBot이 "
               "차단되지 않았는지 기술 인프라 확인, (2) Answer-first 블록이 실제로 라이브인지 "
               "품질 점검, (3) 4주 실험 루프의 W1 데이터를 분석하여 원인을 진단하는 것입니다.", 2)
    add_option(s, "C", "예산을 늘려 외부 링크를 대량 구매", 0,
               "외부 링크 구매는 AI 검색 인용과 직접적 관련이 없습니다. "
               "온사이트 콘텐츠와 기술 인프라 점검이 먼저입니다.", 3)
    add_option(s, "D", "측정을 중단하고 3개월 후 재평가", 0,
               "측정 중단은 원인 데이터를 잃게 만듭니다. 오히려 측정 빈도를 높이고 "
               "기술/콘텐츠 원인을 빠르게 진단해야 합니다.", 4)

    # -- M6-8 Practice --
    s = add_step(m, "practice", "90일 로드맵 최종 구성", (
        "다음 중 Stage 6 최종 제출물로 '완료' 판정을 받을 가능성이 가장 높은 조합은 무엇인가요?"
    ), 4)
    add_option(s, "A", "아이디어 문서 1개와 회의록만 제출", 0,
               "아이디어와 회의록만으로는 실행 가능성을 판단하기 어렵습니다. "
               "일정, 담당, 지표가 연결된 운영 문서 세트가 필요합니다.", 1)
    add_option(s, "B", "RACI + Phase별 티켓(59개) + KPI 목표 + 실험 설계 + 주간 리듬 모두 포함", 1,
               "정답입니다! 90일 로드맵의 필수 구성 요소는 (1) RACI 역할 정의, "
               "(2) Phase별 59개 티켓과 담당자/마감일, (3) KPI-A/B/C 목표와 마일스톤, "
               "(4) 4주 실험 루프 설계, (5) 주간 운영 리듬입니다. "
               "축하합니다! 전체 6개 Stage를 모두 수료하셨습니다. "
               "이제 실제 90일 실행을 시작할 준비가 완료되었으며, "
               "다음 분기부터 바로 사용 가능한 수준의 GEO 운영 체계를 갖추셨습니다.", 2)
    add_option(s, "C", "디자인 시안과 랜딩 초안만 제출", 0,
               "디자인 산출물은 일부 과업만 다룹니다. 캡스톤은 운영 전체를 다루므로 "
               "RACI, 티켓, KPI, 실험 설계, 주간 리듬이 모두 포함되어야 합니다.", 3)
    add_option(s, "D", "성과 그래프만 제출하고 실행 계획 생략", 0,
               "성과 그래프만으로는 다음 실행을 보장할 수 없습니다. "
               "지표와 과업이 연결된 캘린더 및 책임 구조가 함께 제출되어야 합니다.", 4)

    distribution = _rebalance_quiz_answer_labels()
    _flush_option_buffer_to_db()
    conn.commit()
    conn.close()
    print(
        "Seed data upserted successfully. "
        f"Quiz answer labels: A={distribution['A']} B={distribution['B']} C={distribution['C']} D={distribution['D']}"
    )


if __name__ == "__main__":
    seed()
