"use client";

export function SutraWordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 font-hud text-lg ${className}`}>
      <span className="neon">RUD</span>
      <span className="relative mx-0.5 inline-flex h-[1.1em] w-[1.1em] items-center justify-center" aria-hidden="true">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/trishula-icon.png"
          alt=""
          className="h-full w-full object-contain rudra-breath"
          style={{
            mixBlendMode: "screen",
            filter: "drop-shadow(0 0 6px hsl(var(--cosmos-violet) / 0.8))",
          }}
        />
      </span>
      <span className="neon">A</span>
    </span>
  );
}
