"use client";

import { createContext, useContext, useMemo, useRef, type ReactNode } from "react";
import { useFrame } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import * as THREE from "three";
import { grahaColor } from "@/lib/rudra-theme";
import { grahaPosition3D } from "./orbit-math";
import type { GrahaId, Navagraha } from "./navagraha-types";
import { OrbitTube3D } from "./OrbitTube3D";

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

function GrahaSurfaceExtras({ graha }: { graha: Navagraha }) {
  if (graha.surface === "corona") {
    return (
      <>
        <mesh scale={1.45}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshBasicMaterial color={graha.appearance.emissive} transparent opacity={0.22} side={THREE.BackSide} />
        </mesh>
        <mesh scale={1.28}>
          <sphereGeometry args={[1, 24, 24]} />
          <meshBasicMaterial color="#ffdd88" transparent opacity={0.12} />
        </mesh>
      </>
    );
  }
  if (graha.surface === "swirl") {
    return (
      <mesh scale={0.72}>
        <sphereGeometry args={[1, 24, 24]} />
        <meshBasicMaterial color={graha.appearance.emissive} transparent opacity={0.55} />
      </mesh>
    );
  }
  if (graha.surface === "hex") {
    return (
      <mesh>
        <icosahedronGeometry args={[0.92, 1]} />
        <meshPhysicalMaterial
          color={graha.appearance.color}
          emissive={graha.appearance.emissive}
          emissiveIntensity={graha.appearance.emissiveIntensity * 0.8}
          metalness={0.65}
          roughness={0.35}
          flatShading
        />
      </mesh>
    );
  }
  return null;
}

function TexturedGrahaSphere({ graha, map }: { graha: Navagraha; map: THREE.Texture }) {
  return (
    <mesh castShadow receiveShadow>
      <sphereGeometry args={[1, 64, 64]} />
      <meshPhysicalMaterial
        map={map}
        color={graha.appearance.color}
        emissive={graha.appearance.emissive}
        emissiveIntensity={graha.appearance.emissiveIntensity * 0.35}
        metalness={graha.appearance.metalness}
        roughness={graha.appearance.roughness}
        clearcoat={graha.appearance.clearcoat ?? 0}
        clearcoatRoughness={0.12}
      />
    </mesh>
  );
}

function TexturedGrahaBody({ graha }: { graha: Navagraha }) {
  const map = useTexture(graha.texture!);
  map.colorSpace = THREE.SRGBColorSpace;
  const useHex = graha.surface === "hex";
  return (
    <group rotation={[graha.axialTilt, 0, 0]}>
      {useHex ? <GrahaSurfaceExtras graha={graha} /> : <TexturedGrahaSphere graha={graha} map={map} />}
      {!useHex && <GrahaSurfaceExtras graha={graha} />}
      <mesh scale={1.12}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={graha.appearance.emissive} transparent opacity={0.12} side={THREE.BackSide} />
      </mesh>
      {graha.hasRings && <ShaniRings />}
    </group>
  );
}

function ProceduralGrahaBody({ graha }: { graha: Navagraha }) {
  const useHex = graha.surface === "hex";
  return (
    <group rotation={[graha.axialTilt, 0, 0]}>
      {useHex ? (
        <GrahaSurfaceExtras graha={graha} />
      ) : (
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
      )}
      {!useHex && <GrahaSurfaceExtras graha={graha} />}
      <mesh scale={1.12}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={graha.appearance.emissive} transparent opacity={0.12} side={THREE.BackSide} />
      </mesh>
      {graha.hasRings && <ShaniRings />}
    </group>
  );
}

function GrahaBodyInner({ graha }: { graha: Navagraha }) {
  if (graha.texture) return <TexturedGrahaBody graha={graha} />;
  return <ProceduralGrahaBody graha={graha} />;
}

function ShaniRings() {
  const ringMap = useTexture(`${"/textures/planets"}/2k_saturn_ring_alpha.png`);
  ringMap.colorSpace = THREE.SRGBColorSpace;
  return (
    <mesh rotation={[-Math.PI / 2 + 0.35, 0, 0]}>
      <ringGeometry args={[1.45, 2.35, 128]} />
      <meshStandardMaterial
        map={ringMap}
        color="#ccddee"
        transparent
        opacity={0.78}
        side={THREE.DoubleSide}
        depthWrite={false}
        metalness={0.85}
        roughness={0.25}
      />
    </mesh>
  );
}

export function GrahaOrbit3D({
  graha,
  role,
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

  const tubeOpacity = useMemo(() => {
    if (role === "lead") return 0.75;
    if (role === "supporting" || role === "pulse") return 0.52;
    return 0.38;
  }, [role]);

  useFrame((state, dt) => {
    if (!orbitRef.current) return;
    const speedMul = role === "lead" ? 1.4 : role === "supporting" ? 1.1 : 1;
    const motion = reducedMotion ? 0 : 1;
    angleRef.current += dt * graha.speed * speedMul * motion;

    const pos = grahaPosition3D(graha, angleRef.current);
    orbitRef.current.position.copy(pos);
    positionsRef.current.set(graha.id, pos.clone());
    orbitRef.current.renderOrder = pos.z > 0.5 ? 200 : pos.z < -0.5 ? 50 : 120;

    if (bodyRef.current) {
      bodyRef.current.rotation.y += dt * (0.22 + graha.speed) * motion * (role === "lead" ? 1.6 : 1);
    }

    let pulse = 1;
    if (role === "lead") pulse = 1.14 + Math.sin(state.clock.elapsedTime * 3.5) * 0.06;
    else if (role === "supporting" || role === "pulse")
      pulse = 1 + Math.sin(state.clock.elapsedTime * 2 + graha.angle) * 0.05;

    orbitRef.current.scale.setScalar(graha.size * pulse);
  });

  return (
    <group>
      <OrbitTube3D graha={graha} opacity={tubeOpacity} glowOpacity={tubeOpacity * 0.35} />
      <group ref={orbitRef}>
        <group ref={bodyRef}>
          <GrahaBodyInner graha={graha} />
          <pointLight
            color={graha.appearance.emissive}
            intensity={1 + (role === "lead" ? 2.2 : role === "supporting" ? 0.6 : 0)}
            distance={7}
          />
          {role === "lead" && (
            <mesh>
              <sphereGeometry args={[1.22, 32, 32]} />
              <meshBasicMaterial color={accent} transparent opacity={0.18} side={THREE.BackSide} />
            </mesh>
          )}
        </group>
      </group>
    </group>
  );
}

export function getGrahaWorldPosition(
  positionsRef: React.MutableRefObject<PositionMap>,
  id: GrahaId
): THREE.Vector3 | null {
  return positionsRef.current.get(id) ?? null;
}
