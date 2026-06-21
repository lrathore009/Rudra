"use client";

import { useMemo } from "react";
import { SANCTUM_DEFAULT_COUNSEL } from "@/data/navagraha-catalog";

export function CounselLogPane({
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
  const displayCounsel = counselText?.trim() || SANCTUM_DEFAULT_COUNSEL;
  const counselLine = displayCounsel.split(/\n/)[0]?.slice(0, 120) ?? displayCounsel.slice(0, 120);

  const lines = useMemo(() => {
    const base = [...logLines];
    if (processing && leadGrahaName) base.push(`lead · ${leadGrahaName}`);
    return base.slice(-3);
  }, [logLines, processing, leadGrahaName]);

  return (
    <div className="mandala-strip pointer-events-auto">
      <p className="mandala-counsel-line">
        <span className="mandala-counsel-label">counsel</span>
        {counselLine}
        {displayCounsel.length > counselLine.length ? "…" : ""}
      </p>
      <div className="mandala-log-line">
        {lines.map((line, i) => (
          <span key={`${line}-${i}`}>{line.startsWith(">") ? line : `› ${line}`}</span>
        ))}
      </div>
    </div>
  );
}
