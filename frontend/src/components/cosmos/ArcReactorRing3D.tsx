"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** Cyan arc-reactor rings fused around the Trishul — Rudra Prime centerpiece halo */
export function ArcReactorRing3D({
  processing = false,
  listening = false,
  reducedMotion = false,
}: {
  processing?: boolean;
  listening?: boolean;
  reducedMotion?: boolean;
}) {
  const outerRef = useRef<THREE.Mesh>(null);
  const midRef = useRef<THREE.Mesh>(null);
  const innerRef = useRef<THREE.Mesh>(null);
  const coreLight = useRef<THREE.PointLight>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    const pulse = listening ? 1.35 : processing ? 1.15 : 1;
    if (!reducedMotion) {
      if (outerRef.current) outerRef.current.rotation.z = t * 0.12;
      if (midRef.current) midRef.current.rotation.z = -t * 0.18;
      if (innerRef.current) innerRef.current.rotation.z = t * 0.25;
    }
    if (coreLight.current) {
      coreLight.current.intensity = (2.4 + Math.sin(t * (listening ? 4 : 1.5)) * 0.8) * pulse;
    }
  });

  return (
    <group position={[0, -0.35, 0]} rotation={[Math.PI / 2, 0, 0]}>
      <mesh ref={outerRef}>
        <torusGeometry args={[2.85, 0.045, 16, 128]} />
        <meshPhysicalMaterial
          color="#00d4ff"
          emissive="#0088cc"
          emissiveIntensity={listening ? 1.1 : 0.65}
          metalness={1}
          roughness={0.12}
          transparent
          opacity={0.75}
        />
      </mesh>
      <mesh ref={midRef}>
        <torusGeometry args={[2.35, 0.032, 12, 96]} />
        <meshPhysicalMaterial
          color="#ddaa44"
          emissive="#aa7722"
          emissiveIntensity={0.55}
          metalness={1}
          roughness={0.15}
          transparent
          opacity={0.55}
        />
      </mesh>
      <mesh ref={innerRef}>
        <torusGeometry args={[1.85, 0.022, 10, 80]} />
        <meshPhysicalMaterial
          color="#66eeff"
          emissive="#00aaff"
          emissiveIntensity={processing ? 0.95 : 0.5}
          metalness={0.95}
          roughness={0.1}
          transparent
          opacity={0.65}
        />
      </mesh>
      <mesh>
        <ringGeometry args={[0.55, 1.65, 64]} />
        <meshBasicMaterial color="#00d4ff" transparent opacity={0.12} side={THREE.DoubleSide} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      <pointLight ref={coreLight} color="#00d4ff" intensity={2.4} distance={14} position={[0, 0, 0.5]} />
    </group>
  );
}
