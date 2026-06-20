"use client";

import { AnimatePresence, motion } from "framer-motion";
import { InkText } from "@/components/tablet/InkText";
import { grahaColor } from "@/lib/rudra-theme";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  streaming?: boolean;
}

export function RudraCounselPane({
  messages,
  streamingMsgId,
  processing,
  leadGrahaName,
  supportingGrahaNames,
  selectedGrahaName,
  showResponse,
}: {
  messages: Message[];
  streamingMsgId: string | null;
  processing: boolean;
  leadGrahaName?: string;
  supportingGrahaNames?: string[];
  selectedGrahaName?: string;
  showResponse: boolean;
}) {
  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant" && m.content);
  const latestUser = [...messages].reverse().find((m) => m.role === "user");
  const streaming = messages.find((m) => m.id === streamingMsgId);
  const visible = showResponse && (processing || streaming || latestAssistant);

  return (
    <AnimatePresence mode="wait">
      {visible && (latestAssistant || latestUser || streaming) && (
        <motion.div
          key={streaming?.id ?? latestAssistant?.id ?? "counsel"}
          className="cosmic-stream pointer-events-auto mb-3 w-full max-w-3xl text-center"
          initial={{ opacity: 0, y: 10, filter: "blur(4px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.35 }}
        >
          {latestUser && processing && (
            <p className="mb-2 font-terminal text-[10px] uppercase tracking-[0.2em] text-primary/70">
              ◇ {latestUser.content.slice(0, 120)}
              {latestUser.content.length > 120 ? "…" : ""}
            </p>
          )}

          {(streaming || latestAssistant) && (
            <div className="cosmic-response mx-auto max-w-2xl">
              {streaming ? (
                <InkText text={streaming.content} streaming streamed />
              ) : latestAssistant ? (
                <InkText text={latestAssistant.content} streamed />
              ) : null}
            </div>
          )}

          {processing && leadGrahaName && (
            <motion.div
              className="mt-2 flex flex-wrap items-center justify-center gap-2 font-terminal text-[9px] uppercase tracking-widest"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <span className="text-primary/80">Rudra commanding</span>
              <span
                className="cosmic-graha-chip cosmic-graha-chip-lead"
                style={{
                  color: grahaColor(leadGrahaName, 0.95),
                  borderColor: grahaColor(leadGrahaName, 0.5),
                }}
              >
                Lead · {leadGrahaName}
              </span>
              {supportingGrahaNames && supportingGrahaNames.length > 0 && (
                <span className="text-muted-foreground/70">
                  Support · {supportingGrahaNames.join(" · ")}
                </span>
              )}
            </motion.div>
          )}

          {!processing && selectedGrahaName && !visible && (
            <p className="font-terminal text-[9px] uppercase tracking-widest text-muted-foreground/60">
              Channel open · {selectedGrahaName}
            </p>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
