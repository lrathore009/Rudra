"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Mic, Square, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

export function RudraCommandBar({
  input,
  onInputChange,
  onSubmit,
  onStop,
  onVoice,
  listening,
  processing,
  placeholder,
  streamingActive,
  selectedGrahaName,
}: {
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  processing: boolean;
  placeholder: string;
  streamingActive?: boolean;
  selectedGrahaName?: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "/" && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <motion.form
      className="pointer-events-auto cosmic-command-panel prime-command-bar mb-3 flex w-full max-w-5xl items-center gap-3 px-5 py-3.5"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
      whileFocus={{ boxShadow: "0 0 40px hsl(var(--cosmos-violet) / 0.18)" }}
    >
      {selectedGrahaName && (
        <motion.span
          className="hidden shrink-0 rounded border border-primary/30 bg-primary/10 px-2 py-0.5 font-terminal text-[8px] uppercase tracking-widest text-primary/80 sm:inline"
          layoutId="graha-channel-pill"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          {selectedGrahaName}
        </motion.span>
      )}
      <input
        ref={inputRef}
        value={input}
        onChange={(e) => onInputChange(e.target.value)}
        disabled={processing && !streamingActive}
        placeholder={placeholder}
        className="cosmic-command-input min-w-0 flex-1 bg-transparent font-display text-sm uppercase tracking-wide outline-none sm:text-base"
        autoComplete="off"
        aria-label="Command input"
      />
      <motion.button
        type="button"
        onClick={onVoice}
        className={cn("cosmic-icon-btn", listening && "cosmic-icon-btn-active")}
        title="Voice uplink"
        whileTap={{ scale: 0.9 }}
        animate={listening ? { scale: [1, 1.08, 1] } : { scale: 1 }}
        transition={listening ? { repeat: Infinity, duration: 1.2 } : undefined}
      >
        <Mic className="h-4 w-4" />
      </motion.button>
      {processing ? (
        <motion.button
          type="button"
          onClick={onStop}
          className="cosmic-icon-btn cosmic-icon-btn-stop"
          title="Stop"
          whileTap={{ scale: 0.9 }}
        >
          <Square className="h-3.5 w-3.5 fill-current" />
        </motion.button>
      ) : (
        <motion.button
          type="submit"
          disabled={!input.trim()}
          className="cosmic-icon-btn cosmic-icon-btn-send"
          title="Transmit"
          whileTap={{ scale: 0.9 }}
          whileHover={{ scale: input.trim() ? 1.06 : 1 }}
        >
          <Upload className="h-4 w-4" />
        </motion.button>
      )}
    </motion.form>
  );
}
