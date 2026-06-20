"use client";

import { Html } from "@react-three/drei";
import { Volume2, VolumeX } from "lucide-react";
import { SutraWordmark, RudraTagline } from "@/components/hud/SutraWordmark";
import { FOOTER_TICKER_SEGMENTS, themeModeLabel } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";
import type { CosmicUI3DProps } from "./cosmic-ui-types";

function StatusDot({ active }: { active: boolean }) {
  return <span className={cn("cosmic-status-dot", active && "cosmic-status-dot-live")} aria-hidden />;
}

export function SanctumChrome3D({
  themeMode,
  onThemeCycle,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  tickerIdx,
  uplinkActive = true,
  memorySynced = true,
  leadGrahaName,
  supportingGrahaNames,
  processing,
}: Pick<
  CosmicUI3DProps,
  | "themeMode"
  | "onThemeCycle"
  | "status"
  | "clock"
  | "onLogout"
  | "muted"
  | "onToggleMute"
  | "tickerIdx"
  | "uplinkActive"
  | "memorySynced"
  | "leadGrahaName"
  | "supportingGrahaNames"
  | "processing"
>) {
  const nominal = status.toLowerCase().includes("nominal") || status.toLowerCase().includes("online");
  const footerSegment = FOOTER_TICKER_SEGMENTS[tickerIdx % FOOTER_TICKER_SEGMENTS.length];

  return (
    <>
      {/* Header arc panel */}
      <group position={[0, 4.2, 12.5]} rotation={[-0.08, 0, 0]}>
        <mesh>
          <boxGeometry args={[14, 1.2, 0.12]} />
          <meshPhysicalMaterial color="#060810" emissive="#112244" emissiveIntensity={0.25} metalness={0.9} roughness={0.4} transparent opacity={0.85} />
        </mesh>
        <Html transform distanceFactor={11} position={[0, 0, 0.08]} center style={{ width: "680px" }}>
          <div className="pointer-events-auto grid grid-cols-[1fr_auto_1fr] items-center gap-2 px-2">
            <div className="flex flex-col gap-0.5">
              <SutraWordmark className="text-sm" />
              <RudraTagline />
            </div>
            <span className={cn("cosmic-status-badge", nominal && "cosmic-status-badge-nominal")}>
              <span className="cosmic-status-signal">((o))</span>
              {nominal ? "Present · Nominal" : status}
            </span>
            <div className="ml-auto flex items-center justify-end gap-2 font-terminal text-[10px]">
              <button type="button" onClick={onThemeCycle} className="cosmic-ctl">
                {themeModeLabel(themeMode)}
              </button>
              <span className="text-muted-foreground tabular-nums">
                {clock ? clock.toLocaleTimeString("en-GB") : "--:--:--"}
              </span>
              <button type="button" onClick={onLogout} className="cosmic-ctl">
                Exit
              </button>
              <button type="button" onClick={onToggleMute} className="cosmic-ctl-icon" title={muted ? "Unmute" : "Mute"}>
                {muted ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
              </button>
            </div>
          </div>
        </Html>
      </group>

      {/* Lead graha chip — floats in Z between altar and console */}
      {processing && leadGrahaName && (
        <Html position={[0, 0.5, 8.5]} center distanceFactor={10} transform style={{ pointerEvents: "none" }}>
          <div className="flex flex-wrap items-center justify-center gap-2 font-terminal text-[9px] uppercase tracking-widest">
            <span className="text-primary/80">Rudra commanding</span>
            <span className="cosmic-graha-chip cosmic-graha-chip-lead">Lead · {leadGrahaName}</span>
            {supportingGrahaNames && supportingGrahaNames.length > 0 && (
              <span className="text-muted-foreground/70">Support · {supportingGrahaNames.join(" · ")}</span>
            )}
          </div>
        </Html>
      )}

      {/* Footer arc */}
      <group position={[0, -5.2, 11.2]} rotation={[0.06, 0, 0]}>
        <mesh>
          <boxGeometry args={[14, 0.65, 0.1]} />
          <meshPhysicalMaterial color="#060810" emissive="#112244" emissiveIntensity={0.2} metalness={0.9} roughness={0.45} transparent opacity={0.8} />
        </mesh>
        <Html transform distanceFactor={11} position={[0, 0, 0.06]} center style={{ width: "680px" }}>
          <footer className="pointer-events-none flex items-center justify-between font-terminal text-[8px] uppercase tracking-[0.14em] text-muted-foreground/55">
            <span className="cosmic-footer-status">
              <StatusDot active={uplinkActive} />
              Encrypted uplink · {uplinkActive ? "Active" : "Offline"}
              <StatusDot active={memorySynced} />
              · {footerSegment}
            </span>
            <span className="shrink-0">Trishula OS v1.0 · Rudra Core Online</span>
          </footer>
        </Html>
      </group>
    </>
  );
}
