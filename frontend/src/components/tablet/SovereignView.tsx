"use client";

import {
  Activity,
  Brain,
  CalendarClock,
  Radio,
  Shield,
  Volume2,
  VolumeX,
} from "lucide-react";
import { RudrakshaCore } from "@/components/hud/RudrakshaCore";
import { ProcessStream, type Stage } from "@/components/hud/ProcessStream";
import { DailyBriefingPanel } from "@/components/hud/DailyBriefingPanel";
import { ResearchLibraryPanel } from "@/components/hud/ResearchLibraryPanel";
import { SpecialistHubPanel } from "@/components/hud/SpecialistHubPanel";
import { DocumentBrainPanel } from "@/components/hud/DocumentBrainPanel";
import { FounderOSPanel } from "@/components/hud/FounderOSPanel";
import { KnowledgeGraphPanel } from "@/components/hud/KnowledgeGraphPanel";
import { SutraWordmark } from "@/components/hud/SutraWordmark";
import { DecreeScroll, type DecreeMessage } from "@/components/tablet/DecreeScroll";
import { RealmDrawer, RealmSection } from "@/components/tablet/RealmDrawer";
import { RealmRim, type RealmId } from "@/components/tablet/RealmRim";
import { SovereignTablet } from "@/components/tablet/SovereignTablet";
import { SutraField } from "@/components/tablet/SutraField";
import { WorldStrip } from "@/components/tablet/WorldStrip";
import { GemGauge } from "@/components/tablet/GemGauge";
import {
  AGENT_TAG,
  SUTRA_TICKER,
  themeModeLabel,
  facetColor,
  type CoreRhythm,
  type RudraThemeMode,
} from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";
import { speakAsAgent, voiceProfileForAgent } from "@/lib/voice";

