"use client";

import type { GrahaId } from "@/components/cosmos/navagraha-types";
import { GRAHA_PANELS } from "@/data/navagraha-catalog";
import { cn } from "@/lib/utils";

export function GrahaPanelLayer({
  leadGrahaId,
  selectedGrahaId,
  onGrahaSelect,
}: {
  leadGrahaId?: GrahaId;
  selectedGrahaId?: GrahaId;
  onGrahaSelect?: (id: GrahaId) => void;
}) {
  return (
    <div className="mandala-graha-layer" aria-label="Navagraha">
      {GRAHA_PANELS.map((panel) => {
        const isLead = leadGrahaId === panel.id;
        const dim = Boolean(leadGrahaId) && !isLead;
        const keyword = panel.attributes[0];

        return (
          <div
            key={panel.id}
            className={cn("mandala-graha-slot", panel.align === "right" && "mandala-graha-slot-right")}
            style={{ left: `${panel.position.leftPct}%`, top: `${panel.position.topPct}%` }}
          >
            <button
              type="button"
              onClick={() => onGrahaSelect?.(panel.id)}
              className={cn(
                "mandala-graha-chip",
                panel.align === "right" && "mandala-graha-chip-right",
                dim && "mandala-graha-dim",
                isLead && "mandala-graha-lead"
              )}
              style={{ borderColor: panel.glow, color: panel.glow }}
            >
              <span className="mandala-graha-symbol">{panel.symbol}</span>
              <span className="mandala-graha-name">{panel.name}</span>
              <span className="mandala-graha-keyword">{keyword}</span>
            </button>
          </div>
        );
      })}
    </div>
  );
}
