"use client";

export function SutraWordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex flex-col gap-0.5 ${className}`}>
      <span className="inline-flex items-center gap-0.5 font-hud text-lg leading-none">
        <span className="neon">RUD</span>
        <span
          className="relative mx-0.5 inline-flex h-[1.15em] w-[0.55em] items-end justify-center"
          aria-hidden="true"
        >
          <svg viewBox="0 0 24 48" className="h-full w-full rudra-breath" fill="none">
            <path
              d="M12 2 L12 18 M12 18 L4 42 M12 18 L20 42 M12 14 L8 8 M12 14 L16 8"
              stroke="hsl(var(--cosmos-gold))"
              strokeWidth="2.2"
              strokeLinecap="round"
              style={{ filter: "drop-shadow(0 0 6px hsl(var(--cosmos-violet) / 0.8))" }}
            />
            <circle cx="12" cy="16" r="2.5" fill="hsl(var(--cosmos-cyan) / 0.9)" />
          </svg>
        </span>
        <span className="neon">A</span>
      </span>
    </span>
  );
}

export function RudraTagline({ className = "" }: { className?: string }) {
  return (
    <span className={`font-terminal text-[8px] uppercase tracking-[0.28em] text-muted-foreground/75 ${className}`}>
      The void holds your counsel
    </span>
  );
}
