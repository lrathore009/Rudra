"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** Glowing elliptical orbit rings around Trishul — matches preview arc lines */
export function PrimeOrbitalRings3D({ reducedMotion }: { reducedMotion?: boolean }) {
  const groupRef = useRef<THREE.Group>(null);

  const rings = useMemo(
    () => [
      { rx: 11.5, ry: 4.2, lift: 0, color: "#00d4ff", opacity: 0.22, tilt: 0.12 },
      { rx: 10.8, ry: 3.8, lift: 0.5, color: "#00d4ff", opacity: 0.16, tilt: -0.18 },
      { rx: 12.2, ry: 4.5, lift: -0.3, color: "#c9a040", opacity: 0.12, tilt: 0.35 },
      { rx: 9.5, ry: 3.2, lift: 1.2, color: "#bb55ff", opacity: 0.14, tilt: -0.42 },
      { rx: 13.5, ry: 5.0, lift: -0.8, color: "#4488ff", opacity: 0.1, tilt: 0.08 },
    ],
    []
  );

  useFrame((state) => {
    if (!groupRef.current || reducedMotion) return;
    groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.08) * 0.06;
  });

  return (
    <group ref={groupRef} position={[0, 0.2, 0]}>
      {rings.map((r, i) => (
        <mesh key={i} rotation={[Math.PI / 2 + r.tilt, 0, i * 0.4]} position={[0, r.lift, 0]}>
          <ringGeometry args={[r.rx * 0.92, r.rx, 128]} />
          <meshBasicMaterial
            color={r.color}
            transparent
            opacity={r.opacity}
            side={THREE.DoubleSide}
            depthWrite={false}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      ))}
      {/* vertical crosshair plane glow */}
      <mesh rotation={[0, 0, 0]}>
        <torusGeometry args={[8.5, 0.015, 8, 128]} />
        <meshBasicMaterial color="#00d4ff" transparent opacity={0.08} depthWrite={false} />
      </mesh>
    </group>
  );
}