export function SovereignView({
  themeMode,
  onThemeCycle,
  operator,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  modelName,
  memoryCount,
  agentCount,
  successRate,
  subsysRate,
  coreRef,
  processing,
  coreRhythm,
  activeFacetTag,
  selectedAgent,
  activeRoutedAgent,
  errorFacet,
  malaProgress,
  messages,
  feedRef,
  streamingMsgId,
  streamingMsgRef,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  onToggleMode,
  inputRef,
  listening,
  voiceHint,
  mode,
  placeholder,
  actions,
  activeRealm,
  onRealmChange,
  agents,
  onSelectAgent,
  skills,
  jobs,
  vitals,
  stages,
  steps,
  showProcess,
  onAskProject,
  tickerIdx,
  logLine,
  skillsCount,
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
  modelName: string;
  memoryCount: number;
  agentCount: number;
  successRate: number;
  subsysRate: number;
  coreRef: React.RefObject<HTMLDivElement | null>;
  processing: boolean;
  coreRhythm: CoreRhythm;
  activeFacetTag?: string;
  selectedAgent?: string;
  activeRoutedAgent?: string;
  errorFacet?: string;
  malaProgress?: { current: number; total: number };
  messages: DecreeMessage[];
  feedRef: React.RefObject<HTMLDivElement | null>;
  streamingMsgId: string | null;
  streamingMsgRef: React.MutableRefObject<HTMLDivElement | null>;
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  onToggleMode: () => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
  listening: boolean;
  voiceHint: string | null;
  mode: "agents" | "tools";
  placeholder: string;
  actions: { icon: typeof Activity; label: string; run: () => void }[];
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
  agents: AgentInfo[];
  onSelectAgent: (type?: string) => void;
  skills: SkillInfo[];
  jobs: SchedulerJob[];
  vitals: ServiceHealth[];
  stages: Stage[];
  steps: ActStep[];
  showProcess: boolean;
  onAskProject: (name: string) => void;
  tickerIdx: number;
  logLine: string;
  skillsCount: number;
}) {
  return (
    <SovereignTablet
      header={
        <>
          <SutraWordmark />
          <div className="flex items-center gap-2 sm:gap-3 font-terminal text-[10px]">
            <button type="button" onClick={onThemeCycle} className="tablet-ctl hidden sm:inline">
              {themeModeLabel(themeMode)}
            </button>
            <span className="flex items-center gap-1 neon-dim">
              <Radio className="h-3 w-3" />
              <span className="hidden sm:inline">{status}</span>
            </span>
            <span className="text-muted-foreground">{clock ? clock.toLocaleTimeString("en-GB") : "--:--"}</span>
            <button type="button" onClick={onLogout} className="tablet-ctl hidden sm:inline">
              Exit
            </button>
            <button type="button" onClick={onToggleMute} className="tablet-ctl-icon" title={muted ? "Unmute" : "Mute"}>
              {muted ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
            </button>
          </div>
        </>
      }
      footer={
        <>
          <Shield className="h-3 w-3 shrink-0 opacity-60" />
          <span className="hidden truncate sm:inline">{SUTRA_TICKER[tickerIdx]}</span>
          <span className="mx-1 hidden opacity-30 sm:inline">·</span>
          <span className="truncate opacity-50">{logLine}</span>
          <span className="ml-auto shrink-0 opacity-40">
            MEM {memoryCount} · IX {agentCount} · SK {skillsCount}
          </span>
        </>
      }
    >
      <WorldStrip
        greeting={greeting}
        status={status}
        modelName={modelName}
        memoryCount={memoryCount}
        agentCount={agentCount}
        successRate={successRate}
        subsysRate={subsysRate}
        operator={operator}
      />

      <div className="core-chamber">
        <RudrakshaCore
          coreRef={coreRef}
          active={processing}
          status={status}
          size={160}
          rhythm={coreRhythm}
          activeFacet={activeFacetTag}
          activeAgentType={selectedAgent ?? activeRoutedAgent}
          errorFacet={errorFacet}
          malaProgress={malaProgress}
        />
      </div>

      <DecreeScroll
        messages={messages}
        processing={processing}
        feedRef={feedRef}
        streamingMsgId={streamingMsgId}
        streamingMsgRef={streamingMsgRef}
        onReplayVoice={(content, agentType) =>
          speakAsAgent(content, agentType, voiceProfileForAgent(agentType, undefined), muted)
        }
      />

      <div className="sovereign-actions">
        {actions.map((a) => (
          <button
            key={a.label}
            type="button"
            onClick={a.run}
            disabled={processing}
            title={a.label}
            className="sovereign-action-bead"
          >
            <a.icon className="h-3 w-3" />
            <span>{a.label}</span>
          </button>
        ))}
      </div>

      <SutraField
        value={input}
        onChange={onInputChange}
        onSubmit={onSubmit}
        onStop={onStop}
        onVoice={onVoice}
        onToggleMode={onToggleMode}
        processing={processing}
        listening={listening}
        muted={muted}
        placeholder={placeholder}
        voiceHint={voiceHint}
        mode={mode}
        inputRef={inputRef}
      />

      <RealmRim active={activeRealm} onSelect={onRealmChange} activeFacet={activeFacetTag} />

      <RealmDrawer realm={activeRealm} onClose={() => onRealmChange(null)}>
        {activeRealm === "dominions" && (
          <>
            <RealmSection title="Council table">
              <DailyBriefingPanel />
            </RealmSection>
            <RealmSection title="Your dominions">
              <FounderOSPanel onAskProject={onAskProject} />
            </RealmSection>
          </>
        )}
        {activeRealm === "archive" && (
          <>
            <RealmSection title="Mala of memory">
              <KnowledgeGraphPanel />
            </RealmSection>
            <RealmSection title="Research vault">
              <ResearchLibraryPanel />
            </RealmSection>
          </>
        )}
        {activeRealm === "council" && (
          <RealmSection title="The nine · silent">
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
                    <span className="neon-amber">{s.name}</span> — {s.description}
                  </p>
                ))}
              </div>
            )}
          </RealmSection>
        )}
        {activeRealm === "scriptorium" && (
          <>
            <RealmSection title="Horizon desk">
              <SpecialistHubPanel />
            </RealmSection>
            <RealmSection title="Document brain">
              <DocumentBrainPanel />
            </RealmSection>
          </>
        )}
        {activeRealm === "horizon" && (
          <RealmSection title="Horizon">
            <SpecialistHubPanel />
          </RealmSection>
        )}
        {activeRealm === "engine" && (
          <>
            <RealmSection title="What Rudra sees">
              {showProcess ? (
                <ProcessStream stages={stages} steps={steps} processing={processing} />
              ) : (
                <p className="font-terminal text-[10px] text-muted-foreground/80">Awaiting signal…</p>
              )}
            </RealmSection>
            <RealmSection title="Realms pulse">
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
            </RealmSection>
            <RealmSection title="Autonomous rites">
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
            </RealmSection>
          </>
        )}
      </RealmDrawer>
    </SovereignTablet>
  );
}
