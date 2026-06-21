"use client";

import { Suspense, useEffect, useMemo, useRef, useState, type Ref } from "react";
import { Canvas } from "@react-three/fiber";
import { PerspectiveCamera, Environment, ContactShadows } from "@react-three/drei";
import { CosmicNavigation } from "./CosmicNavigation";
import type { CosmicNavHandle } from "./cosmic-nav-types";
import * as THREE from "three";
import { CosmicEnvironment } from "./CosmicEnvironment";
import { TrishulDamru3D, type TrishulPhase } from "./TrishulDamru3D";
import { RudraPlatform } from "./RudraPlatform";
import { NAVAGRAHA, THIRD_EYE_OFFSET, TRISHUL_SCALE, grahaById, grahaPosition, type GrahaId } from "./navagraha-config";
import { GrahaOrbit3D, GrahaPositionsProvider, useGrahaPositionsRef } from "./GrahaOrbit3D";
import { LightningBolt3D } from "./LightningBolt3D";
import { useReducedMotion } from "./use-reduced-motion";
import { ArcReactorRing3D } from "./ArcReactorRing3D";
import { GrahaRimLabels3D } from "./GrahaRimLabels3D";

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
  variant = "main",
  streamingActive,
  navRef,
  listening = false,
}: {
  processing: boolean;
  leadGrahaId?: GrahaId;
  supportingGrahaIds: GrahaId[];
  pulseGrahaIds: GrahaId[];
  errorFacet?: string;
  variant?: "main" | "login";
  streamingActive?: boolean;
  navRef?: Ref<CosmicNavHandle | null>;
  listening?: boolean;
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
              const pos = positionsRef.current.get(leadGrahaId);
              const g = grahaById(leadGrahaId);
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

  const isLogin = variant === "login";

  return (
    <>
      <PerspectiveCamera makeDefault position={isLogin ? [0, 0.6, 22] : [0, 0.8, 26]} fov={isLogin ? 50 : 54} />
      <CosmicNavigation variant={variant} navRef={navRef} />
      <directionalLight
        castShadow
        position={[6, 18, 14]}
        intensity={1.55}
        color="#fff4e8"
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={60}
        shadow-camera-left={-18}
        shadow-camera-right={18}
        shadow-camera-top={18}
        shadow-camera-bottom={-18}
        shadow-bias={-0.00015}
      />
      <directionalLight position={[-8, 6, -10]} intensity={0.45} color="#6688cc" />
      <pointLight position={[-6, 8, 10]} intensity={0.65} color="#8866cc" />
      <pointLight position={[6, 4, -8]} intensity={0.42} color="#4488ff" />
      <pointLight position={[0, -2, 8]} intensity={2.1} color="#ffcc88" />
      <ambientLight intensity={0.22} color="#2a2844" />
      <Environment preset="night" environmentIntensity={0.42} />
      <ContactShadows position={[0, -3.4, 0]} opacity={0.42} scale={28} blur={2.4} far={12} color="#0a0818" />
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

      <group renderOrder={100}>
        <ArcReactorRing3D processing={processing} listening={listening} reducedMotion={reducedMotion} />
        <TrishulDamru3D
          phase={eyePhaseFromCosmos(phase)}
          spinning={spinning}
          scale={TRISHUL_SCALE}
          reducedMotion={reducedMotion}
        />
      </group>
      <LightningBolt3D origin={thirdEyeOrigin} target={boltTarget} active={showBolt} />

      {isLogin && (
        <GrahaRimLabels3D
          leadGrahaId={leadGrahaId}
          supportingGrahaIds={supportingGrahaIds}
          pulseGrahaIds={pulseGrahaIds}
          processing={processing}
        />
      )}
    </>
  );
}

export function CosmicScene({
  processing,
  leadGrahaId,
  supportingGrahaIds = [],
  pulseGrahaIds = [],
  errorFacet,
  variant = "main",
  streamingActive,
  navRef,
  listening = false,
}: {
  processing: boolean;
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
  errorFacet?: string;
  variant?: "main" | "login";
  streamingActive?: boolean;
  navRef?: Ref<CosmicNavHandle | null>;
  listening?: boolean;
}) {
  return (
    <Canvas
      className="cosmic-canvas"
      shadows
      gl={{ antialias: true, alpha: false, powerPreference: "high-performance", logarithmicDepthBuffer: true }}
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
            variant={variant}
            streamingActive={streamingActive}
            navRef={navRef}
            listening={listening}
          />
        </GrahaPositionsProvider>
      </Suspense>
    </Canvas>
  );
}
