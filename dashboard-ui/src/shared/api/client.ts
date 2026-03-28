import type { Mission } from "../types/control";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "request failed");
  }
  return data as T;
}

export function listMissions() {
  return request<Mission[]>("/api/missions");
}

export function createMission(payload: {
  title: string;
  objective_text: string;
  context_text?: string;
  priority?: string;
}) {
  return request<{ mission: Mission }>("/api/missions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMission(missionId: string) {
  return request(`/api/missions/${missionId}`);
}

export function discussMission(missionId: string, payload: { content_text: string; run_analyst?: boolean }) {
  return request(`/api/missions/${missionId}/discuss`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function analyzeMission(missionId: string, payload?: { text?: string; trigger_message_id?: string }) {
  return request(`/api/missions/${missionId}/analyze`, {
    method: "POST",
    body: JSON.stringify(payload || {}),
  });
}

export function getOverview() {
  return request("/api/overview");
}

export function getTasks() {
  return request("/api/tasks?limit=20");
}

export function getTools() {
  return request("/api/tools?profile=steady");
}

export function launchRevision(
  revisionId: string,
  payload?: {
    launch_mode?: string;
    execution_profile?: string;
    selected_tools?: string[];
  },
) {
  return request(`/api/revisions/${revisionId}/launch`, {
    method: "POST",
    body: JSON.stringify(payload || {}),
  });
}

export function createPlanRevision(
  planId: string,
  payload: {
    change_summary: string;
    branch_key?: string;
    parent_revision_id?: string;
    launchable?: boolean;
    plan_outline?: Record<string, unknown>;
    task_tree?: unknown[];
  },
) {
  return request(`/api/plans/${planId}/revisions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function reviseMissionPlan(
  missionId: string,
  planId: string,
  payload: {
    change_summary: string;
    branch_key?: string;
    parent_revision_id?: string;
    launchable?: boolean;
    plan_outline?: Record<string, unknown>;
    task_tree?: unknown[];
  },
) {
  return request(`/api/missions/${missionId}/plans/${planId}/revise`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function branchRevision(
  revisionId: string,
  payload: {
    branch_key: string;
    change_summary?: string;
  },
) {
  return request(`/api/revisions/${revisionId}/branches`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listWorkflows() {
  return request("/api/workflows?limit=20");
}

export function getWorkflow(workflowId: string) {
  return request(`/api/workflows/${workflowId}`);
}

export function getArtifact(artifactId: string) {
  return request<{ artifact: any }>(`/api/artifacts/${artifactId}`);
}

export function listResearchSessions(limit = 20) {
  return request<any[]>(`/api/research/sessions?limit=${limit}`);
}

export function createResearchSession(payload: {
  mission_session_id: string;
  plan_revision_id?: string;
  workflow_id?: string;
  session_goal: string;
  scope_summary?: string;
  created_by?: string;
}) {
  return request<{ research_session: any }>("/api/research/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getResearchSession(sessionId: string) {
  return request<any>(`/api/research/sessions/${sessionId}`);
}

export function getResearchContext(sessionId: string) {
  return request<any>(`/api/research/sessions/${sessionId}/context`);
}

export function createResearchQuestion(
  sessionId: string,
  payload: {
    question_text: string;
    priority?: number;
    assigned_experts?: string[];
  },
) {
  return request<{ research_question: any }>(`/api/research/sessions/${sessionId}/questions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createResearchHypothesis(
  questionId: string,
  payload: {
    expert_role: string;
    title: string;
    summary?: string;
    assumptions?: string[];
    applicability_conditions?: string[];
    confidence_before?: number;
  },
) {
  return request<{ hypothesis: any }>(`/api/research/questions/${questionId}/hypotheses`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function reviewResearchHypothesis(
  hypothesisId: string,
  payload: {
    skeptic_review_status: string;
    skeptic_notes?: string[];
  },
) {
  return request<{ hypothesis: any }>(`/api/research/hypotheses/${hypothesisId}/review`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createResearchExperiment(
  hypothesisId: string,
  payload: {
    requested_by_role?: string;
    request_summary: string;
    required_observations?: string[];
    suggested_tasks?: any[];
    expected_artifacts?: string[];
    risk_level?: string;
    approval_mode?: string;
  },
) {
  return request<{ experiment_request: any }>(`/api/research/hypotheses/${hypothesisId}/experiments`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function approveResearchExperiment(experimentId: string, payload?: { approved_by?: string }) {
  return request<{ experiment_request: any }>(`/api/research/experiments/${experimentId}/approve`, {
    method: "POST",
    body: JSON.stringify(payload || {}),
  });
}

export function launchResearchExperiment(
  experimentId: string,
  payload?: { execution_profile?: string },
) {
  return request<{ experiment_request: any; experiment_result: any }>(`/api/research/experiments/${experimentId}/launch`, {
    method: "POST",
    body: JSON.stringify(payload || {}),
  });
}

export function createApprovalScope(
  missionId: string,
  payload: {
    scope_name: string;
    allowed_categories?: string[];
    allowed_tools?: string[];
    high_risk_tools?: string[];
    interactive_tools?: string[];
  },
) {
  return request(`/api/missions/${missionId}/approval-scopes`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createCampaign(payload: {
  mission_session_id: string;
  plan_revision_id: string;
  approval_scope_id: string;
  execution_profile?: string;
  auto_replan_enabled?: boolean;
  max_parallelism?: number;
}) {
  return request("/api/campaigns", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function controlCampaign(campaignId: string, action: string) {
  return request(`/api/campaigns/${campaignId}/control`, {
    method: "POST",
    body: JSON.stringify({ action }),
  });
}

export function getCampaignEvents(campaignId: string) {
  return request(`/api/campaigns/${campaignId}/events?limit=30`);
}

export function getCommandBoardInsights(missionId: string) {
  return request(`/api/command-board/${missionId}/insights`);
}

export function searchIntel(params?: { q?: string; capability?: string }) {
  const query = new URLSearchParams();
  if (params?.q) query.set("q", params.q);
  if (params?.capability) query.set("capability", params.capability);
  return request(`/api/intel/search?${query.toString()}`);
}

export function searchKnowledge(params?: { q?: string; capability?: string }) {
  const query = new URLSearchParams();
  if (params?.q) query.set("q", params.q);
  if (params?.capability) query.set("capability", params.capability);
  return request(`/api/knowledge/search?${query.toString()}`);
}
