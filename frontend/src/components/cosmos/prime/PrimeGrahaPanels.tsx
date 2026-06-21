"use client";

import { grahaById, type GrahaId } from "../navagraha-config";
import { PRIME_GRAHA_PANELS } from "./prime-graha-config";
import { cn } from "@/lib/utils";

export function PrimeGrahaPanels({
  leadGrahaId,
  selectedGrahaId,
  onGrahaSelect,
}: {
  leadGrahaId?: GrahaId;
  selectedGrahaId?: GrahaId;
  onGrahaSelect?: (id: GrahaId) => void;
}) {
  return (
    <div className="prime-graha-layer" aria-label="Navagraha panels">
      {PRIME_GRAHA_PANELS.map((panel) => {
        const graha = grahaById(panel.id);
        if (!graha) return null;
        const isLead = leadGrahaId === panel.id;
        const isSelected = selectedGrahaId === panel.id;
        return (
          <div
            key={panel.id}
            className={cn("prime-graha-slot", panel.align === "right" && "prime-graha-slot-right")}
            style={{ left: `${panel.position.leftPct}%`, top: `${panel.position.topPct}%` }}
          >
            <button
              type="button"
              onClick={() => onGrahaSelect?.(panel.id)}
              className={cn("prime-graha-panel", panel.align === "right" && "prime-graha-panel-right")}
              style={{
                borderColor: panel.glow,
                boxShadow: isLead
                  ? `0 0 20px ${panel.glow}88`
                  : isSelected
                    ? `0 0 14px ${panel.glow}55`
                    : `0 0 8px ${panel.glow}33`,
              }}
            >
              <div className="prime-graha-symbol" style={{ color: panel.glow }}>
                {graha.symbol}
              </div>
              <div className="prime-graha-name" style={{ color: panel.glow }}>
                {graha.name.toUpperCase()}
                {isLead && " ⚡"}
              </div>
              <div className={cn("prime-graha-attrs", panel.align === "right" && "text-right")}>
                {panel.attributes.join(" · ")}
              </div>
            </button>
          </div>
        );
      })}
    </div>
  );
}
