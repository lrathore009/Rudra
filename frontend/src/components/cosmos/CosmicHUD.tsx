"use client";

import { useEffect, useRef } from "react";
import {
  Activity,
  Brain,
  CalendarClock,
  Mic,
  Radio,
  Search,
  Sparkles,
  Square,
  Upload,
  Volume2,
  VolumeX,
  X,
  type LucideIcon,
} from "lucide-react";
import { SutraWordmark } from "@/components/hud/SutraWordmark";
import { InkText } from "@/components/tablet/InkText";
import { AGENT_TAG, SUTRA_TICKER, facetColor, themeModeLabel, type RudraThemeMode } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";
import type { RealmId } from "@/components/tablet/RealmRim";
import { REALMS } from "@/components/tablet/RealmRim";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  streaming?: boolean;
}

const QUICK_ACTIONS: { icon: LucideIcon; label: string }[] = [
  { icon: Activity, label: "Brief" },
  { icon: Search, label: "Research" },
  { icon: CalendarClock, label: "Digest" },
  { icon: Sparkles, label: "Skills" },
];

export function CosmicHUD({
  themeMode,
  onThemeCycle,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  logLine,
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
  selectedAgent,
  activeFacetTag,
  onSelectAgent,
  agents,
  actions,
  activeRealm,
  onRealmChange,
  showResponse,
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
  selectedAgent?: string;
  activeFacetTag?: string;
  onSelectAgent: (type?: string) => void;
  agents: { type: string; name: string }[];
  actions: { icon: LucideIcon; label: string; run: () => void }[];
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
  showResponse: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant" && m.content);
  const latestUser = [...messages].reverse().find((m) => m.role === "user");
  const streaming = messages.find((m) => m.id === streamingMsgId);

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
      {/* top telemetry */}
      <header className="pointer-events-auto flex items-center justify-between px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <SutraWordmark className="text-sm sm:text-base" />
          <span className="hidden font-terminal text-[9px] uppercase tracking-widest text-muted-foreground/80 sm:inline">
            {greeting}
          </span>
        </div>
        <div className="flex items-center gap-2 font-terminal text-[10px] sm:gap-3">
          <button type="button" onClick={onThemeCycle} className="cosmic-ctl hidden sm:inline">
            {themeModeLabel(themeMode)}
          </button>
          <span className="flex items-center gap-1 neon-dim">
            <Radio className="h-3 w-3" />
            <span className="hidden sm:inline">{status}</span>
          </span>
          <span className="text-muted-foreground">{clock ? clock.toLocaleTimeString("en-GB") : "--:--"}</span>
          <button type="button" onClick={onLogout} className="cosmic-ctl hidden sm:inline">
            Exit
          </button>
          <button type="button" onClick={onToggleMute} className="cosmic-ctl-icon" title={muted ? "Unmute" : "Mute"}>
            {muted ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
          </button>
        </div>
      </header>

      {/* holographic response stream */}
      <div className="flex flex-1 flex-col items-center justify-end px-4 pb-2 sm:px-8">
        {showResponse && (latestAssistant || latestUser || streaming) && (
          <div className="cosmic-stream pointer-events-auto mb-4 w-full max-w-2xl text-center">
            {latestUser && (
              <p className="mb-2 font-terminal text-[10px] uppercase tracking-[0.2em] text-primary/70">
                ◇ {latestUser.content.slice(0, 120)}
                {latestUser.content.length > 120 ? "…" : ""}
              </p>
            )}
            {(streaming || latestAssistant) && (
              <div className="cosmic-response mx-auto max-w-xl">
                {streaming ? (
                  <InkText text={streaming.content} streaming streamed />
                ) : latestAssistant ? (
                  <InkText text={latestAssistant.content} streamed />
                ) : null}
              </div>
            )}
          </div>
        )}

        {/* planet selector strip */}
        <div className="pointer-events-auto mb-3 flex flex-wrap justify-center gap-1.5">
          <button
            type="button"
            onClick={() => onSelectAgent(undefined)}
            className={cn("cosmic-planet-pill", !selectedAgent && "cosmic-planet-pill-active")}
          >
            <Brain className="h-3 w-3" /> ALL
          </button>
          {agents.slice(0, 9).map((a) => {
            const tag = AGENT_TAG[a.type];
            return (
              <button
                key={a.type}
                type="button"
                title={a.name}
                onClick={() => onSelectAgent(selectedAgent === a.type ? undefined : a.type)}
                className={cn("cosmic-planet-pill", selectedAgent === a.type && "cosmic-planet-pill-active")}
                style={
                  selectedAgent === a.type
                    ? {
                        borderColor: facetColor(tag, 0.6),
                        boxShadow: `0 0 12px ${facetColor(tag, 0.35)}`,
                        color: facetColor(tag, 0.95),
                      }
                    : undefined
                }
              >
                {tag}
              </button>
            );
          })}
          {activeFacetTag && (
            <span className="self-center font-terminal text-[8px] text-muted-foreground/70">
              routing · {activeFacetTag}
            </span>
          )}
        </div>

        {/* quick actions */}
        <div className="pointer-events-auto mb-3 flex flex-wrap justify-center gap-2">
          {actions.map((a, i) => (
            <button
              key={a.label}
              type="button"
              disabled={processing}
              onClick={a.run}
              className="cosmic-action"
              title={a.label}
            >
              <a.icon className="h-3 w-3" />
              <span className="hidden sm:inline">{a.label}</span>
            </button>
          ))}
        </div>

        {/* command beam — minimal input, no box UI */}
        <form
          className="pointer-events-auto cosmic-command-beam mb-2 flex w-full max-w-xl items-center gap-2 px-2"
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
            className="cosmic-command-input min-w-0 flex-1 bg-transparent font-display text-sm outline-none sm:text-base"
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
      </div>

      {/* realm orbit controls */}
      <nav className="pointer-events-auto flex items-center justify-center gap-2 px-4 pb-4" aria-label="Realms">
        {REALMS.map((r) => {
          const Icon = r.icon;
          const active = activeRealm === r.id;
          return (
            <button
              key={r.id}
              type="button"
              title={r.label}
              onClick={() => onRealmChange(active ? null : r.id)}
              className={cn("cosmic-realm-orb", active && "cosmic-realm-orb-active")}
            >
              <Icon className="h-3.5 w-3.5" />
              <span className="text-[7px]">{r.short}</span>
            </button>
          );
        })}
      </nav>

      {/* footer telemetry */}
      <footer className="pointer-events-none flex items-center justify-between px-4 pb-3 font-terminal text-[8px] text-muted-foreground/60 sm:px-6">
        <span className="truncate">{SUTRA_TICKER[tickerIdx]}</span>
        <span className="mx-2 opacity-30">·</span>
        <span className="truncate opacity-70">{logLine}</span>
        <span className="ml-auto shrink-0 pl-2 opacity-50">{operator ?? "owner"}</span>
      </footer>
    </div>
  );
}

export { QUICK_ACTIONS };
