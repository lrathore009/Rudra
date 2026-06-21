"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { Lock } from "lucide-react";
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
    <div className="login-prime-page relative min-h-screen overflow-hidden text-foreground">
      <LoginCosmos />

      <div className="relative z-10 flex min-h-screen flex-col">
        <div className="flex-1" aria-hidden />

        <div className="px-4 pb-10 sm:pb-14">
          <form onSubmit={onSubmit} className="login-prime-form mx-auto w-full max-w-md">
            <label className="login-prime-field block">
              <span className="login-prime-label">Operator</span>
              <input
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="login-prime-input"
              />
            </label>

            <label className="login-prime-field mt-5 block">
              <span className="login-prime-label">Access Key</span>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--prime-cyan)] opacity-50" />
                <input
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="login-prime-input login-prime-input-key pl-10"
                  placeholder="Enter key"
                />
              </div>
            </label>

            {error && (
              <p className="mt-4 border border-destructive/30 bg-destructive/10 px-3 py-2 font-terminal text-xs text-red-300">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading || !password}
              className={cn("login-prime-submit mt-6 w-full", loading && "opacity-70")}
            >
              {loading ? "AWAKENING…" : "ENTER PRIME"}
            </button>
          </form>

          <p className="mt-6 text-center font-terminal text-[8px] text-muted-foreground/45">
            OWNER_USERNAME / OWNER_PASSWORD in backend .env
          </p>
        </div>
      </div>
    </div>
  );
}
