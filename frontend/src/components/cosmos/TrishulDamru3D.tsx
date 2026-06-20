"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import {
  createBeadGarland,
  createCenterProngGroup,
  createDamruGroup,
  createShaftGeometry,
  createShaftRings,
  createSideBladeGeometry,
  createThirdEye,
  createTripundra,
  DAMRU_BODY,
  DAMRU_SKIN,
  TRIDENT_GOLD,
  TRIDENT_METAL,
} from "./trishul-geometry";
import { TRISHUL_PIVOT_Y, TRISHUL_SCALE } from "./cosmos-scale";

export type TrishulPhase = "idle" | "awakening" | "dispatch" | "working" | "error";

const EYE_OPEN: Record<TrishulPhase, number> = {
  idle: 0.05,
  awakening: 0.42,
  dispatch: 0.62,
  working: 0.06,
  error: 0,
};

function useSacredMaterials() {
  return useMemo(() => {
    const metal = new THREE.MeshPhysicalMaterial(TRIDENT_METAL);
    const gold = new THREE.MeshPhysicalMaterial(TRIDENT_GOLD);
    const damruBody = new THREE.MeshPhysicalMaterial(DAMRU_BODY);
    const damruSkin = new THREE.MeshPhysicalMaterial(DAMRU_SKIN);
    const bead = new THREE.MeshPhysicalMaterial({
      color: "#3d2810",
      emissive: "#aa6622",
      emissiveIntensity: 0.25,
      metalness: 0.3,
      roughness: 0.55,
    });
    const ash = new THREE.MeshStandardMaterial({
      color: "#ffffff",
      emissive: "#ccccff",
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.85,
    });
    const eyeLens = new THREE.MeshPhysicalMaterial({
      color: "#ffffff",
      emissive: "#cc88ff",
      emissiveIntensity: 0.6,
      metalness: 0.2,
      roughness: 0.05,
      transmission: 0.4,
      thickness: 0.5,
      transparent: true,
      opacity: 0.9,
    });
    const eyeIris = new THREE.MeshStandardMaterial({
      color: "#8844ff",
      emissive: "#aa44ff",
      emissiveIntensity: 1.2,
    });
    return { metal, gold, damruBody, damruSkin, bead, ash, eyeLens, eyeIris };
  }, []);
}

function SacredTrishulMesh({
  phase,
  spinning,
  scale = TRISHUL_SCALE,
}: {
  phase: TrishulPhase;
  spinning: boolean;
  scale?: number;
}) {
  const rootRef = useRef<THREE.Group>(null);
  const damruRef = useRef<THREE.Group>(null);
  const eyeRef = useRef<THREE.Group>(null);
  const glowRef = useRef<THREE.PointLight>(null);
  const mats = useSacredMaterials();
  const eyeOpen = EYE_OPEN[phase];

  const shaftGeo = useMemo(() => createShaftGeometry(), []);
  const leftBladeGeo = useMemo(() => createSideBladeGeometry(-1), []);
  const rightBladeGeo = useMemo(() => createSideBladeGeometry(1), []);

  const centerProng = useMemo(() => createCenterProngGroup(mats.metal), [mats.metal]);
  const damru = useMemo(
    () =>
      createDamruGroup({
        body: mats.damruBody,
        skin: mats.damruSkin,
        gold: mats.gold,
        bead: mats.bead,
      }),
    [mats]
  );
  const tripundra = useMemo(() => createTripundra(mats.ash), [mats.ash]);
  const rings = useMemo(() => createShaftRings(mats.gold), [mats.gold]);
  const garland = useMemo(() => createBeadGarland(mats.bead), [mats.bead]);
  const thirdEye = useMemo(
    () => createThirdEye(eyeOpen, { lens: mats.eyeLens, iris: mats.eyeIris }),
    [eyeOpen, mats.eyeLens, mats.eyeIris]
  );

  useFrame((state, dt) => {
    const t = state.clock.elapsedTime;
    if (rootRef.current) {
      if (spinning) {
        rootRef.current.rotation.y += dt * 3.5;
      } else {
        rootRef.current.rotation.y = THREE.MathUtils.lerp(rootRef.current.rotation.y, 0, 0.04);
        rootRef.current.rotation.x = Math.sin(t * 0.45) * 0.02;
      }
    }
    if (damruRef.current) {
      damruRef.current.rotation.y += spinning ? dt * 10 : dt * 0.35;
      damruRef.current.rotation.z = Math.sin(t * 2) * 0.08;
    }
    if (eyeRef.current) {
      const sy = 0.04 + eyeOpen * 0.5;
      eyeRef.current.scale.y = THREE.MathUtils.lerp(eyeRef.current.scale.y, sy, 0.12);
    }
    if (glowRef.current) {
      glowRef.current.intensity = 2 + eyeOpen * 5 + (spinning ? 3 : 0);
    }
  });

  return (
    <group ref={rootRef} scale={scale}>
      <mesh geometry={shaftGeo} material={mats.metal} castShadow receiveShadow />

      <group position={[0, 1.05, 0]}>
        <primitive object={centerProng} />
        <mesh geometry={leftBladeGeo} material={mats.metal} castShadow />
        <mesh geometry={rightBladeGeo} material={mats.metal} castShadow />
      </group>

      <primitive object={rings} />
      <primitive object={tripundra} />

      <group ref={eyeRef} position={[0, 0.42, 0.16]}>
        <primitive object={thirdEye} />
      </group>

      <group position={[0, 0.05, 0.08]}>
        <mesh material={mats.gold} position={[0, 0.18, 0]}>
          <cylinderGeometry args={[0.008, 0.008, 0.35, 8]} />
        </mesh>
        <group ref={damruRef} position={[0, -0.38, 0.05]}>
          <primitive object={damru} />
        </group>
        <group position={[0, -0.55, 0.06]}>
          <primitive object={garland} />
        </group>
      </group>

      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0.5, 0]}>
        <torusGeometry args={[0.55, 0.006, 8, 64]} />
        <meshBasicMaterial color="#44ddff" transparent opacity={0.2} />
      </mesh>

      <pointLight ref={glowRef} color="#aa66ff" intensity={3} distance={scale * 4} position={[0, 0.6, 0.4]} />
      <pointLight color="#44eeff" intensity={3.5} distance={scale * 5} position={[0.5, 1, 1]} />
      <spotLight color="#88eeff" intensity={3} angle={0.45} penumbra={0.8} position={[2, 3, 2]} castShadow />
    </group>
  );
}

export function TrishulDamru3D({
  phase,
  spinning,
  scale = TRISHUL_SCALE,
}: {
  phase: TrishulPhase;
  spinning: boolean;
  scale?: number;
}) {
  return (
    <group position={[0, TRISHUL_PIVOT_Y * scale, 0]}>
      <SacredTrishulMesh phase={phase} spinning={spinning} scale={scale} />
    </group>
  );
}

export function TrishulDamruPreview({ scale = 0.55 }: { scale?: number }) {
  return (
    <group rotation={[0.25, 0.6, 0]} position={[0, TRISHUL_PIVOT_Y * scale, 0]}>
      <SacredTrishulMesh phase="idle" spinning={false} scale={scale} />
    </group>
  );
}
