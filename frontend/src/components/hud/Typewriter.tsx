"use client";

import { useEffect, useState } from "react";

// Reveals text progressively within ~durationMs regardless of length, with a blinking caret.
export function Typewriter({ text, durationMs = 1200 }: { text: string; durationMs?: number }) {
  const [n, setN] = useState(0);

  useEffect(() => {
    setN(0);
    const total = text.length;
    if (total === 0) return;
    const ticks = Math.min(120, Math.max(20, Math.round(durationMs / 16)));
    const step = Math.max(1, Math.ceil(total / ticks));
    const id = setInterval(() => {
      setN((p) => {
        const next = p + step;
        if (next >= total) {
          clearInterval(id);
          return total;
        }
        return next;
      });
    }, 16);
    return () => clearInterval(id);
  }, [text, durationMs]);

  return (
    <>
      {text.slice(0, n)}
      {n < text.length && <span className="caret neon">▋</span>}
    </>
  );
}
