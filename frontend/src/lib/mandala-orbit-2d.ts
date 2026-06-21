/** 2D projection of inclined Navagraha orbits for the flat mandala SVG */

const CX = 500;
const CY = 380;
const SCALE = 13.5;

export function mandalaCenter() {
  return { cx: CX, cy: CY };
}

export function mandalaEllipseParams(graha: {
  orbitRadiusX: number;
  orbitRadiusZ: number;
  orbitInclination: number;
  orbitAscending: number;
}) {
  const rx = graha.orbitRadiusX * SCALE * 0.92;
  const ry = graha.orbitRadiusZ * SCALE * 1.05;
  return { rx, ry, rotation: graha.orbitAscending + graha.orbitInclination * 0.35 };
}

export function mandalaPoint2D(
  graha: {
    orbitRadiusX: number;
    orbitRadiusZ: number;
    orbitInclination: number;
    orbitLift: number;
  },
  theta: number
): { x: number; y: number } {
  const rx = graha.orbitRadiusX * SCALE;
  const ry = graha.orbitRadiusZ * SCALE;
  let x = Math.cos(theta) * rx;
  let y = Math.sin(theta) * ry;
  const inc = (graha.orbitInclination * Math.PI) / 180;
  const xr = x * Math.cos(inc) - y * Math.sin(inc);
  const yr = x * Math.sin(inc) + y * Math.cos(inc);
  return {
    x: CX + xr,
    y: CY + yr + graha.orbitLift * 4,
  };
}
