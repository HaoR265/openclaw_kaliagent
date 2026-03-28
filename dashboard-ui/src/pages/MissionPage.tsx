import { FormEvent, useEffect, useState } from "react";
import {
  analyzeMission,
  branchRevision,
  createApprovalScope,
  createCampaign,
  createMission,
  controlCampaign,
  discussMission,
  getMission,
  launchRevision,
  listMissions,
  reviseMissionPlan,
} from "../shared/api/client";
import { openStream } from "../shared/api/stream";
import { RecordCard } from "../components/RecordCard";
import { SummaryGroup } from "../components/SummaryGroup";
import type { Mission } from "../shared/types/control";
import { formatCompactId, formatFallback, formatStateLabel, getStatusChipToneClass, getTagToneClass } from "../shared/ui/present";

function stringifyParams(params: Record<string, unknown> | undefined) {
  return JSON.stringify(params || {}, Object.keys(params || {}).sort());
}

function buildRevisionDiff(revision: any, parentRevision: any) {
  const currentTasks = revision?.task_tree_json || [];
  const parentTasks = parentRevision?.task_tree_json || [];
  const sharedCount = Math.min(currentTasks.length, parentTasks.length);
  const changed: string[] = [];

  for (let index = 0; index < sharedCount; index += 1) {
    const current = currentTasks[index] || {};
    const previous = parentTasks[index] || {};
    const currentLabel = `${current.category || current.capability || "task"} / ${current.task || current.operation || "step"}`;
    const previousLabel = `${previous.category || previous.capability || "task"} / ${previous.task || previous.operation || "step"}`;
    const taskChanged =
      currentLabel !== previousLabel ||
      (current.notes || "") !== (previous.notes || "") ||
      stringifyParams(current.params) !== stringifyParams(previous.params);
    if (taskChanged) {
      changed.push(`step ${index + 1}: ${previousLabel} -> ${currentLabel}`);
    }
  }

  if (currentTasks.length > parentTasks.length) {
    currentTasks.slice(parentTasks.length).forEach((task: any, offset: number) => {
      changed.push(`step ${parentTasks.length + offset + 1}: added ${task.category || task.capability || "task"} / ${task.task || task.operation || "step"}`);
    });
  }

  if (parentTasks.length > currentTasks.length) {
    parentTasks.slice(currentTasks.length).forEach((task: any, offset: number) => {
      changed.push(`step ${currentTasks.length + offset + 1}: removed ${task.category || task.capability || "task"} / ${task.task || task.operation || "step"}`);
    });
  }

  return {
    parentId: parentRevision?.id || "",
    added: Math.max(currentTasks.length - parentTasks.length, 0),
    removed: Math.max(parentTasks.length - currentTasks.length, 0),
    changed: changed.length,
    preview: changed.slice(0, 6),
  };
}

