"use client";

export function BootSequence() {
  return (
    <div
      className="boot-fade-short fixed inset-0 z-50 flex flex-col items-center justify-center"
      style={{ background: "hsl(var(--cosmos-void))" }}
    >
      <div className="rudra-breath h-28 w-28">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/trident-core.png"
          alt=""
          className="h-full w-full object-contain trident-idle"
          style={{
            mixBlendMode: "screen",
            filter: "drop-shadow(0 0 20px hsl(var(--cosmos-cyan) / 0.7))",
          }}
        />
      </div>
      <div className="mt-5 font-hud text-xl neon">RUDRA</div>
      <p className="mt-2 font-terminal text-[10px] text-muted-foreground">trishula · awakening</p>
    </div>
  );
}
