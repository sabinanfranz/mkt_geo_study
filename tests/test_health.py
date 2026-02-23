"""Tests for GEO Mentor API endpoints."""

import sqlite3

from fastapi.testclient import TestClient

from apps.api.database import get_db, init_db
from apps.api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_minimal():
    """Insert minimal test data into the database."""
    conn = get_db()
    # Clear
    for table in ("user_bookmarks", "user_progress", "options", "steps", "modules", "stages"):
        conn.execute(f"DELETE FROM {table}")

    conn.execute(
        "INSERT INTO stages (id, title, description, order_idx, unlock_condition) "
        "VALUES (1, 'Stage 1', 'desc1', 1, NULL)"
    )
    conn.execute(
        "INSERT INTO stages (id, title, description, order_idx, unlock_condition) "
        'VALUES (2, \'Stage 2\', \'desc2\', 2, \'{"require_stage_complete": 1, "min_score_pct": 70}\')'
    )

    # Stage 1 modules
    conn.execute(
        "INSERT INTO modules (id, stage_id, title, description, order_idx) "
        "VALUES (1, 1, 'M1', 'mod1', 1)"
    )
    conn.execute(
        "INSERT INTO modules (id, stage_id, title, description, order_idx) "
        "VALUES (2, 1, 'M2 eval', 'mod2', 2)"
    )

    # Stage 2 module
    conn.execute(
        "INSERT INTO modules (id, stage_id, title, description, order_idx) "
        "VALUES (3, 2, 'M3', 'mod3', 1)"
    )

    # Steps for module 1 (reading + quiz)
    conn.execute(
        "INSERT INTO steps (id, module_id, type, title, content_md, order_idx) "
        "VALUES (1, 1, 'reading', 'Read1', 'content', 1)"
    )
    conn.execute(
        "INSERT INTO steps (id, module_id, type, title, content_md, order_idx) "
        "VALUES (2, 1, 'quiz', 'Quiz1', 'question?', 2)"
    )

    # Steps for module 2 (evaluation, quiz only)
    conn.execute(
        "INSERT INTO steps (id, module_id, type, title, content_md, order_idx) "
        "VALUES (3, 2, 'quiz', 'EvalQ1', 'eval q1?', 1)"
    )
    conn.execute(
        "INSERT INTO steps (id, module_id, type, title, content_md, order_idx) "
        "VALUES (4, 2, 'quiz', 'EvalQ2', 'eval q2?', 2)"
    )

    # Steps for module 3
    conn.execute(
        "INSERT INTO steps (id, module_id, type, title, content_md, order_idx) "
        "VALUES (5, 3, 'reading', 'Read2', 'content2', 1)"
    )

    # Options for quiz step 2
    conn.execute(
        "INSERT INTO options (id, step_id, label, content, is_correct, feedback_md, order_idx) "
        "VALUES (1, 2, 'A', '오답 선택지입니다', 0, '이 선택지는 올바르지 않습니다. 다른 선택지를 다시 한번 검토해 보세요.', 1)"
    )
    conn.execute(
        "INSERT INTO options (id, step_id, label, content, is_correct, feedback_md, order_idx) "
        "VALUES (2, 2, 'B', '정답 선택지입니다', 1, '정답입니다! 올바른 선택을 하셨습니다. 이 개념을 잘 이해하고 계십니다.', 2)"
    )

    # Options for eval step 3
    conn.execute(
        "INSERT INTO options (id, step_id, label, content, is_correct, feedback_md, order_idx) "
        "VALUES (3, 3, 'A', '오답 선택지입니다', 0, '이 선택지는 올바르지 않습니다. 다른 선택지를 다시 한번 검토해 보세요.', 1)"
    )
    conn.execute(
        "INSERT INTO options (id, step_id, label, content, is_correct, feedback_md, order_idx) "
        "VALUES (4, 3, 'B', '정답 선택지입니다', 1, '정답입니다! 올바른 선택을 하셨습니다. 이 개념을 잘 이해하고 계십니다.', 2)"
    )

    # Options for eval step 4
    conn.execute(
        "INSERT INTO options (id, step_id, label, content, is_correct, feedback_md, order_idx) "
        "VALUES (5, 4, 'A', '정답 선택지입니다', 1, '정답입니다! 올바른 선택을 하셨습니다. 이 개념을 잘 이해하고 계십니다.', 1)"
    )
    conn.execute(
        "INSERT INTO options (id, step_id, label, content, is_correct, feedback_md, order_idx) "
        "VALUES (6, 4, 'B', '오답 선택지입니다', 0, '이 선택지는 올바르지 않습니다. 다른 선택지를 다시 한번 검토해 보세요.', 2)"
    )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_returns_ok():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------


def test_list_stages():
    _seed_minimal()
    res = client.get("/api/stages")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[0]["is_unlocked"] is True
    assert data[1]["id"] == 2
    assert data[1]["is_unlocked"] is False  # Stage 2 locked by default


