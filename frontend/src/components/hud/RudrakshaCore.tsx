"use client";

import type { Ref } from "react";
import type { CoreRhythm } from "@/lib/rudra-theme";
import { facetColor } from "@/lib/rudra-theme";

const FACETS = [
  { label: "EA", agentType: "executive_assistant", angle: 0 },
  { label: "RA", agentType: "research_analyst", angle: 40 },
  { label: "CG", agentType: "concierge", angle: 80 },
  { label: "LX", agentType: "luxury_analyst", angle: 120 },
  { label: "TR", agentType: "travel", angle: 160 },
  { label: "KL", agentType: "knowledge_librarian", angle: 200 },
  { label: "WR", agentType: "writing", angle: 240 },
  { label: "PR", agentType: "presentation", angle: 280 },
  { label: "OP", agentType: "operations", angle: 320 },
];

const BREATH_CLASS: Record<CoreRhythm, string> = {
  idle: "rudra-breath",
  enriching: "rudra-breath-medium",
  streaming: "rudra-breath-fast",
  error: "rudra-breath-error",
};

export function RudrakshaCore({
  active,
  status,
  size = 220,
  activeFacet,
  activeAgentType,
  rhythm = "idle",
  errorFacet,
  malaProgress,
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
  const breath = BREATH_CLASS[rhythm] ?? (active ? "rudra-breath-fast" : "rudra-breath");
  const cx = 120;
  const cy = 120;
  const highlightTag =
    activeFacet ?? (activeAgentType ? FACETS.find((f) => f.agentType === activeAgentType)?.label : undefined);

  const statusLabel =
    rhythm === "error"
      ? "STILL"
      : rhythm === "streaming"
        ? "UNFOLDING"
        : active
          ? "CONTEMPLATING"
          : "AWAKE";

  return (
    <div ref={coreRef} className={`core-socket relative ${breath}`} style={{ width: size, height: size }}>

      <div
        className="inner-light absolute inset-[8%] rounded-full"
        style={{
          background:
            rhythm === "error"
              ? "radial-gradient(circle, hsl(var(--rudra-ember) / 0.35), transparent 65%)"
              : "radial-gradient(circle, hsl(var(--rudra-saffron) / 0.42), hsl(var(--rudra-gold) / 0.12) 55%, transparent 72%)",
          filter: active ? "blur(22px)" : "blur(16px)",
        }}
      />

      <svg viewBox="0 0 240 240" className="relative h-full w-full" aria-hidden="true">
        <defs>
          <radialGradient id="beadGrad" cx="45%" cy="38%" r="65%">
            <stop offset="0%" stopColor="hsl(28 42% 32%)" />
            <stop offset="55%" stopColor="hsl(22 38% 18%)" />
            <stop offset="100%" stopColor="hsl(20 42% 10%)" />
          </radialGradient>
          <radialGradient id="coreLight" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="hsl(var(--rudra-gold-bright))" />
            <stop offset="70%" stopColor="hsl(var(--rudra-saffron) / 0.85)" />
            <stop offset="100%" stopColor="hsl(var(--rudra-gold) / 0)" />
          </radialGradient>
          <filter id="beadGlow">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {FACETS.map((f, i) => {
          const rad = ((f.angle - 90) * Math.PI) / 180;
          const x = cx + Math.cos(rad) * 102;
          const y = cy + Math.sin(rad) * 102;
          const isActive = highlightTag === f.label;
          const isError = errorFacet === f.label;
          const dim = highlightTag && !isActive;
          const isLit = malaProgress && active && i < malaProgress.current;
          const hue = facetColor(
            f.label,
            isActive ? 0.95 : isLit ? 0.85 : active ? 0.65 : 0.35
          );

          return (
            <g key={f.label} opacity={dim ? 0.25 : 1}>
              {isError && (
                <line
                  x1={x - 4}
                  y1={y - 4}
                  x2={x + 4}
                  y2={y + 4}
                  stroke="hsl(var(--rudra-ember))"
                  strokeWidth="1.2"
                />
              )}
              <circle
                cx={x}
                cy={y}
                r={isActive ? 4.2 : isLit ? 3.8 : active ? 3.2 : 2.4}
                fill={hue}
                className={isActive || isLit || (active && !highlightTag) ? "facet-pulse" : undefined}
                style={{
                  animationDelay: `${i * 0.22}s`,
                  filter: isActive ? `drop-shadow(0 0 5px ${facetColor(f.label, 0.9)})` : undefined,
                }}
              />
              <text
                x={x}
                y={y + 0.5}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={facetColor(f.label, isActive ? 0.95 : 0.55)}
                fontSize="5"
                fontFamily="monospace"
              >
                {f.label}
              </text>
            </g>
          );
        })}

        <ellipse
          cx={cx}
          cy={cy}
          rx={78}
          ry={86}
          fill="url(#beadGrad)"
          stroke="hsl(var(--rudra-bark) / 0.9)"
          strokeWidth="1.5"
          filter="url(#beadGlow)"
        />

        {[0, 72, 144, 216, 288].map((deg, i) => (
          <path
            key={deg}
            d={`M ${cx} ${cy - 82} Q ${cx + (i % 2 === 0 ? 8 : -8)} ${cy} ${cx} ${cy + 82}`}
            fill="none"
            stroke="hsl(18 35% 8% / 0.75)"
            strokeWidth="2.2"
            className="mukhi-shimmer"
            style={{ transform: `rotate(${deg}deg)`, transformOrigin: `${cx}px ${cy}px` }}
          />
        ))}

        <ellipse
          cx={cx}
          cy={cy}
          rx={34}
          ry={38}
          fill="url(#coreLight)"
          className="inner-light"
          style={{ mixBlendMode: "screen" }}
        />
        <ellipse
          cx={cx}
          cy={cy - 4}
          rx={14}
          ry={16}
          fill="hsl(var(--rudra-gold-bright) / 0.92)"
          style={{ filter: "drop-shadow(0 0 10px hsl(var(--rudra-saffron)))" }}
        />
      </svg>

      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-hud text-sm neon">{statusLabel}</span>
        <span className="mt-0.5 font-terminal text-[8px] uppercase tracking-[0.22em] text-amber-200/45">
          ◇ sacred link
        </span>
        <span className="sr-only">{status}</span>
      </div>
    </div>
  );
}

export const ReactorCore = RudrakshaCore;
