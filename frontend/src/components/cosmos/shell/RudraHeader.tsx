"use client";

import { motion } from "framer-motion";
import { Volume2, VolumeX } from "lucide-react";
import { SutraWordmark, RudraTagline } from "@/components/hud/SutraWordmark";
import { themeModeLabel, type RudraThemeMode } from "@/lib/rudra-theme";
import { cn } from "@/lib/utils";

export function RudraHeader({
  themeMode,
  onThemeCycle,
  status,
  clock,
  onLogout,
  muted,
  onToggleMute,
  greeting,
  operator,
}: {
  themeMode: RudraThemeMode;
  onThemeCycle: () => void;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  greeting?: string;
  operator?: string | null;
}) {
  const nominal = status.toLowerCase().includes("nominal") || status.toLowerCase().includes("online");

  return (
    <motion.header
      className="rudra-shell-header pointer-events-auto grid grid-cols-[1fr_auto_1fr] items-start gap-2 px-4 py-3 sm:px-8"
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="flex min-w-0 flex-col gap-1">
        <SutraWordmark className="text-sm sm:text-base" />
        <RudraTagline className="hidden sm:block" />
        {operator && greeting && (
          <motion.span
            className="hidden font-terminal text-[7px] uppercase tracking-[0.2em] text-muted-foreground/50 lg:block"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {greeting}
          </motion.span>
        )}
      </div>

      <motion.div
        className="flex justify-center pt-0.5"
        whileHover={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 400, damping: 28 }}
      >
        <span className={cn("cosmic-status-badge", nominal && "cosmic-status-badge-nominal")}>
          <span className="cosmic-status-signal" aria-hidden>
            ((o))
          </span>
          {nominal ? "Present · Nominal" : status}
        </span>
      </motion.div>

      <div className="ml-auto flex items-center justify-end gap-2 font-terminal text-[10px] sm:gap-3">
        <motion.button
          type="button"
          onClick={onThemeCycle}
          className="cosmic-ctl hidden sm:inline"
          whileTap={{ scale: 0.96 }}
        >
          {themeModeLabel(themeMode)}
        </motion.button>
        <span className="text-muted-foreground tabular-nums">
          {clock ? clock.toLocaleTimeString("en-GB") : "--:--:--"}
        </span>
        <motion.button
          type="button"
          onClick={onLogout}
          className="cosmic-ctl hidden sm:inline"
          whileTap={{ scale: 0.96 }}
        >
          Exit
        </motion.button>
        <motion.button
          type="button"
          onClick={onToggleMute}
          className="cosmic-ctl-icon"
          title={muted ? "Unmute" : "Mute"}
          whileTap={{ scale: 0.92 }}
        >
          {muted ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
        </motion.button>
      </div>
    </motion.header>
  );
}
