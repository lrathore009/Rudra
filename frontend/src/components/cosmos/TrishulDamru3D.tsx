"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import * as THREE from "three";
import {
  createBeadGarland,
  createCenterProngGroup,
  createDamruGroup,
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
} from "./trishul-geometry";

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

function ProngTips({ material }: { material: THREE.Material }) {
  return (
    <>
      {([-1, 1] as const).map((side) => {
        const c = createSideProngCurve(side);
        const tip = c.getPoint(1);
        const tan = c.getTangent(1).normalize();
        const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), tan);
        return (
          <mesh key={side} position={tip} quaternion={quat} material={material}>
            <coneGeometry args={[0.042, 0.2, 12]} />
          </mesh>
        );
      })}
    </>
  );
}

function SacredTrishulMesh({
  phase,
  spinning,
  scale = 1,
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
  const leftProngGeo = useMemo(() => createProngTube(createSideProngCurve(-1), 0.05), []);
  const rightProngGeo = useMemo(() => createProngTube(createSideProngCurve(1), 0.05), []);

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
        rootRef.current.position.y = Math.sin(t * 5) * 0.04;
      } else {
        rootRef.current.rotation.y = THREE.MathUtils.lerp(rootRef.current.rotation.y, 0, 0.04);
        rootRef.current.position.y = Math.sin(t * 0.7) * 0.08;
        rootRef.current.rotation.x = Math.sin(t * 0.45) * 0.035;
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
      glowRef.current.intensity = 1.2 + eyeOpen * 4 + (spinning ? 2 : 0);
    }
  });

  return (
    <group ref={rootRef} scale={scale}>
      <mesh geometry={shaftGeo} material={mats.metal} castShadow receiveShadow />

      <group position={[0, 1.05, 0]}>
        <primitive object={centerProng} />
        <mesh geometry={leftProngGeo} material={mats.metal} castShadow />
        <mesh geometry={rightProngGeo} material={mats.metal} castShadow />
        <ProngTips material={mats.metal} />
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
        <meshBasicMaterial color="#44ddff" transparent opacity={0.25} />
      </mesh>

      <pointLight ref={glowRef} color="#aa66ff" intensity={1.5} distance={7} position={[0, 0.6, 0.4]} />
      <pointLight color="#44eeff" intensity={1.8} distance={9} position={[0.5, 1, 1]} />
      <spotLight color="#88eeff" intensity={2} angle={0.4} penumbra={0.8} position={[2, 3, 2]} castShadow />
    </group>
  );
}

export function TrishulDamru3D({
  phase,
  spinning,
  scale = 1,
}: {
  phase: TrishulPhase;
  spinning: boolean;
  scale?: number;
}) {
  return (
    <Float speed={1.1} rotationIntensity={0.06} floatIntensity={0.2}>
      <group position={[0, -0.35, 0]}>
        <SacredTrishulMesh phase={phase} spinning={spinning} scale={scale} />
      </group>
    </Float>
  );
}

export function TrishulDamruPreview({ scale = 0.55 }: { scale?: number }) {
  return (
    <Float speed={1.3} floatIntensity={0.35}>
      <group rotation={[0.25, 0.6, 0]}>
        <SacredTrishulMesh phase="idle" spinning={false} scale={scale} />
      </group>
    </Float>
  );
}
