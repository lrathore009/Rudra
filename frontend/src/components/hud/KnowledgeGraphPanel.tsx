"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Search, X } from "lucide-react";
import {
  getGraphEntityMemories,
  listGraphEntities,
  listGraphRelationships,
  type GraphEntity,
  type GraphRelationship,
} from "@/lib/api";
import { cn } from "@/lib/utils";

export function KnowledgeGraphPanel() {
  const [query, setQuery] = useState("");
  const [entities, setEntities] = useState<GraphEntity[]>([]);
  const [relationships, setRelationships] = useState<GraphRelationship[]>([]);
  const [selected, setSelected] = useState<GraphEntity | null>(null);
  const [linkedMemories, setLinkedMemories] = useState<
    Array<{ id: string; title: string; content: string }>
  >([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (q?: string) => {
    setLoading(true);
    try {
      const [e, r] = await Promise.all([
        listGraphEntities(q).catch(() => [] as GraphEntity[]),
        listGraphRelationships().catch(() => [] as GraphRelationship[]),
      ]);
      setEntities(e);
      setRelationships(r);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const t = setTimeout(() => void load(query || undefined), 300);
    return () => clearTimeout(t);
  }, [query, load]);

  useEffect(() => {
    if (!selected) {
      setLinkedMemories([]);
      return;
    }
    void getGraphEntityMemories(selected.id)
      .then(setLinkedMemories)
      .catch(() => setLinkedMemories([]));
  }, [selected]);

  const entityMap = useMemo(
    () => Object.fromEntries(entities.map((e) => [e.id, e.name])),
    [entities]
  );

  const selectedRels = useMemo(() => {
    if (!selected) return [];
    return relationships.filter(
      (r) => r.source_entity_id === selected.id || r.target_entity_id === selected.id
    );
  }, [relationships, selected]);

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <p className="font-terminal text-[8px] uppercase tracking-wider text-muted-foreground/70">
        Mala of memory · follow the thread
      </p>
      <div className="relative">
        <Search className="pointer-events-none absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-primary/40" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search nodes…"
          className="w-full border border-primary/20 bg-background/60 py-1.5 pl-7 pr-2 font-terminal text-[11px] text-foreground outline-none focus:border-primary/50"
        />
      </div>

      <div className="mala-thread min-h-0 flex-1 space-y-1 overflow-y-auto pr-1">
        {loading && (
          <p className="font-terminal text-[10px] text-muted-foreground/80">Mapping constellation…</p>
        )}
        {!loading && entities.length === 0 && (
          <p className="font-terminal text-[10px] text-muted-foreground/80">No nodes indexed yet.</p>
        )}
        {entities.map((entity) => (
          <button
            key={entity.id}
            type="button"
            onClick={() => setSelected(entity)}
            className={cn(
              "mala-bead-node flex w-full items-center gap-2 border border-primary/15 px-2 py-1.5 text-left transition hover:bg-primary/5",
              selected?.id === entity.id && "border-primary/40 bg-primary/10"
            )}
          >
            <span className="min-w-0 flex-1 truncate font-terminal text-[11px] text-foreground">
              {entity.name}
            </span>
            <span className="shrink-0 font-terminal text-[8px] uppercase text-muted-foreground/80">
              {entity.entity_type}
            </span>
          </button>
        ))}
      </div>

      {selected && (
        <div className="mt-1 border border-primary/25 bg-background/70 p-2 palm-scroll">
          <div className="mb-2 flex items-start justify-between gap-2">
            <div>
              <p className="font-hud text-[11px] neon">{selected.name}</p>
              <p className="font-terminal text-[8px] uppercase text-muted-foreground/90">
                {selected.entity_type}
              </p>
            </div>
            <button type="button" onClick={() => setSelected(null)} aria-label="Close">
              <X className="h-3.5 w-3.5 text-muted-foreground/90" />
            </button>
          </div>
          {selected.description && (
            <p className="mb-2 font-terminal text-[10px] leading-relaxed text-muted-foreground">
              {selected.description}
            </p>
          )}
          <p className="mb-1 font-terminal text-[8px] uppercase tracking-wider text-muted-foreground/80">
            Thread links
          </p>
          <div className="mb-2 max-h-16 space-y-0.5 overflow-y-auto mala-thread">
            {selectedRels.length === 0 && (
              <p className="font-terminal text-[9px] text-muted-foreground/70">No threads yet</p>
            )}
            {selectedRels.map((rel) => (
              <p key={rel.id} className="truncate font-terminal text-[9px] text-muted-foreground">
                {entityMap[rel.source_entity_id] ?? "?"} — {rel.relation_type} —{" "}
                {entityMap[rel.target_entity_id] ?? "?"}
              </p>
            ))}
          </div>
          <p className="mb-1 font-terminal text-[8px] uppercase tracking-wider text-muted-foreground/80">
            Linked memories
          </p>
          <div className="max-h-20 space-y-0.5 overflow-y-auto">
            {linkedMemories.length === 0 && (
              <p className="font-terminal text-[9px] text-muted-foreground/70">No memories yet</p>
            )}
            {linkedMemories.map((m) => (
              <p key={m.id} className="truncate font-terminal text-[9px] text-muted-foreground">
                {m.title}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
