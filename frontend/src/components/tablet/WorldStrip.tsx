"use client";

import { GemGauge } from "./GemGauge";

export function WorldStrip({
  greeting,
  status,
  modelName,
  memoryCount,
  agentCount,
  successRate,
  subsysRate,
  operator,
}: {
  greeting: string;
  status: string;
  modelName: string;
  memoryCount: number;
  agentCount: number;
  successRate: number;
  subsysRate: number;
  operator: string | null;
}) {
  return (
    <section className="world-strip bark-texture">
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <p className="font-hud text-[11px] tracking-[0.12em] text-foreground/90">{greeting}</p>
        <p className="font-terminal text-[9px] text-muted-foreground/90">
          {operator ? `${operator} · ` : ""}
          {status.toLowerCase()} · {modelName}
        </p>
      </div>
      <div className="flex shrink-0 items-center gap-3">
        <GemGauge value={successRate} label="realm" size={34} />
        <GemGauge value={subsysRate} label="pulse" size={34} />
      </div>
      <div className="hidden w-full flex-wrap gap-2 border-t border-primary/10 pt-2 sm:flex">
        <span className="realm-chip">{memoryCount} memories</span>
        <span className="realm-chip">{agentCount} planets</span>
      </div>
    </section>
  );
}
