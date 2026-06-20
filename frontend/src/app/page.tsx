"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Activity,
  CalendarClock,
  Search,
  Sparkles,
} from "lucide-react";
import { HudBackground } from "@/components/hud/HudBackground";
import { BootSequence } from "@/components/hud/BootSequence";
import { type Stage } from "@/components/hud/ProcessStream";
import { SovereignView } from "@/components/tablet/SovereignView";
import type { RealmId } from "@/components/tablet/RealmRim";
import {
  FIRST_BREATH_KEY,
  SUTRA_TICKER,
  agentTag,
  coreRhythmFromState,
  hapticTap,
  resolveThemeMode,
  sutraPlaceholder,
  worldGreeting,
  type RudraThemeMode,
} from "@/lib/rudra-theme";
import { blip, facetChime, releaseBreath, setAmbient, stopAmbient } from "@/lib/sound";
import { StreamingThread, FirstBreathOverlay } from "@/components/hud/MalaArc";
import {
  ensureMicrophoneAccess,
  primeSpeechSynthesis,
  speakAsAgent,
  startSpeechRecognition,
  stopSpeaking,
  voiceProfileForAgent,
  type SpeechRecognitionHandle,
} from "@/lib/voice";
import {
  agentAct,
  healthServices,
  listAgents,
  listMemories,
  listSchedulerJobs,
  listSkills,
  runSchedulerJob,
  streamCommand,
  traceStats,
  type ActStep,
  type AgentInfo,
  type Memory,
  type RoutingAnalysisItem,
  type SchedulerJob,
  type ServiceHealth,
  type SkillInfo,
  type TraceStats,
  type VoiceProfile,
} from "@/lib/api";
import { fetchMe, isAuthenticated, logout as authLogout } from "@/lib/auth";

interface Msg {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  agentType?: string;
  voiceProfile?: VoiceProfile;
  streamed?: boolean;
  streaming?: boolean;
  ts: Date;
}

const PIPELINE = [
  "SUTRA RECEIVED",
  "INTENT PERCEIVED",
  "INNER COUNCIL",
  "CONTEMPLATION",
  "GATHERING KNOWLEDGE",
  "RESPONSE FORGED",
];

