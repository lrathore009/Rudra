"use client";

import { createContext, useContext, useMemo, useRef, type ReactNode } from "react";
import { useFrame } from "@react-three/fiber";
import { Html, Line } from "@react-three/drei";
import * as THREE from "three";
import { grahaColor } from "@/lib/rudra-theme";
import { grahaPosition, type GrahaId, type Navagraha } from "./navagraha-config";

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

function ellipsePoints(graha: Navagraha, segments = 128): THREE.Vector3[] {
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

function GrahaBody({ graha }: { graha: Navagraha }) {
  return (
    <group rotation={[graha.axialTilt, 0, 0]}>
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[1, 64, 64]} />
        <meshPhysicalMaterial
          color={graha.appearance.color}
          emissive={graha.appearance.emissive}
          emissiveIntensity={graha.appearance.emissiveIntensity}
          metalness={graha.appearance.metalness}
          roughness={graha.appearance.roughness}
          clearcoat={graha.appearance.clearcoat ?? 0}
          clearcoatRoughness={0.12}
        />
      </mesh>
      <mesh scale={1.15}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={graha.appearance.emissive} transparent opacity={0.14} side={THREE.BackSide} />
      </mesh>
      {graha.hasRings && (
        <mesh rotation={[-Math.PI / 2 + 0.35, 0, 0]}>
          <ringGeometry args={[1.5, 2.2, 128]} />
          <meshStandardMaterial
            color="#99aabb"
            transparent
            opacity={0.65}
            side={THREE.DoubleSide}
            depthWrite={false}
            metalness={0.8}
            roughness={0.3}
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
        borderColor: accent,
        boxShadow: isLead ? `0 0 18px ${grahaColor(graha.name, 0.45)}` : `0 0 8px ${grahaColor(graha.name, 0.15)}`,
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
  const bodyRef = useRef<THREE.Group>(null);
  const angleRef = useRef(graha.angle);
  const positionsRef = useGrahaPositionsRef();
  const accent = grahaColor(graha.name, 1);
  const pathPoints = useMemo(() => ellipsePoints(graha), [graha]);

  useFrame((state, dt) => {
    if (!orbitRef.current) return;
    const speedMul = role === "lead" ? 1.4 : role === "supporting" ? 1.1 : 1;
    const motion = reducedMotion ? 0 : 1;
    angleRef.current += dt * graha.speed * speedMul * motion;

    const pos = grahaPosition(graha, angleRef.current);
    orbitRef.current.position.set(pos.x, pos.y, pos.z);
    positionsRef.current.set(graha.id, new THREE.Vector3(pos.x, pos.y, pos.z));

    // Depth sort: grahas toward camera render in front of Trishula
    orbitRef.current.renderOrder = pos.z > 0.5 ? 200 : pos.z < -0.5 ? 50 : 120;

    if (bodyRef.current) {
      bodyRef.current.rotation.y += dt * (0.22 + graha.speed) * motion * (role === "lead" ? 1.6 : 1);
    }

    let pulse = 1;
    if (role === "lead") pulse = 1.12 + Math.sin(state.clock.elapsedTime * 3.5) * 0.05;
    else if (role === "supporting" || role === "pulse") pulse = 1 + Math.sin(state.clock.elapsedTime * 2 + graha.angle) * 0.04;

    orbitRef.current.scale.setScalar(graha.size * pulse);
  });

  const pathOpacity =
    role === "lead" ? 0.65 : role === "supporting" || role === "pulse" ? 0.42 : 0.28;

  const labelPos: [number, number, number] = [
    graha.labelOffsetX,
    graha.labelOffsetY,
    0,
  ];

  return (
    <group>
      <Line points={pathPoints} color={graha.orbitColor} transparent opacity={pathOpacity} lineWidth={1.4} />
      <group ref={orbitRef}>
        <group ref={bodyRef}>
          <GrahaBody graha={graha} />
          <pointLight
            color={graha.appearance.emissive}
            intensity={0.9 + (role === "lead" ? 1.8 : role === "supporting" ? 0.5 : 0)}
            distance={6}
          />
          {role === "lead" && (
            <mesh>
              <sphereGeometry args={[1.18, 32, 32]} />
              <meshBasicMaterial color={accent} transparent opacity={0.15} side={THREE.BackSide} />
            </mesh>
          )}
        </group>
        <Html
          position={labelPos}
          center
          distanceFactor={22}
          zIndexRange={[100, 0]}
          style={{ pointerEvents: "none" }}
          occlude={false}
        >
          <GrahaLabelCard graha={graha} role={role} />
        </Html>
      </group>
    </group>
  );
}

export function GrahaOrbitGuides() {
  return null;
}

export function getGrahaWorldPosition(
  positionsRef: React.MutableRefObject<PositionMap>,
  id: GrahaId
): THREE.Vector3 | null {
  return positionsRef.current.get(id) ?? null;
}
