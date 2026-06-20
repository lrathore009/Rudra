"use client";

import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { facetColor } from "@/lib/rudra-theme";
import type { CosmosPlanet } from "./planet-config";

function planetColor(label: string): string {
  return facetColor(label, 1);
}

function PlanetSurface({ kind, color }: { kind: CosmosPlanet["kind"]; color: string }) {
  if (kind === "ringed") {
    return (
      <>
        <mesh>
          <sphereGeometry args={[1, 32, 32]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.35} roughness={0.6} metalness={0.2} />
        </mesh>
        <mesh rotation={[1.2, 0.3, 0.5]}>
          <torusGeometry args={[1.35, 0.04, 8, 64]} />
          <meshStandardMaterial color="#ccccff" emissive="#8888ff" emissiveIntensity={0.4} transparent opacity={0.7} />
        </mesh>
      </>
    );
  }
  if (kind === "cloud") {
    return (
      <mesh>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial color="#eef8ff" emissive={color} emissiveIntensity={0.25} roughness={0.9} metalness={0.05} />
      </mesh>
    );
  }
  if (kind === "data") {
    return (
      <mesh>
        <icosahedronGeometry args={[1, 2]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} wireframe wireframeLinewidth={1} />
      </mesh>
    );
  }
  if (kind === "facet") {
    return (
      <mesh>
        <octahedronGeometry args={[1, 1]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.45} flatShading />
      </mesh>
    );
  }
  return (
    <mesh>
      <sphereGeometry args={[1, 24, 24]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} roughness={0.55} metalness={0.15} />
    </mesh>
  );
}

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
  const [hovered, setHovered] = useState(false);
  const color = planetColor(planet.label);
  const angleRef = useRef(planet.angle);

  useFrame((state, dt) => {
    if (!ref.current) return;
    angleRef.current += dt * planet.speed * (active ? 1.4 : 1);
    const a = angleRef.current;
    const x = Math.cos(a) * planet.radius;
    const z = Math.sin(a) * planet.radius;
    const y = Math.sin(a * 0.7 + planet.inclination) * planet.inclination * 4;
    ref.current.position.set(x, y, z);
    ref.current.rotation.y += dt * 0.5;

    const pulse = awakened ? 1.35 : selected || hovered ? 1.15 : 1;
    const s = planet.size * pulse * (1 + Math.sin(state.clock.elapsedTime * 2 + planet.angle) * 0.04);
    ref.current.scale.setScalar(s);
  });

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
      <group>
        <PlanetSurface kind={planet.kind} color={color} />
        {(active || selected || hovered) && (
          <pointLight color={color} intensity={selected ? 2 : 1} distance={3} />
        )}
      </group>
      {(hovered || selected || awakened) && (
        <Html center distanceFactor={12} style={{ pointerEvents: "none" }}>
          <span
            className="whitespace-nowrap font-terminal text-[10px] uppercase tracking-widest"
            style={{
              color,
              textShadow: `0 0 12px ${color}`,
            }}
          >
            {planet.label}
            {awakened && " ⚡"}
          </span>
        </Html>
      )}
    </group>
  );
}

export function OrbitRings() {
  return (
    <group>
      {[5, 6.5, 7.5].map((r, i) => (
        <mesh key={i} rotation={[Math.PI / 2 + i * 0.15, 0, i * 0.4]}>
          <torusGeometry args={[r, 0.015, 8, 128]} />
          <meshBasicMaterial color="#44ddff" transparent opacity={0.08} />
        </mesh>
      ))}
    </group>
  );
}

/** World position of a planet for lightning targeting */
export function usePlanetPosition(planet: CosmosPlanet, time: number): THREE.Vector3 {
  const a = planet.angle + time * planet.speed;
  return new THREE.Vector3(
    Math.cos(a) * planet.radius,
    Math.sin(a * 0.7 + planet.inclination) * planet.inclination * 4,
    Math.sin(a) * planet.radius
  );
}
