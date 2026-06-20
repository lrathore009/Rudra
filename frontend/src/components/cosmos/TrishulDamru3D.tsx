"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import * as THREE from "three";

export type TrishulPhase = "idle" | "awakening" | "dispatch" | "working" | "error";

const EYE_OPEN: Record<TrishulPhase, number> = {
  idle: 0.05,
  awakening: 0.42,
  dispatch: 0.62,
  working: 0.06,
  error: 0,
};

function Prong({ rotation }: { rotation: [number, number, number] }) {
  return (
    <group rotation={rotation}>
      <mesh position={[0, 1.35, 0]}>
        <coneGeometry args={[0.14, 1.1, 8]} />
        <meshStandardMaterial
          color="#c8f8ff"
          emissive="#22ddff"
          emissiveIntensity={1.2}
          metalness={0.95}
          roughness={0.15}
        />
      </mesh>
      <mesh position={[0, 0.75, 0]}>
        <cylinderGeometry args={[0.06, 0.09, 0.5, 8]} />
        <meshStandardMaterial color="#88ccdd" emissive="#1188aa" emissiveIntensity={0.6} metalness={0.9} roughness={0.2} />
      </mesh>
    </group>
  );
}

function Damru3D({ spinning }: { spinning: boolean }) {
  const ref = useRef<THREE.Group>(null);
  useFrame((_, dt) => {
    if (ref.current && spinning) ref.current.rotation.y += dt * 8;
    else if (ref.current) ref.current.rotation.y += dt * 0.3;
  });

  return (
    <group ref={ref} position={[0.55, -0.15, 0.35]} rotation={[0.4, 0.5, 0.3]}>
      <mesh rotation={[Math.PI, 0, 0]}>
        <coneGeometry args={[0.22, 0.35, 12]} />
        <meshStandardMaterial color="#d4a040" emissive="#aa6620" emissiveIntensity={0.5} metalness={0.7} roughness={0.35} />
      </mesh>
      <mesh position={[0, 0.32, 0]}>
        <coneGeometry args={[0.22, 0.35, 12]} />
        <meshStandardMaterial color="#e8b850" emissive="#cc8830" emissiveIntensity={0.6} metalness={0.7} roughness={0.35} />
      </mesh>
      <mesh>
        <cylinderGeometry args={[0.06, 0.06, 0.12, 8]} />
        <meshStandardMaterial color="#886622" metalness={0.8} roughness={0.4} />
      </mesh>
      {/* strings */}
      {[0, 1, 2].map((i) => (
        <mesh key={i} position={[Math.cos(i * 2.1) * 0.12, 0.5 + i * 0.08, Math.sin(i * 2.1) * 0.12]}>
          <sphereGeometry args={[0.025, 6, 6]} />
          <meshStandardMaterial color="#ffeeaa" emissive="#ffcc44" emissiveIntensity={0.8} />
        </mesh>
      ))}
    </group>
  );
}

function ThirdEye3D({ openness }: { openness: number }) {
  const scaleY = 0.05 + openness * 0.55;
  return (
    <group position={[0, 0.55, 0.22]}>
      <mesh scale={[0.18, scaleY, 0.04]}>
        <sphereGeometry args={[1, 16, 16]} />
        <meshStandardMaterial
          color="#ffffff"
          emissive="#aa44ff"
          emissiveIntensity={0.4 + openness * 2}
          transparent
          opacity={0.85}
        />
      </mesh>
      {openness > 0.2 && (
        <pointLight color="#cc66ff" intensity={openness * 3} distance={4} />
      )}
    </group>
  );
}

export function TrishulDamru3D({
  phase,
  spinning,
}: {
  phase: TrishulPhase;
  spinning: boolean;
}) {
  const groupRef = useRef<THREE.Group>(null);
  const eyeOpen = EYE_OPEN[phase];

  useFrame((state, dt) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime;
    if (spinning) {
      groupRef.current.rotation.y += dt * 4;
      groupRef.current.position.y = -0.5 + Math.sin(t * 6) * 0.05;
    } else {
      groupRef.current.rotation.y = THREE.MathUtils.lerp(groupRef.current.rotation.y, 0, 0.05);
      groupRef.current.position.y = -0.5 + Math.sin(t * 0.8) * 0.12;
      groupRef.current.rotation.x = Math.sin(t * 0.5) * 0.04;
    }
  });

  return (
    <Float speed={1.2} rotationIntensity={0.08} floatIntensity={0.25}>
      <group ref={groupRef} position={[0, -0.5, 0]}>
        {/* central shaft */}
        <mesh>
          <cylinderGeometry args={[0.1, 0.14, 2.2, 10]} />
          <meshStandardMaterial
            color="#a0eeff"
            emissive="#22ccff"
            emissiveIntensity={0.9}
            metalness={0.92}
            roughness={0.18}
          />
        </mesh>
        {/* cross guard */}
        <mesh position={[0, 0.2, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.05, 0.05, 0.9, 8]} />
          <meshStandardMaterial color="#66bbcc" emissive="#118899" emissiveIntensity={0.5} metalness={0.85} roughness={0.25} />
        </mesh>
        <Prong rotation={[0.25, 0, 0]} />
        <Prong rotation={[0.25, (2 * Math.PI) / 3, 0]} />
        <Prong rotation={[0.25, (4 * Math.PI) / 3, 0]} />
        <ThirdEye3D openness={eyeOpen} />
        <Damru3D spinning={spinning || phase === "dispatch"} />
        <pointLight color="#44eeff" intensity={1.5} distance={8} position={[0, 0.5, 1]} />
        <pointLight color="#aa44ff" intensity={0.8} distance={6} position={[0, 1, -0.5]} />
      </group>
    </Float>
  );
}
