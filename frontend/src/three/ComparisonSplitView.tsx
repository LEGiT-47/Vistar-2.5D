import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { PipelineResults } from '../types';

interface ComparisonSplitViewProps {
  results: PipelineResults;
}

export const ComparisonSplitView: React.FC<ComparisonSplitViewProps> = ({ results }) => {
  const containerLeftRef = useRef<HTMLDivElement>(null);
  const containerRightRef = useRef<HTMLDivElement>(null);

  const comp = results.stage_8_comparison;
  const fixed = comp.fixed;
  const vistar = comp.vistar;
  const adaptiveStats = results.stage_7_adaptive_grid;

  useEffect(() => {
    if (!containerLeftRef.current || !containerRightRef.current) return;

    // Shared camera orbit parameters
    const sharedPolar = {
      radius: 38,
      theta: Math.PI / 4.2,
      phi: Math.PI / 3.4,
      target: new THREE.Vector3(12, 0, -1.0)
    };

    // SETUP LEFT SCENE (CONVENTIONAL FIXED 5cm MAP)
    const sceneLeft = new THREE.Scene();
    sceneLeft.background = new THREE.Color(0x0a0d14);
    const cameraLeft = new THREE.PerspectiveCamera(48, 1, 0.1, 300);
    const rendererLeft = new THREE.WebGLRenderer({ antialias: true });
    containerLeftRef.current.innerHTML = '';
    containerLeftRef.current.appendChild(rendererLeft.domElement);

    // SETUP RIGHT SCENE (VISTAR ADAPTIVE 2.5D MAP)
    const sceneRight = new THREE.Scene();
    sceneRight.background = new THREE.Color(0x0a0d14);
    const cameraRight = new THREE.PerspectiveCamera(48, 1, 0.1, 300);
    const rendererRight = new THREE.WebGLRenderer({ antialias: true });
    containerRightRef.current.innerHTML = '';
    containerRightRef.current.appendChild(rendererRight.domElement);

    // Add lighting & tactical grids
    [sceneLeft, sceneRight].forEach(sc => {
      sc.add(new THREE.AmbientLight(0xffffff, 0.85));
      const dl = new THREE.DirectionalLight(0x00e5ff, 0.6);
      dl.position.set(20, 30, 40);
      sc.add(dl);
      const grid = new THREE.GridHelper(90, 90, 0x1f293d, 0x111827);
      grid.position.z = -1.61;
      grid.rotation.x = Math.PI / 2;
      sc.add(grid);
    });

    // Populate Left (Uniform 5cm Fixed Cells)
    const leftCellsGroup = new THREE.Group();
    // Sample cells and show them as uniform 5cm tiles
    const rawCells = results.vis_payload.cells;
    rawCells.slice(0, 1800).forEach(c => {
      // Subdivide into uniform 5cm dense mini-grid
      const subSteps = Math.max(1, Math.round(c.resolution / 0.05));
      for (let sx = 0; sx < Math.min(3, subSteps); sx++) {
        for (let sy = 0; sy < Math.min(3, subSteps); sy++) {
          const geom = new THREE.BoxGeometry(0.046, 0.046, 0.08);
          const mat = new THREE.MeshStandardMaterial({
            color: 0x475569, // Monolithic uniform fixed gray/slate
            roughness: 0.5
          });
          const mesh = new THREE.Mesh(geom, mat);
          mesh.position.set(
            c.x - (c.resolution / 2) + sx * 0.05 + 0.025,
            c.y - (c.resolution / 2) + sy * 0.05 + 0.025,
            c.elevation_mean
          );
          leftCellsGroup.add(mesh);
        }
      }
    });
    sceneLeft.add(leftCellsGroup);

    // Populate Right (VISTAR Variable Resolution Cells)
    const rightCellsGroup = new THREE.Group();
    rawCells.forEach(c => {
      const res = c.resolution;
      const geom = new THREE.BoxGeometry(res * 0.94, res * 0.94, 0.10);
      let col = 0x334155;
      if (res === 0.05) col = 0x00e5ff;
      else if (res === 0.10) col = 0x3b82f6;
      else if (res === 0.20) col = 0x64748b;

      if (c.is_refined) col = 0xf59e0b; // Refined cell in amber

      const mat = new THREE.MeshStandardMaterial({ color: col, roughness: 0.3 });
      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.set(c.x, c.y, c.elevation_mean);
      rightCellsGroup.add(mesh);
    });
    sceneRight.add(rightCellsGroup);

    function syncCameras() {
      const { radius, theta, phi, target } = sharedPolar;
      const x = target.x + radius * Math.sin(phi) * Math.cos(theta);
      const y = target.y + radius * Math.sin(phi) * Math.sin(theta);
      const z = target.z + radius * Math.cos(phi);

      [cameraLeft, cameraRight].forEach(cam => {
        cam.position.set(x, y, z);
        cam.up.set(0, 0, 1);
        cam.lookAt(target);
      });
    }

    function handleResize() {
      if (!containerLeftRef.current || !containerRightRef.current) return;
      const wL = containerLeftRef.current.clientWidth;
      const hL = containerLeftRef.current.clientHeight;
      cameraLeft.aspect = wL / hL;
      cameraLeft.updateProjectionMatrix();
      rendererLeft.setSize(wL, hL);

      const wR = containerRightRef.current.clientWidth;
      const hR = containerRightRef.current.clientHeight;
      cameraRight.aspect = wR / hR;
      cameraRight.updateProjectionMatrix();
      rendererRight.setSize(wR, hR);
    }
    handleResize();
    syncCameras();

    // Mouse synchronization across either split viewport
    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouse = { x: e.clientX, y: e.clientY };
    };
    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - prevMouse.x;
      const dy = e.clientY - prevMouse.y;
      prevMouse = { x: e.clientX, y: e.clientY };

      sharedPolar.theta -= dx * 0.008;
      sharedPolar.phi = Math.max(0.1, Math.min(Math.PI / 2 - 0.05, sharedPolar.phi - dy * 0.008));
      syncCameras();
    };
    const onMouseUp = () => { isDragging = false; };
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      sharedPolar.radius = Math.max(8, Math.min(120, sharedPolar.radius + e.deltaY * 0.04));
      syncCameras();
    };

    [rendererLeft.domElement, rendererRight.domElement].forEach(el => {
      el.addEventListener('mousedown', onMouseDown);
      el.addEventListener('wheel', onWheel, { passive: false });
    });
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    window.addEventListener('resize', handleResize);

    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      rendererLeft.render(sceneLeft, cameraLeft);
      rendererRight.render(sceneRight, cameraRight);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      window.removeEventListener('resize', handleResize);
      rendererLeft.dispose();
      rendererRight.dispose();
    };
  }, [results]);

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 text-slate-100 select-none">
      {/* Top Benchmark Telemetry Strip */}
      <div className="flex-none px-6 py-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-400 font-mono text-xs font-semibold">
            MANDATORY BASELINE BENCHMARK
          </div>
          <span className="text-xs text-slate-400">
            Identical spatial footprint & ground-truth LiDAR points
          </span>
        </div>

        {/* Factual Reductions */}
        <div className="flex items-center gap-6 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Cell Reduction:</span>
            <span className="text-emerald-400 font-bold">-{comp.cell_reduction_percentage}%</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Measured Memory Reduction:</span>
            <span className="text-cyan-400 font-bold">-{comp.memory_reduction_percentage}%</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Processing Ratio:</span>
            <span className="text-slate-200">{comp.speedup_ratio}x</span>
          </div>
        </div>
      </div>

      {/* Split Screens */}
      <div className="flex-1 grid grid-cols-2 relative min-h-0">
        {/* Left Side: Conventional Fixed 5 cm Map */}
        <div className="relative border-r border-slate-800 overflow-hidden flex flex-col">
          <div className="absolute top-4 left-4 z-10 px-3 py-1.5 rounded bg-slate-900/90 border border-slate-700/80 backdrop-blur font-mono text-xs shadow-lg">
            <div className="text-slate-300 font-semibold tracking-wide">{comp.label_left}</div>
            <div className="text-[11px] text-slate-400 mt-1 flex flex-col gap-0.5">
              <div>Resolution: <span className="text-slate-200">Uniform 0.05 m (5 cm)</span></div>
              <div>Allocated Cells: <span className="text-amber-400 font-bold">{fixed.cell_count.toLocaleString()}</span></div>
              <div>Memory Footprint: <span className="text-amber-400 font-bold">{fixed.memory_mb} MB</span></div>
              <div>Processing Latency: <span className="text-slate-200">{fixed.processing_time_ms} ms</span></div>
            </div>
          </div>
          <div ref={containerLeftRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
        </div>

        {/* Right Side: VISTAR Adaptive 2.5D Map */}
        <div className="relative overflow-hidden flex flex-col">
          <div className="absolute top-4 left-4 z-10 px-3 py-1.5 rounded bg-cyan-950/80 border border-cyan-700/80 backdrop-blur font-mono text-xs shadow-lg">
            <div className="text-cyan-300 font-semibold tracking-wide">{comp.label_right}</div>
            <div className="text-[11px] text-slate-300 mt-1 flex flex-col gap-0.5">
              <div>Resolution: <span className="text-cyan-400 font-bold">Adaptive (5cm / 10cm / 20cm / 50cm)</span></div>
              <div>Allocated Cells: <span className="text-emerald-400 font-bold">{vistar.total_cells.toLocaleString()}</span></div>
              <div>Memory Footprint: <span className="text-emerald-400 font-bold">{vistar.memory_mb} MB</span></div>
              <div>Refined Cells: <span className="text-amber-400">{adaptiveStats.refined_cells_count}</span></div>
            </div>
          </div>
          <div ref={containerRightRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
        </div>

        {/* Center Divider Badge */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 pointer-events-none">
          <div className="px-3 py-1 rounded-full bg-slate-900 border border-slate-700 text-[11px] font-mono text-slate-300 shadow-2xl backdrop-blur">
            SYNCED VIEWPORT
          </div>
        </div>
      </div>
    </div>
  );
};
