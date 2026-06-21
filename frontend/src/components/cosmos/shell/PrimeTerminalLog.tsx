"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

export function PrimeTerminalLog({
  lines,
  listening,
  processing,
  leadGrahaName,
}: {
  lines: string[];
  listening?: boolean;
  processing?: boolean;
  leadGrahaName?: string;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [lines, listening, processing, leadGrahaName]);

  const runtime: string[] = [];
  if (listening) runtime.push("> Recognizing voice…");
  if (processing && leadGrahaName) runtime.push(`> Navagraha routing · Lead ${leadGrahaName}`);
  else if (processing) runtime.push("> Third eye opening…");

  const visible = [...lines.slice(-8), ...runtime];

  return (
    <motion.div
      className="prime-terminal-log pointer-events-auto flex min-h-[4.5rem] flex-col"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div ref={scrollRef} className="prime-terminal-scroll flex-1 overflow-y-auto font-terminal text-[9px] leading-relaxed sm:text-[10px]">
        <AnimatePresence initial={false}>
          {visible.map((line, i) => (
            <motion.p
              key={`${line}-${i}`}
              className="prime-terminal-line truncate"
              initial={{ opacity: 0, x: -4 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
            >
              {line.startsWith(">") ? line : `> ${line}`}
            </motion.p>
          ))}
        </AnimatePresence>
        {!visible.length && <p className="prime-terminal-line opacity-50">&gt; Rudra Prime online — awaiting signal</p>}
      </div>
    </motion.div>
  );
}
