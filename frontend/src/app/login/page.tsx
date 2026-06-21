"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
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
    <div data-theme="observatory" className="obs-login-page relative min-h-screen overflow-hidden">
      <LoginCosmos />

      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4">
        <div className="mb-8 text-center">
          <div className="text-sm font-semibold tracking-[0.28em] text-[var(--obs-cyan)]">OBSERVATORY NINE</div>
          <div className="mt-1 text-[8px] tracking-[0.14em] text-[var(--obs-label)]">RUDRA AI · SECURE UPLINK</div>
        </div>

        <form onSubmit={onSubmit} className="obs-login-form mx-auto w-full max-w-sm">
          <label className="block">
            <span>OPERATOR</span>
            <input
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </label>

          <label className="mt-4 block">
            <span>ACCESS KEY</span>
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter key"
            />
          </label>

          {error && (
            <p className="mt-3 border border-red-500/30 bg-red-500/10 px-2 py-1.5 font-mono text-[9px] text-red-300">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading || !password}
            className={cn("mt-5 w-full", loading && "opacity-70")}
          >
            {loading ? "AUTHENTICATING…" : "ENTER OBSERVATORY"}
          </button>
        </form>

        <p className="mt-5 text-center font-mono text-[7px] text-[var(--obs-label)]">
          OWNER_USERNAME / OWNER_PASSWORD in backend .env
        </p>
      </div>
    </div>
  );
}
