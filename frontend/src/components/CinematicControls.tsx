import React from 'react';
import { Play, Pause, SkipBack, SkipForward, RotateCcw, Award } from 'lucide-react';
import { STAGE_DEFINITIONS } from './stageDefinitions';


interface CinematicControlsProps {
  currentStage: number;
  totalStages: number;
  isPlaying: boolean;
  isDataReady: boolean;
  onNextStage: () => void;
  onPrevStage: () => void;
  onTogglePlay: () => void;
  onReplayStage: () => void;
  onSelectStage: (stage: number) => void;
  onOpenReport: () => void;
}

export const CinematicControls: React.FC<CinematicControlsProps> = ({
  currentStage,
  totalStages,
  isPlaying,
  isDataReady,
  onNextStage,
  onPrevStage,
  onTogglePlay,
  onReplayStage,
  onSelectStage,
  onOpenReport
}) => {
  const currentInfo = STAGE_DEFINITIONS[currentStage - 1] || STAGE_DEFINITIONS[0];

  return (
    <div className="flex-none bg-slate-900/95 border-t border-slate-800 px-6 py-3 select-none backdrop-blur z-20">
      {/* Stage Dots & Scrubber */}
      <div className="flex items-center justify-between gap-1 mb-3">
        {STAGE_DEFINITIONS.map((def) => {
          const isCurrent = def.stage === currentStage;
          const isPassed = def.stage < currentStage;
          return (
            <button
              key={def.stage}
              onClick={() => onSelectStage(def.stage)}
              title={`Stage ${def.stage}: ${def.title}`}
              className={`flex-1 h-1.5 rounded-full transition-all duration-300 ${
                isCurrent
                  ? 'bg-cyan-400 shadow-md shadow-cyan-400/50 scale-y-125'
                  : isPassed
                  ? 'bg-cyan-700/60 hover:bg-cyan-500'
                  : 'bg-slate-800 hover:bg-slate-700'
              }`}
            />
          );
        })}
      </div>

      {/* Main Control Strip */}
      <div className="flex items-center justify-between gap-4">
        {/* Stage Title and Description */}
        <div className="flex items-center gap-3">
          <div className="px-2.5 py-1 rounded bg-cyan-950 border border-cyan-800 text-cyan-400 font-mono text-xs font-bold">
            STAGE {currentStage}/{totalStages}
          </div>
          <div>
            <div className="text-xs font-bold text-slate-100 font-mono">{currentInfo.title}</div>
            <div className="text-[11px] text-slate-400 font-mono line-clamp-1">{currentInfo.desc}</div>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-2 font-mono">
          {!isDataReady && (
            <span className="text-[10px] text-slate-500 font-mono mr-1">Processing pipeline…</span>
          )}
          <button
            onClick={onPrevStage}
            disabled={currentStage <= 1 || !isDataReady}
            className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 border border-slate-700 transition-all"
            title="Previous Stage (Back)"
          >
            <SkipBack className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={onTogglePlay}
            disabled={!isDataReady}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 font-bold text-xs transition-all shadow-md shadow-cyan-500/20"
          >
            {isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>PAUSE</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>PLAY</span>
              </>
            )}
          </button>

          <button
            onClick={onNextStage}
            disabled={currentStage >= totalStages || !isDataReady}
            className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 border border-slate-700 transition-all"
            title="Next Stage"
          >
            <SkipForward className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={onReplayStage}
            className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition-all"
            title="Replay Current Stage"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          {/* Mission Report Button */}
          <button
            onClick={onOpenReport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-800/60 text-xs font-bold transition-all ml-2"
          >
            <Award className="w-3.5 h-3.5 text-cyan-400" />
            <span>MISSION REPORT</span>
          </button>
        </div>
      </div>
    </div>
  );
};
