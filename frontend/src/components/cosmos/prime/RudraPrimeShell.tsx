"use client";

import { useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { GrahaId } from "@/components/cosmos/navagraha-types";
import { GrahaPanelLayer } from "@/components/sanctum/ui/GrahaPanelLayer";
import { CounselLogPane } from "@/components/sanctum/ui/CounselLogPane";
import { SanctumRealmNav } from "@/components/sanctum/ui/SanctumRealmNav";
import { SanctumFooter } from "@/components/sanctum/ui/SanctumFooter";
import { PrimeHeader } from "./PrimeHeader";
import { PrimeSidebar } from "./PrimeSidebar";
import { PrimeCommandBar } from "./PrimeCommandBar";
import { PrimeGridOverlay } from "./PrimeGridOverlay";

export interface RudraPrimeShellProps {
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  processing: boolean;
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  voiceHint?: string | null;
  placeholder: string;
  streamingMsgId: string | null;
  actions: { icon: LucideIcon; label: string; run: () => void }[];
  uplinkActive?: boolean;
  memorySynced?: boolean;
  onQuickSubmit?: (query: string) => void;
  leadGrahaId?: GrahaId;
  leadGrahaName?: string;
  counselText?: string;
  logLines: string[];
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
  onGrahaSelect?: (id: GrahaId) => void;
  selectedGrahaId?: GrahaId;
}

export function RudraPrimeShell({
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  processing,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  voiceHint,
  placeholder,
  streamingMsgId,
  actions,
  uplinkActive = true,
  memorySynced = true,
  onQuickSubmit,
  leadGrahaId,
  leadGrahaName,
  counselText,
  logLines,
  activeRealm,
  onRealmChange,
  onGrahaSelect,
  selectedGrahaId,
}: RudraPrimeShellProps) {
  const [voiceArmed, setVoiceArmed] = useState(true);
  const digestAction = actions.find((a) => a.label === "Run Digest");

  const counsel = useMemo(() => counselText, [counselText]);

  return (
    <div className="rudra-prime-shell mandala-shell rudra-prime-vignette pointer-events-none fixed inset-0 z-10 flex flex-col">
      <PrimeGridOverlay />

      <GrahaPanelLayer
        leadGrahaId={leadGrahaId}
        selectedGrahaId={selectedGrahaId}
        onGrahaSelect={onGrahaSelect}
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
        status={status}
        clock={clock}
        onLogout={onLogout}
        muted={muted}
        onToggleMute={onToggleMute}
        listening={listening}
        voiceArmed={voiceArmed}
      />

      <div className="flex flex-1" />

      <div className="prime-bottom-dock relative z-20 flex flex-col items-center gap-2 px-4 pb-2 sm:px-6">
        <CounselLogPane
          counselText={counsel}
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

        <SanctumRealmNav activeRealm={activeRealm} onRealmChange={onRealmChange} />

        {voiceHint && (
          <p className="pointer-events-auto font-mono text-[8px] text-red-400/80">{voiceHint}</p>
        )}
      </div>

      <SanctumFooter uplinkActive={uplinkActive} memorySynced={memorySynced} />
    </div>
  );
}
