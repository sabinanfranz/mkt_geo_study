"""Pydantic request/response models for the GEO Mentor API."""

from __future__ import annotations

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Stage
# ---------------------------------------------------------------------------

class StageResponse(BaseModel):
    id: int
    title: str
    description: str
    order_idx: int
    is_unlocked: bool
    completed_modules: int
    total_modules: int


# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------

class ModuleResponse(BaseModel):
    id: int
    stage_id: int
    title: str
    description: str
    order_idx: int
    completed_steps: int
    total_steps: int


# ---------------------------------------------------------------------------
# Step / Option
# ---------------------------------------------------------------------------

class OptionResponse(BaseModel):
    id: int
    label: str
    content: str


class StepResponse(BaseModel):
    id: int
    module_id: int
    type: str
    title: str
    content_md: str
    order_idx: int
    extension_md: str | None = None
    options: list[OptionResponse] | None = None
    is_completed: bool = False


# ---------------------------------------------------------------------------
# Answer
# ---------------------------------------------------------------------------

class AnswerRequest(BaseModel):
    selected_option_id: int | None = None
    time_spent_seconds: int | None = None


class OptionReveal(BaseModel):
    id: int
    label: str
    content: str
    feedback_md: str


class AnswerResponse(BaseModel):
    is_correct: bool
    selected_feedback_md: str
    correct_option: OptionReveal


class ReadingCompleteResponse(BaseModel):
    completed: bool


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

class StageProgress(BaseModel):
    stage_id: int
    title: str
    is_unlocked: bool
    completed_modules: int
    total_modules: int
    score_pct: float | None = None


class ProgressResponse(BaseModel):
    stages: list[StageProgress]


# ---------------------------------------------------------------------------
# Evaluate
# ---------------------------------------------------------------------------

class EvaluateResponse(BaseModel):
    score_pct: float
    passed: bool
    total_questions: int
    correct_answers: int
    unlocked_stage_id: int | None = None


# ---------------------------------------------------------------------------
# Bookmark
# ---------------------------------------------------------------------------

class BookmarkResponse(BaseModel):
    step_id: int
    step_title: str
    module_id: int
    module_title: str
    created_at: str | None = None


# ---------------------------------------------------------------------------
# Admin Stats
# ---------------------------------------------------------------------------

class ModuleStats(BaseModel):
    module_id: int
    module_title: str
    stage_id: int
    total_steps: int
    completed_steps: int
    correct_answers: int
    wrong_answers: int
    accuracy_pct: float | None
    avg_time_seconds: float | None


class AdminStatsResponse(BaseModel):
    total_steps_completed: int
    total_steps: int
    overall_accuracy_pct: float | None
    total_time_seconds: int
    modules: list[ModuleStats]
    weakest_modules: list[ModuleStats]
