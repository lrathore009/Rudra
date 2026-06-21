"use client";

import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";

function VoiceWaveform({ active }: { active: boolean }) {
  if (!active) return null;
  return (
    <span className="prime-waveform" aria-hidden>
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} />
      ))}
    </span>
  );
}

export function PrimeHeader({
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  listening,
  voiceArmed,
}: {
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  listening: boolean;
  voiceArmed: boolean;
}) {
  const nominal = status.toLowerCase().includes("nominal") || status.toLowerCase().includes("online");

  return (
    <header className="pointer-events-auto relative z-20 flex items-start justify-between gap-4 px-4 py-2.5 sm:px-6">
      <div className="flex items-center gap-1.5 pt-0.5">
        <span className={cn("prime-status-pill", nominal && "prime-voice-pill")}>
          <span aria-hidden>(( o ))</span>
          {nominal ? "Present · Nominal" : status}
        </span>
        <span className={cn("prime-status-pill", (listening || voiceArmed) && "prime-voice-pill")}>
          Voice armed
          <VoiceWaveform active={listening || voiceArmed} />
        </span>
      </div>

      <div className="ml-auto flex items-center justify-end gap-2 text-[8px] tracking-widest">
        <span className="prime-ctl prime-ctl-static">PRIME</span>
        <span className="tabular-nums text-[var(--prime-cyan)] opacity-80">
          {clock ? clock.toLocaleTimeString("en-GB") : "--:--:--"}
        </span>
        <button type="button" onClick={onLogout} className="prime-ctl">
          Exit
        </button>
        <button type="button" onClick={onToggleMute} className="prime-ctl-icon" title={muted ? "Unmute" : "Mute"}>
          {muted ? <VolumeX className="h-3 w-3" /> : <Volume2 className="h-3 w-3" />}
        </button>
      </div>
    </header>
  );
}
