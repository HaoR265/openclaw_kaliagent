CREATE TABLE IF NOT EXISTS mission_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    objective_text TEXT NOT NULL,
    context_text TEXT NOT NULL DEFAULT '',
    operator_notes TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    priority TEXT NOT NULL DEFAULT 'medium',
    created_by TEXT NOT NULL DEFAULT 'operator',
    latest_plan_id TEXT,
    latest_workflow_id TEXT,
    active_campaign_run_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mission_sessions_updated_at
ON mission_sessions(updated_at DESC);

CREATE TABLE IF NOT EXISTS discussion_messages (
    id TEXT PRIMARY KEY,
    mission_session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    author_type TEXT NOT NULL,
    author_id TEXT NOT NULL,
    content_text TEXT NOT NULL,
    summary_text TEXT NOT NULL DEFAULT '',
    message_kind TEXT NOT NULL DEFAULT 'input',
    token_in INTEGER,
    token_out INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(mission_session_id) REFERENCES mission_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_discussion_messages_mission_created
ON discussion_messages(mission_session_id, created_at ASC);

CREATE TABLE IF NOT EXISTS analysis_jobs (
    id TEXT PRIMARY KEY,
    mission_session_id TEXT NOT NULL,
    trigger_message_id TEXT,
    status TEXT NOT NULL DEFAULT 'queued',
    job_kind TEXT NOT NULL DEFAULT 'background_analysis',
    query_text TEXT NOT NULL,
    input_snapshot_json TEXT NOT NULL DEFAULT '{}',
    output_summary TEXT NOT NULL DEFAULT '',
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    warning_refs_json TEXT NOT NULL DEFAULT '[]',
    error_text TEXT NOT NULL DEFAULT '',
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(mission_session_id) REFERENCES mission_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(trigger_message_id) REFERENCES discussion_messages(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_mission_created
ON analysis_jobs(mission_session_id, created_at DESC);

CREATE TABLE IF NOT EXISTS plan_candidates (
    id TEXT PRIMARY KEY,
    mission_session_id TEXT NOT NULL,
    source_message_id TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    title TEXT NOT NULL,
    goal_summary TEXT NOT NULL DEFAULT '',
    discussion_summary TEXT NOT NULL DEFAULT '',
    assumptions_json TEXT NOT NULL DEFAULT '[]',
    warnings_json TEXT NOT NULL DEFAULT '[]',
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    preferred_branch_key TEXT NOT NULL DEFAULT 'main',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(mission_session_id) REFERENCES mission_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(source_message_id) REFERENCES discussion_messages(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_plan_candidates_mission_updated
ON plan_candidates(mission_session_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS plan_revisions (
    id TEXT PRIMARY KEY,
    plan_candidate_id TEXT NOT NULL,
    revision_no INTEGER NOT NULL,
    branch_key TEXT NOT NULL DEFAULT 'main',
    parent_revision_id TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    change_summary TEXT NOT NULL DEFAULT '',
    plan_outline_json TEXT NOT NULL DEFAULT '{}',
    task_tree_json TEXT NOT NULL DEFAULT '[]',
    launchable INTEGER NOT NULL DEFAULT 0,
    created_by TEXT NOT NULL DEFAULT 'commander',
    created_at TEXT NOT NULL,
    FOREIGN KEY(plan_candidate_id) REFERENCES plan_candidates(id) ON DELETE CASCADE,
    FOREIGN KEY(parent_revision_id) REFERENCES plan_revisions(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_plan_revisions_candidate_revision
ON plan_revisions(plan_candidate_id, revision_no, branch_key);

CREATE TABLE IF NOT EXISTS launch_batches (
    id TEXT PRIMARY KEY,
    mission_session_id TEXT NOT NULL,
    plan_revision_id TEXT NOT NULL,
    workflow_id TEXT,
    launch_mode TEXT NOT NULL,
    execution_profile TEXT NOT NULL DEFAULT 'steady',
    selected_tools_json TEXT NOT NULL DEFAULT '[]',
    task_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'created',
    created_at TEXT NOT NULL,
    FOREIGN KEY(mission_session_id) REFERENCES mission_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(plan_revision_id) REFERENCES plan_revisions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS approval_scopes (
    id TEXT PRIMARY KEY,
    mission_session_id TEXT NOT NULL,
    scope_name TEXT NOT NULL,
    allowed_categories_json TEXT NOT NULL DEFAULT '[]',
    allowed_tools_json TEXT NOT NULL DEFAULT '[]',
    interactive_tools_json TEXT NOT NULL DEFAULT '[]',
    high_risk_tools_json TEXT NOT NULL DEFAULT '[]',
    denied_tools_json TEXT NOT NULL DEFAULT '[]',
    network_scope_json TEXT NOT NULL DEFAULT '{}',
    confirmed_by TEXT NOT NULL,
    confirmed_at TEXT NOT NULL,
    expires_at TEXT,
    FOREIGN KEY(mission_session_id) REFERENCES mission_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS campaign_runs (
    id TEXT PRIMARY KEY,
    mission_session_id TEXT NOT NULL,
    plan_revision_id TEXT NOT NULL,
    approval_scope_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'created',
    objective_summary TEXT NOT NULL,
    scope_summary TEXT NOT NULL DEFAULT '',
    execution_profile TEXT NOT NULL DEFAULT 'steady',
    max_parallelism INTEGER NOT NULL DEFAULT 1,
    auto_replan_enabled INTEGER NOT NULL DEFAULT 1,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(mission_session_id) REFERENCES mission_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(plan_revision_id) REFERENCES plan_revisions(id) ON DELETE CASCADE,
    FOREIGN KEY(approval_scope_id) REFERENCES approval_scopes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_campaign_runs_mission_updated
ON campaign_runs(mission_session_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS campaign_events (
    id TEXT PRIMARY KEY,
    campaign_run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    message TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    related_task_id TEXT,
    related_attempt_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(campaign_run_id) REFERENCES campaign_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_campaign_events_run_created
ON campaign_events(campaign_run_id, created_at DESC);
