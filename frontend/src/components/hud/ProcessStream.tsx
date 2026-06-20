"use client";

import {
  Brain,
  Check,
  Clock,
  Cpu,
  Database,
  Loader2,
  Search,
  Sparkles,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import type { ActStep } from "@/lib/api";

export interface Stage {
  label: string;
  state: "pending" | "active" | "done";
}

function toolIcon(name: string | null): LucideIcon {
  switch (name) {
    case "web_search":
      return Search;
    case "search_memory":
      return Database;
    case "calculator":
      return Cpu;
    case "current_time":
      return Clock;
    case "use_skill":
      return Sparkles;
    case "route_agent":
      return Brain;
    default:
      return Wrench;
  }
}

export function ProcessStream({
  stages,
  steps,
  processing,
}: {
  stages: Stage[];
  steps: ActStep[];
  processing: boolean;
}) {
  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        {stages.map((s, i) => (
          <div key={i} className="flex items-center gap-2 font-terminal text-[11px]">
            <span className="flex h-4 w-4 items-center justify-center">
              {s.state === "done" ? (
                <Check className="h-3 w-3" style={{ color: "hsl(var(--rudra-leaf))" }} />
              ) : s.state === "active" ? (
                <Loader2 className="neon h-3 w-3 animate-spin" />
              ) : (
                <span className="h-1.5 w-1.5 rounded-full bg-primary/25" />
              )}
            </span>
            <span
              className={
                s.state === "pending"
                  ? "text-muted-foreground/70"
                  : s.state === "active"
                    ? "neon"
                    : "text-muted-foreground"
              }
            >
              {s.label}
            </span>
            {s.state === "active" && (
              <span className="ml-auto h-1 w-16 overflow-hidden rounded-full bg-primary/10">
                <span
                  className="block h-full w-1/2 rounded-full"
                  style={{
                    background: "hsl(var(--cosmos-cyan))",
                    animation: "barScan 1.1s linear infinite",
                  }}
                />
              </span>
            )}
          </div>
        ))}
      </div>

      {steps.length > 0 && (
        <div className="space-y-2.5 border-t border-primary/10 pt-2.5">
          {steps.map((st, i) => {
            const Icon = toolIcon(st.tool);
            return (
              <div key={i} className="rise-in" style={{ animationDelay: `${i * 0.12}s` }}>
                <div className="flex items-center gap-1.5 font-terminal text-[9px] neon-dim">
                  <Sparkles className="h-3 w-3" /> INSIGHT · {i + 1}
                </div>
                {st.thought && (
                  <p className="ml-4 font-terminal text-[11px] leading-snug text-foreground/80">
                    {st.thought}
                  </p>
                )}
                {st.tool && (
                  <div className="ml-4 mt-1 flex items-start gap-1.5">
                    <Icon
                      className="mt-0.5 h-3 w-3 shrink-0"
                      style={{ color: "hsl(var(--rudra-saffron))" }}
                    />
                    <div className="min-w-0">
                      <span className="font-terminal text-[10px] neon-amber">{st.tool}</span>
                      <span className="ml-1 font-terminal text-[10px] text-muted-foreground/80">
                        {JSON.stringify(st.args)}
                      </span>
                      {st.observation && (
                        <p className="font-terminal text-[10px] leading-snug text-foreground/75">
                          ↳ {st.observation.slice(0, 200)}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {processing && steps.length === 0 && (
        <p className="blip font-terminal text-[10px] text-muted-foreground/80">
          ◇ signal in motion…
        </p>
      )}
    </div>
  );
}
