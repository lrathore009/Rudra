"use client";

import { Volume2 } from "lucide-react";
import { InkText } from "./InkText";
import { cn } from "@/lib/utils";

export interface DecreeMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agentType?: string;
  streamed?: boolean;
  streaming?: boolean;
}

export function DecreeScroll({
  messages,
  processing,
  feedRef,
  streamingMsgId,
  streamingMsgRef,
  onReplayVoice,
}: {
  messages: DecreeMessage[];
  processing: boolean;
  feedRef: React.RefObject<HTMLDivElement | null>;
  streamingMsgId: string | null;
  streamingMsgRef: React.MutableRefObject<HTMLDivElement | null>;
  onReplayVoice?: (content: string, agentType: string) => void;
}) {
  return (
    <section className="decree-scroll bark-texture min-h-0 flex-1">
      <header className="decree-scroll-header">
        <span className="font-hud text-[10px] tracking-[0.14em] text-muted-foreground">Signal & response</span>
      </header>
      <div ref={feedRef} className="decree-scroll-body">
        {messages.map((m) => (
          <div
            key={m.id}
            ref={
              m.id === streamingMsgId
                ? (el) => {
                    streamingMsgRef.current = el;
                  }
                : undefined
            }
            className={cn("decree-entry rise-in", m.role === "assistant" && "decree-answer")}
          >
            {m.role === "user" && (
              <div className="decree-user">
                <span className="decree-user-label">Your command</span>
                <p className="font-display text-[14px] leading-relaxed text-foreground">{m.content}</p>
              </div>
            )}
            {m.role === "assistant" && (
              <div className={cn("decree-rudra group relative", m.content.length > 80 && "palm-scroll ink-unfold")}>
                {m.agentType && m.content && onReplayVoice && (
                  <button
                    type="button"
                    title="Replay voice"
                    onClick={() => onReplayVoice(m.content, m.agentType!)}
                    className="absolute right-2 top-2 rounded border border-primary/15 p-1 opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
                  >
                    <Volume2 className="h-3 w-3" />
                  </button>
                )}
                <InkText text={m.content} streaming={m.streaming} streamed={m.streamed} />
              </div>
            )}
            {m.role === "system" && (
              <p className="font-terminal text-[11px] text-muted-foreground">{m.content}</p>
            )}
          </div>
        ))}
        {processing && messages.every((m) => !m.streaming) && (
          <p className="font-terminal text-[11px] text-muted-foreground/80">◇ Rudra processing…</p>
        )}
      </div>
    </section>
  );
}
