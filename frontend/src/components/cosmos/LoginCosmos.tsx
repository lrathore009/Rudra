"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import { Float } from "@react-three/drei";

function MiniTrishul() {
  return (
    <Float speed={1.5} floatIntensity={0.4}>
      <group rotation={[0.3, 0.5, 0]}>
        <mesh>
          <cylinderGeometry args={[0.06, 0.09, 1.6, 8]} />
          <meshStandardMaterial color="#a0eeff" emissive="#22ccff" emissiveIntensity={0.8} metalness={0.9} roughness={0.2} />
        </mesh>
        {[0, (2 * Math.PI) / 3, (4 * Math.PI) / 3].map((rot) => (
          <group key={rot} rotation={[0.3, rot, 0]}>
            <mesh position={[0, 0.9, 0]}>
              <coneGeometry args={[0.1, 0.7, 8]} />
              <meshStandardMaterial color="#c8f8ff" emissive="#44ddff" emissiveIntensity={1} metalness={0.95} roughness={0.15} />
            </mesh>
          </group>
        ))}
        <pointLight color="#44eeff" intensity={1.2} distance={6} />
      </group>
    </Float>
  );
}

export function LoginCosmos() {
  return (
    <div className="absolute inset-0">
      <Canvas gl={{ antialias: true }} camera={{ position: [0, 0, 6], fov: 60 }}>
        <color attach="background" args={["#030510"]} />
        <ambientLight intensity={0.2} />
        <Stars radius={80} depth={40} count={3000} factor={3} saturation={0} fade speed={0.5} />
        <MiniTrishul />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.4} />
      </Canvas>
    </div>
  );
}
