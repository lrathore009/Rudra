"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Line } from "@react-three/drei";
import * as THREE from "three";

export function LightningBolt3D({
  origin,
  target,
  active,
}: {
  origin: THREE.Vector3;
  target: THREE.Vector3 | null;
  active: boolean;
}) {
  const groupRef = useRef<THREE.Group>(null);
  const seedRef = useRef(Math.random());

  const points = useMemo(() => {
    if (!target || !active) return null;
    const segments = 14;
    const seed = seedRef.current;
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const p = origin.clone().lerp(target, t);
      const jitter = 0.28 * (1 - Math.abs(t - 0.5) * 1.4);
      p.x += (Math.sin(i * 3.9 + seed) - 0.5) * jitter;
      p.y += (Math.cos(i * 2.7 + seed) - 0.5) * jitter;
      p.z += (Math.sin(i * 4.3 + seed) - 0.5) * jitter;
      pts.push(p);
    }
    return pts;
  }, [origin, target, active]);

  useFrame((state) => {
    if (groupRef.current && active) {
      groupRef.current.visible = Math.sin(state.clock.elapsedTime * 40) > -0.2;
    }
  });

  if (!points || !target) return null;

  return (
    <group ref={groupRef}>
      <Line points={points} color="#ccffff" lineWidth={2.2} transparent opacity={0.95} />
      <Line points={points} color="#88eeff" lineWidth={0.8} transparent opacity={0.5} />
      <mesh position={target}>
        <sphereGeometry args={[0.12, 12, 12]} />
        <meshBasicMaterial color="#ccffff" transparent opacity={0.7} />
      </mesh>
    </group>
  );
}
