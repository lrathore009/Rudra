"use client";

import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { Environment, OrbitControls, Stars } from "@react-three/drei";
import { TrishulDamru3D } from "./TrishulDamru3D";
import { RudraPlatform } from "./RudraPlatform";

/** Full-screen 3D login — golden Trishula only, no PNG */
export function LoginCosmos() {
  return (
    <div className="absolute inset-0 bg-[#030308]">
      <Canvas gl={{ antialias: true }} camera={{ position: [0, 0.5, 7], fov: 48 }} dpr={[1, 2]}>
        <Suspense fallback={null}>
          <color attach="background" args={["#030308"]} />
          <ambientLight intensity={0.25} color="#2a2040" />
          <directionalLight position={[3, 8, 6]} intensity={1.4} color="#ffeedd" />
          <pointLight position={[-3, 2, 4]} intensity={0.8} color="#8866cc" />
          <pointLight position={[0, -1, 3]} intensity={1.2} color="#4488ff" />
          <Environment preset="night" environmentIntensity={0.35} />
          <Stars radius={90} depth={50} count={4000} factor={2.5} saturation={0.15} fade speed={0.3} />
          <LoginNebula />
          <group scale={0.38} position={[0, -1.05, 0]}>
            <RudraPlatform reducedMotion={false} />
          </group>
          <group position={[0, 0.05, 0]}>
            <TrishulDamru3D phase="login" spinning={false} scale={1.05} reducedMotion={false} />
          </group>
          <OrbitControls
            enableZoom={false}
            enablePan={false}
            autoRotate
            autoRotateSpeed={0.35}
            minPolarAngle={Math.PI / 2.8}
            maxPolarAngle={Math.PI / 2.1}
          />
        </Suspense>
      </Canvas>
    </div>
  );
}

function LoginNebula() {
  return (
    <group>
      {[
        { pos: [-4, 1, -6] as const, color: "#6b3fa8", scale: 5 },
        { pos: [5, -1, -7] as const, color: "#1a4a9a", scale: 6 },
        { pos: [0, 2, -8] as const, color: "#9933aa", scale: 7 },
      ].map((b, i) => (
        <mesh key={i} position={b.pos}>
          <sphereGeometry args={[b.scale, 16, 16]} />
          <meshBasicMaterial color={b.color} transparent opacity={0.12} depthWrite={false} />
        </mesh>
      ))}
    </group>
  );
}
