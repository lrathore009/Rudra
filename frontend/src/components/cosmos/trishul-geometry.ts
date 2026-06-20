/**
 * High-detail procedural Trishul + Damru geometry.
 * Flat double-edged blades (not round tubes) — authentic Shiva trident silhouette.
 */
import * as THREE from "three";

export const TRIDENT_METAL = {
  color: "#8af0ff",
  emissive: "#1a8899",
  emissiveIntensity: 0.75,
  metalness: 1,
  roughness: 0.1,
  clearcoat: 1,
  clearcoatRoughness: 0.08,
} as const;

export const TRIDENT_GOLD = {
  color: "#ffd878",
  emissive: "#aa7722",
  emissiveIntensity: 0.45,
  metalness: 1,
  roughness: 0.18,
  clearcoat: 0.9,
  clearcoatRoughness: 0.15,
} as const;

export const DAMRU_BODY = {
  color: "#c48828",
  emissive: "#664010",
  emissiveIntensity: 0.35,
  metalness: 0.85,
  roughness: 0.28,
} as const;

export const DAMRU_SKIN = {
  color: "#f2e6d0",
  emissive: "#886644",
  emissiveIntensity: 0.12,
  metalness: 0.05,
  roughness: 0.82,
} as const;

/** Leaf-shaped flat blade profile for extrusion */
function bladeProfile(maxHalfWidth: number, length: number): THREE.Shape {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.lineTo(maxHalfWidth * 0.35, length * 0.08);
  s.lineTo(maxHalfWidth, length * 0.22);
  s.lineTo(maxHalfWidth * 0.72, length * 0.55);
  s.lineTo(maxHalfWidth * 0.42, length * 0.82);
  s.lineTo(maxHalfWidth * 0.28, length);
  s.lineTo(-maxHalfWidth * 0.28, length);
  s.lineTo(-maxHalfWidth * 0.42, length * 0.82);
  s.lineTo(-maxHalfWidth * 0.72, length * 0.55);
  s.lineTo(-maxHalfWidth, length * 0.22);
  s.lineTo(-maxHalfWidth * 0.35, length * 0.08);
  s.closePath();
  return s;
}

/** Flat center blade — tallest, straight, spear-like */
export function createCenterBladeGeometry(): THREE.ExtrudeGeometry {
  const profile = bladeProfile(0.14, 1.55);
  const geo = new THREE.ExtrudeGeometry(profile, {
    depth: 0.022,
    bevelEnabled: true,
    bevelThickness: 0.004,
    bevelSize: 0.004,
    bevelSegments: 2,
  });
  geo.translate(0, 0, -0.011);
  geo.rotateX(-Math.PI / 2);
  return geo;
}

/** Sharp center blade tip — triangular wedge */
export function createCenterBladeTipGeometry(): THREE.BufferGeometry {
  const geo = new THREE.ConeGeometry(0.055, 0.42, 4, 1);
  geo.scale(1, 1, 0.18);
  return geo;
}

/** Curved side prong path — sweeps outward then upward (classic trishul horns) */
export function createSideProngCurve(side: 1 | -1): THREE.CatmullRomCurve3 {
  return new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(side * 0.1, 0.22, 0),
    new THREE.Vector3(side * 0.42, 0.48, 0.015),
    new THREE.Vector3(side * 0.52, 0.82, 0),
    new THREE.Vector3(side * 0.38, 1.15, -0.02),
    new THREE.Vector3(side * 0.18, 1.38, 0),
  ]);
}

/** Flat curved side blade extruded along prong path */
export function createSideBladeGeometry(side: 1 | -1): THREE.ExtrudeGeometry {
  const curve = createSideProngCurve(side);
  const profile = bladeProfile(0.09, 0.85);
  const geo = new THREE.ExtrudeGeometry(profile, {
    extrudePath: curve,
    steps: 48,
    depth: 0.018,
    bevelEnabled: true,
    bevelThickness: 0.003,
    bevelSize: 0.003,
    bevelSegments: 2,
  });
  return geo;
}

/** Ornate lathe-turned shaft with ring bands */
export function createShaftGeometry(): THREE.LatheGeometry {
  const pts: THREE.Vector2[] = [];
  const segments = 28;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const y = t * 2.6 - 1.15;
    const band = Math.sin(t * Math.PI * 14) * 0.008;
    const flare = t < 0.08 ? 0.04 * (1 - t / 0.08) : 0;
    const crown = t > 0.88 ? 0.035 * ((t - 0.88) / 0.12) : 0;
    const r = 0.055 + band + flare + crown;
    pts.push(new THREE.Vector2(Math.max(0.035, r), y));
  }
  return new THREE.LatheGeometry(pts, 48);
}

/** Prong crown — three-blade socket where prongs meet shaft */
export function createProngCrown(material: THREE.Material): THREE.Group {
  const g = new THREE.Group();
  const guard = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.1, 0.08, 6), material);
  guard.position.y = 0.04;
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.014, 8, 24), material);
  ring.rotation.x = Math.PI / 2;
  g.add(guard, ring);
  return g;
}

