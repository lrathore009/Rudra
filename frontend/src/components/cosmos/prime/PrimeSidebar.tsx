"use client";

import { Activity, Clock, FileText, Globe, Mic, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export function PrimeSidebar({
  onTime,
  onWikipedia,
  onVoice,
  onDigest,
  systemsNominal,
  listening,
}: {
  onTime: () => void;
  onWikipedia: () => void;
  onVoice: () => void;
  onDigest: () => void;
  systemsNominal: boolean;
  listening: boolean;
}) {
  const items: { icon: LucideIcon; label: string; sub?: string; onClick: () => void; active?: boolean }[] = [
    { icon: Clock, label: "Time", onClick: onTime },
    { icon: Globe, label: "Wikipedia", onClick: onWikipedia },
    { icon: Mic, label: "Voice", onClick: onVoice, active: listening },
    { icon: FileText, label: "Digest", onClick: onDigest },
    {
      icon: Activity,
      label: "System Diagnostics",
      sub: systemsNominal ? "Nominal" : "Degraded",
      onClick: () => {},
    },
  ];

  return (
    <aside className="prime-sidebar pointer-events-auto" aria-label="Prime modules">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <button
            key={item.label}
            type="button"
            onClick={item.onClick}
            className={cn("prime-sidebar-btn", item.active && "prime-voice-pill")}
          >
            <Icon />
            <span>{item.label}</span>
            {item.sub && <span className="prime-sidebar-nominal">{item.sub}</span>}
          </button>
        );
      })}
    </aside>
  );
}
