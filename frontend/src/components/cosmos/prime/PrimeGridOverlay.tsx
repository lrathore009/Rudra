"use client";

/** Subtle hex grid — no orbital rings or center reticle */
export function PrimeGridOverlay() {
  return (
    <div className="prime-grid-overlay" aria-hidden>
      <div className="prime-bg-hex" />
    </div>
  );
}
