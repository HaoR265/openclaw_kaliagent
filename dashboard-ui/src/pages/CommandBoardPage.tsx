import { useEffect, useState } from "react";
import {
  getCampaignEvents,
  getCommandBoardInsights,
  getMission,
  listMissions,
  searchIntel,
  searchKnowledge,
} from "../shared/api/client";
import { InsightSection } from "../components/InsightSection";
import { SummaryGroup } from "../components/SummaryGroup";
import { openStream } from "../shared/api/stream";
import type { Mission } from "../shared/types/control";
import { formatCompactId, formatFallback, formatStateLabel, formatTimestamp, getStatusChipToneClass, getTagToneClass } from "../shared/ui/present";

export function CommandBoardPage() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selected, setSelected] = useState<string>(() => new URLSearchParams(window.location.search).get("mission") || localStorage.getItem("command:selectedMission") || "");
  const [detail, setDetail] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [insights, setInsights] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState(() => new URLSearchParams(window.location.search).get("query") || localStorage.getItem("command:searchQuery") || "");
  const [lookup, setLookup] = useState<{ intel: any[]; knowledge: any[] }>({ intel: [], knowledge: [] });
  const [layoutMode, setLayoutMode] = useState<"dual" | "stack">(() => {
    const queryMode = new URLSearchParams(window.location.search).get("layout");
    return queryMode === "stack" || queryMode === "dual"
      ? queryMode
      : ((localStorage.getItem("command:layoutMode") as "dual" | "stack") || "dual");
  });
  const [insightFilter, setInsightFilter] = useState(() => new URLSearchParams(window.location.search).get("filter") || localStorage.getItem("command:insightFilter") || "all");
  const [streamState, setStreamState] = useState<"connecting" | "live" | "reconnecting" | "recovered">("connecting");

  async function refreshMissions() {
    const items = await listMissions();
    setMissions(items);
    if (!selected && items[0]?.id) {
      setSelected(items[0].id);
    } else if (selected && !items.some((item) => item.id === selected) && items[0]?.id) {
      setSelected(items[0].id);
    }
  }

  useEffect(() => {
    refreshMissions().catch(console.error);
  }, []);

  useEffect(() => {
    if (selected) {
      localStorage.setItem("command:selectedMission", selected);
      const url = new URL(window.location.href);
      url.searchParams.set("mission", selected);
      window.history.replaceState({}, "", `${url.pathname}${url.search}`);
    }
  }, [selected]);

  useEffect(() => {
    localStorage.setItem("command:searchQuery", searchQuery);
    const url = new URL(window.location.href);
    if (searchQuery.trim()) {
      url.searchParams.set("query", searchQuery);
    } else {
      url.searchParams.delete("query");
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}`);
  }, [searchQuery]);

  useEffect(() => {
    localStorage.setItem("command:layoutMode", layoutMode);
    const url = new URL(window.location.href);
    url.searchParams.set("layout", layoutMode);
    window.history.replaceState({}, "", `${url.pathname}${url.search}`);
  }, [layoutMode]);

  useEffect(() => {
    localStorage.setItem("command:insightFilter", insightFilter);
    const url = new URL(window.location.href);
    if (insightFilter !== "all") {
      url.searchParams.set("filter", insightFilter);
    } else {
      url.searchParams.delete("filter");
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}`);
  }, [insightFilter]);

  useEffect(() => {
    if (!selected) return;
    getMission(selected)
      .then(async (item) => {
        setDetail(item);
        const campaignId = item.campaigns?.[0]?.id;
        if (campaignId) {
          setEvents(await getCampaignEvents(campaignId));
        } else {
          setEvents([]);
        }
        setInsights(await getCommandBoardInsights(selected));
        const capability = item.revisions?.[0]?.task_tree_json?.[0]?.category || undefined;
        const [intel, knowledge] = await Promise.all([
          searchIntel({ q: "", capability }),
          searchKnowledge({ q: "", capability }),
        ]);
        setLookup({ intel: intel.items || [], knowledge: knowledge.items || [] });
      })
      .catch(console.error);
  }, [selected]);

  useEffect(() => {
    if (!selected) return;
    const timer = window.setInterval(() => {
      refreshMissions().catch(() => undefined);
      getMission(selected)
        .then(async (item) => {
          setDetail(item);
          const campaignId = item.campaigns?.[0]?.id;
          if (campaignId) {
            setEvents(await getCampaignEvents(campaignId));
          } else {
            setEvents([]);
          }
          const capability = item.revisions?.[0]?.task_tree_json?.[0]?.category || undefined;
          const [intel, knowledge] = await Promise.all([
            searchIntel({ q: searchQuery, capability }),
            searchKnowledge({ q: searchQuery, capability }),
          ]);
          setLookup({ intel: intel.items || [], knowledge: knowledge.items || [] });
        })
        .catch(() => undefined);
    }, 15000);
    const source = openStream({ missionId: selected }, async (payload) => {
      setDetail(payload);
      const campaignId = payload.campaigns?.[0]?.id;
      if (campaignId) {
        setEvents(await getCampaignEvents(campaignId));
      }
      setInsights(await getCommandBoardInsights(selected));
      const capability = payload.revisions?.[0]?.task_tree_json?.[0]?.category || undefined;
      const [intel, knowledge] = await Promise.all([
        searchIntel({ q: searchQuery, capability }),
        searchKnowledge({ q: searchQuery, capability }),
      ]);
      setLookup({ intel: intel.items || [], knowledge: knowledge.items || [] });
    }, {
      onStatus: setStreamState,
    });
    return () => {
      window.clearInterval(timer);
      source.close();
    };
  }, [selected]);

  useEffect(() => {
    if (!selected || !detail) return;
    const capability = detail.revisions?.[0]?.task_tree_json?.[0]?.category || undefined;
    Promise.all([
      searchIntel({ q: searchQuery, capability }),
      searchKnowledge({ q: searchQuery, capability }),
    ])
      .then(([intel, knowledge]) => {
        setLookup({ intel: intel.items || [], knowledge: knowledge.items || [] });
      })
      .catch(console.error);
  }, [selected, searchQuery, detail]);

  const filteredKnowledgeCards =
    insightFilter === "all" || insightFilter === "knowledge" ? insights?.knowledge_cards || [] : [];
  const filteredIntelCards =
    insightFilter === "all" || insightFilter === "intel" ? insights?.intel_cards || [] : [];
  const filteredRiskCards =
    insightFilter === "all" || insightFilter === "risk" ? insights?.risk_cards || [] : [];
  const filteredFailureCards =
    insightFilter === "all" || insightFilter === "failure" ? insights?.failure_cards || [] : [];
  const analystWarnings = (detail?.analysis_jobs || []).flatMap((job: any) => job.warning_refs_json || []);
  const latestCampaignEvents = events.slice(0, 6);
  const runtimeKnowledge = (lookup.knowledge || []).filter((item: any) => item.validated_status === "runtime-derived" || item.entry_type === "runtime-result");
  const runtimeIntel = (lookup.intel || []).filter((item: any) => item.validated_status === "runtime-derived" || item.source_type === "runtime-result");
  const runtimeCards = insights?.runtime_cards || [];
  const commanderStats = detail
    ? [
        `plans ${(detail.plans || []).length}`,
        `revisions ${(detail.revisions || []).length}`,
        `analysis ${(detail.analysis_jobs || []).length}`,
        `events ${events.length}`,
        `runtime ${runtimeKnowledge.length + runtimeIntel.length}`,
      ]
    : [];

  return (
    <div className="page-grid">
      <section className="panel span-2">
        <div className="panel-title">Mission Focus</div>
        <div className="filter-row">
          <button
            type="button"
            className={`chip${layoutMode === "dual" ? " active" : ""}`}
            onClick={() => setLayoutMode("dual")}
          >
            dual
          </button>
          <button
            type="button"
            className={`chip${layoutMode === "stack" ? " active" : ""}`}
            onClick={() => setLayoutMode("stack")}
          >
            stack
          </button>
          <select className="input compact-input" value={insightFilter} onChange={(e) => setInsightFilter(e.target.value)}>
            <option value="all">all types</option>
            <option value="knowledge">knowledge</option>
            <option value="intel">intel</option>
            <option value="risk">risk</option>
            <option value="failure">failure</option>
          </select>
        </div>
        <div className="mission-chip-row">
          {missions.slice(0, 8).map((mission) => (
            <button
              key={mission.id}
              type="button"
              className={`chip${selected === mission.id ? " active" : ""}`}
              onClick={() => setSelected(mission.id)}
            >
              {mission.title}
            </button>
          ))}
        </div>
      </section>
      <section className={`panel${layoutMode === "stack" ? " span-2" : ""}`}>
        <div className="panel-title">Commander</div>
        {!detail ? (
          <div className="empty-state">选择 Mission。</div>
        ) : (
          <div className="stack">
            <div className="summary-card">
              <div className="summary-title">{detail.mission.title}</div>
              <div className="muted">{detail.mission.objective_text}</div>
            </div>
            <SummaryGroup
              title="Current State"
              lines={[
                `mission ${formatStateLabel(detail.mission.status)}`,
                `latest workflow ${formatCompactId(detail.mission.latest_workflow_id)}`,
                `active campaign ${formatCompactId(detail.mission.active_campaign_run_id)}`,
              ]}
            />
            {streamState !== "live" ? (
              <div className="empty-state">
                {streamState === "connecting"
                  ? "实时流连接中。"
                  : streamState === "recovered"
                    ? "实时流已恢复，数据已刷新。"
                    : "实时流重连中，页面会自动恢复。"}
              </div>
            ) : null}
            {detail.campaigns?.[0] ? (
              <SummaryGroup
                title="Authorization Snapshot"
                tags={[
                  detail.campaigns[0].status,
                  detail.campaigns[0].execution_profile,
                  `parallel ${detail.campaigns[0].max_parallelism}`,
                ]}
              />
            ) : null}
            {insights?.current_plan ? (
              <SummaryGroup
                title="Current Plan"
                lines={[
                  formatFallback(insights.current_plan.title),
                  formatFallback(insights.current_plan.goal_summary, ""),
                  formatFallback(insights.current_plan.discussion_summary, ""),
                ].filter(Boolean)}
              />
            ) : null}
            {insights?.current_revision ? (
              <SummaryGroup
                title="Current Revision"
                lines={[
                  `${formatCompactId(insights.current_revision.id)} / rev ${insights.current_revision.revision_no}`,
                  formatFallback(insights.current_revision.change_summary, ""),
                ].filter(Boolean)}
                tags={[
                  insights.current_revision.branch_key,
                  `tasks ${insights.current_revision.task_count}`,
                  insights.current_revision.launchable ? "launchable" : "draft",
                ]}
              />
            ) : null}
            {insights?.current_workflow ? (
              <SummaryGroup
                title="Current Workflow"
                lines={[
                  formatCompactId(insights.current_workflow.id),
                  `${formatFallback(insights.current_workflow.launch_mode)} / ${formatFallback(insights.current_workflow.execution_profile)}`,
                ]}
                tags={[
                  `tasks ${insights.current_workflow.task_count}`,
                  `artifacts ${insights.current_workflow.artifact_count}`,
                ]}
              />
            ) : null}
            <div className="stats-strip">
              {commanderStats.map((chip) => (
                <div key={chip} className={`status-chip ${getStatusChipToneClass(chip)}`.trim()}>
                  {chip}
                </div>
              ))}
            </div>
            {(detail.plans || []).length ? (
              (detail.plans || []).map((plan: any) => (
                <article className="mini-card" key={plan.id}>
                  <div className="mini-title">{plan.title}</div>
                  <div className="muted">{plan.goal_summary}</div>
                  <div className="detail-text">{plan.discussion_summary}</div>
                </article>
              ))
            ) : (
              <div className="empty-state">暂无方案候选。</div>
            )}
          </div>
        )}
      </section>
      <section className={`panel${layoutMode === "stack" ? " span-2" : ""}`}>
        <div className="panel-title">Analyst</div>
        {!detail ? (
          <div className="empty-state">等待 Mission。</div>
        ) : (
          <div className="stack">
            <div className="summary-card">
              <div className="mini-title">Lookup</div>
              <input
                className="input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search intel or knowledge"
              />
            </div>
            <div className="dual">
              <SummaryGroup
                title="Analyst Status"
                lines={[
                  `${(detail.analysis_jobs || []).length} jobs`,
                  analystWarnings.length ? `${analystWarnings.length} warnings` : "no warnings",
                ]}
                tags={[
                  latestCampaignEvents.length ? `events ${latestCampaignEvents.length}` : "no-campaign-feed",
                ]}
              />
              <SummaryGroup
                title="Card Filter"
                lines={[
                  `knowledge ${filteredKnowledgeCards.length}`,
                  `intel ${filteredIntelCards.length}`,
                  `risk ${filteredRiskCards.length}`,
                  `failure ${filteredFailureCards.length}`,
                ]}
                tags={[insightFilter]}
              />
            </div>
            <SummaryGroup
              title="Runtime Memory"
              lines={[
                `workflow hits ${runtimeCards.length}`,
                `knowledge ${runtimeKnowledge.length}`,
                `intel ${runtimeIntel.length}`,
              ]}
              tags={[
                runtimeKnowledge.length || runtimeIntel.length ? "runtime-derived" : "empty",
              ]}
            />
            {(detail.analysis_jobs || []).length ? (
              (detail.analysis_jobs || []).map((job: any) => (
                <article className="mini-card" key={job.id}>
                  <div className="mini-title">{job.job_kind} · {formatStateLabel(job.status)}</div>
                  <div className="muted">{job.query_text}</div>
                  {job.output_summary ? <div className="detail-text">{job.output_summary}</div> : null}
                  {(job.warning_refs_json || []).length ? (
                    <div className="tag-row">
                      {(job.warning_refs_json || []).map((warning: string) => (
                        <span key={warning} className={`tag ${getTagToneClass(warning)}`.trim()}>{warning}</span>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))
            ) : (
              <div className="empty-state">暂无 analyst 输出。</div>
            )}
            {events.length ? (
              <article className="mini-card">
                <div className="mini-title">Campaign Feed</div>
                <div className="stack">
                  {latestCampaignEvents.map((event: any) => (
                    <div className="muted" key={event.id}>
                      {formatTimestamp(event.created_at)} · {formatStateLabel(event.event_type)} · {event.message}
                    </div>
                  ))}
                </div>
              </article>
            ) : (
              <div className="empty-state">暂无 campaign feed。</div>
            )}
            {insights ? <InsightSection title="Knowledge Cards" cards={filteredKnowledgeCards} /> : null}
            {insights ? <InsightSection title="Intel Cards" cards={filteredIntelCards} /> : null}
            {insights ? <InsightSection title="Risk Cards" cards={filteredRiskCards} /> : null}
            {insights ? <InsightSection title="Recent Failure Points" cards={filteredFailureCards} /> : null}
            <InsightSection title="Current Workflow Runtime" cards={runtimeCards} />
            <InsightSection title="Runtime Knowledge" cards={runtimeKnowledge} />
            <InsightSection title="Runtime Intel" cards={runtimeIntel} />
            <InsightSection title="Knowledge Search" cards={lookup.knowledge || []} />
            <InsightSection title="Intel Search" cards={lookup.intel || []} />
          </div>
        )}
      </section>
    </div>
  );
}
