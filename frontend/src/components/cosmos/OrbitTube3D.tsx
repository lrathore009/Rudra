"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { createOrbitTubeGeometry } from "./orbit-math";
import type { Navagraha } from "./navagraha-config";

export function OrbitTube3D({
  graha,
  opacity = 0.45,
  glowOpacity = 0.18,
}: {
  graha: Navagraha;
  opacity?: number;
  glowOpacity?: number;
}) {
  const glowRef = useRef<THREE.Mesh>(null);
  const coreRef = useRef<THREE.Mesh>(null);
  const { tubeGeo, glowGeo, coreGeo } = useMemo(() => {
    return {
      coreGeo: createOrbitTubeGeometry(graha, 160, 0.018),
      tubeGeo: createOrbitTubeGeometry(graha, 160, 0.042),
      glowGeo: createOrbitTubeGeometry(graha, 128, 0.078),
    };
  }, [graha]);

  useFrame((state) => {
    const pulse = 0.04 * Math.sin(state.clock.elapsedTime * 0.9 + graha.angle);
    if (glowRef.current) {
      const m = glowRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = glowOpacity + pulse;
    }
    if (coreRef.current) {
      const m = coreRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = 0.55 + pulse * 0.5;
    }
  });

  const color = graha.orbitColor;

  return (
    <group>
      <mesh geometry={glowGeo} ref={glowRef} renderOrder={1}>
        <meshBasicMaterial
          color={color}
          transparent
          opacity={glowOpacity}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      <mesh geometry={tubeGeo} castShadow receiveShadow renderOrder={2}>
        <meshPhysicalMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.75}
          transparent
          opacity={opacity}
          metalness={0.92}
          roughness={0.12}
          clearcoat={0.85}
          clearcoatRoughness={0.08}
          side={THREE.DoubleSide}
        />
      </mesh>
      <mesh geometry={coreGeo} ref={coreRef} renderOrder={3}>
        <meshBasicMaterial color="#ffffff" transparent opacity={0.5} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
    </group>
  );
}
