"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import * as THREE from "three";
import { SOLAR_TEXTURES } from "./solar-textures";

/** Solar System Scope sun — corona behind the Trishul core */
export function CentralSun() {
  const ref = useRef<THREE.Mesh>(null);
  const map = useTexture(SOLAR_TEXTURES.sun);
  map.colorSpace = THREE.SRGBColorSpace;

  useFrame((_, dt) => {
    if (ref.current) ref.current.rotation.y += dt * 0.06;
  });

  return (
    <group>
      <mesh ref={ref}>
        <sphereGeometry args={[1.65, 64, 64]} />
        <meshBasicMaterial map={map} toneMapped={false} />
      </mesh>
      <mesh>
        <sphereGeometry args={[1.85, 32, 32]} />
        <meshBasicMaterial color="#ffaa44" transparent opacity={0.12} depthWrite={false} />
      </mesh>
      <pointLight color="#ffcc66" intensity={3.5} distance={22} decay={2} />
      <pointLight color="#ff8844" intensity={1.5} distance={14} decay={2} position={[0, 0, 0]} />
    </group>
  );
}
