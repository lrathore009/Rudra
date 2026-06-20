/** Inclined 3D orbital mechanics for Navagraha paths */
import * as THREE from "three";
import type { Navagraha } from "./navagraha-types";

const _v = new THREE.Vector3();
const X_AXIS = new THREE.Vector3(1, 0, 0);
const Y_AXIS = new THREE.Vector3(0, 1, 0);

/** Position on inclined ellipse at orbital angle θ (radians) */
export function grahaPosition3D(graha: Navagraha, theta: number): THREE.Vector3 {
  const x = Math.cos(theta) * graha.orbitRadiusX;
  const z = Math.sin(theta) * graha.orbitRadiusZ;
  _v.set(x, 0, z);

  const inc = THREE.MathUtils.degToRad(graha.orbitInclination);
  _v.applyAxisAngle(X_AXIS, inc);

  const asc = THREE.MathUtils.degToRad(graha.orbitAscending);
  _v.applyAxisAngle(Y_AXIS, asc);

  _v.y += graha.orbitLift + Math.sin(theta * 0.5) * 0.2;
  return _v.clone();
}

export function orbitPathPoints(graha: Navagraha, segments = 128): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  for (let i = 0; i <= segments; i++) {
    const theta = (i / segments) * Math.PI * 2;
    pts.push(grahaPosition3D(graha, theta));
  }
  return pts;
}

/** Inner sanctum rim plaque anchor — fixed in world space */
export function grahaRimLabelPosition(graha: Navagraha): THREE.Vector3 {
  const r = 9.4;
  const y = 0.8 + graha.orbitLift * 0.35;
  return new THREE.Vector3(Math.cos(graha.rimAngle) * r, y, Math.sin(graha.rimAngle) * r);
}

export function createOrbitTubeGeometry(graha: Navagraha, segments = 128, radius = 0.045): THREE.TubeGeometry {
  const points = orbitPathPoints(graha, segments);
  const curve = new THREE.CatmullRomCurve3(points, true, "catmullrom", 0.2);
  return new THREE.TubeGeometry(curve, segments, radius, 8, true);
}
