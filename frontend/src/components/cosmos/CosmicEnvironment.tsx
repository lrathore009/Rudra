"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float, Line, useTexture } from "@react-three/drei";
import * as THREE from "three";
import { SSS_STARS_MILKY_WAY } from "./navagraha-config";

const STAR_COUNT = 2500;
const METEOR_COUNT = 48;
const NEURAL_NODES = 36;

function MilkyWaySky({ reducedMotion }: { reducedMotion: boolean }) {
  const map = useTexture(SSS_STARS_MILKY_WAY);
  map.colorSpace = THREE.SRGBColorSpace;
  const ref = useRef<THREE.Mesh>(null);

  useFrame((_, dt) => {
    if (ref.current && !reducedMotion) ref.current.rotation.y += dt * 0.004;
  });

  return (
    <mesh ref={ref} scale={[-1, 1, 1]}>
      <sphereGeometry args={[140, 64, 64]} />
      <meshBasicMaterial map={map} side={THREE.BackSide} depthWrite={false} />
    </mesh>
  );
}
function Starfield({ reducedMotion }: { reducedMotion: boolean }) {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const arr = new Float32Array(STAR_COUNT * 3);
    for (let i = 0; i < STAR_COUNT; i++) {
      const r = 40 + Math.random() * 120;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, []);

  useFrame((_, dt) => {
    if (ref.current && !reducedMotion) ref.current.rotation.y += dt * 0.008;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.08} color="#e8f4ff" transparent opacity={0.85} sizeAttenuation depthWrite={false} />
    </points>
  );
}

function NebulaClouds({ reducedMotion }: { reducedMotion: boolean }) {
  const blobs = useMemo(
    () => [
      { pos: [-14, 2, -12] as [number, number, number], color: "#7b3fa8", scale: 22 },
      { pos: [18, -4, -16] as [number, number, number], color: "#1a5a9a", scale: 26 },
      { pos: [-6, 6, -24] as [number, number, number], color: "#c040a0", scale: 28 },
      { pos: [10, -8, -20] as [number, number, number], color: "#2244cc", scale: 18 },
      { pos: [0, -2, -8] as [number, number, number], color: "#553311", scale: 18 },
      { pos: [0, 0, -30] as [number, number, number], color: "#4422aa", scale: 32 },
    ],
    []
  );

  if (reducedMotion) {
    return (
      <group>
        {blobs.map((b, i) => (
          <mesh key={i} position={b.pos}>
            <sphereGeometry args={[b.scale, 12, 12]} />
            <meshBasicMaterial color={b.color} transparent opacity={0.09} depthWrite={false} />
          </mesh>
        ))}
      </group>
    );
  }

  return (
    <group>
      {blobs.map((b, i) => (
        <Float key={i} speed={0.4 + i * 0.1} rotationIntensity={0.1} floatIntensity={0.6}>
          <mesh position={b.pos}>
            <sphereGeometry args={[b.scale, 16, 16]} />
            <meshBasicMaterial color={b.color} transparent opacity={0.09} depthWrite={false} />
          </mesh>
        </Float>
      ))}
    </group>
  );
}

function Meteors() {
  const ref = useRef<THREE.Points>(null);
  const data = useMemo(() => {
    const pos = new Float32Array(METEOR_COUNT * 3);
    const vel = new Float32Array(METEOR_COUNT * 3);
    for (let i = 0; i < METEOR_COUNT; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 80;
      pos[i * 3 + 1] = Math.random() * 40 + 5;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 80;
      vel[i * 3] = -0.8 - Math.random() * 1.2;
      vel[i * 3 + 1] = -2 - Math.random() * 4;
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.5;
    }
    return { pos, vel };
  }, []);

  useFrame((_, dt) => {
    if (!ref.current) return;
    const attr = ref.current.geometry.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < METEOR_COUNT; i++) {
      let x = attr.getX(i) + data.vel[i * 3] * dt;
      let y = attr.getY(i) + data.vel[i * 3 + 1] * dt;
      let z = attr.getZ(i) + data.vel[i * 3 + 2] * dt;
      if (y < -20) {
        x = (Math.random() - 0.5) * 80;
        y = 30 + Math.random() * 20;
        z = (Math.random() - 0.5) * 80;
      }
      attr.setXYZ(i, x, y, z);
    }
    attr.needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[data.pos, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.15} color="#88eeff" transparent opacity={0.7} sizeAttenuation depthWrite={false} />
    </points>
  );
}

function NeuralWeb({ intensity, reducedMotion }: { intensity: number; reducedMotion: boolean }) {
  const groupRef = useRef<THREE.Group>(null);
  const nodes = useMemo(() => {
    return Array.from({ length: NEURAL_NODES }, () => ({
      pos: new THREE.Vector3(
        (Math.random() - 0.5) * 50,
        (Math.random() - 0.5) * 30,
        (Math.random() - 0.5) * 50 - 10
      ),
      pulse: Math.random() * Math.PI * 2,
    }));
  }, []);

  const lines = useMemo(() => {
    const segs: [THREE.Vector3, THREE.Vector3][] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if (nodes[i].pos.distanceTo(nodes[j].pos) < 14 && Math.random() > 0.55) {
          segs.push([nodes[i].pos.clone(), nodes[j].pos.clone()]);
        }
      }
    }
    return segs;
  }, [nodes]);

  useFrame((state) => {
    if (groupRef.current && !reducedMotion) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.015;
    }
  });

  const lineOpacity = 0.04 + intensity * 0.04;
  const nodeOpacity = 0.15 + intensity * 0.12;

  return (
    <group ref={groupRef}>
      {lines.map(([a, b], i) => (
        <Line key={i} points={[a, b]} color="#44ddff" transparent opacity={lineOpacity} />
      ))}
      {nodes.map((n, i) => (
        <mesh key={i} position={n.pos}>
          <sphereGeometry args={[0.06 + intensity * 0.02, 6, 6]} />
          <meshBasicMaterial color="#aa66ff" transparent opacity={nodeOpacity} />
        </mesh>
      ))}
    </group>
  );
}

function SanctumWarmGlow() {
  return (
    <group position={[0, -1.5, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[8, 48]} />
        <meshBasicMaterial color="#ffaa44" transparent opacity={0.06} depthWrite={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <circleGeometry args={[14, 48]} />
        <meshBasicMaterial color="#6644aa" transparent opacity={0.04} depthWrite={false} />
      </mesh>
      <pointLight color="#ffcc88" intensity={2.5} distance={28} position={[0, 2, 2]} />
    </group>
  );
}

export function CosmicEnvironment({
  neuralIntensity = 0.5,
  reducedMotion = false,
}: {
  neuralIntensity?: number;
  reducedMotion?: boolean;
}) {
  return (
    <>
      <color attach="background" args={["#020208"]} />
      <fog attach="fog" args={["#020208", 40, 130]} />
      <MilkyWaySky reducedMotion={reducedMotion} />
      <Starfield reducedMotion={reducedMotion} />
      <NebulaClouds reducedMotion={reducedMotion} />
      <SanctumWarmGlow />
      {!reducedMotion && <Meteors />}
      <NeuralWeb intensity={neuralIntensity} reducedMotion={reducedMotion} />
    </>
  );
}
