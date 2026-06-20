"use client";

import dynamic from "next/dynamic";
import { GrahaScreenLabels } from "./GrahaScreenLabels";

const CosmicScene = dynamic(
  () => import("./CosmicScene").then((m) => m.CosmicScene),
  { ssr: false }
);

/** Full Navagraha sanctum for login — same cosmos as main, dimmed labels */
export function LoginCosmos() {
  return (
    <div className="absolute inset-0 bg-[#030308]">
      <CosmicScene variant="login" processing={false} />
      <GrahaScreenLabels dimmed processing={false} />
    </div>
  );
}
