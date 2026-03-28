import { getStatusChipToneClass } from "../shared/ui/present";

type Overview = {
  stats?: {
    total?: number;
    states?: Record<string, number>;
  };
  workers?: Array<{ id: string; status: string }>;
  results_count?: number;
  dead_letter_count?: number;
};

export function StatusBar({ overview }: { overview: Overview | null }) {
  const states = overview?.stats?.states || {};
  const onlineWorkers = (overview?.workers || []).filter((item) => item.status === "online").length;
  const chips = [
    `tasks ${overview?.stats?.total ?? 0}`,
    `queued ${states.queued ?? 0}`,
    `running ${(states.running ?? 0) + (states.leased ?? 0)}`,
    `ok ${states.succeeded ?? 0}`,
    `dead ${states.dead_letter ?? 0}`,
    `results ${overview?.results_count ?? 0}`,
    `workers ${onlineWorkers}`,
  ];

  return (
    <div className="status-bar">
      {chips.map((chip) => (
        <div className={`status-chip ${getStatusChipToneClass(chip)}`.trim()} key={chip}>
          {chip}
        </div>
      ))}
    </div>
  );
}
