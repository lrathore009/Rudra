"use client";

import { useTexture } from "@react-three/drei";
import * as THREE from "three";
import { SANCTUM_STARS } from "@/data/navagraha-catalog";

export function SanctumEnvironment() {
  const stars = useTexture(SANCTUM_STARS);
  stars.colorSpace = THREE.SRGBColorSpace;
  stars.mapping = THREE.EquirectangularReflectionMapping;

  return (
    <>
      <color attach="background" args={["#030208"]} />
      <fog attach="fog" args={["#030208", 18, 42]} />
      <ambientLight intensity={0.35} color="#334466" />
      <directionalLight
        position={[8, 12, 6]}
        intensity={0.55}
        color="#8899bb"
        castShadow
        shadow-mapSize={[1024, 1024]}
      />
      <hemisphereLight args={["#446688", "#110822", 0.45]} />
      <mesh scale={[-1, 1, 1]}>
        <sphereGeometry args={[80, 64, 64]} />
        <meshBasicMaterial map={stars} side={THREE.BackSide} depthWrite={false} />
      </mesh>
    </>
  );
}

export function SanctumPlatform() {
  return (
    <group position={[0, -2.8, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <circleGeometry args={[5.5, 64]} />
        <meshStandardMaterial
          color="#0a0e18"
          emissive="#112244"
          emissiveIntensity={0.25}
          metalness={0.85}
          roughness={0.35}
          transparent
          opacity={0.92}
        />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[4.8, 5.4, 64]} />
        <meshBasicMaterial color="#00d4ff" transparent opacity={0.12} depthWrite={false} />
      </mesh>
    </group>
  );
}
