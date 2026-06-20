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

  const stoneMat = {
    color: "#141018",
    emissive: "#1a1208",
    emissiveIntensity: 0.28,
    metalness: 0.35,
    roughness: 0.62,
    clearcoat: 0.25,
    clearcoatRoughness: 0.4,
  };

  return (
    <group position={[0, -3.15, 0]} scale={1.35}>
      {/* outer plinth */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow castShadow position={[0, -0.06, 0]}>
        <cylinderGeometry args={[3.15, 3.35, 0.28, 96]} />
        <meshPhysicalMaterial {...stoneMat} />
      </mesh>
      {/* main stone tier */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow castShadow>
        <cylinderGeometry args={[2.85, 3.05, 0.22, 96]} />
        <meshPhysicalMaterial {...stoneMat} roughness={0.58} />
      </mesh>
      {/* polished obsidian inset */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.12, 0]} receiveShadow>
        <circleGeometry args={[2.75, 96]} />
        <meshPhysicalMaterial
          color="#0c0a12"
          emissive="#221144"
          emissiveIntensity={0.18}
          metalness={0.75}
          roughness={0.22}
          clearcoat={0.55}
          clearcoatRoughness={0.15}
        />
      </mesh>
      {/* raised gold lip */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.135, 0]} castShadow>
        <torusGeometry args={[2.68, 0.028, 12, 128]} />
        <meshPhysicalMaterial color="#c9942e" emissive="#886622" emissiveIntensity={0.45} metalness={1} roughness={0.18} clearcoat={1} />
      </mesh>

      {/* gold circuit rings */}
      <group ref={ringsRef}>
        {[0.55, 0.95, 1.35, 1.75, 2.15, 2.55].map((r, i) => (
          <mesh key={r} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.14 + i * 0.004, 0]} castShadow>
            <torusGeometry args={[r, 0.014, 10, 128]} />
            <meshPhysicalMaterial
              color="#ddaa44"
              emissive="#aa7722"
              emissiveIntensity={0.35 + i * 0.05}
              metalness={1}
              roughness={0.15}
              transparent
              opacity={0.35 + i * 0.08}
            />
          </mesh>
        ))}
      </group>

      {/* inner power ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.132, 0]}>
        <ringGeometry args={[0.35, 2.65, 96]} />
        <meshPhysicalMaterial
          color="#3388ff"
          emissive="#2266cc"
          emissiveIntensity={0.55}
          transparent
          opacity={0.22}
          metalness={0.9}
          roughness={0.1}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* circuit tick marks */}
      {Array.from({ length: 32 }, (_, i) => {
        const a = (i / 32) * Math.PI * 2;
        return (
          <mesh key={i} position={[Math.cos(a) * 2.35, 0.15, Math.sin(a) * 2.35]} rotation={[0, -a, 0]} castShadow>
            <boxGeometry args={[0.1, 0.012, 0.028]} />
            <meshPhysicalMaterial
              color={i % 2 === 0 ? "#ffcc66" : "#55aaff"}
              emissive={i % 2 === 0 ? "#aa7722" : "#2266aa"}
              emissiveIntensity={0.4}
              metalness={0.95}
              roughness={0.2}
              transparent
              opacity={0.55}
            />
          </mesh>
        );
      })}

      <pointLight ref={goldPulse} color="#ffcc66" intensity={4.2} distance={16} position={[0, 0.8, 0.2]} />
      <pointLight ref={pulseRef} color="#4488ff" intensity={2.8} distance={12} position={[0, 0.3, 0.5]} />
    </group>
  );
}
