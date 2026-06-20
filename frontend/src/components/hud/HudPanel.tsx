"use client";

import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { MalaBeadIcon } from "./MalaBeadIcon";

export function HudPanel({
  title,
  children,
  className,
  right,
  accent = "gold",
  float = true,
  floatDelay = 0,
  dataPulse,
}: {
  title?: string;
  children: ReactNode;
  className?: string;
  right?: ReactNode;
  accent?: "gold" | "saffron";
  float?: boolean;
  floatDelay?: number;
  /** Change to re-trigger header bead pulse */
  dataPulse?: string | number;
}) {
  return (
    <section
      className={cn("glass brackets bark-texture flex min-h-0 flex-col", float && "float-y", className)}
      style={float ? { animationDelay: `${floatDelay}s` } : undefined}
    >
      {title && (
        <header className="hud-underline flex shrink-0 items-center justify-between border-b border-amber-500/15 px-3 py-2">
          <div className="flex items-center gap-2">
            <MalaBeadIcon key={dataPulse} pulse className="h-3.5 w-3.5" />
            <h2
              className={cn(
                "font-hud text-[10px]",
                accent === "saffron" ? "neon-amber" : "neon-dim"
              )}
            >
              {title}
            </h2>
          </div>
          {right}
        </header>
      )}
      <div className="min-h-0 flex-1 overflow-y-auto p-3">{children}</div>
    </section>
  );
}
