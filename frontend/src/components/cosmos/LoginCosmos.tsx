"use client";

import { useRef } from "react";
import dynamic from "next/dynamic";
import { CosmicViewControls } from "./CosmicViewControls";
import type { CosmicNavHandle } from "./cosmic-nav-types";

const CosmicScene = dynamic(
  () => import("./CosmicScene").then((m) => m.CosmicScene),
  { ssr: false }
);

/** Login — full inclined-orbit sanctum with free camera navigation */
export function LoginCosmos() {
  const navRef = useRef<CosmicNavHandle | null>(null);

  return (
    <div className="absolute inset-0 bg-[#030308]">
      <CosmicScene variant="login" processing={false} navRef={navRef} />
      <CosmicViewControls navRef={navRef} className="top-[42%]" />
    </div>
  );
}
