"use client";

import { Mic, MicOff, Square, Stamp } from "lucide-react";
import { cn } from "@/lib/utils";

export function SutraField({
  value,
  onChange,
  onSubmit,
  onStop,
  onVoice,
  onToggleMode,
  processing,
  listening,
  muted: _muted,
  placeholder,
  voiceHint,
  mode,
  inputRef,
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  onToggleMode: () => void;
  processing: boolean;
  listening: boolean;
  muted: boolean;
  placeholder: string;
  voiceHint: string | null;
  mode: "agents" | "tools";
  inputRef: React.RefObject<HTMLInputElement | null>;
}) {
  return (
    <form
      className={cn("sutra-field", listening && "sutra-field-listening")}
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <button
        type="button"
        onClick={onToggleMode}
        className="sutra-mode-pill"
        title="Facet routing vs autonomous tools"
      >
        {mode === "agents" ? "◇ planets" : "◇ tools"}
      </button>
      <input
        ref={inputRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={processing}
        placeholder={placeholder}
        className="sutra-input font-display"
        autoFocus
      />
      {voiceHint && (
        <span className="hidden max-w-[140px] truncate font-terminal text-[8px] text-primary/80 sm:inline">
          {voiceHint}
        </span>
      )}
      <button
        type="button"
        onClick={onVoice}
        title="Voice command"
        className={cn("sutra-icon-btn", listening && "sutra-voice-active")}
      >
        {listening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
      </button>
      {processing ? (
        <button type="button" onClick={onStop} title="Release (Esc)" className="sutra-icon-btn sutra-stop">
          <Square className="h-3.5 w-3.5 fill-current" />
        </button>
      ) : (
        <button type="submit" disabled={!value.trim()} className="sutra-seal" title="Transmit command">
          <Stamp className="h-4 w-4" />
        </button>
      )}
    </form>
  );
}
