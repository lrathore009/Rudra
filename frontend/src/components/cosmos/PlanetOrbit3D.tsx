"use client";

import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { facetColor } from "@/lib/rudra-theme";
import type { CosmosPlanet } from "./planet-config";
import { TexturedPlanetBody } from "./PlanetMesh";

export function PlanetOrbit3D({
  planet,
  active,
  selected,
  awakened,
  onSelect,
}: {
  planet: CosmosPlanet;
  active: boolean;
  selected: boolean;
  awakened: boolean;
  onSelect: (agentType: string) => void;
}) {
  const ref = useRef<THREE.Group>(null);
  const spinRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);
  const accent = facetColor(planet.label, 1);
  const angleRef = useRef(planet.angle);

  useFrame((state, dt) => {
    if (!ref.current) return;
    angleRef.current += dt * planet.speed * (active ? 1.25 : 1);
    const a = angleRef.current;
    const x = Math.cos(a) * planet.radius;
    const z = Math.sin(a) * planet.radius;
    const y = Math.sin(a * 0.65 + planet.inclination) * planet.inclination * 3.5;
    ref.current.position.set(x, y, z);

    if (spinRef.current) spinRef.current.rotation.y += dt * planet.spin;

    const pulse = awakened ? 1.28 : selected || hovered ? 1.12 : 1;
    const s = planet.size * pulse * (1 + Math.sin(state.clock.elapsedTime * 2 + planet.angle) * 0.025);
    ref.current.scale.setScalar(s);
  });

  const highlighted = selected || hovered || awakened;

  return (
    <group ref={ref}>
      <mesh
        onClick={(e) => {
          e.stopPropagation();
          onSelect(planet.agentType);
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = "pointer";
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = "auto";
        }}
      >
        <sphereGeometry args={[1, 16, 16]} />
        <meshStandardMaterial visible={false} />
      </mesh>

      <group ref={spinRef}>
        <TexturedPlanetBody body={planet.solarBody} accent={accent} highlighted={highlighted} />
        {highlighted && <pointLight color={accent} intensity={awakened ? 2.5 : 1.2} distance={4} />}
      </group>

      {(hovered || selected || awakened) && (
        <Html center distanceFactor={14} style={{ pointerEvents: "none" }}>
          <div className="text-center">
            <span
              className="block whitespace-nowrap font-hud text-[10px] uppercase tracking-widest"
              style={{ color: accent, textShadow: `0 0 14px ${accent}` }}
            >
              {planet.label}
              {awakened && " ⚡"}
            </span>
            <span className="block font-terminal text-[8px] text-white/70">{planet.solarName}</span>
          </div>
        </Html>
      )}
    </group>
  );
}

/** Orbital path rings — inner → outer solar distances */
export function OrbitRings() {
  const radii = [4.5, 5.2, 5.8, 6.2, 6.5, 9.2, 10.5, 11.5, 12.8];
  return (
    <group>
      {radii.map((r, i) => (
        <mesh key={r} rotation={[Math.PI / 2 + i * 0.02, 0, i * 0.15]}>
          <torusGeometry args={[r, 0.012, 8, 160]} />
          <meshBasicMaterial color="#55ccff" transparent opacity={0.07} />
        </mesh>
      ))}
    </group>
  );
}

export function getPlanetWorldPosition(planet: CosmosPlanet, time: number): THREE.Vector3 {
  const a = planet.angle + time * planet.speed;
  return new THREE.Vector3(
    Math.cos(a) * planet.radius,
    Math.sin(a * 0.65 + planet.inclination) * planet.inclination * 3.5,
    Math.sin(a) * planet.radius
  );
}
