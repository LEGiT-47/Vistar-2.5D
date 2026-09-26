import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { ViewMode, VisPayload } from '../types';

interface LidarViewportProps {
  payload: VisPayload | null;
  viewMode: ViewMode;
  stageIndex: number;
  isSensorDegraded: boolean;
  highlightRefined?: boolean;
  showDEM?: boolean;
}

const SEMANTIC_COLORS: Record<number, number> = {
  0: 0x808080, 1: 0x966e50, 2: 0x3cb4f0, 3: 0x50c878,
  4: 0x228b22, 5: 0x8b4513, 6: 0x1e90ff, 7: 0xb22222,
  8: 0xd2691e, 9: 0xffa500, 10: 0xff4500, 11: 0xffd700,
  12: 0xdc143c, 13: 0xb0c4de,
};

// Shared dummy object for matrix computation
const _dummy = new THREE.Object3D();
const _color = new THREE.Color();

export const LidarViewport: React.FC<LidarViewportProps> = ({
  payload,
  viewMode,
  stageIndex,
  isSensorDegraded,
  showDEM = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const objectsGroupRef = useRef<THREE.Group | null>(null);
  const isMouseDown = useRef(false);
  const mousePrev = useRef({ x: 0, y: 0 });
  const cameraPolar = useRef({
    radius: 36, theta: Math.PI / 4, phi: Math.PI / 3.2,
    target: new THREE.Vector3(10, 0, -1.0)
  });

  // ── Initialize Three.js scene once ──────────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 500;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0d14);
    scene.fog = new THREE.FogExp2(0x0a0d14, 0.010);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(48, width / height, 0.1, 300);
    cameraRef.current = camera;
    syncCamera();

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: 'high-performance',
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Lights
    scene.add(new THREE.AmbientLight(0xffffff, 0.85));
    const dirLight = new THREE.DirectionalLight(0x00e5ff, 0.6);
    dirLight.position.set(20, 30, 40);
    scene.add(dirLight);

    // Grid
    const grid = new THREE.GridHelper(90, 90, 0x1f293d, 0x111827);
    grid.position.z = -1.61;
    grid.rotation.x = Math.PI / 2;
    scene.add(grid);

    // Root group for all data objects
    const objGroup = new THREE.Group();
    scene.add(objGroup);
    objectsGroupRef.current = objGroup;

    // Animation loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    // Mouse orbit
    const onMouseDown = (e: MouseEvent) => {
      isMouseDown.current = true;
      mousePrev.current = { x: e.clientX, y: e.clientY };
    };
    const onMouseMove = (e: MouseEvent) => {
      if (!isMouseDown.current) return;
      const dx = e.clientX - mousePrev.current.x;
      const dy = e.clientY - mousePrev.current.y;
      mousePrev.current = { x: e.clientX, y: e.clientY };
      if (e.buttons === 1) {
        cameraPolar.current.theta -= dx * 0.008;
        cameraPolar.current.phi = Math.max(0.1, Math.min(Math.PI / 2 - 0.05, cameraPolar.current.phi - dy * 0.008));
      } else if (e.buttons === 2) {
        const camRight = new THREE.Vector3().crossVectors(camera.up, camera.getWorldDirection(new THREE.Vector3())).normalize();
        cameraPolar.current.target.addScaledVector(camRight, dx * 0.04);
        cameraPolar.current.target.y += dy * 0.04;
      }
      syncCamera();
    };
    const onMouseUp = () => { isMouseDown.current = false; };
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      cameraPolar.current.radius = Math.max(5, Math.min(120, cameraPolar.current.radius + e.deltaY * 0.04));
      syncCamera();
    };

    const dom = renderer.domElement;
    dom.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    dom.addEventListener('wheel', onWheel, { passive: false });
    dom.addEventListener('contextmenu', (e) => e.preventDefault());

    const onResize = () => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animId);
      dom.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      dom.removeEventListener('wheel', onWheel);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
    };
  }, []);

  function syncCamera() {
    if (!cameraRef.current) return;
    const { radius, theta, phi, target } = cameraPolar.current;
    const x = target.x + radius * Math.sin(phi) * Math.cos(theta);
    const y = target.y + radius * Math.sin(phi) * Math.sin(theta);
    const z = target.z + radius * Math.cos(phi);
    cameraRef.current.position.set(x, y, z);
    cameraRef.current.up.set(0, 0, 1);
    cameraRef.current.lookAt(target);
  }

  // ── Re-render data whenever payload / viewMode / stage changes ────────
  useEffect(() => {
    const group = objectsGroupRef.current;
    if (!group) return;

    // Dispose old objects to free GPU memory
    disposeGroup(group);
    group.clear();

    // Always render the ego vehicle
    group.add(createEgoVehicle());

    if (!payload) return;

    const { points, semantics, confidence, dynamic_points, cells, dem_cells, route_waypoints } = payload;

    // Degraded-sensor slice
    const ptSlice = isSensorDegraded ? Math.floor(points.length * 0.15) : points.length;
    const effectivePoints = points.slice(0, ptSlice);
    const effectiveSemantics = semantics.slice(0, Math.floor(ptSlice / 3));
    const effectiveConfidence = confidence.slice(0, Math.floor(ptSlice / 3));

    const showPointCloud = viewMode === 'LIDAR_3D' || stageIndex <= 6;
    const showCells = !showPointCloud || viewMode !== 'LIDAR_3D';

    // ── 1. POINT CLOUD ─────────────────────────────────────────────────
    if (showPointCloud && effectivePoints.length > 0) {
      const pCount = Math.floor(effectivePoints.length / 3);
      const geom = new THREE.BufferGeometry();
      const posArray = new Float32Array(effectivePoints.slice(0, pCount * 3));
      const colArray = new Float32Array(pCount * 3);

      for (let i = 0; i < pCount; i++) {
        const pz = effectivePoints[i * 3 + 2];
        const sem = effectiveSemantics[i] ?? 0;
        const conf = effectiveConfidence[i] ?? 1.0;

        if (viewMode === 'SEMANTIC' || stageIndex === 5) {
          _color.setHex(SEMANTIC_COLORS[sem] ?? 0x808080);
        } else if (viewMode === 'CONFIDENCE' || stageIndex === 6) {
          _color.setHSL(conf * 0.35, 0.9, 0.55);
        } else {
          const normZ = Math.max(0, Math.min(1, (pz + 1.6) / 3.5));
          _color.setHSL(0.55 - normZ * 0.45, 0.95, 0.55);
        }
        colArray[i * 3] = _color.r;
        colArray[i * 3 + 1] = _color.g;
        colArray[i * 3 + 2] = _color.b;
      }

      geom.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
      geom.setAttribute('color', new THREE.BufferAttribute(colArray, 3));

      const pMesh = new THREE.Points(geom, new THREE.PointsMaterial({
        size: 0.12, vertexColors: true, transparent: true,
        opacity: isSensorDegraded ? 0.4 : 0.88,
      }));
      group.add(pMesh);
    }

    // ── 2. 2.5D GRID via InstancedMesh (1 draw call per color bucket) ──
    if (showCells && cells.length > 0) {
      group.add(buildInstancedCells(cells, viewMode, stageIndex));
    }

    // ── 3. DYNAMIC POINTS ──────────────────────────────────────────────
    if (dynamic_points && dynamic_points.length > 0 && stageIndex >= 10) {
      const dynGeom = new THREE.BufferGeometry();
      dynGeom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(dynamic_points), 3));
      const dynMesh = new THREE.Points(dynGeom, new THREE.PointsMaterial({
        size: 0.18, color: 0xff3b30, transparent: true, opacity: 0.95,
      }));
      group.add(dynMesh);

      group.add(new THREE.Box3Helper(
        new THREE.Box3(new THREE.Vector3(13.0, 0.5, -1.5), new THREE.Vector3(17.5, 2.2, 0.2)),
        new THREE.Color(0xff9500)
      ));
    }

    // ── 4. ROUTE PLANNING ──────────────────────────────────────────────
    if (route_waypoints && route_waypoints.length > 1 && (stageIndex >= 12 || viewMode === 'TRAVERSABILITY')) {
      const pathPts = route_waypoints.map(w => new THREE.Vector3(w[0], w[1], w[2] + 0.15));
      const curve = new THREE.CatmullRomCurve3(pathPts);
      const tubeGeom = new THREE.TubeGeometry(curve, 64, 0.08, 8, false);
      group.add(new THREE.Mesh(tubeGeom, new THREE.MeshBasicMaterial({ color: 0x00e5ff })));
      group.add(createPinMarker(pathPts[0], 0x10b981));
      group.add(createPinMarker(pathPts[pathPts.length - 1], 0x00e5ff));
    }

    // ── 5. DEM CONTEXT ─────────────────────────────────────────────────
    if (showDEM && dem_cells && dem_cells.length > 0 && (stageIndex >= 15 || stageIndex === 1)) {
      group.add(buildInstancedDEM(dem_cells));
    }

  }, [payload, viewMode, stageIndex, isSensorDegraded, showDEM]);

  return (
    <div className="relative w-full h-full overflow-hidden select-none bg-slate-950">
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {isSensorDegraded && (
        <div className="absolute top-4 left-4 z-20 flex items-center gap-2.5 px-3 py-1.5 rounded border border-amber-500/60 bg-amber-950/80 backdrop-blur text-amber-300 font-mono text-xs tracking-wider animate-pulse shadow-lg shadow-amber-900/30">
          <div className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
          <span>SIMULATION: SENSOR DEGRADED — BACKTRACK CORRIDOR ACTIVE</span>
        </div>
      )}

      <div className="absolute bottom-3 right-3 z-10 text-[10px] font-mono text-slate-400/80 bg-slate-900/80 backdrop-blur px-2.5 py-1 rounded border border-slate-800 pointer-events-none">
        Left Click: Orbit • Right Click: Pan • Scroll: Zoom • Z-Up Frame
      </div>
    </div>
  );
};

