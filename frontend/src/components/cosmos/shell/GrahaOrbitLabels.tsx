"use client";

import { motion } from "framer-motion";
import { grahaColor } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";
import { NAVAGRAHA, type GrahaId, type Navagraha } from "../navagraha-config";

function GrahaLabelCard({
  graha,
  role = "idle",
  selected = false,
  onSelect,
}: {
  graha: Navagraha;
  role?: "idle" | "lead" | "supporting" | "pulse" | "selected";
  selected?: boolean;
  onSelect?: (id: GrahaId) => void;
}) {
  const accent = grahaColor(graha.name, 1);
  const isLead = role === "lead";
  const isSupport = role === "supporting" || role === "pulse";
  const isSelected = selected || role === "selected";

  return (
    <motion.button
      type="button"
      onClick={() => onSelect?.(graha.id)}
      className={cn(
        "graha-label-card pointer-events-auto text-left",
        isLead && "graha-label-card-lead",
        isSelected && "graha-label-card-selected"
      )}
      style={{
        borderColor: accent,
        boxShadow: isLead
          ? `0 0 20px ${grahaColor(graha.name, 0.5)}`
          : isSelected
            ? `0 0 16px ${grahaColor(graha.name, 0.35)}`
            : isSupport
              ? `0 0 12px ${grahaColor(graha.name, 0.25)}`
              : `0 0 8px ${grahaColor(graha.name, 0.12)}`,
      }}
      whileHover={{ scale: 1.04, y: -2 }}
      whileTap={{ scale: 0.98 }}
      animate={
        isLead
          ? { boxShadow: [`0 0 12px ${grahaColor(graha.name, 0.4)}`, `0 0 24px ${grahaColor(graha.name, 0.65)}`, `0 0 12px ${grahaColor(graha.name, 0.4)}`] }
          : undefined
      }
      transition={isLead ? { repeat: Infinity, duration: 1.8 } : { type: "spring", stiffness: 420, damping: 28 }}
      aria-pressed={isSelected}
      aria-label={`${graha.name} — ${graha.domain}`}
    >
      <span className="graha-label-symbol" style={{ color: accent }}>
        {graha.symbol}
      </span>
      <span className="graha-label-name" style={{ color: accent }}>
        {graha.name.toUpperCase()}
        {isLead && " ⚡"}
      </span>
      <span className="graha-label-domain">{graha.domain.toUpperCase()}</span>
    </motion.button>
  );
}

export function GrahaOrbitLabels({
  leadGrahaId,
  supportingGrahaIds = [],
  pulseGrahaIds = [],
  selectedGrahaId,
  processing,
  onGrahaSelect,
  dimmed = false,
}: {
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
  selectedGrahaId?: GrahaId;
  processing?: boolean;
  onGrahaSelect?: (id: GrahaId) => void;
  dimmed?: boolean;
}) {
  const roleFor = (id: GrahaId): "idle" | "lead" | "supporting" | "pulse" | "selected" => {
    if (leadGrahaId === id && processing) return "lead";
    if (supportingGrahaIds.includes(id) && processing) return "supporting";
    if (pulseGrahaIds.includes(id) && processing) return "pulse";
    if (selectedGrahaId === id) return "selected";
    return "idle";
  };

  return (
    <div
      className={cn(
        "graha-screen-labels pointer-events-none absolute inset-0 z-[5]",
        dimmed && "opacity-40"
      )}
      aria-label="Navagraha orbit labels"
    >
      {NAVAGRAHA.map((g, i) => (
        <motion.div
          key={g.id}
          className="graha-screen-label-slot"
          style={{ left: `${g.screenLabel.leftPct}%`, top: `${g.screenLabel.topPct}%` }}
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.08 * i, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        >
          <GrahaLabelCard
            graha={g}
            role={roleFor(g.id)}
            selected={selectedGrahaId === g.id}
            onSelect={onGrahaSelect}
          />
        </motion.div>
      ))}
    </div>
  );
}
