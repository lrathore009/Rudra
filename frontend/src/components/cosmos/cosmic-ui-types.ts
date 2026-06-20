import type { RudraThemeMode } from "@/lib/rudra-theme";
import type { RealmId } from "@/components/tablet/RealmRim";
import type { GrahaId } from "./navagraha-config";

export interface CosmicUI3DProps {
  themeMode: RudraThemeMode;
  onThemeCycle: () => void;
  status: string;
  clock: Date | null;
  onLogout: () => void;
  muted: boolean;
  onToggleMute: () => void;
  tickerIdx: number;
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  onVoice: () => void;
  listening: boolean;
  processing: boolean;
  placeholder: string;
  voiceHint?: string | null;
  leadGrahaName?: string;
  supportingGrahaNames?: string[];
  activeRealm: RealmId | null;
  onRealmChange: (r: RealmId | null) => void;
  uplinkActive?: boolean;
  memorySynced?: boolean;
  counselText?: string;
  showCounsel?: boolean;
  leadGrahaId?: GrahaId;
  supportingGrahaIds?: GrahaId[];
  pulseGrahaIds?: GrahaId[];
}
