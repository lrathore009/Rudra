"use client";

/** Observatory login — flat void, no 3D */
export function LoginCosmos() {
  return (
    <div
      className="pointer-events-none fixed inset-0"
      aria-hidden
      style={{
        background: "var(--obs-bg)",
        backgroundImage:
          "linear-gradient(rgba(0,188,212,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(0,188,212,0.02) 1px, transparent 1px)",
        backgroundSize: "24px 24px",
      }}
    />
  );
}
