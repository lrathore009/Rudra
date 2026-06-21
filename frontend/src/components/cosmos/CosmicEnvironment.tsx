"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float, Line, useTexture } from "@react-three/drei";
import * as THREE from "three";
import { SSS_STARS_MILKY_WAY } from "./navagraha-config";

const STAR_COUNT = 2500;
const METEOR_COUNT = 48;
const NEURAL_NODES = 36;

function MilkyWaySky({ reducedMotion, dimmed = false }: { reducedMotion: boolean; dimmed?: boolean }) {
  const map = useTexture(SSS_STARS_MILKY_WAY);
  map.colorSpace = THREE.SRGBColorSpace;
  const ref = useRef<THREE.Mesh>(null);

  useFrame((_, dt) => {
    if (ref.current && !reducedMotion) ref.current.rotation.y += dt * 0.004;
  });

  return (
    <mesh ref={ref} scale={[-1, 1, 1]}>
      <sphereGeometry args={[140, 64, 64]} />
      <meshBasicMaterial map={map} side={THREE.BackSide} depthWrite={false} transparent opacity={dimmed ? 0.35 : 1} />
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
      { pos: [0, 0, -18] as [number, number, number], color: "#6b2fa8", scale: 38 },
      { pos: [-12, 4, -22] as [number, number, number], color: "#9b4fd4", scale: 28 },
      { pos: [14, -2, -20] as [number, number, number], color: "#1a6aaa", scale: 32 },
      { pos: [-8, -6, -16] as [number, number, number], color: "#2244cc", scale: 24 },
      { pos: [8, 8, -26] as [number, number, number], color: "#c040a0", scale: 22 },
      { pos: [0, -4, -12] as [number, number, number], color: "#5533aa", scale: 20 },
    ],
    []
  );

  const opacity = 0.16;

  if (reducedMotion) {
    return (
      <group>
        {blobs.map((b, i) => (
          <mesh key={i} position={b.pos}>
            <sphereGeometry args={[b.scale, 12, 12]} />
            <meshBasicMaterial color={b.color} transparent opacity={opacity} depthWrite={false} />
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
            <meshBasicMaterial color={b.color} transparent opacity={opacity} depthWrite={false} />
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
        <meshBasicMaterial color="#ffaa44" transparent opacity={0.1} depthWrite={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <circleGeometry args={[14, 48]} />
        <meshBasicMaterial color="#8844cc" transparent opacity={0.12} depthWrite={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <circleGeometry args={[22, 48]} />
        <meshBasicMaterial color="#2244aa" transparent opacity={0.08} depthWrite={false} />
      </mesh>
      <pointLight color="#aa88ff" intensity={3.2} distance={32} position={[0, 2, 2]} />
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
  const bg = "#08051a";
  const neuralScale = 0.35;

  return (
    <>
      <fog attach="fog" args={[bg, 35, 110]} />
      <MilkyWaySky reducedMotion={reducedMotion} dimmed />
      <Starfield reducedMotion={reducedMotion} />
      <NebulaClouds reducedMotion={reducedMotion} />
      <SanctumWarmGlow />
      {!reducedMotion && <Meteors />}
      {neuralScale > 0 && (
        <NeuralWeb intensity={neuralIntensity * neuralScale} reducedMotion={reducedMotion} />
      )}
    </>
  );
}