// ── Helpers ──────────────────────────────────────────────────────────────

/**
 * Build grid cells using InstancedMesh – one shared BoxGeometry per resolution
 * tier, one shared material per color bucket. Reduces draw calls from O(cells)
 * to O(color_buckets × resolution_tiers) ≈ 8 draw calls.
 */
function buildInstancedCells(
  cells: import('../types').Cell25D[],
  viewMode: ViewMode,
  stageIndex: number
): THREE.Group {
  const out = new THREE.Group();

  // Determine color for each cell
  const colorOf = (cell: import('../types').Cell25D): number => {
    if (viewMode === 'RESOLUTION_MAP' || stageIndex === 8 || stageIndex === 9) {
      if (cell.is_refined) return 0xf59e0b;
      if (cell.resolution <= 0.05) return 0x00e5ff;
      if (cell.resolution <= 0.10) return 0x3b82f6;
      if (cell.resolution <= 0.20) return 0x64748b;
      return 0x334155;
    }
    if (viewMode === 'TRAVERSABILITY' || stageIndex >= 11) {
      if (cell.traversability >= 0.65) return 0x10b981;
      if (cell.traversability >= 0.35) return 0xf59e0b;
      return 0xef4444;
    }
    if (viewMode === 'RISK_HAZARD') {
      if (cell.hazard === 'POTHOLE') return 0x8b5cf6;
      if (cell.hazard === 'WALL') return 0xd946ef;
      if (cell.hazard === 'OBSTACLE') return 0xef4444;
      if (cell.hazard === 'STEEP_SLOPE') return 0xf97316;
      if (cell.hazard === 'ROUGH_TERRAIN') return 0xd97706;
      if (cell.hazard === 'WATER') return 0x06b6d4;
      return 0x10b981;
    }
    if (viewMode === 'CONFIDENCE') {
      _color.setHSL(cell.confidence * 0.35, 0.9, 0.5);
      return _color.getHex();
    }
    if (viewMode === 'SEMANTIC') {
      return SEMANTIC_COLORS[cell.semantic_class] ?? 0x808080;
    }
    // Height mode
    const normH = Math.max(0, Math.min(1, (cell.elevation_mean + 1.6) / 3.0));
    _color.setHSL(0.55 - normH * 0.45, 0.9, 0.55);
    return _color.getHex();
  };

  // Group cells by (colorHex, resolution) key to share instanced meshes
  const buckets = new Map<string, { color: number; res: number; items: import('../types').Cell25D[] }>();

  for (const cell of cells) {
    const col = colorOf(cell);
    const key = `${col}_${cell.resolution.toFixed(3)}`;
    if (!buckets.has(key)) buckets.set(key, { color: col, res: cell.resolution, items: [] });
    buckets.get(key)!.items.push(cell);
  }

  for (const { color, res, items } of buckets.values()) {
    const geom = new THREE.BoxGeometry(res * 0.94, res * 0.94, 1);
    const mat = new THREE.MeshStandardMaterial({
      color,
      roughness: 0.4,
      metalness: 0.1,
      transparent: true,
      opacity: color === 0xf59e0b ? 0.95 : 0.75,
    });
    const mesh = new THREE.InstancedMesh(geom, mat, items.length);
    mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

    for (let i = 0; i < items.length; i++) {
      const cell = items[i];
      const h = Math.max(0.05, cell.elevation_max - cell.elevation_min);
      _dummy.position.set(cell.x, cell.y, cell.elevation_mean);
      _dummy.scale.set(1, 1, h);
      _dummy.updateMatrix();
      mesh.setMatrixAt(i, _dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
    out.add(mesh);
  }

  return out;
}

function buildInstancedDEM(demCells: import('../types').DEMCell[]): THREE.Group {
  const out = new THREE.Group();
  if (demCells.length === 0) return out;

  const geom = new THREE.PlaneGeometry(1, 1);
  const mat = new THREE.MeshBasicMaterial({
    color: 0x6366f1, wireframe: true, transparent: true, opacity: 0.30,
  });
  const mesh = new THREE.InstancedMesh(geom, mat, demCells.length);

  for (let i = 0; i < demCells.length; i++) {
    const d = demCells[i];
    const s = d.resolution * 0.95;
    _dummy.position.set(d.x, d.y, d.elevation);
    _dummy.scale.set(s, s, 1);
    _dummy.rotation.set(0, 0, 0);
    _dummy.updateMatrix();
    mesh.setMatrixAt(i, _dummy.matrix);
  }
  mesh.instanceMatrix.needsUpdate = true;
  out.add(mesh);
  return out;
}

function createEgoVehicle(): THREE.Group {
  const vGroup = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(1.6, 0.9, 0.45),
    new THREE.MeshStandardMaterial({ color: 0x00e5ff, metalness: 0.8, roughness: 0.2 })
  );
  body.position.set(0, 0, -1.35);
  vGroup.add(body);

  const puck = new THREE.Mesh(
    new THREE.CylinderGeometry(0.12, 0.12, 0.15, 16),
    new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x00e5ff, emissiveIntensity: 0.5 })
  );
  puck.position.set(0, 0, -1.05);
  puck.rotation.x = Math.PI / 2;
  vGroup.add(puck);

  vGroup.add(new THREE.ArrowHelper(
    new THREE.Vector3(1, 0, 0),
    new THREE.Vector3(0, 0, -1.05),
    1.4, 0x00e5ff, 0.3, 0.2
  ));
  return vGroup;
}

function createPinMarker(pos: THREE.Vector3, colorHex: number): THREE.Group {
  const pin = new THREE.Group();
  const pole = new THREE.Mesh(
    new THREE.CylinderGeometry(0.04, 0.04, 0.8, 8),
    new THREE.MeshBasicMaterial({ color: colorHex })
  );
  pole.position.set(pos.x, pos.y, pos.z + 0.4);
  pole.rotation.x = Math.PI / 2;
  pin.add(pole);
  const sphere = new THREE.Mesh(
    new THREE.SphereGeometry(0.18, 16, 16),
    new THREE.MeshBasicMaterial({ color: colorHex })
  );
  sphere.position.set(pos.x, pos.y, pos.z + 0.85);
  pin.add(sphere);
  return pin;
}

function disposeGroup(group: THREE.Group) {
  group.traverse((obj) => {
    if (obj instanceof THREE.Mesh || obj instanceof THREE.InstancedMesh || obj instanceof THREE.Points) {
      obj.geometry?.dispose();
      if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
      else (obj.material as THREE.Material)?.dispose();
    }
  });
}
