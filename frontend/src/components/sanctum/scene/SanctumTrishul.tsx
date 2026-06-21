"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import * as THREE from "three";
import {
  createBeadGarland,
  createCenterProngGroup,
  createDamruGroup,
  createOmDecal,
  createProngTube,
  createShaftGeometry,
  createShaftRings,
  createSideProngCurve,
  createThirdEye,
  createTripundra,
  DAMRU_BODY,
  DAMRU_SKIN,
  TRIDENT_GOLD,
  TRIDENT_METAL,
} from "@/components/cosmos/trishul-geometry";
import { SANCTUM_TRISHUL_SCALE } from "@/data/navagraha-catalog";

export type SanctumPhase = "idle" | "query" | "analysis" | "working" | "completed" | "error";

const EYE_OPEN: Record<SanctumPhase, number> = {
  idle: 0.05,
  query: 0.45,
  analysis: 0.65,
  working: 0.28,
  completed: 0.05,
  error: 0,
};

function useTrishulMaterials() {
  return useMemo(() => {
    const metal = new THREE.MeshPhysicalMaterial({
      ...TRIDENT_METAL,
      envMapIntensity: 1.4,
    });
    const gold = new THREE.MeshPhysicalMaterial({
      ...TRIDENT_GOLD,
      envMapIntensity: 1.6,
    });
    const damruBody = new THREE.MeshPhysicalMaterial(DAMRU_BODY);
    const damruSkin = new THREE.MeshPhysicalMaterial(DAMRU_SKIN);
    const bead = new THREE.MeshPhysicalMaterial({
      color: "#3d2810",
      emissive: "#aa6622",
      emissiveIntensity: 0.3,
      metalness: 0.35,
      roughness: 0.5,
    });
    const ash = new THREE.MeshStandardMaterial({
      color: "#ffffff",
      emissive: "#ccccff",
      emissiveIntensity: 0.45,
      transparent: true,
      opacity: 0.85,
    });
    const eyeLens = new THREE.MeshPhysicalMaterial({
      color: "#ffffff",
      emissive: "#cc88ff",
      emissiveIntensity: 0.7,
      metalness: 0.15,
      roughness: 0.04,
      transmission: 0.45,
      thickness: 0.5,
      transparent: true,
      opacity: 0.92,
    });
    const eyeIris = new THREE.MeshStandardMaterial({
      color: "#8844ff",
      emissive: "#aa44ff",
      emissiveIntensity: 1.3,
    });
    return { metal, gold, damruBody, damruSkin, bead, ash, eyeLens, eyeIris };
  }, []);
}

export function SanctumTrishul({ phase, processing }: { phase: SanctumPhase; processing: boolean }) {
  const rootRef = useRef<THREE.Group>(null);
  const damruRef = useRef<THREE.Group>(null);
  const eyeRef = useRef<THREE.Group>(null);
  const glowRef = useRef<THREE.PointLight>(null);
  const mats = useTrishulMaterials();
  const eyeOpen = EYE_OPEN[phase];

  const shaftGeo = useMemo(() => createShaftGeometry(), []);
  const leftProngGeo = useMemo(() => createProngTube(createSideProngCurve(-1), 0.05), []);
  const rightProngGeo = useMemo(() => createProngTube(createSideProngCurve(1), 0.05), []);

  const centerProng = useMemo(() => createCenterProngGroup(mats.metal), [mats.metal]);
  const damru = useMemo(
    () => createDamruGroup({ body: mats.damruBody, skin: mats.damruSkin, gold: mats.gold, bead: mats.bead }),
    [mats]
  );
  const tripundra = useMemo(() => createTripundra(mats.ash), [mats.ash]);
  const rings = useMemo(() => createShaftRings(mats.gold), [mats.gold]);
  const garland = useMemo(() => createBeadGarland(mats.bead), [mats.bead]);
  const omDecal = useMemo(() => (typeof document !== "undefined" ? createOmDecal() : null), []);
  const thirdEye = useMemo(
    () => createThirdEye(eyeOpen, { lens: mats.eyeLens, iris: mats.eyeIris }),
    [eyeOpen, mats.eyeLens, mats.eyeIris]
  );

  useFrame((state, dt) => {
    const t = state.clock.elapsedTime;
    if (rootRef.current) {
      rootRef.current.rotation.y += dt * (processing ? 0.004 : 0.0015);
      rootRef.current.position.y = Math.sin(t * 0.45) * 0.035;
      rootRef.current.rotation.x = Math.sin(t * 0.3) * 0.012;
    }
    if (damruRef.current) {
      damruRef.current.rotation.y += dt * (processing ? 0.6 : 0.28);
      damruRef.current.rotation.z = Math.sin(t * 1.8) * 0.06;
    }
    if (eyeRef.current) {
      const target = EYE_OPEN[phase];
      const sy = 0.04 + target * 0.5;
      eyeRef.current.scale.y = THREE.MathUtils.lerp(eyeRef.current.scale.y, sy, 0.1);
    }
    if (glowRef.current) {
      glowRef.current.intensity = 1.5 + eyeOpen * 3.5 + (processing ? 1.5 : 0);
    }
  });

  return (
    <Float speed={1.2} rotationIntensity={0.08} floatIntensity={0.25}>
      <group ref={rootRef} scale={SANCTUM_TRISHUL_SCALE} position={[0, -0.35, 0]}>
        <mesh geometry={shaftGeo} material={mats.metal} castShadow receiveShadow />

        <group position={[0, 1.05, 0]}>
          <primitive object={centerProng} />
          <mesh geometry={leftProngGeo} material={mats.metal} castShadow />
          <mesh geometry={rightProngGeo} material={mats.metal} castShadow />
        </group>

        <primitive object={rings} />
        <primitive object={tripundra} />

        <group ref={eyeRef} position={[0, 0.42, 0.16]}>
          <primitive object={thirdEye} />
        </group>

        <group ref={damruRef} position={[0, -0.55, 0]}>
          <primitive object={damru} />
        </group>

        <primitive object={garland} />
        {omDecal && <primitive object={omDecal} position={[0, 0.08, 0.18]} />}

        <pointLight ref={glowRef} color="#aa66ff" intensity={2} distance={6} decay={2} position={[0, 0.5, 0.2]} />
      </group>
    </Float>
  );
}
