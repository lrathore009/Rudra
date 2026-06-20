"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, Environment, useTexture } from "@react-three/drei";
import * as THREE from "three";
import { CosmicEnvironment } from "./CosmicEnvironment";
import { CentralSun } from "./CentralSun";
import { TrishulDamru3D, type TrishulPhase } from "./TrishulDamru3D";
import { COSMOS_PLANETS, planetByAgent, planetByLabel } from "./planet-config";
import { OrbitRings, PlanetOrbit3D, getPlanetWorldPosition } from "./PlanetOrbit3D";
import { LightningBolt3D } from "./LightningBolt3D";
import { ALL_SOLAR_TEXTURE_URLS } from "./solar-textures";
import { CAMERA } from "./cosmos-scale";

function SceneContent({
  processing,
  activeAgentType,
  activeFacet,
  errorFacet,
  selectedAgent,
  onSelectAgent,
}: {
  processing: boolean;
  activeAgentType?: string;
  activeFacet?: string;
  errorFacet?: string;
  selectedAgent?: string;
  onSelectAgent: (type: string) => void;
}) {
  const [phase, setPhase] = useState<TrishulPhase>("idle");
  const [boltTarget, setBoltTarget] = useState<THREE.Vector3 | null>(null);
  const [awoken, setAwoken] = useState<string | null>(null);
  const [spinning, setSpinning] = useState(false);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const timeRef = useRef(0);

  // Preload all solar textures once for the scene
  useTexture(ALL_SOLAR_TEXTURE_URLS);

  const routedTag = activeFacet ?? planetByAgent(activeAgentType)?.label;

  useEffect(() => {
    timers.current.forEach(clearTimeout);
    timers.current = [];

    if (errorFacet) {
      setPhase("error");
      setSpinning(false);
      setBoltTarget(null);
      return;
    }

    if (!processing) {
      setPhase("idle");
      setSpinning(false);
      setBoltTarget(null);
      setAwoken(null);
      return;
    }

    setPhase("awakening");
    timers.current.push(
      setTimeout(() => {
        if (routedTag) {
          setPhase("dispatch");
          setSpinning(true);
          const p = planetByLabel(routedTag);
          if (p) {
            setBoltTarget(getPlanetWorldPosition(p, timeRef.current));
            setAwoken(routedTag);
          }
          timers.current.push(
            setTimeout(() => {
              setPhase("working");
              setSpinning(false);
              setBoltTarget(null);
            }, 900)
          );
        } else {
          setPhase("working");
        }
      }, 400)
    );

    return () => timers.current.forEach(clearTimeout);
  }, [processing, routedTag, errorFacet]);

  const showBolt = phase === "dispatch" && boltTarget !== null;

  useFrame((_, dt) => {
    timeRef.current += dt;
  });

  return (
    <>
      <PerspectiveCamera makeDefault position={CAMERA.position} fov={CAMERA.fov} />
      <OrbitControls
        enablePan={false}
        enableZoom
        minDistance={CAMERA.minDistance}
        maxDistance={CAMERA.maxDistance}
        maxPolarAngle={Math.PI / 1.55}
        minPolarAngle={Math.PI / 5}
        autoRotate={!processing}
        autoRotateSpeed={0.25}
        target={CAMERA.target}
      />
      <directionalLight position={[5, 8, 5]} intensity={0.6} color="#aaccff" />
      <Environment preset="night" environmentIntensity={0.35} />
      <CosmicEnvironment />
      <CentralSun />
      <OrbitRings />
      <TrishulDamru3D phase={phase} spinning={spinning} />
      <LightningBolt3D target={boltTarget} active={showBolt} />
      {COSMOS_PLANETS.map((p) => (
        <PlanetOrbit3D
          key={p.label}
          planet={p}
          active={processing}
          selected={selectedAgent === p.agentType}
          awakened={awoken === p.label}
          onSelect={onSelectAgent}
        />
      ))}
    </>
  );
}

export function CosmicScene({
  processing,
  activeAgentType,
  activeFacet,
  errorFacet,
  selectedAgent,
  onSelectAgent,
}: {
  processing: boolean;
  activeAgentType?: string;
  activeFacet?: string;
  errorFacet?: string;
  selectedAgent?: string;
  onSelectAgent: (type: string) => void;
}) {
  return (
    <Canvas
      className="cosmic-canvas"
      gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
      dpr={[1, 2]}
    >
      <Suspense fallback={null}>
        <SceneContent
          processing={processing}
          activeAgentType={activeAgentType}
          activeFacet={activeFacet}
          errorFacet={errorFacet}
          selectedAgent={selectedAgent}
          onSelectAgent={onSelectAgent}
        />
      </Suspense>
    </Canvas>
  );
}
