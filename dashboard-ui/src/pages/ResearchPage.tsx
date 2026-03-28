import { useEffect, useMemo, useState } from "react";
import { RecordCard } from "../components/RecordCard";
import { SummaryGroup } from "../components/SummaryGroup";
import {
  approveResearchExperiment,
  createResearchExperiment,
  createResearchHypothesis,
  createResearchQuestion,
  createResearchSession,
  getMission,
  getResearchContext,
  getResearchSession,
  launchResearchExperiment,
  listMissions,
  listResearchSessions,
  reviewResearchHypothesis,
} from "../shared/api/client";
import type { Mission } from "../shared/types/control";
import { formatCompactId, formatFallback, formatStateLabel, formatTimestamp, getStatusChipToneClass } from "../shared/ui/present";

function splitLines(value: string): string[] {
  return value
    .split(/\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function replaceQueryParam(key: string, value: string) {
  const url = new URL(window.location.href);
  if (value) {
    url.searchParams.set(key, value);
  } else {
    url.searchParams.delete(key);
  }
  window.history.replaceState({}, "", `${url.pathname}${url.search}`);
}

export function ResearchPage() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [selectedSession, setSelectedSession] = useState(
    () => new URLSearchParams(window.location.search).get("session") || localStorage.getItem("research:selectedSession") || "",
  );
  const [selectedMissionId, setSelectedMissionId] = useState(
    () => new URLSearchParams(window.location.search).get("mission") || localStorage.getItem("research:selectedMission") || "",
  );
  const [missionDetail, setMissionDetail] = useState<any>(null);
  const [detail, setDetail] = useState<any>(null);
  const [context, setContext] = useState<any>(null);
  const [busyAction, setBusyAction] = useState("");
  const [errorText, setErrorText] = useState("");
  const [noticeText, setNoticeText] = useState("");

  const [sessionGoal, setSessionGoal] = useState("");
  const [scopeSummary, setScopeSummary] = useState("");
  const [selectedRevisionId, setSelectedRevisionId] = useState("");

  const [questionText, setQuestionText] = useState("");
  const [questionPriority, setQuestionPriority] = useState("50");
  const [assignedExpertsText, setAssignedExpertsText] = useState("research-lead\nwireless-protocol\nskeptic");
  const [selectedQuestionId, setSelectedQuestionId] = useState("");

  const [hypothesisTitle, setHypothesisTitle] = useState("");
  const [hypothesisSummary, setHypothesisSummary] = useState("");
  const [expertRole, setExpertRole] = useState("wireless-protocol");
  const [assumptionsText, setAssumptionsText] = useState("");
  const [conditionsText, setConditionsText] = useState("");
  const [confidenceBefore, setConfidenceBefore] = useState("0.5");
  const [selectedHypothesisId, setSelectedHypothesisId] = useState("");
  const [reviewStatus, setReviewStatus] = useState("reviewed");
  const [reviewNotesText, setReviewNotesText] = useState("");

  const [requestSummary, setRequestSummary] = useState("");
  const [requiredObservationsText, setRequiredObservationsText] = useState("");
  const [expectedArtifactsText, setExpectedArtifactsText] = useState("pcap\nhandshake transcript\nbeacon fingerprint");
  const [experimentCapability, setExperimentCapability] = useState("wireless");
  const [experimentTask, setExperimentTask] = useState("");
  const [experimentNotes, setExperimentNotes] = useState("");
  const [riskLevel, setRiskLevel] = useState("medium");
  const [approvalMode, setApprovalMode] = useState("commander_review");
  const [interactiveTask, setInteractiveTask] = useState(false);
  const [secondaryConfirmation, setSecondaryConfirmation] = useState(true);
  const [launchProfile, setLaunchProfile] = useState("steady");

  const questions = detail?.questions || [];
  const hypotheses = detail?.hypotheses || [];
  const experiments = detail?.experiments || [];
  const experimentResults = detail?.experiment_results || [];
  const analysisPackages = detail?.analysis_packages || [];

  const selectedQuestion = questions.find((item: any) => item.id === selectedQuestionId) || null;
  const selectedHypothesis = hypotheses.find((item: any) => item.id === selectedHypothesisId) || null;
  const resultByExperimentId = useMemo(
    () =>
      new Map(
        experimentResults.map((item: any) => [item.experiment_request_id, item]),
      ),
    [experimentResults],
  );

  async function refreshSessions(preferredId?: string) {
    const items = await listResearchSessions();
    setSessions(items);
    const targetId = preferredId || selectedSession;
    if (targetId && items.some((item: any) => item.id === targetId)) {
      if (targetId !== selectedSession) {
        setSelectedSession(targetId);
      }
      return;
    }
    if (items[0]?.id) {
      setSelectedSession(items[0].id);
    } else if (selectedSession) {
      setSelectedSession("");
    }
  }

  async function refreshSelectedSession(sessionId = selectedSession) {
    if (!sessionId) {
      setDetail(null);
      setContext(null);
      return;
    }
    const [sessionDetail, sessionContext] = await Promise.all([
      getResearchSession(sessionId),
      getResearchContext(sessionId),
    ]);
    setDetail(sessionDetail);
    setContext(sessionContext);
  }

  async function withAction(label: string, action: () => Promise<void>) {
    setBusyAction(label);
    setErrorText("");
    setNoticeText("");
    try {
      await action();
    } catch (error: any) {
      setErrorText(error?.message || "request failed");
    } finally {
      setBusyAction("");
    }
  }

  useEffect(() => {
    Promise.all([listMissions(), listResearchSessions()])
      .then(([missionItems, sessionItems]) => {
        setMissions(missionItems);
        setSessions(sessionItems);
        if (!selectedMissionId && missionItems[0]?.id) {
          setSelectedMissionId(missionItems[0].id);
        } else if (selectedMissionId && !missionItems.some((item) => item.id === selectedMissionId) && missionItems[0]?.id) {
          setSelectedMissionId(missionItems[0].id);
        }
        if (!selectedSession && sessionItems[0]?.id) {
          setSelectedSession(sessionItems[0].id);
        } else if (
          selectedSession &&
          !sessionItems.some((item: any) => item.id === selectedSession) &&
          sessionItems[0]?.id
        ) {
          setSelectedSession(sessionItems[0].id);
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedMissionId) {
      setMissionDetail(null);
      return;
    }
    getMission(selectedMissionId)
      .then((payload: any) => {
        setMissionDetail(payload);
        if (!selectedRevisionId && payload.revisions?.[0]?.id) {
          setSelectedRevisionId(payload.revisions[0].id);
        } else if (
          selectedRevisionId &&
          !payload.revisions?.some((revision: any) => revision.id === selectedRevisionId)
        ) {
          setSelectedRevisionId(payload.revisions?.[0]?.id || "");
        }
      })
      .catch(console.error);
  }, [selectedMissionId]);

  useEffect(() => {
    if (!selectedSession) {
      setDetail(null);
      setContext(null);
      return;
    }
    refreshSelectedSession(selectedSession).catch(console.error);
  }, [selectedSession]);

  useEffect(() => {
    if (selectedSession) {
      localStorage.setItem("research:selectedSession", selectedSession);
      replaceQueryParam("session", selectedSession);
    }
  }, [selectedSession]);

  useEffect(() => {
    if (selectedMissionId) {
      localStorage.setItem("research:selectedMission", selectedMissionId);
      replaceQueryParam("mission", selectedMissionId);
    }
  }, [selectedMissionId]);

  useEffect(() => {
    if (!selectedQuestionId && questions[0]?.id) {
      setSelectedQuestionId(questions[0].id);
      return;
    }
    if (selectedQuestionId && !questions.some((item: any) => item.id === selectedQuestionId)) {
      setSelectedQuestionId(questions[0]?.id || "");
    }
  }, [questions, selectedQuestionId]);

  useEffect(() => {
    if (!selectedHypothesisId && hypotheses[0]?.id) {
      setSelectedHypothesisId(hypotheses[0].id);
      return;
    }
    if (selectedHypothesisId && !hypotheses.some((item: any) => item.id === selectedHypothesisId)) {
      setSelectedHypothesisId(hypotheses[0]?.id || "");
    }
  }, [hypotheses, selectedHypothesisId]);

  useEffect(() => {
    const capabilities = context?.capabilities || [];
    if (capabilities.length && !capabilities.includes(experimentCapability)) {
      setExperimentCapability(capabilities[0]);
    }
  }, [context, experimentCapability]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      refreshSessions().catch(() => undefined);
      if (selectedSession) {
        refreshSelectedSession(selectedSession).catch(() => undefined);
      }
    }, 20000);
    return () => window.clearInterval(timer);
  }, [selectedSession]);

  const sessionStats = [
    `sessions ${sessions.length}`,
    `questions ${questions.length}`,
    `hypotheses ${hypotheses.length}`,
    `experiments ${experiments.length}`,
    `results ${experimentResults.length}`,
  ];

  return (
    <div className="page-grid">
      <section className="panel span-2">
        <div className="panel-title">Research Studio</div>
        <div className="detail-text">
          这页先收最小研究闭环：建立 research session，拆 question，产 hypothesis，生成 experiment request，然后交给控制面 approve / launch。
        </div>
        <div className="stats-strip top-gap">
          {sessionStats.map((chip) => (
            <div key={chip} className={`status-chip ${getStatusChipToneClass(chip)}`.trim()}>
              {chip}
            </div>
          ))}
        </div>
        {errorText ? <div className="empty-state top-gap">错误：{errorText}</div> : null}
        {noticeText ? <div className="empty-state top-gap">完成：{noticeText}</div> : null}
      </section>

      <section className="panel">
        <div className="panel-title">New Session</div>
        <div className="stack">
          <select className="input" value={selectedMissionId} onChange={(e) => setSelectedMissionId(e.target.value)}>
            <option value="">选择 mission</option>
            {missions.map((mission) => (
              <option key={mission.id} value={mission.id}>
                {mission.title}
              </option>
            ))}
          </select>
          <select className="input" value={selectedRevisionId} onChange={(e) => setSelectedRevisionId(e.target.value)}>
            <option value="">latest / none</option>
            {(missionDetail?.revisions || []).map((revision: any) => (
              <option key={revision.id} value={revision.id}>
                {revision.branch_key || "main"} / {formatCompactId(revision.id)}
              </option>
            ))}
          </select>
          <textarea
            className="textarea"
            rows={3}
            value={sessionGoal}
            onChange={(e) => setSessionGoal(e.target.value)}
            placeholder="本轮研究目标"
          />
          <textarea
            className="textarea"
            rows={3}
            value={scopeSummary}
            onChange={(e) => setScopeSummary(e.target.value)}
            placeholder="边界、假设、风险说明"
          />
          <div className="button-row">
            <button
              type="button"
              className="button primary"
              disabled={!selectedMissionId || !sessionGoal.trim() || !!busyAction}
              onClick={() =>
                withAction("create-session", async () => {
                  const payload = await createResearchSession({
                    mission_session_id: selectedMissionId,
                    plan_revision_id: selectedRevisionId || undefined,
                    session_goal: sessionGoal.trim(),
                    scope_summary: scopeSummary.trim(),
                    created_by: "research-lead",
                  });
                  const nextId = payload.research_session.id;
                  setSessionGoal("");
                  setScopeSummary("");
                  setSelectedSession(nextId);
                  await refreshSessions(nextId);
                  await refreshSelectedSession(nextId);
                  setNoticeText("research session 已创建");
                })
              }
            >
              {busyAction === "create-session" ? "Creating..." : "Create Session"}
            </button>
            {missionDetail?.mission?.latest_workflow_id ? (
              <a className="button" href={`/execution?workflow=${missionDetail.mission.latest_workflow_id}`}>
                Open Latest Workflow
              </a>
            ) : null}
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-title">Sessions</div>
        <div className="stack">
          {sessions.length ? (
            sessions.map((session: any) => (
              <button
                key={session.id}
                type="button"
                className={`list-card${selectedSession === session.id ? " active" : ""}`}
                onClick={() => setSelectedSession(session.id)}
              >
                <div className="list-title">{session.mission_title}</div>
                <div className="list-sub">{formatCompactId(session.id)}</div>
                <div className="list-sub">
                  {formatStateLabel(session.status)} / q {session.question_count} / exp {session.experiment_count}
                </div>
                <div className="detail-text">{formatFallback(session.session_goal, "no goal")}</div>
              </button>
            ))
          ) : (
            <div className="empty-state">暂无 research session。</div>
          )}
        </div>
      </section>

      <section className="panel span-2">
        <div className="panel-title">Context</div>
        {!detail || !context ? (
          <div className="empty-state">选择一个 research session。</div>
        ) : (
          <div className="dual">
            <SummaryGroup
              title={context.research_session.session_goal || "Untitled research session"}
              lines={[
                `${context.mission?.title || detail.research_session.mission_title} / ${formatStateLabel(context.research_session.status)}`,
                formatFallback(context.research_session.scope_summary, "no scope summary"),
                `created ${formatTimestamp(context.research_session.created_at)}`,
              ]}
              tags={[
                `mission ${formatCompactId(context.research_session.mission_session_id)}`,
                context.research_session.plan_revision_id ? `revision ${formatCompactId(context.research_session.plan_revision_id)}` : "",
                context.research_session.workflow_id ? `workflow ${formatCompactId(context.research_session.workflow_id)}` : "",
              ]}
            />
            <SummaryGroup
              title="Context Snapshot"
              lines={[
                formatFallback(context.mission?.objective_text, "no objective"),
                `capabilities ${context.capabilities?.join(", ") || "none"}`,
                `counts q ${context.question_count} / hyp ${context.hypothesis_count} / exp ${context.experiment_count}`,
              ]}
              tags={[
                context.selected_revision?.branch_key || "",
                context.workflow?.launch_mode || "",
                context.workflow?.execution_profile || "",
              ]}
            />
            <div className="button-row">
              <a className="button" href={`/?mission=${context.research_session.mission_session_id}`}>
                Open Mission
              </a>
              {context.research_session.plan_revision_id ? (
                <a
                  className="button"
                  href={`/?mission=${context.research_session.mission_session_id}&revision=${context.research_session.plan_revision_id}`}
                >
                  Open Revision
                </a>
              ) : null}
              {context.research_session.workflow_id ? (
                <a className="button" href={`/execution?workflow=${context.research_session.workflow_id}`}>
                  Open Workflow
                </a>
              ) : null}
            </div>
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-title">Questions</div>
        <div className="stack">
          <textarea
            className="textarea"
            rows={3}
            value={questionText}
            onChange={(e) => setQuestionText(e.target.value)}
            placeholder="当前要回答的研究问题"
          />
          <div className="filter-row">
            <input
              className="input compact-input"
              type="number"
              value={questionPriority}
              onChange={(e) => setQuestionPriority(e.target.value)}
              placeholder="priority"
            />
            <textarea
              className="textarea"
              rows={3}
              value={assignedExpertsText}
              onChange={(e) => setAssignedExpertsText(e.target.value)}
              placeholder="assigned experts, use comma or newline"
            />
          </div>
          <button
            type="button"
            className="button primary"
            disabled={!selectedSession || !questionText.trim() || !!busyAction}
            onClick={() =>
              withAction("create-question", async () => {
                const payload = await createResearchQuestion(selectedSession, {
                  question_text: questionText.trim(),
                  priority: Number(questionPriority) || 50,
                  assigned_experts: splitLines(assignedExpertsText),
                });
                setQuestionText("");
                setSelectedQuestionId(payload.research_question.id);
                await refreshSelectedSession();
                setNoticeText("question 已加入当前 research session");
              })
            }
          >
            {busyAction === "create-question" ? "Saving..." : "Add Question"}
          </button>
          {questions.length ? (
            questions.map((question: any) => (
              <button
                key={question.id}
                type="button"
                className={`list-card${selectedQuestionId === question.id ? " active" : ""}`}
                onClick={() => setSelectedQuestionId(question.id)}
              >
                <div className="list-title">{question.question_text}</div>
                <div className="list-sub">
                  priority {question.priority} / {formatStateLabel(question.status)}
                </div>
                <div className="tag-row">
                  {(question.assigned_experts_json || []).map((expert: string) => (
                    <span key={`${question.id}-${expert}`} className="tag">
                      {expert}
                    </span>
                  ))}
                </div>
              </button>
            ))
          ) : (
            <div className="empty-state">先建立问题，再让专家提出 hypothesis。</div>
          )}
        </div>
      </section>

      <section className="panel">
        <div className="panel-title">Hypotheses</div>
        <div className="stack">
          <select className="input" value={selectedQuestionId} onChange={(e) => setSelectedQuestionId(e.target.value)}>
            <option value="">选择 question</option>
            {questions.map((question: any) => (
              <option key={question.id} value={question.id}>
                {question.question_text}
              </option>
            ))}
          </select>
          <div className="filter-row">
            <select className="input compact-input" value={expertRole} onChange={(e) => setExpertRole(e.target.value)}>
              <option value="research-lead">research-lead</option>
              <option value="wireless-protocol">wireless-protocol</option>
              <option value="web-vuln">web-vuln</option>
              <option value="identity-auth">identity-auth</option>
              <option value="crypto">crypto</option>
              <option value="skeptic">skeptic</option>
            </select>
            <input
              className="input compact-input"
              value={confidenceBefore}
              onChange={(e) => setConfidenceBefore(e.target.value)}
              placeholder="confidence"
            />
          </div>
          <input
            className="input"
            value={hypothesisTitle}
            onChange={(e) => setHypothesisTitle(e.target.value)}
            placeholder="hypothesis title"
          />
          <textarea
            className="textarea"
            rows={3}
            value={hypothesisSummary}
            onChange={(e) => setHypothesisSummary(e.target.value)}
            placeholder="hypothesis summary"
          />
          <textarea
            className="textarea"
            rows={3}
            value={assumptionsText}
            onChange={(e) => setAssumptionsText(e.target.value)}
            placeholder="assumptions, one per line"
          />
          <textarea
            className="textarea"
            rows={3}
            value={conditionsText}
            onChange={(e) => setConditionsText(e.target.value)}
            placeholder="applicability conditions, one per line"
          />
          <button
            type="button"
            className="button primary"
            disabled={!selectedQuestionId || !hypothesisTitle.trim() || !!busyAction}
            onClick={() =>
              withAction("create-hypothesis", async () => {
                const payload = await createResearchHypothesis(selectedQuestionId, {
                  expert_role: expertRole,
                  title: hypothesisTitle.trim(),
                  summary: hypothesisSummary.trim(),
                  assumptions: splitLines(assumptionsText),
                  applicability_conditions: splitLines(conditionsText),
                  confidence_before: Number(confidenceBefore) || 0.5,
                });
                setHypothesisTitle("");
                setHypothesisSummary("");
                setAssumptionsText("");
                setConditionsText("");
                setSelectedHypothesisId(payload.hypothesis.id);
                await refreshSelectedSession();
                setNoticeText("hypothesis 已创建");
              })
            }
          >
            {busyAction === "create-hypothesis" ? "Saving..." : "Add Hypothesis"}
          </button>
          {hypotheses.length ? (
            hypotheses.map((hypothesis: any) => (
              <button
                key={hypothesis.id}
                type="button"
                className={`list-card${selectedHypothesisId === hypothesis.id ? " active" : ""}`}
                onClick={() => {
                  setSelectedHypothesisId(hypothesis.id);
                  setReviewStatus(hypothesis.skeptic_review_status || "reviewed");
                  setReviewNotesText((hypothesis.skeptic_notes_json || []).join("\n"));
                }}
              >
                <div className="list-title">{hypothesis.title}</div>
                <div className="list-sub">
                  {hypothesis.expert_role} / {formatFallback(hypothesis.question_text, "none")}
                </div>
                <div className="detail-text">{formatFallback(hypothesis.summary, "no summary")}</div>
                <div className="tag-row">
                  <span className="tag">{formatStateLabel(hypothesis.status)}</span>
                  <span className="tag">{formatStateLabel(hypothesis.skeptic_review_status)}</span>
                  <span className="tag">{`conf ${hypothesis.confidence_before}`}</span>
                </div>
              </button>
            ))
          ) : (
            <div className="empty-state">问题建立后，再由专家提出 hypothesis。</div>
          )}
        </div>
      </section>

      <section className="panel">
        <div className="panel-title">Review + Experiment</div>
        {!selectedHypothesis ? (
          <div className="empty-state">先选一个 hypothesis。</div>
        ) : (
          <div className="stack">
            <SummaryGroup
              title={selectedHypothesis.title}
              lines={[
                `${selectedHypothesis.expert_role} / ${formatFallback(selectedHypothesis.question_text, "none")}`,
                formatFallback(selectedHypothesis.summary, "no summary"),
              ]}
              tags={[
                formatStateLabel(selectedHypothesis.skeptic_review_status),
                `conf ${selectedHypothesis.confidence_before}`,
              ]}
            />
            <select className="input compact-input" value={reviewStatus} onChange={(e) => setReviewStatus(e.target.value)}>
              <option value="reviewed">reviewed</option>
              <option value="challenged">challenged</option>
              <option value="needs-evidence">needs-evidence</option>
            </select>
            <textarea
              className="textarea"
              rows={3}
              value={reviewNotesText}
              onChange={(e) => setReviewNotesText(e.target.value)}
              placeholder="skeptic notes, one per line"
            />
            <button
              type="button"
              className="button"
              disabled={!selectedHypothesisId || !!busyAction}
              onClick={() =>
                withAction("review-hypothesis", async () => {
                  await reviewResearchHypothesis(selectedHypothesisId, {
                    skeptic_review_status: reviewStatus,
                    skeptic_notes: splitLines(reviewNotesText),
                  });
                  await refreshSelectedSession();
                  setNoticeText("hypothesis review 已更新");
                })
              }
            >
              {busyAction === "review-hypothesis" ? "Saving..." : "Save Review"}
            </button>

            <div className="subheading">Experiment Request</div>
            <input
              className="input"
              value={requestSummary}
              onChange={(e) => setRequestSummary(e.target.value)}
              placeholder="why this experiment matters"
            />
            <div className="filter-row">
              <select className="input compact-input" value={experimentCapability} onChange={(e) => setExperimentCapability(e.target.value)}>
                <option value="wireless">wireless</option>
                <option value="recon">recon</option>
                <option value="web">web</option>
                <option value="internal">internal</option>
                <option value="exploit">exploit</option>
                <option value="social">social</option>
              </select>
              <input
                className="input"
                value={experimentTask}
                onChange={(e) => setExperimentTask(e.target.value)}
                placeholder="task / operation"
              />
            </div>
            <textarea
              className="textarea"
              rows={3}
              value={experimentNotes}
              onChange={(e) => setExperimentNotes(e.target.value)}
              placeholder="task notes or experiment intent"
            />
            <textarea
              className="textarea"
              rows={3}
              value={requiredObservationsText}
              onChange={(e) => setRequiredObservationsText(e.target.value)}
              placeholder="required observations, one per line"
            />
            <textarea
              className="textarea"
              rows={3}
              value={expectedArtifactsText}
              onChange={(e) => setExpectedArtifactsText(e.target.value)}
              placeholder="expected artifacts, one per line"
            />
            <div className="filter-row">
              <select className="input compact-input" value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
              <select className="input compact-input" value={approvalMode} onChange={(e) => setApprovalMode(e.target.value)}>
                <option value="commander_review">commander_review</option>
                <option value="scope_gate">scope_gate</option>
              </select>
              <select className="input compact-input" value={launchProfile} onChange={(e) => setLaunchProfile(e.target.value)}>
                <option value="steady">steady</option>
                <option value="rush">rush</option>
              </select>
            </div>
            <label className="toggle-card">
              <input type="checkbox" checked={interactiveTask} onChange={(e) => setInteractiveTask(e.target.checked)} />
              <span>interactive</span>
            </label>
            <label className="toggle-card">
              <input
                type="checkbox"
                checked={secondaryConfirmation}
                onChange={(e) => setSecondaryConfirmation(e.target.checked)}
              />
              <span>secondary confirmation</span>
            </label>
            <button
              type="button"
              className="button primary"
              disabled={!selectedHypothesisId || !requestSummary.trim() || !experimentTask.trim() || !!busyAction}
              onClick={() =>
                withAction("create-experiment", async () => {
                  await createResearchExperiment(selectedHypothesisId, {
                    requested_by_role: selectedHypothesis.expert_role,
                    request_summary: requestSummary.trim(),
                    required_observations: splitLines(requiredObservationsText),
                    expected_artifacts: splitLines(expectedArtifactsText),
                    risk_level: riskLevel,
                    approval_mode: approvalMode,
                    suggested_tasks: [
                      {
                        type: "task",
                        category: experimentCapability,
                        task: experimentTask.trim(),
                        notes: experimentNotes.trim(),
                        params: {
                          executionMode: "agent_api",
                          interactive: interactiveTask,
                          secondaryConfirmation,
                          notes: experimentNotes.trim(),
                        },
                      },
                    ],
                  });
                  setRequestSummary("");
                  setExperimentTask("");
                  setExperimentNotes("");
                  setRequiredObservationsText("");
                  await refreshSelectedSession();
                  setNoticeText("experiment request 已创建");
                })
              }
            >
              {busyAction === "create-experiment" ? "Saving..." : "Create Experiment Request"}
            </button>
          </div>
        )}
      </section>

      <section className="panel span-2">
        <div className="panel-title">Experiments</div>
        <div className="stack">
          {experiments.length ? (
            experiments.map((experiment: any) => {
              const result = resultByExperimentId.get(experiment.id);
              return (
                <div key={experiment.id} className="mini-card">
                  <SummaryGroup
                    title={experiment.request_summary}
                    lines={[
                      `${formatCompactId(experiment.id)} / ${experiment.expert_role} / ${formatFallback(experiment.question_text, "none")}`,
                      `risk ${experiment.risk_level} / approval ${formatFallback(experiment.approval_mode, "none")}`,
                      `requested ${formatTimestamp(experiment.created_at)}`,
                    ]}
                    tags={[
                      formatStateLabel(experiment.status),
                      experiment.workflow_id ? `workflow ${formatCompactId(experiment.workflow_id)}` : "",
                      experiment.hypothesis_title || "",
                    ]}
                  />
                  {!!experiment.required_observations_json?.length && (
                    <RecordCard
                      title="Required Observations"
                      body={experiment.required_observations_json.join(" · ")}
                    />
                  )}
                  {!!experiment.suggested_tasks_json?.length && (
                    <RecordCard
                      title="Suggested Tasks"
                      body={experiment.suggested_tasks_json.map((task: any) => `${task.category || task.capability} / ${task.task || task.operation}`).join(" · ")}
                      tags={experiment.suggested_tasks_json.map((task: any) => task.category || task.capability)}
                    />
                  )}
                  <div className="button-row top-gap">
                    <button
                      type="button"
                      className="button"
                      disabled={experiment.status !== "pending_review" || !!busyAction}
                      onClick={() =>
                        withAction(`approve-${experiment.id}`, async () => {
                          await approveResearchExperiment(experiment.id, { approved_by: "commander" });
                          await refreshSelectedSession();
                          setNoticeText("experiment request 已批准");
                        })
                      }
                    >
                      {busyAction === `approve-${experiment.id}` ? "Approving..." : "Approve"}
                    </button>
                    <button
                      type="button"
                      className="button primary"
                      disabled={!["approved", "launched"].includes(experiment.status) || !!busyAction}
                      onClick={() =>
                        withAction(`launch-${experiment.id}`, async () => {
                          await launchResearchExperiment(experiment.id, { execution_profile: launchProfile });
                          await refreshSelectedSession();
                          setNoticeText("experiment 已进入执行队列");
                        })
                      }
                    >
                      {busyAction === `launch-${experiment.id}` ? "Launching..." : "Launch"}
                    </button>
                    {experiment.workflow_id ? (
                      <a className="button" href={`/execution?workflow=${experiment.workflow_id}`}>
                        Open Workflow
                      </a>
                    ) : null}
                  </div>
                  {result ? (
                    <div className="top-gap">
                      <SummaryGroup
                        title="Experiment Result"
                        lines={[
                          formatFallback(result.result_summary, "no result yet"),
                          `updated ${formatTimestamp(result.updated_at)}`,
                          `tasks ${(result.task_ids_json || []).length} / artifacts ${(result.artifact_refs_json || []).length}`,
                        ]}
                        tags={[
                          `delta ${result.confidence_delta}`,
                          result.workflow_id ? `workflow ${formatCompactId(result.workflow_id)}` : "",
                        ]}
                      />
                    </div>
                  ) : null}
                </div>
              );
            })
          ) : (
            <div className="empty-state">还没有 experiment request。</div>
          )}
        </div>
      </section>

      <section className="panel span-2">
        <div className="panel-title">Analysis Packages</div>
        <div className="stack">
          {analysisPackages.length ? (
            analysisPackages.map((pkg: any) => (
              <SummaryGroup
                key={pkg.id}
                title={pkg.package_title || formatCompactId(pkg.id)}
                lines={[
                  formatFallback(pkg.summary_text, "no summary"),
                  `updated ${formatTimestamp(pkg.updated_at)}`,
                ]}
                tags={[
                  `hypotheses ${(pkg.hypotheses_json || []).length}`,
                  `options ${(pkg.options_json || []).length}`,
                  `warnings ${(pkg.warnings_json || []).length}`,
                ]}
              />
            ))
          ) : (
            <div className="empty-state">v1 先把 session / hypothesis / experiment 跑通，analysis package 下一轮再接真正的汇总产出。</div>
          )}
        </div>
      </section>
    </div>
  );
}
