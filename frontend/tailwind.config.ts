import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        cosmos: {
          void: "hsl(var(--cosmos-void))",
          deep: "hsl(var(--cosmos-deep))",
          cyan: "hsl(var(--cosmos-cyan))",
          violet: "hsl(var(--cosmos-violet))",
          magenta: "hsl(var(--cosmos-magenta))",
          star: "hsl(var(--cosmos-star))",
        },
        rudra: {
          gold: "hsl(var(--rudra-gold))",
          "gold-dim": "hsl(var(--rudra-gold-dim))",
          panel: "hsl(var(--rudra-panel))",
          terminal: "hsl(var(--rudra-terminal))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        hud: ["var(--font-space)", "Space Grotesk", "system-ui", "sans-serif"],
        terminal: ['"SF Mono"', '"Fira Code"', "Consolas", "monospace"],
        display: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
