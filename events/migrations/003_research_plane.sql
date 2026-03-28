CREATE TABLE IF NOT EXISTS research_sessions (
    id TEXT PRIMARY KEY,
    mission_session_id TEXT NOT NULL,
    plan_revision_id TEXT,
    workflow_id TEXT,
    session_goal TEXT NOT NULL DEFAULT '',
    scope_summary TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    created_by TEXT NOT NULL DEFAULT 'operator',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(mission_session_id) REFERENCES mission_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(plan_revision_id) REFERENCES plan_revisions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_research_sessions_mission_updated
ON research_sessions(mission_session_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS research_questions (
    id TEXT PRIMARY KEY,
    research_session_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 50,
    assigned_experts_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL,
    FOREIGN KEY(research_session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_research_questions_session_created
ON research_questions(research_session_id, created_at ASC);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    research_question_id TEXT NOT NULL,
    expert_role TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    assumptions_json TEXT NOT NULL DEFAULT '[]',
    applicability_conditions_json TEXT NOT NULL DEFAULT '[]',
    confidence_before REAL NOT NULL DEFAULT 0.5,
    skeptic_review_status TEXT NOT NULL DEFAULT 'pending',
    skeptic_notes_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(research_question_id) REFERENCES research_questions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hypotheses_question_created
ON hypotheses(research_question_id, created_at DESC);

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    research_session_id TEXT NOT NULL,
    finding_type TEXT NOT NULL DEFAULT 'observation',
    summary TEXT NOT NULL,
    confidence_level TEXT NOT NULL DEFAULT 'medium',
    validated_status TEXT NOT NULL DEFAULT 'draft',
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    FOREIGN KEY(research_session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiment_requests (
    id TEXT PRIMARY KEY,
    research_session_id TEXT NOT NULL,
    hypothesis_id TEXT NOT NULL,
    requested_by_role TEXT NOT NULL,
    request_summary TEXT NOT NULL,
    required_observations_json TEXT NOT NULL DEFAULT '[]',
    suggested_tasks_json TEXT NOT NULL DEFAULT '[]',
    expected_artifacts_json TEXT NOT NULL DEFAULT '[]',
    risk_level TEXT NOT NULL DEFAULT 'medium',
    approval_mode TEXT NOT NULL DEFAULT 'commander_review',
    status TEXT NOT NULL DEFAULT 'pending_review',
    approved_by TEXT,
    approved_at TEXT,
    workflow_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(research_session_id) REFERENCES research_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_experiment_requests_session_created
ON experiment_requests(research_session_id, created_at DESC);

CREATE TABLE IF NOT EXISTS experiment_results (
    id TEXT PRIMARY KEY,
    experiment_request_id TEXT NOT NULL UNIQUE,
    workflow_id TEXT,
    task_ids_json TEXT NOT NULL DEFAULT '[]',
    result_summary TEXT NOT NULL DEFAULT '',
    structured_observations_json TEXT NOT NULL DEFAULT '{}',
    artifact_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence_delta REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(experiment_request_id) REFERENCES experiment_requests(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_packages (
    id TEXT PRIMARY KEY,
    research_session_id TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    hypotheses_json TEXT NOT NULL DEFAULT '[]',
    options_json TEXT NOT NULL DEFAULT '[]',
    warnings_json TEXT NOT NULL DEFAULT '[]',
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    proposed_revision_json TEXT NOT NULL DEFAULT '{}',
    proposed_experiments_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(research_session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_analysis_packages_session_updated
ON analysis_packages(research_session_id, updated_at DESC);
