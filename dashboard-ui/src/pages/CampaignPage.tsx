import { useEffect, useState } from "react";
import { controlCampaign } from "../shared/api/client";
import { openStream } from "../shared/api/stream";
import { SummaryGroup } from "../components/SummaryGroup";
import { formatCompactId, formatFallback, formatStateLabel, formatTimestamp, getStatusChipToneClass, getTagToneClass } from "../shared/ui/present";

async function listCampaigns() {
  const res = await fetch("/api/campaigns?limit=20");
  if (!res.ok) throw new Error("failed to load campaigns");
  return res.json();
}

async function getCampaign(campaignId: string) {
  const res = await fetch(`/api/campaigns/${campaignId}`);
  if (!res.ok) throw new Error("failed to load campaign");
  return res.json();
}

export function CampaignPage() {
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [selected, setSelected] = useState(() => new URLSearchParams(window.location.search).get("campaign") || localStorage.getItem("campaign:selected") || "");
  const [detail, setDetail] = useState<any>(null);
  const [severityFilter, setSeverityFilter] = useState(() => localStorage.getItem("campaign:severity") || "all");
  const [eventQuery, setEventQuery] = useState(() => localStorage.getItem("campaign:query") || "");
  const [busy, setBusy] = useState(false);
  const [controlError, setControlError] = useState("");
  const [streamState, setStreamState] = useState<"connecting" | "live" | "reconnecting" | "recovered">("connecting");

  useEffect(() => {
    listCampaigns()
      .then((items) => {
        setCampaigns(items);
        if (!selected && items[0]?.id) {
          setSelected(items[0].id);
        } else if (selected && !items.some((item: any) => item.id === selected) && items[0]?.id) {
          setSelected(items[0].id);
        }
      })
      .catch(console.error);
  }, [selected]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      listCampaigns().then(setCampaigns).catch(() => undefined);
    }, 15000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (selected) {
      localStorage.setItem("campaign:selected", selected);
      const url = new URL(window.location.href);
      url.searchParams.set("campaign", selected);
      window.history.replaceState({}, "", `${url.pathname}${url.search}`);
    }
  }, [selected]);

  useEffect(() => {
    localStorage.setItem("campaign:severity", severityFilter);
  }, [severityFilter]);

  useEffect(() => {
    localStorage.setItem("campaign:query", eventQuery);
  }, [eventQuery]);

  useEffect(() => {
    if (!selected) return;
    getCampaign(selected).then(setDetail).catch(console.error);
    const source = openStream({ campaignId: selected }, (payload) => setDetail(payload), {
      onStatus: setStreamState,
    });
    return () => source.close();
  }, [selected]);

  async function onControl(action: string) {
    if (!selected) return;
    setBusy(true);
    setControlError("");
    try {
      await controlCampaign(selected, action);
      setDetail(await getCampaign(selected));
      setCampaigns(await listCampaigns());
    } catch (error) {
      setControlError(error instanceof Error ? error.message : "control failed");
    } finally {
      setBusy(false);
    }
  }

  const events = detail?.events || [];
  const warningCount = events.filter((event: any) => event.severity === "warning").length;
  const errorCount = events.filter((event: any) => event.severity === "error").length;
  const infoCount = events.filter((event: any) => event.severity === "info").length;
  const toolUsage = Array.from(
    new Set(
      events
        .map((event: any) => event.payload_json?.tool_name || event.payload_json?.tool || event.related_task_id)
        .filter(Boolean),
    ),
  );
  const filteredEvents = events.filter((event: any) => {
    if (severityFilter !== "all" && event.severity !== severityFilter) {
      return false;
    }
    if (!eventQuery.trim()) {
      return true;
    }
    const haystack = JSON.stringify(event).toLowerCase();
    return haystack.includes(eventQuery.trim().toLowerCase());
  });
  const blockedReasons = events
    .filter((event: any) => event.severity === "warning" || event.severity === "error")
    .slice(0, 6)
    .map((event: any) => event.message);
  const recentReplans = events
    .filter((event: any) => {
      const text = `${event.event_type} ${event.message}`.toLowerCase();
      return text.includes("replan") || text.includes("revision") || text.includes("branch");
    })
    .slice(0, 5);
  const interactiveSessions = events
    .filter((event: any) => {
      const payload = event.payload_json || {};
      return Boolean(payload.session_id || payload.transcript_id || payload.interactive || payload.tty);
    })
    .slice(0, 5);
  const latestControlEvent = events.find((event: any) => event.event_type?.endsWith("_requested"));
  const activeSteps = (detail?.campaign?.task_tree_json || []).map((task: any, index: number) => ({
    id: `${index}-${task.task || task.operation || "step"}`,
    label: `${index + 1}. ${task.task || task.operation || "step"}`,
    capability: task.category || task.capability || "none",
    notes: task.notes || "",
    executionMode: task.params?.executionMode || "agent_api",
    interactive: Boolean(task.params?.interactive),
    secondaryConfirmation: Boolean(task.params?.secondaryConfirmation),
  }));
  const campaignStats = [
    `events ${events.length}`,
    `visible ${filteredEvents.length}`,
    `tools ${toolUsage.length}`,
    `replans ${recentReplans.length}`,
    `interactive ${interactiveSessions.length}`,
  ];

  return (
    <div className="page-grid">
      <section className="panel">
        <div className="panel-title">Campaigns</div>
        <div className="stack">
          {campaigns.length ? (
            campaigns.map((campaign) => (
              <button
                key={campaign.id}
                className={`list-card${selected === campaign.id ? " active" : ""}`}
                onClick={() => setSelected(campaign.id)}
                type="button"
              >
                <div className="list-title">{campaign.mission_title}</div>
                <div className="list-sub">{formatCompactId(campaign.id)}</div>
                <div className="list-sub">{formatStateLabel(campaign.status)} / {campaign.execution_profile}</div>
              </button>
            ))
          ) : (
            <div className="empty-state">暂无 campaign。</div>
          )}
        </div>
      </section>
      <section className="panel span-2">
        <div className="panel-title">Campaign Detail</div>
        {!detail ? (
          <div className="empty-state">选择一个 campaign。</div>
        ) : (
          <div className="stack">
            <div className="summary-card">
              <div className="summary-title">{detail.campaign.mission_title}</div>
              <div className="muted">{detail.campaign.objective_text}</div>
              <div className="muted">
                {formatStateLabel(detail.campaign.status)} / {detail.campaign.execution_profile} / parallel {detail.campaign.max_parallelism}
              </div>
              <div className="tag-row">
                <span className={`tag ${getTagToneClass(detail.campaign.status)}`.trim()}>{formatStateLabel(detail.campaign.status)}</span>
                <span className="tag">{detail.campaign.scope_name}</span>
                <span className="tag">auto-replan {detail.campaign.auto_replan_enabled ? "on" : "off"}</span>
              </div>
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
            <div className="dual">
              <SummaryGroup
                title="Route"
                lines={[
                  `revision ${formatCompactId(detail.campaign.plan_revision_id)} / ${formatFallback(detail.campaign.branch_key)} / rev ${detail.campaign.revision_no}`,
                  formatFallback(detail.campaign.revision_change_summary, "no revision summary"),
                ]}
                tags={[
                  detail.campaign.execution_profile,
                  `parallel ${detail.campaign.max_parallelism}`,
                  formatStateLabel(detail.campaign.status),
                ]}
              />
              <SummaryGroup
                title="Latest Control"
                lines={
                  latestControlEvent
                    ? [
                        `${formatStateLabel(latestControlEvent.payload_json?.action || latestControlEvent.event_type)} · ${formatTimestamp(latestControlEvent.created_at)}`,
                        `${formatFallback(latestControlEvent.payload_json?.from_status, "none")} -> ${formatFallback(latestControlEvent.payload_json?.to_status, "none")}`,
                      ]
                    : ["no control action yet"]
                }
                tags={[
                  latestControlEvent ? formatStateLabel(latestControlEvent.severity) : "idle",
                  latestControlEvent ? formatStateLabel(latestControlEvent.payload_json?.to_status || detail.campaign.status) : "",
                  ...(detail.campaign.available_actions || []).slice(0, 3),
                ]}
              />
            </div>
            <div className="dual">
              <SummaryGroup
                title="Event Snapshot"
                lines={[
                  `recent ${events.length} events`,
                  `info ${infoCount} / warning ${warningCount} / error ${errorCount}`,
                ]}
                tags={[
                  detail.campaign.status,
                  detail.campaign.auto_replan_enabled ? "auto-replan on" : "auto-replan off",
                ]}
              />
              <div className="mini-card">
                <div className="mini-title">Approval Scope</div>
                <div className="tag-row">
                  {(detail.campaign.allowed_categories_json || []).map((item: string) => (
                    <span key={item} className="tag">{item}</span>
                  ))}
                </div>
                <div className="stack top-gap">
                  <div>
                    <div className="subheading">Allowed Tools</div>
                    {(detail.campaign.allowed_tools_json || []).length ? (
                      <div className="tag-row">
                        {(detail.campaign.allowed_tools_json || []).map((tool: string) => (
                          <span key={tool} className="tag">{tool}</span>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-state">未限制到具体工具。</div>
                    )}
                  </div>
                  <div>
                    <div className="subheading">Denied Tools</div>
                    {(detail.campaign.denied_tools_json || []).length ? (
                      <div className="tag-row">
                        {(detail.campaign.denied_tools_json || []).map((tool: string) => (
                          <span key={tool} className={`tag ${getTagToneClass(`warning ${tool}`)}`.trim()}>{tool}</span>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-state">当前没有显式 deny 列表。</div>
                    )}
                  </div>
                </div>
              </div>
              <div className="mini-card">
                <div className="mini-title">Risk / Interactive</div>
                <div className="stack">
                  <div>
                    <div className="subheading">High Risk Tools</div>
                    {(detail.campaign.high_risk_tools_json || []).length ? (
                      <div className="tag-row">
                        {(detail.campaign.high_risk_tools_json || []).map((tool: string) => (
                          <span key={tool} className={`tag ${getTagToneClass(`high-risk ${tool}`)}`.trim()}>{tool}</span>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-state">当前没有高风险工具授权。</div>
                    )}
                  </div>
                  <div>
                    <div className="subheading">Interactive Tools</div>
                    {(detail.campaign.interactive_tools_json || []).length ? (
                      <div className="tag-row">
                        {(detail.campaign.interactive_tools_json || []).map((tool: string) => (
                          <span key={tool} className="tag">{tool}</span>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-state">当前没有交互式工具授权。</div>
                    )}
                  </div>
                  <div>
                    <div className="subheading">Network Scope</div>
                    {Object.keys(detail.campaign.network_scope_json || {}).length ? (
                      <pre className="code-block">{JSON.stringify(detail.campaign.network_scope_json, null, 2)}</pre>
                    ) : (
                      <div className="empty-state">当前没有额外网络范围约束。</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <div className="mini-card">
              <div className="mini-title">Tool Usage Summary</div>
              {toolUsage.length ? (
                <div className="tag-row">
                  {toolUsage.map((tool) => (
                    <span key={tool} className="tag">{tool}</span>
                  ))}
                </div>
              ) : (
                <div className="empty-state">最近事件里还没有明确工具使用记录。</div>
              )}
            </div>
            <div className="stats-strip">
              {campaignStats.map((chip) => (
                <div key={chip} className={`status-chip ${getStatusChipToneClass(chip)}`.trim()}>
                  {chip}
                </div>
              ))}
            </div>
            <div className="dual">
              <div className="mini-card">
                <div className="mini-title">Active Steps</div>
                {activeSteps.length ? (
                  <div className="stack top-gap">
                    {activeSteps.map((step) => (
                      <div className="mini-card nested-card" key={step.id}>
                        <div className="mini-title">{step.label}</div>
                        <div className="muted">{step.capability} / {step.executionMode}</div>
                        {step.notes ? <div className="detail-text">{step.notes}</div> : null}
                        <div className="tag-row">
                          {step.interactive ? <span className="tag">interactive</span> : null}
                          {step.secondaryConfirmation ? <span className={`tag ${getTagToneClass("secondary-confirmation")}`.trim()}>secondary-confirmation</span> : null}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">当前 revision 还没有 task tree。</div>
                )}
              </div>
              <div className="mini-card">
                <div className="mini-title">Blocked Reasons</div>
                {detail.campaign.scope_issues?.length ? (
                  <div className="tag-row top-gap">
                    {detail.campaign.scope_issues.slice(0, 4).map((issue: string) => (
                      <span key={issue} className="tag danger">{issue}</span>
                    ))}
                  </div>
                ) : null}
                {blockedReasons.length ? (
                  <div className="stack top-gap">
                    {blockedReasons.map((reason: string, index: number) => (
                      <div className="mini-card nested-card" key={`${reason}-${index}`}>
                        <div className="muted">{reason}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">最近事件里没有明显的阻塞或风险提示。</div>
                )}
              </div>
            </div>
            <div className="dual">
              <div className="mini-card">
                <div className="mini-title">Recent Replans</div>
                {recentReplans.length ? (
                  <div className="stack top-gap">
                    {recentReplans.map((event: any) => (
                      <div className="mini-card nested-card" key={`replan-${event.id}`}>
                        <div className="mini-title">{event.event_type}</div>
                        <div className="muted">{event.message}</div>
                        <div className="muted">{formatTimestamp(event.created_at)}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">最近没有检测到重规划或 revision 变更事件。</div>
                )}
              </div>
              <div className="mini-card">
                <div className="mini-title">Interactive Sessions</div>
                {interactiveSessions.length ? (
                  <div className="stack top-gap">
                    {interactiveSessions.map((event: any) => (
                      <div className="mini-card nested-card" key={`interactive-${event.id}`}>
                        <div className="mini-title">{event.event_type}</div>
                        <div className="muted">{event.message}</div>
                        {Object.keys(event.payload_json || {}).length ? (
                          <pre className="code-block">{JSON.stringify(event.payload_json, null, 2)}</pre>
                        ) : null}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">当前没有检测到活跃或最近的交互式会话。</div>
                )}
              </div>
            </div>
            <div className="button-row">
              {detail.campaign.mission_session_id ? (
                <a
                  className="button"
                  href={`/?mission=${detail.campaign.mission_session_id}&revision=${detail.campaign.plan_revision_id}`}
                >
                  Open Revision
                </a>
              ) : null}
              {detail.campaign.latest_workflow_id ? (
                <a className="button" href={`/execution?workflow=${detail.campaign.latest_workflow_id}`}>
                  Open Workflow
                </a>
              ) : null}
              {detail.campaign.status === "under_review" ? (
                <button className="button primary" type="button" disabled={busy || !detail.campaign.available_actions?.includes("approve")} onClick={() => onControl("approve")}>Approve</button>
              ) : null}
              {detail.campaign.status === "under_review" ? (
                <button className="button" type="button" disabled={busy || !detail.campaign.available_actions?.includes("reject")} onClick={() => onControl("reject")}>Reject</button>
              ) : null}
              <button className="button" type="button" disabled={busy || !detail.campaign.available_actions?.includes("pause")} onClick={() => onControl("pause")}>Pause</button>
              <button className="button" type="button" disabled={busy || !detail.campaign.available_actions?.includes("resume")} onClick={() => onControl("resume")}>Resume</button>
              <button className="button" type="button" disabled={busy || !detail.campaign.available_actions?.includes("drain")} onClick={() => onControl("drain")}>Drain</button>
              <button className="button" type="button" disabled={busy || !detail.campaign.available_actions?.includes("stop")} onClick={() => onControl("stop")}>Stop</button>
              <button className="button" type="button" disabled={busy || !detail.campaign.available_actions?.includes("kill")} onClick={() => onControl("kill")}>Kill</button>
            </div>
            {controlError ? <div className="empty-state">{controlError}</div> : null}
            <div>
              <div className="subheading">Event Feed</div>
              <div className="filter-row top-gap">
                <select className="input compact-input" value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
                  <option value="all">all severities</option>
                  <option value="info">info</option>
                  <option value="warning">warning</option>
                  <option value="error">error</option>
                </select>
                <input
                  className="input"
                  value={eventQuery}
                  onChange={(e) => setEventQuery(e.target.value)}
                  placeholder="Search event, tool, or reason"
                />
              </div>
              <div className="stack">
                {filteredEvents.length ? (
                  filteredEvents.map((event: any) => (
                    <article className="mini-card" key={event.id}>
                      <div className="mini-title">{formatStateLabel(event.event_type)} · {formatStateLabel(event.severity)}</div>
                      <div className="muted">{formatTimestamp(event.created_at)}</div>
                      <div className="muted">{event.message}</div>
                      {event.related_task_id ? <div className="list-sub">task {formatCompactId(event.related_task_id)}</div> : null}
                      {Object.keys(event.payload_json || {}).length ? (
                        <pre className="code-block">{JSON.stringify(event.payload_json, null, 2)}</pre>
                      ) : null}
                    </article>
                  ))
                ) : (
                  <div className="empty-state">当前筛选条件下没有事件。</div>
                )}
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
