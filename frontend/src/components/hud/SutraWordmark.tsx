"use client";

export function SutraWordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-0.5 font-hud text-lg ${className}`}>
      <span className="neon">RUD</span>
      <span className="relative mx-0.5 inline-flex h-[1.1em] w-[1.1em] items-center justify-center" aria-hidden="true">
        <svg viewBox="0 0 16 16" className="h-full w-full rudra-breath">
          <ellipse cx="8" cy="8.5" rx="5" ry="5.5" fill="hsl(22 38% 18%)" stroke="hsl(var(--rudra-gold))" strokeWidth="0.7" />
          <ellipse cx="8" cy="8" rx="1.8" ry="2" fill="hsl(var(--rudra-gold-bright))" />
        </svg>
      </span>
      <span className="neon">A</span>
    </span>
  );
}
