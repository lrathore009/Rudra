"use client";

import { useEffect, useRef } from "react";
import {
  Archive,
  BookOpen,
  Castle,
  Cog,
  Mic,
  Radar,
  Square,
  Upload,
  Users,
  Volume2,
  VolumeX,
  type LucideIcon,
} from "lucide-react";
import { SutraWordmark, RudraTagline } from "@/components/hud/SutraWordmark";
import { InkText } from "@/components/tablet/InkText";
import { FOOTER_TICKER_SEGMENTS, grahaColor, themeModeLabel, type RudraThemeMode } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";
import type { RealmId } from "@/components/tablet/RealmRim";
import { REALMS } from "@/components/tablet/RealmRim";

const REALM_ICONS: Record<RealmId, LucideIcon> = {
  dominions: Castle,
  archive: Archive,
  council: Users,
  scriptorium: BookOpen,
  horizon: Radar,
  engine: Cog,
};

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  streaming?: boolean;
}

function StatusPulse({ active }: { active: boolean }) {
  return (
    <span className={cn("cosmic-status-dot", active && "cosmic-status-dot-live")} aria-hidden />
  );
}

export function CosmicHUD({
  themeMode,
  onThemeCycle,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  tickerIdx,
  operator,
  messages,
  streamingMsgId,
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  processing,
  placeholder,
  voiceHint,
  leadGrahaName,
  supportingGrahaNames,
  actions,
  activeRealm,
  onRealmChange,
  showResponse,
  uplinkActive = true,
  memorySynced = true,
}: {
  themeMode: RudraThemeMode;
  onThemeCycle: () => void;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  greeting: string;
  logLine: string;
  tickerIdx: number;
  operator: string | null;
  messages: Message[];
  streamingMsgId: string | null;
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  processing: boolean;
  placeholder: string;
  voiceHint?: string | null;
  leadGrahaName?: string;
  supportingGrahaNames?: string[];
  actions: { icon: LucideIcon; label: string; run: () => void }[];
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
  showResponse: boolean;
  uplinkActive?: boolean;
  memorySynced?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant" && m.content);
  const latestUser = [...messages].reverse().find((m) => m.role === "user");
  const streaming = messages.find((m) => m.id === streamingMsgId);
  const nominal = status.toLowerCase().includes("nominal") || status.toLowerCase().includes("online");
  const footerSegment = FOOTER_TICKER_SEGMENTS[tickerIdx % FOOTER_TICKER_SEGMENTS.length];

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "/" && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="cosmic-hud pointer-events-none fixed inset-0 z-10 flex flex-col">
      <header className="pointer-events-auto grid grid-cols-[1fr_auto_1fr] items-start gap-2 px-4 py-3 sm:px-8">
        <div className="flex min-w-0 flex-col gap-1">
          <SutraWordmark className="text-sm sm:text-base" />
          <RudraTagline className="hidden sm:block" />
          {operator && (
            <span className="hidden font-terminal text-[7px] uppercase tracking-[0.2em] text-muted-foreground/50 lg:block">
              {greeting}
            </span>
          )}
        </div>
        <div className="flex justify-center pt-0.5">
          <span className={cn("cosmic-status-badge", nominal && "cosmic-status-badge-nominal")}>
            <span className="cosmic-status-signal" aria-hidden>
              ((o))
            </span>
            {nominal ? "Present · Nominal" : status}
          </span>
        </div>
        <div className="ml-auto flex items-center justify-end gap-2 font-terminal text-[10px] sm:gap-3">
          <button type="button" onClick={onThemeCycle} className="cosmic-ctl hidden sm:inline">
            {themeModeLabel(themeMode)}
          </button>
          <span className="text-muted-foreground tabular-nums">
            {clock ? clock.toLocaleTimeString("en-GB") : "--:--:--"}
          </span>
          <button type="button" onClick={onLogout} className="cosmic-ctl hidden sm:inline">
            Exit
          </button>
          <button type="button" onClick={onToggleMute} className="cosmic-ctl-icon" title={muted ? "Unmute" : "Mute"}>
            {muted ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
          </button>
        </div>
      </header>

      <div className="flex flex-1 flex-col items-center justify-end px-4 pb-1 sm:px-8">
        {showResponse && (processing || streaming || latestAssistant) && (latestAssistant || latestUser || streaming) && (
          <div className="cosmic-stream pointer-events-auto mb-3 w-full max-w-3xl text-center">
            {latestUser && processing && (
              <p className="mb-2 font-terminal text-[10px] uppercase tracking-[0.2em] text-primary/70">
                ◇ {latestUser.content.slice(0, 120)}
                {latestUser.content.length > 120 ? "…" : ""}
              </p>
            )}
            {(streaming || latestAssistant) && (
              <div className="cosmic-response mx-auto max-w-2xl">
                {streaming ? (
                  <InkText text={streaming.content} streaming streamed />
                ) : latestAssistant ? (
                  <InkText text={latestAssistant.content} streamed />
                ) : null}
              </div>
            )}
          </div>
        )}

        {processing && leadGrahaName && (
          <div className="pointer-events-none mb-2 flex flex-wrap items-center justify-center gap-2 font-terminal text-[9px] uppercase tracking-widest">
            <span className="text-primary/80">Rudra commanding</span>
            <span
              className="cosmic-graha-chip cosmic-graha-chip-lead"
              style={{ color: grahaColor(leadGrahaName, 0.95), borderColor: grahaColor(leadGrahaName, 0.5) }}
            >
              Lead · {leadGrahaName}
            </span>
            {supportingGrahaNames && supportingGrahaNames.length > 0 && (
              <span className="text-muted-foreground/70">Support · {supportingGrahaNames.join(" · ")}</span>
            )}
          </div>
        )}

        <form
          className="pointer-events-auto cosmic-command-panel mb-3 flex w-full max-w-4xl items-center gap-3 px-5 py-3.5"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            disabled={processing && !streamingMsgId}
            placeholder={placeholder}
            className="cosmic-command-input min-w-0 flex-1 bg-transparent font-display text-sm uppercase tracking-wide outline-none sm:text-base"
            autoComplete="off"
          />
          <button
            type="button"
            onClick={onVoice}
            className={cn("cosmic-icon-btn", listening && "cosmic-icon-btn-active")}
            title="Voice uplink"
          >
            <Mic className="h-4 w-4" />
          </button>
          {processing ? (
            <button type="button" onClick={onStop} className="cosmic-icon-btn cosmic-icon-btn-stop" title="Stop">
              <Square className="h-3.5 w-3.5 fill-current" />
            </button>
          ) : (
            <button type="submit" disabled={!input.trim()} className="cosmic-icon-btn cosmic-icon-btn-send" title="Transmit">
              <Upload className="h-4 w-4" />
            </button>
          )}
        </form>
        {voiceHint && (
          <p className="pointer-events-auto mb-2 font-terminal text-[9px] text-destructive/80">{voiceHint}</p>
        )}

        <div className="sr-only">
          {actions.map((a) => (
            <button key={a.label} type="button" onClick={a.run}>
              {a.label}
            </button>
          ))}
        </div>
      </div>

      <nav className="pointer-events-auto flex flex-wrap items-end justify-center gap-2 px-4 pb-3 sm:gap-2.5" aria-label="Realms">
        {REALMS.map((r) => {
          const Icon = REALM_ICONS[r.id];
          const active = activeRealm === r.id;
          return (
            <button
              key={r.id}
              type="button"
              title={r.label}
              onClick={() => onRealmChange(active ? null : r.id)}
              className={cn("cosmic-realm-tile", active && "cosmic-realm-tile-active")}
            >
              <Icon className="h-4 w-4" />
              <span>{r.cosmicLabel}</span>
            </button>
          );
        })}
      </nav>

      <footer className="pointer-events-none flex flex-wrap items-center justify-between gap-x-3 gap-y-1 px-4 pb-3 font-terminal text-[7px] uppercase tracking-[0.14em] text-muted-foreground/55 sm:px-8 sm:text-[8px]">
        <span className="cosmic-footer-status truncate">
          <StatusPulse active={uplinkActive} />
          Encrypted uplink · {uplinkActive ? "Active" : "Offline"}
          <StatusPulse active={memorySynced} />
          · {footerSegment}
        </span>
        <span className="ml-auto shrink-0">Trishula OS v1.0 · Rudra Core Online</span>
      </footer>
    </div>
  );
}
