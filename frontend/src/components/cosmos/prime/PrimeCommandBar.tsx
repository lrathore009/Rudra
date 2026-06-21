"use client";

import { useRef } from "react";
import { Mic, Square } from "lucide-react";
import { cn } from "@/lib/utils";

function PrimeMandala() {
  return (
    <svg className="prime-mandala" viewBox="0 0 64 64" fill="none" aria-hidden>
      <circle cx="32" cy="32" r="28" stroke="rgba(201,160,64,0.35)" strokeWidth="0.75" />
      <circle cx="32" cy="32" r="18" stroke="rgba(0,212,255,0.25)" strokeWidth="0.5" />
      {[0, 45, 90, 135].map((deg) => (
        <line
          key={deg}
          x1="32"
          y1="32"
          x2={32 + 26 * Math.cos((deg * Math.PI) / 180)}
          y2={32 + 26 * Math.sin((deg * Math.PI) / 180)}
          stroke="rgba(201,160,64,0.2)"
          strokeWidth="0.5"
        />
      ))}
      <circle cx="32" cy="32" r="3" fill="rgba(0,212,255,0.4)" />
    </svg>
  );
}

export function PrimeCommandBar({
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  processing,
  placeholder,
  streamingActive,
}: {
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  processing: boolean;
  placeholder: string;
  streamingActive?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="prime-command-wrap pointer-events-auto">
      <form
        className="prime-command-bar"
        onSubmit={(e) => {
          e.preventDefault();
          if (processing && streamingActive) onStop();
          else onSubmit();
        }}
      >
        <PrimeMandala />
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          disabled={processing && !streamingActive}
          placeholder={placeholder}
          className="prime-command-input"
          autoComplete="off"
          aria-label="Command input"
        />
        <button
          type="button"
          onClick={onVoice}
          className={cn("prime-mic-btn", listening && "prime-mic-btn-active")}
          title="Voice uplink"
        >
          <Mic className="h-4 w-4" />
        </button>
        {processing && !streamingActive ? (
          <button type="button" onClick={onStop} className="prime-send-btn">
            <Square className="mr-1 inline h-3 w-3 fill-current" />
            Stop
          </button>
        ) : (
          <button type="submit" disabled={!input.trim() && !processing} className="prime-send-btn">
            Send
          </button>
        )}
      </form>
    </div>
  );
}
