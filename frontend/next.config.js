/** @type {import('next').NextConfig} */
const path = require("path");

// Backend URL for server-side proxy rewrites (tunnel or localhost).
// Browser calls same-origin /api/rudra/* — no CORS, no mixed-content issues.
const backendUrl =
  process.env.RUDRA_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

const nextConfig = {
  output: "standalone",
  // Prevent Next from picking ~/package-lock.json as the workspace root (breaks Tailwind/CSS in dev).
  outputFileTracingRoot: path.join(__dirname, ".."),
  // Proxy handled at runtime by src/app/api/rudra/[...path]/route.ts (reads env per request).
  // Rewrites below are dev fallback only when the route handler is unavailable.
  async rewrites() {
    if (process.env.VERCEL) return [];
    return [
      {
        source: "/api/rudra/:path*",
        destination: `${backendUrl.replace(/\/$/, "")}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
