"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock } from "lucide-react";
import { HudBackground } from "@/components/hud/HudBackground";
import { SovereignTablet } from "@/components/tablet/SovereignTablet";
import { SutraWordmark } from "@/components/hud/SutraWordmark";
import { FIRST_BREATH_KEY } from "@/lib/rudra-theme";
import { login } from "@/lib/auth";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("owner");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      sessionStorage.setItem(FIRST_BREATH_KEY, "pending");
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-background text-amber-100">
      <HudBackground />

      <SovereignTablet
        className="max-w-md"
        header={
          <>
            <SutraWordmark className="text-sm" />
            <span className="font-terminal text-[9px] uppercase tracking-widest text-amber-200/45">
              Sacred uplink
            </span>
          </>
        }
        footer={
          <span className="font-terminal text-[8px] text-amber-200/35">
            OWNER_USERNAME / OWNER_PASSWORD in backend .env
          </span>
        }
      >
        <div className="flex flex-col items-center py-2 text-center">
          <div className="rudra-breath mb-5 flex h-36 w-36 items-center justify-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/trident-login.png"
              alt="Rudra trishula"
              className="h-full w-full object-contain"
              style={{
                mixBlendMode: "screen",
                WebkitMaskImage: "radial-gradient(ellipse 60% 70% at 50% 48%, #000 56%, transparent 100%)",
                maskImage: "radial-gradient(ellipse 60% 70% at 50% 48%, #000 56%, transparent 100%)",
                filter: "drop-shadow(0 0 16px hsl(var(--cosmos-violet) / 0.6))",
              }}
            />
          </div>
          <p className="font-hud text-xs tracking-[0.28em] text-amber-200/70">PRESENT YOUR KEY</p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4 px-1">
          <label className="block">
            <span className="mb-1.5 block font-terminal text-[9px] uppercase tracking-wider text-amber-200/45">
              Operator
            </span>
            <input
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-amber-500/25 bg-black/50 px-3 py-2.5 font-terminal text-sm text-amber-100 outline-none focus:border-amber-400/60"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block font-terminal text-[9px] uppercase tracking-wider text-amber-200/45">
              Access Key
            </span>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-amber-400/40" />
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-amber-500/25 bg-black/50 py-2.5 pl-10 pr-3 font-terminal text-sm text-amber-100 outline-none focus:border-amber-400/60"
                placeholder="Enter key"
              />
            </div>
          </label>

          {error && (
            <p className="border border-red-500/30 bg-red-950/30 px-3 py-2 font-terminal text-xs text-red-300">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading || !password}
            className={cn(
              "w-full border border-amber-400/50 bg-stone-950/40 py-3 font-hud text-sm tracking-[0.22em] text-amber-100",
              "transition hover:bg-stone-900/50 disabled:cursor-not-allowed disabled:opacity-40"
            )}
          >
            {loading ? "AWAKENING…" : "ENTER SANCTUM"}
          </button>
        </form>
      </SovereignTablet>
    </div>
  );
}
