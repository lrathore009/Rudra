"use client";

import { CommandConsole3D } from "./CommandConsole3D";
import { CounselPlane3D } from "./CounselPlane3D";
import { GrahaRimLabels3D } from "./GrahaRimLabels3D";
import { RealmPedestals3D } from "./RealmPedestals3D";
import { SanctumChrome3D } from "./SanctumChrome3D";
import type { CosmicUI3DProps } from "./cosmic-ui-types";

export function CosmicUI3D(props: CosmicUI3DProps & { streamingActive?: boolean }) {
  return (
    <>
      <SanctumChrome3D
        themeMode={props.themeMode}
        onThemeCycle={props.onThemeCycle}
        status={props.status}
        clock={props.clock}
        onLogout={props.onLogout}
        muted={props.muted}
        onToggleMute={props.onToggleMute}
        tickerIdx={props.tickerIdx}
        uplinkActive={props.uplinkActive}
        memorySynced={props.memorySynced}
        leadGrahaName={props.leadGrahaName}
        supportingGrahaNames={props.supportingGrahaNames}
        processing={props.processing}
      />
      <GrahaRimLabels3D
        leadGrahaId={props.leadGrahaId}
        supportingGrahaIds={props.supportingGrahaIds}
        pulseGrahaIds={props.pulseGrahaIds}
        processing={props.processing}
      />
      <CounselPlane3D text={props.counselText ?? ""} visible={Boolean(props.showCounsel && props.counselText)} />
      <CommandConsole3D
        input={props.input}
        onInputChange={props.onInputChange}
        onSubmit={props.onSubmit}
        onStop={props.onStop}
        onVoice={props.onVoice}
        listening={props.listening}
        processing={props.processing}
        placeholder={props.placeholder}
        streamingActive={props.streamingActive}
      />
      <RealmPedestals3D activeRealm={props.activeRealm} onRealmChange={props.onRealmChange} />
    </>
  );
}
