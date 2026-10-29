import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface BandTunnel3DProps {
  compaRatio: number;
  bandPosition: number;
  minSalary: number;
  midSalary: number;
  maxSalary: number;
  actualSalary: number;
  currency: string;
}

export const BandTunnel3D: React.FC<BandTunnel3DProps> = ({
  compaRatio,
  bandPosition,
  minSalary,
  midSalary,
  maxSalary,
  actualSalary,
  currency,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight || 260;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 5, 20);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Ambient & Directional Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const mainLight = new THREE.PointLight(0x6366f1, 3, 50);
    mainLight.position.set(10, 10, 10);
    scene.add(mainLight);

    const tunnelGroup = new THREE.Group();
    scene.add(tunnelGroup);

    // 1. Layered Band Ring Markers
    const createMarkerRing = (xPos: number, radius: number, color: number, label: string) => {
      const ringGeo = new THREE.TorusGeometry(radius, 0.12, 16, 64);
      const ringMat = new THREE.MeshStandardMaterial({
        color,
        emissive: color,
        emissiveIntensity: 0.6,
        metalness: 0.5,
        roughness: 0.2,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.y = Math.PI / 2;
      ring.position.x = xPos;
      tunnelGroup.add(ring);

      // Inner disc
      const discGeo = new THREE.CircleGeometry(radius, 32);
      const discMat = new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity: 0.08,
        side: THREE.DoubleSide,
      });
      const disc = new THREE.Mesh(discGeo, discMat);
      disc.rotation.y = Math.PI / 2;
      disc.position.x = xPos;
      tunnelGroup.add(disc);
    };

    // Tunnel bounds: Min at x = -6, Mid at x = 0, Max at x = 6
    createMarkerRing(-6, 3.5, 0x06b6d4, 'Min');
    createMarkerRing(0, 3.8, 0x6366f1, 'Mid');
    createMarkerRing(6, 3.5, 0xf59e0b, 'Max');

    // 2. Connecting Longitudinal Rails
    const railMat = new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.4 });
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const points = [
        new THREE.Vector3(-9, 3.5 * Math.sin(angle), 3.5 * Math.cos(angle)),
        new THREE.Vector3(9, 3.5 * Math.sin(angle), 3.5 * Math.cos(angle)),
      ];
      const railGeo = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(railGeo, railMat);
      tunnelGroup.add(line);
    }

    // 3. Employee Position Sphere in 3D
    // Map bandPosition (0% to 100%) to x from -6 to +6
    const mappedX = -6 + ((bandPosition || 50) / 100) * 12;
    const clampedX = Math.max(-9, Math.min(9, mappedX));

    const isBelow = bandPosition < 0;
    const isAbove = bandPosition > 100;
    const empColor = isBelow ? 0xf43f5e : isAbove ? 0xfbbf24 : 0x10b981;

    // Glowing Sphere
    const empGeo = new THREE.SphereGeometry(0.85, 32, 32);
    const empMat = new THREE.MeshStandardMaterial({
      color: empColor,
      emissive: empColor,
      emissiveIntensity: 1.0,
      metalness: 0.3,
      roughness: 0.2,
    });
    const empMesh = new THREE.Mesh(empGeo, empMat);
    empMesh.position.set(clampedX, 0, 0);
    tunnelGroup.add(empMesh);

    // Orbiting halo around employee position
    const haloGeo = new THREE.RingGeometry(1.2, 1.35, 32);
    const haloMat = new THREE.MeshBasicMaterial({
      color: empColor,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.7,
    });
    const haloMesh = new THREE.Mesh(haloGeo, haloMat);
    haloMesh.rotation.y = Math.PI / 2;
    haloMesh.position.set(clampedX, 0, 0);
    tunnelGroup.add(haloMesh);

    // Animation Loop
    let reqId: number;
    let clock = 0;
    const animate = () => {
      reqId = requestAnimationFrame(animate);
      clock += 0.02;

      tunnelGroup.rotation.y = Math.sin(clock * 0.5) * 0.25;
      tunnelGroup.rotation.x = Math.cos(clock * 0.4) * 0.12;

      haloMesh.scale.setScalar(1 + Math.sin(clock * 3) * 0.12);
      empMesh.scale.setScalar(1 + Math.cos(clock * 3) * 0.08);

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(reqId);
      renderer.dispose();
      scene.clear();
    };
  }, [bandPosition]);

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 border border-indigo-500/30 p-4 shadow-xl">
      <div className="flex items-center justify-between pb-2 border-b border-indigo-500/20 text-xs font-mono">
        <span className="font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Salary Band Spatial Alignment Horizon</span>
        </span>
        <span className="text-cyan-300 font-bold">Position: {bandPosition.toFixed(1)}%</span>
      </div>

      <div className="relative h-56 w-full">
        <div ref={mountRef} className="w-full h-full" />

        {/* Legend Overlay */}
        <div className="absolute bottom-2 left-4 right-4 flex items-center justify-between text-[11px] font-mono text-slate-300 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700">
          <div className="text-cyan-400 font-semibold">Min: ${minSalary?.toLocaleString()}</div>
          <div className="text-indigo-300 font-bold">Midpoint: ${midSalary?.toLocaleString()}</div>
          <div className="text-amber-400 font-semibold">Max: ${maxSalary?.toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
};
