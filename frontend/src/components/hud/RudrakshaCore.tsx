"use client";

import { useEffect, useRef, useState, type Ref } from "react";
import type { CoreRhythm } from "@/lib/rudra-theme";
import { facetColor } from "@/lib/rudra-theme";

type PlanetKind = "ringed" | "data" | "cloud" | "luxe" | "ocean" | "glyph" | "ink" | "facet" | "grid";

interface Planet {
  label: string;
  agentType: string;
  angle: number;
  kind: PlanetKind;
}

// Nine facets → nine distinct orbiting planets, each styled to its specialty.
const PLANETS: Planet[] = [
  { label: "EA", agentType: "executive_assistant", angle: 0, kind: "ringed" },
  { label: "RA", agentType: "research_analyst", angle: 40, kind: "data" },
  { label: "CG", agentType: "concierge", angle: 80, kind: "cloud" },
  { label: "LX", agentType: "luxury_analyst", angle: 120, kind: "luxe" },
  { label: "TR", agentType: "travel", angle: 160, kind: "ocean" },
  { label: "KL", agentType: "knowledge_librarian", angle: 200, kind: "glyph" },
  { label: "WR", agentType: "writing", angle: 240, kind: "ink" },
  { label: "PR", agentType: "presentation", angle: 280, kind: "facet" },
  { label: "OP", agentType: "operations", angle: 320, kind: "grid" },
];

type Phase = "idle" | "awakening" | "dispatch" | "working" | "error";

const EYE_OPEN: Record<Phase, number> = {
  idle: 0.05,
  awakening: 0.42,
  dispatch: 0.62,
  working: 0.06,
  error: 0,
};

function tagFor(activeFacet?: string, activeAgentType?: string): string | undefined {
  if (activeFacet) return activeFacet;
  if (!activeAgentType) return undefined;
  return PLANETS.find((p) => p.agentType === activeAgentType)?.label;
}

/** Distinct planet surface per specialty — hue comes from facetColor, texture from kind. */
function planetBackground(kind: PlanetKind, hue: string, hueSoft: string): string {
  switch (kind) {
    case "data":
      return `radial-gradient(circle at 34% 30%, ${hue}, ${hueSoft} 60%, #04060f 100%)`;
    case "cloud":
      return `radial-gradient(circle at 38% 32%, #eafcff, ${hue} 55%, ${hueSoft} 100%)`;
    case "luxe":
      return `radial-gradient(circle at 36% 30%, #ffe8f2, ${hue} 50%, ${hueSoft} 100%)`;
    case "ocean":
      return `radial-gradient(circle at 35% 30%, #d6fbff, ${hue} 55%, ${hueSoft} 100%)`;
    case "ink":
      return `radial-gradient(circle at 35% 30%, #ffe6c2, ${hue} 52%, ${hueSoft} 100%)`;
    case "facet":
      return `conic-gradient(from 20deg, ${hue}, ${hueSoft}, ${hue}, ${hueSoft}, ${hue})`;
    case "grid":
      return `radial-gradient(circle at 36% 30%, ${hue}, ${hueSoft} 70%, #04100a 100%)`;
    case "glyph":
      return `radial-gradient(circle at 36% 30%, ${hue}, ${hueSoft} 70%, #0a1004 100%)`;
    case "ringed":
    default:
      return `radial-gradient(circle at 36% 30%, #fff3d0, ${hue} 50%, ${hueSoft} 100%)`;
  }
}

