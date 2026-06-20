"use client";

import { useRef } from "react";
import { CosmicScene } from "./CosmicScene";
import { CosmicRealmPanel } from "./CosmicRealmPanel";
import { CosmicViewControls } from "./CosmicViewControls";
import type { CosmicNavHandle } from "./cosmic-nav-types";
import type { Stage } from "@/components/hud/ProcessStream";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { RudraThemeMode } from "@/lib/rudra-theme";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";
import type { GrahaId } from "./navagraha-config";
import type { LucideIcon } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  agentType?: string;
  streaming?: boolean;
}

export function CosmicPlayground({
  themeMode,
  onThemeCycle,
  operator,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  logLine,
  tickerIdx,
  processing,
  leadGrahaId,
  supportingGrahaIds,
  pulseGrahaIds,
  leadGrahaName,
  supportingGrahaNames,
  errorFacet,
  onSelectAgent,
  messages,
  streamingMsgId,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  voiceHint,
  placeholder,
  actions,
  activeRealm,
  onRealmChange,
  agents,
  skills,
  jobs,
  vitals,
  stages,
  steps,
  showProcess,
  successRate,
  subsysRate,
  onAskProject,
  uplinkActive = true,
  memorySynced = true,
}: {
  themeMode: RudraThemeMode;
  onThemeCycle: () => void;
  operator: string | null;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  greeting: string;
  logLine: string;
  tickerIdx: number;
  processing: boolean;
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
  leadGrahaName?: string;
  supportingGrahaNames?: string[];
  errorFacet?: string;
  onSelectAgent: (type?: string) => void;
  messages: Message[];
  streamingMsgId: string | null;
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  voiceHint?: string | null;
  placeholder: string;
  actions: { icon: LucideIcon; label: string; run: () => void }[];
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
  agents: AgentInfo[];
  skills: SkillInfo[];
  jobs: SchedulerJob[];
  vitals: ServiceHealth[];
  stages: Stage[];
  steps: ActStep[];
  showProcess: boolean;
  successRate: number;
  subsysRate: number;
  onAskProject: (name: string) => void;
  uplinkActive?: boolean;
  memorySynced?: boolean;
}) {
  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant" && m.content);
  const showCounsel =
    processing || Boolean(streamingMsgId) || Boolean(latestAssistant?.content);
  const navRef = useRef<CosmicNavHandle | null>(null);

  return (
    <div className="cosmic-playground relative h-screen w-screen overflow-hidden">
      <CosmicScene
        navRef={navRef}
        processing={processing}
        leadGrahaId={leadGrahaId}
        supportingGrahaIds={supportingGrahaIds ?? []}
        pulseGrahaIds={pulseGrahaIds ?? []}
        errorFacet={errorFacet}
        streamingActive={Boolean(streamingMsgId)}
        ui={{
          themeMode,
          onThemeCycle,
          status,
          clock,
          onLogout,
          muted,
          onToggleMute,
          tickerIdx,
          input,
          onInputChange,
          onSubmit,
          onStop,
          onVoice,
          listening,
          processing,
          placeholder,
          voiceHint,
          leadGrahaName,
          supportingGrahaNames,
          activeRealm,
          onRealmChange,
          uplinkActive,
          memorySynced,
          leadGrahaId,
          supportingGrahaIds,
          pulseGrahaIds,
          counselText: latestAssistant?.content ?? "",
          showCounsel,
        }}
      />

      <CosmicViewControls navRef={navRef} />

      {voiceHint && (
        <p className="pointer-events-none absolute bottom-28 left-0 right-0 z-20 text-center font-terminal text-[9px] text-destructive/80">
          {voiceHint}
        </p>
      )}

      <div className="sr-only">
        {actions.map((a) => (
          <button key={a.label} type="button" onClick={a.run}>
            {a.label}
          </button>
        ))}
        {operator && <span>{greeting}</span>}
        <span>{logLine}</span>
      </div>

      {activeRealm && (
        <>
          <button
            type="button"
            className="cosmic-realm-backdrop"
            aria-label="Close realm"
            onClick={() => onRealmChange(null)}
          />
          <div className="cosmic-realm-wrap cosmic-realm-wrap-3d">
            <CosmicRealmPanel
              realm={activeRealm}
              onClose={() => onRealmChange(null)}
              agents={agents}
              selectedAgent={undefined}
              onSelectAgent={onSelectAgent}
              skills={skills}
              showProcess={showProcess}
              stages={stages}
              steps={steps}
              processing={processing}
              successRate={successRate}
              subsysRate={subsysRate}
              vitals={vitals}
              jobs={jobs}
              onAskProject={onAskProject}
            />
          </div>
        </>
      )}
    </div>
  );
}