export function MissionPage() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selected, setSelected] = useState<string>(() => new URLSearchParams(window.location.search).get("mission") || localStorage.getItem("mission:selected") || "");
  const [detail, setDetail] = useState<any>(null);
  const [selectedRevisionId, setSelectedRevisionId] = useState(() => new URLSearchParams(window.location.search).get("revision") || localStorage.getItem("mission:selectedRevision") || "");
  const [objective, setObjective] = useState("");
  const [title, setTitle] = useState("");
  const [discussion, setDiscussion] = useState("");
  const [busy, setBusy] = useState(false);
  const [campaignRevisionId, setCampaignRevisionId] = useState("");
  const [revisionNotes, setRevisionNotes] = useState<Record<string, string>>({});
  const [branchNames, setBranchNames] = useState<Record<string, string>>({});
  const [branchNotes, setBranchNotes] = useState<Record<string, string>>({});
  const [taskTreeDraft, setTaskTreeDraft] = useState<any[]>([]);
  const [treeRevisionNote, setTreeRevisionNote] = useState("");
  const [selectedDraftIndexes, setSelectedDraftIndexes] = useState<number[]>([]);
  const [campaignError, setCampaignError] = useState("");
  const [streamState, setStreamState] = useState<"connecting" | "live" | "reconnecting" | "recovered">("connecting");

  async function loadMission(missionId: string) {
    const item = await getMission(missionId);
    setDetail(item);
  }

  async function refresh() {
    const items = await listMissions();
    setMissions(items);
    if (!selected && items[0]?.id) {
      setSelected(items[0].id);
    } else if (selected && !items.some((item) => item.id === selected) && items[0]?.id) {
      setSelected(items[0].id);
    }
  }

  useEffect(() => {
    refresh().catch(console.error);
  }, []);

  useEffect(() => {
    if (selected) {
      localStorage.setItem("mission:selected", selected);
      const url = new URL(window.location.href);
      url.searchParams.set("mission", selected);
      window.history.replaceState({}, "", `${url.pathname}${url.search}`);
    }
  }, [selected]);

  useEffect(() => {
    if (selectedRevisionId) {
      localStorage.setItem("mission:selectedRevision", selectedRevisionId);
      const url = new URL(window.location.href);
      url.searchParams.set("revision", selectedRevisionId);
      window.history.replaceState({}, "", `${url.pathname}${url.search}`);
    }
  }, [selectedRevisionId]);

  useEffect(() => {
    if (!selected) return;
    loadMission(selected).catch(console.error);
  }, [selected]);

  useEffect(() => {
    const revisions = detail?.revisions || [];
    if (!revisions.length) {
      setSelectedRevisionId("");
      return;
    }
    if (!selectedRevisionId || !revisions.some((revision: any) => revision.id === selectedRevisionId)) {
      setSelectedRevisionId(revisions[0].id);
    }
  }, [detail, selectedRevisionId]);

  useEffect(() => {
    const revisions = detail?.revisions || [];
    const activeRevision =
      revisions.find((revision: any) => revision.id === selectedRevisionId) || revisions[0] || null;
    setTaskTreeDraft(activeRevision ? JSON.parse(JSON.stringify(activeRevision.task_tree_json || [])) : []);
    setTreeRevisionNote(activeRevision?.change_summary || "");
    setSelectedDraftIndexes([]);
  }, [detail, selectedRevisionId]);

  useEffect(() => {
    if (!selected) return;
    const timer = window.setInterval(() => {
      refresh().catch(() => undefined);
    }, 15000);
    const source = openStream({ missionId: selected }, (payload) => setDetail(payload), {
      onStatus: setStreamState,
    });
    return () => {
      window.clearInterval(timer);
      source.close();
    };
  }, [selected]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    const { mission } = await createMission({
      title: title || "未命名 Mission",
      objective_text: objective,
      priority: "high",
    });
    setTitle("");
    setObjective("");
    await refresh();
    setSelected(mission.id);
  }

  async function onDiscuss(e: FormEvent) {
    e.preventDefault();
    if (!selected || !discussion.trim()) return;
    setBusy(true);
    await discussMission(selected, { content_text: discussion, run_analyst: true });
    setDiscussion("");
    await loadMission(selected);
    setBusy(false);
  }

  async function onAnalyze() {
    if (!selected) return;
    setBusy(true);
    await analyzeMission(selected);
    await loadMission(selected);
    setBusy(false);
  }

  async function onLaunch(revisionId: string) {
    if (!selected) return;
    setBusy(true);
    await launchRevision(revisionId, {
      launch_mode: "assisted",
      execution_profile: "steady",
    });
    await loadMission(selected);
    await refresh();
    setBusy(false);
  }

  async function onRevisePlan(planId: string, parentRevisionId?: string) {
    if (!selected) return;
    setBusy(true);
    try {
      await reviseMissionPlan(selected, planId, {
        change_summary: revisionNotes[planId]?.trim() || "manual revision",
        parent_revision_id: parentRevisionId,
        launchable: true,
      });
      setRevisionNotes((current) => ({ ...current, [planId]: "" }));
      await loadMission(selected);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function onBranchRevision(revisionId: string) {
    const branchKey = (branchNames[revisionId] || "").trim();
    if (!branchKey || !selected) return;
    setBusy(true);
    try {
      await branchRevision(revisionId, {
        branch_key: branchKey,
        change_summary: branchNotes[revisionId]?.trim() || `branch ${branchKey}`,
      });
      setBranchNames((current) => ({ ...current, [revisionId]: "" }));
      setBranchNotes((current) => ({ ...current, [revisionId]: "" }));
      await loadMission(selected);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function onCreateCampaign() {
    if (!selected || !campaignRevisionId) return;
    setBusy(true);
    setCampaignError("");
    try {
      const scopeResult = await createApprovalScope(selected, {
        scope_name: "default-campaign-scope",
        allowed_categories: ["wireless", "recon", "web", "internal", "exploit", "social"],
        allowed_tools: [],
        high_risk_tools: [],
        interactive_tools: [],
      });
      await createCampaign({
        mission_session_id: selected,
        plan_revision_id: campaignRevisionId,
        approval_scope_id: scopeResult.approval_scope.id,
        execution_profile: "rush",
        auto_replan_enabled: true,
        max_parallelism: 2,
      });
      await loadMission(selected);
      await refresh();
    } catch (error) {
      setCampaignError(error instanceof Error ? error.message : "campaign action failed");
    } finally {
      setBusy(false);
    }
  }

  async function onControlCampaign(campaignId: string, action: string) {
    setBusy(true);
    setCampaignError("");
    try {
      await controlCampaign(campaignId, action);
      await loadMission(selected);
    } catch (error) {
      setCampaignError(error instanceof Error ? error.message : "campaign control failed");
    } finally {
      setBusy(false);
    }
  }

  function updateDraftTask(index: number, key: string, value: string) {
    setTaskTreeDraft((current) =>
      current.map((task, taskIndex) =>
        taskIndex === index
          ? {
              ...task,
              [key]: value,
            }
          : task,
      ),
    );
  }

  function removeDraftTask(index: number) {
    setTaskTreeDraft((current) => current.filter((_, taskIndex) => taskIndex !== index));
    setSelectedDraftIndexes((current) => current.filter((item) => item !== index).map((item) => (item > index ? item - 1 : item)));
  }

  function addDraftTask() {
    setTaskTreeDraft((current) => [
      ...current,
      {
        category: "recon",
        task: "new-task",
        notes: "",
        type: "task",
        params: {},
      },
    ]);
  }

  function cloneDraftTask(index: number) {
    setTaskTreeDraft((current) => {
      const source = current[index];
      if (!source) {
        return current;
      }
      const clone = JSON.parse(JSON.stringify(source));
      return [...current.slice(0, index + 1), clone, ...current.slice(index + 1)];
    });
  }

  function toggleDraftSelection(index: number, checked: boolean) {
    setSelectedDraftIndexes((current) => {
      if (checked) {
        return current.includes(index) ? current : [...current, index].sort((a, b) => a - b);
      }
      return current.filter((item) => item !== index);
    });
  }

  function clearDraftSelection() {
    setSelectedDraftIndexes([]);
  }

  function removeSelectedDraftTasks() {
    if (!selectedDraftIndexes.length) {
      return;
    }
    setTaskTreeDraft((current) => current.filter((_, taskIndex) => !selectedDraftIndexes.includes(taskIndex)));
    setSelectedDraftIndexes([]);
  }

  function moveDraftTask(index: number, direction: -1 | 1) {
    setTaskTreeDraft((current) => {
      const nextIndex = index + direction;
      if (nextIndex < 0 || nextIndex >= current.length) {
        return current;
      }
      const clone = [...current];
      const [item] = clone.splice(index, 1);
      clone.splice(nextIndex, 0, item);
      return clone;
    });
  }

  function updateDraftTaskParam(index: number, key: string, value: string) {
    setTaskTreeDraft((current) =>
      current.map((task, taskIndex) =>
        taskIndex === index
          ? {
              ...task,
              params: {
                ...(task.params || {}),
                [key]: value,
              },
            }
          : task,
      ),
    );
  }

  function updateDraftTaskFlag(index: number, key: string, checked: boolean) {
    setTaskTreeDraft((current) =>
      current.map((task, taskIndex) =>
        taskIndex === index
          ? {
              ...task,
              params: {
                ...(task.params || {}),
                [key]: checked,
              },
            }
          : task,
      ),
    );
  }

  function removeDraftTaskParam(index: number, key: string) {
    setTaskTreeDraft((current) =>
      current.map((task, taskIndex) => {
        if (taskIndex !== index) {
          return task;
        }
        const nextParams = { ...(task.params || {}) };
        delete nextParams[key];
        return {
          ...task,
          params: nextParams,
        };
      }),
    );
  }

  function addDraftTaskParam(index: number) {
    setTaskTreeDraft((current) =>
      current.map((task, taskIndex) => {
        if (taskIndex !== index) {
          return task;
        }
        const params = { ...(task.params || {}) };
        let seed = "newParam";
        let counter = 1;
        while (seed in params) {
          seed = `newParam${counter}`;
          counter += 1;
        }
        params[seed] = "";
        return {
          ...task,
          params,
        };
      }),
    );
  }

  function getOrderedTaskParams(task: any): Array<[string, unknown]> {
    const params = Object.entries(task.params || {});
    const priority = ["executionMode", "interactive", "secondaryConfirmation"];
    return params.sort(([left], [right]) => {
      const leftIndex = priority.indexOf(left);
      const rightIndex = priority.indexOf(right);
      if (leftIndex >= 0 || rightIndex >= 0) {
        if (leftIndex < 0) return 1;
        if (rightIndex < 0) return -1;
        return leftIndex - rightIndex;
      }
      return left.localeCompare(right);
    });
  }

  async function onSaveTaskTreeRevision() {
    if (!selected || !selectedRevision) return;
    setBusy(true);
    try {
      await reviseMissionPlan(selected, selectedRevision.plan_candidate_id, {
        change_summary: treeRevisionNote.trim() || `refine ${selectedRevision.branch_key} rev ${selectedRevision.revision_no}`,
        parent_revision_id: selectedRevision.id,
        branch_key: selectedRevision.branch_key,
        launchable: true,
        task_tree: taskTreeDraft,
        plan_outline: selectedRevision.plan_outline_json || {},
      });
      await loadMission(selected);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  const revisions = detail?.revisions || [];
  const selectedRevision = revisions.find((revision: any) => revision.id === selectedRevisionId) || revisions[0] || null;
  const currentMainRevision =
    revisions.find((revision: any) => revision.branch_key === "main") || null;
  const parentRevision =
    selectedRevision?.parent_revision_id
      ? revisions.find((revision: any) => revision.id === selectedRevision.parent_revision_id) || null
      : null;
  const revisionDiff = selectedRevision ? buildRevisionDiff(selectedRevision, parentRevision) : null;
  const missionStats = detail
    ? [
        `plans ${(detail.plans || []).length}`,
        `revisions ${(detail.revisions || []).length}`,
        `analysis ${(detail.analysis_jobs || []).length}`,
        `campaigns ${(detail.campaigns || []).length}`,
      ]
    : [];

  return (
    <div className="page-grid">
      <section className="panel">
        <div className="panel-title">Mission Intake</div>
        <form className="stack" onSubmit={onCreate}>
          <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Mission title" />
          <textarea
            className="textarea"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            placeholder="Describe mission objective"
            rows={6}
          />
          <button className="button primary" type="submit">创建 Mission</button>
        </form>
      </section>
      <section className="panel">
        <div className="panel-title">Mission List</div>
        <div className="stack">
          {missions.length ? (
            missions.map((mission) => (
              <button
                key={mission.id}
                className={`list-card${selected === mission.id ? " active" : ""}`}
                onClick={() => setSelected(mission.id)}
                type="button"
              >
                <div className="list-title">{mission.title}</div>
                <div className="list-sub">{formatStateLabel(mission.status)} · {mission.priority}</div>
              </button>
            ))
          ) : (
            <div className="empty-state">暂无 Mission，先创建一个新的工作项。</div>
          )}
        </div>
      </section>
      <section className="panel span-2">
        <div className="panel-title">Mission Workbench</div>
        {!detail ? (
          <div className="empty-state">选择或创建一个 Mission。</div>
        ) : (
          <>
            <SummaryGroup
              title={detail.mission.title}
              lines={[detail.mission.objective_text]}
              tags={[
                detail.mission.status,
                detail.mission.priority,
                ...(detail.mission.latest_workflow_id ? ["wf linked"] : []),
                ...(detail.mission.active_campaign_run_id ? ["campaign active"] : []),
              ]}
            />
            {streamState !== "live" ? (
              <div className="empty-state top-gap">
                {streamState === "connecting"
                  ? "实时流连接中。"
                  : streamState === "recovered"
                    ? "实时流已恢复，数据已刷新。"
                    : "实时流重连中，页面会自动恢复。"}
              </div>
            ) : null}
            <div className="stats-strip top-gap">
              {missionStats.map((chip) => (
                <div key={chip} className={`status-chip ${getStatusChipToneClass(chip)}`.trim()}>
                  {chip}
                </div>
              ))}
            </div>
            <form className="stack" onSubmit={onDiscuss}>
              <textarea
                className="textarea"
                value={discussion}
                onChange={(e) => setDiscussion(e.target.value)}
                placeholder="Add discussion, intelligence, or operator note"
                rows={4}
              />
              <div className="button-row">
                <button className="button" type="submit" disabled={busy}>提交讨论并触发 Analyst</button>
                <button className="button primary" type="button" disabled={busy} onClick={onAnalyze}>
                  直接分析 Mission
                </button>
              </div>
            </form>
            <div className="dual">
              <div>
                <div className="subheading">Discussion</div>
                <div className="stack">
                  {(detail.messages || []).length ? (
                    (detail.messages || []).map((message: any) => (
                      <article className="mini-card" key={message.id}>
                        <div className="mini-title">{message.role} · {message.message_kind}</div>
                        <div className="muted">{message.content_text}</div>
                      </article>
                    ))
                  ) : (
                    <div className="empty-state">暂无讨论记录。</div>
                  )}
                </div>
              </div>
              <div>
                <div className="subheading">Analyst</div>
                <div className="stack">
                  {(detail.analysis_jobs || []).length ? (
                    (detail.analysis_jobs || []).map((job: any) => (
                      <article className="mini-card" key={job.id}>
                        <div className="mini-title">{job.job_kind} · {formatStateLabel(job.status)}</div>
                        <div className="muted">{job.query_text}</div>
                        {job.output_summary ? <div className="detail-text">{job.output_summary}</div> : null}
                      </article>
                    ))
                  ) : (
                    <div className="empty-state">暂无分析作业。</div>
                  )}
                </div>
              </div>
            </div>
            <div className="dual mission-lower">
              <div>
                <div className="subheading">Plan Candidates</div>
                <div className="stack">
                  {(detail.plans || []).length ? (
                    (detail.plans || []).map((plan: any) => (
                      <article className="mini-card" key={plan.id}>
                        <div className="mini-title">{plan.title} · {formatStateLabel(plan.status)}</div>
                        <div className="muted">{plan.goal_summary}</div>
                        {plan.discussion_summary ? <div className="detail-text">{plan.discussion_summary}</div> : null}
                        <div className="tag-row">
                          {(plan.assumptions_json || []).slice(0, 3).map((item: string) => (
                            <span key={`${plan.id}-${item}`} className="tag">A: {item}</span>
                          ))}
                          {(detail.revisions || [])
                            .filter((revision: any) => revision.plan_candidate_id === plan.id)
                            .slice(0, 1)
                            .map((revision: any) => (
                              <span key={`${plan.id}-current-${revision.id}`} className="tag status-tag">
                                current rev {revision.revision_no} · {revision.branch_key}
                              </span>
                            ))}
                        </div>
                        <div className="stack top-gap">
                          <input
                            className="input"
                            value={revisionNotes[plan.id] || ""}
                            onChange={(e) => setRevisionNotes((current) => ({ ...current, [plan.id]: e.target.value }))}
                            placeholder="Describe revision change"
                          />
                          <button
                            className="button"
                            type="button"
                            disabled={busy}
                            onClick={() =>
                              onRevisePlan(
                                plan.id,
                                (detail.revisions || []).find((revision: any) => revision.plan_candidate_id === plan.id)?.id,
                              )
                            }
                          >
                            New Revision
                          </button>
                        </div>
                      </article>
                    ))
                  ) : (
                    <div className="empty-state">暂无方案候选。</div>
                  )}
                </div>
              </div>
              <div>
                <div className="subheading">Revisions / Campaign</div>
                {currentMainRevision ? (
                  <SummaryGroup
                    title="Current Main Revision"
                    lines={[
                      `${formatCompactId(currentMainRevision.id)} · rev ${currentMainRevision.revision_no}`,
                      formatFallback(currentMainRevision.change_summary, "no summary"),
                    ]}
                    tags={[
                      currentMainRevision.branch_key,
                      currentMainRevision.launchable ? "launchable" : "draft",
                    ]}
                  />
                ) : null}
                {detail.mission.latest_workflow_id || detail.mission.active_campaign_run_id ? (
                  <div className="button-row top-gap">
                    {detail.mission.latest_workflow_id ? (
                      <a className="button" href={`/execution?workflow=${detail.mission.latest_workflow_id}`}>
                        Open Current Workflow
                      </a>
                    ) : null}
                    {detail.mission.active_campaign_run_id ? (
                      <a className="button" href={`/campaigns?campaign=${detail.mission.active_campaign_run_id}`}>
                        Open Current Campaign
                      </a>
                    ) : null}
                  </div>
                ) : null}
                <SummaryGroup
                  title="Run Chain"
                  lines={[
                    `mission ${formatStateLabel(detail.mission.status)}`,
                    `workflow ${formatCompactId(detail.mission.latest_workflow_id)}`,
                    `campaign ${formatCompactId(detail.mission.active_campaign_run_id)}`,
                  ]}
                  tags={[
                    selectedRevisionId ? `revision ${formatCompactId(selectedRevisionId)}` : "",
                  ]}
                />
                <div className="button-row top-gap">
                  <select
                    className="input compact-input"
                    value={campaignRevisionId}
                    onChange={(e) => setCampaignRevisionId(e.target.value)}
                  >
                    <option value="">选择 revision 启动 campaign</option>
                    {(detail.revisions || []).map((revision: any) => (
                      <option key={revision.id} value={revision.id}>
                        {formatCompactId(revision.id)} · rev {revision.revision_no} · {revision.branch_key}
                      </option>
                    ))}
                  </select>
                  <button className="button primary" type="button" disabled={busy || !campaignRevisionId} onClick={onCreateCampaign}>
                    Start Campaign
                  </button>
                </div>
                {campaignError ? <div className="empty-state top-gap">{campaignError}</div> : null}
                <div className="stack">
                  {(detail.revisions || []).length ? (
                    (detail.revisions || []).map((revision: any) => (
                      <article
                        className={`mini-card revision-card${selectedRevisionId === revision.id ? " active" : ""}`}
                        key={revision.id}
                      >
                        <div className="mini-title">
                          rev {revision.revision_no} · {revision.branch_key} · {formatStateLabel(revision.launchable ? "planned" : "draft")}
                        </div>
                        <div className="muted">{formatFallback(revision.change_summary, "no summary")}</div>
                        {revision.parent_revision_id ? (
                          <div className="muted">parent {formatCompactId(revision.parent_revision_id)}</div>
                        ) : null}
                        {(revision.task_tree_json || []).length ? (
                          <div className="tag-row">
                            {(revision.task_tree_json || []).slice(0, 4).map((task: any, index: number) => (
                              <span key={`${revision.id}-${index}`} className="tag">
                                {(task.category || task.capability || "task")} / {(task.task || task.operation || "step")}
                              </span>
                            ))}
                          </div>
                        ) : null}
                        <div className="button-row top-gap">
                          <button
                            className="button"
                            type="button"
                            onClick={() => setSelectedRevisionId(revision.id)}
                          >
                            Preview Tree
                          </button>
                          <button
                            className="button"
                            type="button"
                            disabled={busy}
                            onClick={() => onRevisePlan(revision.plan_candidate_id, revision.id)}
                          >
                            Clone To Revision
                          </button>
                          <button
                            className="button"
                            type="button"
                            disabled={busy || !revision.launchable}
                            onClick={() => onLaunch(revision.id)}
                          >
                            Launch Revision
                          </button>
                        </div>
                        <div className="stack top-gap">
                          <input
                            className="input"
                            value={branchNames[revision.id] || ""}
                            onChange={(e) => setBranchNames((current) => ({ ...current, [revision.id]: e.target.value }))}
                            placeholder="Branch key"
                          />
                          <input
                            className="input"
                            value={branchNotes[revision.id] || ""}
                            onChange={(e) => setBranchNotes((current) => ({ ...current, [revision.id]: e.target.value }))}
                            placeholder="Branch note"
                          />
                          <button
                            className="button"
                            type="button"
                            disabled={busy || !(branchNames[revision.id] || "").trim()}
                            onClick={() => onBranchRevision(revision.id)}
                          >
                            Create Branch
                          </button>
                        </div>
                      </article>
                    ))
                  ) : (
                    <div className="empty-state">暂无 revision。</div>
                  )}
                  {(detail.campaigns || []).length ? (
                    (detail.campaigns || []).map((campaign: any) => (
                      <article className="mini-card" key={campaign.id}>
                        <div className="mini-title">{formatCompactId(campaign.id)} · {formatStateLabel(campaign.status)}</div>
                        <div className="muted">{campaign.execution_profile} / parallel {campaign.max_parallelism}</div>
                        <div className="tag-row">
                          <span className={`tag ${getTagToneClass(campaign.status)}`.trim()}>{formatStateLabel(campaign.status)}</span>
                          <span className="tag">{campaign.execution_profile}</span>
                          <span className="tag">auto-replan {campaign.auto_replan_enabled ? "on" : "off"}</span>
                        </div>
                        <div className="button-row top-gap">
                          {campaign.status === "under_review" ? (
                            <button className="button primary" type="button" disabled={busy} onClick={() => onControlCampaign(campaign.id, "approve")}>Approve</button>
                          ) : null}
                          <button className="button" type="button" disabled={busy} onClick={() => onControlCampaign(campaign.id, "pause")}>Pause</button>
                          <button className="button" type="button" disabled={busy} onClick={() => onControlCampaign(campaign.id, "resume")}>Resume</button>
                          <button className="button" type="button" disabled={busy} onClick={() => onControlCampaign(campaign.id, "stop")}>Stop</button>
                        </div>
                      </article>
                    ))
                  ) : (
                    <div className="empty-state">暂无 campaign。</div>
                  )}
                </div>
              </div>
            </div>
            <div className="dual mission-lower">
              <div>
                <div className="subheading">Revision Timeline</div>
                <div className="stack">
                  {revisions.length ? (
                    revisions.map((revision: any) => (
                      <button
                        key={`timeline-${revision.id}`}
                        className={`list-card revision-timeline${selectedRevisionId === revision.id ? " active" : ""}`}
                        onClick={() => setSelectedRevisionId(revision.id)}
                        type="button"
                      >
                        <div className="list-title">
                          {revision.branch_key} · rev {revision.revision_no}
                          {currentMainRevision?.id === revision.id ? " · current main" : ""}
                        </div>
                        <div className="list-sub">{formatFallback(revision.change_summary, "no summary")}</div>
                        <div className="list-sub">
                          {revision.parent_revision_id ? `from ${formatCompactId(revision.parent_revision_id)}` : "root revision"}
                        </div>
                      </button>
                    ))
                  ) : (
                    <div className="empty-state">暂无 revision timeline。</div>
                  )}
                </div>
              </div>
              <div>
                <div className="subheading">Task Tree Preview</div>
                {!selectedRevision ? (
                  <div className="empty-state">选择一个 revision 预览任务树。</div>
                ) : (
                  <div className="stack">
                    <SummaryGroup
                      title={`${selectedRevision.branch_key} · rev ${selectedRevision.revision_no}`}
                      lines={[
                        formatCompactId(selectedRevision.id),
                        formatFallback(selectedRevision.change_summary, "no summary"),
                      ]}
                      tags={[
                        selectedRevision.launchable ? "launchable" : "draft",
                        `tasks ${(selectedRevision.task_tree_json || []).length}`,
                      ]}
                    />
                    <SummaryGroup
                      title="Revision Diff"
                      lines={
                        revisionDiff?.parentId
                          ? [
                              `parent ${formatCompactId(revisionDiff.parentId)}`,
                              ...revisionDiff.preview,
                            ]
                          : ["root revision"]
                      }
                      tags={
                        revisionDiff
                          ? [
                              `changed ${revisionDiff.changed}`,
                              `added ${revisionDiff.added}`,
                              `removed ${revisionDiff.removed}`,
                            ]
                          : []
                      }
                    />
                    <div className="mini-card">
                      <div className="mini-title">Edit Before Launch</div>
                      <div className="stack top-gap">
                        <input
                          className="input"
                          value={treeRevisionNote}
                          onChange={(e) => setTreeRevisionNote(e.target.value)}
                          placeholder="Describe revision change"
                        />
                        <div className="button-row">
                          <button className="button" type="button" onClick={addDraftTask}>
                            Add Task
                          </button>
                          <button
                            className="button"
                            type="button"
                            disabled={!selectedDraftIndexes.length}
                            onClick={removeSelectedDraftTasks}
                          >
                            Delete Selected
                          </button>
                          <button
                            className="button"
                            type="button"
                            disabled={!selectedDraftIndexes.length}
                            onClick={clearDraftSelection}
                          >
                            Clear Selection
                          </button>
                          <button className="button primary" type="button" disabled={busy} onClick={onSaveTaskTreeRevision}>
                            Save As New Revision
                          </button>
                        </div>
                      </div>
                    </div>
                    {taskTreeDraft.length ? (
                      taskTreeDraft.map((task: any, index: number) => (
                        <article className="mini-card" key={`${selectedRevision.id}-task-edit-${index}`}>
                          <div className="task-header-row">
                            <label className="toggle-card">
                              <input
                                type="checkbox"
                                checked={selectedDraftIndexes.includes(index)}
                                onChange={(e) => toggleDraftSelection(index, e.target.checked)}
                              />
                              <span>select</span>
                            </label>
                            <div className="mini-title">{index + 1}. {task.task || task.operation || "step"}</div>
                          </div>
                          <div className="task-edit-grid">
                            <select
                              className="input"
                              value={task.category || task.capability || "recon"}
                              onChange={(e) => updateDraftTask(index, "category", e.target.value)}
                            >
                              <option value="wireless">wireless</option>
                              <option value="recon">recon</option>
                              <option value="web">web</option>
                              <option value="internal">internal</option>
                              <option value="exploit">exploit</option>
                              <option value="social">social</option>
                            </select>
                            <input
                              className="input"
                              value={task.task || task.operation || ""}
                              onChange={(e) => updateDraftTask(index, "task", e.target.value)}
                              placeholder="Task name"
                            />
                          </div>
                          <textarea
                            className="textarea top-gap"
                            rows={3}
                            value={task.notes || ""}
                            onChange={(e) => updateDraftTask(index, "notes", e.target.value)}
                            placeholder="Task notes"
                          />
                          <div className="task-toggle-grid top-gap">
                            <select
                              className="input"
                              value={task.params?.executionMode || "agent_api"}
                              onChange={(e) => updateDraftTaskParam(index, "executionMode", e.target.value)}
                            >
                              <option value="agent_api">agent_api</option>
                              <option value="local_tool">local_tool</option>
                              <option value="hybrid">hybrid</option>
                            </select>
                            <label className="toggle-card">
                              <input
                                type="checkbox"
                                checked={Boolean(task.params?.interactive)}
                                onChange={(e) => updateDraftTaskFlag(index, "interactive", e.target.checked)}
                              />
                              <span>interactive</span>
                            </label>
                            <label className="toggle-card">
                              <input
                                type="checkbox"
                                checked={Boolean(task.params?.secondaryConfirmation)}
                                onChange={(e) => updateDraftTaskFlag(index, "secondaryConfirmation", e.target.checked)}
                              />
                              <span>secondary confirmation</span>
                            </label>
                          </div>
                          <div className="stack top-gap">
                            <div className="mini-title">Params</div>
                            {getOrderedTaskParams(task).map(([key, value]) => (
                              <div className="param-row" key={`${selectedRevision.id}-${index}-${key}`}>
                                <input
                                  className="input"
                                  value={key}
                                  onChange={(e) => {
                                    const nextKey = e.target.value;
                                    if (!nextKey || nextKey === key) return;
                                    removeDraftTaskParam(index, key);
                                    updateDraftTaskParam(index, nextKey, String(value));
                                  }}
                                  placeholder="Param key"
                                />
                                <input
                                  className="input"
                                  value={String(value)}
                                  onChange={(e) => updateDraftTaskParam(index, key, e.target.value)}
                                  placeholder="Param value"
                                />
                                <button className="button" type="button" onClick={() => removeDraftTaskParam(index, key)}>
                                  Remove Param
                                </button>
                              </div>
                            ))}
                            <button className="button" type="button" onClick={() => addDraftTaskParam(index)}>
                              Add Param
                            </button>
                          </div>
                          <div className="tag-row">
                            <span className="tag">{task.type || "task"}</span>
                            {getOrderedTaskParams(task).map(([key, value]) => (
                              <span className="tag" key={`${selectedRevision.id}-${index}-${key}`}>
                                {key}={String(value)}
                              </span>
                            ))}
                          </div>
                          <div className="button-row top-gap">
                            <button
                              className="button"
                              type="button"
                              disabled={index === 0}
                              onClick={() => moveDraftTask(index, -1)}
                            >
                              Move Up
                            </button>
                            <button
                              className="button"
                              type="button"
                              disabled={index === taskTreeDraft.length - 1}
                              onClick={() => moveDraftTask(index, 1)}
                            >
                              Move Down
                            </button>
                            <button className="button" type="button" onClick={() => cloneDraftTask(index)}>
                              Clone Task
                            </button>
                            <button className="button" type="button" onClick={() => removeDraftTask(index)}>
                              Remove Task
                            </button>
                          </div>
                        </article>
                      ))
                    ) : (
                      <div className="empty-state">这个 revision 目前没有任务树内容，可以直接新增节点。</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
