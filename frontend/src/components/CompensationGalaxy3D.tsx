import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Sparkles, Eye, RotateCw, Layers, Compass } from 'lucide-react';

interface CompensationGalaxyProps {
  metrics: {
    total_employees: number;
    review_candidates_count: number;
    data_quality_exceptions_count: number;
    below_band_count: number;
    above_band_count: number;
    avg_compa_ratio?: number;
  };
  onSelectAnomaly?: (type: string) => void;
}

export const CompensationGalaxy3D: React.FC<CompensationGalaxyProps> = ({
  metrics,
  onSelectAnomaly,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<{
    id: string;
    type: string;
    salary: string;
    cr: string;
    pos: string;
  } | null>(null);
  const [viewMode, setViewMode] = useState<'galaxy' | 'terrain' | 'bands'>('galaxy');
  const [isRotating, setIsRotating] = useState(true);

  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const animationFrameId = useRef<number | null>(null);
  const nodesGroupRef = useRef<THREE.Group | null>(null);
  const bandsGroupRef = useRef<THREE.Group | null>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight || 360;

    // 1. Scene & Camera
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.fog = new THREE.FogExp2(0x090d16, 0.015);

    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    camera.position.set(0, 22, 45);
    camera.lookAt(0, 0, 0);

    // 2. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0x6366f1, 3, 100);
    pointLight1.position.set(20, 20, 20);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x10b981, 2.5, 100);
    pointLight2.position.set(-25, -10, -15);
    scene.add(pointLight2);

    const coreLight = new THREE.PointLight(0xf43f5e, 2, 50);
    coreLight.position.set(0, 0, 0);
    scene.add(coreLight);

    // 4. Central Holographic Core (3D Gyroscope/Icosahedron)
    const coreGeo = new THREE.IcosahedronGeometry(3.5, 1);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0x4f46e5,
      wireframe: true,
      emissive: 0x312e81,
      emissiveIntensity: 0.8,
      transparent: true,
      opacity: 0.45,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    scene.add(coreMesh);

    // 5. 3D Band Horizon Planes (Min, Midpoint, Max)
    const bandsGroup = new THREE.Group();
    bandsGroupRef.current = bandsGroup;
    scene.add(bandsGroup);

    const gridHelper = new THREE.GridHelper(50, 24, 0x6366f1, 0x1e293b);
    gridHelper.position.y = -6; // Band Min floor
    bandsGroup.add(gridHelper);

    const midGrid = new THREE.GridHelper(50, 24, 0x38bdf8, 0x0f172a);
    midGrid.position.y = 0; // Midpoint benchmark plane
    bandsGroup.add(midGrid);

    const topGrid = new THREE.GridHelper(50, 24, 0xf59e0b, 0x1e293b);
    topGrid.position.y = 6; // Band Max ceiling
    bandsGroup.add(topGrid);

    // Floating 3D orbital rings
    const ringGeo = new THREE.RingGeometry(18, 18.3, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x6366f1,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.25,
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 2;
    scene.add(ringMesh);

    // 6. Dynamic Employee 3D Spatial Nodes
    const nodesGroup = new THREE.Group();
    nodesGroupRef.current = nodesGroup;
    scene.add(nodesGroup);

    // Node categories: In-Band (emerald), Below-Band (ruby), Above-Band (amber), Data-Quality (magenta)
    const totalSample = 320;
    const belowRatio = 0.08;
    const aboveRatio = 0.12;
    const dqRatio = 0.03;

    const sphereGeo = new THREE.SphereGeometry(0.45, 16, 16);
    const glowGeo = new THREE.SphereGeometry(0.7, 12, 12);

    const matInBand = new THREE.MeshStandardMaterial({
      color: 0x10b981,
      emissive: 0x047857,
      emissiveIntensity: 0.4,
      metalness: 0.2,
      roughness: 0.3,
    });

    const matBelow = new THREE.MeshStandardMaterial({
      color: 0xf43f5e,
      emissive: 0xe11d48,
      emissiveIntensity: 0.9,
      metalness: 0.4,
      roughness: 0.2,
    });

    const matAbove = new THREE.MeshStandardMaterial({
      color: 0xfbbf24,
      emissive: 0xd97706,
      emissiveIntensity: 0.8,
      metalness: 0.3,
      roughness: 0.3,
    });

    const matDQ = new THREE.MeshStandardMaterial({
      color: 0xd946ef,
      emissive: 0xa21caf,
      emissiveIntensity: 1.0,
      metalness: 0.5,
      roughness: 0.2,
    });

    const nodeMeshes: THREE.Mesh[] = [];

    for (let i = 0; i < totalSample; i++) {
      let mat = matInBand;
      let yPos = (Math.random() - 0.5) * 8; // near midpoint
      let type = 'IN_BAND';
      let cr = (0.9 + Math.random() * 0.2).toFixed(2);
      let pos = `${(25 + Math.random() * 50).toFixed(0)}%`;

      const rand = Math.random();
      if (rand < belowRatio) {
        mat = matBelow;
        yPos = -7.5 - Math.random() * 3.5; // strictly below minimum plane
        type = 'BELOW_BAND_MINIMUM';
        cr = (0.65 + Math.random() * 0.14).toFixed(2);
        pos = `-${(5 + Math.random() * 30).toFixed(0)}%`;
      } else if (rand < belowRatio + aboveRatio) {
        mat = matAbove;
        yPos = 7.5 + Math.random() * 4.0; // strictly above maximum plane
        type = 'ABOVE_BAND_MAXIMUM';
        cr = (1.22 + Math.random() * 0.25).toFixed(2);
        pos = `${(105 + Math.random() * 35).toFixed(0)}%`;
      } else if (rand < belowRatio + aboveRatio + dqRatio) {
        mat = matDQ;
        yPos = (Math.random() - 0.5) * 14;
        type = 'DATA_QUALITY_EXCEPTION';
        cr = 'N/A';
        pos = 'BLOCKED';
      }

      const nodeMesh = new THREE.Mesh(sphereGeo, mat);

      // Spherical orbital distribution
      const radius = 9 + Math.random() * 15;
      const theta = Math.random() * Math.PI * 2;
      const phi = (Math.random() - 0.5) * Math.PI;

      nodeMesh.position.x = radius * Math.cos(theta) * Math.cos(phi);
      nodeMesh.position.y = yPos;
      nodeMesh.position.z = radius * Math.sin(theta) * Math.cos(phi);

      nodeMesh.userData = {
        id: `EMP-${String(i + 1).padStart(6, '0')}`,
        type,
        salary: `$${(70000 + Math.random() * 110000).toFixed(0)}`,
        cr,
        pos,
      };

      nodesGroup.add(nodeMesh);
      nodeMeshes.push(nodeMesh);
    }

    // 7. Raycasting for Mouse Interaction
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeMeshes);

      if (intersects.length > 0) {
        const hit = intersects[0].object as THREE.Mesh;
        setHoveredNode(hit.userData as any);
      } else {
        setHoveredNode(null);
      }
    };

    container.addEventListener('mousemove', handleMouseMove);

    // 8. Animation Loop
    let angle = 0;
    const animate = () => {
      animationFrameId.current = requestAnimationFrame(animate);

      if (isRotating) {
        angle += 0.0035;
        nodesGroup.rotation.y = angle;
        coreMesh.rotation.y -= 0.006;
        coreMesh.rotation.x += 0.004;
      }

      // Floating wave animation on nodes
      const time = Date.now() * 0.0015;
      coreMesh.scale.setScalar(1 + Math.sin(time * 2) * 0.06);

      renderer.render(scene, camera);
    };

    animate();

    // 9. Resize Handling
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 360;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      if (animationFrameId.current) cancelAnimationFrame(animationFrameId.current);
      container.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      scene.clear();
    };
  }, [viewMode, isRotating]);

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 border border-indigo-500/30 p-5 shadow-2xl">
      {/* 3D Ambient Neon Glow Highlights */}
      <div className="absolute -top-24 -left-24 w-72 h-72 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-rose-600/15 rounded-full blur-3xl pointer-events-none" />

      {/* Top Controls Header */}
      <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-indigo-500/20">
        <div>
          <div className="flex items-center space-x-2">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
            </span>
            <h3 className="text-base font-bold text-white tracking-wide flex items-center space-x-2">
              <span>Interactive Workforce Compensation Landscape</span>
              <Sparkles className="w-4 h-4 text-indigo-400" />
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Spatial distribution of employees relative to effective-dated salary band minimum, midpoint, and maximum planes.
          </p>
        </div>

        {/* Action Pills */}
        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setIsRotating(!isRotating)}
            className={`px-3 py-1.5 rounded-lg border font-mono flex items-center space-x-1.5 transition-all ${
              isRotating
                ? 'bg-indigo-500/20 border-indigo-400/40 text-indigo-200'
                : 'bg-slate-800/60 border-slate-700 text-slate-400'
            }`}
          >
            <RotateCw className={`w-3.5 h-3.5 ${isRotating ? 'animate-spin' : ''}`} />
            <span>{isRotating ? 'Auto Orbit: ON' : 'Auto Orbit: PAUSED'}</span>
          </button>
        </div>
      </div>

      {/* 3D Canvas Viewport */}
      <div className="relative h-80 sm:h-96 w-full mt-2 cursor-grab active:cursor-grabbing">
        <div ref={mountRef} className="w-full h-full" />

        {/* 3D Horizon Level Legend */}
        <div className="absolute left-4 top-4 z-10 space-y-2 pointer-events-none bg-slate-900/80 backdrop-blur-md p-3 rounded-xl border border-indigo-500/20 text-[11px] font-mono">
          <div className="text-slate-400 font-bold uppercase tracking-wider text-[10px]">Spatial Band Horizons</div>
          <div className="flex items-center space-x-2 text-amber-300">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-sm shadow-amber-400/50" />
            <span>Upper Ceiling: Band Max (&gt; 100%)</span>
          </div>
          <div className="flex items-center space-x-2 text-cyan-300">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/50" />
            <span>Zero Plane: Band Midpoint (1.00)</span>
          </div>
          <div className="flex items-center space-x-2 text-rose-300">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500/50" />
            <span>Lower Floor: Band Min (&lt; 0%)</span>
          </div>
          <div className="flex items-center space-x-2 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
            <span>Normal Spread: In-Band (0–100%)</span>
          </div>
        </div>

        {/* Interactive Hover Tooltip */}
        {hoveredNode && (
          <div className="absolute right-4 top-4 z-20 bg-slate-900/95 backdrop-blur-md p-3.5 rounded-xl border border-indigo-400/40 text-xs shadow-2xl font-mono text-white pointer-events-none space-y-1.5 min-w-[210px] animate-fadeIn">
            <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
              <span className="font-bold text-indigo-400">{hoveredNode.id}</span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-sans font-bold ${
                  hoveredNode.type.includes('BELOW')
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    : hoveredNode.type.includes('ABOVE')
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                }`}
              >
                {hoveredNode.type.replace(/_/g, ' ')}
              </span>
            </div>
            <div className="flex justify-between text-slate-300 text-[11px]">
              <span>Sample Salary:</span>
              <span className="font-bold text-white">{hoveredNode.salary}</span>
            </div>
            <div className="flex justify-between text-slate-300 text-[11px]">
              <span>Compa-Ratio:</span>
              <span className="font-bold text-cyan-300">{hoveredNode.cr}</span>
            </div>
            <div className="flex justify-between text-slate-300 text-[11px]">
              <span>Within-Band Pos:</span>
              <span
                className={`font-bold ${
                  hoveredNode.pos.startsWith('-') ? 'text-rose-400' : 'text-emerald-400'
                }`}
              >
                {hoveredNode.pos}
              </span>
            </div>
          </div>
        )}

        {/* Bottom Floating Stats Pill */}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10 flex items-center space-x-4 bg-slate-900/85 backdrop-blur-md px-4 py-2 rounded-full border border-indigo-500/30 text-xs text-slate-300 shadow-xl font-mono">
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-400">Total Orbit Nodes:</span>
            <span className="text-white font-bold">{metrics.total_employees.toLocaleString()}</span>
          </div>
          <span className="text-slate-600">•</span>
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-400">Below Floor:</span>
            <span className="text-rose-400 font-bold">{metrics.below_band_count}</span>
          </div>
          <span className="text-slate-600">•</span>
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-400">Above Ceiling:</span>
            <span className="text-amber-400 font-bold">{metrics.above_band_count}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
