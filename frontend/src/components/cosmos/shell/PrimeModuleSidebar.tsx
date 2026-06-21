"use client";

import { motion } from "framer-motion";
import { Brain, Clock, Mic, Search, BookOpen, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

const MODULES: { id: string; label: string; icon: LucideIcon }[] = [
  { id: "time", label: "Time", icon: Clock },
  { id: "wikipedia", label: "Wikipedia", icon: BookOpen },
  { id: "voice", label: "Voice", icon: Mic },
  { id: "memory", label: "Memory", icon: Brain },
  { id: "research", label: "Research", icon: Search },
];

export function PrimeModuleSidebar({
  activeId,
  listening,
  onModule,
}: {
  activeId?: string;
  listening?: boolean;
  onModule: (id: string) => void;
}) {
  return (
    <motion.aside
      className="prime-module-sidebar pointer-events-auto absolute left-3 top-[4.5rem] z-20 flex flex-col gap-1.5 sm:left-5"
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.45, delay: 0.1 }}
      aria-label="Jarvis modules"
    >
      {MODULES.map((m, i) => {
        const Icon = m.icon;
        const active = activeId === m.id || (m.id === "voice" && listening);
        return (
          <motion.button
            key={m.id}
            type="button"
            onClick={() => onModule(m.id)}
            className={cn("prime-module-tile", active && "prime-module-tile-active")}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.12 + i * 0.04 }}
            whileHover={{ x: 3 }}
            whileTap={{ scale: 0.97 }}
          >
            <Icon className="h-3.5 w-3.5 shrink-0" />
            <span>{m.label.toUpperCase()}</span>
          </motion.button>
        );
      })}
    </motion.aside>
  );
}
