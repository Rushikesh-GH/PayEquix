import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface ProposalFlowCylinder3DProps {
  statusCounts: {
    draft?: number;
    submitted?: number;
    approved?: number;
    rejected?: number;
    applied?: number;
  };
}

export const ProposalFlowCylinder3D: React.FC<ProposalFlowCylinder3DProps> = ({ statusCounts }) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = 260;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b0f19);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 10, 32);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const stages = [
      { key: 'draft', label: 'Draft', color: 0x94a3b8, count: statusCounts.draft || 0, x: -16 },
      { key: 'submitted', label: 'Submitted', color: 0x3b82f6, count: statusCounts.submitted || 0, x: -8 },
      { key: 'approved', label: 'Approved', color: 0x10b981, count: statusCounts.approved || 0, x: 0 },
      { key: 'applied', label: 'Applied', color: 0x6366f1, count: statusCounts.applied || 0, x: 8 },
      { key: 'rejected', label: 'Rejected', color: 0xef4444, count: statusCounts.rejected || 0, x: 16 },
    ];

    const group = new THREE.Group();
    scene.add(group);

    // Connecting 3D pipeline rail
    const railGeo = new THREE.CylinderGeometry(0.15, 0.15, 34, 16);
    const railMat = new THREE.MeshBasicMaterial({ color: 0x334155 });
    const rail = new THREE.Mesh(railGeo, railMat);
    rail.rotation.z = Math.PI / 2;
    group.add(rail);

    stages.forEach((stg) => {
      // 3D stage ring
      const ringGeo = new THREE.TorusGeometry(3.2, 0.35, 16, 48);
      const ringMat = new THREE.MeshStandardMaterial({
        color: stg.color,
        emissive: stg.color,
        emissiveIntensity: 0.4,
        roughness: 0.2,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.position.x = stg.x;
      group.add(ring);

      // Inner pulsating core sphere representing proposal volume
      const sphereRadius = THREE.MathUtils.clamp((stg.count || 1) * 0.4 + 1.0, 1.2, 2.8);
      const sphereGeo = new THREE.SphereGeometry(sphereRadius, 24, 24);
      const sphereMat = new THREE.MeshStandardMaterial({
        color: stg.color,
        wireframe: true,
        transparent: true,
        opacity: 0.8,
      });
      const sphere = new THREE.Mesh(sphereGeo, sphereMat);
      sphere.position.x = stg.x;
      group.add(sphere);
    });

    // Ambient and directional lighting
    const ambLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);

    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Gentle wave float
      group.rotation.y = Math.sin(elapsed * 0.4) * 0.25;
      group.position.y = Math.sin(elapsed * 1.2) * 0.6;

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
  }, [statusCounts]);

  return (
    <div className="relative rounded-2xl overflow-hidden border border-indigo-900/50 shadow-xl bg-slate-950 mb-6">
      <div className="absolute top-3 left-4 z-10 flex items-center space-x-2">
        <span className="w-2.5 h-2.5 rounded-full bg-indigo-400 animate-ping" />
        <span className="text-xs font-semibold text-indigo-300 font-mono tracking-wider uppercase">
          Review Proposal Pipeline Lifecycle (Draft ➔ Review ➔ Approved ➔ Applied)
        </span>
      </div>
      <div ref={mountRef} className="w-full h-[260px]" />
    </div>
  );
};
