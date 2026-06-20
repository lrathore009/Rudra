"use client";

import { motion } from "framer-motion";
import { REALMS, type RealmId } from "@/components/tablet/RealmRim";
import { cn } from "@/lib/utils";

export function RudraRealmNav({
  activeRealm,
  onRealmChange,
}: {
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
}) {
  return (
    <motion.nav
      className="pointer-events-auto flex flex-wrap items-end justify-center gap-2 px-4 pb-3 sm:gap-2.5"
      aria-label="Realms"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
    >
      {REALMS.map((r, i) => {
        const Icon = r.icon;
        const active = activeRealm === r.id;
        return (
          <motion.button
            key={r.id}
            type="button"
            title={r.label}
            onClick={() => onRealmChange(active ? null : r.id)}
            className={cn("cosmic-realm-tile", active && "cosmic-realm-tile-active")}
            aria-pressed={active}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + i * 0.04 }}
            whileHover={{ y: -3, transition: { duration: 0.15 } }}
            whileTap={{ scale: 0.96 }}
          >
            <Icon className="h-4 w-4" />
            <span>{r.cosmicLabel}</span>
          </motion.button>
        );
      })}
    </motion.nav>
  );
}
