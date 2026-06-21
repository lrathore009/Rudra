"use client";

import { REALMS, type RealmId } from "@/components/tablet/RealmRim";
import { cn } from "@/lib/utils";

export function SanctumRealmNav({
  activeRealm,
  onRealmChange,
}: {
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
}) {
  return (
    <nav className="mandala-realm-dots pointer-events-auto" aria-label="Realms">
      {REALMS.map((r) => {
        const active = activeRealm === r.id;
        return (
          <button
            key={r.id}
            type="button"
            title={r.cosmicLabel}
            onClick={() => onRealmChange(active ? null : r.id)}
            className={cn("mandala-realm-dot", active && "mandala-realm-dot-active")}
            aria-pressed={active}
            aria-label={r.label}
          />
        );
      })}
    </nav>
  );
}
