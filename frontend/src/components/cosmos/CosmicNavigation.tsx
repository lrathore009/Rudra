"use client";

import { useImperativeHandle, useMemo, useRef, type Ref } from "react";
import { OrbitControls } from "@react-three/drei";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import * as THREE from "three";
import {
  COSMIC_DEFAULT_TARGET,
  cosmicDefaultCamera,
  type CosmicNavHandle,
} from "./cosmic-nav-types";

export function CosmicNavigation({
  variant = "main",
  navRef,
}: {
  variant?: "main" | "login";
  navRef?: Ref<CosmicNavHandle | null>;
}) {
  const controlsRef = useRef<OrbitControlsImpl>(null);
  const defaultCamPos = useMemo(
    () => new THREE.Vector3(...cosmicDefaultCamera(variant)),
    [variant]
  );
  const defaultTarget = useMemo(() => new THREE.Vector3(...COSMIC_DEFAULT_TARGET), []);

  useImperativeHandle(
    navRef,
    () => ({
      resetView() {
        const ctrl = controlsRef.current;
        if (!ctrl) return;
        const cam = ctrl.object as THREE.PerspectiveCamera;
        cam.position.copy(defaultCamPos);
        ctrl.target.copy(defaultTarget);
        ctrl.update();
      },
      zoomIn() {
        controlsRef.current?.dollyIn(1.2);
        controlsRef.current?.update();
      },
      zoomOut() {
        controlsRef.current?.dollyOut(1.2);
        controlsRef.current?.update();
      },
    }),
    [defaultCamPos, defaultTarget]
  );

  return (
    <OrbitControls
      ref={controlsRef}
      makeDefault
      target={COSMIC_DEFAULT_TARGET}
      enableRotate
      enableZoom
      enablePan
      minDistance={5}
      maxDistance={58}
      minPolarAngle={0.06}
      maxPolarAngle={Math.PI - 0.06}
      minAzimuthAngle={-Infinity}
      maxAzimuthAngle={Infinity}
      enableDamping
      dampingFactor={0.065}
      rotateSpeed={0.75}
      zoomSpeed={1.05}
      panSpeed={0.72}
      screenSpacePanning
      mouseButtons={{
        LEFT: THREE.MOUSE.ROTATE,
        MIDDLE: THREE.MOUSE.DOLLY,
        RIGHT: THREE.MOUSE.PAN,
      }}
      touches={{
        ONE: THREE.TOUCH.ROTATE,
        TWO: THREE.TOUCH.DOLLY_PAN,
      }}
    />
  );
}
