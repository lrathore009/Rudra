"use client";

export function GemGauge({
  value,
  label,
  size = 36,
}: {
  value: number;
  label: string;
  size?: number;
}) {
  const v = Math.max(0, Math.min(1, value));
  const r = size * 0.38;
  const c = 2 * Math.PI * r;
  const cx = size / 2;
  const cy = size / 2;

  const gradId = `gem-${label.replace(/\s/g, "-")}`;
  return (
    <div className="flex flex-col items-center gap-0.5" title={label}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
        <defs>
          <radialGradient id={gradId} cx="35%" cy="30%" r="65%">
            <stop offset="0%" stopColor="hsl(var(--rudra-gold-bright) / 0.9)" />
            <stop offset="100%" stopColor="hsl(var(--rudra-gold) / 0.35)" />
          </radialGradient>
        </defs>
        <circle cx={cx} cy={cy} r={r + 3} fill="hsl(var(--rudra-bark-deep) / 0.8)" />
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="hsl(var(--rudra-gold) / 0.15)"
          strokeWidth="2.5"
        />
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={`url(#${gradId})`}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - v)}
          transform={`rotate(-90 ${cx} ${cy})`}
          style={{ filter: "drop-shadow(0 0 3px hsl(var(--rudra-saffron) / 0.5))" }}
        />
        <circle
          cx={cx - 2}
          cy={cy - 2}
          r={r * 0.35}
          fill="hsl(var(--rudra-gold-bright) / 0.25)"
        />
      </svg>
      <span className="font-terminal text-[7px] uppercase tracking-wider text-amber-200/40">{label}</span>
    </div>
  );
}
