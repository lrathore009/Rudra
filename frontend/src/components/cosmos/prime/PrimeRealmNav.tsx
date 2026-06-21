"use client";

import { REALMS, type RealmId } from "@/components/tablet/RealmRim";
import { cn } from "@/lib/utils";

export function PrimeRealmNav({
  activeRealm,
  onRealmChange,
}: {
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
}) {
  return (
    <nav className="prime-realm-nav pointer-events-auto px-4 pb-2" aria-label="Realms">
      {REALMS.map((r) => {
        const Icon = r.icon;
        const active = activeRealm === r.id;
        return (
          <button
            key={r.id}
            type="button"
            title={r.label}
            onClick={() => onRealmChange(active ? null : r.id)}
            className={cn("prime-realm-hex", active && "prime-realm-hex-active")}
            aria-pressed={active}
          >
            <Icon />
            <span>{r.cosmicLabel}</span>
          </button>
        );
      })}
    </nav>
  );
}
