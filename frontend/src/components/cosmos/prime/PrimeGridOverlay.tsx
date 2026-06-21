"use client";

/** Hex grid + orbital SVG lines over the 3D scene (matches preview overlay) */
export function PrimeGridOverlay() {
  return (
    <div className="prime-grid-overlay" aria-hidden>
      <div className="prime-bg-hex" />
      <svg className="prime-bg-orbits" viewBox="0 0 1000 800" preserveAspectRatio="xMidYMid slice">
        <ellipse cx="500" cy="380" rx="320" ry="120" className="prime-orbit-ring prime-orbit-1" />
        <ellipse cx="500" cy="380" rx="260" ry="95" className="prime-orbit-ring prime-orbit-2" />
        <ellipse cx="500" cy="380" rx="200" ry="72" className="prime-orbit-ring prime-orbit-3" />
        <ellipse cx="500" cy="380" rx="145" ry="52" className="prime-orbit-ring prime-orbit-4" />
        <ellipse cx="500" cy="380" rx="380" ry="145" className="prime-orbit-ring prime-orbit-5" transform="rotate(-18 500 380)" />
        <ellipse cx="500" cy="380" rx="340" ry="130" className="prime-orbit-ring prime-orbit-6" transform="rotate(22 500 380)" />
        <line x1="500" y1="200" x2="500" y2="560" className="prime-orbit-cross" />
        <line x1="340" y1="380" x2="660" y2="380" className="prime-orbit-cross" />
        <circle cx="500" cy="380" r="4" className="prime-orbit-core" />
      </svg>
    </div>
  );
}
