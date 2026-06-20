"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import * as THREE from "three";
import { SOLAR_TEXTURES, textureForBody, type SolarBody } from "./solar-textures";

const SPHERE_SEGMENTS = 48;

function configureMap(map: THREE.Texture) {
  map.colorSpace = THREE.SRGBColorSpace;
  return map;
}

function EarthPlanet({ accent, highlighted }: { accent: string; highlighted: boolean }) {
  const [surfaceMap, cloudMap] = useTexture([SOLAR_TEXTURES.earth, SOLAR_TEXTURES.earthClouds]);
  configureMap(surfaceMap);
  configureMap(cloudMap);
  const cloudRef = useRef<THREE.Mesh>(null);
  useFrame((_, dt) => {
    if (cloudRef.current) cloudRef.current.rotation.y += dt * 0.08;
  });
  return (
    <>
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[1, SPHERE_SEGMENTS, SPHERE_SEGMENTS]} />
        <meshStandardMaterial
          map={surfaceMap}
          roughness={0.95}
          metalness={0.05}
          emissive={highlighted ? accent : "#000000"}
          emissiveIntensity={highlighted ? 0.15 : 0}
        />
      </mesh>
      <mesh ref={cloudRef} scale={1.015}>
        <sphereGeometry args={[1, SPHERE_SEGMENTS, SPHERE_SEGMENTS]} />
        <meshStandardMaterial map={cloudMap} transparent opacity={0.42} depthWrite={false} roughness={1} />
      </mesh>
    </>
  );
}

function SaturnPlanet({ accent, highlighted }: { accent: string; highlighted: boolean }) {
  const [surfaceMap, ringMap] = useTexture([SOLAR_TEXTURES.saturn, SOLAR_TEXTURES.saturnRing]);
  configureMap(surfaceMap);
  configureMap(ringMap);
  return (
    <>
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[1, SPHERE_SEGMENTS, SPHERE_SEGMENTS]} />
        <meshStandardMaterial
          map={surfaceMap}
          roughness={0.85}
          metalness={0.05}
          emissive={highlighted ? accent : "#000000"}
          emissiveIntensity={highlighted ? 0.15 : 0}
        />
      </mesh>
      <mesh rotation={[Math.PI / 2.2, 0.15, 0]}>
        <ringGeometry args={[1.15, 1.85, 128]} />
        <meshStandardMaterial
          map={ringMap}
          transparent
          opacity={0.88}
          side={THREE.DoubleSide}
          depthWrite={false}
          roughness={0.9}
        />
      </mesh>
    </>
  );
}

function StandardPlanet({
  body,
  accent,
  highlighted,
}: {
  body: Exclude<SolarBody, "earth" | "saturn">;
  accent: string;
  highlighted: boolean;
}) {
  const surfaceMap = configureMap(useTexture(textureForBody(body)));
  const rough = body === "jupiter" || body === "uranus" || body === "neptune" ? 0.88 : 0.95;
  return (
    <mesh castShadow receiveShadow>
      <sphereGeometry args={[1, SPHERE_SEGMENTS, SPHERE_SEGMENTS]} />
      <meshStandardMaterial
        map={surfaceMap}
        roughness={rough}
        metalness={0.05}
        emissive={highlighted ? accent : "#000000"}
        emissiveIntensity={highlighted ? 0.15 : 0}
      />
    </mesh>
  );
}

function TexturedPlanetBody({
  body,
  accent,
  highlighted,
}: {
  body: SolarBody;
  accent: string;
  highlighted: boolean;
}) {
  return (
    <group>
      {body === "earth" && <EarthPlanet accent={accent} highlighted={highlighted} />}
      {body === "saturn" && <SaturnPlanet accent={accent} highlighted={highlighted} />}
      {body !== "earth" && body !== "saturn" && (
        <StandardPlanet body={body} accent={accent} highlighted={highlighted} />
      )}
      {highlighted && (
        <mesh scale={1.08}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshBasicMaterial color={accent} transparent opacity={0.06} depthWrite={false} />
        </mesh>
      )}
    </group>
  );
}

export { TexturedPlanetBody, SPHERE_SEGMENTS };
