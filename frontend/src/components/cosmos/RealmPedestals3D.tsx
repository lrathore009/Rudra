"use client";

import { useRef, type ComponentType } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { REALMS, type RealmId } from "@/components/tablet/RealmRim";

const PEDESTAL_RADIUS = 4.35;
const PEDESTAL_Y = -2.65;

export function RealmPedestals3D({
  activeRealm,
  onRealmChange,
}: {
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
}) {
  return (
    <group position={[0, PEDESTAL_Y, 0]}>
      {REALMS.map((realm, i) => {
        const angle = (i / REALMS.length) * Math.PI * 2 - Math.PI / 2;
        const x = Math.cos(angle) * PEDESTAL_RADIUS;
        const z = Math.sin(angle) * PEDESTAL_RADIUS;
        const active = activeRealm === realm.id;
        return (
          <RealmPedestal
            key={realm.id}
            position={[x, 0, z]}
            rotationY={-angle + Math.PI / 2}
            label={realm.cosmicLabel}
            icon={realm.icon}
            active={active}
            onClick={() => onRealmChange(active ? null : realm.id)}
          />
        );
      })}
    </group>
  );
}

function RealmPedestal({
  position,
  rotationY,
  label,
  icon: Icon,
  active,
  onClick,
}: {
  position: [number, number, number];
  rotationY: number;
  label: string;
  icon: ComponentType<{ className?: string }>;
  active: boolean;
  onClick: () => void;
}) {
  const meshRef = useRef<THREE.Group>(null);
  const liftRef = useRef(0);

  useFrame((_, dt) => {
    const target = active ? 0.35 : 0;
    liftRef.current = THREE.MathUtils.lerp(liftRef.current, target, dt * 4);
    if (meshRef.current) {
      meshRef.current.position.y = liftRef.current;
    }
  });

  return (
    <group position={position} rotation={[0, rotationY, 0]}>
      <group ref={meshRef}>
        {/* stone base */}
        <mesh receiveShadow castShadow>
          <cylinderGeometry args={[0.48, 0.58, 0.32, 6]} />
          <meshPhysicalMaterial
            color={active ? "#181c30" : "#0a0c14"}
            emissive={active ? "#223355" : "#0a1018"}
            emissiveIntensity={active ? 0.35 : 0.15}
            metalness={0.55}
            roughness={0.48}
            clearcoat={0.35}
          />
        </mesh>
        {/* gold cap */}
        <mesh position={[0, 0.18, 0]} castShadow>
          <cylinderGeometry args={[0.38, 0.38, 0.05, 6]} />
          <meshPhysicalMaterial
            color="#ddaa44"
            emissive="#aa7722"
            emissiveIntensity={active ? 0.75 : 0.35}
            metalness={1}
            roughness={0.12}
            clearcoat={1}
          />
        </mesh>
        {/* glow ring when active */}
        {active && (
          <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[0.42, 0.56, 6]} />
            <meshBasicMaterial color="#4488ff" transparent opacity={0.35} side={THREE.DoubleSide} blending={THREE.AdditiveBlending} depthWrite={false} />
          </mesh>
        )}
        <Html transform center distanceFactor={9} position={[0, 0.55, 0]} style={{ pointerEvents: "auto" }}>
          <button
            type="button"
            onClick={onClick}
            className={active ? "cosmic-realm-tile cosmic-realm-tile-active" : "cosmic-realm-tile"}
            aria-pressed={active}
            title={`Open ${label} realm`}
          >
            <Icon className="mx-auto h-3.5 w-3.5" />
            <span>{label}</span>
          </button>
        </Html>
      </group>
    </group>
  );
}
