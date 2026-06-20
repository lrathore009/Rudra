"use client";

export function MalaBeadIcon({ pulse = false, className = "h-3 w-3" }: { pulse?: boolean; className?: string }) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={`${className} ${pulse ? "bead-pulse-once" : ""}`}
      aria-hidden="true"
    >
      <circle cx="8" cy="8" r="5.5" fill="hsl(var(--cosmos-deep))" stroke="hsl(var(--cosmos-cyan) / 0.55)" strokeWidth="0.6" />
      <circle cx="8" cy="8" r="2.2" fill="hsl(var(--cosmos-cyan) / 0.85)" />
      <circle cx="8" cy="8" r="5.5" fill="none" stroke="hsl(var(--cosmos-violet) / 0.25)" strokeWidth="0.4" strokeDasharray="2 3" />
    </svg>
  );
}
