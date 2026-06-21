"use client";

/** Full-screen CSS background matched to rudra-prime-preview.png (nebula + stars, behind canvas) */
export function PrimeBackground() {
  return (
    <div className="prime-bg-root" aria-hidden>
      <div className="prime-bg-nebula" />
      <div className="prime-bg-stars" />
      <div className="prime-bg-vignette" />
    </div>
  );
}
