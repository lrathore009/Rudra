"use client";

import { PrimeBackground } from "./prime/PrimeBackground";

/** Login — Prime nebula background only (no 3D sanctum) */
export function LoginCosmos() {
  return (
    <div className="absolute inset-0">
      <PrimeBackground />
    </div>
  );
}
