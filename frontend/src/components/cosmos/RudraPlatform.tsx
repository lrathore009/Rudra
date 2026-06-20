"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** Glowing golden circuit platform beneath the Trishula — sanctum dais */
export function RudraPlatform({ reducedMotion = false }: { reducedMotion?: boolean }) {
  const ringsRef = useRef<THREE.Group>(null);
  const pulseRef = useRef<THREE.PointLight>(null);
  const goldPulse = useRef<THREE.PointLight>(null);

  useFrame((state) => {
    if (ringsRef.current && !reducedMotion) {
      ringsRef.current.rotation.y = state.clock.elapsedTime * 0.04;
    }
    const t = state.clock.elapsedTime;
    if (pulseRef.current) {
      pulseRef.current.intensity = 2.8 + Math.sin(t * 1.2) * 0.6;
    }
    if (goldPulse.current) {
      goldPulse.current.intensity = 4.2 + Math.sin(t * 0.9) * 0.8;
    }
  });

  return (
    <group position={[0, -3.15, 0]} scale={1.35}>
      {/* dark stone base */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <cylinderGeometry args={[2.85, 3.05, 0.22, 72]} />
        <meshStandardMaterial color="#0a0810" emissive="#1a1208" emissiveIntensity={0.35} metalness={0.85} roughness={0.55} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.12, 0]} receiveShadow>
        <circleGeometry args={[2.75, 72]} />
        <meshStandardMaterial color="#120e08" emissive="#332208" emissiveIntensity={0.25} metalness={0.9} roughness={0.45} />
      </mesh>

      {/* gold circuit rings */}
      <group ref={ringsRef}>
        {[0.55, 0.95, 1.35, 1.75, 2.15, 2.55].map((r, i) => (
          <mesh key={r} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.14 + i * 0.004, 0]}>
            <torusGeometry args={[r, 0.016, 8, 128]} />
            <meshBasicMaterial color="#ddaa44" transparent opacity={0.22 + i * 0.06} />
          </mesh>
        ))}
      </group>

      {/* inner blue power ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.13, 0]}>
        <ringGeometry args={[0.35, 2.65, 72]} />
        <meshBasicMaterial color="#3388ff" transparent opacity={0.14} side={THREE.DoubleSide} />
      </mesh>

      {/* circuit tick marks */}
      {Array.from({ length: 32 }, (_, i) => {
        const a = (i / 32) * Math.PI * 2;
        return (
          <mesh key={i} position={[Math.cos(a) * 2.35, 0.15, Math.sin(a) * 2.35]} rotation={[0, -a, 0]}>
            <boxGeometry args={[0.1, 0.01, 0.025]} />
            <meshBasicMaterial color={i % 2 === 0 ? "#ffcc66" : "#55aaff"} transparent opacity={0.45} />
          </mesh>
        );
      })}

      <pointLight ref={goldPulse} color="#ffcc66" intensity={4.2} distance={16} position={[0, 0.8, 0.2]} />
      <pointLight ref={pulseRef} color="#4488ff" intensity={2.8} distance={12} position={[0, 0.3, 0.5]} />
    </group>
  );
}
