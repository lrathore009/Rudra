"use client";

import dynamic from "next/dynamic";
import { PrimeBackground } from "./prime/PrimeBackground";

const CosmicScene = dynamic(
  () => import("./CosmicScene").then((m) => m.CosmicScene),
  { ssr: false }
);

/** Login — Prime nebula + 3D sanctum (orbit controls only) */
export function LoginCosmos() {
  return (
    <div className="absolute inset-0">
      <PrimeBackground />
      <CosmicScene variant="login" processing={false} />
    </div>
  );
}
