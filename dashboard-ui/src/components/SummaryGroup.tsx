import { getTagToneClass } from "../shared/ui/present";

export function SummaryGroup({
  title,
  lines,
  tags,
}: {
  title: string;
  lines?: string[];
  tags?: string[];
}) {
  const visibleLines = (lines || []).filter(Boolean);
  const visibleTags = (tags || []).filter(Boolean);

  return (
    <div className="summary-card">
      <div className="mini-title">{title}</div>
      {visibleLines.map((line, index) => (
        <div className="muted card-line" key={`${title}-${index}`}>
          {line}
        </div>
      ))}
      {visibleTags.length ? (
        <div className="tag-row">
          {visibleTags.map((tag) => (
            <span key={`${title}-${tag}`} className={`tag ${getTagToneClass(tag)}`.trim()}>
              {tag}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}