def test_list_stages_has_module_counts():
    _seed_minimal()
    res = client.get("/api/stages")
    data = res.json()
    assert data[0]["total_modules"] == 2
    assert data[0]["completed_modules"] == 0


# ---------------------------------------------------------------------------
# Modules
# ---------------------------------------------------------------------------


def test_list_modules():
    _seed_minimal()
    res = client.get("/api/stages/1/modules")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["title"] == "M1"


def test_list_modules_not_found():
    _seed_minimal()
    res = client.get("/api/stages/999/modules")
    assert res.status_code == 404


def test_get_module():
    _seed_minimal()
    res = client.get("/api/modules/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["total_steps"] == 2
    assert data["completed_steps"] == 0


def test_get_module_not_found():
    _seed_minimal()
    res = client.get("/api/modules/999")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


def test_list_steps():
    _seed_minimal()
    res = client.get("/api/modules/1/steps")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    # Reading step has no options
    assert data[0]["type"] == "reading"
    assert data[0]["options"] is None
    # Quiz step has options (without is_correct/feedback)
    assert data[1]["type"] == "quiz"
    assert data[1]["options"] is not None
    assert len(data[1]["options"]) == 2
    # Options should NOT contain is_correct or feedback_md
    opt_keys = set(data[1]["options"][0].keys())
    assert "is_correct" not in opt_keys
    assert "feedback_md" not in opt_keys


def test_list_steps_not_found():
    _seed_minimal()
    res = client.get("/api/modules/999/steps")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Answer submission
# ---------------------------------------------------------------------------


def test_answer_quiz_correct():
    _seed_minimal()
    res = client.post("/api/steps/2/answer", json={"selected_option_id": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True
    assert "정답입니다" in data["selected_feedback_md"]
    assert data["correct_option"]["id"] == 2


def test_answer_quiz_incorrect():
    _seed_minimal()
    res = client.post("/api/steps/2/answer", json={"selected_option_id": 1})
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is False
    assert "올바르지 않습니다" in data["selected_feedback_md"]
    assert data["correct_option"]["id"] == 2  # Still reveals correct option


def test_answer_reading_step():
    _seed_minimal()
    res = client.post("/api/steps/1/answer")
    assert res.status_code == 200
    data = res.json()
    assert data["completed"] is True


def test_answer_step_not_found():
    _seed_minimal()
    res = client.post("/api/steps/999/answer", json={"selected_option_id": 1})
    assert res.status_code == 404


def test_answer_option_not_found():
    _seed_minimal()
    res = client.post("/api/steps/2/answer", json={"selected_option_id": 999})
    assert res.status_code == 404


def test_answer_quiz_requires_option():
    _seed_minimal()
    res = client.post("/api/steps/2/answer", json={})
    assert res.status_code == 422


def test_answer_records_progress():
    _seed_minimal()
    # Submit answer
    client.post("/api/steps/2/answer", json={"selected_option_id": 2})
    # Check step is now completed
    res = client.get("/api/modules/1/steps")
    data = res.json()
    assert data[1]["is_completed"] is True


def test_answer_reading_records_progress():
    _seed_minimal()
    client.post("/api/steps/1/answer")
    res = client.get("/api/modules/1/steps")
    data = res.json()
    assert data[0]["is_completed"] is True


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------


def test_progress_initial():
    _seed_minimal()
    res = client.get("/api/progress")
    assert res.status_code == 200
    data = res.json()
    assert len(data["stages"]) == 2
    assert data["stages"][0]["completed_modules"] == 0
    assert data["stages"][0]["is_unlocked"] is True
    assert data["stages"][1]["is_unlocked"] is False


def test_progress_after_completing_module():
    _seed_minimal()
    # Complete all steps in module 1
    client.post("/api/steps/1/answer")
    client.post("/api/steps/2/answer", json={"selected_option_id": 2})

    res = client.get("/api/progress")
    data = res.json()
    assert data["stages"][0]["completed_modules"] == 1


# ---------------------------------------------------------------------------
# Evaluate
# ---------------------------------------------------------------------------


def test_evaluate_stage():
    _seed_minimal()
    # Answer both eval quiz steps correctly
    client.post("/api/steps/3/answer", json={"selected_option_id": 4})
    client.post("/api/steps/4/answer", json={"selected_option_id": 5})

    res = client.post("/api/stages/1/evaluate")
    assert res.status_code == 200
    data = res.json()
    assert data["score_pct"] == 100.0
    assert data["passed"] is True
    assert data["total_questions"] == 2
    assert data["correct_answers"] == 2
    assert data["unlocked_stage_id"] == 2


def test_evaluate_stage_fail():
    _seed_minimal()
    # Answer only one correctly, one wrong
    client.post("/api/steps/3/answer", json={"selected_option_id": 3})  # wrong
    client.post("/api/steps/4/answer", json={"selected_option_id": 5})  # correct

    res = client.post("/api/stages/1/evaluate")
    data = res.json()
    assert data["score_pct"] == 50.0
    assert data["passed"] is False


def test_evaluate_stage_not_found():
    _seed_minimal()
    res = client.post("/api/stages/999/evaluate")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Stage unlock logic
# ---------------------------------------------------------------------------


def test_stage_2_unlocks_after_passing():
    _seed_minimal()
    # Answer both eval quiz steps correctly (module 2 is last in stage 1)
    client.post("/api/steps/3/answer", json={"selected_option_id": 4})
    client.post("/api/steps/4/answer", json={"selected_option_id": 5})

    res = client.get("/api/stages")
    data = res.json()
    assert data[1]["is_unlocked"] is True


def test_stage_2_stays_locked_after_failing():
    _seed_minimal()
    # Answer both eval quiz steps wrong
    client.post("/api/steps/3/answer", json={"selected_option_id": 3})
    client.post("/api/steps/4/answer", json={"selected_option_id": 6})

    res = client.get("/api/stages")
    data = res.json()
    assert data[1]["is_unlocked"] is False


# ---------------------------------------------------------------------------
# Extension Mission (US-023)
# ---------------------------------------------------------------------------


def test_steps_include_extension_md():
    _seed_minimal()
    # Add extension to step 1
    conn = get_db()
    conn.execute(
        "UPDATE steps SET extension_md = '### 더 알아보기\n심화 내용입니다.' WHERE id = 1"
    )
    conn.commit()
    conn.close()

    res = client.get("/api/modules/1/steps")
    data = res.json()
    # Step 1 has extension
    assert data[0]["extension_md"] is not None
    assert "더 알아보기" in data[0]["extension_md"]
    # Step 2 has no extension
    assert data[1]["extension_md"] is None


# ---------------------------------------------------------------------------
# Admin Stats (US-024)
# ---------------------------------------------------------------------------


def test_admin_stats_empty_progress():
    """Stats with no user progress: all counters zero, no weakest modules."""
    _seed_minimal()
    res = client.get("/api/admin/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_steps"] == 5
    assert data["total_steps_completed"] == 0
    assert data["overall_accuracy_pct"] is None
    assert data["total_time_seconds"] == 0
    assert len(data["modules"]) == 3
    assert data["weakest_modules"] == []
    # Each module should have zero completed
    for m in data["modules"]:
        assert m["completed_steps"] == 0
        assert m["correct_answers"] == 0
        assert m["wrong_answers"] == 0


def test_admin_stats_with_progress():
    """Stats after answering some quiz steps."""
    _seed_minimal()
    # Complete reading step with time
    client.post("/api/steps/1/answer", json={"time_spent_seconds": 30})
    # Answer quiz correctly with time
    client.post("/api/steps/2/answer", json={"selected_option_id": 2, "time_spent_seconds": 20})
    # Answer eval quiz: one correct, one wrong
    client.post("/api/steps/3/answer", json={"selected_option_id": 4, "time_spent_seconds": 15})
    client.post("/api/steps/4/answer", json={"selected_option_id": 6, "time_spent_seconds": 10})

    res = client.get("/api/admin/stats")
    assert res.status_code == 200
    data = res.json()

    assert data["total_steps_completed"] == 4
    assert data["total_steps"] == 5
    assert data["total_time_seconds"] == 75

    # Overall accuracy: 3 rows with is_correct NOT NULL (steps 2,3,4), 2 correct
    assert data["overall_accuracy_pct"] == round((2 / 3) * 100, 1)

    # Module 1 stats: step 1 (reading, no accuracy), step 2 (quiz, correct)
    mod1 = next(m for m in data["modules"] if m["module_id"] == 1)
    assert mod1["completed_steps"] == 2
    assert mod1["correct_answers"] == 1
    assert mod1["wrong_answers"] == 0
    assert mod1["accuracy_pct"] == 100.0

    # Module 2 stats: step 3 correct, step 4 wrong
    mod2 = next(m for m in data["modules"] if m["module_id"] == 2)
    assert mod2["completed_steps"] == 2
    assert mod2["correct_answers"] == 1
    assert mod2["wrong_answers"] == 1
    assert mod2["accuracy_pct"] == 50.0

    # Module 3: no progress
    mod3 = next(m for m in data["modules"] if m["module_id"] == 3)
    assert mod3["completed_steps"] == 0
    assert mod3["accuracy_pct"] is None

    # Weakest modules: mod2 (50%) then mod1 (100%)
    assert len(data["weakest_modules"]) == 2
    assert data["weakest_modules"][0]["module_id"] == 2
    assert data["weakest_modules"][1]["module_id"] == 1


def test_admin_stats_avg_time():
    """Average time excludes zero-time entries."""
    _seed_minimal()
    # Answer with specific times
    client.post("/api/steps/3/answer", json={"selected_option_id": 4, "time_spent_seconds": 10})
    client.post("/api/steps/4/answer", json={"selected_option_id": 5, "time_spent_seconds": 20})

    res = client.get("/api/admin/stats")
    data = res.json()
    mod2 = next(m for m in data["modules"] if m["module_id"] == 2)
    assert mod2["avg_time_seconds"] == 15.0
