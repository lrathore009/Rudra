"use client";

export function MalaBeadIcon({ pulse = false, className = "h-3 w-3" }: { pulse?: boolean; className?: string }) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={`${className} ${pulse ? "bead-pulse-once" : ""}`}
      aria-hidden="true"
    >
      <ellipse cx="8" cy="8.5" rx="5.5" ry="6" fill="hsl(22 38% 18%)" stroke="hsl(var(--rudra-gold) / 0.5)" strokeWidth="0.6" />
      {[0, 72, 144, 216, 288].map((deg) => (
        <line
          key={deg}
          x1="8"
          y1="2.5"
          x2="8"
          y2="14.5"
          stroke="hsl(18 35% 8% / 0.65)"
          strokeWidth="0.5"
          transform={`rotate(${deg} 8 8.5)`}
        />
      ))}
      <ellipse cx="8" cy="8" rx="2" ry="2.2" fill="hsl(var(--rudra-gold-bright) / 0.85)" />
    </svg>
  );
}
