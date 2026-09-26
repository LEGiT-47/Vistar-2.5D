export type ViewMode = 
  | 'LIDAR_3D' 
  | 'HEIGHT_25D' 
  | 'SEMANTIC' 
  | 'TRAVERSABILITY' 
  | 'RISK_HAZARD' 
  | 'CONFIDENCE' 
  | 'RESOLUTION_MAP';

export interface ScenarioMetadata {
  id: string;
  title: string;
  dataset: string;
  environment: string;
  challenge: string;
  lidar_source: string;
  description: string;
  license: string;
  source_url: string;
  scene_type: string;
  has_smoke: boolean;
  is_synthetic_stress: boolean;
  terrain_type: string;
  scene_signature?: string;
  start: [number, number];
  goal: [number, number];
  num_points?: number;
  thumbnail_url?: string;
  vehicle_pose?: { x: number; y: number; z: number; yaw: number };
}

export interface Cell25D {
  x: number;
  y: number;
  resolution: number;
  elevation_mean: number;
  elevation_min: number;
  elevation_max: number;
  occupancy: number;
  semantic_class: number;
  slope_deg: number;
  roughness: number;
  traversability: number;
  dynamic_probability: number;
  confidence: number;
  uncertainty: number;
  hazard: string;
  point_count: number;
  is_refined?: boolean;
}

export interface DEMCell {
  x: number;
  y: number;
  elevation: number;
  resolution: number;
  source: string;
  is_live_lidar: boolean;
}

export interface VisPayload {
  points: number[];
  semantics: number[];
  confidence: number[];
  dynamic_points: number[];
  cells: Cell25D[];
  dem_cells: DEMCell[];
  route_waypoints: [number, number, number][];
  trajectory: [number, number, number, number][];
  start: [number, number];
  goal: [number, number];
}

export interface PipelineResults {
  stage_1_input: { raw_point_count: number; has_intensity: boolean; timestamp: number };
  stage_2_filter: { raw_point_count: number; filtered_point_count: number; removed_point_count: number; filter_time_ms: number; estimated_density_pts_m2: number; effective_range_m: number };
  stage_3_ground: { ground_point_count: number; obstacle_point_count: number; ground_ratio: number; plane_normal: number[]; plane_offset_d: number };
  stage_4_semantics: { active_mode: string; mode_display: string; model_name: string; scientific_honesty_note: string };
  stage_5_clear_vision: { total_points_evaluated: number; trusted_points_passed: number; low_confidence_rejected: number; rejection_percentage: number; synthetic_stress_active: boolean };
  stage_6_dynamic: { dynamic_point_count: number; static_point_count: number; dynamic_ratio: number; tracked_instances: number };
  stage_7_adaptive_grid: {
    total_cells: number;
    res_5cm_count: number;
    res_10cm_count: number;
    res_20cm_count: number;
    res_50cm_count: number;
    res_5cm_pct: number;
    res_10cm_pct: number;
    res_20cm_pct: number;
    res_50cm_pct: number;
    refined_cells_count: number;
    processing_time_ms: number;
    memory_bytes: number;
    memory_kb: number;
    memory_mb: number;
  };
  stage_8_comparison: {
    fixed: {
      fixed_resolution_m: number;
      cell_count: number;
      sparse_occupied_5cm: number;
      memory_bytes: number;
      memory_mb: number;
      processing_time_ms: number;
      effective_coverage_radius_m: number;
    };
    vistar: {
      total_cells: number;
      memory_bytes: number;
      memory_mb: number;
      processing_time_ms: number;
    };
    cell_reduction_percentage: number;
    memory_reduction_percentage: number;
    speedup_ratio: number;
    label_left: string;
    label_right: string;
  };
  stage_9_planning: {
    status: string;
    waypoints: [number, number, number][];
    path_length_m: number;
    reached_goal: boolean;
  };
  stage_10_cache: {
    cached_cell_count: number;
    cached_area_m2: number;
    cache_size_bytes: number;
    cache_size_kb: number;
    cache_size_mb: number;
    cumulative_raw_points: number;
    raw_equivalent_mb: number;
    compression_ratio: number;
    mission_distance_m: number;
    sensor_degraded: boolean;
    breadcrumb_waypoints: number;
  };
  stage_11_dem: {
    dem_source: string;
    dem_context_cell_count: number;
    mean_elevation_difference_m: number;
    dem_agreement_score: number;
    dem_coverage_radius_m: number;
  };
  mission_trust_score: number;
  total_pipeline_time_ms: number;
  vis_payload: VisPayload;
}

export interface PipelineStageEvent {
  stage_idx: number;
  total_stages: number;
  code: string;
  title: string;
  payload: Record<string, any>;
  timestamp: number;
}
