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

/** Rudra Prime — Trishula × Jarvis hybrid wordmark */
export function RudraPrimeWordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex flex-col gap-0.5 ${className}`}>
      <span className="inline-flex items-center gap-0.5 font-hud text-base leading-none sm:text-lg">
        <span className="neon-prime">RUD</span>
        <span
          className="relative mx-0.5 inline-flex h-[1.15em] w-[0.55em] items-end justify-center"
          aria-hidden="true"
        >
          <svg viewBox="0 0 24 48" className="h-full w-full rudra-breath" fill="none">
            <path
              d="M12 2 L12 18 M12 18 L4 42 M12 18 L20 42 M12 14 L8 8 M12 14 L16 8"
              stroke="hsl(var(--prime-gold))"
              strokeWidth="2.2"
              strokeLinecap="round"
              style={{ filter: "drop-shadow(0 0 6px hsl(var(--prime-cyan) / 0.85))" }}
            />
            <circle cx="12" cy="16" r="2.5" fill="hsl(var(--prime-cyan) / 0.95)" />
          </svg>
        </span>
        <span className="neon-prime">A</span>
        <span className="ml-1.5 font-terminal text-[9px] tracking-[0.35em] text-primary/80 sm:text-[10px]">
          PRIME
        </span>
      </span>
    </span>
  );
}

export function RudraPrimeTagline({ className = "" }: { className?: string }) {
  return (
    <span className={`font-terminal text-[7px] uppercase tracking-[0.22em] text-muted-foreground/70 sm:text-[8px] ${className}`}>
      The void holds your counsel · at your service, sir
    </span>
  );
}
