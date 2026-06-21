"use client";

import { FlatMandala } from "@/components/mandala/FlatMandala";
import { RudraPrimeShell } from "./prime";
import { PrimeBackground } from "./prime/PrimeBackground";
import { CosmicRealmPanel } from "./CosmicRealmPanel";
import type { Stage } from "@/components/hud/ProcessStream";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { GrahaId } from "@/components/cosmos/navagraha-types";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";
import type { LucideIcon } from "lucide-react";

export function CosmicPlayground({
  operator,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  logLine,
  logLines,
  processing,
  leadGrahaId,
  leadGrahaName,
  pulseGrahaIds,
  counselText,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  voiceHint,
  placeholder,
  actions,
  streamingMsgId,
  uplinkActive = true,
  memorySynced = true,
  onQuickSubmit,
  activeRealm,
  onRealmChange,
  onGrahaSelect,
  selectedGrahaId,
  onSelectAgent,
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
}: {
  operator: string | null;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  greeting: string;
  logLine: string;
  logLines?: string[];
  processing: boolean;
  leadGrahaId?: GrahaId;
  leadGrahaName?: string;
  pulseGrahaIds?: GrahaId[];
  counselText?: string;
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  voiceHint?: string | null;
  placeholder: string;
  actions: { icon: LucideIcon; label: string; run: () => void }[];
  streamingMsgId: string | null;
  uplinkActive?: boolean;
  memorySynced?: boolean;
  onQuickSubmit?: (query: string) => void;
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
  onGrahaSelect?: (id: GrahaId) => void;
  selectedGrahaId?: GrahaId;
  onSelectAgent: (type?: string) => void;
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
}) {
  const lines = logLines ?? (logLine ? [logLine] : []);

  return (
    <div className="cosmic-playground prime-stage mandala-stage relative h-screen w-screen overflow-hidden">
      <PrimeBackground />

      <FlatMandala
        leadGrahaId={leadGrahaId}
        pulseGrahaIds={pulseGrahaIds ?? []}
        processing={processing}
      />

      <RudraPrimeShell
        status={status}
        clock={clock}
        onLogout={onLogout}
        muted={muted}
        onToggleMute={onToggleMute}
        processing={processing}
        input={input}
        onInputChange={onInputChange}
        onSubmit={onSubmit}
        onStop={onStop}
        onVoice={onVoice}
        listening={listening}
        voiceHint={voiceHint}
        placeholder={placeholder}
        streamingMsgId={streamingMsgId}
        actions={actions}
        uplinkActive={uplinkActive}
        memorySynced={memorySynced}
        onQuickSubmit={onQuickSubmit}
        leadGrahaId={leadGrahaId}
        leadGrahaName={leadGrahaName}
        counselText={counselText}
        logLines={lines}
        activeRealm={activeRealm}
        onRealmChange={onRealmChange}
        onGrahaSelect={onGrahaSelect}
        selectedGrahaId={selectedGrahaId}
      />

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
