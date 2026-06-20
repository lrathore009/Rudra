"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** Glowing circular platform beneath the Trishula — neural engine base */
export function RudraPlatform({ reducedMotion = false }: { reducedMotion?: boolean }) {
  const ringsRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (ringsRef.current && !reducedMotion) {
      ringsRef.current.rotation.y = state.clock.elapsedTime * 0.08;
    }
  });

  return (
    <group position={[0, -2.85, 0]} scale={1.15}>
      {/* base disc */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <circleGeometry args={[2.4, 64]} />
        <meshStandardMaterial
          color="#0a0a18"
          emissive="#1a3366"
          emissiveIntensity={0.35}
          metalness={0.85}
          roughness={0.35}
        />
      </mesh>

      <group ref={ringsRef}>
        {[0.7, 1.1, 1.5, 1.9, 2.25].map((r, i) => (
          <mesh key={r} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02 + i * 0.004, 0]}>
            <torusGeometry args={[r, 0.012, 8, 96]} />
            <meshBasicMaterial color="#44aaff" transparent opacity={0.15 + i * 0.06} />
          </mesh>
        ))}
      </group>

      {/* inner glow pulse */}
      <pointLight color="#4488ff" intensity={2.5} distance={8} position={[0, 0.5, 0]} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[0.3, 2.2, 64]} />
        <meshBasicMaterial color="#2266cc" transparent opacity={0.12} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}
