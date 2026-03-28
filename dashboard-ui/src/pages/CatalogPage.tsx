import { useEffect, useState } from "react";
import { getTools } from "../shared/api/client";
import { RecordCard } from "../components/RecordCard";
import { formatStateLabel } from "../shared/ui/present";

export function CatalogPage() {
  const [tools, setTools] = useState<any[]>([]);

  useEffect(() => {
    getTools().then((items: any) => setTools(items)).catch(console.error);
  }, []);

  return (
    <div className="page-grid">
      <section className="panel span-2">
        <div className="panel-title">Tool Catalog</div>
        <div className="stats-strip">
          <div className="status-chip">tools {tools.length}</div>
        </div>
        <div className="stack">
          {tools.length ? (
            tools.map((tool) => (
              <RecordCard
                key={`${tool.catalog}:${tool.name}`}
                title={tool.name}
                subtitle={`${tool.catalog} / ${tool.category}`}
                body={tool.summary}
                tags={[formatStateLabel(tool.risk_level), tool.category]}
              />
            ))
          ) : (
            <div className="empty-state">暂无工具目录。</div>
          )}
        </div>
      </section>
    </div>
  );
}
