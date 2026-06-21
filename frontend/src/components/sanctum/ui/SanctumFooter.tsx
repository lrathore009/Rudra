"use client";

import { Lock } from "lucide-react";

export function SanctumFooter({
  uplinkActive = true,
  memorySynced = true,
}: {
  uplinkActive?: boolean;
  memorySynced?: boolean;
}) {
  return (
    <footer className="prime-footer pointer-events-none relative z-20 grid grid-cols-[1fr_auto_1fr] items-center gap-2 px-4 pb-2.5 sm:px-6">
      <span className="flex items-center gap-1 truncate">
        <Lock className="h-2.5 w-2.5 shrink-0 opacity-60" aria-hidden />
        Encrypted uplink · {uplinkActive ? "Active" : "Offline"}
        {memorySynced && " · Navagraha synced"}
      </span>
      <span className="prime-om" aria-hidden>
        ॐ
      </span>
      <span className="ml-auto shrink-0 text-right">Rudra Prime v1.0 · Local · Sealed · Yours</span>
    </footer>
  );
}
