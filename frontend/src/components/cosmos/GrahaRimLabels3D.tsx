"use client";

import { Html } from "@react-three/drei";
import { NAVAGRAHA, type GrahaId } from "./navagraha-config";
import { grahaRimLabelPosition } from "./orbit-math";
import { GrahaLabelCard } from "./GrahaScreenLabels";

export function GrahaRimLabels3D({
  leadGrahaId,
  supportingGrahaIds = [],
  pulseGrahaIds = [],
  processing,
}: {
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
  processing?: boolean;
}) {
  const roleFor = (id: GrahaId): "idle" | "lead" | "supporting" | "pulse" => {
    if (leadGrahaId === id && processing) return "lead";
    if (supportingGrahaIds.includes(id) && processing) return "supporting";
    if (pulseGrahaIds.includes(id) && processing) return "pulse";
    return "idle";
  };

  return (
    <group>
      {NAVAGRAHA.map((g) => {
        const pos = grahaRimLabelPosition(g);
        return (
          <Html
            key={g.id}
            position={[pos.x, pos.y, pos.z]}
            center
            distanceFactor={14}
            zIndexRange={[80, 0]}
            transform
            sprite
            style={{ pointerEvents: "none" }}
          >
            <GrahaLabelCard graha={g} role={roleFor(g.id)} />
          </Html>
        );
      })}
    </group>
  );
}
