"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { Lock } from "lucide-react";
import { SutraWordmark } from "@/components/hud/SutraWordmark";
import { FIRST_BREATH_KEY } from "@/lib/rudra-theme";
import { login } from "@/lib/auth";
import { cn } from "@/lib/utils";

const LoginCosmos = dynamic(
  () => import("@/components/cosmos/LoginCosmos").then((m) => m.LoginCosmos),
  { ssr: false }
);

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
    <div className="relative min-h-screen overflow-hidden bg-background text-foreground">
      <LoginCosmos />

      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4">
        <SutraWordmark className="mb-8 text-2xl" />

        <div className="mb-6 flex h-32 w-32 items-center justify-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/trident-login.png"
            alt="Rudra trishula"
            className="h-full w-full object-contain trident-idle"
            style={{
              mixBlendMode: "screen",
              filter: "drop-shadow(0 0 24px hsl(var(--cosmos-violet) / 0.7))",
            }}
          />
        </div>

        <p className="mb-6 font-hud text-xs tracking-[0.28em] text-muted-foreground">COSMIC UPLINK</p>

        <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4">
          <label className="block">
            <span className="mb-1.5 block font-terminal text-[9px] uppercase tracking-wider text-muted-foreground/90">
              Operator
            </span>
            <input
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border-b border-primary/30 bg-transparent px-1 py-2.5 font-terminal text-sm text-foreground outline-none focus:border-primary/60"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block font-terminal text-[9px] uppercase tracking-wider text-muted-foreground/90">
              Access Key
            </span>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-0 top-1/2 h-4 w-4 -translate-y-1/2 text-primary/40" />
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border-b border-primary/30 bg-transparent py-2.5 pl-8 pr-1 font-terminal text-sm text-foreground outline-none focus:border-primary/60"
                placeholder="Enter key"
              />
            </div>
          </label>

          {error && (
            <p className="border border-destructive/30 bg-destructive/10 px-3 py-2 font-terminal text-xs text-red-300">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading || !password}
            className={cn(
              "mt-4 w-full py-3 font-hud text-sm tracking-[0.22em] text-foreground",
              "border border-primary/40 bg-primary/5 backdrop-blur-sm transition",
              "hover:border-primary/60 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-40"
            )}
          >
            {loading ? "AWAKENING…" : "ENTER COSMOS"}
          </button>
        </form>

        <p className="mt-8 font-terminal text-[8px] text-muted-foreground/60">
          OWNER_USERNAME / OWNER_PASSWORD in backend .env
        </p>
      </div>
    </div>
  );
}
