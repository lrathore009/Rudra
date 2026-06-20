"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stars, Environment } from "@react-three/drei";
import { TrishulDamruPreview } from "./TrishulDamru3D";

export function LoginCosmos() {
  return (
    <div className="absolute inset-0">
      <Canvas gl={{ antialias: true }} camera={{ position: [0, 0.2, 5], fov: 55 }}>
        <color attach="background" args={["#030510"]} />
        <ambientLight intensity={0.25} />
        <Environment preset="night" environmentIntensity={0.4} />
        <Stars radius={80} depth={40} count={3000} factor={3} saturation={0} fade speed={0.5} />
        <TrishulDamruPreview scale={0.65} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.4} />
      </Canvas>
    </div>
  );
}
