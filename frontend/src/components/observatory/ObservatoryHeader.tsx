"use client";

function TrishulIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" aria-hidden>
      <path
        d="M12 2 L12 10 M12 10 L5 20 M12 10 L19 20 M12 8 L9 4 M12 8 L15 4"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function ObservatoryHeader({ onLogout }: { onLogout: () => void }) {
  return (
    <header className="obs-header">
      <div className="obs-brand">
        <TrishulIcon className="obs-brand-icon" />
        <div>
          <div className="obs-brand-title">RUDRA AI</div>
          <div className="obs-brand-sub">NINE AGENTS · ONE PURPOSE</div>
        </div>
      </div>

      <h1 className="obs-title">OBSERVATORY NINE</h1>

      <div className="obs-header-right">
        <div className="obs-mode">
          <span>MODE</span>
          <span className="obs-mode-val">OBSERVATION</span>
        </div>
        <button type="button" className="obs-reticle-btn" title="Exit" onClick={onLogout} aria-label="Exit">
          <svg viewBox="0 0 16 16" width="12" height="12" fill="none" aria-hidden>
            <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1" />
            <line x1="8" y1="2" x2="8" y2="14" stroke="currentColor" strokeWidth="0.75" />
            <line x1="2" y1="8" x2="14" y2="8" stroke="currentColor" strokeWidth="0.75" />
            <circle cx="8" cy="8" r="1.5" fill="currentColor" />
          </svg>
        </button>
      </div>
    </header>
  );
}
