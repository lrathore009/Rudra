"use client";

import { useEffect, useState } from "react";
import { PerspectiveCamera } from "@react-three/drei";
import type { GrahaId } from "@/components/cosmos/navagraha-types";
import { SANCTUM_GRAHAS } from "@/data/navagraha-catalog";
import { SanctumEnvironment, SanctumPlatform } from "./SanctumEnvironment";
import { SanctumTrishul, type SanctumPhase } from "./SanctumTrishul";
import { SanctumPlanetField } from "./SanctumPlanetField";

export function SanctumSceneInner({
  processing,
  leadGrahaId,
  pulseGrahaIds,
}: {
  processing: boolean;
  leadGrahaId?: GrahaId;
  pulseGrahaIds: GrahaId[];
}) {
  const [phase, setPhase] = useState<SanctumPhase>("idle");

  useEffect(() => {
    if (!processing) {
      setPhase("completed");
      const t = setTimeout(() => setPhase("idle"), 1200);
      return () => clearTimeout(t);
    }
    setPhase("query");
    const t1 = setTimeout(() => setPhase("analysis"), 600);
    const t2 = setTimeout(() => setPhase("working"), 1800);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [processing]);

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 2.2, 14]} fov={42} />
      <SanctumEnvironment />
      <SanctumPlatform />
      <SanctumPlanetField grahas={SANCTUM_GRAHAS} leadGrahaId={leadGrahaId} pulseGrahaIds={pulseGrahaIds} />
      <SanctumTrishul phase={phase} processing={processing} />
    </>
  );
}
