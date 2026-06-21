"use client";

import type { GrahaId } from "@/components/cosmos/navagraha-types";
import { ObservatoryHeader } from "./ObservatoryHeader";
import { ObservatoryLeftPanel } from "./ObservatoryLeftPanel";
import { ObservatoryRightPanel } from "./ObservatoryRightPanel";
import { InstrumentDial } from "./InstrumentDial";
import { ObservationWindow } from "./ObservationWindow";

export interface ObservatoryShellProps {
  status: string;
  onLogout: () => void;
  logLines: string[];
  processing: boolean;
  leadGrahaId?: GrahaId;
  counselText?: string;
  uplinkActive?: boolean;
  systemsNominal?: boolean;
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  placeholder: string;
  streamingActive: boolean;
  onGrahaSelect?: (id: GrahaId) => void;
  selectedGrahaId?: GrahaId;
}

export function ObservatoryShell({
  onLogout,
  logLines,
  processing,
  leadGrahaId,
  counselText,
  uplinkActive = true,
  systemsNominal = true,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  placeholder,
  streamingActive,
  onGrahaSelect,
  selectedGrahaId,
}: ObservatoryShellProps) {
  const activeId: GrahaId = leadGrahaId ?? selectedGrahaId ?? "mangal";

  return (
    <div className="obs-root">
      <ObservatoryHeader onLogout={onLogout} />

      <ObservatoryLeftPanel
        logLines={logLines}
        uplinkActive={uplinkActive}
        systemsNominal={systemsNominal}
        processing={processing}
      />

      <InstrumentDial
        activeId={activeId}
        onSelect={(id) => onGrahaSelect?.(id)}
      />

      <ObservatoryRightPanel />

      <ObservationWindow activeId={activeId} counselText={counselText} processing={processing} />

      <form
        className="obs-command"
        onSubmit={(e) => {
          e.preventDefault();
          if (streamingActive) onStop();
          else onSubmit();
        }}
      >
        <span className="obs-command-prompt">&gt;_</span>
        <input
          className="obs-command-input"
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder={placeholder}
          aria-label="Counsel command"
        />
        <div className="obs-command-actions">
          <button
            type="button"
            className="obs-cmd-btn"
            onClick={onVoice}
            aria-pressed={listening}
          >
            {listening ? "MIC ON" : "VOICE"}
          </button>
          <button type="submit" className="obs-cmd-btn" disabled={!input.trim() && !streamingActive}>
            {streamingActive ? "STOP" : "SEND"}
          </button>
        </div>
      </form>
    </div>
  );
}
