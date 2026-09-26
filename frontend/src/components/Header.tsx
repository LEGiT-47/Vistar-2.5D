import React from 'react';
import { ShieldCheck, Cpu, Radio, RotateCcw, AlertTriangle } from 'lucide-react';

interface HeaderProps {
  activeScenarioTitle?: string;
  onExitScenario?: () => void;
  isSensorDegraded?: boolean;
  onToggleSensorDegradation?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeScenarioTitle,
  onExitScenario,
  isSensorDegraded,
  onToggleSensorDegradation
}) => {
  return (
    <header className="flex-none h-14 bg-slate-900/95 border-b border-slate-800 px-6 flex items-center justify-between z-30 select-none backdrop-blur">
      {/* Brand & Project Identity */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <span className="font-mono font-black text-slate-950 text-sm tracking-tighter">V2.5</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-wider text-slate-100 font-mono">VISTAR-2.5D</h1>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800">
                SIH26053
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono">
              Adaptive Variable Resolution 2.5D LiDAR Perception
            </p>
          </div>
        </div>

        {activeScenarioTitle && (
          <div className="flex items-center gap-2 pl-4 border-l border-slate-800">
            <span className="text-xs text-slate-400 font-mono">MISSION:</span>
            <span className="text-xs font-semibold text-cyan-400 font-mono">{activeScenarioTitle}</span>
          </div>
        )}
      </div>

      {/* Middle: System Architecture & Status Badges */}
      <div className="hidden lg:flex items-center gap-3">
        {/* ML Execution Mode */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800/80 border border-slate-700/80 text-[11px] font-mono text-slate-300">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span>MODE B: DATASET REPLAY (Verified Annotations)</span>
        </div>

        {/* ROS 2 Architecture */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800/80 border border-slate-700/80 text-[11px] font-mono text-slate-300">
          <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>ROS 2 DDS: ACTIVE</span>
        </div>

        {/* Scientific Transparency */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800/80 border border-slate-700/80 text-[11px] font-mono text-emerald-300">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>SCIENTIFIC HONESTY COMPLIANT</span>
        </div>
      </div>

      {/* Right Action Buttons */}
      <div className="flex items-center gap-3">
        {activeScenarioTitle && onToggleSensorDegradation && (
          <button
            onClick={onToggleSensorDegradation}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono font-semibold transition-all border ${
              isSensorDegraded
                ? 'bg-amber-500/20 text-amber-300 border-amber-500 animate-pulse'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
            }`}
            title="Simulate severe LiDAR attenuation to test breadcrumb cache"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>{isSensorDegraded ? 'RESTORE SENSOR' : 'SIMULATE DEGRADATION'}</span>
          </button>
        )}

        {activeScenarioTitle && onExitScenario && (
          <button
            onClick={onExitScenario}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-mono transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>EXIT MISSION</span>
          </button>
        )}
      </div>
    </header>
  );
};
