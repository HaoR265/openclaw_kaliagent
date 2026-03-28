import { formatStateLabel } from "../shared/ui/present";

type InsightCard = {
  title: string;
  summary?: string;
  capability?: string;
  tool?: string;
  status?: string;
};

export function InsightSection({
  title,
  cards,
}: {
  title: string;
  cards: InsightCard[];
}) {
  if (!cards.length) {
    return (
      <article className="mini-card">
        <div className="mini-title">{title}</div>
        <div className="empty-state">当前没有可显示内容。</div>
      </article>
    );
  }

  return (
    <article className="mini-card">
      <div className="mini-title">{title}</div>
      <div className="stack">
        {cards.map((card, index) => (
          <div key={`${card.title}-${index}`} className="mini-card nested-card">
            <div className="mini-title">{card.title}</div>
            {card.capability || card.tool || card.status ? (
              <div className="muted">
                {[card.capability, card.tool, card.status ? formatStateLabel(card.status) : null].filter(Boolean).join(" / ")}
              </div>
            ) : null}
            {card.summary ? <div className="detail-text">{card.summary}</div> : null}
          </div>
        ))}
      </div>
    </article>
  );
}
