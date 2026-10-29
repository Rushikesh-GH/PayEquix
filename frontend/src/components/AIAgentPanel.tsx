import React, { useState } from 'react';
import { 
  Bot, Database, Search, Sparkles, CheckCircle2, 
  ArrowRight, Activity, Terminal, ShieldAlert 
} from 'lucide-react';
import { api } from '../services/api';
import { Card3D } from './Card3D';

interface AIAgentPanelProps {
  employeeId?: string;
  compaRatio?: number;
  bandPosition?: number;
  normalizedSalary?: number;
  bandMid?: number;
  title?: string;
}

export const AIAgentPanel: React.FC<AIAgentPanelProps> = ({
  employeeId = 'EMP-000001',
  compaRatio = 0.78,
  bandPosition = -12.4,
  normalizedSalary = 98000,
  bandMid = 125000,
  title = 'Senior Software Engineer',
}) => {
  const [activeTab, setActiveTab] = useState<'crew' | 'vector'>('crew');
  const [loading, setLoading] = useState(false);
  const [crewResult, setCrewResult] = useState<any | null>(null);

  // Vector Search state
  const [query, setQuery] = useState('compa-ratio compression and below band adjustment thresholds');
  const [vectorResults, setVectorResults] = useState<any | null>(null);
  const [vectorLoading, setVectorLoading] = useState(false);

  const handleRunCrew = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        compa_ratio: compaRatio.toString(),
        band_position: bandPosition.toString(),
        normalized_salary: normalizedSalary.toString(),
        band_mid: bandMid.toString(),
        title,
      });
      const data = await api.getCrewTriage(employeeId, params.toString());
      setCrewResult(data);
    } catch (e) {
      console.error('Crew triage failed', e);
    } finally {
      setLoading(false);
    }
  };

  const handleVectorSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query) return;
    setVectorLoading(true);
    try {
      const data = await api.searchPoliciesVector(query, 3);
      setVectorResults(data);
    } catch (e) {
      console.error('Vector search failed', e);
    } finally {
      setVectorLoading(false);
    }
  };

  return (
    <Card3D glowColor="purple" tiltStrength={6} depth={16} className="p-5 my-6 bg-slate-900/90 border border-indigo-500/40 text-slate-100 shadow-2xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-4 border-b border-indigo-500/30 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-white shadow-md">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <span>Agentic AI & Vector Intelligence Copilot</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                CrewAI + Pinecone Architecture
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Multi-agent review collaboration with semantic vector search & LLM observability telemetry.
            </p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center space-x-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-xs font-medium">
          <button
            onClick={() => setActiveTab('crew')}
            className={`px-3 py-1 rounded-lg transition-all ${
              activeTab === 'crew' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            CrewAI Triage
          </button>
          <button
            onClick={() => {
              setActiveTab('vector');
              if (!vectorResults) handleVectorSearch();
            }}
            className={`px-3 py-1 rounded-lg transition-all ${
              activeTab === 'vector' ? 'bg-purple-600 text-white shadow-xs' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Vector DB Search
          </button>
        </div>
      </div>

      {/* Tab 1: CrewAI Multi-Agent Pipeline */}
      {activeTab === 'crew' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-xs gap-3">
            <div className="space-y-0.5">
              <span className="text-slate-400">Target Candidate:</span>
              <div className="font-bold text-white flex items-center gap-2">
                <span>{employeeId} • {title}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                  compaRatio < 0.85 ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                }`}>
                  Compa-Ratio: {compaRatio.toFixed(2)}
                </span>
              </div>
            </div>

            <button
              onClick={handleRunCrew}
              disabled={loading}
              className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 shadow-md shadow-indigo-500/25 transition-all disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{loading ? 'Orchestrating Agents...' : 'Run CrewAI Triage'}</span>
            </button>
          </div>

          {crewResult ? (
            <div className="space-y-3">
              {/* Executive Summary */}
              <div className="bg-indigo-950/40 border border-indigo-500/30 p-3.5 rounded-xl text-xs space-y-1.5">
                <div className="font-bold text-indigo-300 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Synthesized Proposal Decision</span>
                  <span className="font-mono text-[10px] bg-indigo-500/20 px-2 py-0.5 rounded text-indigo-200">
                    Action: {crewResult.action_code}
                  </span>
                </div>
                <p className="text-slate-200 leading-relaxed text-[11px]">{crewResult.executive_summary}</p>
              </div>

              {/* Agent Collaboration Trace */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block font-mono">
                  Agent Pipeline Execution Trace (LangGraph Sequential DAG)
                </span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
                  {crewResult.pipeline_trace?.map((step: any, idx: number) => (
                    <div key={idx} className="bg-slate-950/70 border border-slate-800 p-2.5 rounded-xl space-y-1">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-bold text-purple-300">{step.agent}</span>
                        <span className="text-[10px] font-mono text-emerald-400">{step.latency_ms}ms</span>
                      </div>
                      <p className="text-slate-400 text-[10px] leading-tight">{step.observation}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Telemetry Observability */}
              <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800 text-[10px] font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-3">
                  <span>Tokens: <strong className="text-slate-200">{crewResult.observability?.total_tokens_evaluated}</strong></span>
                  <span>Vector Lookups: <strong className="text-slate-200">{crewResult.observability?.vector_db_lookups}</strong></span>
                  <span>Confidence: <strong className="text-emerald-400">{(crewResult.observability?.confidence_score * 100).toFixed(0)}%</strong></span>
                </div>
                <div className="flex items-center space-x-1.5">
                  {crewResult.observability?.guardrail_checks?.map((chk: string) => (
                    <span key={chk} className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                      ✓ {chk}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 text-xs text-slate-400 bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
              Click <strong>"Run CrewAI Triage"</strong> to simulate autonomous multi-agent analysis with Disparity, Compliance, and Proposal Synthesizer agents.
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Pinecone/Weaviate Vector DB Search */}
      {activeTab === 'vector' && (
        <div className="space-y-3">
          <form onSubmit={handleVectorSearch} className="flex gap-2 text-xs">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Query policies via cosine similarity embeddings..."
                className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-hidden focus:border-purple-500"
              />
            </div>
            <button
              type="submit"
              disabled={vectorLoading}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-colors"
            >
              {vectorLoading ? 'Searching Vector Index...' : 'Vector Search'}
            </button>
          </form>

          {/* Results */}
          {vectorResults && (
            <div className="space-y-2">
              <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between">
                <span>Index: <strong>{vectorResults.vector_index}</strong> (Cosine Similarity • {vectorResults.dimension}-D Vectors)</span>
                <span>Matches: {vectorResults.results_count}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
                {vectorResults.results?.map((doc: any) => (
                  <div key={doc.id} className="bg-slate-950/80 p-3 rounded-xl border border-purple-500/30 text-xs space-y-1.5 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between text-[10px] font-mono">
                        <span className="text-purple-400 font-bold">{doc.id}</span>
                        <span className="px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 font-bold">
                          Score: {(doc.similarity_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <h4 className="font-bold text-white text-xs mt-1">{doc.title}</h4>
                      <p className="text-[11px] text-slate-300 mt-1 leading-snug">{doc.content}</p>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 pt-1 border-t border-slate-800">
                      Category: {doc.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Card3D>
  );
};
