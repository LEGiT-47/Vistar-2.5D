// Pipeline stage definitions — kept in a separate file so that
// CinematicControls.tsx can use React Fast Refresh without conflicts.
export const STAGE_DEFINITIONS = [
  { stage: 1,  title: 'Mission Ingested',              desc: 'LiDAR scan stream loaded with vehicle calibration coordinates.' },
  { stage: 2,  title: 'Raw 3D Point Cloud',            desc: 'Full 360-degree dense spherical LiDAR point cloud rendered in 3D.' },
  { stage: 3,  title: 'Voxel Filtering & Normalization', desc: 'Valid range bounding box and spatial voxel downsampling applied.' },
  { stage: 4,  title: 'Ground & Obstacle Extraction',  desc: 'RANSAC ground surface extraction separates drivable terrain from obstacles.' },
  { stage: 5,  title: 'Semantic Classification',       desc: 'Harmonized ontology maps road, vegetation, buildings, and vehicles (Mode B).' },
  { stage: 6,  title: 'Low-Confidence Return Filtering', desc: 'Airborne exhaust plumes, aerosols, and ghost returns are down-weighted & rejected.' },
  { stage: 7,  title: 'Terrain & Roughness Analysis',  desc: 'Local elevation variation, surface normal gradients, and pothole detection computed.' },
  { stage: 8,  title: '3D Cloud → 2.5D Grid',          desc: 'Trusted LiDAR points project into compact, memory-efficient 2.5D cell columns.' },
  { stage: 9,  title: 'Foveated Variable Resolution',  desc: 'Adaptive tiers allocated: 5 cm near, 10 cm mid, 20 cm far, 50 cm peripheral.' },
  { stage: 10, title: 'Dynamic Object Isolation',      desc: 'Moving vehicles and pedestrians remain live obstacles but leave the terrain map.' },
  { stage: 11, title: 'Traversability Field',          desc: 'Cell cost calculated from slope, roughness, obstacles, semantics, and uncertainty.' },
  { stage: 12, title: 'A* Optimal Route Planning',     desc: 'Hazard-penalized navigation corridor planned from vehicle origin to mission goal.' },
  { stage: 13, title: 'Digital Breadcrumb Cache',      desc: 'Spatial deduplication stores persistent historical terrain in compact footprint.' },
  { stage: 14, title: 'Sensor Degradation Resilience', desc: 'LiDAR attenuation event: vehicle safely retains historical backtrack corridor.' },
  { stage: 15, title: 'Offline DEM Fusion',            desc: 'Coarse 90 m Copernicus GLO-90 elevation context extends beyond LiDAR horizon.' },
  { stage: 16, title: 'Fixed 5 cm vs VISTAR',          desc: 'Synchronized split-screen proves 70–85 % memory reduction over identical terrain.' },
  { stage: 17, title: 'Mission Complete',              desc: 'Comprehensive SIH perception report and scientific benchmarks compiled.' },
];
