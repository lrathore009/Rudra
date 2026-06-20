"use client";

import {
  Archive,
  BookOpen,
  Castle,
  Cog,
  Radar,
  Users,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type RealmId = "dominions" | "archive" | "council" | "scriptorium" | "horizon" | "engine";

export const REALMS: { id: RealmId; label: string; short: string; cosmicLabel: string; icon: LucideIcon }[] = [
  { id: "dominions", label: "Dominions", short: "DOM", cosmicLabel: "Domain Citadel", icon: Castle },
  { id: "archive", label: "Archive", short: "ARC", cosmicLabel: "Archive Vault", icon: Archive },
  { id: "council", label: "The Nine", short: "IX", cosmicLabel: "Intelligence Council", icon: Users },
  { id: "scriptorium", label: "Scriptorium", short: "SCR", cosmicLabel: "Scriptures Library", icon: BookOpen },
  { id: "horizon", label: "Horizon", short: "HOR", cosmicLabel: "Horizon Scanner", icon: Radar },
  { id: "engine", label: "Engine", short: "ENG", cosmicLabel: "Engine Control", icon: Cog },
];

export function RealmRim({
  active,
  onSelect,
  activeFacet,
}: {
  active: RealmId | null;
  onSelect: (id: RealmId | null) => void;
  activeFacet?: string;
}) {
  return (
    <nav className="realm-rim" aria-label="Realms">
      {REALMS.map((r) => {
        const Icon = r.icon;
        const isActive = active === r.id;
        return (
          <button
            key={r.id}
            type="button"
            title={r.label}
            onClick={() => onSelect(isActive ? null : r.id)}
            className={cn("realm-bead", isActive && "realm-bead-active")}
          >
            <span className="realm-bead-icon">
              <Icon className="h-3 w-3" />
            </span>
            <span className="realm-bead-label">{r.short}</span>
          </button>
        );
      })}
      {activeFacet && (
        <span className="realm-facet-hint font-terminal text-[8px] text-muted-foreground/70">
          planet · {activeFacet}
        </span>
      )}
    </nav>
  );
}
