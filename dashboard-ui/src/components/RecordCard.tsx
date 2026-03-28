import { getTagToneClass } from "../shared/ui/present";

export function RecordCard({
  title,
  subtitle,
  body,
  tags,
}: {
  title: string;
  subtitle?: string;
  body?: string;
  tags?: string[];
}) {
  const visibleTags = (tags || []).filter(Boolean);

  return (
    <article className="mini-card">
      <div className="mini-title">{title}</div>
      {subtitle ? <div className="muted card-subtitle">{subtitle}</div> : null}
      {body ? <div className="detail-text">{body}</div> : null}
      {visibleTags.length ? (
        <div className="tag-row">
          {visibleTags.map((tag) => (
            <span key={`${title}-${tag}`} className={`tag ${getTagToneClass(tag)}`.trim()}>
              {tag}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  );
}
