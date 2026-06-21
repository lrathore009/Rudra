"use client";

import { useMemo } from "react";
import { PRIME_DEFAULT_COUNSEL } from "./prime-graha-config";

function TrishulIcon() {
  return (
    <svg viewBox="0 0 16 24" className="h-3 w-2" fill="none" aria-hidden>
      <path
        d="M8 1 L8 9 M8 9 L3 21 M8 9 L13 21"
        stroke="#f0d070"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function PrimeDualPane({
  counselText,
  processing,
  leadGrahaName,
  logLines,
}: {
  counselText?: string;
  processing: boolean;
  leadGrahaName?: string;
  logLines: string[];
}) {
  const displayCounsel = counselText?.trim() || PRIME_DEFAULT_COUNSEL;

  const lines = useMemo(() => {
    const base = [...logLines];
    if (processing && leadGrahaName && !base.some((l) => l.includes("Lead"))) {
      base.push(`> Lead · ${leadGrahaName}`);
    }
    if (processing && !base.some((l) => l.includes("Transmission"))) {
      base.push("> Transmission ready");
    }
    return base.slice(-6);
  }, [logLines, processing, leadGrahaName]);

  return (
    <div className="prime-dual-pane pointer-events-auto">
      <div className="prime-counsel-box">
        <div className="prime-counsel-title">
          <TrishulIcon />
          Rudra&apos;s Counsel
        </div>
        <p className="prime-counsel-text">{displayCounsel}</p>
      </div>
      <div className="prime-log-box">
        <div className="prime-log-title">System Log</div>
        {lines.map((line, i) => (
          <div key={`${line}-${i}`} className="prime-log-line">
            {line.startsWith(">") ? line : `> ${line}`}
          </div>
        ))}
      </div>
    </div>
  );
}
