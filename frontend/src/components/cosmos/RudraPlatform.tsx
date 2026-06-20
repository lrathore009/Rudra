"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** Glowing circular platform beneath the Trishula — neural engine base */
export function RudraPlatform({ reducedMotion = false }: { reducedMotion?: boolean }) {
  const ringsRef = useRef<THREE.Group>(null);
  const pulseRef = useRef<THREE.PointLight>(null);

  useFrame((state) => {
    if (ringsRef.current && !reducedMotion) {
      ringsRef.current.rotation.y = state.clock.elapsedTime * 0.06;
    }
    if (pulseRef.current) {
      pulseRef.current.intensity = 3.5 + Math.sin(state.clock.elapsedTime * 1.2) * 0.8;
    }
  });

  return (
    <group position={[0, -3.1, 0]} scale={1.25}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <circleGeometry args={[2.6, 72]} />
        <meshStandardMaterial
          color="#080818"
          emissive="#1a4488"
          emissiveIntensity={0.55}
          metalness={0.9}
          roughness={0.3}
        />
      </mesh>

      <group ref={ringsRef}>
        {[0.65, 1.0, 1.35, 1.7, 2.05, 2.4].map((r, i) => (
          <mesh key={r} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.025 + i * 0.005, 0]}>
            <torusGeometry args={[r, 0.014, 8, 128]} />
            <meshBasicMaterial color="#55ccff" transparent opacity={0.18 + i * 0.05} />
          </mesh>
        ))}
      </group>

      <pointLight ref={pulseRef} color="#55aaff" intensity={3.5} distance={14} position={[0, 0.6, 0]} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.015, 0]}>
        <ringGeometry args={[0.25, 2.5, 72]} />
        <meshBasicMaterial color="#3388ff" transparent opacity={0.18} side={THREE.DoubleSide} />
      </mesh>
      {/* circuit ticks */}
      {Array.from({ length: 24 }, (_, i) => {
        const a = (i / 24) * Math.PI * 2;
        return (
          <mesh
            key={i}
            position={[Math.cos(a) * 2.15, 0.04, Math.sin(a) * 2.15]}
            rotation={[0, -a, 0]}
          >
            <boxGeometry args={[0.08, 0.008, 0.02]} />
            <meshBasicMaterial color="#88ccff" transparent opacity={0.35} />
          </mesh>
        );
      })}
    </group>
  );
}
