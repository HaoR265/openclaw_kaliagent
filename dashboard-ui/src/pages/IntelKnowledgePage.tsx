import { useEffect, useState } from "react";
import { RecordCard } from "../components/RecordCard";
import { searchIntel, searchKnowledge } from "../shared/api/client";
import { formatFallback, formatStateLabel, getStatusChipToneClass, getTagToneClass } from "../shared/ui/present";

export function IntelKnowledgePage() {
  const [query, setQuery] = useState(() => new URLSearchParams(window.location.search).get("query") || localStorage.getItem("intel:query") || "");
  const [capability, setCapability] = useState(() => new URLSearchParams(window.location.search).get("capability") || localStorage.getItem("intel:capability") || "");
  const [intel, setIntel] = useState<any[]>([]);
  const [knowledge, setKnowledge] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      searchIntel({ q: query, capability: capability || undefined }),
      searchKnowledge({ q: query, capability: capability || undefined }),
    ])
      .then(([intelRes, knowledgeRes]) => {
        setIntel(intelRes.items || []);
        setKnowledge(knowledgeRes.items || []);
      })
      .catch(console.error);
  }, [query, capability]);

  useEffect(() => {
    localStorage.setItem("intel:query", query);
    const url = new URL(window.location.href);
    if (query.trim()) {
      url.searchParams.set("query", query);
    } else {
      url.searchParams.delete("query");
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}`);
  }, [query]);

  useEffect(() => {
    localStorage.setItem("intel:capability", capability);
    const url = new URL(window.location.href);
    if (capability) {
      url.searchParams.set("capability", capability);
    } else {
      url.searchParams.delete("capability");
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}`);
  }, [capability]);

  return (
    <div className="page-grid">
      <section className="panel span-2">
        <div className="panel-title">Intel / Knowledge</div>
        <div className="filter-row">
          <input
            className="input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search intel or knowledge"
          />
          <select className="input compact-input" value={capability} onChange={(e) => setCapability(e.target.value)}>
            <option value="">全部能力</option>
            <option value="wireless">wireless</option>
            <option value="recon">recon</option>
            <option value="web">web</option>
            <option value="internal">internal</option>
            <option value="exploit">exploit</option>
            <option value="social">social</option>
          </select>
        </div>
        <div className="stats-strip">
          <div className={`status-chip ${getStatusChipToneClass(`intel ${intel.length}`)}`.trim()}>intel {intel.length}</div>
          <div className={`status-chip ${getStatusChipToneClass(`knowledge ${knowledge.length}`)}`.trim()}>knowledge {knowledge.length}</div>
          {capability ? <div className={`status-chip ${getTagToneClass(capability)}`.trim()}>{capability}</div> : null}
        </div>
      </section>
      <section className="panel">
        <div className="panel-title">Intel</div>
        <div className="stack">
          {intel.length ? (
            intel.map((item) => (
              <RecordCard
                key={item.id}
                title={item.title}
                subtitle={`${formatFallback(item.capability, "none")} / ${formatStateLabel(item.validated_status)}`}
                body={item.summary}
                tags={[item.confidence_level, formatStateLabel(item.validated_status)]}
              />
            ))
          ) : (
            <div className="empty-state">暂无 intel 结果。</div>
          )}
        </div>
      </section>
      <section className="panel">
        <div className="panel-title">Knowledge</div>
        <div className="stack">
          {knowledge.length ? (
            knowledge.map((item) => (
              <RecordCard
                key={item.id}
                title={item.title}
                subtitle={`${formatFallback(item.capability, "none")} / ${formatStateLabel(item.validated_status)}`}
                body={item.summary}
                tags={[item.confidence_level, formatStateLabel(item.validated_status)]}
              />
            ))
          ) : (
            <div className="empty-state">暂无 knowledge 结果。</div>
          )}
        </div>
      </section>
    </div>
  );
}
