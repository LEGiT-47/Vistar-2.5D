import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Layers } from 'lucide-react';
import { ViewMode } from '../types';

interface LegendOverlayProps {
  viewMode: ViewMode;
}

export const LegendOverlay: React.FC<LegendOverlayProps> = ({ viewMode }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="absolute bottom-4 left-4 z-20 font-mono text-[11px] select-none">
      <div className="rounded-xl bg-slate-900/90 border border-slate-700/80 backdrop-blur shadow-2xl overflow-hidden transition-all duration-200">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-3 py-1.5 flex items-center justify-between gap-3 text-slate-300 hover:text-white bg-slate-800/60 transition-colors"
        >
          <div className="flex items-center gap-1.5 font-semibold text-cyan-400">
            <Layers className="w-3.5 h-3.5" />
            <span>LEGEND: {viewMode.replace('_', ' ')}</span>
          </div>
          {isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-slate-400" /> : <ChevronUp className="w-3.5 h-3.5 text-slate-400" />}
        </button>

        {isExpanded && (
          <div className="p-3 max-h-56 overflow-y-auto space-y-1.5 text-slate-300">
            {viewMode === 'RESOLUTION_MAP' && (
              <>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#00e5ff]" />
                  <span>5 cm (0–10m Near Field)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#3b82f6]" />
                  <span>10 cm (10–25m Mid-Near)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#64748b]" />
                  <span>20 cm (25–50m Mid-Far)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#334155]" />
                  <span>50 cm (50m+ Far Field)</span>
                </div>
                <div className="flex items-center gap-2 pt-1 border-t border-slate-800">
                  <div className="w-3 h-3 rounded bg-[#f59e0b]" />
                  <span className="text-amber-300 font-bold">Refined (Hazard/Roughness/Slope)</span>
                </div>
              </>
            )}

            {viewMode === 'TRAVERSABILITY' && (
              <>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#10b981]" />
                  <span>SAFE (Paved, Flat Road, Grass)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#f59e0b]" />
                  <span>CAUTION (Mud, Slope, Rut)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#ef4444]" />
                  <span>BLOCKED (Obstacle, Wall, Vehicle)</span>
                </div>
              </>
            )}

            {viewMode === 'RISK_HAZARD' && (
              <>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#8b5cf6]" />
                  <span>POTHOLE (Negative Elevation Defect)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#ef4444]" />
                  <span>OBSTACLE (Debris, Bollard, Rock)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#d946ef]" />
                  <span>WALL / BARRIER (Vertical Gradient)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#f97316]" />
                  <span>STEEP SLOPE (&gt; 18° Incline)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#06b6d4]" />
                  <span>WATER HAZARD</span>
                </div>
              </>
            )}

            {viewMode === 'SEMANTIC' && (
              <>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#3cb4f0]" />
                  <span>ROAD / LANE CORRIDOR</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#966e50]" />
                  <span>GROUND / DIRT</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#50c878]" />
                  <span>GRASS / LAWN</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#228b22]" />
                  <span>VEGETATION / TREES</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#ffa500]" />
                  <span>VEHICLE</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#ff4500]" />
                  <span>PEDESTRIAN</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#b22222]" />
                  <span>BUILDING</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#b0c4de]" />
                  <span>SMOKE / EXHAUST (Low-Conf)</span>
                </div>
              </>
            )}

            {(viewMode === 'LIDAR_3D' || viewMode === 'HEIGHT_25D' || viewMode === 'CONFIDENCE') && (
              <>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-2 rounded bg-gradient-to-r from-red-500 via-yellow-400 to-green-500" />
                  <span>Scale: Low to High</span>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
