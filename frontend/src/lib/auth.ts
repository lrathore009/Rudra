/**
 * Client-side auth token storage (sessionStorage — cleared when tab closes).
 */

const TOKEN_KEY = "rudra_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

export function authHeaders(): Record<string, string> {
  const token = getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}

export interface AuthUser {
  user_id: string;
  username: string;
  display_name: string | null;
  is_owner: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  username: string;
  display_name: string | null;
}

function apiBase(): string {
  if (typeof window !== "undefined") {
    return "/api/rudra";
  }
  return (
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.RUDRA_BACKEND_URL ||
    "http://localhost:8000/api"
  )
    .replace(/\/$/, "")
    .replace(/\/api$/, "") + "/api";
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${apiBase()}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    let detail = "Invalid credentials";
    try {
      const body = await res.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      if (res.status === 502 || res.status === 503 || res.status === 530) {
        detail =
          "Rudra backend unreachable. Ensure your Mac is running start.sh + start-tunnel.sh and Vercel RUDRA_BACKEND_URL is current.";
      }
    }
    throw new Error(detail);
  }
  const data = (await res.json()) as LoginResponse;
  setToken(data.access_token);
  return data;
}

export async function logout(): Promise<void> {
  const token = getToken();
  if (token) {
    try {
      await fetch(`${apiBase()}/v1/auth/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      /* best effort */
    }
  }
  clearToken();
}

export async function fetchMe(): Promise<AuthUser | null> {
  const token = getToken();
  if (!token) return null;
  const res = await fetch(`${apiBase()}/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 401) {
    clearToken();
    return null;
  }
  if (!res.ok) return null;
  return res.json() as Promise<AuthUser>;
}
