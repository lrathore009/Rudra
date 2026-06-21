"use client";

import { useEffect, useRef, useState } from "react";
import type { GrahaId } from "@/components/cosmos/navagraha-types";
import { GRAHA_PANELS, SANCTUM_GRAHAS } from "@/data/navagraha-catalog";
import { mandalaCenter, mandalaEllipseParams, mandalaPoint2D } from "@/lib/mandala-orbit-2d";
import { cn } from "@/lib/utils";

function TrishulGlyph() {
  const { cx, cy } = mandalaCenter();
  return (
    <g transform={`translate(${cx}, ${cy})`} aria-hidden>
      <path
        d="M0 -36 L0 4 M0 4 L-16 32 M0 4 L16 32 M0 -4 L-6 -14 M0 -4 L6 -14"
        stroke="var(--mandala-gold)"
        strokeWidth="1.8"
        strokeLinecap="round"
        fill="none"
        opacity={0.85}
      />
      <circle cx={0} cy={0} r="2.5" fill="var(--mandala-gold)" opacity={0.5} />
    </g>
  );
}

function GrahaDot({
  graha,
  angle,
  lead,
  dim,
  pulse,
}: {
  graha: (typeof SANCTUM_GRAHAS)[0];
  angle: number;
  lead: boolean;
  dim: boolean;
  pulse: boolean;
}) {
  const panel = GRAHA_PANELS.find((p) => p.id === graha.id);
  const color = panel?.glow ?? graha.orbitColor;
  const p = mandalaPoint2D(graha, angle);

  return (
    <circle
      cx={p.x}
      cy={p.y}
      r={lead ? 5.5 : 4}
      fill={color}
      opacity={dim ? 0.22 : lead ? 0.95 : 0.55}
      className={cn(pulse && "mandala-dot-pulse")}
      style={lead ? { filter: `drop-shadow(0 0 6px ${color})` } : undefined}
    />
  );
}

function MandalaOrbitRing({
  graha,
  active,
  dim,
}: {
  graha: (typeof SANCTUM_GRAHAS)[0];
  active: boolean;
  dim: boolean;
}) {
  const panel = GRAHA_PANELS.find((p) => p.id === graha.id);
  const color = panel?.glow ?? graha.orbitColor;
  const { cx, cy } = mandalaCenter();
  const { rx, ry, rotation } = mandalaEllipseParams(graha);

  return (
    <ellipse
      cx={cx}
      cy={cy}
      rx={rx}
      ry={ry}
      transform={`rotate(${rotation} ${cx} ${cy})`}
      fill="none"
      stroke={color}
      strokeWidth={active ? 1 : 0.6}
      opacity={dim ? 0.08 : active ? 0.42 : 0.16}
      strokeDasharray={graha.surface === "swirl" || graha.surface === "hex" ? "3 5" : undefined}
    />
  );
}

export function FlatMandala({
  leadGrahaId,
  pulseGrahaIds = [],
  processing,
}: {
  leadGrahaId?: GrahaId;
  pulseGrahaIds?: GrahaId[];
  processing?: boolean;
}) {
  const anglesRef = useRef<Record<string, number>>({});
  const [, tick] = useState(0);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    for (const g of SANCTUM_GRAHAS) {
      if (anglesRef.current[g.id] === undefined) anglesRef.current[g.id] = g.angle;
    }
    let last = performance.now();
    const loop = (now: number) => {
      const dt = Math.min((now - last) / 1000, 0.05);
      last = now;
      for (const g of SANCTUM_GRAHAS) {
        const speed = processing && g.id === leadGrahaId ? g.speed * 2.2 : g.speed * 0.35;
        anglesRef.current[g.id] = (anglesRef.current[g.id] ?? g.angle) + dt * speed;
      }
      tick((n) => (n + 1) % 100000);
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [leadGrahaId, processing]);

  const hasLead = Boolean(leadGrahaId);

  return (
    <div className="mandala-root" aria-hidden>
      <svg className="mandala-svg" viewBox="0 0 1000 800" preserveAspectRatio="xMidYMid slice">
        <line x1={500} y1={240} x2={500} y2={520} className="mandala-cross" />
        <line x1={360} y1={380} x2={640} y2={380} className="mandala-cross" />

        {SANCTUM_GRAHAS.map((g) => (
          <MandalaOrbitRing
            key={`ring-${g.id}`}
            graha={g}
            active={g.id === leadGrahaId}
            dim={hasLead && g.id !== leadGrahaId}
          />
        ))}

        <TrishulGlyph />

        {SANCTUM_GRAHAS.map((g) => (
          <GrahaDot
            key={`dot-${g.id}`}
            graha={g}
            angle={anglesRef.current[g.id] ?? g.angle}
            lead={g.id === leadGrahaId}
            dim={hasLead && g.id !== leadGrahaId}
            pulse={pulseGrahaIds.includes(g.id)}
          />
        ))}
      </svg>
    </div>
  );
}
