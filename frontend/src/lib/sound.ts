let ctx: AudioContext | null = null;
let ambientOsc: OscillatorNode | null = null;
let ambientGain: GainNode | null = null;

function getCtx(): AudioContext | null {
  if (typeof window === "undefined") return null;
  if (!ctx) {
    const AC =
      window.AudioContext ??
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (AC) ctx = new AC();
  }
  return ctx;
}

type BlipKind = "send" | "recv" | "tick" | "boot";

/** Warm, breath-like UI tones — no asset files. Resumes on first gesture. */
export function blip(kind: BlipKind, muted = false): void {
  if (muted) return;
  const c = getCtx();
  if (!c) return;
  if (c.state === "suspended") void c.resume();

  const osc = c.createOscillator();
  const gain = c.createGain();
  const freq =
    kind === "recv" ? 392 : kind === "send" ? 294 : kind === "boot" ? 220 : 330;
  osc.type = kind === "boot" ? "triangle" : "sine";
  osc.frequency.value = freq;

  const t0 = c.currentTime;
  const peak = kind === "boot" ? 0.05 : 0.06;
  gain.gain.setValueAtTime(0.0001, t0);
  gain.gain.exponentialRampToValueAtTime(peak, t0 + 0.018);
  gain.gain.exponentialRampToValueAtTime(0.0001, t0 + (kind === "boot" ? 0.35 : 0.22));

  osc.connect(gain);
  gain.connect(c.destination);
  osc.start(t0);
  osc.stop(t0 + 0.4);
}

/** Soft chime when inner council routes to a facet — never spoken, only felt */
export function facetChime(muted = false): void {
  if (muted) return;
  const c = getCtx();
  if (!c) return;
  if (c.state === "suspended") void c.resume();

  const t0 = c.currentTime;
  [329.63, 392].forEach((freq, i) => {
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.0001, t0 + i * 0.04);
    gain.gain.exponentialRampToValueAtTime(0.04, t0 + i * 0.04 + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + i * 0.04 + 0.28);
    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(t0 + i * 0.04);
    osc.stop(t0 + i * 0.04 + 0.3);
  });
}

/** Exhale on Stop / Esc */
export function releaseBreath(muted = false): void {
  if (muted) return;
  const c = getCtx();
  if (!c) return;
  if (c.state === "suspended") void c.resume();

  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = "triangle";
  osc.frequency.setValueAtTime(180, c.currentTime);
  osc.frequency.exponentialRampToValueAtTime(90, c.currentTime + 0.35);

  const t0 = c.currentTime;
  gain.gain.setValueAtTime(0.0001, t0);
  gain.gain.exponentialRampToValueAtTime(0.05, t0 + 0.04);
  gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.45);

  osc.connect(gain);
  gain.connect(c.destination);
  osc.start(t0);
  osc.stop(t0 + 0.5);
}

/** Single subtle damaru beat — minor queries */
export function damruBeat(muted = false): void {
  if (muted) return;
  const c = getCtx();
  if (!c) return;
  if (c.state === "suspended") void c.resume();

  const t0 = c.currentTime;
  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = "triangle";
  osc.frequency.setValueAtTime(320, t0);
  osc.frequency.exponentialRampToValueAtTime(188, t0 + 0.06);
  gain.gain.setValueAtTime(0.0001, t0);
  gain.gain.exponentialRampToValueAtTime(0.07, t0 + 0.008);
  gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.16);
  osc.connect(gain);
  gain.connect(c.destination);
  osc.start(t0);
  osc.stop(t0 + 0.2);
}

/** Damaru roll — full roll for major queries (research, strategy, planning) */
export function damru(muted = false): void {
  if (muted) return;
  const c = getCtx();
  if (!c) return;
  if (c.state === "suspended") void c.resume();

  const t0 = c.currentTime;
  // DA-da-da · DUM-da-da — two grouped strikes, like a turning damaru.
  const pattern = [0, 0.085, 0.165, 0.3, 0.385, 0.465];
  pattern.forEach((dt, i) => {
    const accent = i % 3 === 0;
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = "triangle";
    const base = accent ? 188 : 232 + (i % 2) * 46;
    osc.frequency.setValueAtTime(base * 1.7, t0 + dt);
    osc.frequency.exponentialRampToValueAtTime(base, t0 + dt + 0.05);
    const peak = accent ? 0.09 : 0.05;
    gain.gain.setValueAtTime(0.0001, t0 + dt);
    gain.gain.exponentialRampToValueAtTime(peak, t0 + dt + 0.007);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dt + 0.14);
    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(t0 + dt);
    osc.stop(t0 + dt + 0.22);
  });
}

/** Ultra-low ambient bed — muted by default via caller */
export function setAmbient(active: boolean, streaming: boolean, muted: boolean): void {
  const c = getCtx();
  if (!c || muted) {
    stopAmbient();
    return;
  }
  if (c.state === "suspended") void c.resume();

  if (!active) {
    stopAmbient();
    return;
  }

  if (!ambientOsc) {
    ambientOsc = c.createOscillator();
    ambientGain = c.createGain();
    ambientOsc.type = "sine";
    ambientOsc.frequency.value = 55;
    ambientOsc.connect(ambientGain);
    ambientGain.connect(c.destination);
    ambientGain.gain.value = 0.0001;
    ambientOsc.start();
  }

  const target = streaming ? 0.012 : 0.006;
  ambientGain!.gain.exponentialRampToValueAtTime(
    Math.max(target, 0.0001),
    c.currentTime + 0.4
  );
}

export function stopAmbient(): void {
  if (ambientGain && ctx) {
    ambientGain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.3);
  }
}
