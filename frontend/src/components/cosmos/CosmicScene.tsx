"use client";

import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, Environment } from "@react-three/drei";
import * as THREE from "three";
import { CosmicEnvironment } from "./CosmicEnvironment";
import { TrishulDamru3D, type TrishulPhase } from "./TrishulDamru3D";
import { RudraPlatform } from "./RudraPlatform";
import { NAVAGRAHA, THIRD_EYE_OFFSET, TRISHUL_SCALE, grahaById, grahaPosition, type GrahaId } from "./navagraha-config";
import { GrahaOrbit3D, GrahaPositionsProvider, useGrahaPositionsRef } from "./GrahaOrbit3D";
import { LightningBolt3D } from "./LightningBolt3D";
import { useReducedMotion } from "./use-reduced-motion";

export type CosmosPhase =
  | "idle"
  | "query"
  | "analysis"
  | "dispatch"
  | "working"
  | "completed"
  | "error";

function eyePhaseFromCosmos(phase: CosmosPhase): TrishulPhase {
  switch (phase) {
    case "query":
      return "query";
    case "analysis":
      return "analysis";
    case "dispatch":
      return "dispatch";
    case "working":
      return "working";
    case "completed":
      return "completed";
    case "error":
      return "error";
    default:
      return "idle";
  }
}

function SceneContent({
  processing,
  leadGrahaId,
  supportingGrahaIds,
  pulseGrahaIds,
  errorFacet,
}: {
  processing: boolean;
  leadGrahaId?: GrahaId;
  supportingGrahaIds: GrahaId[];
  pulseGrahaIds: GrahaId[];
  errorFacet?: string;
}) {
  const reducedMotion = useReducedMotion();
  const positionsRef = useGrahaPositionsRef();
  const [phase, setPhase] = useState<CosmosPhase>("idle");
  const [boltTarget, setBoltTarget] = useState<THREE.Vector3 | null>(null);
  const [spinning, setSpinning] = useState(false);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  const thirdEyeOrigin = useMemo(
    () =>
      new THREE.Vector3(
        THIRD_EYE_OFFSET.x,
        THIRD_EYE_OFFSET.y - 0.35 + (TRISHUL_SCALE - 1) * 0.5,
        THIRD_EYE_OFFSET.z
      ),
    []
  );

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
      if (phase !== "idle" && phase !== "completed") {
        setPhase("completed");
        timers.current.push(
          setTimeout(() => {
            setPhase("idle");
            setSpinning(false);
            setBoltTarget(null);
          }, 600)
        );
      } else {
        setPhase("idle");
        setSpinning(false);
        setBoltTarget(null);
      }
      return;
    }

    setPhase("query");
    timers.current.push(
      setTimeout(() => {
        setPhase("analysis");
        timers.current.push(
          setTimeout(() => {
            if (leadGrahaId) {
              setPhase("dispatch");
              setSpinning(true);
              const g = grahaById(leadGrahaId);
              const pos = positionsRef.current.get(leadGrahaId);
              const fallback = g ? grahaPosition(g, g.angle) : null;
              if (pos || fallback) {
                setBoltTarget(
                  pos?.clone() ?? new THREE.Vector3(fallback!.x, fallback!.y, fallback!.z)
                );
              }
              timers.current.push(
                setTimeout(() => {
                  setPhase("working");
                  setSpinning(false);
                  setBoltTarget(null);
                }, 2800)
              );
            } else {
              setPhase("working");
            }
          }, 700)
        );
      }, 350)
    );

    return () => timers.current.forEach(clearTimeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [processing, leadGrahaId, errorFacet]);

  const neuralIntensity =
    phase === "analysis" ? 1.8 : phase === "query" ? 1.2 : phase === "dispatch" ? 1.4 : processing ? 0.9 : 0.5;

  const showBolt = phase === "dispatch" && boltTarget !== null;

  const grahaRole = (id: GrahaId): "idle" | "lead" | "supporting" | "pulse" => {
    if (leadGrahaId === id && (phase === "dispatch" || phase === "working")) return "lead";
    if (supportingGrahaIds.includes(id) && (phase === "analysis" || phase === "dispatch" || phase === "working"))
      return "supporting";
    if (pulseGrahaIds.includes(id) && (phase === "analysis" || phase === "query")) return "pulse";
    return "idle";
  };

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 2, 30]} fov={52} />
      <OrbitControls
        enablePan={false}
        enableZoom
        minDistance={18}
        maxDistance={48}
        maxPolarAngle={Math.PI / 1.75}
        minPolarAngle={Math.PI / 3.2}
        autoRotate={!processing && !reducedMotion}
        autoRotateSpeed={0.12}
        target={[0, 0.5, 0]}
      />
      <directionalLight position={[4, 16, 22]} intensity={1.1} color="#ffeedd" />
      <pointLight position={[-6, 8, 10]} intensity={0.6} color="#8866cc" />
      <pointLight position={[6, 4, -8]} intensity={0.4} color="#4488ff" />
      <ambientLight intensity={0.22} color="#2a2844" />
      <Environment preset="night" environmentIntensity={0.28} />
      <CosmicEnvironment neuralIntensity={neuralIntensity} reducedMotion={reducedMotion} />

      <RudraPlatform reducedMotion={reducedMotion} />

      {NAVAGRAHA.map((g) => (
        <GrahaOrbit3D
          key={g.id}
          graha={g}
          role={grahaRole(g.id)}
          processing={processing}
          reducedMotion={reducedMotion}
        />
      ))}

      <TrishulDamru3D
        phase={eyePhaseFromCosmos(phase)}
        spinning={spinning}
        scale={TRISHUL_SCALE}
        reducedMotion={reducedMotion}
      />
      <LightningBolt3D origin={thirdEyeOrigin} target={boltTarget} active={showBolt} />
    </>
  );
}

export function CosmicScene({
  processing,
  leadGrahaId,
  supportingGrahaIds = [],
  pulseGrahaIds = [],
  errorFacet,
}: {
  processing: boolean;
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
  errorFacet?: string;
}) {
  return (
    <Canvas
      className="cosmic-canvas"
      gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
      dpr={[1, 1.75]}
    >
      <Suspense fallback={null}>
        <GrahaPositionsProvider>
          <SceneContent
            processing={processing}
            leadGrahaId={leadGrahaId}
            supportingGrahaIds={supportingGrahaIds}
            pulseGrahaIds={pulseGrahaIds}
            errorFacet={errorFacet}
          />
        </GrahaPositionsProvider>
      </Suspense>
    </Canvas>
  );
}
