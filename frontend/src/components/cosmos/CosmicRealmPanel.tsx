"use client";

import { Brain, CalendarClock, X } from "lucide-react";
import { ProcessStream, type Stage } from "@/components/hud/ProcessStream";
import { DailyBriefingPanel } from "@/components/hud/DailyBriefingPanel";
import { ResearchLibraryPanel } from "@/components/hud/ResearchLibraryPanel";
import { SpecialistHubPanel } from "@/components/hud/SpecialistHubPanel";
import { DocumentBrainPanel } from "@/components/hud/DocumentBrainPanel";
import { FounderOSPanel } from "@/components/hud/FounderOSPanel";
import { KnowledgeGraphPanel } from "@/components/hud/KnowledgeGraphPanel";
import { GemGauge } from "@/components/tablet/GemGauge";
import { AGENT_TAG, facetColor } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";
import type { RealmId } from "@/components/tablet/RealmRim";
import { REALMS } from "@/components/tablet/RealmRim";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      <p className="mb-1.5 font-hud text-[9px] uppercase tracking-[0.16em] text-primary/80">{title}</p>
      {children}
    </div>
  );
}

export function CosmicRealmPanel({
  realm,
  onClose,
  agents,
  selectedAgent,
  onSelectAgent,
  skills,
  showProcess,
  stages,
  steps,
  processing,
  successRate,
  subsysRate,
  vitals,
  jobs,
  onAskProject,
}: {
  realm: RealmId;
  onClose: () => void;
  agents: AgentInfo[];
  selectedAgent?: string;
  onSelectAgent: (type?: string) => void;
  skills: SkillInfo[];
  showProcess: boolean;
  stages: Stage[];
  steps: ActStep[];
  processing: boolean;
  successRate: number;
  subsysRate: number;
  vitals: ServiceHealth[];
  jobs: SchedulerJob[];
  onAskProject: (name: string) => void;
}) {
  const meta = REALMS.find((r) => r.id === realm);

  return (
    <div className="cosmic-realm-panel pointer-events-auto">
      <header className="mb-3 flex items-start justify-between border-b border-primary/15 pb-2">
        <div>
          <p className="font-hud text-xs tracking-[0.14em] neon-dim">{meta?.label ?? realm}</p>
          <p className="font-terminal text-[9px] text-muted-foreground/70">Cosmic sector · tap void to dismiss</p>
        </div>
        <button type="button" onClick={onClose} className="cosmic-ctl-icon">
          <X className="h-4 w-4" />
        </button>
      </header>

      <div className="max-h-[50vh] overflow-y-auto pr-1">
        {realm === "dominions" && (
          <>
            <Section title="Executive intel">
              <DailyBriefingPanel />
            </Section>
            <Section title="Dominions">
              <FounderOSPanel onAskProject={onAskProject} />
            </Section>
          </>
        )}
        {realm === "archive" && (
          <>
            <Section title="Constellation map">
              <KnowledgeGraphPanel />
            </Section>
            <Section title="Research vault">
              <ResearchLibraryPanel />
            </Section>
          </>
        )}
        {realm === "council" && (
          <Section title="The nine planets">
            <div className="space-y-1">
              <button
                type="button"
                onClick={() => onSelectAgent(undefined)}
                className={cn(
                  "agent-accent relative w-full rounded px-2 py-1.5 text-left font-terminal text-[11px]",
                  !selectedAgent ? "bg-primary/10 neon" : "text-muted-foreground"
                )}
              >
                <Brain className="mr-1 inline h-3 w-3" /> Autoroute · all planets
              </button>
              {agents.map((a) => (
                <button
                  key={a.type}
                  type="button"
                  onClick={() => onSelectAgent(a.type)}
                  className={cn(
                    "agent-accent relative flex w-full items-center gap-2 rounded px-2 py-1.5 text-left font-terminal text-[11px]",
                    selectedAgent === a.type ? "bg-primary/10 neon" : "text-muted-foreground"
                  )}
                >
                  <span
                    className="flex h-4 w-5 items-center justify-center rounded border text-[8px] font-bold"
                    style={{
                      color: facetColor(AGENT_TAG[a.type], 0.95),
                      borderColor: facetColor(AGENT_TAG[a.type], 0.4),
                      background: facetColor(AGENT_TAG[a.type], 0.12),
                    }}
                  >
                    {AGENT_TAG[a.type]}
                  </span>
                  <span className="truncate">{a.name}</span>
                </button>
              ))}
            </div>
            {skills.length > 0 && (
              <div className="mt-3 space-y-1 border-t border-primary/10 pt-2">
                {skills.map((s) => (
                  <p key={s.name} className="font-terminal text-[9px] text-muted-foreground">
                    <span className="neon-violet">{s.name}</span> — {s.description}
                  </p>
                ))}
              </div>
            )}
          </Section>
        )}
        {realm === "scriptorium" && (
          <>
            <Section title="Horizon desk">
              <SpecialistHubPanel />
            </Section>
            <Section title="Document brain">
              <DocumentBrainPanel />
            </Section>
          </>
        )}
        {realm === "horizon" && (
          <Section title="Horizon">
            <SpecialistHubPanel />
          </Section>
        )}
        {realm === "engine" && (
          <>
            <Section title="Neural activity">
              {showProcess ? (
                <ProcessStream stages={stages} steps={steps} processing={processing} />
              ) : (
                <p className="font-terminal text-[10px] text-muted-foreground/80">Awaiting signal…</p>
              )}
            </Section>
            <Section title="Realm pulse">
              <div className="mb-3 flex justify-around">
                <GemGauge value={successRate} label="success" />
                <GemGauge value={subsysRate} label="subsys" />
              </div>
              <div className="space-y-1">
                {vitals.map((v) => (
                  <div key={v.service} className="flex items-center gap-2 font-terminal text-[10px]">
                    <span
                      className="h-1.5 w-1.5 rounded-full"
                      style={{
                        background: v.ok ? "hsl(var(--rudra-leaf))" : "hsl(var(--rudra-ember) / 0.6)",
                      }}
                    />
                    <span className="text-foreground/85">{v.service}</span>
                    <span className="ml-auto text-muted-foreground/80">{v.ok ? "online" : "down"}</span>
                  </div>
                ))}
              </div>
            </Section>
            <Section title="Autonomous rites">
              {jobs.length === 0 ? (
                <p className="font-terminal text-[10px] text-muted-foreground/80">None scheduled</p>
              ) : (
                jobs.map((j) => (
                  <p key={j.id} className="font-terminal text-[10px] text-muted-foreground">
                    <CalendarClock className="mr-1 inline h-3 w-3" />
                    {j.name}
                  </p>
                ))
              )}
            </Section>
          </>
        )}
      </div>
    </div>
  );
}
