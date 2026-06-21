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
    <header className="pointer-events-auto relative z-20 grid grid-cols-[1fr_auto_1fr] items-start gap-2 px-4 py-2.5 sm:px-6">
      <div className="prime-logo-row flex min-w-0 flex-col gap-0.5">
        <span className="inline-flex items-center gap-0.5 text-xl leading-none sm:text-2xl">
          <span className="prime-logo-gold">RUD</span>
          <span className="relative mx-0.5 inline-flex h-[1.1em] w-[0.5em] items-end justify-center" aria-hidden>
            <svg viewBox="0 0 24 48" className="h-full w-full" fill="none">
              <path
                d="M12 2 L12 18 M12 18 L4 42 M12 18 L20 42 M12 14 L8 8 M12 14 L16 8"
                stroke="#f0d070"
                strokeWidth="2.2"
                strokeLinecap="round"
                style={{ filter: "drop-shadow(0 0 6px rgba(201,160,64,0.8))" }}
              />
              <circle cx="12" cy="16" r="2.5" fill="rgba(0,212,255,0.9)" />
            </svg>
          </span>
          <span className="prime-logo-gold">A</span>
        </span>
        <span className="prime-tagline">Prime · The void holds your counsel</span>
      </div>

      <div className="flex items-center justify-center gap-1.5 pt-0.5">
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
