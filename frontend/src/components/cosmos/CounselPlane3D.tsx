"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { InkText } from "@/components/tablet/InkText";

export function CounselPlane3D({ text, visible }: { text: string; visible: boolean }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!groupRef.current || !visible) return;
    groupRef.current.position.y = 1.2 + Math.sin(state.clock.elapsedTime * 0.5) * 0.08;
  });

  if (!visible || !text) return null;

  return (
    <group ref={groupRef} position={[0, 1.2, 7.5]} rotation={[-0.05, 0, 0]}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[7.5, 2.2, 0.06]} />
        <meshPhysicalMaterial
          color="#0a0818"
          emissive="#221144"
          emissiveIntensity={0.4}
          transparent
          opacity={0.82}
          metalness={0.72}
          roughness={0.28}
          clearcoat={0.65}
          clearcoatRoughness={0.12}
        />
      </mesh>
      <mesh position={[0, 0, 0.04]}>
        <planeGeometry args={[7.3, 0.05]} />
        <meshPhysicalMaterial color="#55ccff" emissive="#2288cc" emissiveIntensity={0.6} transparent opacity={0.45} metalness={0.9} roughness={0.1} />
      </mesh>
      <Html transform center distanceFactor={9} position={[0, 0, 0.06]} style={{ width: "340px" }}>
        <div className="cosmic-response pointer-events-none px-3 py-2 text-center">
          <InkText text={text} streamed />
        </div>
      </Html>
    </group>
  );
}
