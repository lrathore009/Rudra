"use client";

import { useEffect, useState } from "react";

/** Faint mala arc behind the center column — parallax via CSS var */
export function MalaArc({ parallaxX = 0, parallaxY = 0 }: { parallaxX?: number; parallaxY?: number }) {
  const beads = 9;
  return (
    <div
      className="pointer-events-none absolute inset-x-0 top-[8%] z-0 flex justify-center opacity-[0.22] motion-safe:transition-transform motion-safe:duration-200"
      style={{ transform: `translate(${parallaxX * 0.4}px, ${parallaxY * 0.3}px)` }}
      aria-hidden="true"
    >
      <svg viewBox="0 0 400 120" className="h-28 w-[min(100%,520px)]">
        <path
          d="M 20 90 Q 200 10 380 90"
          fill="none"
          stroke="hsl(var(--rudra-gold) / 0.35)"
          strokeWidth="1"
          strokeDasharray="4 6"
        />
        {Array.from({ length: beads }).map((_, i) => {
          const t = i / (beads - 1);
          const x = 20 + t * 360;
          const y = 90 - Math.sin(t * Math.PI) * 78;
          return (
            <ellipse
              key={i}
              cx={x}
              cy={y}
              rx={5}
              ry={5.5}
              fill="hsl(22 38% 16%)"
              stroke="hsl(var(--rudra-gold) / 0.4)"
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
        stroke="hsl(var(--rudra-gold))"
        strokeWidth="1.5"
        strokeDasharray="6 4"
        className={releasing ? "thread-release" : "thread-flow"}
        style={{ filter: "drop-shadow(0 0 4px hsl(var(--rudra-saffron) / 0.5))" }}
      />
    </svg>
  );
}

/** Post-login single breath before sanctum */
export function FirstBreathOverlay({ show, onDone }: { show: boolean; onDone: () => void }) {
  useEffect(() => {
    if (!show) return;
    const t = setTimeout(onDone, 900);
    return () => clearTimeout(t);
  }, [show, onDone]);

  if (!show) return null;

  return (
    <div className="first-breath-overlay fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="rudra-breath h-32 w-32">
        <svg viewBox="0 0 100 100" className="h-full w-full">
          <ellipse cx="50" cy="52" rx="34" ry="38" fill="hsl(22 38% 18%)" stroke="hsl(var(--rudra-gold))" strokeWidth="1" />
          <ellipse cx="50" cy="50" rx="12" ry="14" fill="hsl(var(--rudra-gold-bright))" className="inner-light" />
        </svg>
      </div>
    </div>
  );
}
