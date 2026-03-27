CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    workflow_id TEXT,
    parent_task_id TEXT,
    correlation_id TEXT NOT NULL,
    capability TEXT NOT NULL,
    operation TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    target_agent TEXT,
    state TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 50,
    payload_json TEXT NOT NULL,
    policy_ref TEXT,
    idempotency_key TEXT,
    schedule_at TEXT,
    lease_owner TEXT,
    lease_expires_at TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    timeout_seconds INTEGER,
    last_error_code TEXT,
    last_error_message TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_state_priority_created
ON tasks(state, priority DESC, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_tasks_capability_state
ON tasks(capability, state);

CREATE TABLE IF NOT EXISTS task_attempts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    worker_id TEXT NOT NULL,
    executor_type TEXT NOT NULL,
    tool_name TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    outcome TEXT NOT NULL,
    exit_code INTEGER,
    error_code TEXT,
    error_message TEXT,
    raw_output_ref TEXT,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    dependency_type TEXT NOT NULL,
    PRIMARY KEY(task_id, depends_on_task_id),
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS results (
    task_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    structured_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    path TEXT NOT NULL,
    mime_type TEXT,
    size_bytes INTEGER,
    sha256 TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    hostname TEXT,
    pid INTEGER,
    last_heartbeat_at TEXT,
    status TEXT NOT NULL
);

