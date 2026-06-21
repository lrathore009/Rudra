"use client";

import type { GrahaId } from "@/components/cosmos/navagraha-types";
import {
  OBSERVATORY_INSTRUMENTS,
  dialNodePosition,
  type ObservatoryInstrument,
} from "./observatory-config";

const CX = 250;
const CY = 250;
const R = 175;
const NODE_R = 28;

function TrishulReticle() {
  return (
    <g aria-hidden>
      <circle cx={CX} cy={CY} r="22" fill="none" stroke="rgba(0,188,212,0.35)" strokeWidth="1" />
      <circle cx={CX} cy={CY} r="12" fill="none" stroke="rgba(0,188,212,0.25)" strokeWidth="0.75" />
      <path
        d={`M${CX} ${CY - 16} L${CX} ${CY + 2} M${CX} ${CY + 2} L${CX - 10} ${CY + 14} M${CX} ${CY + 2} L${CX + 10} ${CY + 14}`}
        stroke="#00bcd4"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      <text x={CX} y={CY + 32} textAnchor="middle" className="obs-dial-center-label">
        RUDRA TRISHUL
      </text>
      <text x={CX} y={CY + 42} textAnchor="middle" className="obs-dial-center-label">
        COMMAND RETICLE
      </text>
    </g>
  );
}

function DialNode({
  inst,
  index,
  active,
  onSelect,
}: {
  inst: ObservatoryInstrument;
  index: number;
  active: boolean;
  onSelect: (id: GrahaId) => void;
}) {
  const { x, y } = dialNodePosition(index, CX, CY, R);
  const labelY = y + NODE_R + 14;

  return (
    <g className="obs-dial-node" onClick={() => onSelect(inst.id)} role="button" tabIndex={0}>
      <circle
        cx={x}
        cy={y}
        r={NODE_R + 4}
        className={active ? "obs-dial-node-ring obs-dial-node-ring-active" : "obs-dial-node-ring"}
      />
      {inst.texture ? (
        <>
          <defs>
            <clipPath id={`clip-${inst.id}`}>
              <circle cx={x} cy={y} r={NODE_R - 2} />
            </clipPath>
          </defs>
          <image
            href={inst.texture}
            x={x - NODE_R + 2}
            y={y - NODE_R + 2}
            width={(NODE_R - 2) * 2}
            height={(NODE_R - 2) * 2}
            clipPath={`url(#clip-${inst.id})`}
            preserveAspectRatio="xMidYMid slice"
          />
          <circle cx={x} cy={y} r={NODE_R - 2} className="obs-dial-planet" fill="none" />
        </>
      ) : (
        <circle cx={x} cy={y} r={NODE_R - 2} fill={inst.nodeColor} opacity={0.85} className="obs-dial-planet" />
      )}
      <text x={x} y={labelY - 8} textAnchor="middle" className="obs-dial-label-num">
        {inst.num}
      </text>
      <text x={x} y={labelY + 2} textAnchor="middle" className="obs-dial-label-name">
        {inst.name}
      </text>
      <text x={x} y={labelY + 12} textAnchor="middle" className="obs-dial-label-role">
        {inst.role}
      </text>
    </g>
  );
}

export function InstrumentDial({
  activeId,
  onSelect,
}: {
  activeId: GrahaId;
  onSelect: (id: GrahaId) => void;
}) {
  return (
    <div className="obs-center">
      <div className="obs-dial-wrap">
        <svg className="obs-dial-svg" viewBox="0 0 500 500" aria-label="Nine instrument dial">
          {[R + 35, R + 12, R - 12].map((radius, i) => (
            <circle
              key={radius}
              cx={CX}
              cy={CY}
              r={radius}
              className={i === 0 ? "obs-dial-ring obs-dial-ring-outer" : "obs-dial-ring"}
            />
          ))}

          {OBSERVATORY_INSTRUMENTS.map((_, i) => {
            const p = dialNodePosition(i, CX, CY, R);
            return (
              <line key={`spoke-${i}`} x1={CX} y1={CY} x2={p.x} y2={p.y} className="obs-dial-spoke" />
            );
          })}

          {OBSERVATORY_INSTRUMENTS.map((inst, i) => {
            const p = dialNodePosition(i, CX, CY, R);
            const next = dialNodePosition((i + 1) % 9, CX, CY, R);
            return (
              <line
                key={`arc-${inst.id}`}
                x1={p.x}
                y1={p.y}
                x2={next.x}
                y2={next.y}
                stroke="rgba(0,188,212,0.15)"
                strokeWidth="0.75"
              />
            );
          })}

          <TrishulReticle />

          {OBSERVATORY_INSTRUMENTS.map((inst, i) => (
            <DialNode
              key={inst.id}
              inst={inst}
              index={i}
              active={activeId === inst.id}
              onSelect={onSelect}
            />
          ))}
        </svg>
      </div>
    </div>
  );
}
