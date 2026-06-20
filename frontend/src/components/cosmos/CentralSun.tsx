"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import * as THREE from "three";
import { SOLAR_TEXTURES } from "./solar-textures";
import { SUN_RADIUS, TRISHUL_SCALE } from "./cosmos-scale";

/** Solar System Scope sun — corona behind the Trishul core */
export function CentralSun() {
  const ref = useRef<THREE.Mesh>(null);
  const map = useTexture(SOLAR_TEXTURES.sun);
  map.colorSpace = THREE.SRGBColorSpace;

  useFrame((_, dt) => {
    if (ref.current) ref.current.rotation.y += dt * 0.06;
  });

  return (
    <group position={[0, TRISHUL_SCALE * 0.12, -0.2]}>
      <mesh ref={ref}>
        <sphereGeometry args={[SUN_RADIUS, 64, 64]} />
        <meshBasicMaterial map={map} toneMapped={false} />
      </mesh>
      <mesh>
        <sphereGeometry args={[SUN_RADIUS * 1.12, 32, 32]} />
        <meshBasicMaterial color="#ffaa44" transparent opacity={0.1} depthWrite={false} />
      </mesh>
      <pointLight color="#ffcc66" intensity={4} distance={TRISHUL_SCALE * 8} decay={2} />
      <pointLight color="#ff8844" intensity={2} distance={TRISHUL_SCALE * 5} decay={2} />
    </group>
  );
}
