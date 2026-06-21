"use client";

import { RudraPrimeShell } from "./prime";
import { PrimeBackground } from "./prime/PrimeBackground";
import type { LucideIcon } from "lucide-react";

export function CosmicPlayground({
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  logLine,
  processing,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  voiceHint,
  placeholder,
  actions,
  operator,
  streamingMsgId,
  uplinkActive = true,
  onQuickSubmit,
}: {
  operator: string | null;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  greeting: string;
  logLine: string;
  processing: boolean;
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
  onQuickSubmit?: (query: string) => void;
}) {
  return (
    <div className="cosmic-playground prime-stage relative h-screen w-screen overflow-hidden">
      <PrimeBackground />

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
        onQuickSubmit={onQuickSubmit}
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
    </div>
  );
}
