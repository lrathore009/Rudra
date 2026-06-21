"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import * as THREE from "three";
import type { Navagraha } from "@/components/cosmos/navagraha-types";
import { grahaPosition3D } from "@/components/cosmos/orbit-math";

const RING_TEX = "/textures/planets/2k_saturn_ring_alpha.png";
const FALLBACK_TEX = "/textures/planets/2k_mercury.jpg";

function usePlanetTextures(graha: Navagraha) {
  const primary = graha.texture ?? FALLBACK_TEX;
  const paths = graha.hasRings ? [primary, RING_TEX] : [primary];
  const loaded = useTexture(paths);
  return {
    surface: loaded[0],
    ring: graha.hasRings ? loaded[1] : null,
  };
}

function PlanetMesh({
  graha,
  highlighted,
  pulsing,
  children,
}: {
  graha: Navagraha;
  highlighted: boolean;
  pulsing: boolean;
  children: React.ReactNode;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state, dt) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y += dt * (graha.id === "surya" ? 0.08 : 0.25);
    const pulse = pulsing ? 1 + Math.sin(state.clock.elapsedTime * 4) * 0.06 : 1;
    const scale = graha.size * (highlighted ? 1.12 * pulse : pulse);
    meshRef.current.scale.setScalar(scale);
  });

  return (
    <mesh ref={meshRef} castShadow receiveShadow rotation={[0, 0, THREE.MathUtils.degToRad(graha.axialTilt)]}>
      <sphereGeometry args={[1, 64, 64]} />
      {children}
    </mesh>
  );
}

function TexturedBody({
  graha,
  highlighted,
  pulsing,
}: {
  graha: Navagraha;
  highlighted: boolean;
  pulsing: boolean;
}) {
  const { surface, ring } = usePlanetTextures(graha);
  const ringRef = useRef<THREE.Mesh>(null);
  const isSun = graha.id === "surya";

  useFrame((_, dt) => {
    if (ringRef.current) ringRef.current.rotation.z += dt * 0.05;
  });

  return (
    <>
      <PlanetMesh graha={graha} highlighted={highlighted} pulsing={pulsing}>
        <meshStandardMaterial
          map={surface}
          emissive={isSun ? graha.appearance.emissive : "#000000"}
          emissiveIntensity={isSun ? graha.appearance.emissiveIntensity : 0}
          metalness={graha.appearance.metalness}
          roughness={graha.appearance.roughness}
        />
      </PlanetMesh>
      {ring && (
        <mesh
          ref={ringRef}
          rotation={[THREE.MathUtils.degToRad(90 + graha.axialTilt), 0, 0]}
          scale={graha.size}
        >
          <ringGeometry args={[1.35, 2.1, 128]} />
          <meshStandardMaterial
            map={ring}
            transparent
            opacity={0.75}
            side={THREE.DoubleSide}
            depthWrite={false}
            metalness={0.2}
            roughness={0.6}
          />
        </mesh>
      )}
    </>
  );
}

function NodeBody({
  graha,
  highlighted,
  pulsing,
}: {
  graha: Navagraha;
  highlighted: boolean;
  pulsing: boolean;
}) {
  const mat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: graha.appearance.color,
        emissive: graha.appearance.emissive,
        emissiveIntensity: graha.appearance.emissiveIntensity,
        metalness: graha.appearance.metalness,
        roughness: graha.appearance.roughness,
        transparent: true,
        opacity: 0.9,
      }),
    [graha]
  );

  return (
    <PlanetMesh graha={graha} highlighted={highlighted} pulsing={pulsing}>
      <primitive object={mat} attach="material" />
    </PlanetMesh>
  );
}

export function SanctumPlanet({
  graha,
  angle,
  highlighted,
  pulsing,
  local = false,
}: {
  graha: Navagraha;
  angle: number;
  highlighted: boolean;
  pulsing: boolean;
  /** When true, parent group handles world position */
  local?: boolean;
}) {
  const pos = useMemo(() => (local ? null : grahaPosition3D(graha, angle)), [graha, angle, local]);
  const isNode = graha.surface === "swirl" || graha.surface === "hex";
  const isSun = graha.id === "surya";

  const body = (
    <>
      {isSun && (
        <>
          <pointLight color="#ffaa44" intensity={4.5} distance={30} decay={2} />
          <mesh scale={graha.size * 1.4}>
            <sphereGeometry args={[1, 32, 32]} />
            <meshBasicMaterial color="#ff8800" transparent opacity={0.14} depthWrite={false} />
          </mesh>
        </>
      )}

      {isNode ? (
        <NodeBody graha={graha} highlighted={highlighted} pulsing={pulsing} />
      ) : (
        <TexturedBody graha={graha} highlighted={highlighted} pulsing={pulsing} />
      )}

      {highlighted && (
        <mesh scale={graha.size * 1.25}>
          <sphereGeometry args={[1, 24, 24]} />
          <meshBasicMaterial color={graha.orbitColor} transparent opacity={0.08} depthWrite={false} />
        </mesh>
      )}
    </>
  );

  if (local) return <group>{body}</group>;
  return <group position={[pos!.x, pos!.y, pos!.z]}>{body}</group>;
}
