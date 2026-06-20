"use client";

import { useCallback, useEffect, useState } from "react";
import { Briefcase, ChevronRight } from "lucide-react";
import { getProjectDashboard, type ProjectDashboard, type ProjectCard } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Props {
  onAskProject?: (name: string) => void;
}

export function FounderOSPanel({ onAskProject }: Props) {
  const [dashboard, setDashboard] = useState<ProjectDashboard | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setDashboard(await getProjectDashboard());
    } catch {
      setDashboard(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const projects = (dashboard?.projects ?? []).filter(
    (p) => priorityFilter === null || p.priority <= priorityFilter
  );

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <div className="flex gap-1">
        {[null, 1, 2, 3].map((p) => (
          <button
            key={String(p)}
            type="button"
            onClick={() => setPriorityFilter(p)}
            className={cn(
              "flex-1 border px-1 py-0.5 font-terminal text-[8px] uppercase",
              priorityFilter === p
                ? "border-primary/50 bg-primary/10 text-foreground"
                : "border-primary/15 text-muted-foreground/90"
            )}
          >
            {p === null ? "All" : `P${p}`}
          </button>
        ))}
      </div>

      {loading && <p className="font-terminal text-[10px] text-muted-foreground/80">Loading portfolio…</p>}

      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
        {projects.map((project) => (
          <ProjectCardView key={project.id} project={project} onAsk={onAskProject} />
        ))}
      </div>

      {dashboard && (
        <p className="font-terminal text-[8px] text-muted-foreground/70">
          {dashboard.blocked_count} blocked · {dashboard.stale_count} stale
        </p>
      )}
    </div>
  );
}

function ProjectCardView({
  project,
  onAsk,
}: {
  project: ProjectCard;
  onAsk?: (name: string) => void;
}) {
  return (
    <div className="border border-primary/15 bg-background/50 p-2">
      <div className="mb-1 flex items-center gap-2">
        <Briefcase className="h-3 w-3 text-primary/60" />
        <span className="truncate font-terminal text-[11px] text-foreground">{project.name}</span>
        <span className="ml-auto font-terminal text-[8px] text-muted-foreground/80">P{project.priority}</span>
      </div>
      <div className="mb-1 h-1.5 overflow-hidden rounded bg-secondary/80">
        <div
          className="h-full bg-primary/70 transition-all"
          style={{ width: `${Math.min(100, project.progress_percent)}%` }}
        />
      </div>
      <p className="truncate font-terminal text-[9px] text-muted-foreground">
        Next: {project.next_action ?? "—"}
      </p>
      {project.blockers && (
        <p className="truncate font-terminal text-[9px] text-red-300/70">Blocker: {project.blockers}</p>
      )}
      {onAsk && (
        <button
          type="button"
          onClick={() => onAsk(project.name)}
          className="mt-1 flex items-center gap-1 font-terminal text-[8px] uppercase text-muted-foreground/90 hover:text-foreground"
        >
          Ask Rudra <ChevronRight className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}
