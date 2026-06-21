"use client";

import { AnimatePresence, motion } from "framer-motion";
import { InkText } from "@/components/tablet/InkText";
import { PrimeTerminalLog } from "./PrimeTerminalLog";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  streaming?: boolean;
}

export function RudraPrimeCounselSplit({
  messages,
  streamingMsgId,
  processing,
  leadGrahaName,
  logLines,
  listening,
  showResponse,
}: {
  messages: Message[];
  streamingMsgId: string | null;
  processing: boolean;
  leadGrahaName?: string;
  logLines: string[];
  listening?: boolean;
  showResponse?: boolean;
}) {
  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant" && m.content);
  const streaming = messages.find((m) => m.id === streamingMsgId);
  const visible = showResponse && (processing || streaming || latestAssistant);

  if (!visible && !logLines.length && !listening && !processing) return null;

  return (
    <motion.div
      className="prime-split-panel pointer-events-auto mb-3 grid w-full max-w-5xl grid-cols-1 gap-2 sm:grid-cols-2 sm:gap-3"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="prime-counsel-pane">
        <p className="prime-pane-label font-terminal text-[8px] uppercase tracking-widest">Counsel</p>
        <AnimatePresence mode="wait">
          {visible && (streaming || latestAssistant) ? (
            <motion.div key={streaming?.id ?? "counsel"} className="cosmic-response mt-1 text-left" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              {streaming ? (
                <InkText text={streaming.content} streaming streamed />
              ) : latestAssistant ? (
                <InkText text={latestAssistant.content} streamed />
              ) : null}
            </motion.div>
          ) : (
            <p className="mt-1 font-terminal text-[9px] uppercase tracking-wide text-muted-foreground/45">
              Signal & response channel ready
            </p>
          )}
        </AnimatePresence>
      </div>
      <div className="prime-terminal-pane">
        <p className="prime-pane-label font-terminal text-[8px] uppercase tracking-widest">Engine log</p>
        <PrimeTerminalLog lines={logLines} listening={listening} processing={processing} leadGrahaName={leadGrahaName} />
      </div>
    </motion.div>
  );
}
