"use client";

import type { GrahaId } from "@/components/cosmos/navagraha-types";
import { instrumentByGraha } from "./observatory-config";

function TravelMap() {
  return (
    <svg className="obs-map-svg" viewBox="0 0 400 220" aria-hidden>
      <rect width="400" height="220" fill="#0a1418" />
      {/* Simplified India outline */}
      <path
        d="M180 30 L200 25 L220 35 L240 50 L250 70 L255 95 L250 120 L240 145 L220 165 L200 180 L185 175 L170 160 L160 130 L155 100 L160 70 L170 45 Z"
        fill="rgba(0,60,80,0.35)"
        stroke="rgba(0,188,212,0.2)"
        strokeWidth="1"
      />
      {/* Route */}
      <path
        d="M95 95 Q180 110 280 130"
        fill="none"
        stroke="#00bcd4"
        strokeWidth="1.5"
        strokeDasharray="6 4"
      />
      <circle cx="95" cy="95" r="5" fill="#00bcd4" />
      <circle cx="280" cy="130" r="5" fill="#00bcd4" />
      <text x="88" y="88" fill="#00bcd4" fontSize="8" fontFamily="monospace">
        BOM
      </text>
      <text x="72" y="98" fill="rgba(176,190,197,0.8)" fontSize="6">
        Mumbai
      </text>
      <text x="288" y="128" fill="#00bcd4" fontSize="8" fontFamily="monospace">
        BLR
      </text>
      <text x="288" y="138" fill="rgba(176,190,197,0.8)" fontSize="6">
        Bengaluru
      </text>
    </svg>
  );
}

const OBJECTIVES: Record<GrahaId, string> = {
  surya: "Generate executive daily briefing with top three priorities and calendar conflicts for today.",
  chandra: "Draft contemplative note on research findings — tone: precise, warm, publication-ready.",
  mangal: "Plan optimized travel route to Bengaluru for client meeting on May 28.",
  budha: "Assemble presentation deck outline — five slides, executive summary first.",
  guru: "Synthesize multi-source research brief with citations and strategic recommendations.",
  shukra: "Compare luxury experience options — venue tier, ambiance, and estimated cost.",
  shani: "Review operations ledger — scheduled jobs, system health, and pending tasks.",
  rahu: "Surface concierge options grid — book, find, arrange — for open-ended request.",
  ketu: "Retrieve archived memory leaf — past context, graph node, and insight summary.",
};

const STATUS_LABEL: Record<GrahaId, string> = {
  surya: "Briefing compiled",
  chandra: "Draft in progress",
  mangal: "Route options generated",
  budha: "Slide strip ready",
  guru: "Synthesis complete",
  shani: "Ledger synced",
  shukra: "Options compared",
  rahu: "Grid populated",
  ketu: "Memory retrieved",
};

function RouteCard() {
  return (
    <div className="obs-route-card">
      <div className="obs-route-title">TRAVEL ROUTE · OPTION A</div>
      <div className="obs-route-row">
        <span>✈</span>
        <span>
          Depart <strong>08:15</strong> BOM
        </span>
      </div>
      <div className="obs-route-row">
        <span>◎</span>
        <span>
          Arrive <strong>10:20</strong> BLR
        </span>
      </div>
      <div className="obs-route-row">
        <span>⏱</span>
        <span>
          Duration <strong>2h 05m</strong>
        </span>
      </div>
      <div className="obs-route-row">
        <span>₹</span>
        <span>
          Est. Cost <strong>₹ 8,650</strong>
        </span>
      </div>
    </div>
  );
}

export function ObservationWindow({
  activeId,
  counselText,
  processing,
}: {
  activeId: GrahaId;
  counselText?: string;
  processing: boolean;
}) {
  const inst = instrumentByGraha(activeId) ?? instrumentByGraha("mangal")!;
  const isTravel = activeId === "mangal";
  const objective = counselText?.trim().slice(0, 200) || OBJECTIVES[activeId];

  return (
    <section className="obs-observation" aria-label="Observation window">
      <div className="obs-obs-title">
        OBSERVATION · {inst.name}
      </div>

      {isTravel ? (
        <div className="obs-obs-grid">
          <div>
            <div className="obs-obs-col-title">OBJECTIVE</div>
            <p className="obs-obs-objective">{objective}</p>
            <div className="obs-obs-status">
              <span className="obs-status-dot" />
              {processing ? "Computing route…" : STATUS_LABEL[activeId]}
            </div>
          </div>
          <div>
            <TravelMap />
          </div>
          <div>
            <RouteCard />
          </div>
        </div>
      ) : (
        <div className="obs-obs-grid">
          <div>
            <div className="obs-obs-col-title">OBJECTIVE</div>
            <p className="obs-obs-objective">{objective}</p>
            <div className="obs-obs-status">
              <span className="obs-status-dot" />
              {processing ? "Instrument active…" : STATUS_LABEL[activeId]}
            </div>
          </div>
          <div className="obs-preview-generic" style={{ gridColumn: "2 / -1" }}>
            {counselText?.trim() ||
              `Awaiting counsel from ${inst.name} (${inst.role}).\nAgent · ${inst.agentType} · standing by.`}
          </div>
        </div>
      )}
    </section>
  );
}
