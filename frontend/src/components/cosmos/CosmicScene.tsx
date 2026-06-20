"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";
import { CosmicEnvironment } from "./CosmicEnvironment";
import { TrishulDamru3D, type TrishulPhase } from "./TrishulDamru3D";
import { COSMOS_PLANETS, planetByAgent, planetByLabel } from "./planet-config";
import { OrbitRings, PlanetOrbit3D } from "./PlanetOrbit3D";
import { LightningBolt3D } from "./LightningBolt3D";

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
            const a = p.angle;
            setBoltTarget(
              new THREE.Vector3(
                Math.cos(a) * p.radius,
                Math.sin(a * 0.7 + p.inclination) * p.inclination * 4,
                Math.sin(a) * p.radius
              )
            );
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

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 2, 16]} fov={55} />
      <OrbitControls
        enablePan={false}
        enableZoom
        minDistance={8}
        maxDistance={28}
        maxPolarAngle={Math.PI / 1.6}
        minPolarAngle={Math.PI / 6}
        autoRotate={!processing}
        autoRotateSpeed={0.35}
        target={[0, 0, 0]}
      />
      <directionalLight position={[5, 8, 5]} intensity={0.6} color="#aaccff" />
      <CosmicEnvironment />
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
