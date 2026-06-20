"use client";

import { useCallback, useEffect, useState } from "react";
import { Calendar, Mail, Plug, RefreshCw, Sparkles } from "lucide-react";
import {
  connectMockIntegration,
  generateDailyBriefing,
  generateSpokenDigest,
  getCommandStack,
  listCalendarEvents,
  listIntegrations,
  listRecentEmails,
  syncExecutiveSources,
  type BriefingPayload,
  type CalendarEvent,
  type EmailMessage,
  type IntegrationStatus,
} from "@/lib/api";

export function DailyBriefingPanel() {
  const [integrations, setIntegrations] = useState<IntegrationStatus[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [emails, setEmails] = useState<EmailMessage[]>([]);
  const [briefing, setBriefing] = useState<BriefingPayload | null>(null);
  const [commitmentCount, setCommitmentCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [i, e, m, stack] = await Promise.all([
        listIntegrations().catch(() => [] as IntegrationStatus[]),
        listCalendarEvents().catch(() => [] as CalendarEvent[]),
        listRecentEmails().catch(() => [] as EmailMessage[]),
        getCommandStack().catch(() => null),
      ]);
      setIntegrations(i);
      setEvents(e);
      setEmails(m);
      const commitments = (stack?.commitments as unknown[] | undefined) ?? [];
      setCommitmentCount(commitments.length);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function connectStack() {
    await connectMockIntegration();
    await syncExecutiveSources();
    await refresh();
  }

  async function runSync() {
    setSyncing(true);
    try {
      await syncExecutiveSources();
      await refresh();
    } finally {
      setSyncing(false);
    }
  }

  const [spokenText, setSpokenText] = useState<string | null>(null);

  async function runBriefing() {
    setBriefing(await generateDailyBriefing());
  }

  async function runSpokenBriefing() {
    const digest = await generateSpokenDigest();
    setSpokenText(digest.text);
    if (digest.audio?.mode === "browser" && typeof window !== "undefined" && "speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(digest.text);
      u.rate = 0.95;
      window.speechSynthesis.speak(u);
    }
  }

  const connectedCount = integrations.filter((i) => i.connected).length;

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <div className="flex items-center justify-between gap-1">
        <span className="font-terminal text-[9px] uppercase text-amber-300/45">
          {connectedCount > 0 ? `${connectedCount} sources live` : "Command stack offline"}
        </span>
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => void runSync()}
            disabled={syncing}
            className="border border-amber-400/25 px-1.5 py-0.5 font-terminal text-[8px] uppercase text-amber-200/60 hover:bg-amber-500/10"
            title="Sync all tiers"
          >
            <RefreshCw className={`inline h-2.5 w-2.5 ${syncing ? "animate-spin" : ""}`} />
          </button>
          {connectedCount === 0 && (
            <button
              type="button"
              onClick={() => void connectStack()}
              className="border border-amber-400/25 px-2 py-0.5 font-terminal text-[8px] uppercase text-amber-200/60 hover:bg-amber-500/10"
            >
              <Plug className="inline h-2.5 w-2.5" /> Connect
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <p className="font-terminal text-[10px] text-amber-300/40">Loading executive intel…</p>
      ) : (
        <>
          <section>
            <p className="mb-1 flex items-center gap-1 font-terminal text-[8px] uppercase text-amber-300/40">
              <Calendar className="h-3 w-3" /> Meetings · {events.length}
            </p>
            <div className="space-y-0.5">
              {events.slice(0, 3).map((ev, idx) => (
                <p key={idx} className="truncate font-terminal text-[9px] text-amber-200/60">
                  {ev.starts_at} · {ev.title}
                </p>
              ))}
            </div>
          </section>

          <section>
            <p className="mb-1 flex items-center gap-1 font-terminal text-[8px] uppercase text-amber-300/40">
              <Mail className="h-3 w-3" /> Inbox · {commitmentCount} commitments
            </p>
            <div className="space-y-0.5">
              {emails.filter((e) => e.needs_attention).slice(0, 3).map((mail, idx) => (
                <p key={idx} className="truncate font-terminal text-[9px] text-amber-200/70">
                  {mail.subject}
                </p>
              ))}
            </div>
          </section>

          {integrations.length > 0 && (
            <section>
              <p className="mb-1 font-terminal text-[8px] uppercase text-amber-300/40">Connect order</p>
              <div className="flex flex-wrap gap-1">
                {integrations.slice(0, 6).map((i) => (
                  <span
                    key={i.provider}
                    className={`font-terminal text-[7px] uppercase px-1 py-0.5 border ${
                      i.connected
                        ? "border-emerald-400/40 text-emerald-200/70"
                        : "border-amber-400/15 text-amber-300/35"
                    }`}
                  >
                    {i.provider}
                  </span>
                ))}
              </div>
            </section>
          )}
        </>
      )}

      <div className="mt-auto flex gap-1">
        <button
          type="button"
          onClick={() => void runBriefing()}
          className="flex flex-1 items-center justify-center gap-1 border border-amber-400/30 py-1 font-terminal text-[9px] uppercase tracking-wider text-amber-200/70 hover:bg-amber-500/10"
        >
          <Sparkles className="h-3 w-3" /> Brief
        </button>
        <button
          type="button"
          onClick={() => void runSpokenBriefing()}
          className="flex flex-1 items-center justify-center gap-1 border border-amber-400/30 py-1 font-terminal text-[9px] uppercase tracking-wider text-amber-200/70 hover:bg-amber-400/10"
        >
          <Sparkles className="h-3 w-3" /> Speak
        </button>
      </div>

      {briefing && (
        <pre className="max-h-28 overflow-y-auto whitespace-pre-wrap font-terminal text-[9px] leading-relaxed text-amber-200/60">
          {briefing.content}
        </pre>
      )}
      {spokenText && (
        <pre className="max-h-28 overflow-y-auto whitespace-pre-wrap font-terminal text-[9px] leading-relaxed text-amber-200/70">
          {spokenText}
        </pre>
      )}
    </div>
  );
}
