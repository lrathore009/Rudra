"use client";

// Viewport cosmic frame — cyan corner brackets framing the command deck.
export function HudFrame() {
  const corners = [
    "left-2 top-2 border-l-2 border-t-2",
    "right-2 top-2 border-r-2 border-t-2",
    "left-2 bottom-2 border-l-2 border-b-2",
    "right-2 bottom-2 border-r-2 border-b-2",
  ];
  return (
    <div className="pointer-events-none fixed inset-0 z-30">
      {corners.map((c, i) => (
        <span
          key={i}
          className={`absolute h-5 w-5 ${c}`}
          style={{ borderColor: "hsl(var(--cosmos-cyan) / 0.45)" }}
        />
      ))}
      <span
        className="absolute left-1/2 top-2 h-px w-28 -translate-x-1/2"
        style={{
          background:
            "linear-gradient(90deg, transparent, hsl(var(--cosmos-cyan) / 0.45), transparent)",
        }}
      />
      <span
        className="absolute bottom-2 left-1/2 h-px w-28 -translate-x-1/2"
        style={{
          background:
            "linear-gradient(90deg, transparent, hsl(var(--cosmos-cyan) / 0.45), transparent)",
        }}
      />
    </div>
  );
}
