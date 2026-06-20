"use client";

import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function SovereignTablet({
  header,
  footer,
  children,
  className,
}: {
  header: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className="sovereign-stage">
      <div className="sovereign-vignette" aria-hidden="true" />
      <div className={cn("sovereign-tablet yantra-surface", className)}>
        <div className="sovereign-bezel" aria-hidden="true" />
        <header className="sovereign-tablet-header">{header}</header>
        <div className="sovereign-tablet-body">{children}</div>
        {footer && <footer className="sovereign-tablet-footer">{footer}</footer>}
      </div>
    </div>
  );
}
