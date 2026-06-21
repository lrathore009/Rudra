"use client";

import { useMemo } from "react";
import * as THREE from "three";
import type { GrahaId, Navagraha } from "@/components/cosmos/navagraha-types";
import { createOrbitTubeGeometry } from "@/components/cosmos/orbit-math";

function OrbitRing({ graha, active }: { graha: Navagraha; active: boolean }) {
  const geo = useMemo(() => createOrbitTubeGeometry(graha, 128, active ? 0.055 : 0.038), [graha, active]);
  const mat = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: graha.orbitColor,
        transparent: true,
        opacity: active ? 0.55 : 0.22,
        depthWrite: false,
      }),
    [graha.orbitColor, active]
  );
  return <mesh geometry={geo} material={mat} />;
}

export function SanctumOrbits({
  grahas,
  leadGrahaId,
}: {
  grahas: Navagraha[];
  leadGrahaId?: GrahaId;
}) {
  return (
    <group>
      {grahas.map((g) => (
        <OrbitRing key={g.id} graha={g} active={g.id === leadGrahaId} />
      ))}
    </group>
  );
}
