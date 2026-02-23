"""FastAPI application — GEO Mentor API.

Serves the REST API and static frontend files.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from apps.api.database import get_db, init_db, is_truthy_env
from apps.api.models import (
    AdminStatsResponse,
    AnswerRequest,
    AnswerResponse,
    EvaluateResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MeResponse,
    ModuleResponse,
    ModuleStats,
    OptionResponse,
    OptionReveal,
    ProgressResponse,
    ReadingCompleteResponse,
    StageProgress,
    StageResponse,
    StepResponse,
)

# ---------------------------------------------------------------------------
# Lifespan — initialise DB on startup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa: ARG001
    init_db()
    if is_truthy_env("SEED_ON_START", default=False):
        from apps.api.seed import seed

        seed(run_migrations=False)
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

def _resolve_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
    if not raw or raw == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="GEO Mentor API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_resolve_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static files — serve apps/web/ at "/"
# ---------------------------------------------------------------------------

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALLOWED_USER_IDS = {f"b2b_mkt_{idx}" for idx in range(1, 11)}
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-session-secret-change-me")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "604800"))


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(payload_b64: str) -> str:
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _b64url_encode(signature)


def _create_access_token(user_id: str) -> str:
    payload = {
        "u": user_id,
        "exp": int(time.time()) + SESSION_TTL_SECONDS,
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    payload_b64 = _b64url_encode(payload_json)
    return f"{payload_b64}.{_sign(payload_b64)}"


def _decode_access_token(token: str) -> str:
    try:
        payload_b64, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    expected_signature = _sign(payload_b64)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token payload") from exc

    exp = payload.get("exp")
    user_id = payload.get("u")
    if not isinstance(exp, int) or exp < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expired")
    if user_id not in ALLOWED_USER_IDS:
        raise HTTPException(status_code=401, detail="Unknown user")
    return user_id


def get_current_user_id(
    authorization: str | None = Header(default=None),
) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    return _decode_access_token(token)


def _is_stage_unlocked(stage_row, conn, user_id: str) -> bool:
    """Check whether a stage is unlocked for the current user."""
    if stage_row["id"] == 1:
        return True
    if not stage_row["unlock_condition"]:
        return True

    condition = json.loads(stage_row["unlock_condition"])
    required_stage = condition.get("require_stage_complete")
    min_score = condition.get("min_score_pct", 70)

    if required_stage is None:
        return True

    # Find last module (highest order_idx) in the required stage
    last_module = conn.execute(
        "SELECT id FROM modules WHERE stage_id = ? ORDER BY order_idx DESC LIMIT 1",
        (required_stage,),
    ).fetchone()
    if not last_module:
        return False

    # Get quiz steps in that module
    quiz_steps = conn.execute(
        "SELECT id FROM steps WHERE module_id = ? AND type = 'quiz'",
        (last_module["id"],),
    ).fetchall()
    if not quiz_steps:
        return False

    quiz_step_ids = [s["id"] for s in quiz_steps]
    placeholders = ",".join("?" * len(quiz_step_ids))
    correct = conn.execute(
        f"SELECT COUNT(*) AS cnt FROM user_progress "
        f"WHERE user_id = ? AND step_id IN ({placeholders}) AND is_correct = 1",
        [user_id, *quiz_step_ids],
    ).fetchone()["cnt"]

    score_pct = (correct / len(quiz_step_ids)) * 100
    return score_pct >= min_score


def _module_completed_steps(module_id: int, conn, user_id: str) -> tuple[int, int]:
    """Return (completed_steps, total_steps) for a module."""
    total = conn.execute(
        "SELECT COUNT(*) AS cnt FROM steps WHERE module_id = ?",
        (module_id,),
    ).fetchone()["cnt"]

    completed = conn.execute(
        "SELECT COUNT(*) AS cnt FROM user_progress up "
        "JOIN steps s ON up.step_id = s.id "
        "WHERE s.module_id = ? AND up.user_id = ?",
        (module_id, user_id),
    ).fetchone()["cnt"]

    return completed, total


def _is_module_completed(module_id: int, conn, user_id: str) -> bool:
    completed, total = _module_completed_steps(module_id, conn, user_id)
    return total > 0 and completed >= total


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health_check():
    """Health-check endpoint."""
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    """Authenticate one of the fixed team accounts."""
    username = body.username.strip()
    password = body.password.strip()
    if username not in ALLOWED_USER_IDS or password != username:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = _create_access_token(username)
    return LoginResponse(access_token=token, user_id=username)


@app.get("/api/auth/me", response_model=MeResponse)
def me(user_id: str = Depends(get_current_user_id)):
    return MeResponse(user_id=user_id)


@app.post("/api/auth/logout", response_model=LogoutResponse)
def logout(_: str = Depends(get_current_user_id)):
    # Stateless token model; client removes token.
    return LogoutResponse(ok=True)


@app.get("/api/stages", response_model=list[StageResponse])
def list_stages(user_id: str = Depends(get_current_user_id)):
    """Return all stages with unlock status and progress."""
    conn = get_db()
    try:
        stages = conn.execute(
            "SELECT * FROM stages ORDER BY order_idx"
        ).fetchall()

        result: list[StageResponse] = []
        for s in stages:
            modules = conn.execute(
                "SELECT id FROM modules WHERE stage_id = ?", (s["id"],)
            ).fetchall()
            total_modules = len(modules)
            completed_modules = sum(
                1 for m in modules if _is_module_completed(m["id"], conn, user_id)
            )
            result.append(
                StageResponse(
                    id=s["id"],
                    title=s["title"],
                    description=s["description"],
                    order_idx=s["order_idx"],
                    is_unlocked=_is_stage_unlocked(s, conn, user_id),
                    completed_modules=completed_modules,
                    total_modules=total_modules,
                )
            )
        return result
    finally:
        conn.close()


@app.get("/api/stages/{stage_id}/modules", response_model=list[ModuleResponse])
def list_modules(stage_id: int, user_id: str = Depends(get_current_user_id)):
    """Return modules within a stage, with progress info."""
    conn = get_db()
    try:
        stage = conn.execute(
            "SELECT * FROM stages WHERE id = ?", (stage_id,)
        ).fetchone()
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")

        modules = conn.execute(
            "SELECT * FROM modules WHERE stage_id = ? ORDER BY order_idx",
            (stage_id,),
        ).fetchall()

        result: list[ModuleResponse] = []
        for m in modules:
            completed, total = _module_completed_steps(m["id"], conn, user_id)
            result.append(
                ModuleResponse(
                    id=m["id"],
                    stage_id=m["stage_id"],
                    title=m["title"],
                    description=m["description"],
                    order_idx=m["order_idx"],
                    completed_steps=completed,
                    total_steps=total,
                )
            )
        return result
    finally:
        conn.close()


@app.get("/api/modules/{module_id}", response_model=ModuleResponse)
def get_module(module_id: int, user_id: str = Depends(get_current_user_id)):
    """Return a single module with progress info."""
    conn = get_db()
    try:
        m = conn.execute(
            "SELECT * FROM modules WHERE id = ?", (module_id,)
        ).fetchone()
        if not m:
            raise HTTPException(status_code=404, detail="Module not found")

        completed, total = _module_completed_steps(m["id"], conn, user_id)
        return ModuleResponse(
            id=m["id"],
            stage_id=m["stage_id"],
            title=m["title"],
            description=m["description"],
            order_idx=m["order_idx"],
            completed_steps=completed,
            total_steps=total,
        )
    finally:
        conn.close()


@app.get(
    "/api/modules/{module_id}/steps", response_model=list[StepResponse]
)
def list_steps(module_id: int, user_id: str = Depends(get_current_user_id)):
    """Return steps within a module, with options (hiding is_correct/feedback)."""
    conn = get_db()
    try:
        m = conn.execute(
            "SELECT id FROM modules WHERE id = ?", (module_id,)
        ).fetchone()
        if not m:
            raise HTTPException(status_code=404, detail="Module not found")

        steps = conn.execute(
            "SELECT * FROM steps WHERE module_id = ? ORDER BY order_idx",
            (module_id,),
        ).fetchall()

        result: list[StepResponse] = []
        for s in steps:
            # Check completion
            progress = conn.execute(
                "SELECT id FROM user_progress WHERE user_id = ? AND step_id = ?",
                (user_id, s["id"]),
            ).fetchone()
            is_completed = progress is not None

            # Get options for quiz/practice steps
            options = None
            if s["type"] in ("quiz", "practice"):
                opt_rows = conn.execute(
                    "SELECT id, label, content FROM options "
                    "WHERE step_id = ? ORDER BY order_idx",
                    (s["id"],),
                ).fetchall()
                options = [
                    OptionResponse(
                        id=o["id"], label=o["label"], content=o["content"]
                    )
                    for o in opt_rows
                ]

            result.append(
                StepResponse(
                    id=s["id"],
                    module_id=s["module_id"],
                    type=s["type"],
                    title=s["title"],
                    content_md=s["content_md"],
                    order_idx=s["order_idx"],
                    extension_md=s["extension_md"],
                    options=options,
                    is_completed=is_completed,
                )
            )
        return result
    finally:
        conn.close()


@app.post("/api/steps/{step_id}/answer")
def submit_answer(
    step_id: int,
    body: AnswerRequest | None = None,
    user_id: str = Depends(get_current_user_id),
):
    """Submit an answer for a quiz/practice step, or mark a reading step as complete."""
    conn = get_db()
    try:
        step = conn.execute(
            "SELECT * FROM steps WHERE id = ?", (step_id,)
        ).fetchone()
        if not step:
            raise HTTPException(status_code=404, detail="Step not found")

        # ---- Reading step: just mark complete ----
        if step["type"] == "reading":
            time_spent = body.time_spent_seconds if body and body.time_spent_seconds else 0
            conn.execute(
                "INSERT INTO user_progress "
                "(user_id, step_id, selected_option_id, is_correct, time_spent_seconds) "
                "VALUES (?, ?, NULL, NULL, ?) "
                "ON CONFLICT(user_id, step_id) DO UPDATE SET "
                "selected_option_id = NULL, "
                "is_correct = NULL, "
                "time_spent_seconds = excluded.time_spent_seconds, "
                "completed_at = CURRENT_TIMESTAMP",
                (user_id, step_id, time_spent),
            )
            conn.commit()
            return JSONResponse(
                content={"completed": True},
                media_type="application/json; charset=utf-8",
            )

        # ---- Quiz / Practice: require an option ----
        if body is None or body.selected_option_id is None:
            raise HTTPException(
                status_code=422,
                detail="selected_option_id is required for quiz/practice steps",
            )

        selected = conn.execute(
            "SELECT * FROM options WHERE id = ? AND step_id = ?",
            (body.selected_option_id, step_id),
        ).fetchone()
        if not selected:
            raise HTTPException(
                status_code=404,
                detail="Option not found for this step",
            )

        is_correct = bool(selected["is_correct"])

        # UPSERT progress
        time_spent = body.time_spent_seconds if body.time_spent_seconds else 0
        conn.execute(
            "INSERT INTO user_progress "
            "(user_id, step_id, selected_option_id, is_correct, time_spent_seconds) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(user_id, step_id) DO UPDATE SET "
            "selected_option_id = excluded.selected_option_id, "
            "is_correct = excluded.is_correct, "
            "time_spent_seconds = excluded.time_spent_seconds, "
            "completed_at = CURRENT_TIMESTAMP",
            (user_id, step_id, body.selected_option_id, int(is_correct), time_spent),
        )
        conn.commit()

        # Find correct option
        correct_opt = conn.execute(
            "SELECT * FROM options WHERE step_id = ? AND is_correct = 1 LIMIT 1",
            (step_id,),
        ).fetchone()

        response = AnswerResponse(
            is_correct=is_correct,
            selected_feedback_md=selected["feedback_md"],
            correct_option=OptionReveal(
                id=correct_opt["id"],
                label=correct_opt["label"],
                content=correct_opt["content"],
                feedback_md=correct_opt["feedback_md"],
            ),
        )
        return JSONResponse(
            content=response.model_dump(),
            media_type="application/json; charset=utf-8",
        )
    finally:
        conn.close()


@app.get("/api/progress", response_model=ProgressResponse)
def get_progress(user_id: str = Depends(get_current_user_id)):
    """Return overall progress summary across all stages."""
    conn = get_db()
    try:
        stages = conn.execute(
            "SELECT * FROM stages ORDER BY order_idx"
        ).fetchall()

        stage_list: list[StageProgress] = []
        for s in stages:
            modules = conn.execute(
                "SELECT id FROM modules WHERE stage_id = ?", (s["id"],)
            ).fetchall()
            total_modules = len(modules)
            completed_modules = sum(
                1 for m in modules if _is_module_completed(m["id"], conn, user_id)
            )

            # Calculate score_pct from the evaluation module (last module)
            score_pct = None
            last_module = conn.execute(
                "SELECT id FROM modules WHERE stage_id = ? ORDER BY order_idx DESC LIMIT 1",
                (s["id"],),
            ).fetchone()
            if last_module:
                quiz_steps = conn.execute(
                    "SELECT id FROM steps WHERE module_id = ? AND type = 'quiz'",
                    (last_module["id"],),
                ).fetchall()
                if quiz_steps:
                    quiz_ids = [qs["id"] for qs in quiz_steps]
                    placeholders = ",".join("?" * len(quiz_ids))
                    answered = conn.execute(
                        f"SELECT COUNT(*) AS cnt FROM user_progress "
                        f"WHERE user_id = ? AND step_id IN ({placeholders})",
                        [user_id, *quiz_ids],
                    ).fetchone()["cnt"]
                    if answered > 0:
                        correct = conn.execute(
                            f"SELECT COUNT(*) AS cnt FROM user_progress "
                            f"WHERE user_id = ? AND step_id IN ({placeholders}) AND is_correct = 1",
                            [user_id, *quiz_ids],
                        ).fetchone()["cnt"]
                        score_pct = round((correct / len(quiz_ids)) * 100, 1)

            stage_list.append(
                StageProgress(
                    stage_id=s["id"],
                    title=s["title"],
                    is_unlocked=_is_stage_unlocked(s, conn, user_id),
                    completed_modules=completed_modules,
                    total_modules=total_modules,
                    score_pct=score_pct,
                )
            )

        return ProgressResponse(stages=stage_list)
    finally:
        conn.close()


@app.post("/api/stages/{stage_id}/evaluate", response_model=EvaluateResponse)
def evaluate_stage(stage_id: int, user_id: str = Depends(get_current_user_id)):
    """Calculate evaluation score for a stage's final module quiz steps."""
    conn = get_db()
    try:
        stage = conn.execute(
            "SELECT * FROM stages WHERE id = ?", (stage_id,)
        ).fetchone()
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")

        # Find the evaluation module (last module by order_idx)
        eval_module = conn.execute(
            "SELECT id FROM modules WHERE stage_id = ? ORDER BY order_idx DESC LIMIT 1",
            (stage_id,),
        ).fetchone()
        if not eval_module:
            raise HTTPException(
                status_code=404, detail="No modules found for this stage"
            )

        # Get quiz steps in the eval module
        quiz_steps = conn.execute(
            "SELECT id FROM steps WHERE module_id = ? AND type = 'quiz'",
            (eval_module["id"],),
        ).fetchall()
        total_questions = len(quiz_steps)
        if total_questions == 0:
            raise HTTPException(
                status_code=404,
                detail="No quiz steps in evaluation module",
            )

        quiz_ids = [qs["id"] for qs in quiz_steps]
        placeholders = ",".join("?" * len(quiz_ids))

        correct_answers = conn.execute(
            f"SELECT COUNT(*) AS cnt FROM user_progress "
            f"WHERE user_id = ? AND step_id IN ({placeholders}) AND is_correct = 1",
            [user_id, *quiz_ids],
        ).fetchone()["cnt"]

        score_pct = round((correct_answers / total_questions) * 100, 1)
        passed = score_pct >= 70

        # Check if next stage is unlocked
        unlocked_stage_id = None
        if passed:
            next_stage = conn.execute(
                "SELECT id FROM stages WHERE order_idx > ? ORDER BY order_idx LIMIT 1",
                (stage["order_idx"],),
            ).fetchone()
            if next_stage:
                unlocked_stage_id = next_stage["id"]

        return EvaluateResponse(
            score_pct=score_pct,
            passed=passed,
            total_questions=total_questions,
            correct_answers=correct_answers,
            unlocked_stage_id=unlocked_stage_id,
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Bookmarks
# ---------------------------------------------------------------------------


@app.post("/api/bookmarks/{step_id}")
def toggle_bookmark(step_id: int, user_id: str = Depends(get_current_user_id)):
    """Toggle bookmark on a step. Returns current bookmark state."""
    conn = get_db()
    try:
        step = conn.execute("SELECT id FROM steps WHERE id = ?", (step_id,)).fetchone()
        if not step:
            raise HTTPException(status_code=404, detail="Step not found")

        existing = conn.execute(
            "SELECT id FROM user_bookmarks WHERE user_id = ? AND step_id = ?",
            (user_id, step_id),
        ).fetchone()

        if existing:
            conn.execute("DELETE FROM user_bookmarks WHERE id = ?", (existing["id"],))
            conn.commit()
            return {"bookmarked": False, "step_id": step_id}
        else:
            conn.execute(
                "INSERT INTO user_bookmarks (user_id, step_id) VALUES (?, ?)",
                (user_id, step_id),
            )
            conn.commit()
            return {"bookmarked": True, "step_id": step_id}
    finally:
        conn.close()


@app.get("/api/bookmarks")
def list_bookmarks(user_id: str = Depends(get_current_user_id)):
    """Return all bookmarked steps for the current user."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT b.step_id, s.title AS step_title, s.module_id, "
            "m.title AS module_title, b.created_at "
            "FROM user_bookmarks b "
            "JOIN steps s ON b.step_id = s.id "
            "JOIN modules m ON s.module_id = m.id "
            "WHERE b.user_id = ? "
            "ORDER BY b.created_at DESC",
            (user_id,),
        ).fetchall()
        return [
            {
                "step_id": r["step_id"],
                "step_title": r["step_title"],
                "module_id": r["module_id"],
                "module_title": r["module_title"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Admin Stats
# ---------------------------------------------------------------------------


@app.get("/api/admin/stats", response_model=AdminStatsResponse)
def admin_stats(user_id: str = Depends(get_current_user_id)):
    """Return learning statistics for the admin dashboard."""
    conn = get_db()
    try:
        # 1. Total step count
        total_steps = conn.execute(
            "SELECT COUNT(*) AS cnt FROM steps"
        ).fetchone()["cnt"]

        # 2. Completed step count
        total_completed = conn.execute(
            "SELECT COUNT(*) AS cnt FROM user_progress WHERE user_id = ?",
            (user_id,),
        ).fetchone()["cnt"]

        # 3. Overall accuracy (quiz/practice only, where is_correct IS NOT NULL)
        quiz_progress = conn.execute(
            "SELECT COUNT(*) AS total, "
            "SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct "
            "FROM user_progress WHERE user_id = ? AND is_correct IS NOT NULL",
            (user_id,),
        ).fetchone()
        overall_accuracy = None
        if quiz_progress["total"] > 0:
            overall_accuracy = round(
                (quiz_progress["correct"] / quiz_progress["total"]) * 100, 1
            )

        # 4. Total learning time
        total_time = conn.execute(
            "SELECT COALESCE(SUM(time_spent_seconds), 0) AS total "
            "FROM user_progress WHERE user_id = ?",
            (user_id,),
        ).fetchone()["total"]

        # 5. Per-module statistics
        modules = conn.execute(
            "SELECT m.id, m.title, m.stage_id "
            "FROM modules m ORDER BY m.stage_id, m.order_idx"
        ).fetchall()

        module_stats_list: list[ModuleStats] = []
        for mod in modules:
            # Total steps in module
            mod_total = conn.execute(
                "SELECT COUNT(*) AS cnt FROM steps WHERE module_id = ?",
                (mod["id"],),
            ).fetchone()["cnt"]

            # Completed steps in module
            mod_completed = conn.execute(
                "SELECT COUNT(*) AS cnt FROM user_progress up "
                "JOIN steps s ON up.step_id = s.id "
                "WHERE s.module_id = ? AND up.user_id = ?",
                (mod["id"], user_id),
            ).fetchone()["cnt"]

            # Quiz/practice accuracy in module
            mod_quiz = conn.execute(
                "SELECT COUNT(*) AS total, "
                "SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) AS correct, "
                "SUM(CASE WHEN up.is_correct = 0 THEN 1 ELSE 0 END) AS wrong "
                "FROM user_progress up "
                "JOIN steps s ON up.step_id = s.id "
                "WHERE s.module_id = ? AND up.user_id = ? AND up.is_correct IS NOT NULL",
                (mod["id"], user_id),
            ).fetchone()

            accuracy = None
            correct = mod_quiz["correct"] or 0
            wrong = mod_quiz["wrong"] or 0
            if mod_quiz["total"] > 0:
                accuracy = round((correct / mod_quiz["total"]) * 100, 1)

            # Average time per step in module
            avg_time_row = conn.execute(
                "SELECT AVG(up.time_spent_seconds) AS avg_time "
                "FROM user_progress up "
                "JOIN steps s ON up.step_id = s.id "
                "WHERE s.module_id = ? AND up.user_id = ? AND up.time_spent_seconds > 0",
                (mod["id"], user_id),
            ).fetchone()
            avg_time = (
                round(avg_time_row["avg_time"], 1)
                if avg_time_row["avg_time"]
                else None
            )

            ms = ModuleStats(
                module_id=mod["id"],
                module_title=mod["title"],
                stage_id=mod["stage_id"],
                total_steps=mod_total,
                completed_steps=mod_completed,
                correct_answers=correct,
                wrong_answers=wrong,
                accuracy_pct=accuracy,
                avg_time_seconds=avg_time,
            )
            module_stats_list.append(ms)

        # 6. Weakest modules (lowest accuracy among those with scores, top 3)
        scored = [m for m in module_stats_list if m.accuracy_pct is not None]
        weakest = sorted(scored, key=lambda x: x.accuracy_pct)[:3]

        return AdminStatsResponse(
            total_steps_completed=total_completed,
            total_steps=total_steps,
            overall_accuracy_pct=overall_accuracy,
            total_time_seconds=total_time,
            modules=module_stats_list,
            weakest_modules=weakest,
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Catch-all: serve static frontend files
# ---------------------------------------------------------------------------

if WEB_DIR.exists() and (WEB_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(WEB_DIR / "css")), name="css")
if WEB_DIR.exists() and (WEB_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(WEB_DIR / "js")), name="js")


@app.get("/")
def serve_index():
    """Serve the frontend index.html."""
    index = WEB_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index))
