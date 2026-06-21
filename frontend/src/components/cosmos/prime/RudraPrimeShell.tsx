"use client";

import { useState } from "react";
import type { LucideIcon } from "lucide-react";
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
  onQuickSubmit?: (query: string) => void;
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
  onQuickSubmit,
}: RudraPrimeShellProps) {
  const [voiceArmed, setVoiceArmed] = useState(true);
  const digestAction = actions.find((a) => a.label === "Run Digest");

  return (
    <div className="rudra-prime-shell rudra-prime-vignette pointer-events-none fixed inset-0 z-10 flex flex-col">
      <PrimeGridOverlay />

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

      <div className="prime-bottom-dock relative z-20 flex flex-col items-center gap-2 px-4 pb-6 sm:px-6">
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
    </div>
  );
}
