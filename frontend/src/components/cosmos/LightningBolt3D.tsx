"use client";

import { useMemo } from "react";
import { Line } from "@react-three/drei";
import * as THREE from "three";
import { BLADE_TIP_LOCAL_Y, TRISHUL_PIVOT_Y, TRISHUL_SCALE } from "./cosmos-scale";

export function LightningBolt3D({
  target,
  active,
}: {
  target: THREE.Vector3 | null;
  active: boolean;
}) {
  const points = useMemo(() => {
    if (!target || !active) return null;
    const start = new THREE.Vector3(0, (BLADE_TIP_LOCAL_Y + TRISHUL_PIVOT_Y) * TRISHUL_SCALE, 0);
    const segments = 10;
    const seed = Math.random();
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const p = start.clone().lerp(target, t);
      const jitter = 0.35 * (1 - Math.abs(t - 0.5) * 1.5);
      p.x += (Math.sin(i * 3.7 + seed) - 0.5) * jitter;
      p.y += (Math.cos(i * 2.3 + seed) - 0.5) * jitter;
      p.z += (Math.sin(i * 4.1 + seed) - 0.5) * jitter;
      pts.push(p);
    }
    return pts;
  }, [target, active]);

  if (!points) return null;

  return <Line points={points} color="#88eeff" lineWidth={1.5} transparent opacity={0.85} />;
}
