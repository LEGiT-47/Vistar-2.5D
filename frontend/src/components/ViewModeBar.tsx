import React from 'react';
import { ViewMode } from '../types';
import { Box, Layers, Palette, ShieldAlert, Zap, CheckCircle2, Sliders } from 'lucide-react';

interface ViewModeBarProps {
  currentMode: ViewMode;
  onSelectMode: (mode: ViewMode) => void;
  isComparisonActive: boolean;
  onToggleComparison: () => void;
}

export const ViewModeBar: React.FC<ViewModeBarProps> = ({
  currentMode,
  onSelectMode,
  isComparisonActive,
  onToggleComparison
}) => {
  const modes: { id: ViewMode; label: string; icon: React.ReactNode; desc: string }[] = [
    { id: 'LIDAR_3D', label: '3D LiDAR', icon: <Box className="w-3.5 h-3.5" />, desc: 'Raw/filtered 3D spherical point cloud' },
    { id: 'HEIGHT_25D', label: '2.5D Height', icon: <Layers className="w-3.5 h-3.5" />, desc: 'Extruded elevation surface' },
    { id: 'SEMANTIC', label: 'Semantic', icon: <Palette className="w-3.5 h-3.5" />, desc: '14-class robotics ontology' },
    { id: 'TRAVERSABILITY', label: 'Traversability', icon: <CheckCircle2 className="w-3.5 h-3.5" />, desc: 'Safe, Caution, Blocked' },
    { id: 'RISK_HAZARD', label: 'Risk / Hazards', icon: <ShieldAlert className="w-3.5 h-3.5" />, desc: 'Potholes, Walls, Steep Slopes' },
    { id: 'CONFIDENCE', label: 'Confidence', icon: <Sliders className="w-3.5 h-3.5" />, desc: 'Sensor trust & uncertainty' },
    { id: 'RESOLUTION_MAP', label: 'Adaptive Grid', icon: <Zap className="w-3.5 h-3.5" />, desc: '5cm / 10cm / 20cm / 50cm tiers' }
  ];

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-700/80 backdrop-blur shadow-2xl font-mono text-xs select-none">
      {modes.map(m => {
        const isActive = currentMode === m.id && !isComparisonActive;
        return (
          <button
            key={m.id}
            onClick={() => onSelectMode(m.id)}
            title={m.desc}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              isActive
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            {m.icon}
            <span>{m.label}</span>
          </button>
        );
      })}

      <div className="w-[1px] h-4 bg-slate-700 mx-1" />

      {/* Split-screen Comparison Button */}
      <button
        onClick={onToggleComparison}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all ${
          isComparisonActive
            ? 'bg-amber-400 text-slate-950 shadow-md shadow-amber-400/20'
            : 'text-amber-400/90 hover:text-amber-300 hover:bg-amber-950/40 border border-amber-500/30'
        }`}
        title="Toggle split-screen synchronized comparison (Fixed 5cm vs VISTAR Adaptive)"
      >
        <span>FIXED vs VISTAR</span>
      </button>
    </div>
  );
};
