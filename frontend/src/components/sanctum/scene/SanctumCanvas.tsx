"use client";

import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import type { GrahaId } from "@/components/cosmos/navagraha-types";
import { SanctumSceneInner } from "./SanctumSceneInner";

export function SanctumCanvas({
  processing,
  leadGrahaId,
  pulseGrahaIds = [],
}: {
  processing: boolean;
  leadGrahaId?: GrahaId;
  pulseGrahaIds?: GrahaId[];
}) {
  return (
    <Canvas
      className="cosmic-canvas"
      dpr={[1, 1.75]}
      gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
      shadows
      style={{ background: "transparent" }}
    >
      <Suspense fallback={null}>
        <SanctumSceneInner
          processing={processing}
          leadGrahaId={leadGrahaId}
          pulseGrahaIds={pulseGrahaIds}
        />
      </Suspense>
    </Canvas>
  );
}
