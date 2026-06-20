"use client";

import { useEffect, useMemo, useState } from "react";

function frac(x: number): number {
  return x - Math.floor(x);
}

function buildParticles() {
  return Array.from({ length: 24 }).map((_, i) => {
    const f = (n: number) => frac(Math.sin(i * 127.1 + n * 311.7) * 43758.5453);
    return {
      left: Math.round(f(1) * 10000) / 100,
      top: Math.round(f(2) * 10000) / 100,
      size: Math.round((1 + f(3) * 2) * 100) / 100,
      delay: Math.round(f(4) * 800) / 100,
      dur: Math.round((7 + f(5) * 10) * 100) / 100,
      op: Math.round((0.12 + f(6) * 0.4) * 1000) / 1000,
    };
  });
}

export function HudBackground({ still = false }: { still?: boolean }) {
  const [mounted, setMounted] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);
  const particles = useMemo(() => buildParticles(), []);

  useEffect(() => {
    setMounted(true);
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduceMotion(mq.matches);
    const fn = () => setReduceMotion(mq.matches);
    mq.addEventListener("change", fn);
    return () => mq.removeEventListener("change", fn);
  }, []);

  const showParticles = mounted && !still && !reduceMotion;

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden scanlines">
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at 50% 30%, hsl(28 38% 10%), hsl(24 28% 4%) 58%, hsl(22 32% 2%))",
        }}
      />
      <div className="absolute inset-0 hud-grid" />
      <div className="absolute inset-0 vignette" />
      {showParticles &&
        particles.map((p, i) => (
          <span
            key={i}
            className="absolute rounded-full"
            style={{
              left: `${p.left}%`,
              top: `${p.top}%`,
              width: p.size,
              height: p.size,
              background: "hsl(var(--rudra-gold-bright))",
              opacity: p.op,
              boxShadow: "0 0 5px hsl(var(--rudra-saffron) / 0.6)",
              animation: `floatY ${p.dur}s ease-in-out ${p.delay}s infinite`,
            }}
          />
        ))}
      {!reduceMotion && (
        <div
          className="scan-sweep absolute left-0 right-0 h-24"
          style={{
            background:
              "linear-gradient(180deg, transparent, hsl(var(--rudra-saffron) / 0.05), transparent)",
          }}
        />
      )}
    </div>
  );
}
