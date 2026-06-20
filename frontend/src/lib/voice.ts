/** Browser speech recognition + per-agent text-to-speech. */

export interface VoiceProfile {
  pitch?: number;
  rate?: number;
  voice_hints?: string[];
}

export interface SpeechRecognitionHandle {
  stop: () => void;
}

type SpeechRecognitionCtor = new () => {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  onresult: ((ev: { resultIndex: number; results: SpeechRecognitionResultListLike }) => void) | null;
  onend: (() => void) | null;
  onerror: ((ev: { error?: string }) => void) | null;
  onstart: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
};

interface SpeechRecognitionResultListLike {
  length: number;
  [index: number]: {
    isFinal: boolean;
    0: { transcript: string };
  };
}

function getSpeechRecognition(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

/** Prime TTS voices — required on Safari/Chrome before first speak(). */
export function primeSpeechSynthesis(): void {
  if (typeof window === "undefined" || !window.speechSynthesis) return;
  window.speechSynthesis.getVoices();
  if (window.speechSynthesis.paused) window.speechSynthesis.resume();
}

export async function ensureMicrophoneAccess(): Promise<boolean> {
  if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
    return true;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((t) => t.stop());
    return true;
  } catch {
    return false;
  }
}

export function startSpeechRecognition(opts: {
  onInterim: (text: string) => void;
  onFinal: (text: string) => void;
  onError: (message: string) => void;
  onListeningChange: (listening: boolean) => void;
}): SpeechRecognitionHandle | null {
  const Ctor = getSpeechRecognition();
  if (!Ctor) {
    opts.onError("Voice not supported here — use Chrome or Edge, or type your command.");
    return null;
  }

  let retries = 0;
  let stopped = false;
  let rec: InstanceType<SpeechRecognitionCtor> | null = null;

  const startOnce = () => {
    if (stopped) return;
    rec = new Ctor();
    rec.lang = navigator.language || "en-US";
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;

    rec.onstart = () => opts.onListeningChange(true);

    rec.onresult = (ev) => {
      let interim = "";
      let finalText = "";
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        const chunk = ev.results[i][0]?.transcript ?? "";
        if (ev.results[i].isFinal) finalText += chunk;
        else interim += chunk;
      }
      if (interim) opts.onInterim(interim.trim());
      if (finalText.trim()) opts.onFinal(finalText.trim());
    };

    rec.onerror = (ev) => {
      const code = ev.error ?? "unknown";
      if (code === "network" && retries < 2) {
        retries++;
        setTimeout(startOnce, 400);
        return;
      }
      const messages: Record<string, string> = {
        "not-allowed": "Mic blocked — allow microphone for this site in browser settings.",
        "no-speech": "Didn't catch that — try again or type your command.",
        network:
          "Voice needs internet (Chrome sends audio to Google). Type your command, or check connection.",
        aborted: "Voice stopped.",
      };
      opts.onError(messages[code] ?? `Voice error: ${code}`);
      opts.onListeningChange(false);
    };

    rec.onend = () => {
      if (!stopped) opts.onListeningChange(false);
    };

    try {
      rec.start();
    } catch {
      opts.onError("Could not start mic — click again or type your command.");
      opts.onListeningChange(false);
    }
  };

  startOnce();

  return {
    stop: () => {
      stopped = true;
      try {
        rec?.stop();
      } catch {
        rec?.abort();
      }
    },
  };
}

let voiceCache: SpeechSynthesisVoice[] | null = null;

function loadVoices(): SpeechSynthesisVoice[] {
  if (typeof window === "undefined" || !window.speechSynthesis) return [];
  voiceCache = window.speechSynthesis.getVoices();
  return voiceCache;
}

if (typeof window !== "undefined" && window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => {
    voiceCache = window.speechSynthesis.getVoices();
  };
}

function pickVoice(hints: string[] = []): SpeechSynthesisVoice | null {
  const voices = loadVoices().filter((v) => v.lang.startsWith("en"));
  if (!voices.length) return null;
  for (const hint of hints) {
    const h = hint.toLowerCase();
    const match = voices.find(
      (v) => v.name.toLowerCase().includes(h) || v.lang.toLowerCase().includes(h)
    );
    if (match) return match;
  }
  return voices[0] ?? null;
}

export function stopSpeaking(): void {
  if (typeof window === "undefined" || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
}

/** Speak text with an agent-specific voice persona. */
export function speakAsAgent(
  text: string,
  agentType: string,
  profile: VoiceProfile | undefined,
  muted: boolean
): void {
  if (muted || !text.trim()) return;
  if (typeof window === "undefined" || !window.speechSynthesis) return;

  primeSpeechSynthesis();
  stopSpeaking();

  const utter = new SpeechSynthesisUtterance(text);
  utter.pitch = profile?.pitch ?? 1;
  utter.rate = profile?.rate ?? 0.92;
  const voice = pickVoice(profile?.voice_hints ?? ["en-US"]);
  if (voice) utter.voice = voice;

  utter.onerror = () => {
    /* fallback silent — text still visible */
  };

  window.speechSynthesis.speak(utter);
}

export const DEFAULT_AGENT_VOICES: Record<string, VoiceProfile> = {
  executive_assistant: { pitch: 0.88, rate: 0.95, voice_hints: ["Daniel", "Alex", "Male", "en-GB"] },
  research_analyst: { pitch: 1.0, rate: 0.88, voice_hints: ["Samantha", "Karen", "Female", "en-AU"] },
  concierge: { pitch: 1.05, rate: 0.9, voice_hints: ["Victoria", "Moira", "Female", "en-GB"] },
  luxury_analyst: { pitch: 0.95, rate: 0.85, voice_hints: ["Fred", "Tom", "Male", "en-US"] },
  travel: { pitch: 1.02, rate: 0.93, voice_hints: ["Tessa", "Allison", "Female", "en-US"] },
  knowledge_librarian: { pitch: 0.92, rate: 0.87, voice_hints: ["Serena", "Kate", "Female", "en-GB"] },
  writing: { pitch: 1.08, rate: 0.9, voice_hints: ["Zira", "Susan", "Female", "en-US"] },
  presentation: { pitch: 0.9, rate: 0.86, voice_hints: ["Rishi", "Oliver", "Male", "en-IN"] },
  operations: { pitch: 0.85, rate: 0.94, voice_hints: ["Aaron", "Nathan", "Male", "en-US"] },
};

export function voiceProfileForAgent(
  agentType: string,
  fromApi?: VoiceProfile
): VoiceProfile {
  return fromApi ?? DEFAULT_AGENT_VOICES[agentType] ?? { pitch: 1, rate: 0.92, voice_hints: ["en-US"] };
}
