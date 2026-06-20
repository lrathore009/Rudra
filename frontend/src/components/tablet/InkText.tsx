"use client";

import { Typewriter } from "@/components/hud/Typewriter";

/** Rudra answer text — ink settling instead of terminal caret */
export function InkText({
  text,
  streaming,
  streamed,
}: {
  text: string;
  streaming?: boolean;
  streamed?: boolean;
}) {
  if (streamed) {
    return (
      <span className="ink-text font-display text-[15px] leading-[1.65] text-amber-50/92">
        {text}
        {streaming && <span className="ink-cursor" aria-hidden="true" />}
      </span>
    );
  }
  return (
    <span className="ink-text font-display text-[15px] leading-[1.65] text-amber-50/92">
      <Typewriter text={text} />
    </span>
  );
}
