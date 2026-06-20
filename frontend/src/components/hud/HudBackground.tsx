"use client";

import { useEffect, useMemo, useState } from "react";

function frac(x: number): number {
  return x - Math.floor(x);
}

function rng(i: number, n: number): number {
  return frac(Math.sin(i * 127.1 + n * 311.7) * 43758.5453);
}

function buildStars(count: number) {
  return Array.from({ length: count }).map((_, i) => ({
    left: Math.round(rng(i, 1) * 10000) / 100,
    top: Math.round(rng(i, 2) * 10000) / 100,
    size: Math.round((0.6 + rng(i, 3) * 1.8) * 100) / 100,
    delay: Math.round(rng(i, 4) * 600) / 100,
    dur: Math.round((2.5 + rng(i, 5) * 5) * 100) / 100,
    op: Math.round((0.25 + rng(i, 6) * 0.6) * 1000) / 1000,
    cyan: rng(i, 7) > 0.82,
  }));
}

// A sparse "neural cosmic" web: deterministic nodes linked to nearby nodes.
function buildNeural() {
  const nodes = Array.from({ length: 16 }).map((_, i) => ({
    x: Math.round(rng(i, 11) * 1000) / 10,
    y: Math.round(rng(i, 12) * 1000) / 10,
  }));
  const edges: { a: number; b: number; dur: number; delay: number }[] = [];
  nodes.forEach((n, i) => {
    let best = -1;
    let bestD = Infinity;
    nodes.forEach((m, j) => {
      if (i === j) return;
      const d = (n.x - m.x) ** 2 + (n.y - m.y) ** 2;
      if (d < bestD) {
        bestD = d;
        best = j;
      }
    });
    if (best > i) edges.push({ a: i, b: best, dur: 5 + rng(i, 13) * 6, delay: rng(i, 14) * 4 });
  });
  return { nodes, edges };
}

export function HudBackground({ still = false }: { still?: boolean }) {
  const [mounted, setMounted] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);
  const stars = useMemo(() => buildStars(70), []);
  const neural = useMemo(() => buildNeural(), []);

  useEffect(() => {
    setMounted(true);
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduceMotion(mq.matches);
    const fn = () => setReduceMotion(mq.matches);
    mq.addEventListener("change", fn);
    return () => mq.removeEventListener("change", fn);
  }, []);

  const animate = mounted && !still && !reduceMotion;

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* deep space base */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at 50% 32%, hsl(248 52% 9%), hsl(238 58% 5%) 55%, hsl(235 62% 2%))",
        }}
      />

      {/* breathing nebula gas clouds */}
      <div
        className="nebula-blob"
        style={{
          left: "8%",
          top: "12%",
          width: "46vw",
          height: "46vw",
          background: "radial-gradient(circle, hsl(var(--cosmos-violet) / 0.5), transparent 70%)",
          animationPlayState: animate ? "running" : "paused",
        }}
      />
      <div
        className="nebula-blob"
        style={{
          right: "4%",
          top: "30%",
          width: "40vw",
          height: "40vw",
          background: "radial-gradient(circle, hsl(var(--cosmos-cyan) / 0.32), transparent 70%)",
          animationDelay: "5s",
          animationPlayState: animate ? "running" : "paused",
        }}
      />
      <div
        className="nebula-blob"
        style={{
          left: "32%",
          bottom: "2%",
          width: "44vw",
          height: "44vw",
          background: "radial-gradient(circle, hsl(var(--cosmos-magenta) / 0.26), transparent 72%)",
          animationDelay: "9s",
          animationPlayState: animate ? "running" : "paused",
        }}
      />

      {/* neural cosmic web */}
      <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none" aria-hidden="true">
        {neural.edges.map((e, i) => {
          const a = neural.nodes[e.a];
          const b = neural.nodes[e.b];
          return (
            <line
              key={i}
              x1={`${a.x}%`}
              y1={`${a.y}%`}
              x2={`${b.x}%`}
              y2={`${b.y}%`}
              stroke="hsl(var(--cosmos-cyan))"
              strokeWidth="0.6"
              style={{
                opacity: 0.12,
                animation: animate ? `neuralPulse ${e.dur}s ease-in-out ${e.delay}s infinite` : undefined,
              }}
            />
          );
        })}
        {neural.nodes.map((n, i) => (
          <circle
            key={i}
            cx={`${n.x}%`}
            cy={`${n.y}%`}
            r={1.4}
            fill="hsl(var(--cosmos-cyan))"
            style={{
              opacity: 0.4,
              animation: animate ? `neuralPulse ${4 + (i % 5)}s ease-in-out ${i * 0.3}s infinite` : undefined,
            }}
          />
        ))}
      </svg>

      {/* parallax starfield */}
      <div
        className="absolute inset-0"
        style={{ animation: animate ? "starDrift 60s linear infinite alternate" : undefined }}
      >
        {mounted &&
          stars.map((s, i) => (
            <span
              key={i}
              className="star"
              style={{
                left: `${s.left}%`,
                top: `${s.top}%`,
                width: s.size,
                height: s.size,
                opacity: s.op,
                background: s.cyan ? "hsl(var(--cosmos-cyan))" : "hsl(var(--cosmos-star))",
                boxShadow: s.size > 1.4 ? "0 0 4px hsl(var(--cosmos-star) / 0.7)" : undefined,
                animation: animate ? `starTwinkle ${s.dur}s ease-in-out ${s.delay}s infinite` : undefined,
              }}
            />
          ))}
      </div>

      <div className="vignette absolute inset-0" />
    </div>
  );
}
