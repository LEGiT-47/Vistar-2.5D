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
    const pointValues = results.vis_payload.points;
    const bounds = getBounds(pointValues);
    const span = Math.max(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY, 12);
    const sharedPolar = {
      radius: span * 1.25,
      theta: Math.PI / 4.2,
      phi: Math.PI / 3.0,
      target: new THREE.Vector3(
        (bounds.minX + bounds.maxX) / 2,
        (bounds.minY + bounds.maxY) / 2,
        bounds.minZ
      )
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
      const gridSize = Math.max(40, span * 1.8);
      const grid = new THREE.GridHelper(gridSize, Math.min(120, Math.ceil(gridSize * 2)), 0x1f293d, 0x111827);
      grid.position.z = -1.61;
      grid.rotation.x = Math.PI / 2;
      sc.add(grid);
    });

    // Use instancing on both sides: comparison is intentionally dense, but it
    // should not create one GPU object and material for every visible tile.
    const rawCells = results.vis_payload.cells;
    sceneLeft.add(buildPointCloud(pointValues, 0x38bdf8, 0.16, 0.85));
    sceneLeft.add(buildFixedComparisonCells(pointValues));
    sceneRight.add(buildPointCloud(pointValues, 0x64748b, 0.11, 0.30));
    sceneRight.add(buildAdaptiveComparisonCells(rawCells));
    sceneLeft.add(buildRoute(results.vis_payload.route_waypoints, 0xf59e0b));
    sceneRight.add(buildRoute(results.vis_payload.route_waypoints, 0x00e5ff));

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
      disposeScene(sceneLeft);
      disposeScene(sceneRight);
      rendererLeft.dispose();
      rendererRight.dispose();
    };

    function buildFixedComparisonCells(points: number[]): THREE.Group {
      const buckets = new Map<string, { x: number; y: number; z: number }>();
      for (let i = 0; i < points.length; i += 3) {
        const x = Math.floor(points[i] / 0.25) * 0.25 + 0.125;
        const y = Math.floor(points[i + 1] / 0.25) * 0.25 + 0.125;
        const key = `${x}:${y}`;
        if (!buckets.has(key)) buckets.set(key, { x, y, z: points[i + 2] });
      }
      const items = [...buckets.values()].slice(0, 6000);

      const group = new THREE.Group();
      const mesh = new THREE.InstancedMesh(
        new THREE.BoxGeometry(0.22, 0.22, 0.10),
        new THREE.MeshBasicMaterial({ color: 0x22d3ee }),
        items.length
      );
      const dummy = new THREE.Object3D();
      items.forEach((item, index) => {
        dummy.position.set(item.x, item.y, item.z);
        dummy.updateMatrix();
        mesh.setMatrixAt(index, dummy.matrix);
      });
      mesh.instanceMatrix.needsUpdate = true;
      group.add(mesh);
      return group;
    }

    function buildAdaptiveComparisonCells(cells: PipelineResults['vis_payload']['cells']): THREE.Group {
      const group = new THREE.Group();
      const buckets = new Map<string, { color: number; items: PipelineResults['vis_payload']['cells'] }>();
      cells.forEach(cell => {
        const color = cell.is_refined
          ? 0xf59e0b
          : cell.resolution <= 0.05
            ? 0x00e5ff
            : cell.resolution <= 0.10
              ? 0x3b82f6
              : cell.resolution <= 0.20
                ? 0x64748b
                : 0x334155;
        const key = `${color}:${cell.resolution}`;
        if (!buckets.has(key)) buckets.set(key, { color, items: [] });
        buckets.get(key)!.items.push(cell);
      });

      const dummy = new THREE.Object3D();
      buckets.forEach(({ color, items }) => {
        const resolution = items[0].resolution;
        const mesh = new THREE.InstancedMesh(
          new THREE.BoxGeometry(resolution * 0.94, resolution * 0.94, 0.1),
          new THREE.MeshStandardMaterial({ color, roughness: 0.3 }),
          items.length
        );
        items.forEach((cell, index) => {
          dummy.position.set(cell.x, cell.y, cell.elevation_mean);
          dummy.updateMatrix();
          mesh.setMatrixAt(index, dummy.matrix);
        });
        mesh.instanceMatrix.needsUpdate = true;
        group.add(mesh);
      });
      return group;
    }

    function disposeScene(scene: THREE.Scene): void {
      scene.traverse(object => {
        const mesh = object as THREE.Mesh;
        if (mesh.geometry) mesh.geometry.dispose();
        const material = mesh.material;
        if (Array.isArray(material)) material.forEach(item => item.dispose());
        else if (material) material.dispose();
      });
    }
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
            <span className="text-slate-400">Fixed / Adaptive Time:</span>
            <span className="text-slate-200">
              {(fixed.processing_time_ms / Math.max(0.01, vistar.processing_time_ms)).toFixed(2)}x
            </span>
          </div>
        </div>
      </div>

      {/* Split Screens */}
      <div className="flex-1 grid grid-cols-2 relative min-h-[260px]">
        {/* Left Side: Conventional Fixed 5 cm Map */}
        <div className="relative border-r border-slate-800 overflow-hidden flex flex-col">
          <div className="absolute top-4 left-4 z-10 px-3 py-1.5 rounded bg-slate-900/90 border border-slate-700/80 backdrop-blur font-mono text-xs shadow-lg">
            <div className="text-slate-300 font-semibold tracking-wide">{comp.label_left}</div>
            <div className="text-[11px] text-slate-400 mt-1 flex flex-col gap-0.5">
              <div>Resolution: <span className="text-slate-200">Uniform 0.05 m (5 cm)</span></div>
              <div>Allocated Cells: <span className="text-amber-400 font-bold">{fixed.cell_count.toLocaleString()}</span></div>
              <div>Memory Footprint: <span className="text-amber-400 font-bold">{fixed.memory_mb} MB</span></div>
              <div>Processing Latency: <span className="text-slate-200">{fixed.processing_time_ms} ms</span></div>
              <div>Rendered Samples: <span className="text-cyan-300">6,000 max</span></div>
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

function getBounds(points: number[]) {
  const bounds = {
    minX: Infinity, maxX: -Infinity,
    minY: Infinity, maxY: -Infinity,
    minZ: Infinity, maxZ: -Infinity,
  };
  for (let i = 0; i < points.length; i += 3) {
    bounds.minX = Math.min(bounds.minX, points[i]);
    bounds.maxX = Math.max(bounds.maxX, points[i]);
    bounds.minY = Math.min(bounds.minY, points[i + 1]);
    bounds.maxY = Math.max(bounds.maxY, points[i + 1]);
    bounds.minZ = Math.min(bounds.minZ, points[i + 2]);
    bounds.maxZ = Math.max(bounds.maxZ, points[i + 2]);
  }
  return bounds;
}

function buildPointCloud(
  points: number[],
  color: number,
  size: number,
  opacity: number
): THREE.Points {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
  return new THREE.Points(
    geometry,
    new THREE.PointsMaterial({ color, size, sizeAttenuation: true, transparent: opacity < 1, opacity })
  );
}

function buildRoute(waypoints: [number, number, number][], color: number): THREE.Object3D {
  if (waypoints.length < 2) return new THREE.Group();
  const geometry = new THREE.BufferGeometry().setFromPoints(
    waypoints.map(([x, y, z]) => new THREE.Vector3(x, y, z + 0.18))
  );
  return new THREE.Line(
    geometry,
    new THREE.LineBasicMaterial({ color, linewidth: 2, transparent: true, opacity: 0.95 })
  );
}
