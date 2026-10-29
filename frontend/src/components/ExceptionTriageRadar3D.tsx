import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface ExceptionTriageRadar3DProps {
  exceptionCounts: Record<string, number>;
  onSelectCategory?: (category: string) => void;
}

export const ExceptionTriageRadar3D: React.FC<ExceptionTriageRadar3DProps> = ({
  exceptionCounts,
  onSelectCategory,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = 300;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x090d16);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 18, 30);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Dynamic 3D Radar Concentric Rings
    const ringsGroup = new THREE.Group();
    scene.add(ringsGroup);

    [4, 8, 12, 16].forEach((radius, idx) => {
      const ringGeo = new THREE.RingGeometry(radius - 0.05, radius + 0.05, 48);
      const ringMat = new THREE.MeshBasicMaterial({
        color: idx === 3 ? 0xf43f5e : 0x6366f1,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.25 - idx * 0.04,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      ringsGroup.add(ring);
    });

    // 3D Sweeping Radar Beacon Beam
    const sweepGeo = new THREE.ConeGeometry(16, 0.1, 32, 1, false, 0, Math.PI / 4);
    const sweepMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.18,
      side: THREE.DoubleSide,
    });
    const sweepCone = new THREE.Mesh(sweepGeo, sweepMat);
    sweepCone.rotation.x = Math.PI / 2;
    scene.add(sweepCone);

    // Data Pins Extruded in 3D
    const entries = Object.entries(exceptionCounts);
    const pinMeshes: THREE.Mesh[] = [];

    entries.forEach(([type, count], index) => {
      const angle = (index / (entries.length || 1)) * Math.PI * 2;
      const radius = 6 + (index % 3) * 3;
      const height = Math.min(count * 0.6 + 1.5, 14);

      // Cylinder pillar
      const cylGeo = new THREE.CylinderGeometry(0.4, 0.6, height, 16);
      const isCritical = type.toLowerCase().includes('currency') || type.toLowerCase().includes('fte');
      const pinColor = isCritical ? 0xf43f5e : 0xf59e0b;

      const cylMat = new THREE.MeshStandardMaterial({
        color: pinColor,
        emissive: pinColor,
        emissiveIntensity: 0.4,
        roughness: 0.3,
      });

      const pin = new THREE.Mesh(cylGeo, cylMat);
      const posX = Math.cos(angle) * radius;
      const posZ = Math.sin(angle) * radius;
      pin.position.set(posX, height / 2, posZ);
      pin.userData = { type, count };
      scene.add(pin);
      pinMeshes.push(pin);

      // Glowing beacon cap on top of pillar
      const capGeo = new THREE.SphereGeometry(0.7, 16, 16);
      const capMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const cap = new THREE.Mesh(capGeo, capMat);
      cap.position.set(posX, height + 0.4, posZ);
      scene.add(cap);
    });

    // Lighting
    const light = new THREE.PointLight(0x6366f1, 2, 60);
    light.position.set(0, 15, 0);
    scene.add(light);

    const ambLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambLight);

    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Sweep rotation
      sweepCone.rotation.z = -elapsed * 1.4;

      // Pulsing rings
      ringsGroup.rotation.y = elapsed * 0.08;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [exceptionCounts]);

  return (
    <div className="relative rounded-2xl overflow-hidden border border-rose-900/50 shadow-xl bg-slate-950 mb-6">
      <div className="absolute top-3 left-4 z-10 flex items-center space-x-2">
        <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
        <span className="text-xs font-semibold text-rose-300 font-mono tracking-wider uppercase">
          Exception Triage Radar & Spatial Data Quality Defect Scanner
        </span>
      </div>
      <div ref={mountRef} className="w-full h-[300px]" />
    </div>
  );
};
