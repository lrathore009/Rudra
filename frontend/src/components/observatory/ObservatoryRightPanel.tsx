"use client";

import {
  OBSERVATORY_INSTRUMENTS,
  OBSERVATORY_OVERALL_METRIC,
} from "./observatory-config";

function OrbitalOverview() {
  return (
    <svg className="obs-orbit-svg" viewBox="0 0 200 80" aria-hidden>
      <circle cx="100" cy="40" r="6" fill="#e8a030" opacity={0.9} />
      {[18, 28, 38, 48].map((r, i) => (
        <ellipse
          key={r}
          cx="100"
          cy="40"
          rx={r}
          ry={r * 0.38}
          fill="none"
          stroke="rgba(0,188,212,0.25)"
          strokeWidth="0.75"
          transform={`rotate(${i * 12} 100 40)`}
        />
      ))}
      <circle cx="118" cy="36" r="2.5" fill="#607890" />
      <circle cx="82" cy="44" r="2" fill="#a8b8c8" />
      <circle cx="130" cy="42" r="3" fill="#c88b3a" />
    </svg>
  );
}

function BrainWireframe() {
  return (
    <svg className="obs-brain-svg" viewBox="0 0 48 48" aria-hidden>
      <ellipse cx="24" cy="24" rx="18" ry="20" fill="none" stroke="rgba(0,188,212,0.5)" strokeWidth="0.75" />
      <path
        d="M24 6 C14 6 8 14 8 24 C8 34 14 42 24 42 C34 42 40 34 40 24 C40 14 34 6 24 6 M24 6 C24 6 24 42 24 42 M8 24 C16 20 32 20 40 24 M8 24 C16 28 32 28 40 24"
        fill="none"
        stroke="rgba(0,188,212,0.45)"
        strokeWidth="0.6"
      />
      <circle cx="24" cy="24" r="2" fill="rgba(0,188,212,0.6)" />
    </svg>
  );
}

export function ObservatoryRightPanel() {
  return (
    <aside className="obs-side obs-side-right">
      <div className="obs-panel">
        <div className="obs-panel-title">ORBITAL OVERVIEW</div>
        <OrbitalOverview />
        <div className="obs-feed-row">
          <span>SOLAR POSITION</span>
          <span className="obs-feed-val">SUN</span>
        </div>
        <div className="obs-feed-row">
          <span>DISTANCE</span>
          <span className="obs-feed-val">1.495M km</span>
        </div>
        <div className="obs-feed-row">
          <span>VELOCITY</span>
          <span className="obs-feed-val">29.78 km/s</span>
        </div>
        <div className="obs-feed-row">
          <span>ORBITAL PHASE</span>
          <span className="obs-feed-val">0.42 rad</span>
        </div>
      </div>

      <div className="obs-panel">
        <div className="obs-panel-title">INSTRUMENT METRICS</div>
        {OBSERVATORY_INSTRUMENTS.map((inst) => (
          <div key={inst.id} className="obs-metric-row">
            <span>{inst.name}</span>
            <div className="obs-metric-bar">
              <div className="obs-metric-fill" style={{ width: `${inst.metric}%` }} />
            </div>
            <span className="obs-metric-pct">{inst.metric}%</span>
          </div>
        ))}
        <div className="obs-metric-row" style={{ marginTop: "0.25rem", paddingTop: "0.2rem", borderTop: "1px solid rgba(0,188,212,0.12)" }}>
          <span>OVERALL</span>
          <div className="obs-metric-bar">
            <div className="obs-metric-fill" style={{ width: `${OBSERVATORY_OVERALL_METRIC}%` }} />
          </div>
          <span className="obs-metric-pct">{OBSERVATORY_OVERALL_METRIC}%</span>
        </div>
      </div>

      <div className="obs-panel">
        <div className="obs-panel-title">AI CORE STATUS</div>
        <div className="obs-brain-wrap">
          <BrainWireframe />
          <div className="obs-core-spec">
            <div>
              MODEL: <span>RUDRA-9</span>
            </div>
            <div>
              PARAMETERS: <span>9.1T</span>
            </div>
            <div>
              CONTEXT WINDOW: <span>2.0M</span>
            </div>
            <div>
              LEARNING RATE: <span>ADAPTIVE</span>
            </div>
            <div>
              GUARDRAILS: <span>ACTIVE</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
