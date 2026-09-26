import React, { useState, useEffect, useRef } from 'react';
import { ScenarioMetadata, PipelineResults, ViewMode } from './types';
import { fetchScenarios, processScenario, triggerSensorDegradation, restoreSensor } from './services/api';
import { Header } from './components/Header';
import { LandingScene } from './scenes/LandingScene';
import { LidarViewport } from './three/LidarViewport';
import { ComparisonSplitView } from './three/ComparisonSplitView';
import { ViewModeBar } from './components/ViewModeBar';
import { OperatorDashboard } from './components/OperatorDashboard';
import { CinematicControls } from './components/CinematicControls';
import { MissionReportModal } from './components/MissionReportModal';
import { LegendOverlay } from './components/LegendOverlay';

// Pipeline stage labels shown in the loading screen
const LOADING_STAGES = [
  'Ingesting LiDAR scan stream…',
  'Voxel filtering & range normalization…',
  'RANSAC ground plane extraction…',
  'Semantic ontology classification…',
  'Low-confidence aerosol rejection…',
  'Dynamic object segregation…',
  'Terrain roughness analysis…',
  'Projecting to 2.5D adaptive grid…',
  'Foveated variable-resolution allocation…',
  'Route planning via A* hazard graph…',
  'Digital breadcrumb cache compaction…',
  'Copernicus DEM topographic fusion…',
  'Fixed 5cm benchmark comparison…',
  'Compiling mission telemetry…',
];

