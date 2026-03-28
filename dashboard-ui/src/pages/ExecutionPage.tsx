import { useEffect, useState } from "react";
import { RecordCard } from "../components/RecordCard";
import { SummaryGroup } from "../components/SummaryGroup";
import { getArtifact, getWorkflow, listWorkflows } from "../shared/api/client";
import { openStream } from "../shared/api/stream";
import { formatCompactId, formatFallback, formatStateLabel, formatTimestamp, getStatusChipToneClass } from "../shared/ui/present";

export function ExecutionPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [selected, setSelected] = useState<string>(() => new URLSearchParams(window.location.search).get("workflow") || localStorage.getItem("execution:selected") || "");
  const [detail, setDetail] = useState<any>(null);
  const [taskStateFilter, setTaskStateFilter] = useState(() => localStorage.getItem("execution:taskState") || "all");
  const [taskQuery, setTaskQuery] = useState(() => localStorage.getItem("execution:taskQuery") || "");
  const [timelineFilter, setTimelineFilter] = useState(() => localStorage.getItem("execution:timelineFilter") || "all");
  const [taskFocus, setTaskFocus] = useState(() => localStorage.getItem("execution:taskFocus") || "");
  const [artifactFocus, setArtifactFocus] = useState(() => localStorage.getItem("execution:artifactFocus") || "");
  const [artifactDetail, setArtifactDetail] = useState<any>(null);
  const [streamState, setStreamState] = useState<"connecting" | "live" | "reconnecting" | "recovered">("connecting");

  useEffect(() => {
    listWorkflows()
      .then((items: any) => {
        setWorkflows(items);
        if (!selected && items[0]?.workflow_id) {
          setSelected(items[0].workflow_id);
        } else if (
          selected &&
          !items.some((item: any) => item.workflow_id === selected) &&
          items[0]?.workflow_id
        ) {
          setSelected(items[0].workflow_id);
        }
      })
      .catch(console.error);
  }, [selected]);

  useEffect(() => {
    if (!selected) return;
    getWorkflow(selected).then(setDetail).catch(console.error);
  }, [selected]);

  useEffect(() => {
    if (selected) {
      localStorage.setItem("execution:selected", selected);
      const url = new URL(window.location.href);
      url.searchParams.set("workflow", selected);
      window.history.replaceState({}, "", `${url.pathname}${url.search}`);
    }
  }, [selected]);

  useEffect(() => {
    localStorage.setItem("execution:taskState", taskStateFilter);
  }, [taskStateFilter]);

  useEffect(() => {
    localStorage.setItem("execution:taskQuery", taskQuery);
  }, [taskQuery]);

  useEffect(() => {
    localStorage.setItem("execution:timelineFilter", timelineFilter);
  }, [timelineFilter]);

  useEffect(() => {
    localStorage.setItem("execution:taskFocus", taskFocus);
  }, [taskFocus]);

  useEffect(() => {
    localStorage.setItem("execution:artifactFocus", artifactFocus);
  }, [artifactFocus]);

  useEffect(() => {
    if (!artifactFocus) {
      setArtifactDetail(null);
      return;
    }
    getArtifact(artifactFocus)
      .then((payload) => setArtifactDetail(payload.artifact))
      .catch(() => {
        setArtifactDetail(null);
        setArtifactFocus("");
      });
  }, [artifactFocus]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      listWorkflows()
        .then((items: any) => {
          setWorkflows(items);
          if (!selected && items[0]?.workflow_id) {
            setSelected(items[0].workflow_id);
          } else if (selected && !items.some((item: any) => item.workflow_id === selected) && items[0]?.workflow_id) {
            setSelected(items[0].workflow_id);
          }
        })
        .catch(() => undefined);
      if (selected) {
        getWorkflow(selected).then(setDetail).catch(() => undefined);
      }
    }, 15000);
    const source = selected ? openStream({ workflowId: selected }, (payload) => setDetail(payload), {
      onStatus: setStreamState,
    }) : null;
    return () => {
      window.clearInterval(timer);
      source?.close();
    };
  }, [selected]);

  const tasks = detail?.tasks || [];
  const artifacts = detail?.artifacts || [];
  const timeline = detail?.timeline || [];

  useEffect(() => {
    if (taskFocus && !tasks.some((task: any) => task.id === taskFocus)) {
      setTaskFocus("");
    }
    if (artifactFocus && !artifacts.some((artifact: any) => artifact.id === artifactFocus)) {
      setArtifactFocus("");
    }
  }, [taskFocus, artifactFocus, tasks, artifacts]);

  const filteredTasks = tasks.filter((task: any) => {
    if (taskFocus && task.id !== taskFocus) {
      return false;
    }
    if (taskStateFilter !== "all" && task.state !== taskStateFilter) {
      return false;
    }
    if (!taskQuery.trim()) {
      return true;
    }
    const haystack = JSON.stringify(task).toLowerCase();
    return haystack.includes(taskQuery.trim().toLowerCase());
  });
  const failedTasks = tasks.filter((task: any) => ["failed", "dead_letter"].includes(task.state) || task.last_error_message);
  const filteredTimeline = timeline.filter((event: any) => timelineFilter === "all" || event.type === timelineFilter);
  const artifactKinds = Array.from(new Set(artifacts.map((artifact: any) => artifact.kind).filter(Boolean)));
  const executionStats = [`tasks ${tasks.length}`, `failed ${failedTasks.length}`, `artifacts ${artifacts.length}`, `timeline ${timeline.length}`];
  const focusedTask = taskFocus ? tasks.find((task: any) => task.id === taskFocus) || null : null;
  const focusedArtifact = artifactFocus ? artifacts.find((artifact: any) => artifact.id === artifactFocus) || null : null;
  const focusedArtifacts = taskFocus ? artifacts.filter((artifact: any) => artifact.task_id === taskFocus) : [];
  const focusedTimeline = taskFocus ? timeline.filter((event: any) => event.task_id === taskFocus) : [];
  const getTaskBody = (task: any) =>
    task.last_error_message ||
    task.summary_json?.message ||
    task.summary_json?.summary ||
    task.last_error_code ||
    formatFallback(task.result_status, "no result");

  return (
    <div className="page-grid">
      <section className="panel">
        <div className="panel-title">Workflows</div>
        <div className="stack">
          {workflows.length ? (
            workflows.map((workflow) => (
              <button
                key={workflow.workflow_id}
                className={`list-card${selected === workflow.workflow_id ? " active" : ""}`}
                onClick={() => setSelected(workflow.workflow_id)}
                type="button"
              >
                <div className="list-title">{workflow.mission_title}</div>
                <div className="list-sub">{formatCompactId(workflow.workflow_id)}</div>
                <div className="list-sub">
                  {workflow.launch_mode} / {workflow.execution_profile} / ok {workflow.succeeded_tasks} / failed {workflow.failed_tasks}
                </div>
              </button>
            ))
          ) : (
            <div className="empty-state">暂无 workflow。</div>
          )}
        </div>
      </section>
      <section className="panel span-2">
        <div className="panel-title">Workflow Detail</div>
        {!detail ? (
          <div className="empty-state">选择一个 workflow。</div>
        ) : (
          <div className="stack">
            <SummaryGroup
              title={detail.workflow.mission_title}
              lines={[
                `${formatCompactId(detail.workflow.workflow_id)} · ${detail.workflow.launch_mode} · ${detail.workflow.execution_profile}`,
                formatFallback(detail.workflow.change_summary, ""),
              ].filter(Boolean)}
              tags={[
                detail.workflow.active_campaign_run_id ? `campaign ${formatCompactId(detail.workflow.active_campaign_run_id)}` : "",
                `tasks ${(detail.tasks || []).length}`,
                `artifacts ${(detail.artifacts || []).length}`,
              ]}
            />
            <div className="button-row">
              {detail.workflow.mission_id ? (
                <a
                  className="button"
                  href={`/?mission=${detail.workflow.mission_id}${detail.workflow.plan_revision_id ? `&revision=${detail.workflow.plan_revision_id}` : ""}`}
                >
                  Open Mission
                </a>
              ) : null}
              {detail.workflow.mission_id && detail.workflow.plan_revision_id ? (
                <a
                  className="button"
                  href={`/?mission=${detail.workflow.mission_id}&revision=${detail.workflow.plan_revision_id}`}
                >
                  Open Revision
                </a>
              ) : null}
              {detail.workflow.active_campaign_run_id ? (
                <a className="button" href={`/campaigns?campaign=${detail.workflow.active_campaign_run_id}`}>Open Campaign</a>
              ) : null}
            </div>
            <div className="stats-strip">
              {executionStats.map((chip) => (
                <div key={chip} className={`status-chip ${getStatusChipToneClass(chip)}`.trim()}>
                  {chip}
                </div>
              ))}
            </div>
            {streamState !== "live" ? (
              <div className="empty-state">
                {streamState === "connecting"
                  ? "实时流连接中。"
                  : streamState === "recovered"
                    ? "实时流已恢复，数据已刷新。"
                    : "实时流重连中，页面会自动恢复。"}
              </div>
            ) : null}
            {focusedTask ? (
              <div className="mini-card">
                <div className="mini-title">Focused Task</div>
                <SummaryGroup
                  title={focusedTask.operation}
                  lines={[
                    `${formatCompactId(focusedTask.id)} / ${formatStateLabel(focusedTask.state)}`,
                    `${formatFallback(focusedTask.capability, "none")} / ${formatFallback(focusedTask.executor_type, "none")} / ${formatFallback(focusedTask.tool_name, "none")}`,
                    getTaskBody(focusedTask),
                  ]}
                  tags={[
                    focusedTask.attempt_outcome || "no-attempt",
                    focusedTask.result_status || "no-result",
                    `artifacts ${focusedArtifacts.length}`,
                    `timeline ${focusedTimeline.length}`,
                  ]}
                />
                {Object.keys(focusedTask.structured_json || {}).length ? (
                  <pre className="code-block top-gap">{JSON.stringify(focusedTask.structured_json, null, 2)}</pre>
                ) : null}
              </div>
            ) : null}
            {focusedArtifact ? (
              <div className="mini-card">
                <div className="mini-title">Focused Artifact</div>
                <SummaryGroup
                  title={formatFallback(artifactDetail?.kind || focusedArtifact.kind, "artifact")}
                  lines={[
                    `${formatCompactId(focusedArtifact.id)} / ${formatCompactId(focusedArtifact.task_id)}`,
                    `${formatFallback(artifactDetail?.mime_type || focusedArtifact.mime_type, "none")} / ${artifactDetail?.size_bytes || focusedArtifact.size_bytes || 0} bytes`,
                    formatTimestamp(artifactDetail?.created_at || focusedArtifact.created_at),
                    artifactDetail?.path || focusedArtifact.path,
                  ]}
                  tags={[
                    formatFallback(artifactDetail?.capability, ""),
                    formatFallback(artifactDetail?.operation, ""),
                    artifactDetail?.result_status || "",
                  ]}
                />
                {artifactDetail?.preview_text ? (
                  <pre className="code-block top-gap">{artifactDetail.preview_text}</pre>
                ) : null}
                <div className="button-row top-gap">
                  {focusedArtifact.task_id ? (
                    <button className="button" type="button" onClick={() => setTaskFocus(focusedArtifact.task_id)}>
                      Focus Related Task
                    </button>
                  ) : null}
                  <button className="button" type="button" onClick={() => setArtifactFocus("")}>
                    Clear Artifact Focus
                  </button>
                </div>
              </div>
            ) : null}
            <div className="dual">
              <div className="mini-card">
                <div className="mini-title">Failure Points</div>
                {failedTasks.length ? (
                  <div className="stack top-gap">
                    {failedTasks.map((task: any) => (
                      <RecordCard
                        key={`failed-${task.id}`}
                        title={`${task.operation} · ${formatStateLabel(task.state)}`}
                        subtitle={`${formatFallback(task.capability, "none")} / ${formatFallback(task.executor_type, "none")} / ${formatFallback(task.tool_name, "none")}`}
                        body={getTaskBody(task)}
                        tags={[
                          "failed",
                          task.attempt_outcome || "no-attempt",
                          task.result_status || "no-result",
                        ]}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">当前 workflow 没有失败节点。</div>
                )}
              </div>
              <div className="mini-card">
                <div className="mini-title">Artifacts</div>
                {artifacts.length ? (
                  <div className="stack top-gap">
                    <div className="tag-row">
                      {artifactKinds.map((kind) => (
                        <span key={kind} className="tag">{kind}</span>
                      ))}
                    </div>
                    {artifacts.slice(0, 12).map((artifact: any) => (
                      <div key={artifact.id}>
                        <RecordCard
                          title={`${formatFallback(artifact.kind, "artifact")} · ${formatCompactId(artifact.task_id)}`}
                          subtitle={`${formatFallback(artifact.mime_type, "none")} / ${artifact.size_bytes || 0} bytes / ${formatTimestamp(artifact.created_at)}`}
                          body={artifact.path}
                          tags={[
                            artifact.id === artifactFocus ? "focused" : "",
                            formatFallback(artifact.kind, "artifact"),
                            formatFallback(artifact.mime_type, "none"),
                          ]}
                        />
                        {artifact.task_id ? (
                          <div className="button-row top-gap">
                            <button className="button" type="button" onClick={() => setTaskFocus(artifact.task_id)}>
                              Focus Task
                            </button>
                            <button className="button" type="button" onClick={() => setArtifactFocus(artifact.id)}>
                              Open Artifact
                            </button>
                          </div>
                        ) : null}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">当前 workflow 还没有 artifacts。</div>
                )}
              </div>
            </div>
            <div className="dual">
              <div>
                <div className="subheading">Tasks</div>
                <div className="filter-row top-gap">
                  <select className="input compact-input" value={taskStateFilter} onChange={(e) => setTaskStateFilter(e.target.value)}>
                    <option value="all">all states</option>
                    <option value="queued">queued</option>
                    <option value="leased">leased</option>
                    <option value="running">running</option>
                    <option value="succeeded">ok</option>
                    <option value="failed">failed</option>
                    <option value="dead_letter">dead</option>
                  </select>
                  <input
                    className="input"
                    value={taskQuery}
                    onChange={(e) => setTaskQuery(e.target.value)}
                    placeholder="Search task, tool, or error"
                  />
                  {taskFocus ? (
                    <button className="button" type="button" onClick={() => setTaskFocus("")}>
                      Clear Task Focus
                    </button>
                  ) : null}
                </div>
                <div className="stack">
                  {filteredTasks.length ? (
                    filteredTasks.map((task: any) => (
                      <RecordCard
                        key={task.id}
                        title={`${task.operation} · ${formatStateLabel(task.state)}`}
                        subtitle={`${formatFallback(task.capability, "none")} / ${formatFallback(task.executor_type, "none")} / ${formatFallback(task.tool_name, "none")}`}
                        body={getTaskBody(task)}
                        tags={[
                          task.id === taskFocus ? "focused" : "",
                          task.attempt_outcome || "no-attempt",
                          task.result_status || "no-result",
                        ]}
                      />
                    ))
                  ) : (
                    <div className="empty-state">当前筛选条件下没有 task。</div>
                  )}
                </div>
              </div>
              <div>
                <div className="subheading">Timeline</div>
                <div className="filter-row top-gap">
                  <select className="input compact-input" value={timelineFilter} onChange={(e) => setTimelineFilter(e.target.value)}>
                    <option value="all">all types</option>
                    <option value="task">task</option>
                    <option value="artifact">artifact</option>
                  </select>
                </div>
                <div className="stack">
                  {filteredTimeline.length ? (
                    filteredTimeline.map((event: any, index: number) => (
                      <div key={`${event.type}-${index}-${event.timestamp || ""}`}>
                        <RecordCard
                          title={formatStateLabel(event.type)}
                          subtitle={formatCompactId(event.task_id || event.operation || event.kind || "event")}
                          body={formatTimestamp(event.timestamp)}
                          tags={[formatStateLabel(event.status || event.kind || "event")]}
                        />
                        {event.task_id ? (
                          <div className="button-row top-gap">
                            <button className="button" type="button" onClick={() => setTaskFocus(event.task_id)}>
                              Focus Task
                            </button>
                          </div>
                        ) : null}
                      </div>
                    ))
                  ) : (
                    <div className="empty-state">当前筛选条件下没有时间线事件。</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
