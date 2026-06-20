"use client";

export function BootSequence() {
  return (
    <div
      className="boot-fade-short fixed inset-0 z-50 flex flex-col items-center justify-center"
      style={{ background: "hsl(24 28% 3%)" }}
    >
      <div className="rudra-breath h-28 w-28">
        <svg viewBox="0 0 100 100" className="h-full w-full">
          <ellipse cx="50" cy="52" rx="34" ry="38" fill="hsl(22 38% 18%)" stroke="hsl(var(--rudra-gold) / 0.5)" strokeWidth="1" />
          {[0, 72, 144, 216, 288].map((deg) => (
            <line
              key={deg}
              x1="50"
              y1="14"
              x2="50"
              y2="86"
              stroke="hsl(18 35% 8% / 0.7)"
              strokeWidth="1.5"
              transform={`rotate(${deg} 50 50)`}
            />
          ))}
          <ellipse
            cx="50"
            cy="50"
            rx="12"
            ry="14"
            fill="hsl(var(--rudra-gold-bright))"
            className="inner-light"
            style={{ filter: "drop-shadow(0 0 8px hsl(var(--rudra-saffron)))" }}
          />
        </svg>
      </div>
      <div className="mt-5 font-hud text-xl neon">RUDRA</div>
      <p className="mt-2 font-terminal text-[10px] text-amber-200/55">one breath · awakening</p>
    </div>
  );
}