export function App() {
  const [scenarios, setScenarios] = useState<ScenarioMetadata[]>([]);
  const [activeScenario, setActiveScenario] = useState<ScenarioMetadata | null>(null);
  const [results, setResults] = useState<PipelineResults | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStageLabel, setLoadingStageLabel] = useState('');
  const [loadingElapsedSeconds, setLoadingElapsedSeconds] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>('LIDAR_3D');
  const [isComparisonActive, setIsComparisonActive] = useState(false);
  const [currentStage, setCurrentStage] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSensorDegraded, setIsSensorDegraded] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);

  const playTimerRef = useRef<number | null>(null);
  const loadingLabelTimerRef = useRef<number | null>(null);
  const loadingElapsedTimerRef = useRef<number | null>(null);

  // Load scenario list on mount
  useEffect(() => {
    fetchScenarios()
      .then(data => setScenarios(data))
      .catch(err => console.error('Error loading scenarios:', err));
  }, []);

  // Animate the loading stage labels while pipeline runs
  const startLoadingAnimation = () => {
    let idx = 0;
    const startedAt = performance.now();
    setLoadingStageLabel(LOADING_STAGES[0]);
    setLoadingElapsedSeconds(0);
    loadingLabelTimerRef.current = window.setInterval(() => {
      idx = (idx + 1) % LOADING_STAGES.length;
      setLoadingStageLabel(LOADING_STAGES[idx]);
    }, 900);
    loadingElapsedTimerRef.current = window.setInterval(() => {
      setLoadingElapsedSeconds(Math.floor((performance.now() - startedAt) / 1000));
    }, 250);
  };

  const stopLoadingAnimation = () => {
    if (loadingLabelTimerRef.current) {
      clearInterval(loadingLabelTimerRef.current);
      loadingLabelTimerRef.current = null;
    }
    if (loadingElapsedTimerRef.current) {
      clearInterval(loadingElapsedTimerRef.current);
      loadingElapsedTimerRef.current = null;
    }
  };

  // Handle scenario selection
  const handleSelectScenario = async (sc: ScenarioMetadata) => {
    setActiveScenario(sc);
    setIsLoading(true);
    setCurrentStage(1);
    setIsPlaying(false);
    setIsSensorDegraded(false);
    setIsComparisonActive(false);
    setResults(null);

    startLoadingAnimation();

    try {
      const pipelineData = await processScenario(sc.id, {
        is_synthetic_stress: sc.is_synthetic_stress,
        start_point: sc.start,
        goal_point: sc.goal,
      });
      setResults(pipelineData);
      setViewMode('LIDAR_3D');
    } catch (err) {
      console.error('Pipeline execution failed:', err);
    } finally {
      stopLoadingAnimation();
      setIsLoading(false);
    }
  };

  // Cinematic auto-play loop
  useEffect(() => {
    if (isPlaying) {
      playTimerRef.current = window.setInterval(() => {
        setCurrentStage(prev => {
          if (prev >= 17) {
            setIsPlaying(false);
            setIsReportOpen(true);
            return 17;
          }
          return prev + 1;
        });
      }, 3200);
    } else if (playTimerRef.current) {
      clearInterval(playTimerRef.current);
    }
    return () => {
      if (playTimerRef.current) clearInterval(playTimerRef.current);
    };
  }, [isPlaying]);

  // Auto-switch view mode on stage change for cinematic storytelling
  useEffect(() => {
    if (!results) return;
    if (currentStage <= 4) {
      setViewMode('LIDAR_3D'); setIsComparisonActive(false);
    } else if (currentStage === 5) {
      setViewMode('SEMANTIC'); setIsComparisonActive(false);
    } else if (currentStage === 6) {
      setViewMode('CONFIDENCE'); setIsComparisonActive(false);
    } else if (currentStage === 7) {
      setViewMode('RISK_HAZARD'); setIsComparisonActive(false);
    } else if (currentStage >= 8 && currentStage <= 10) {
      setViewMode('RESOLUTION_MAP'); setIsComparisonActive(false);
    } else if (currentStage === 11 || currentStage === 12) {
      setViewMode('TRAVERSABILITY'); setIsComparisonActive(false);
    } else if (currentStage === 14) {
      setIsSensorDegraded(true); setIsComparisonActive(false);
    } else if (currentStage === 16) {
      setIsComparisonActive(true);
    } else if (currentStage === 17) {
      setIsReportOpen(true);
    }
  }, [currentStage, results]);

  const handleToggleSensorDegradation = async () => {
    if (!activeScenario) return;
    if (isSensorDegraded) {
      await restoreSensor(activeScenario.id);
      setIsSensorDegraded(false);
    } else {
      await triggerSensorDegradation(activeScenario.id);
      setIsSensorDegraded(true);
    }
  };

  return (
    <div className="flex flex-col w-screen h-screen bg-slate-950 overflow-hidden font-mono">
      <Header
        activeScenarioTitle={activeScenario?.title}
        onExitScenario={() => {
          setActiveScenario(null);
          setResults(null);
          setIsPlaying(false);
          setIsComparisonActive(false);
          setIsReportOpen(false);
        }}
        isSensorDegraded={isSensorDegraded}
        onToggleSensorDegradation={handleToggleSensorDegradation}
      />

      {!activeScenario ? (
        <LandingScene
          scenarios={scenarios}
          onSelectScenario={handleSelectScenario}
          isLoading={isLoading}
        />
      ) : (
        <div className="flex-1 flex flex-col relative min-h-0">

          {/* ── Blocking modal while the perception pipeline runs ── */}
          {isLoading && (
            <div
              className="fixed inset-0 flex items-center justify-center p-6"
              style={{
                zIndex: 2147483647,
                isolation: 'isolate',
                backgroundColor: 'rgba(2, 6, 23, 0.88)',
                backdropFilter: 'blur(8px)',
                WebkitBackdropFilter: 'blur(8px)',
              }}
              role="status"
              aria-live="polite"
              aria-label="Processing LiDAR pipeline"
            >
              <div
                className="w-full max-w-xl rounded-2xl px-8 py-10 flex flex-col items-center gap-7"
                style={{
                  backgroundColor: '#0f172a',
                  border: '2px solid rgba(34, 211, 238, 0.75)',
                  boxShadow: '0 25px 80px rgba(0, 0, 0, 0.75), 0 0 40px rgba(8, 145, 178, 0.25)',
                }}
              >
                {/* Pulsing radar ring */}
                <div className="relative w-32 h-32 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-2 border-cyan-500/20 animate-ping" />
                  <div className="absolute inset-3 rounded-full border-2 border-cyan-400/40 animate-ping" style={{ animationDelay: '0.3s' }} />
                  <div className="absolute inset-7 rounded-full border-2 border-cyan-300/60 animate-ping" style={{ animationDelay: '0.6s' }} />
                  <div className="w-5 h-5 rounded-full bg-cyan-400 shadow-lg shadow-cyan-400/60" />
                </div>

                <div className="text-center space-y-3">
                  <div className="text-cyan-300 font-bold text-2xl tracking-[0.2em] uppercase">
                    Processing pipeline
                  </div>
                  <div className="text-white text-lg font-semibold">
                    LiDAR data is being processed
                  </div>
                  <div className="text-slate-300 text-sm font-mono">
                    {loadingStageLabel || 'Loading scenario data…'}
                  </div>
                </div>

                {/* Progress bar shimmer */}
                <div className="w-full max-w-md h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-transparent via-cyan-400 to-transparent w-1/2 animate-[shimmer_1.2s_ease-in-out_infinite]" />
                </div>

                <div className="flex flex-col items-center gap-1 text-xs font-mono">
                  <div className="text-slate-300">{activeScenario?.title}</div>
                  <div className="text-slate-500">Elapsed: {loadingElapsedSeconds}s · Please wait</div>
                </div>
              </div>
            </div>
          )}

          <ViewModeBar
            currentMode={viewMode}
            onSelectMode={(mode) => { setViewMode(mode); setIsComparisonActive(false); }}
            isComparisonActive={isComparisonActive}
            onToggleComparison={() => setIsComparisonActive(!isComparisonActive)}
          />

          <div className="flex-1 relative min-h-0">
            {isComparisonActive && results ? (
              <ComparisonSplitView results={results} />
            ) : (
              <LidarViewport
                payload={results?.vis_payload || null}
                viewMode={viewMode}
                stageIndex={currentStage}
                isSensorDegraded={isSensorDegraded}
                showDEM={currentStage >= 15 || currentStage === 1}
              />
            )}
            {!isComparisonActive && <LegendOverlay viewMode={viewMode} />}
          </div>

          <CinematicControls
            currentStage={currentStage}
            totalStages={17}
            isPlaying={isPlaying}
            isDataReady={!isLoading && results !== null}
            onNextStage={() => setCurrentStage(s => Math.min(17, s + 1))}
            onPrevStage={() => setCurrentStage(s => Math.max(1, s - 1))}
            onTogglePlay={() => setIsPlaying(!isPlaying)}
            onReplayStage={() => {
              const s = currentStage;
              setCurrentStage(1);
              setTimeout(() => setCurrentStage(s), 50);
            }}
            onSelectStage={(s) => setCurrentStage(s)}
            onOpenReport={() => setIsReportOpen(true)}
          />

          <OperatorDashboard
            results={results}
            scenarioTitle={activeScenario.title}
            isSensorDegraded={isSensorDegraded}
          />

          <MissionReportModal
            isOpen={isReportOpen}
            onClose={() => setIsReportOpen(false)}
            results={results}
            scenario={activeScenario}
            onReplayMission={() => {
              setIsReportOpen(false);
              setCurrentStage(1);
              setIsPlaying(true);
            }}
            onCompareAnother={() => {
              setIsReportOpen(false);
              setActiveScenario(null);
              setResults(null);
            }}
          />
        </div>
      )}
    </div>
  );
}

export default App;
