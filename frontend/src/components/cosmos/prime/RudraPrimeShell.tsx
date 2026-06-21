"use client";

import { useCallback, useMemo, useState } from "react";
import type { Stage } from "@/components/hud/ProcessStream";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { RudraThemeMode } from "@/lib/rudra-theme";
import type { ActStep, AgentInfo, SchedulerJob, ServiceHealth, SkillInfo } from "@/lib/api";
import type { GrahaId } from "../navagraha-config";
import { grahaById } from "../navagraha-config";
import type { LucideIcon } from "lucide-react";
import { PrimeHeader } from "./PrimeHeader";
import { PrimeSidebar } from "./PrimeSidebar";
import { PrimeGrahaPanels } from "./PrimeGrahaPanels";
import { PrimeCommandBar } from "./PrimeCommandBar";
import { PrimeDualPane } from "./PrimeDualPane";
import { PrimeRealmNav } from "./PrimeRealmNav";
import { PrimeFooter } from "./PrimeFooter";
import { PrimeGridOverlay } from "./PrimeGridOverlay";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  agentType?: string;
  streaming?: boolean;
}

export interface RudraPrimeShellProps {
  themeMode: RudraThemeMode;
  onThemeCycle: () => void;
  operator: string | null;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  tickerIdx: number;
  processing: boolean;
  leadGrahaId?: GrahaId;
  leadGrahaName?: string;
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
  logLine?: string;
  onQuickSubmit?: (query: string) => void;
  agents?: AgentInfo[];
  skills?: SkillInfo[];
  jobs?: SchedulerJob[];
  vitals?: ServiceHealth[];
  stages?: Stage[];
  steps?: ActStep[];
  showProcess?: boolean;
}

export function RudraPrimeShell({
  themeMode,
  onThemeCycle,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  processing,
  leadGrahaId,
  leadGrahaName,
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
  logLine,
  onQuickSubmit,
}: RudraPrimeShellProps) {
  const [selectedGrahaId, setSelectedGrahaId] = useState<GrahaId | undefined>();
  const [voiceArmed, setVoiceArmed] = useState(true);

  const handleGrahaSelect = useCallback(
    (id: GrahaId) => {
      setSelectedGrahaId((prev) => {
        const next = prev === id ? undefined : id;
        onSelectAgent(grahaById(next)?.agentType);
        return next;
      });
    },
    [onSelectAgent]
  );

  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant" && m.content);
  const systemWelcome = messages.find((m) => m.role === "system")?.content;
  const streaming = messages.find((m) => m.id === streamingMsgId);

  const counselText = streaming?.content || latestAssistant?.content || systemWelcome;

  const logLines = useMemo(() => {
    const lines: string[] = [];
    if (listening) lines.push("Listening...");
    else if (processing) lines.push("Listening...", "Intent deciphered");
    else lines.push("Listening...", "Intent deciphered");
    if (leadGrahaName && processing) lines.push(`Lead · ${leadGrahaName}`);
    if (logLine) lines.push(logLine.replace(/^◇\s*|^·\s*|^>>\s*/g, "").slice(0, 48));
    if (!processing && !listening) lines.push("Awaiting transmission");
    return lines;
  }, [listening, processing, leadGrahaName, logLine]);

  const digestAction = actions.find((a) => a.label === "Run Digest");

  return (
    <div className="rudra-prime-shell rudra-prime-vignette pointer-events-none fixed inset-0 z-10 flex flex-col">
      <PrimeGridOverlay />

      <PrimeGrahaPanels
        leadGrahaId={leadGrahaId}
        selectedGrahaId={selectedGrahaId}
        onGrahaSelect={handleGrahaSelect}
      />

      <PrimeSidebar
        onTime={() => onQuickSubmit?.("What time is it?")}
        onWikipedia={() => onQuickSubmit?.("Search wikipedia for ")}
        onVoice={() => {
          setVoiceArmed(true);
          onVoice();
        }}
        onDigest={() => digestAction?.run()}
        systemsNominal={uplinkActive}
        listening={listening}
      />

      <PrimeHeader
        themeMode={themeMode}
        onThemeCycle={onThemeCycle}
        status={status}
        clock={clock}
        onLogout={onLogout}
        muted={muted}
        onToggleMute={onToggleMute}
        listening={listening}
        voiceArmed={voiceArmed}
      />

      <div className="flex flex-1" />

      <div className="relative z-20 flex flex-col items-center gap-2 px-4 pb-1 sm:px-6">
        <PrimeDualPane
          counselText={counselText}
          processing={processing}
          leadGrahaName={leadGrahaName}
          logLines={logLines}
        />

        <PrimeCommandBar
          input={input}
          onInputChange={onInputChange}
          onSubmit={onSubmit}
          onStop={onStop}
          onVoice={onVoice}
          listening={listening}
          processing={processing}
          placeholder={placeholder}
          streamingActive={Boolean(streamingMsgId)}
        />

        {voiceHint && (
          <p className="pointer-events-auto font-mono text-[8px] text-red-400/80">{voiceHint}</p>
        )}
      </div>

      <PrimeRealmNav activeRealm={activeRealm} onRealmChange={onRealmChange} />
      <PrimeFooter uplinkActive={uplinkActive} memorySynced={memorySynced} />
    </div>
  );
}
