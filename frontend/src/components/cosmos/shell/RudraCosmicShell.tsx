"use client";

import { useCallback, useMemo, useState } from "react";
import type { Stage } from "@/components/hud/ProcessStream";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { RudraThemeMode } from "@/lib/rudra-theme";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";
import type { GrahaId } from "../navagraha-config";
import { grahaById } from "../navagraha-config";
import type { LucideIcon } from "lucide-react";
import { RudraHeader } from "./RudraHeader";
import { RudraCounselPane } from "./RudraCounselPane";
import { RudraCommandBar } from "./RudraCommandBar";
import { RudraRealmNav } from "./RudraRealmNav";
import { RudraFooter } from "./RudraFooter";
import { GrahaOrbitLabels } from "./GrahaOrbitLabels";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  agentType?: string;
  streaming?: boolean;
}

export interface RudraCosmicShellProps {
  themeMode: RudraThemeMode;
  onThemeCycle: () => void;
  operator: string | null;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  greeting: string;
  tickerIdx: number;
  processing: boolean;
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
  leadGrahaName?: string;
  supportingGrahaNames?: string[];
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
  uplinkActive?: boolean;
  memorySynced?: boolean;
  /** Hide counsel stream until user sends first command */
  showResponse?: boolean;
  /** @internal — passed for realm panel compatibility */
  agents?: AgentInfo[];
  skills?: SkillInfo[];
  jobs?: SchedulerJob[];
  vitals?: ServiceHealth[];
  stages?: Stage[];
  steps?: ActStep[];
  showProcess?: boolean;
}

/**
 * Production shell matching the Trishula Cosmos mockup — 2D overlay on full-screen R3F canvas.
 * Header · orbit labels · counsel stream · command bar · realm nav · footer.
 */
export function RudraCosmicShell({
  themeMode,
  onThemeCycle,
  operator,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  tickerIdx,
  processing,
  leadGrahaId,
  supportingGrahaIds,
  pulseGrahaIds,
  leadGrahaName,
  supportingGrahaNames,
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
  uplinkActive = true,
  memorySynced = true,
  showResponse = true,
}: RudraCosmicShellProps) {
  const [selectedGrahaId, setSelectedGrahaId] = useState<GrahaId | undefined>();

  const selectedGrahaName = useMemo(() => {
    const g = grahaById(selectedGrahaId);
    return g?.name;
  }, [selectedGrahaId]);

  const handleGrahaSelect = useCallback(
    (id: GrahaId) => {
      setSelectedGrahaId((prev) => {
        const next = prev === id ? undefined : id;
        const graha = grahaById(next);
        onSelectAgent(graha?.agentType);
        return next;
      });
    },
    [onSelectAgent]
  );

  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant" && m.content);
  const counselVisible =
    showResponse && (processing || Boolean(streamingMsgId) || Boolean(latestAssistant?.content));

  return (
    <div className="rudra-cosmic-shell cosmic-hud pointer-events-none fixed inset-0 z-10 flex flex-col">
      <GrahaOrbitLabels
        leadGrahaId={leadGrahaId}
        supportingGrahaIds={supportingGrahaIds}
        pulseGrahaIds={pulseGrahaIds}
        selectedGrahaId={selectedGrahaId}
        processing={processing}
        onGrahaSelect={handleGrahaSelect}
        dimmed={counselVisible}
      />

      <RudraHeader
        themeMode={themeMode}
        onThemeCycle={onThemeCycle}
        status={status}
        clock={clock}
        onLogout={onLogout}
        muted={muted}
        onToggleMute={onToggleMute}
        greeting={greeting}
        operator={operator}
      />

      <div className="flex flex-1 flex-col items-center justify-end px-4 pb-1 sm:px-8">
        <RudraCounselPane
          messages={messages}
          streamingMsgId={streamingMsgId}
          processing={processing}
          leadGrahaName={leadGrahaName}
          supportingGrahaNames={supportingGrahaNames}
          selectedGrahaName={selectedGrahaName}
          showResponse={showResponse}
        />

        <RudraCommandBar
          input={input}
          onInputChange={onInputChange}
          onSubmit={onSubmit}
          onStop={onStop}
          onVoice={onVoice}
          listening={listening}
          processing={processing}
          placeholder={placeholder}
          streamingActive={Boolean(streamingMsgId)}
          selectedGrahaName={selectedGrahaName}
        />

        {voiceHint && (
          <p className="pointer-events-auto mb-2 font-terminal text-[9px] text-destructive/80">{voiceHint}</p>
        )}

        <div className="sr-only" aria-hidden>
          {actions.map((a) => (
            <button key={a.label} type="button" onClick={a.run}>
              {a.label}
            </button>
          ))}
        </div>
      </div>

      <RudraRealmNav activeRealm={activeRealm} onRealmChange={onRealmChange} />
      <RudraFooter tickerIdx={tickerIdx} uplinkActive={uplinkActive} memorySynced={memorySynced} />
    </div>
  );
}

export { RudraHeader } from "./RudraHeader";
export { RudraCommandBar } from "./RudraCommandBar";
export { RudraCounselPane } from "./RudraCounselPane";
export { RudraRealmNav } from "./RudraRealmNav";
export { RudraFooter } from "./RudraFooter";
export { GrahaOrbitLabels } from "./GrahaOrbitLabels";
