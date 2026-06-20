/**
 * High-detail procedural Trishul + Damru geometry.
 * Authentic Shiva trident: tall centre blade, curved side prongs,
 * lathe-turned shaft, damaru with skin heads + bead strings.
 */
import * as THREE from "three";

export const TRIDENT_METAL = {
  color: "#ddb844",
  emissive: "#886622",
  emissiveIntensity: 0.55,
  metalness: 1,
  roughness: 0.14,
  clearcoat: 1,
  clearcoatRoughness: 0.1,
} as const;

export const TRIDENT_GOLD = {
  color: "#ffcc55",
  emissive: "#cc8822",
  emissiveIntensity: 0.6,
  metalness: 1,
  roughness: 0.12,
  clearcoat: 0.95,
  clearcoatRoughness: 0.1,
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

/** Ornate lathe-turned shaft with ring bands */
export function createShaftGeometry(): THREE.LatheGeometry {
  const pts: THREE.Vector2[] = [];
  const segments = 28;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const y = t * 2.6 - 1.15;
    const band = Math.sin(t * Math.PI * 14) * 0.008;
    const flare = t < 0.08 ? 0.04 * (1 - t / 0.08) : 0;
    const crown = t > 0.88 ? 0.025 * ((t - 0.88) / 0.12) : 0;
    const r = 0.055 + band + flare + crown;
    pts.push(new THREE.Vector2(Math.max(0.035, r), y));
  }
  return new THREE.LatheGeometry(pts, 48);
}

/** Curved side prong — sweeps outward then upward (classic trishul) */
export function createSideProngCurve(side: 1 | -1): THREE.CatmullRomCurve3 {
  return new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(side * 0.08, 0.25, 0),
    new THREE.Vector3(side * 0.35, 0.55, 0.02),
    new THREE.Vector3(side * 0.42, 0.95, 0),
    new THREE.Vector3(side * 0.28, 1.35, -0.02),
    new THREE.Vector3(side * 0.12, 1.55, 0),
  ]);
}

export function createProngTube(curve: THREE.Curve<THREE.Vector3>, radius = 0.055): THREE.TubeGeometry {
  return new THREE.TubeGeometry(curve, 40, radius, 12, false);
}

/** Central prong — straight, tallest blade with tapered tip */
export function createCenterProngGroup(material: THREE.Material): THREE.Group {
  const g = new THREE.Group();
  const blade = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.07, 1.05, 12), material);
  blade.position.y = 0.52;
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.35, 12), material);
  tip.position.y = 1.22;
  const guard = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.018, 8, 24), material);
  guard.rotation.x = Math.PI / 2;
  guard.position.y = 0.05;
  g.add(blade, tip, guard);
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
  // orange tassel
  const tassel = new THREE.Mesh(
    new THREE.CylinderGeometry(0.012, 0.02, 0.14, 8),
    new THREE.MeshStandardMaterial({ color: "#ee6622", emissive: "#cc4400", emissiveIntensity: 0.4, roughness: 0.7 })
  );
  tassel.position.set(0.06, -0.38, 0.08);
  g.add(tassel);
  return g;
}

/** ॐ decal for damaru — canvas texture, no external font */
export function createOmTexture(): THREE.CanvasTexture {
  const size = 256;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, size, size);
  ctx.fillStyle = "#ffdd88";
  ctx.font = "bold 180px serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.shadowColor = "#cc8822";
  ctx.shadowBlur = 12;
  ctx.fillText("ॐ", size / 2, size / 2 + 8);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createOmDecal(material?: THREE.Material): THREE.Mesh {
  const tex = createOmTexture();
  const mat =
    material ??
    new THREE.MeshStandardMaterial({
      map: tex,
      transparent: true,
      opacity: 0.95,
      emissive: "#cc8822",
      emissiveIntensity: 0.35,
      metalness: 0.2,
      roughness: 0.4,
      depthWrite: false,
    });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.22), mat);
  mesh.position.set(0.26, 0.08, 0.29);
  mesh.rotation.y = 0.35;
  return mesh;
}
