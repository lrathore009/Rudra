"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Float, Line } from "@react-three/drei";

const STAR_COUNT = 4000;
const METEOR_COUNT = 48;
const NEURAL_NODES = 36;

function Starfield() {
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
    if (ref.current) ref.current.rotation.y += dt * 0.008;
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

function NebulaClouds() {
  const blobs = useMemo(
    () => [
      { pos: [-12, 4, -18] as [number, number, number], color: "#6b3fa0", scale: 14 },
      { pos: [16, -6, -22] as [number, number, number], color: "#1a6b8a", scale: 18 },
      { pos: [0, 8, -28] as [number, number, number], color: "#c04090", scale: 20 },
      { pos: [-8, -10, -15] as [number, number, number], color: "#2244aa", scale: 12 },
    ],
    []
  );

  return (
    <group>
      {blobs.map((b, i) => (
        <Float key={i} speed={0.4 + i * 0.1} rotationIntensity={0.1} floatIntensity={0.6}>
          <mesh position={b.pos}>
            <sphereGeometry args={[b.scale, 16, 16]} />
            <meshBasicMaterial color={b.color} transparent opacity={0.07} depthWrite={false} />
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

function NeuralWeb() {
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
    if (groupRef.current) groupRef.current.rotation.y = state.clock.elapsedTime * 0.015;
  });

  return (
    <group ref={groupRef}>
      {lines.map(([a, b], i) => (
        <Line key={i} points={[a, b]} color="#44ddff" transparent opacity={0.06} />
      ))}
      {nodes.map((n, i) => (
        <mesh key={i} position={n.pos}>
          <sphereGeometry args={[0.06, 6, 6]} />
          <meshBasicMaterial color="#aa66ff" transparent opacity={0.25} />
        </mesh>
      ))}
    </group>
  );
}

export function CosmicEnvironment() {
  return (
    <>
      <color attach="background" args={["#030510"]} />
      <fog attach="fog" args={["#030510", 28, 95]} />
      <ambientLight intensity={0.15} />
      <Starfield />
      <NebulaClouds />
      <Meteors />
      <NeuralWeb />
    </>
  );
}