/** Central prong assembly — flat blade + wedge tip + crown */
export function createCenterProngGroup(material: THREE.Material): THREE.Group {
  const g = new THREE.Group();
  const blade = new THREE.Mesh(createCenterBladeGeometry(), material);
  blade.position.y = 0.78;
  const tip = new THREE.Mesh(createCenterBladeTipGeometry(), material);
  tip.position.y = 1.68;
  g.add(blade, tip, createProngCrown(material));
  return g;
}

/** Hourglass damaru with drum skins, waist cord, and bead strings */
export function createDamruGroup(materials: {
  body: THREE.Material;
  skin: THREE.Material;
  gold: THREE.Material;
  bead: THREE.Material;
}): THREE.Group {
  const g = new THREE.Group();

  const lower = new THREE.Mesh(new THREE.SphereGeometry(0.28, 32, 24, 0, Math.PI * 2, 0, Math.PI / 2), materials.skin);
  lower.rotation.x = Math.PI;
  lower.position.y = -0.14;

  const upper = new THREE.Mesh(new THREE.SphereGeometry(0.26, 32, 24, 0, Math.PI * 2, 0, Math.PI / 2), materials.skin);
  upper.position.y = 0.14;

  const waist = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.22, 24), materials.body);
  const waistRing = new THREE.Mesh(new THREE.TorusGeometry(0.13, 0.014, 8, 32), materials.gold);
  waistRing.rotation.x = Math.PI / 2;

  for (let i = 0; i < 4; i++) {
    const cord = new THREE.Mesh(new THREE.TorusGeometry(0.115, 0.006, 6, 32), materials.gold);
    cord.rotation.x = Math.PI / 2;
    cord.rotation.y = (i * Math.PI) / 4;
    g.add(cord);
  }

  for (let s = 0; s < 3; s++) {
    const angle = (s / 3) * Math.PI * 2;
    const stringCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(Math.cos(angle) * 0.12, 0.12, Math.sin(angle) * 0.12),
      new THREE.Vector3(Math.cos(angle) * 0.2, 0.35, Math.sin(angle) * 0.2),
      new THREE.Vector3(Math.cos(angle) * 0.08, 0.48, Math.sin(angle) * 0.08),
    ]);
    const stringMesh = new THREE.Mesh(new THREE.TubeGeometry(stringCurve, 12, 0.008, 6, false), materials.gold);
    const bead = new THREE.Mesh(new THREE.SphereGeometry(0.035, 12, 12), materials.bead);
    bead.position.set(Math.cos(angle) * 0.08, 0.5, Math.sin(angle) * 0.08);
    g.add(stringMesh, bead);
  }

  const loop = new THREE.Mesh(new THREE.TorusGeometry(0.05, 0.012, 8, 20), materials.gold);
  loop.position.y = 0.32;
  loop.rotation.x = Math.PI / 2;

  g.add(lower, upper, waist, waistRing, loop);
  return g;
}

/** Tripundra — three sacred ash lines */
export function createTripundra(material: THREE.Material): THREE.Group {
  const g = new THREE.Group();
  [-0.04, 0, 0.04].forEach((x) => {
    const line = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.012, 0.012), material);
    line.position.set(x, 0.38, 0.14);
    g.add(line);
  });
  return g;
}

/** Vertical third eye — lens + iris layers */
export function createThirdEye(openness: number, materials: { lens: THREE.Material; iris: THREE.Material }): THREE.Group {
  const g = new THREE.Group();
  const sy = 0.04 + openness * 0.5;
  const lens = new THREE.Mesh(new THREE.SphereGeometry(0.1, 24, 24), materials.lens);
  lens.scale.set(1, sy, 0.35);
  const iris = new THREE.Mesh(new THREE.SphereGeometry(0.045, 16, 16), materials.iris);
  iris.scale.set(1, sy * 0.8, 0.3);
  iris.position.z = 0.04;
  g.add(lens, iris);
  return g;
}

/** Decorative gold rings along shaft */
export function createShaftRings(material: THREE.Material): THREE.Group {
  const g = new THREE.Group();
  [0.15, 0.45, 0.75].forEach((y) => {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.075, 0.008, 8, 32), material);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = y;
    g.add(ring);
  });
  return g;
}

/** Rudraksha beads below damaru */
export function createBeadGarland(material: THREE.Material, count = 5): THREE.Group {
  const g = new THREE.Group();
  for (let i = 0; i < count; i++) {
    const bead = new THREE.Mesh(new THREE.SphereGeometry(0.028, 10, 10), material);
    const t = i / (count - 1);
    bead.position.set(Math.sin(t * Math.PI) * 0.08, -0.15 - t * 0.12, 0.06 + Math.cos(t * Math.PI) * 0.04);
    g.add(bead);
  }
  return g;
}
