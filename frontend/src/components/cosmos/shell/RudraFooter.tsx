"use client";

import { motion } from "framer-motion";
import { FOOTER_TICKER_SEGMENTS } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";

function StatusPulse({ active }: { active: boolean }) {
  return <span className={cn("cosmic-status-dot", active && "cosmic-status-dot-live")} aria-hidden />;
}

export function RudraFooter({
  tickerIdx,
  uplinkActive = true,
  memorySynced = true,
}: {
  tickerIdx: number;
  uplinkActive?: boolean;
  memorySynced?: boolean;
}) {
  const footerSegment = FOOTER_TICKER_SEGMENTS[tickerIdx % FOOTER_TICKER_SEGMENTS.length];

  return (
    <motion.footer
      className="pointer-events-none flex flex-wrap items-center justify-between gap-x-3 gap-y-1 px-4 pb-3 font-terminal text-[7px] uppercase tracking-[0.14em] text-muted-foreground/55 sm:px-8 sm:text-[8px]"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.4, duration: 0.45 }}
    >
      <span className="cosmic-footer-status truncate">
        <StatusPulse active={uplinkActive} />
        Encrypted uplink · {uplinkActive ? "Active" : "Offline"}
        <StatusPulse active={memorySynced} />
        · {footerSegment}
      </span>
      <span className="ml-auto shrink-0">Trishula OS v1.9 · Rudra Core Online</span>
    </motion.footer>
  );
}
