"use client";

import { useCallback, useEffect, useState } from "react";
import { BookOpen, Briefcase, Compass, FileText, Layers, Plane, Sparkles } from "lucide-react";
import {
  buildDeck,
  createConciergeRequest,
  createTrip,
  getConciergeRequests,
  getLuxuryDesk,
  getOpsRunbook,
  getPresentationDecks,
  getTravelTrips,
  getWritingDrafts,
  librarianSearch,
  type DomainDeck,
  type DomainDraft,
  type DomainRequest,
  type DomainTrip,
} from "@/lib/api";
import { facetColor } from "@/lib/rudra-theme";

const TABS = [
  { id: "kl", label: "LIBRARIAN", short: "KL", icon: BookOpen },
  { id: "cg", label: "CONCIERGE", short: "CG", icon: Compass },
  { id: "tr", label: "TRAVEL", short: "TR", icon: Plane },
  { id: "lx", label: "LUXURY", short: "LX", icon: Sparkles },
  { id: "wr", label: "WRITING", short: "WR", icon: FileText },
  { id: "pr", label: "PRESENT", short: "PR", icon: Layers },
  { id: "op", label: "OPS", short: "OP", icon: Briefcase },
] as const;

type TabId = (typeof TABS)[number]["id"];

export function SpecialistHubPanel() {
  const [tab, setTab] = useState<TabId>("kl");
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Array<{ type: string; title: string; snippet?: string; score?: number }>>([]);
  const [requests, setRequests] = useState<DomainRequest[]>([]);
  const [trips, setTrips] = useState<DomainTrip[]>([]);
  const [luxury, setLuxury] = useState<{ trends: { count: number; avg_exclusivity: number }; snapshots: unknown[] } | null>(null);
  const [drafts, setDrafts] = useState<DomainDraft[]>([]);
  const [decks, setDecks] = useState<DomainDeck[]>([]);
  const [ops, setOps] = useState<{ maintenance_due: Array<{ title: string; next_due: string }> } | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      if (tab === "kl" && query.trim()) {
        setHits(await librarianSearch(query.trim()));
      } else if (tab === "cg") {
        setRequests(await getConciergeRequests());
      } else if (tab === "tr") {
        setTrips(await getTravelTrips());
      } else if (tab === "lx") {
        setLuxury(await getLuxuryDesk());
      } else if (tab === "wr") {
        setDrafts(await getWritingDrafts());
      } else if (tab === "pr") {
        setDecks(await getPresentationDecks());
      } else if (tab === "op") {
        setOps(await getOpsRunbook());
      }
    } finally {
      setLoading(false);
    }
  }, [tab, query]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <p className="font-terminal text-[8px] uppercase tracking-wider text-muted-foreground/70">
        Nine planets · silent counsel
      </p>
      <div className="flex flex-wrap gap-1">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            title={t.label}
            className={`border px-1.5 py-0.5 font-terminal text-[8px] uppercase ${
              tab === t.id
                ? "border-primary/50 text-foreground"
                : "border-primary/15 text-muted-foreground/90"
            }`}
            style={
              tab === t.id
                ? {
                    background: facetColor(t.short, 0.12),
                    borderColor: facetColor(t.short, 0.45),
                    color: facetColor(t.short, 0.95),
                  }
                : undefined
            }
          >
            {t.short}
          </button>
        ))}
      </div>

      {tab === "kl" && (
        <form
          className="flex gap-1"
          onSubmit={(e) => {
            e.preventDefault();
            void refresh();
          }}
        >
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Unified search…"
            className="min-w-0 flex-1 rounded border border-primary/20 bg-secondary/80 px-2 py-0.5 font-terminal text-[10px] text-foreground outline-none"
          />
        </form>
      )}

      <div className="min-h-0 flex-1 overflow-y-auto font-terminal text-[9px] text-muted-foreground">
        {loading && <p className="text-muted-foreground/70">Loading…</p>}
        {tab === "kl" &&
          hits.map((h, i) => (
            <p key={i} className="mb-1">
              [{h.type}] {h.title} {h.score != null ? `· ${h.score.toFixed(3)}` : ""}
            </p>
          ))}
        {tab === "cg" &&
          requests.map((r) => (
            <p key={r.id} className="mb-1">
              [{r.status}] {r.title}
            </p>
          ))}
        {tab === "tr" &&
          trips.map((t) => (
            <p key={t.id} className="mb-1">
              {t.title} · {t.legs?.length ?? 0} legs
            </p>
          ))}
        {tab === "lx" && luxury && (
          <p>
            {luxury.trends.count} snapshots · exclusivity {luxury.trends.avg_exclusivity.toFixed(2)}
          </p>
        )}
        {tab === "wr" &&
          drafts.map((d) => (
            <p key={d.id} className="mb-1">
              [{d.status}] {d.title} v{d.version}
            </p>
          ))}
        {tab === "pr" &&
          decks.map((d) => (
            <p key={d.id} className="mb-1">
              {d.title} · {d.slides} slides
            </p>
          ))}
        {tab === "op" &&
          ops?.maintenance_due?.map((m, i) => (
            <p key={i} className="mb-1">
              Due {m.next_due}: {m.title}
            </p>
          ))}
      </div>

      {tab === "cg" && (
        <button
          type="button"
          className="border border-primary/25 px-2 py-0.5 font-terminal text-[8px] uppercase text-muted-foreground"
          onClick={() =>
            void createConciergeRequest("Quick request", "Logged from HUD").then(() => refresh())
          }
        >
          + Request
        </button>
      )}
      {tab === "tr" && (
        <button
          type="button"
          className="border border-primary/25 px-2 py-0.5 font-terminal text-[8px] uppercase text-muted-foreground"
          onClick={() =>
            void createTrip("HUD trip", ["Tokyo", "Dubai"]).then(() => refresh())
          }
        >
          + Trip
        </button>
      )}
      {tab === "pr" && (
        <button
          type="button"
          className="border border-primary/25 px-2 py-0.5 font-terminal text-[8px] uppercase text-muted-foreground"
          onClick={() =>
            void buildDeck("HUD deck", "Rudra OS overview").then(() => refresh())
          }
        >
          + Build deck
        </button>
      )}
    </div>
  );
}
