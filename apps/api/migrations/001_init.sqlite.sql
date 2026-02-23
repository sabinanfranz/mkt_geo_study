CREATE TABLE IF NOT EXISTS stages (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    order_idx INTEGER NOT NULL,
    unlock_condition TEXT
);

CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_id INTEGER NOT NULL REFERENCES stages(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    order_idx INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL REFERENCES modules(id),
    type TEXT NOT NULL CHECK(type IN ('reading', 'quiz', 'practice')),
    title TEXT NOT NULL,
    content_md TEXT NOT NULL,
    order_idx INTEGER NOT NULL,
    extension_md TEXT
);

CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL REFERENCES steps(id),
    label TEXT NOT NULL,
    content TEXT NOT NULL,
    is_correct INTEGER DEFAULT 0,
    feedback_md TEXT NOT NULL,
    order_idx INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    step_id INTEGER NOT NULL REFERENCES steps(id),
    selected_option_id INTEGER REFERENCES options(id),
    is_correct INTEGER,
    time_spent_seconds INTEGER DEFAULT 0,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, step_id)
);

CREATE TABLE IF NOT EXISTS user_bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    step_id INTEGER NOT NULL REFERENCES steps(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, step_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_modules_stage_order
    ON modules(stage_id, order_idx);

CREATE UNIQUE INDEX IF NOT EXISTS uq_steps_module_order
    ON steps(module_id, order_idx);

CREATE UNIQUE INDEX IF NOT EXISTS uq_options_step_order
    ON options(step_id, order_idx);

CREATE INDEX IF NOT EXISTS idx_modules_stage ON modules(stage_id);
CREATE INDEX IF NOT EXISTS idx_steps_module ON steps(module_id);
CREATE INDEX IF NOT EXISTS idx_options_step ON options(step_id);
CREATE INDEX IF NOT EXISTS idx_progress_user_step ON user_progress(user_id, step_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_created ON user_bookmarks(user_id, created_at DESC);
