"use client";

import { ObservatoryShell } from "@/components/observatory";
import { CosmicRealmPanel } from "./CosmicRealmPanel";
import type { Stage } from "@/components/hud/ProcessStream";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { GrahaId } from "@/components/cosmos/navagraha-types";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";
import type { LucideIcon } from "lucide-react";

export function CosmicPlayground({
  operator,
  status,
  onLogout,
  logLines,
  logLine,
  processing,
  leadGrahaId,
  counselText,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  placeholder,
  streamingMsgId,
  uplinkActive = true,
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
  activeRealm,
  onRealmChange,
  systemsNominal = true,
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
  systemsNominal?: boolean;
}) {
  const lines = logLines ?? (logLine ? [logLine] : []);

  return (
    <div className="cosmic-playground relative h-screen w-screen overflow-hidden">
      <ObservatoryShell
        status={status}
        onLogout={onLogout}
        logLines={lines}
        processing={processing}
        leadGrahaId={leadGrahaId}
        counselText={counselText}
        uplinkActive={uplinkActive}
        systemsNominal={systemsNominal}
        input={input}
        onInputChange={onInputChange}
        onSubmit={onSubmit}
        onStop={onStop}
        onVoice={onVoice}
        listening={listening}
        placeholder={placeholder}
        streamingActive={Boolean(streamingMsgId)}
        onGrahaSelect={onGrahaSelect}
        selectedGrahaId={selectedGrahaId}
      />

      {activeRealm && (
        <>
          <button
            type="button"
            className="cosmic-realm-backdrop"
            aria-label="Close realm"
            onClick={() => onRealmChange(null)}
          />
          <div className="cosmic-realm-wrap">
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

      <div className="sr-only">{operator && <span>Rudra observatory</span>}</div>
    </div>
  );
}
