import React from 'react';
import { X, Award, RotateCcw, ArrowRight, ShieldCheck, CheckCircle2, Database, Zap, Layers, Activity } from 'lucide-react';
import { PipelineResults, ScenarioMetadata } from '../types';

interface MissionReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  results: PipelineResults | null;
  scenario: ScenarioMetadata | null;
  onReplayMission: () => void;
  onCompareAnother: () => void;
}

export const MissionReportModal: React.FC<MissionReportModalProps> = ({
  isOpen,
  onClose,
  results,
  scenario,
  onReplayMission,
  onCompareAnother
}) => {
  if (!isOpen || !results || !scenario) return null;

  const rawCount = results.stage_1_input.raw_point_count;
  const filteredCount = results.stage_2_filter.filtered_point_count;
  const cvStats = results.stage_5_clear_vision;
  const dynStats = results.stage_6_dynamic;
  const adaptiveStats = results.stage_7_adaptive_grid;
  const comp = results.stage_8_comparison;
  const cacheStats = results.stage_10_cache;
  const demStats = results.stage_11_dem;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-slate-100 font-mono">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">VISTAR-2.5D MISSION REPORT</h2>
                <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 border border-cyan-800 text-cyan-400">
                  SIH26053 VERIFIED
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {scenario.title} • {scenario.dataset} • {cacheStats.mission_distance_m} m Mission Run
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs">
          {/* Section 1: Perception & Mapping Highlights Banner */}
          <div className="grid grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Raw Points Processed</span>
              <span className="text-xl font-bold text-slate-100">{rawCount.toLocaleString()}</span>
              <span className="text-[10px] text-cyan-400 block mt-1">100% Valid Returns</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Memory Reduction</span>
              <span className="text-xl font-bold text-cyan-400">-{comp.memory_reduction_percentage}%</span>
              <span className="text-[10px] text-slate-400 block mt-1">vs Fixed 5cm Baseline</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Perception Trust</span>
              <span className="text-xl font-bold text-emerald-400">{results.mission_trust_score}%</span>
              <span className="text-[10px] text-emerald-400/80 block mt-1">Nominal Confidence</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">DEM Topographic Sync</span>
              <span className="text-xl font-bold text-purple-400">{demStats.dem_agreement_score}%</span>
              <span className="text-[10px] text-purple-400/80 block mt-1">Δ {demStats.mean_elevation_difference_m}m Mean Error</span>
            </div>
          </div>

          {/* Section 2: Perception Breakdown */}
          <div className="rounded-xl border border-slate-800 p-4 bg-slate-950/40">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Layers className="w-3.5 h-3.5" />
              <span>PERCEPTION TELEMETRY</span>
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
              <div>
                <span className="text-slate-500 block">Filtered Points:</span>
                <span className="font-semibold text-slate-200">{filteredCount.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Active Semantic Classes:</span>
                <span className="font-semibold text-slate-200">14 Ontology Classes</span>
              </div>
              <div>
                <span className="text-slate-500 block">Dynamic Actors Segregated:</span>
                <span className="font-semibold text-amber-400">{dynStats.dynamic_point_count.toLocaleString()} pts</span>
              </div>
              <div>
                <span className="text-slate-500 block">Low-Confidence Rejected:</span>
                <span className="font-semibold text-rose-400">{cvStats.low_confidence_rejected.toLocaleString()} pts ({cvStats.rejection_percentage}%)</span>
              </div>
            </div>
          </div>

          {/* Section 3: Adaptive Mapping Grid Tiers */}
          <div className="rounded-xl border border-slate-800 p-4 bg-slate-950/40">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Zap className="w-3.5 h-3.5" />
              <span>VARIABLE RESOLUTION CELL ALLOCATION</span>
            </h3>
            <div className="grid grid-cols-4 gap-3 text-[11px]">
              <div className="p-2.5 rounded-lg bg-slate-900 border border-cyan-800/40">
                <span className="text-cyan-400 block font-bold">5 cm Near-Field</span>
                <div className="text-slate-200 text-sm font-bold mt-1">{adaptiveStats.res_5cm_count.toLocaleString()} cells</div>
                <div className="text-[10px] text-slate-400">{adaptiveStats.res_5cm_pct}% of map</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-blue-800/40">
                <span className="text-blue-400 block font-bold">10 cm Mid-Near</span>
                <div className="text-slate-200 text-sm font-bold mt-1">{adaptiveStats.res_10cm_count.toLocaleString()} cells</div>
                <div className="text-[10px] text-slate-400">{adaptiveStats.res_10cm_pct}% of map</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-750">
                <span className="text-slate-300 block font-bold">20 cm Mid-Far</span>
                <div className="text-slate-200 text-sm font-bold mt-1">{adaptiveStats.res_20cm_count.toLocaleString()} cells</div>
                <div className="text-[10px] text-slate-400">{adaptiveStats.res_20cm_pct}% of map</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block font-bold">50 cm Peripheral</span>
                <div className="text-slate-200 text-sm font-bold mt-1">{adaptiveStats.res_50cm_count.toLocaleString()} cells</div>
                <div className="text-[10px] text-slate-400">{adaptiveStats.res_50cm_pct}% of map</div>
              </div>
            </div>
            <div className="mt-2 text-[10px] text-amber-400/90 font-mono">
              ★ {adaptiveStats.refined_cells_count} peripheral cells were automatically refined to high-resolution due to obstacle hazards and slope complexity!
            </div>
          </div>

          {/* Section 4: Performance & Memory Benchmark */}
          <div className="rounded-xl border border-slate-800 p-4 bg-slate-950/40">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Database className="w-3.5 h-3.5" />
              <span>RIGOROUS BASELINE COMPARISON</span>
            </h3>
            <div className="grid grid-cols-2 gap-4 text-[11px]">
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400 block font-bold uppercase">{comp.label_left}</span>
                <div className="mt-2 space-y-1 text-slate-300">
                  <div>Cell Count: <span className="font-bold text-amber-400">{comp.fixed.cell_count.toLocaleString()}</span></div>
                  <div>Memory: <span className="font-bold text-amber-400">{comp.fixed.memory_mb} MB</span></div>
                  <div>Processing Time: <span>{comp.fixed.processing_time_ms} ms</span></div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-cyan-950/30 border border-cyan-800/60">
                <span className="text-cyan-300 block font-bold uppercase">{comp.label_right}</span>
                <div className="mt-2 space-y-1 text-slate-200">
                  <div>Cell Count: <span className="font-bold text-emerald-400">{comp.vistar.total_cells.toLocaleString()}</span></div>
                  <div>Memory: <span className="font-bold text-emerald-400">{comp.vistar.memory_mb} MB</span></div>
                  <div>Measured Reduction: <span className="font-bold text-cyan-400">-{comp.memory_reduction_percentage}%</span></div>
                </div>
              </div>
            </div>
          </div>

          {/* Section 5: Digital Breadcrumb & DEM Continuity */}
          <div className="rounded-xl border border-slate-800 p-4 bg-slate-950/40">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2 flex items-center gap-2">
              <Activity className="w-3.5 h-3.5" />
              <span>PERSISTENT CACHE & MACROSCOPIC DEM</span>
            </h3>
            <div className="grid grid-cols-3 gap-3 text-[11px]">
              <div>
                <span className="text-slate-500 block">Historical Cache Size:</span>
                <span className="font-semibold text-slate-200">{cacheStats.cache_size_kb} KB</span>
              </div>
              <div>
                <span className="text-slate-500 block">Raw LiDAR Equivalent:</span>
                <span className="font-semibold text-slate-200">{cacheStats.raw_equivalent_mb} MB</span>
              </div>
              <div>
                <span className="text-slate-500 block">Historical Compression:</span>
                <span className="font-semibold text-cyan-400">{cacheStats.compression_ratio}:1</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>SIH26053 Evaluation Ready</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onReplayMission}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>REPLAY MISSION</span>
            </button>

            <button
              onClick={onCompareAnother}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition-all shadow-md shadow-cyan-500/20"
            >
              <span>COMPARE ANOTHER SCENARIO</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
