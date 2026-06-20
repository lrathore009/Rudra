"use client";

import {
  Archive,
  BookOpen,
  Briefcase,
  Compass,
  Cog,
  Users,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type RealmId = "dominions" | "archive" | "council" | "scriptorium" | "horizon" | "engine";

export const REALMS: { id: RealmId; label: string; short: string; icon: LucideIcon }[] = [
  { id: "dominions", label: "Dominions", short: "DOM", icon: Briefcase },
  { id: "archive", label: "Archive", short: "ARC", icon: Archive },
  { id: "council", label: "The Nine", short: "IX", icon: Users },
  { id: "scriptorium", label: "Scriptorium", short: "SCR", icon: BookOpen },
  { id: "horizon", label: "Horizon", short: "HOR", icon: Compass },
  { id: "engine", label: "Engine", short: "ENG", icon: Cog },
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
        <span className="realm-facet-hint font-terminal text-[8px] text-amber-200/35">
          facet · {activeFacet}
        </span>
      )}
    </nav>
  );
}
