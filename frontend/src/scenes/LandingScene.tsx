import React, { useState } from 'react';
import { Search, Sparkles } from 'lucide-react';
import { ScenarioMetadata } from '../types';
import { ScenarioCard } from '../components/ScenarioCard';

interface LandingSceneProps {
  scenarios: ScenarioMetadata[];
  onSelectScenario: (scenario: ScenarioMetadata) => void;
  isLoading: boolean;
}

export const LandingScene: React.FC<LandingSceneProps> = ({
  scenarios,
  onSelectScenario,
  isLoading
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('ALL');

  const categories = [
    { id: 'ALL',     label: 'All' },
    { id: 'URBAN',   label: 'Urban' },
    { id: 'OFFROAD', label: 'Off-Road' },
    { id: 'ADVERSE', label: 'Adverse Weather' },
    { id: 'STRESS',  label: 'Stress Tests' },
  ];

  const filteredScenarios = scenarios.filter((sc) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch =
      sc.title.toLowerCase().includes(q) ||
      sc.dataset.toLowerCase().includes(q) ||
      sc.challenge.toLowerCase().includes(q) ||
      sc.environment.toLowerCase().includes(q);
    if (!matchesSearch) return false;
    if (activeFilter === 'ALL') return true;
    if (activeFilter === 'URBAN') return sc.scene_type.includes('urban') || sc.scene_type.includes('residential') || sc.scene_type.includes('highway');
    if (activeFilter === 'OFFROAD') return sc.scene_type.includes('offroad') || sc.scene_type.includes('mountain');
    if (activeFilter === 'ADVERSE') return sc.has_smoke || sc.scene_type.includes('rain') || sc.scene_type.includes('snow');
    if (activeFilter === 'STRESS') return sc.is_synthetic_stress || sc.scene_type.includes('stress');
    return true;
  });

  return (
    <div className="flex-1 bg-slate-950 overflow-y-auto px-6 py-8 text-slate-100 font-mono">
      <div className="max-w-7xl mx-auto space-y-7">

        {/* ── Hero ─────────────────────────────────────────────────── */}
        <div className="relative rounded-2xl bg-gradient-to-br from-slate-900 to-cyan-950/30 border border-slate-800 p-7 overflow-hidden">
          {/* Decorative accent blobs */}
          <div className="pointer-events-none absolute -top-10 -right-10 w-48 h-48 rounded-full bg-cyan-500/5 blur-3xl" />
          <div className="pointer-events-none absolute bottom-0 left-1/2 w-64 h-32 rounded-full bg-indigo-500/5 blur-3xl" />

          <div className="relative z-10 flex flex-col sm:flex-row sm:items-center gap-6">
            <div className="flex-1 min-w-0">
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-[10px] font-semibold mb-3">
                <Sparkles className="w-3 h-3" />
                <span>SIH 2026 · Problem SIH26053</span>
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-white leading-snug mb-2">
                VISTAR-2.5D
                <span className="ml-2 text-cyan-400">Adaptive LiDAR Mapping</span>
              </h1>
              <p className="text-xs text-slate-400 leading-relaxed font-sans max-w-xl">
                Converts dense 3D LiDAR clouds into a lightweight semantic 2.5D terrain grid
                with automatic resolution scaling — near obstacles at 5 cm, distant terrain at 50 cm.
              </p>
            </div>

            {/* Key numbers — compact column */}
            <div className="flex sm:flex-col gap-4 sm:gap-2 text-right flex-shrink-0">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">Memory Saved</div>
                <div className="text-xl font-bold text-emerald-400">70–85%</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">Resolution Tiers</div>
                <div className="text-xl font-bold text-cyan-400">4</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">Mission Scenarios</div>
                <div className="text-xl font-bold text-purple-400">15</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Filter + Search ──────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-1 p-1 bg-slate-900 border border-slate-800 rounded-xl overflow-x-auto">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveFilter(cat.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  activeFilter === cat.id
                    ? 'bg-cyan-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-60">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search scenarios…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
        </div>

        {/* ── Mission Grid ─────────────────────────────────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredScenarios.map((sc) => (
            <ScenarioCard
              key={sc.id}
              scenario={sc}
              onSelect={onSelectScenario}
              isLoading={isLoading}
            />
          ))}
        </div>

        {filteredScenarios.length === 0 && (
          <div className="text-center py-16 text-slate-500 text-xs">
            No missions match "{searchQuery}".
          </div>
        )}
      </div>
    </div>
  );
};
