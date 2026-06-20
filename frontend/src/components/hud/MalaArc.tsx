"use client";

import { useEffect, useState } from "react";

/** Constellation arc behind the center column — nine planet nodes */
export function MalaArc({ parallaxX = 0, parallaxY = 0 }: { parallaxX?: number; parallaxY?: number }) {
  const planets = [
    { hue: "190 95% 62%", size: 5 },
    { hue: "210 55% 58%", size: 4.5 },
    { hue: "262 85% 68%", size: 5.5 },
    { hue: "328 55% 58%", size: 4 },
    { hue: "165 45% 50%", size: 5 },
    { hue: "85 40% 48%", size: 4.5 },
    { hue: "200 60% 55%", size: 5 },
    { hue: "270 45% 62%", size: 4 },
    { hue: "145 45% 46%", size: 5 },
  ];
  return (
    <div
      className="pointer-events-none absolute inset-x-0 top-[8%] z-0 flex justify-center opacity-[0.28] motion-safe:transition-transform motion-safe:duration-200"
      style={{ transform: `translate(${parallaxX * 0.4}px, ${parallaxY * 0.3}px)` }}
      aria-hidden="true"
    >
      <svg viewBox="0 0 400 120" className="h-28 w-[min(100%,520px)]">
        <path
          d="M 20 90 Q 200 10 380 90"
          fill="none"
          stroke="hsl(var(--cosmos-cyan) / 0.3)"
          strokeWidth="1"
          strokeDasharray="3 8"
        />
        {planets.map((p, i) => {
          const t = i / (planets.length - 1);
          const x = 20 + t * 360;
          const y = 90 - Math.sin(t * Math.PI) * 78;
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r={p.size}
              fill={`hsl(${p.hue} / 0.35)`}
              stroke={`hsl(${p.hue} / 0.65)`}
              strokeWidth="0.6"
            />
          );
        })}
      </svg>
    </div>
  );
}

/** Overlay SVG thread from core to streaming message */
export function StreamingThread({
  active,
  releasing,
  coreRect,
  targetRect,
}: {
  active: boolean;
  releasing?: boolean;
  coreRect: DOMRect | null;
  targetRect: DOMRect | null;
}) {
  const [path, setPath] = useState("");

  useEffect(() => {
    if (!active || !coreRect || !targetRect) {
      setPath("");
      return;
    }
    const x1 = coreRect.left + coreRect.width / 2;
    const y1 = coreRect.bottom - 8;
    const x2 = targetRect.left + 12;
    const y2 = targetRect.top + 12;
    const midY = (y1 + y2) / 2;
    setPath(`M ${x1} ${y1} Q ${(x1 + x2) / 2} ${midY} ${x2} ${y2}`);
  }, [active, coreRect, targetRect]);

  if (!path) return null;

  return (
    <svg className="pointer-events-none fixed inset-0 z-[15] h-full w-full" aria-hidden="true">
      <path
        d={path}
        fill="none"
        stroke="hsl(var(--cosmos-cyan))"
        strokeWidth="1.5"
        strokeDasharray="6 4"
        className={releasing ? "thread-release" : "thread-flow"}
        style={{ filter: "drop-shadow(0 0 4px hsl(var(--cosmos-violet) / 0.5))" }}
      />
    </svg>
  );
}

/** Post-login single breath before the command deck */
export function FirstBreathOverlay({ show, onDone }: { show: boolean; onDone: () => void }) {
  useEffect(() => {
    if (!show) return;
    const t = setTimeout(onDone, 900);
    return () => clearTimeout(t);
  }, [show, onDone]);

  if (!show) return null;

  return (
    <div className="first-breath-overlay fixed inset-0 z-[60] flex items-center justify-center bg-background/85 backdrop-blur-sm">
      <div className="rudra-breath h-32 w-32">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/trident-core.png"
          alt=""
          className="h-full w-full object-contain trident-idle"
          style={{
            mixBlendMode: "screen",
            filter: "drop-shadow(0 0 24px hsl(var(--cosmos-cyan) / 0.75))",
          }}
        />
      </div>
    </div>
  );
}
