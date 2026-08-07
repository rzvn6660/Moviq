import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  ShieldCheck, 
  Clock, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  BarChart3, 
  DollarSign, 
  RefreshCw,
  Server,
  Info
} from 'lucide-react';
import { MoviqApiClient } from '../services/apiClient';
import type { 
  ProviderHealthInfo, 
  RecommendProviderResponse, 
  CostEstimateResponse, 
  ProviderBenchmarkMetric 
} from '../types/video';

export const ProviderHealthPage: React.FC = () => {
  const [healthData, setHealthData] = useState<ProviderHealthInfo[]>([]);
  const [benchmarks, setBenchmarks] = useState<ProviderBenchmarkMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  // Recommender sandbox state
  const [promptInput, setPromptInput] = useState<string>('A high-speed cybernetic sports car drifting through rainy neon Tokyo');
  const [priorityInput, setPriorityInput] = useState<'quality' | 'speed' | 'cost' | 'local'>('quality');
  const [recommendation, setRecommendation] = useState<RecommendProviderResponse | null>(null);
  const [recommending, setRecommending] = useState<boolean>(false);

  // Estimator sandbox state
  const [modelInput, setModelInput] = useState<string>('kling-3.0/video');
  const [durationInput, setDurationInput] = useState<'5s' | '10s' | '15s'>('5s');
  const [costEstimate, setCostEstimate] = useState<CostEstimateResponse | null>(null);

  const fetchHealth = async (forceRefresh: boolean = false) => {
    if (forceRefresh) setRefreshing(true);
    try {
      const res = await MoviqApiClient.fetchProviderHealth(forceRefresh);
      setHealthData(res.providers || []);
      setLastUpdated(res.cached_at || new Date().toISOString());
    } catch (err) {
      console.error("Failed to load provider health:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchBenchmarks = async () => {
    try {
      const res = await MoviqApiClient.fetchProviderBenchmarks();
      setBenchmarks(res.benchmarks || []);
    } catch (err) {
      console.error("Failed to load benchmarks:", err);
    }
  };

  const handleRecommend = async () => {
    setRecommending(true);
    try {
      const res = await MoviqApiClient.recommendProvider({
        prompt: promptInput,
        priority: priorityInput
      });
      setRecommendation(res);
    } catch (err) {
      console.error("Recommendation query error:", err);
    } finally {
      setRecommending(false);
    }
  };

  const handleEstimate = async () => {
    try {
      const res = await MoviqApiClient.estimateCost({
        modelId: modelInput,
        duration: durationInput
      });
      setCostEstimate(res);
    } catch (err) {
      console.error("Cost estimation query error:", err);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchBenchmarks();
    handleRecommend();
    handleEstimate();

    const interval = setInterval(() => fetchHealth(false), 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    handleEstimate();
  }, [modelInput, durationInput]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ONLINE':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3.5 h-3.5" /> ONLINE</span>;
      case 'DEGRADED':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20"><AlertTriangle className="w-3.5 h-3.5" /> DEGRADED</span>;
      case 'GPU_BUSY':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20"><Clock className="w-3.5 h-3.5" /> GPU BUSY</span>;
      case 'AUTH_FAILED':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20"><ShieldCheck className="w-3.5 h-3.5" /> AUTH FAILED</span>;
      case 'QUOTA_EXHAUSTED':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20"><DollarSign className="w-3.5 h-3.5" /> QUOTA EXHAUSTED</span>;
      case 'CONFIG_MISSING':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20"><Info className="w-3.5 h-3.5" /> CONFIG MISSING</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20"><XCircle className="w-3.5 h-3.5" /> OFFLINE</span>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
                Provider Operations & Intelligence
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Real-time health telemetry, AI recommendation rules, and empirical execution benchmarks.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 font-mono">
            Cached: {lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : 'Refreshing...'}
          </span>
          <button
            onClick={() => fetchHealth(true)}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh Health'}
          </button>
        </div>
      </div>

      {/* Grid 1: Provider Live Health Cards */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
          <Server className="w-5 h-5 text-cyan-400" />
          Provider Node Telemetry (v2.1 Unified Backplane)
        </h2>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-44 rounded-xl bg-slate-900/60 border border-slate-800/60 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {healthData.map((node) => (
              <div 
                key={node.provider}
                className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700/80 transition-all shadow-xl backdrop-blur-sm space-y-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-base text-slate-100 capitalize">{node.provider} AI</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{node.available_models} Models Registered</p>
                  </div>
                  {getStatusBadge(node.status)}
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60">
                    <span className="text-slate-500 block">Ping Latency</span>
                    <span className="font-mono text-slate-200 font-semibold">{node.latency_ms > 0 ? `${node.latency_ms} ms` : 'Unknown'}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60">
                    <span className="text-slate-500 block">Queue Traffic</span>
                    <span className="font-mono text-slate-200 font-semibold">{node.queue_status}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    Est. Wait: <strong className="text-slate-300 font-mono">{node.estimated_wait}s</strong>
                  </span>
                  <span className="text-slate-500 font-mono">
                    {node.credits.known ? `Credits: ${node.credits.remaining}` : 'Credits: Unknown'}
                  </span>
                </div>

                {node.message && (
                  <p className="text-[11px] text-slate-400 bg-slate-950/80 p-2 rounded border border-slate-800/50 font-mono">
                    {node.message}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Grid 2: AI Recommender Sandbox & Cost Estimator Sandbox */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommendation Engine Widget */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4 shadow-xl">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-semibold text-slate-200">AI Provider Recommendation Engine</h2>
          </div>
          <p className="text-xs text-slate-400">
            Deterministic rule-based keyword & preference matching without arbitrary random scores.
          </p>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Target Prompt</label>
              <textarea
                value={promptInput}
                onChange={(e) => setPromptInput(e.target.value)}
                rows={2}
                className="w-full text-xs p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:border-amber-500/50 focus:outline-none resize-none"
              />
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Optimization Priority</label>
                <select
                  value={priorityInput}
                  onChange={(e: any) => setPriorityInput(e.target.value)}
                  className="text-xs p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200"
                >
                  <option value="quality">Quality First</option>
                  <option value="speed">Speed Optimized</option>
                  <option value="cost">Cost Saver</option>
                  <option value="local">Local GPU Privacy</option>
                </select>
              </div>

              <button
                onClick={handleRecommend}
                disabled={recommending}
                className="px-4 py-2 text-xs font-semibold rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 transition-all"
              >
                Evaluate Rules
              </button>
            </div>

            {recommendation && (
              <div className="p-4 rounded-xl bg-slate-950/80 border border-amber-500/20 space-y-2 mt-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Recommended Provider:</span>
                  <span className="text-sm font-bold text-amber-400 uppercase tracking-wide">
                    {recommendation.recommended_provider} ({recommendation.recommended_model_id})
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Confidence Score:</span>
                  <span className="text-xs font-mono font-bold text-emerald-400">{recommendation.confidence}%</span>
                </div>
                <p className="text-xs text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                  💡 {recommendation.reason}
                </p>
                <div className="text-[11px] text-slate-500 pt-1">
                  Fallbacks: {recommendation.fallback_providers.join(', ')}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Cost & Runtime Estimator Widget */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4 shadow-xl">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-semibold text-slate-200">Truthful Cost & Runtime Estimator</h2>
          </div>
          <p className="text-xs text-slate-400">
            Calculates documented pricing & runtime bounds. Displays "Unknown" if pricing is unverified.
          </p>

          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Target Model</label>
                <select
                  value={modelInput}
                  onChange={(e) => setModelInput(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                >
                  <option value="kling-3.0/video">Kling 3.0 Pro (Kie.ai)</option>
                  <option value="wan-2.1/video">Wan 2.1 T2V (Kie.ai)</option>
                  <option value="veo-3.1">Google Veo 3.1 (Kie.ai)</option>
                  <option value="dream-machine">Dream Machine (Luma AI)</option>
                  <option value="hailuo-01">MiniMax Video 01 (Hailuo AI)</option>
                  <option value="Wan-AI/Wan2.2-TI2V-5B">Wan2.2 5B (Hugging Face)</option>
                  <option value="Wan-AI/Wan2.1-T2V-1.3B-Diffusers">Wan2.1 Diffusers (Remote GPU)</option>
                  <option value="ltx-video">LTX Video 0.9 (Local GPU)</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Duration</label>
                <select
                  value={durationInput}
                  onChange={(e: any) => setDurationInput(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                >
                  <option value="5s">5 Seconds</option>
                  <option value="10s">10 Seconds</option>
                </select>
              </div>
            </div>

            {costEstimate && (
              <div className="p-4 rounded-xl bg-slate-950/80 border border-emerald-500/20 space-y-3 mt-3">
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                    <span className="text-slate-500 block">Est. Cost (USD)</span>
                    <span className="text-sm font-bold font-mono text-emerald-400">
                      {costEstimate.pricing_known && costEstimate.estimated_cost_usd !== null 
                        ? `$${costEstimate.estimated_cost_usd}` 
                        : 'Unknown'}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                    <span className="text-slate-500 block">Est. Runtime</span>
                    <span className="text-sm font-bold font-mono text-cyan-400">
                      ~{costEstimate.estimated_runtime_seconds}s
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span>Target Res: {costEstimate.resolution}</span>
                  <span>Est. Queue: {costEstimate.estimated_queue_seconds}s</span>
                </div>

                <p className="text-[11px] text-slate-400 font-mono border-t border-slate-800/60 pt-2">
                  ℹ️ {costEstimate.notes}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Grid 3: Provider Performance Benchmarks Table */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-400" />
          Empirical Provider Performance Benchmarks
        </h2>

        <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/70 shadow-xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="p-4">Provider / Engine</th>
                <th className="p-4">Avg Gen Time</th>
                <th className="p-4">Avg Queue Time</th>
                <th className="p-4">Success Rate</th>
                <th className="p-4">Motion Score</th>
                <th className="p-4">Realism Score</th>
                <th className="p-4">Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {benchmarks.map((b) => (
                <tr key={b.provider} className="hover:bg-slate-800/30 transition-all">
                  <td className="p-4 font-semibold text-slate-100 font-sans">
                    {b.name}
                  </td>
                  <td className="p-4 text-cyan-400 font-semibold">{b.avg_generation_time_seconds}s</td>
                  <td className="p-4 text-slate-400">{b.avg_queue_time_seconds}s</td>
                  <td className="p-4 text-emerald-400 font-semibold">{b.success_rate_percentage}%</td>
                  <td className="p-4 text-amber-400">{b.motion_quality_score} / 10</td>
                  <td className="p-4 text-indigo-400">{b.realism_score} / 10</td>
                  <td className="p-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {b.overall_rating}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
