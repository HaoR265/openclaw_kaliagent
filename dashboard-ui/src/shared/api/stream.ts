export function openStream(
  params: { missionId?: string; workflowId?: string; campaignId?: string },
  onData: (payload: any) => void,
  options?: { onStatus?: (status: "connecting" | "live" | "reconnecting" | "recovered") => void },
) {
  const query = new URLSearchParams();
  if (params.missionId) query.set("mission_id", params.missionId);
  if (params.workflowId) query.set("workflow_id", params.workflowId);
  if (params.campaignId) query.set("campaign_id", params.campaignId);
  let source: EventSource | null = null;
  let closed = false;
  let retryTimer: number | null = null;
  let retryDelayMs = 3000;
  let hasConnected = false;
  let didReconnect = false;

  const connect = () => {
    if (closed) return;
    options?.onStatus?.(hasConnected ? "reconnecting" : "connecting");
    source = new EventSource(`/api/stream?${query.toString()}`);
    source.onopen = () => {
      retryDelayMs = 3000;
      if (didReconnect) {
        options?.onStatus?.("recovered");
        window.setTimeout(() => {
          if (!closed) options?.onStatus?.("live");
        }, 1800);
      } else {
        options?.onStatus?.("live");
      }
      hasConnected = true;
      didReconnect = false;
    };
    source.onmessage = () => undefined;
    source.addEventListener("mission.updated", (event) => onData(JSON.parse((event as MessageEvent).data)));
    source.addEventListener("workflow.updated", (event) => onData(JSON.parse((event as MessageEvent).data)));
    source.addEventListener("campaign.updated", (event) => onData(JSON.parse((event as MessageEvent).data)));
    source.onerror = () => {
      source?.close();
      source = null;
      if (!closed && retryTimer == null) {
        options?.onStatus?.("reconnecting");
        didReconnect = true;
        retryTimer = window.setTimeout(() => {
          retryTimer = null;
          connect();
        }, retryDelayMs);
        retryDelayMs = Math.min(retryDelayMs * 2, 15000);
      }
    };
  };

  connect();

  return {
    close() {
      closed = true;
      source?.close();
      source = null;
      if (retryTimer != null) {
        window.clearTimeout(retryTimer);
        retryTimer = null;
      }
    },
  };
}