export function RudrakshaCore({
  active,
  status,
  size = 220,
  activeFacet,
  activeAgentType,
  rhythm = "idle",
  errorFacet,
  coreRef,
}: {
  active: boolean;
  status: string;
  size?: number;
  activeFacet?: string;
  activeAgentType?: string;
  rhythm?: CoreRhythm;
  errorFacet?: string;
  malaProgress?: { current: number; total: number };
  coreRef?: Ref<HTMLDivElement>;
}) {
  const routedTag = tagFor(activeFacet, activeAgentType);
  const [phase, setPhase] = useState<Phase>("idle");
  const [bolt, setBolt] = useState<string | null>(null);
  const [awoken, setAwoken] = useState<string | null>(null);
  const dispatchedRef = useRef(false);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  // Lifecycle: idle → (submit) awakening → (routing known) dispatch+lightning → working → idle.
  useEffect(() => {
    const clear = () => {
      timers.current.forEach(clearTimeout);
      timers.current = [];
    };
    if (errorFacet) {
      clear();
      setPhase("error");
      setBolt(null);
      return;
    }
    if (!active) {
      clear();
      setPhase("idle");
      setBolt(null);
      setAwoken(null);
      dispatchedRef.current = false;
      return;
    }
    // active
    if (!dispatchedRef.current) {
      if (routedTag) {
        // The eye opens fully, trident rises + spins, then fires lightning at the planet.
        dispatchedRef.current = true;
        setPhase("dispatch");
        setBolt(routedTag);
        setAwoken(routedTag);
        timers.current.push(
          setTimeout(() => {
            setBolt(null);
            // The eye never stays open without reason — it closes once the order is sent.
            setPhase("working");
          }, 900)
        );
      } else {
        setPhase("awakening");
      }
    }
    return clear;
  }, [active, routedTag, errorFacet]);

  const eyeOpen = EYE_OPEN[phase];
  const tridentClass =
    phase === "dispatch"
      ? "trident-lifted trident-spin"
      : phase === "awakening"
        ? "trident-lifted"
        : "trident-idle";

  const stage = size;
  const tridentW = Math.round(stage * 0.5);
  const cx = stage / 2;
  const cy = stage / 2;
  const R = stage * 0.4;

  // Resolve the struck planet's pixel position for the lightning path.
  const struck = bolt ? PLANETS.find((p) => p.label === bolt) : undefined;
  let boltTarget: { x: number; y: number } | null = null;
  if (struck) {
    const rad = ((struck.angle - 90) * Math.PI) / 180;
    boltTarget = { x: cx + Math.cos(rad) * R, y: cy + Math.sin(rad) * R };
  }

  function boltPath(x: number, y: number): string {
    const sx = cx;
    const sy = cy - tridentW * 0.06; // from the eye, slightly above center
    const mx = (sx + x) / 2;
    const my = (sy + y) / 2;
    const nx = -(y - sy);
    const ny = x - sx;
    const len = Math.hypot(nx, ny) || 1;
    const j = stage * 0.05;
    const j2 = stage * 0.035;
    return `M ${sx} ${sy} L ${mx + (nx / len) * j} ${my + (ny / len) * j} L ${
      (mx + x) / 2 - (nx / len) * j2
    } ${(my + y) / 2 - (ny / len) * j2} L ${x} ${y}`;
  }

  const statusLabel =
    phase === "error"
      ? "STILL"
      : phase === "dispatch"
        ? "DISPATCHING"
        : phase === "working"
          ? "UNFOLDING"
          : active
            ? "AWAKENING"
            : "AWAKE";

  void rhythm;

  return (
    <div ref={coreRef} className="core-socket relative" style={{ width: stage, height: stage }}>
      {/* central glow */}
      <div
        className="inner-light absolute inset-[14%] rounded-full"
        style={{
          background:
            phase === "error"
              ? "radial-gradient(circle, hsl(var(--rudra-ember) / 0.3), transparent 65%)"
              : "radial-gradient(circle, hsl(var(--cosmos-violet) / 0.34), hsl(var(--cosmos-cyan) / 0.12) 55%, transparent 72%)",
          filter: active ? "blur(26px)" : "blur(18px)",
        }}
      />

      {/* orbit rings */}
      <div className="cosmos-orbit">
        <div className="cosmos-orbit-ring" style={{ inset: "6%" }} />
        <div className="cosmos-orbit-ring" style={{ inset: "20%", opacity: 0.6 }} />
      </div>

      {/* nine planets */}
      {PLANETS.map((p, i) => {
        const rad = ((p.angle - 90) * Math.PI) / 180;
        const x = cx + Math.cos(rad) * R;
        const y = cy + Math.sin(rad) * R;
        const isRouted = routedTag === p.label;
        const isAwoken = awoken === p.label;
        const isError = errorFacet === p.label;
        const dim = routedTag && !isRouted ? 0.4 : 1;
        const pd = stage * (isRouted ? 0.13 : 0.1);
        const hue = facetColor(p.label, 1);
        const hueSoft = facetColor(p.label, 0.45);
        return (
          <div
            key={p.label}
            className={`planet-body ${isAwoken ? "planet-awaken" : ""} ${p.kind === "ringed" ? "planet-ringed" : ""}`}
            style={{
              left: x,
              top: y,
              width: pd,
              height: pd,
              color: hue,
              opacity: dim,
              background: planetBackground(p.kind, hue, hueSoft),
              boxShadow: isRouted
                ? `0 0 14px ${facetColor(p.label, 0.9)}, 0 0 28px ${facetColor(p.label, 0.4)}`
                : `0 0 6px ${facetColor(p.label, 0.4)}`,
              animationDelay: `${i * 0.3}s`,
              border: isError ? "1px solid hsl(var(--rudra-ember))" : undefined,
            }}
            title={p.label}
          >
            {p.kind === "grid" && (
              <span
                className="absolute inset-0 rounded-full"
                style={{
                  backgroundImage:
                    "linear-gradient(currentColor 1px, transparent 1px), linear-gradient(90deg, currentColor 1px, transparent 1px)",
                  backgroundSize: "5px 5px",
                  opacity: 0.25,
                }}
              />
            )}
            {p.kind === "data" && (
              <span
                className="absolute inset-0 rounded-full"
                style={{
                  backgroundImage:
                    "repeating-linear-gradient(90deg, #bfeaff 0 1px, transparent 1px 4px)",
                  opacity: 0.4,
                }}
              />
            )}
            {p.kind === "glyph" && (
              <span
                className="absolute inset-[-30%] rounded-full"
                style={{ border: "1px solid currentColor", opacity: 0.4 }}
              />
            )}
          </div>
        );
      })}

      {/* lightning from the third eye to the routed planet */}
      {boltTarget && (
        <svg
          className="pointer-events-none absolute inset-0"
          viewBox={`0 0 ${stage} ${stage}`}
          width={stage}
          height={stage}
          aria-hidden="true"
        >
          <path
            className="lightning-bolt"
            d={boltPath(boltTarget.x, boltTarget.y)}
            fill="none"
            stroke="hsl(var(--cosmos-cyan))"
            strokeWidth="2.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            className="lightning-bolt"
            d={boltPath(boltTarget.x, boltTarget.y)}
            fill="none"
            stroke="#ffffff"
            strokeWidth="0.9"
            strokeLinecap="round"
          />
        </svg>
      )}

      {/* trident core (image) + vertical third eye overlay */}
      <div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
        style={{ width: tridentW }}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/trident-core.png"
          alt="Rudra trishula"
          width={tridentW}
          height={Math.round(tridentW * 1.5)}
          className={`trident-img ${tridentClass}`}
          style={{
            width: tridentW,
            height: "auto",
            mixBlendMode: "screen",
            WebkitMaskImage:
              "radial-gradient(ellipse 58% 74% at 50% 46%, #000 52%, transparent 100%)",
            maskImage: "radial-gradient(ellipse 58% 74% at 50% 46%, #000 52%, transparent 100%)",
            filter:
              phase === "error"
                ? "drop-shadow(0 0 10px hsl(var(--rudra-ember) / 0.6)) saturate(0.7)"
                : `drop-shadow(0 0 ${active ? 14 : 8}px hsl(var(--cosmos-violet) / 0.5))`,
          }}
        />

        {/* the vertical third eye sits on the crossguard, opens by phase */}
        <div className="third-eye" style={{ top: "50%", opacity: phase === "error" ? 0.25 : 1 }}>
          <svg width={tridentW * 0.3} height={tridentW * 0.34} viewBox="0 0 30 34" aria-hidden="true">
            {/* tripundra — three sacred lines above the eye */}
            {[0, 1, 2].map((k) => (
              <line
                key={k}
                x1={9 + k * 4}
                y1={3}
                x2={9 + k * 4}
                y2={9}
                stroke="hsl(var(--rudra-gold-bright) / 0.8)"
                strokeWidth="1.1"
                strokeLinecap="round"
              />
            ))}
            <g
              className="third-eye-lens"
              style={{ transform: `scaleY(${Math.max(eyeOpen, 0.04)})`, transformOrigin: "15px 21px" }}
            >
              {/* vertical almond eye */}
              <path
                d="M15 9 C19 14, 19 28, 15 33 C11 28, 11 14, 15 9 Z"
                fill="hsl(var(--cosmos-deep))"
                stroke="hsl(var(--rudra-gold-bright))"
                strokeWidth="0.9"
              />
              <ellipse
                cx="15"
                cy="21"
                rx="3"
                ry="7"
                fill="hsl(var(--cosmos-cyan))"
                opacity={eyeOpen > 0.3 ? 1 : 0.4}
                style={{ filter: "drop-shadow(0 0 4px hsl(var(--cosmos-cyan)))" }}
              />
              <ellipse cx="15" cy="21" rx="1.2" ry="3.4" fill="#ffffff" opacity={eyeOpen > 0.3 ? 0.9 : 0.3} />
            </g>
            {/* closed seam glow */}
            <line
              x1="15"
              y1="10"
              x2="15"
              y2="32"
              stroke="hsl(var(--rudra-gold-bright))"
              strokeWidth={eyeOpen < 0.15 ? 1.2 : 0.4}
              opacity={eyeOpen < 0.15 ? 0.9 : 0.2}
              style={{ filter: "drop-shadow(0 0 3px hsl(var(--rudra-saffron)))" }}
            />
          </svg>
        </div>
      </div>

      <div className="pointer-events-none absolute inset-x-0 bottom-1 flex flex-col items-center justify-center">
        <span className="font-hud text-xs neon">{statusLabel}</span>
        <span className="sr-only">{status}</span>
      </div>
    </div>
  );
}

export const ReactorCore = RudrakshaCore;
