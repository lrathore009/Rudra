"use client";

import { createContext, useContext, useMemo, useRef, useState, type ReactNode } from "react";
import { useFrame } from "@react-three/fiber";
import { Html, Line } from "@react-three/drei";
import * as THREE from "three";
import { grahaColor } from "@/lib/rudra-theme";
import { NAVAGRAHA, grahaPosition, type GrahaId, type Navagraha } from "./navagraha-config";

type PositionMap = Map<GrahaId, THREE.Vector3>;

const GrahaPositionsContext = createContext<React.MutableRefObject<PositionMap> | null>(null);

export function GrahaPositionsProvider({ children }: { children: ReactNode }) {
  const positionsRef = useRef<PositionMap>(new Map());
  return <GrahaPositionsContext.Provider value={positionsRef}>{children}</GrahaPositionsContext.Provider>;
}

export function useGrahaPositionsRef() {
  const ctx = useContext(GrahaPositionsContext);
  if (!ctx) throw new Error("useGrahaPositionsRef requires GrahaPositionsProvider");
  return ctx;
}

function ellipsePoints(graha: Navagraha, segments = 96): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  for (let i = 0; i <= segments; i++) {
    const t = (i / segments) * Math.PI * 2;
    pts.push(
      new THREE.Vector3(
        Math.cos(t) * graha.orbitRadiusX,
        graha.orbitLift,
        Math.sin(t) * graha.orbitRadiusZ
      )
    );
  }
  return pts;
}

function GrahaMaterial({ graha }: { graha: Navagraha }) {
  const { appearance: a } = graha;
  return (
    <meshPhysicalMaterial
      color={a.color}
      emissive={a.emissive}
      emissiveIntensity={a.emissiveIntensity}
      metalness={a.metalness}
      roughness={a.roughness}
      clearcoat={a.clearcoat ?? 0}
      clearcoatRoughness={0.15}
    />
  );
}

function GrahaBody({ graha }: { graha: Navagraha }) {
  return (
    <group rotation={[graha.axialTilt, 0, 0]}>
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[1, 56, 56]} />
        <GrahaMaterial graha={graha} />
      </mesh>
      {/* atmospheric glow */}
      <mesh scale={1.08}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={graha.appearance.emissive} transparent opacity={0.08} side={THREE.BackSide} />
      </mesh>
      {graha.hasRings && (
        <mesh rotation={[-Math.PI / 2 + 0.35, 0, 0]}>
          <ringGeometry args={[1.45, 2.1, 96]} />
          <meshStandardMaterial
            color="#8899aa"
            transparent
            opacity={0.6}
            side={THREE.DoubleSide}
            depthWrite={false}
            metalness={0.75}
            roughness={0.35}
          />
        </mesh>
      )}
    </group>
  );
}

function GrahaLabelCard({ graha, role }: { graha: Navagraha; role: string }) {
  const accent = grahaColor(graha.name, 1);
  const isLead = role === "lead";
  return (
    <div
      className="graha-label-card"
      style={{
        borderColor: `${accent}`,
        boxShadow: isLead ? `0 0 20px ${grahaColor(graha.name, 0.4)}` : undefined,
      }}
    >
      <span className="graha-label-symbol" style={{ color: accent }}>
        {graha.symbol}
      </span>
      <span className="graha-label-name" style={{ color: accent }}>
        {graha.name.toUpperCase()}
        {isLead && " ⚡"}
      </span>
      <span className="graha-label-domain">{graha.domain.toUpperCase()}</span>
    </div>
  );
}

export function GrahaOrbit3D({
  graha,
  role,
  processing,
  reducedMotion,
}: {
  graha: Navagraha;
  role: "idle" | "lead" | "supporting" | "pulse";
  processing: boolean;
  reducedMotion: boolean;
}) {
  const orbitRef = useRef<THREE.Group>(null);
  const spinRef = useRef<THREE.Group>(null);
  const angleRef = useRef(graha.angle);
  const positionsRef = useGrahaPositionsRef();
  const accent = grahaColor(graha.name, 1);
  const pathPoints = useMemo(() => ellipsePoints(graha), [graha]);

  useFrame((state, dt) => {
    if (!orbitRef.current) return;
    const speedMul = role === "lead" ? 1.5 : role === "supporting" ? 1.12 : 1;
    const motion = reducedMotion ? 0 : 1;
    angleRef.current += dt * graha.speed * speedMul * motion * (processing ? 1.05 : 1);

    const pos = grahaPosition(graha, angleRef.current);
    orbitRef.current.position.set(pos.x, pos.y, pos.z);
    positionsRef.current.set(graha.id, new THREE.Vector3(pos.x, pos.y, pos.z));

    if (spinRef.current) {
      spinRef.current.rotation.y += dt * (0.18 + graha.speed) * motion * (role === "lead" ? 1.8 : 1);
    }

    let pulse = 1;
    if (role === "lead") pulse = 1.14 + Math.sin(state.clock.elapsedTime * 3.5) * 0.05;
    else if (role === "supporting" || role === "pulse") pulse = 1 + Math.sin(state.clock.elapsedTime * 2 + graha.angle) * 0.04;

    orbitRef.current.scale.setScalar(graha.size * pulse);
  });

  const pathOpacity = role === "lead" ? 0.55 : role === "supporting" || role === "pulse" ? 0.35 : 0.22;

  return (
    <group>
      <Line
        points={pathPoints}
        color={graha.orbitColor}
        transparent
        opacity={pathOpacity}
        lineWidth={1.2}
      />
      <group ref={orbitRef}>
        <group ref={spinRef}>
          <GrahaBody graha={graha} />
          <pointLight color={graha.appearance.emissive} intensity={0.6 + (role === "lead" ? 1.5 : 0)} distance={4} />
          {role === "lead" && (
            <mesh>
              <sphereGeometry args={[1.15, 32, 32]} />
              <meshBasicMaterial color={accent} transparent opacity={0.12} side={THREE.BackSide} />
            </mesh>
          )}
        </group>
        <Html center distanceFactor={14} zIndexRange={[0, 0]} style={{ pointerEvents: "none" }}>
          <GrahaLabelCard graha={graha} role={role} />
        </Html>
      </group>
    </group>
  );
}

/** @deprecated — per-graha colored paths replace generic guides */
export function GrahaOrbitGuides() {
  return null;
}

export function getGrahaWorldPosition(
  positionsRef: React.MutableRefObject<PositionMap>,
  id: GrahaId
): THREE.Vector3 | null {
  return positionsRef.current.get(id) ?? null;
}
