"use client";

import { useCallback, useEffect, useState } from "react";
import { BookOpen, Mic, Plus, RefreshCw, Search, TrendingUp } from "lucide-react";
import {
  addResearchWatchlist,
  generateSpokenResearchBrief,
  getResearchLibrary,
  searchResearchLibrary,
  type ResearchLibraryPayload,
  type ResearchReportSummary,
} from "@/lib/api";

export function ResearchLibraryPanel() {
  const [library, setLibrary] = useState<ResearchLibraryPayload | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchHits, setSearchHits] = useState<ResearchReportSummary[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [spokenText, setSpokenText] = useState<string | null>(null);
  const [newTopic, setNewTopic] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setLibrary(await getResearchLibrary());
      setSearchHits(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function runSearch() {
    if (!searchQuery.trim()) {
      setSearchHits(null);
      return;
    }
    setSearchHits(await searchResearchLibrary(searchQuery.trim()));
  }

  async function runSpokenBrief() {
    const brief = await generateSpokenResearchBrief(searchQuery.trim() || undefined);
    setSpokenText(brief.text);
    if (brief.audio?.mode === "browser" && typeof window !== "undefined" && "speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(brief.text);
      u.rate = 0.95;
      window.speechSynthesis.speak(u);
    }
  }

  async function addTopic() {
    const topic = newTopic.trim();
    if (!topic) return;
    await addResearchWatchlist(topic, topic);
    setNewTopic("");
    await refresh();
  }

  const reports = searchHits ?? library?.reports ?? [];
  const trends = library?.trends;

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <div className="flex items-center justify-between gap-1">
        <span className="font-terminal text-[9px] uppercase text-amber-300/45">
          {trends ? `${trends.count} reports · conf ${trends.avg_confidence.toFixed(2)}` : "Research library"}
        </span>
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => void refresh()}
            disabled={loading}
            className="border border-amber-400/25 px-1.5 py-0.5 font-terminal text-[8px] uppercase text-amber-200/60 hover:bg-amber-500/10"
            title="Refresh library"
          >
            <RefreshCw className={`inline h-2.5 w-2.5 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            type="button"
            onClick={() => void runSpokenBrief()}
            className="border border-amber-400/25 px-1.5 py-0.5 font-terminal text-[8px] uppercase text-amber-200/60 hover:bg-amber-500/10"
            title="Spoken research brief"
          >
            <Mic className="inline h-2.5 w-2.5" /> Speak
          </button>
        </div>
      </div>

      {trends && (
        <div className="flex items-center gap-2 font-terminal text-[9px] text-amber-200/50">
          <TrendingUp className="h-3 w-3 neon-dim" />
          <span>Stale {trends.stale_count}</span>
          {library?.watchlist?.length ? (
            <span className="truncate">Watch: {library.watchlist.map((w) => w.topic).join(", ")}</span>
          ) : null}
        </div>
      )}

      <form
        className="flex gap-1"
        onSubmit={(e) => {
          e.preventDefault();
          void runSearch();
        }}
      >
        <input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Hybrid search…"
          className="min-w-0 flex-1 rounded border border-amber-400/20 bg-stone-950/30 px-2 py-0.5 font-terminal text-[10px] text-amber-50 outline-none placeholder:text-amber-300/30"
        />
        <button
          type="submit"
          className="border border-amber-400/25 px-1.5 py-0.5 font-terminal text-[8px] uppercase text-amber-200/60 hover:bg-amber-500/10"
        >
          <Search className="inline h-2.5 w-2.5" />
        </button>
      </form>

      <div className="min-h-0 flex-1 space-y-1 overflow-y-auto pr-0.5">
        {reports.length === 0 ? (
          <p className="font-terminal text-[10px] text-amber-200/40">No reports yet — run /research or save via agent.</p>
        ) : (
          reports.map((r) => (
            <div key={r.id} className="rounded border border-amber-400/10 px-2 py-1">
              <div className="flex items-start gap-1.5">
                <BookOpen className="mt-0.5 h-3 w-3 shrink-0 neon-dim" />
                <div className="min-w-0">
                  <p className="truncate font-terminal text-[10px] text-amber-100/80">{r.title}</p>
                  <p className="font-terminal text-[8px] text-amber-300/45">
                    conf {r.confidence_score.toFixed(2)}
                    {"score" in r && r.score != null ? ` · rrf ${r.score.toFixed(3)}` : ""}
                  </p>
                  {"snippet" in r && r.snippet ? (
                    <p className="line-clamp-2 font-terminal text-[9px] leading-tight text-amber-200/45">{r.snippet}</p>
                  ) : null}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <form
        className="flex gap-1 border-t border-amber-400/10 pt-1"
        onSubmit={(e) => {
          e.preventDefault();
          void addTopic();
        }}
      >
        <input
          value={newTopic}
          onChange={(e) => setNewTopic(e.target.value)}
          placeholder="Add watchlist topic…"
          className="min-w-0 flex-1 rounded border border-amber-400/20 bg-stone-950/30 px-2 py-0.5 font-terminal text-[10px] text-amber-50 outline-none placeholder:text-amber-300/30"
        />
        <button
          type="submit"
          className="border border-amber-400/25 px-1.5 py-0.5 font-terminal text-[8px] uppercase text-amber-200/60 hover:bg-amber-500/10"
        >
          <Plus className="inline h-2.5 w-2.5" />
        </button>
      </form>

      {spokenText ? (
        <p className="line-clamp-3 border-t border-amber-400/10 pt-1 font-terminal text-[9px] leading-relaxed text-amber-200/55">
          {spokenText}
        </p>
      ) : null}
    </div>
  );
}
