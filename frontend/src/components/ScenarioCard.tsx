import React from 'react';
import { Play, CloudRain, Wind, Mountain, AlertOctagon, Navigation } from 'lucide-react';
import { ScenarioMetadata } from '../types';

interface ScenarioCardProps {
  scenario: ScenarioMetadata;
  onSelect: (scenario: ScenarioMetadata) => void;
  isLoading?: boolean;
  isSmallest?: boolean;
}

export const ScenarioCard: React.FC<ScenarioCardProps> = ({ scenario, onSelect, isLoading, isSmallest }) => {
  const getIcon = () => {
    if (scenario.has_smoke || scenario.is_synthetic_stress) return <Wind className="w-3.5 h-3.5 text-cyan-400" />;
    if (scenario.scene_type.includes('rain') || scenario.scene_type.includes('snow')) return <CloudRain className="w-3.5 h-3.5 text-blue-400" />;
    if (scenario.terrain_type.includes('mountain') || scenario.terrain_type.includes('mud')) return <Mountain className="w-3.5 h-3.5 text-emerald-400" />;
    if (scenario.scene_type.includes('stress')) return <AlertOctagon className="w-3.5 h-3.5 text-amber-400" />;
    return <Navigation className="w-3.5 h-3.5 text-cyan-400" />;
  };

  // Derive a short badge label for the challenge type
  const challengeBadge = scenario.is_synthetic_stress
    ? 'Stress Test'
    : scenario.has_smoke
    ? 'Smoke / Aerosol'
    : scenario.scene_type.includes('rain')
    ? 'Rain'
    : scenario.scene_type.includes('snow')
    ? 'Snow'
    : scenario.scene_type.includes('offroad') || scenario.terrain_type.includes('mud')
    ? 'Off-Road'
    : 'Urban';

  return (
    <div className="group relative bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/40 rounded-xl p-4 flex flex-col gap-3 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-950/20">

      {/* Header row */}
      <div className="flex items-center gap-2.5">
        <div className="p-1.5 rounded-md bg-slate-800 border border-slate-700 flex-shrink-0">
          {getIcon()}
        </div>
        <div className="flex items-center justify-between gap-2">
          <span className="px-2 py-1 rounded-md bg-slate-950 border border-slate-700 text-[10px] text-slate-300">
            {scenario.num_points?.toLocaleString() ?? '—'} points
          </span>
          {isSmallest && (
            <span className="px-2 py-1 rounded-md bg-emerald-950/70 border border-emerald-500/60 text-[10px] text-emerald-300 font-bold uppercase tracking-wide">
              Smallest point cloud
            </span>
          )}
        </div>
        <div className="min-w-0">
          <div className="text-[10px] text-cyan-400 font-semibold uppercase tracking-wider truncate">
            {scenario.dataset}
          </div>
          <h3 className="text-sm font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors leading-snug truncate">
            {scenario.title}
          </h3>
        </div>
      </div>

      {/* One-line description */}
      <p className="text-xs text-slate-400 leading-relaxed line-clamp-2 font-sans">
        {scenario.description}
      </p>
      <p className="text-[10px] text-amber-300/80 leading-relaxed font-mono">
        Scene: {scenario.scene_signature ?? scenario.scene_type}
      </p>

      {/* Tags + CTA */}
      <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-800/60">
        <div className="flex items-center gap-1.5">
          <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-slate-800 border border-slate-700 text-slate-400">
            {scenario.environment}
          </span>
          <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-cyan-950/60 border border-cyan-800/50 text-cyan-400">
            {challengeBadge}
          </span>
        </div>

        <button
          onClick={() => onSelect(scenario)}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs transition-all shadow-md shadow-cyan-500/20 hover:shadow-cyan-400/30 disabled:opacity-50 flex-shrink-0"
        >
          <Play className="w-3 h-3 fill-current" />
          <span>RUN</span>
        </button>
      </div>
    </div>
  );
};
