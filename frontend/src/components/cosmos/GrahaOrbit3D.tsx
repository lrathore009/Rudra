"use client";

import { createContext, useContext, useRef, useState, type ReactNode } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { grahaColor } from "@/lib/rudra-theme";
import { grahaPosition, orbitGuideRadii, type GrahaId, type Navagraha } from "./navagraha-config";

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
      clearcoatRoughness={0.2}
    />
  );
}

function GrahaBody({ graha }: { graha: Navagraha }) {
  const tilt = graha.axialTilt;
  return (
    <group rotation={[tilt, 0, 0]}>
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[1, 48, 48]} />
        <GrahaMaterial graha={graha} />
      </mesh>
      {graha.hasRings && (
        <mesh rotation={[-Math.PI / 2 + 0.35, 0, 0]}>
          <ringGeometry args={[1.4, 2.0, 96]} />
          <meshStandardMaterial
            color="#334455"
            transparent
            opacity={0.55}
            side={THREE.DoubleSide}
            depthWrite={false}
            metalness={0.7}
            roughness={0.4}
          />
        </mesh>
      )}
    </group>
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
  const [hovered, setHovered] = useState(false);
  const angleRef = useRef(graha.angle);
  const positionsRef = useGrahaPositionsRef();
  const accent = grahaColor(graha.name, 1);

  useFrame((state, dt) => {
    if (!orbitRef.current) return;
    const speedMul = role === "lead" ? 1.6 : role === "supporting" ? 1.15 : 1;
    const motion = reducedMotion ? 0 : 1;
    angleRef.current += dt * graha.speed * speedMul * motion * (processing ? 1.1 : 1);

    const pos = grahaPosition(graha, angleRef.current);
    orbitRef.current.position.set(pos.x, pos.y, pos.z);

    positionsRef.current.set(graha.id, new THREE.Vector3(pos.x, pos.y, pos.z));

    if (spinRef.current) {
      spinRef.current.rotation.y += dt * (0.2 + graha.speed) * motion * (role === "lead" ? 2 : 1);
    }

    let pulse = 1;
    if (role === "lead") pulse = 1.18 + Math.sin(state.clock.elapsedTime * 4) * 0.06;
    else if (role === "supporting" || role === "pulse") pulse = 1 + Math.sin(state.clock.elapsedTime * 2.5 + graha.angle) * 0.05;
    else if (hovered) pulse = 1.06;

    const s = graha.size * pulse;
    orbitRef.current.scale.setScalar(s);
  });

  const showLabel = role === "lead" || role === "supporting" || hovered;

  return (
    <group ref={orbitRef}>
      <mesh
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
        }}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[1, 24, 24]} />
        <meshStandardMaterial visible={false} />
      </mesh>

      <group ref={spinRef}>
        <GrahaBody graha={graha} />
        {(role === "lead" || role === "supporting") && (
          <pointLight
            color={accent}
            intensity={role === "lead" ? 2.2 : 0.7}
            distance={role === "lead" ? 5 : 3}
          />
        )}
        {role === "lead" && (
          <mesh>
            <sphereGeometry args={[1.12, 32, 32]} />
            <meshBasicMaterial color={accent} transparent opacity={0.1} side={THREE.BackSide} />
          </mesh>
        )}
        {(role === "supporting" || role === "pulse") && (
          <mesh>
            <sphereGeometry args={[1.06, 24, 24]} />
            <meshBasicMaterial color={accent} transparent opacity={0.05} side={THREE.BackSide} />
          </mesh>
        )}
      </group>

      {showLabel && (
        <Html center distanceFactor={16} style={{ pointerEvents: "none" }}>
          <span
            className="whitespace-nowrap font-terminal text-[10px] uppercase tracking-widest"
            style={{ color: accent, textShadow: `0 0 14px ${accent}` }}
          >
            {graha.name}
            {role === "lead" && " ⚡"}
          </span>
        </Html>
      )}
    </group>
  );
}

/** Elliptical orbit guides — wide horizontal paths */
export function GrahaOrbitGuides() {
  const guides = orbitGuideRadii();
  return (
    <group>
      {guides.map(({ rx, rz }, i) => (
        <mesh key={`${rx}-${rz}`} rotation={[Math.PI / 2, 0, i * 0.12]}>
          <torusGeometry args={[rx, 0.008, 6, 128, Math.PI * 2]} scale={[1, rz / rx, 1]} />
          <meshBasicMaterial color="#44ccff" transparent opacity={0.04 + i * 0.005} />
        </mesh>
      ))}
    </group>
  );
}

export function getGrahaWorldPosition(
  positionsRef: React.MutableRefObject<PositionMap>,
  id: GrahaId
): THREE.Vector3 | null {
  return positionsRef.current.get(id) ?? null;
}
