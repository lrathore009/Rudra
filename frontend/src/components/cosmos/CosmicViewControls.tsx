"use client";

import { useEffect, useState, type RefObject } from "react";
import { Home, Minus, Plus, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import type { CosmicNavHandle } from "./cosmic-nav-types";

export function CosmicViewControls({
  navRef,
  className,
}: {
  navRef: RefObject<CosmicNavHandle | null>;
  className?: string;
}) {
  const [hintVisible, setHintVisible] = useState(true);

  useEffect(() => {
    const timer = window.setTimeout(() => setHintVisible(false), 10000);
    return () => window.clearTimeout(timer);
  }, []);

  const act = (fn: keyof CosmicNavHandle) => () => navRef.current?.[fn]();

  return (
    <>
      <div
        className={cn(
          "cosmic-nav-toolbar pointer-events-auto absolute right-3 top-1/2 z-30 flex -translate-y-1/2 flex-col gap-1.5 sm:right-4",
          className
        )}
        role="toolbar"
        aria-label="Sanctum camera controls"
      >
        <button type="button" className="cosmic-nav-btn" onClick={act("zoomIn")} title="Zoom in">
          <Plus className="h-4 w-4" aria-hidden />
          <span className="sr-only">Zoom in</span>
        </button>
        <button type="button" className="cosmic-nav-btn" onClick={act("zoomOut")} title="Zoom out">
          <Minus className="h-4 w-4" aria-hidden />
          <span className="sr-only">Zoom out</span>
        </button>
        <button type="button" className="cosmic-nav-btn" onClick={act("resetView")} title="Reset view">
          <RotateCcw className="h-4 w-4" aria-hidden />
          <span className="sr-only">Reset view</span>
        </button>
        <button type="button" className="cosmic-nav-btn cosmic-nav-btn-home" onClick={act("resetView")} title="Home position">
          <Home className="h-3.5 w-3.5" aria-hidden />
          <span className="sr-only">Home</span>
        </button>
      </div>

      {hintVisible && (
        <div className="cosmic-nav-hint pointer-events-none absolute bottom-36 left-1/2 z-20 max-w-md -translate-x-1/2 px-4 text-center sm:bottom-32">
          <p className="font-terminal text-[9px] uppercase tracking-[0.14em] text-muted-foreground/70 sm:text-[10px]">
            Drag to orbit · Scroll or pinch to zoom · Right-drag / two-finger drag to pan
          </p>
          <button
            type="button"
            className="cosmic-nav-hint-dismiss pointer-events-auto mt-1.5 font-terminal text-[8px] uppercase tracking-widest text-primary/60 underline-offset-2 hover:text-primary/90 hover:underline"
            onClick={() => setHintVisible(false)}
          >
            Got it
          </button>
        </div>
      )}
    </>
  );
}
