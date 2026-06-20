"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { Mic, Square, Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import type { CosmicUI3DProps } from "./cosmic-ui-types";

const CONSOLE_POS: [number, number, number] = [0, -3.6, 10.8];
const CONSOLE_ROT: [number, number, number] = [-0.14, 0, 0];

export function CommandConsole3D({
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  processing,
  placeholder,
  streamingActive,
}: Pick<
  CosmicUI3DProps,
  "input" | "onInputChange" | "onSubmit" | "onStop" | "onVoice" | "listening" | "processing" | "placeholder"
> & { streamingActive?: boolean }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!groupRef.current) return;
    groupRef.current.position.y = CONSOLE_POS[1] + Math.sin(state.clock.elapsedTime * 0.6) * 0.06;
  });

  return (
    <group ref={groupRef} position={CONSOLE_POS} rotation={CONSOLE_ROT}>
      {/* extruded console slab */}
      <mesh position={[0, 0, -0.08]} castShadow receiveShadow>
        <boxGeometry args={[9.2, 0.55, 0.35]} />
        <meshPhysicalMaterial
          color="#0a0e18"
          emissive="#1a2844"
          emissiveIntensity={0.35}
          metalness={0.85}
          roughness={0.35}
          clearcoat={0.4}
        />
      </mesh>
      <mesh position={[0, 0.28, 0]} castShadow>
        <boxGeometry args={[9.0, 0.06, 0.38]} />
        <meshPhysicalMaterial color="#ddaa44" emissive="#886622" emissiveIntensity={0.55} metalness={1} roughness={0.12} clearcoat={1} />
      </mesh>
      <mesh position={[0, -0.02, 0.12]}>
        <boxGeometry args={[8.6, 0.02, 0.08]} />
        <meshBasicMaterial color="#55ccff" transparent opacity={0.25} />
      </mesh>
      {/* side struts */}
      {([-1, 1] as const).map((side) => (
        <mesh key={side} position={[side * 4.2, -0.35, 0.05]}>
          <boxGeometry args={[0.12, 0.5, 0.12]} />
          <meshStandardMaterial color="#334466" metalness={0.9} roughness={0.3} />
        </mesh>
      ))}

      <Html transform distanceFactor={8.5} position={[0, 0.05, 0.22]} style={{ width: "420px" }}>
        <form
          className="cosmic-command-panel pointer-events-auto flex w-full items-center gap-3 px-4 py-2.5"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <input
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            disabled={processing && !streamingActive}
            placeholder={placeholder}
            className="cosmic-command-input min-w-0 flex-1 bg-transparent font-display text-xs uppercase tracking-wide outline-none sm:text-sm"
            autoComplete="off"
          />
          <button
            type="button"
            onClick={onVoice}
            className={cn("cosmic-icon-btn", listening && "cosmic-icon-btn-active")}
            title="Voice uplink"
          >
            <Mic className="h-3.5 w-3.5" />
          </button>
          {processing ? (
            <button type="button" onClick={onStop} className="cosmic-icon-btn cosmic-icon-btn-stop" title="Stop">
              <Square className="h-3 w-3 fill-current" />
            </button>
          ) : (
            <button type="submit" disabled={!input.trim()} className="cosmic-icon-btn cosmic-icon-btn-send" title="Transmit">
              <Upload className="h-3.5 w-3.5" />
            </button>
          )}
        </form>
      </Html>
    </group>
  );
}
