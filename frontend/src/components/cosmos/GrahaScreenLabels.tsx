"use client";

import { grahaColor } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";
import { NAVAGRAHA, type GrahaId, type Navagraha } from "./navagraha-config";

export function GrahaLabelCard({
  graha,
  role = "idle",
  compact = false,
}: {
  graha: Navagraha;
  role?: "idle" | "lead" | "supporting" | "pulse";
  compact?: boolean;
}) {
  const accent = grahaColor(graha.name, 1);
  const isLead = role === "lead";
  const isSupport = role === "supporting" || role === "pulse";
  return (
    <div
      className={cn("graha-label-card", compact && "graha-label-card-compact", isLead && "graha-label-card-lead")}
      style={{
        borderColor: accent,
        boxShadow: isLead
          ? `0 0 20px ${grahaColor(graha.name, 0.5)}`
          : isSupport
            ? `0 0 12px ${grahaColor(graha.name, 0.25)}`
            : `0 0 8px ${grahaColor(graha.name, 0.12)}`,
      }}
    >
      <span className="graha-label-symbol" style={{ color: accent }}>
        {graha.symbol}
      </span>
      <span className="graha-label-name" style={{ color: accent }}>
        {graha.name.toUpperCase()}
        {isLead && " ⚡"}
      </span>
      <span className="graha-label-domain">{graha.domain.toUpperCase()}</span>
    </div>
  );
}

export function GrahaScreenLabels({
  leadGrahaId,
  supportingGrahaIds = [],
  pulseGrahaIds = [],
  processing,
  dimmed = false,
}: {
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
  processing?: boolean;
  dimmed?: boolean;
}) {
  const roleFor = (id: GrahaId): "idle" | "lead" | "supporting" | "pulse" => {
    if (leadGrahaId === id && processing) return "lead";
    if (supportingGrahaIds.includes(id) && processing) return "supporting";
    if (pulseGrahaIds.includes(id) && processing) return "pulse";
    return "idle";
  };

  return (
    <div
      className={cn("graha-screen-labels pointer-events-none absolute inset-0 z-[5]", dimmed && "opacity-40")}
      aria-hidden
    >
      {NAVAGRAHA.map((g) => (
        <div
          key={g.id}
          className="graha-screen-label-slot"
          style={{ left: `${g.screenLabel.leftPct}%`, top: `${g.screenLabel.topPct}%` }}
        >
          <GrahaLabelCard graha={g} role={roleFor(g.id)} />
        </div>
      ))}
    </div>
  );
}
