"use client";

import { X } from "lucide-react";
import { HudPanel } from "@/components/hud/HudPanel";
import type { RealmId } from "./RealmRim";
import { REALMS } from "./RealmRim";

export function RealmDrawer({
  realm,
  onClose,
  title,
  children,
}: {
  realm: RealmId | null;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}) {
  if (!realm) return null;
  const meta = REALMS.find((r) => r.id === realm);

  return (
    <>
      <button type="button" className="realm-backdrop" onClick={onClose} aria-label="Close realm" />
      <aside className="realm-drawer bark-texture" role="dialog" aria-label={meta?.label}>
        <header className="realm-drawer-header">
          <div>
            <p className="font-hud text-sm tracking-[0.12em] neon-dim">{title ?? meta?.label}</p>
            <p className="font-terminal text-[9px] text-muted-foreground/80">Turn the tablet · another face</p>
          </div>
          <button type="button" onClick={onClose} className="realm-drawer-close">
            <X className="h-4 w-4" />
          </button>
        </header>
        <div className="realm-drawer-body">{children}</div>
      </aside>
    </>
  );
}

/** Compact panel wrapper inside drawer */
export function RealmSection({ title, children }: { title?: string; children: React.ReactNode }) {
  if (title) {
    return (
      <HudPanel title={title} float={false} className="mb-3 max-h-[min(42vh,360px)]">
        {children}
      </HudPanel>
    );
  }
  return <div className="mb-3">{children}</div>;
}
