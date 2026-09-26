import React from 'react';
import { Gauge, Shield, Database, Compass, Activity, Zap, Layers } from 'lucide-react';
import { PipelineResults } from '../types';

interface OperatorDashboardProps {
  results: PipelineResults | null;
  scenarioTitle: string;
  isSensorDegraded: boolean;
}

export const OperatorDashboard: React.FC<OperatorDashboardProps> = ({
  results,
  scenarioTitle,
  isSensorDegraded
}) => {
  if (!results) {
    return (
      <div className="flex-none h-14 bg-slate-900/90 border-t border-slate-800 px-6 flex items-center justify-between font-mono text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400 animate-spin" />
          <span>INITIALIZING VISTAR PERCEPTION PIPELINE...</span>
        </div>
      </div>
    );
  }

  const rawPts = results.stage_1_input.raw_point_count;
  const adaptiveStats = results.stage_7_adaptive_grid;
  const cacheStats = results.stage_10_cache;
  const demStats = results.stage_11_dem;
  const trustScore = isSensorDegraded ? Math.max(12, Math.round(results.mission_trust_score * 0.35)) : results.mission_trust_score;
  const latencyMs = results.total_pipeline_time_ms;

  return (
    <div className="flex-none bg-slate-900/95 border-t border-slate-800 px-6 py-2.5 flex items-center justify-between text-xs font-mono select-none backdrop-blur z-20 overflow-x-auto">
      {/* 1. Mission Distance */}
      <div className="flex items-center gap-2.5 pl-1 pr-4 border-r border-slate-800">
        <Compass className="w-4 h-4 text-cyan-400 flex-none" />
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Distance</div>
          <div className="text-slate-100 font-bold">{cacheStats.mission_distance_m} m</div>
        </div>
      </div>

      {/* 2. LiDAR Points */}
      <div className="flex items-center gap-2.5 px-4 border-r border-slate-800">
        <Layers className="w-4 h-4 text-blue-400 flex-none" />
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Points</div>
          <div className="text-slate-100 font-bold">{isSensorDegraded ? Math.floor(rawPts * 0.15).toLocaleString() : rawPts.toLocaleString()}</div>
        </div>
      </div>

      {/* 3. Resolution Tiers */}
      <div className="flex items-center gap-2.5 px-4 border-r border-slate-800">
        <Zap className="w-4 h-4 text-amber-400 flex-none" />
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Resolution</div>
          <div className="text-cyan-400 font-bold">5cm / 10cm / 20cm / 50cm</div>
        </div>
      </div>

      {/* 4. Trust Score & Uncertainty */}
      <div className="flex items-center gap-2.5 px-4 border-r border-slate-800">
        <Shield className={`w-4 h-4 flex-none ${trustScore > 70 ? 'text-emerald-400' : trustScore > 40 ? 'text-amber-400' : 'text-rose-400'}`} />
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Trust Score</div>
          <div className={`font-bold ${trustScore > 70 ? 'text-emerald-400' : trustScore > 40 ? 'text-amber-400' : 'text-rose-400'}`}>
            {trustScore}%
          </div>
        </div>
      </div>

      {/* 5. Traversability */}
      <div className="flex items-center gap-2.5 px-4 border-r border-slate-800">
        <Gauge className="w-4 h-4 text-emerald-400 flex-none" />
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Traversability</div>
          <div className="text-emerald-400 font-bold">SAFE CORRIDOR</div>
        </div>
      </div>

      {/* 6. Digital Breadcrumb Cache Size */}
      <div className="flex items-center gap-2.5 px-4 border-r border-slate-800">
        <Database className="w-4 h-4 text-indigo-400 flex-none" />
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Cache Size</div>
          <div className="text-slate-100 font-bold">
            {cacheStats.cache_size_kb} KB <span className="text-[10px] text-cyan-400">({cacheStats.compression_ratio}:1)</span>
          </div>
        </div>
      </div>

      {/* 7. DEM Topographic Agreement */}
      <div className="flex items-center gap-2.5 px-4 border-r border-slate-800">
        <Activity className="w-4 h-4 text-purple-400 flex-none" />
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">DEM Agreement</div>
          <div className="text-purple-300 font-bold">{demStats.dem_agreement_score}%</div>
        </div>
      </div>

      {/* 8. Pipeline Latency */}
      <div className="flex items-center gap-2.5 pl-4 pr-1">
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Latency</div>
          <div className="text-slate-200 font-bold">{latencyMs} ms</div>
        </div>
      </div>
    </div>
  );
};
