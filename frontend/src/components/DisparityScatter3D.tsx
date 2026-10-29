import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface DisparityScatter3DProps {
  groups?: Array<{
    group_id: string;
    group_name: string;
    headcount: number;
    avg_compa_ratio: number;
    median_fte_salary: number;
    spread: number;
  }>;
  onSelectGroup?: (groupId: string) => void;
}

export const DisparityScatter3D: React.FC<DisparityScatter3DProps> = ({
  groups = [],
  onSelectGroup,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = 340;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a); // Deep slate space background
    scene.fog = new THREE.FogExp2(0x0f172a, 0.008);

    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    camera.position.set(0, 35, 75);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Coordinate Planes & Floor Grid
    const gridHelper = new THREE.GridHelper(80, 20, 0x6366f1, 0x1e293b);
    gridHelper.position.y = -15;
    scene.add(gridHelper);

    // Benchmark Midpoint Target Plane (Compa-Ratio = 1.00)
    const midPlaneGeo = new THREE.PlaneGeometry(80, 80);
    const midPlaneMat = new THREE.MeshBasicMaterial({
      color: 0x10b981,
      wireframe: true,
      transparent: true,
      opacity: 0.12,
    });
    const midPlane = new THREE.Mesh(midPlaneGeo, midPlaneMat);
    midPlane.rotation.x = -Math.PI / 2;
    midPlane.position.y = 0; // Baseline Y = 0 represents Compa-Ratio 1.0
    scene.add(midPlane);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x60a5fa, 1.5);
    dirLight.position.set(20, 40, 30);
    scene.add(dirLight);

    // Generate 3D Spheres for groups (or realistic clusters if groups empty)
    const sampleGroups = groups.length > 0 ? groups : [
      { group_id: 'GRP-ENG-SR', group_name: 'Senior Software Engineer (SF)', headcount: 48, avg_compa_ratio: 0.98, median_fte_salary: 165000, spread: 0.18 },
      { group_id: 'GRP-ENG-STF', group_name: 'Staff Software Engineer (NY)', headcount: 22, avg_compa_ratio: 1.08, median_fte_salary: 215000, spread: 0.14 },
      { group_id: 'GRP-PM-L4', group_name: 'Product Manager III (London)', headcount: 34, avg_compa_ratio: 0.92, median_fte_salary: 135000, spread: 0.22 },
      { group_id: 'GRP-DS-L5', group_name: 'Lead Data Scientist (Remote)', headcount: 19, avg_compa_ratio: 1.02, median_fte_salary: 180000, spread: 0.11 },
      { group_id: 'GRP-DES-L3', group_name: 'Product Designer II (Austin)', headcount: 27, avg_compa_ratio: 0.84, median_fte_salary: 110000, spread: 0.28 },
      { group_id: 'GRP-SALES-DIR', group_name: 'Sales Director (Chicago)', headcount: 15, avg_compa_ratio: 1.15, median_fte_salary: 220000, spread: 0.25 },
      { group_id: 'GRP-OPS-L2', group_name: 'Operations Specialist (Atlanta)', headcount: 42, avg_compa_ratio: 0.79, median_fte_salary: 82000, spread: 0.32 },
    ];

    const nodesGroup = new THREE.Group();
    scene.add(nodesGroup);

    const sphereMeshes: THREE.Mesh[] = [];

    sampleGroups.forEach((grp, index) => {
      // Scale radius by headcount
      const radius = THREE.MathUtils.clamp(grp.headcount * 0.08 + 1.2, 1.5, 5);
      const geo = new THREE.SphereGeometry(radius, 24, 24);

      // Y position = Compa Ratio offset (1.0 = 0)
      const posY = (grp.avg_compa_ratio - 1.0) * 80;
      // X position = spread around axis
      const angle = (index / sampleGroups.length) * Math.PI * 2;
      const distance = THREE.MathUtils.clamp((grp.median_fte_salary / 220000) * 32, 12, 34);
      const posX = Math.cos(angle) * distance;
      const posZ = Math.sin(angle) * distance;

      // Color code by equity status
      let nodeColor = 0x10b981; // Balanced emerald
      if (grp.avg_compa_ratio < 0.85) nodeColor = 0xf43f5e; // Underpaid rose
      else if (grp.avg_compa_ratio > 1.12) nodeColor = 0xf59e0b; // Overpaid amber

      const mat = new THREE.MeshStandardMaterial({
        color: nodeColor,
        roughness: 0.25,
        metalness: 0.6,
        emissive: nodeColor,
        emissiveIntensity: 0.35,
      });

      const sphere = new THREE.Mesh(geo, mat);
      sphere.position.set(posX, posY, posZ);
      sphere.userData = grp;
      nodesGroup.add(sphere);
      sphereMeshes.push(sphere);

      // Vertical tether to ground grid
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(posX, -15, posZ),
        new THREE.Vector3(posX, posY, posZ),
      ]);
      const lineMat = new THREE.LineBasicMaterial({
        color: nodeColor,
        transparent: true,
        opacity: 0.35,
      });
      const tether = new THREE.Line(lineGeo, lineMat);
      nodesGroup.add(tether);
    });

    // Raycaster for mouse picking
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(sphereMeshes);

      if (intersects.length > 0 && tooltipRef.current) {
        const item = intersects[0].object.userData;
        tooltipRef.current.style.display = 'block';
        tooltipRef.current.style.left = `${e.clientX - rect.left + 15}px`;
        tooltipRef.current.style.top = `${e.clientY - rect.top + 15}px`;
        tooltipRef.current.innerHTML = `
          <div class="font-bold text-white text-xs">${item.group_name || item.group_id}</div>
          <div class="text-[11px] text-slate-300 mt-1">Headcount: <span class="font-bold text-indigo-400">${item.headcount}</span></div>
          <div class="text-[11px] text-slate-300">Avg Compa-Ratio: <span class="font-bold ${item.avg_compa_ratio < 0.85 ? 'text-rose-400' : 'text-emerald-400'}">${item.avg_compa_ratio?.toFixed(3)}</span></div>
          <div class="text-[11px] text-slate-300">Median Salary: <span class="font-bold text-white">$${item.median_fte_salary?.toLocaleString()}</span></div>
        `;
      } else if (tooltipRef.current) {
        tooltipRef.current.style.display = 'none';
      }
    };

    const handleClick = () => {
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(sphereMeshes);
      if (intersects.length > 0 && onSelectGroup) {
        onSelectGroup(intersects[0].object.userData.group_id);
      }
    };

    container.addEventListener('mousemove', handleMouseMove);
    container.addEventListener('click', handleClick);

    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Smooth slow orbital rotation of entire spatial cluster
      nodesGroup.rotation.y = elapsedTime * 0.15;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      container.removeEventListener('mousemove', handleMouseMove);
      container.removeEventListener('click', handleClick);
      cancelAnimationFrame(animationFrameId);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [groups]);

  return (
    <div className="relative rounded-2xl overflow-hidden border border-slate-700/60 shadow-xl bg-slate-900">
      {/* Canvas Header Bar */}
      <div className="absolute top-3 left-4 z-10 flex items-center space-x-3 pointer-events-none">
        <span className="flex h-2.5 w-2.5 rounded-full bg-indigo-400 animate-ping" />
        <span className="text-xs font-semibold text-slate-200 tracking-wide uppercase font-mono">
          Multi-Cohort Disparity Space (Compa-Ratio vs. Headcount & Salary Dispersion)
        </span>
      </div>

      <div className="absolute top-3 right-4 z-10 flex items-center space-x-3 text-[11px] text-slate-400 font-mono pointer-events-none">
        <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 mr-1.5" /> Balanced</span>
        <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-rose-500 mr-1.5" /> Below Target</span>
        <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 mr-1.5" /> Above Target</span>
      </div>

      <div ref={mountRef} className="w-full h-[340px] cursor-grab active:cursor-grabbing" />

      {/* Floating Hover Tooltip */}
      <div
        ref={tooltipRef}
        className="pointer-events-none absolute z-30 hidden rounded-xl bg-slate-900/95 backdrop-blur-md p-3 border border-indigo-500/50 shadow-2xl text-left"
      />
    </div>
  );
};