export default function Jarvis() {
  const router = useRouter();
  const [authReady, setAuthReady] = useState(false);
  const [operator, setOperator] = useState<string | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<"agents" | "tools">("agents");
  const [processing, setProcessing] = useState(false);
  const [stageIdx, setStageIdx] = useState(-1);
  const [steps, setSteps] = useState<ActStep[]>([]);
  const [routingAnalysis, setRoutingAnalysis] = useState<RoutingAnalysisItem[]>([]);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [vitals, setVitals] = useState<ServiceHealth[]>([]);
  const [systemsNominal, setSystemsNominal] = useState(false);
  const [jobs, setJobs] = useState<SchedulerJob[]>([]);
  const [stats, setStats] = useState<TraceStats | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | undefined>();
  const [status, setStatus] = useState("BOOTING CORE");
  const [clock, setClock] = useState<Date | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [booting, setBooting] = useState(true);
  const [muted, setMuted] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceHint, setVoiceHint] = useState<string | null>(null);
  const [themeMode, setThemeMode] = useState<RudraThemeMode>("auto");
  const [activeRoutedAgent, setActiveRoutedAgent] = useState<string | undefined>();
  const [errorFacet, setErrorFacet] = useState<string | undefined>();
  const [firstBreath, setFirstBreath] = useState(false);
  const [threadReleasing, setThreadReleasing] = useState(false);
  const [tickerIdx, setTickerIdx] = useState(0);
  const [streamingMsgId, setStreamingMsgId] = useState<string | null>(null);
  const [coreRect, setCoreRect] = useState<DOMRect | null>(null);
  const [streamRect, setStreamRect] = useState<DOMRect | null>(null);
  const [activeRealm, setActiveRealm] = useState<RealmId | null>(null);
  const feedRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recRef = useRef<SpeechRecognitionHandle | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const coreRef = useRef<HTMLDivElement>(null);
  const streamingMsgRef = useRef<HTMLDivElement | null>(null);

  const pushLog = useCallback((s: string) => setLog((p) => [...p.slice(-50), s]), []);

  useEffect(() => {
    (async () => {
      if (!isAuthenticated()) {
        router.replace("/login");
        return;
      }
      const me = await fetchMe();
      if (!me) {
        router.replace("/login");
        return;
      }
      setOperator(me.display_name || me.username);
      setAuthReady(true);
    })();
  }, [router]);

  useEffect(() => {
    const id = setTimeout(() => setBooting(false), 1200);
    return () => clearTimeout(id);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const saved = localStorage.getItem("rudra-theme-mode") as RudraThemeMode | null;
    if (saved === "sandhya" || saved === "nisha" || saved === "auto") setThemeMode(saved);
    if (sessionStorage.getItem(FIRST_BREATH_KEY) === "pending") {
      sessionStorage.removeItem(FIRST_BREATH_KEY);
      setFirstBreath(true);
    }
  }, []);

  useEffect(() => {
    const t = setInterval(() => setTickerIdx((i) => (i + 1) % SUTRA_TICKER.length), 8000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    return () => {
      recRef.current?.stop();
      stopSpeaking();
    };
  }, []);

  useEffect(() => {
    if (muted) stopSpeaking();
  }, [muted]);

  useEffect(() => {
    setClock(new Date());
    const t = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const boot = [
      "threading the mala",
      "nine facets aligned",
      "local vault sealed",
      "breath calibrated",
    ];
    boot.forEach((b, i) => setTimeout(() => pushLog(`◇ ${b}`), i * 200));
    (async () => {
      try {
        const [a, sk, m, v, j, st] = await Promise.all([
          listAgents().catch(() => [] as AgentInfo[]),
          listSkills().catch(() => [] as SkillInfo[]),
          listMemories(8).catch(() => [] as Memory[]),
          healthServices()
            .then((r) => {
              setSystemsNominal(r.required_ok);
              return r.services;
            })
            .catch(() => [] as ServiceHealth[]),
          listSchedulerJobs().catch(() => [] as SchedulerJob[]),
          traceStats().catch(() => null),
        ]);
        setAgents(a);
        setSkills(sk);
        setMemories(m);
        setVitals(v);
        setJobs(j);
        setStats(st);
        const ok = v.length === 0 || v.filter((s) => !s.optional).every((s) => s.ok);
        setStatus(ok ? "PRESENT · NOMINAL" : "DEGRADED");
        setMessages([
          {
            id: "w",
            role: "system",
            content: "Rudra is present. The mala is threaded. Offer your sutra.",
            ts: new Date(),
          },
        ]);
        pushLog("◇ RUDRA PRESENT");
      } catch {
        setStatus("LINK OFFLINE");
        setMessages([
          {
            id: "w",
            role: "system",
            content: "Backend unreachable on :8000. Start it to bring Rudra online.",
            ts: new Date(),
          },
        ]);
      }
    })();
  }, [pushLog]);

  useEffect(() => {
    const evts = [
      "heartbeat ◇ ok",
      "memory lattice synced",
      "ollama bridge stable",
      "vector index warm",
      "audit ledger sealed",
      "entropy pool nominal",
      "cipher rotation ok",
      "scheduler tick ◇",
    ];
    let i = 0;
    const t = setInterval(() => {
      pushLog(`· ${evts[i % evts.length]}`);
      i++;
    }, 2600);
    return () => clearInterval(t);
  }, [pushLog]);

  useEffect(() => {
    const t = setInterval(async () => {
      try {
        const h = await healthServices();
        setVitals(h.services);
        setSystemsNominal(h.required_ok);
      } catch {
        /* keep last */
      }
      try {
        setStats(await traceStats());
      } catch {
        /* keep last */
      }
    }, 13000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!processing) return;
    setStageIdx(0);
    const t = setInterval(() => setStageIdx((p) => Math.min(p + 1, PIPELINE.length - 2)), 620);
    return () => clearInterval(t);
  }, [processing]);

  useEffect(() => {
    feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, steps]);

  const stages: Stage[] = useMemo(
    () =>
      PIPELINE.map(
        (label, i): Stage => ({
          label,
          state: processing
            ? i < stageIdx
              ? "done"
              : i === stageIdx
                ? "active"
                : "pending"
            : "done",
        })
      ),
    [processing, stageIdx]
  );

  const resolvedTheme = useMemo(
    () => resolveThemeMode(themeMode, clock?.getHours() ?? 12),
    [themeMode, clock]
  );
  const isStreaming = useMemo(() => messages.some((m) => m.streaming), [messages]);
  const coreRhythm = useMemo(
    () =>
      coreRhythmFromState(processing, isStreaming, !!errorFacet, processing && stageIdx >= 2),
    [processing, isStreaming, errorFacet, stageIdx]
  );
  const malaProgress = useMemo(
    () =>
      processing
        ? {
            current: Math.min(9, Math.max(1, stageIdx + 1 + Math.min(steps.length, 2))),
            total: 9,
          }
        : undefined,
    [processing, stageIdx, steps.length]
  );
  const activeFacetTag = useMemo(
    () => agentTag(selectedAgent ?? activeRoutedAgent),
    [selectedAgent, activeRoutedAgent]
  );

  const submit = useCallback(
    async (override?: string) => {
      const q = (override ?? input).trim();
      if (!q || processing) return;
      setMessages((p) => [...p, { id: crypto.randomUUID(), role: "user", content: q, ts: new Date() }]);
      setInput("");
      setSteps([]);
      setRoutingAnalysis([]);
      setProcessing(true);
      setStageIdx(0);
      setActiveRoutedAgent(selectedAgent);
      blip("send", muted);
      hapticTap(10);
      pushLog(`◇ sutra · ${q.slice(0, 36)}`);
      primeSpeechSynthesis();
      try {
        if (mode === "tools" && !selectedAgent) {
          const r = await agentAct(q);
          setSteps(r.steps);
          setMessages((p) => [
            ...p,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: r.answer,
              agent: `autonomous · ${r.model} · ${r.latency_ms}ms · ${r.tools_used.length} ops`,
              ts: new Date(),
            },
          ]);
          pushLog(`<< ${r.tools_used.length} tool ops · ${r.latency_ms}ms`);
        } else {
          // Streaming path — one Rudra voice, tokens appear live, cancellable via Stop.
          const controller = new AbortController();
          abortRef.current = controller;
          const msgId = crypto.randomUUID();
          let acc = "";
          let routedType = selectedAgent ?? "executive_assistant";
          setStreamingMsgId(msgId);
          setMessages((p) => [
            ...p,
            {
              id: msgId,
              role: "assistant",
              content: "",
              agent: "Rudra",
              agentType: routedType,
              streamed: true,
              streaming: true,
              ts: new Date(),
            },
          ]);
          await streamCommand(q, {
            agentType: selectedAgent,
            signal: controller.signal,
            onMeta: (meta) => {
              routedType = meta.agent_type;
              setActiveRoutedAgent(meta.agent_type);
              facetChime(muted);
              setMessages((p) =>
                p.map((x) => (x.id === msgId ? { ...x, agentType: meta.agent_type } : x))
              );
              if (meta.sources_used?.length) pushLog(`◇ ${meta.sources_used.length} sources gathered`);
            },
            onToken: (t) => {
              acc += t;
              setMessages((p) => p.map((x) => (x.id === msgId ? { ...x, content: acc } : x)));
            },
            onDone: () => {
              setStreamingMsgId(null);
              setMessages((p) => p.map((x) => (x.id === msgId ? { ...x, streaming: false } : x)));
              if (!muted && acc) {
                speakAsAgent(acc, routedType, voiceProfileForAgent(routedType, undefined), muted);
              }
              pushLog(`<< Rudra · ${acc.length} chars`);
            },
          });
        }
        blip("recv", muted);
        try {
          setMemories(await listMemories(8));
        } catch {
          /* keep */
        }
        try {
          setStats(await traceStats());
        } catch {
          /* keep */
        }
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") {
          setMessages((p) => p.map((x) => (x.streaming ? { ...x, streaming: false } : x)));
          setStreamingMsgId(null);
          pushLog("◇ breath released");
        } else {
          const m = e instanceof Error && e.message ? e.message : "Backend unreachable on :8000";
          setErrorFacet(agentTag(activeRoutedAgent ?? selectedAgent));
          setMessages((p) => [
            ...p,
            {
              id: crypto.randomUUID(),
              role: "system",
              content: `Rudra could not complete that sutra. ${m}`,
              ts: new Date(),
            },
          ]);
          pushLog("◇ facet strain");
        }
      } finally {
        abortRef.current = null;
        setProcessing(false);
        setActiveRoutedAgent(undefined);
        inputRef.current?.focus();
      }
    },
    [input, processing, mode, selectedAgent, activeRoutedAgent, muted, pushLog]
  );

  const stop = useCallback(() => {
    setThreadReleasing(true);
    setTimeout(() => setThreadReleasing(false), 400);
    abortRef.current?.abort();
    abortRef.current = null;
    stopSpeaking();
    releaseBreath(muted);
    hapticTap([12, 40, 20]);
    setStreamingMsgId(null);
    setProcessing(false);
    pushLog("◇ breath released");
  }, [muted, pushLog]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && abortRef.current) stop();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [stop]);

  useEffect(() => {
    setAmbient(processing, isStreaming, muted);
    return () => stopAmbient();
  }, [processing, isStreaming, muted]);

  useEffect(() => {
    if (!errorFacet) return;
    const t = setTimeout(() => setErrorFacet(undefined), 3200);
    return () => clearTimeout(t);
  }, [errorFacet]);

  useEffect(() => {
    const measure = () => {
      if (coreRef.current) setCoreRect(coreRef.current.getBoundingClientRect());
      if (streamingMsgRef.current) setStreamRect(streamingMsgRef.current.getBoundingClientRect());
    };
    measure();
    if (!isStreaming) return;
    const id = setInterval(measure, 120);
    window.addEventListener("resize", measure);
    return () => {
      clearInterval(id);
      window.removeEventListener("resize", measure);
    };
  }, [isStreaming, messages, stageIdx]);

  const runDigest = useCallback(async () => {
    if (processing) return;
    setProcessing(true);
    setSteps([]);
    setStageIdx(0);
    pushLog(">> RUN morning_digest");
    try {
      const r = await runSchedulerJob("morning_digest");
      setMessages((p) => [
        ...p,
        { id: crypto.randomUUID(), role: "assistant", content: r.result, agent: "scheduler · morning_digest", ts: new Date() },
      ]);
      try {
        setJobs(await listSchedulerJobs());
      } catch {
        /* keep */
      }
    } catch {
      setMessages((p) => [...p, { id: crypto.randomUUID(), role: "system", content: "⚠ Could not run digest.", ts: new Date() }]);
    } finally {
      setProcessing(false);
    }
  }, [processing, pushLog]);

  const startVoice = useCallback(async () => {
    primeSpeechSynthesis();
    if (listening) {
      recRef.current?.stop();
      recRef.current = null;
      setListening(false);
      return;
    }
    setVoiceHint(null);
    const allowed = await ensureMicrophoneAccess();
    if (!allowed) {
      setVoiceHint("Microphone blocked — allow access in browser settings.");
      pushLog("!! mic permission denied");
      return;
    }
    recRef.current = startSpeechRecognition({
      onInterim: (text) => setInput(text),
      onFinal: (text) => {
        setInput(text);
        if (text.trim()) void submit(text);
      },
      onError: (message) => {
        setVoiceHint(message);
        pushLog(`!! ${message}`);
      },
      onListeningChange: (active) => {
        setListening(active);
        if (!active) recRef.current = null;
      },
    });
    if (recRef.current) {
      blip("send", muted);
      pushLog(">> VOICE UPLINK OPEN");
    }
  }, [listening, muted, submit, pushLog]);

  const requiredVitals = vitals.filter((v) => !v.optional);
  const requiredOnline = requiredVitals.filter((v) => v.ok).length;
  const subsysRate =
    requiredVitals.length > 0
      ? requiredOnline / requiredVitals.length
      : systemsNominal
        ? 1
        : 0;
  const successRate = systemsNominal ? 1 : (stats?.success_rate ?? subsysRate);
  const showProcess = processing || steps.length > 0 || routingAnalysis.length > 0;
  const modelName = stats?.by_model ? Object.keys(stats.by_model)[0] ?? "local" : "local";

  const ACTIONS = [
    { icon: Activity, label: "Daily Brief", run: () => submit("Give me my executive daily briefing.") },
    {
      icon: Search,
      label: "Deep Research",
      run: () => submit("Research the current state of local-first personal AI and summarize the key points."),
    },
    { icon: CalendarClock, label: "Run Digest", run: runDigest },
    { icon: Sparkles, label: "Capabilities", run: () => submit("List what you can do for me right now.") },
  ];

  if (!authReady) {
    return (
      <main className="relative h-screen w-screen overflow-hidden text-amber-50">
        <HudBackground />
        <div className="sovereign-stage">
          <div className="flex h-full items-center justify-center font-hud text-sm neon">VERIFYING PRESENCE…</div>
        </div>
      </main>
    );
  }

  return (
    <main data-theme={resolvedTheme} className="relative h-screen w-screen overflow-hidden text-amber-50">
      {booting && <BootSequence />}
      <FirstBreathOverlay show={firstBreath} onDone={() => setFirstBreath(false)} />
      <HudBackground still={!!errorFacet} />
      <StreamingThread
        active={isStreaming && !threadReleasing}
        releasing={threadReleasing}
        coreRect={coreRect}
        targetRect={streamRect}
      />
      <SovereignView
        themeMode={themeMode}
        onThemeCycle={() => {
          const next: RudraThemeMode =
            themeMode === "auto" ? "sandhya" : themeMode === "sandhya" ? "nisha" : "auto";
          setThemeMode(next);
          localStorage.setItem("rudra-theme-mode", next);
        }}
        operator={operator}
        status={status}
        clock={clock}
        onLogout={async () => {
          await authLogout();
          router.replace("/login");
        }}
        muted={muted}
        onToggleMute={() => setMuted((v) => !v)}
        greeting={worldGreeting(clock?.getHours() ?? 12)}
        modelName={modelName}
        memoryCount={memories.length}
        agentCount={agents.length}
        successRate={successRate}
        subsysRate={subsysRate}
        coreRef={coreRef}
        processing={processing}
        coreRhythm={coreRhythm}
        activeFacetTag={activeFacetTag}
        selectedAgent={selectedAgent}
        activeRoutedAgent={activeRoutedAgent}
        errorFacet={errorFacet}
        malaProgress={malaProgress}
        messages={messages}
        feedRef={feedRef}
        streamingMsgId={streamingMsgId}
        streamingMsgRef={streamingMsgRef}
        input={input}
        onInputChange={setInput}
        onSubmit={() => void submit()}
        onStop={stop}
        onVoice={() => void startVoice()}
        onToggleMode={() => setMode((m) => (m === "agents" ? "tools" : "agents"))}
        inputRef={inputRef}
        listening={listening}
        voiceHint={voiceHint}
        mode={mode}
        placeholder={sutraPlaceholder(clock?.getHours() ?? 12, processing)}
        actions={ACTIONS}
        activeRealm={activeRealm}
        onRealmChange={setActiveRealm}
        agents={agents}
        onSelectAgent={setSelectedAgent}
        skills={skills}
        jobs={jobs}
        vitals={vitals}
        stages={stages}
        steps={steps}
        showProcess={showProcess}
        onAskProject={(name) => submit(`What should I do next in ${name}?`)}
        tickerIdx={tickerIdx}
        logLine={log.slice(-1)[0] ?? "awakening…"}
        skillsCount={skills.length}
      />
    </main>
  );
}
