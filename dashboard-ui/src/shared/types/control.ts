export type Mission = {
  id: string;
  title: string;
  objective_text: string;
  status: string;
  priority: string;
  latest_plan_id?: string | null;
  latest_workflow_id?: string | null;
  active_campaign_run_id?: string | null;
  created_at: string;
  updated_at: string;
};

export type DiscussionMessage = {
  id: string;
  role: string;
  author_type: string;
  author_id: string;
  content_text: string;
  summary_text: string;
  message_kind: string;
  created_at: string;
};

export type AnalysisJob = {
  id: string;
  status: string;
  job_kind: string;
  query_text: string;
  output_summary: string;
  evidence_refs_json: string[] | unknown[];
  warning_refs_json: string[] | unknown[];
  created_at: string;
};

export type PlanCandidate = {
  id: string;
  status: string;
  title: string;
  goal_summary: string;
  discussion_summary: string;
};
