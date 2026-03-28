const STATE_LABELS: Record<string, string> = {
  queued: "queued",
  leased: "leased",
  running: "running",
  succeeded: "ok",
  failed: "failed",
  dead_letter: "dead",
  canceled: "canceled",
  paused: "paused",
  draining: "draining",
  stopped: "stopped",
  killed: "killed",
  created: "created",
  planned: "planned",
  draft: "draft",
  launchable: "launchable",
  validated: "validated",
  pending: "pending",
};

export function formatStateLabel(value: string | null | undefined): string {
  if (!value) {
    return "unknown";
  }
  return STATE_LABELS[value] || value.replaceAll("_", " ");
}

export function formatFallback(value: string | null | undefined, fallback = "none"): string {
  if (!value) {
    return fallback;
  }
  const text = value.trim();
  return text || fallback;
}

export function formatCompactId(value: string | null | undefined, keep = 6): string {
  const text = formatFallback(value, "none");
  if (text === "none" || text.length <= keep * 2 + 1) {
    return text;
  }
  return `${text.slice(0, keep)}...${text.slice(-keep)}`;
}

export function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "unknown time";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getTagToneClass(value: string | null | undefined): string {
  const text = (value || "").toLowerCase();
  if (!text) {
    return "";
  }
  if (
    text.includes("failed") ||
    text.includes("dead") ||
    text.includes("kill") ||
    text.includes("danger") ||
    text.includes("warning") ||
    text.includes("error") ||
    text.includes("high-risk") ||
    text.includes("secondary-confirmation")
  ) {
    return "danger";
  }
  if (
    text.includes("running") ||
    text.includes("ok") ||
    text.includes("status") ||
    text.includes("launchable") ||
    text.includes("planned") ||
    text.includes("validated") ||
    text.includes("interactive") ||
    text.includes("online")
  ) {
    return "status-tag";
  }
  return "";
}

export function getStatusChipToneClass(value: string): string {
  const text = value.toLowerCase();
  if (text.includes("dead") || text.includes("failed")) {
    return "danger";
  }
  if (text.includes("running") || text.includes("ok") || text.includes("workers")) {
    return "status-tag";
  }
  return "";
}
