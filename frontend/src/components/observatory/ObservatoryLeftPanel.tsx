"use client";

import { useEffect, useState } from "react";

function formatMissionTime(ms: number) {
  const totalSec = Math.floor(ms / 1000);
  const days = Math.floor(totalSec / 86400);
  const hrs = Math.floor((totalSec % 86400) / 3600);
  const mins = Math.floor((totalSec % 3600) / 60);
  const secs = totalSec % 60;
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(days)} : ${pad(hrs)} : ${pad(mins)} : ${pad(secs)}`;
}

function missionStamp(ms: number) {
  const totalSec = Math.floor(ms / 1000);
  const days = Math.floor(totalSec / 86400);
  const hrs = Math.floor((totalSec % 86400) / 3600);
  const mins = Math.floor((totalSec % 3600) / 60);
  const secs = totalSec % 60;
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${days}:${pad(hrs)}:${pad(mins)}:${pad(secs)}`;
}

export function ObservatoryLeftPanel({
  logLines,
  uplinkActive,
  systemsNominal,
  processing,
}: {
  logLines: string[];
  uplinkActive: boolean;
  systemsNominal: boolean;
  processing: boolean;
}) {
  const [boot] = useState(() => Date.now());
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setElapsed(Date.now() - boot), 1000);
    return () => clearInterval(id);
  }, [boot]);

  const stamp = missionStamp(elapsed);

  return (
    <aside className="obs-side">
      <div className="obs-panel">
        <div className="obs-panel-title">SYSTEM STATUS</div>
        <div className="obs-status-row">
          <span>ORBITAL NETWORK</span>
          <span className="obs-status-ok">{uplinkActive ? "ONLINE" : "OFFLINE"}</span>
        </div>
        <div className="obs-status-row">
          <span>INSTRUMENT ARRAY</span>
          <span className="obs-status-ok">{systemsNominal ? "NOMINAL" : "DEGRADED"}</span>
        </div>
        <div className="obs-status-row">
          <span>AI CORE</span>
          <span className="obs-status-ok">{processing ? "ROUTING" : "STABLE"}</span>
        </div>
        <div className="obs-status-row">
          <span>DATA STREAM</span>
          <span className="obs-status-ok">LIVE</span>
        </div>
      </div>

      <div className="obs-panel">
        <div className="obs-panel-title">OBSERVATORY FEED</div>
        <div className="obs-feed-row">
          <span>LOCATION</span>
          <span className="obs-feed-val">L1 ORBIT</span>
        </div>
        <div className="obs-feed-row">
          <span>COORDINATES</span>
          <span className="obs-feed-val">1.495M km</span>
        </div>
        <div className="obs-feed-row">
          <span>LATENCY</span>
          <span className="obs-feed-val">128 ms</span>
        </div>
        <div className="obs-feed-row">
          <span>UPLINK</span>
          <span className="obs-feed-val">{uplinkActive ? "NOMINAL" : "LOST"}</span>
        </div>
      </div>

      <div className="obs-panel">
        <div className="obs-panel-title">MISSION TIME</div>
        <div className="obs-mission-time">{formatMissionTime(elapsed)}</div>
        <div className="obs-mission-labels">
          <span>DAYS</span>
          <span>HRS</span>
          <span>MINS</span>
          <span>SECS</span>
        </div>
      </div>

      <div className="obs-panel" style={{ flex: 1, minHeight: 0 }}>
        <div className="obs-panel-title">SYSTEM LOG</div>
        <div className="obs-log">
          {logLines.slice(-8).map((line, i) => (
            <div key={`${line}-${i}`} className="obs-log-line">
              [{stamp}] {line.replace(/^>\s*/, "").toUpperCase()}
            </div>
          ))}
          {logLines.length === 0 && (
            <div className="obs-log-line">[{stamp}] RUDRA → CORE: Observatory Nine online</div>
          )}
        </div>
      </div>
    </aside>
  );
}

export { missionStamp };
