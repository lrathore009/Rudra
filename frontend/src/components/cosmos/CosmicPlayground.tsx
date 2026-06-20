"use client";

import { CosmicScene } from "./CosmicScene";
import { CosmicHUD } from "./CosmicHUD";
import { CosmicRealmPanel } from "./CosmicRealmPanel";
import type { Stage } from "@/components/hud/ProcessStream";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { RudraThemeMode } from "@/lib/rudra-theme";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";
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
  activeFacetTag,
  selectedAgent,
  activeRoutedAgent,
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
  activeFacetTag?: string;
  selectedAgent?: string;
  activeRoutedAgent?: string;
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
}) {
  const handlePlanetSelect = (agentType: string) => {
    onSelectAgent(selectedAgent === agentType ? undefined : agentType);
  };

  return (
    <div className="cosmic-playground relative h-screen w-screen overflow-hidden">
      <CosmicScene
        processing={processing}
        activeAgentType={activeRoutedAgent ?? selectedAgent}
        activeFacet={activeFacetTag}
        errorFacet={errorFacet}
        selectedAgent={selectedAgent}
        onSelectAgent={handlePlanetSelect}
      />

      <CosmicHUD
        themeMode={themeMode}
        onThemeCycle={onThemeCycle}
        status={status}
        clock={clock}
        onLogout={onLogout}
        muted={muted}
        onToggleMute={onToggleMute}
        greeting={greeting}
        logLine={logLine}
        tickerIdx={tickerIdx}
        operator={operator}
        messages={messages}
        streamingMsgId={streamingMsgId}
        input={input}
        onInputChange={onInputChange}
        onSubmit={onSubmit}
        onStop={onStop}
        onVoice={onVoice}
        listening={listening}
        processing={processing}
        placeholder={placeholder}
        voiceHint={voiceHint}
        selectedAgent={selectedAgent}
        activeFacetTag={activeFacetTag}
        onSelectAgent={onSelectAgent}
        agents={agents}
        actions={actions}
        activeRealm={activeRealm}
        onRealmChange={onRealmChange}
        showResponse
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
              selectedAgent={selectedAgent}
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
