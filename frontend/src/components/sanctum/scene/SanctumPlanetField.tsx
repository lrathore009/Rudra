"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { GrahaId, Navagraha } from "@/components/cosmos/navagraha-types";
import { grahaPosition3D } from "@/components/cosmos/orbit-math";
import { SanctumPlanet } from "./SanctumPlanet";
import { SanctumOrbits } from "./SanctumOrbits";

function OrbitingPlanet({
  graha,
  highlighted,
  pulsing,
}: {
  graha: Navagraha;
  highlighted: boolean;
  pulsing: boolean;
}) {
  const groupRef = useRef<THREE.Group>(null);
  const angleRef = useRef(graha.angle);

  useFrame((_, dt) => {
    angleRef.current += dt * graha.speed;
    if (!groupRef.current) return;
    const p = grahaPosition3D(graha, angleRef.current);
    groupRef.current.position.set(p.x, p.y, p.z);
  });

  return (
    <group ref={groupRef}>
      <SanctumPlanet graha={graha} angle={graha.angle} highlighted={highlighted} pulsing={pulsing} local />
    </group>
  );
}

export function SanctumPlanetField({
  grahas,
  leadGrahaId,
  pulseGrahaIds,
}: {
  grahas: Navagraha[];
  leadGrahaId?: GrahaId;
  pulseGrahaIds: GrahaId[];
}) {
  return (
    <>
      <SanctumOrbits grahas={grahas} leadGrahaId={leadGrahaId} />
      {grahas.map((g) => (
        <OrbitingPlanet
          key={g.id}
          graha={g}
          highlighted={g.id === leadGrahaId}
          pulsing={pulseGrahaIds.includes(g.id)}
        />
      ))}
    </>
  );
}
