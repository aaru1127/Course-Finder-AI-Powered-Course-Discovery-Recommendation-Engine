import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Zap, RefreshCw, Cpu, Layers, KeyRound, Award, CheckCircle2 } from 'lucide-react';
import { getBenchmarkMetrics } from '../services/api';

export default function EvaluationDashboard() {
  const [benchmark, setBenchmark] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBenchmark(false);
  }, []);

  const loadBenchmark = async (force) => {
    try {
      setLoading(true);
      const data = await getBenchmarkMetrics(force);
      setBenchmark(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getBarWidth = (val) => `${Math.round(val * 100)}%`;

  return (
    <div className="space-y-8 animate-in fade-in">
      {/* Header card */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-blue-400 mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>Information Retrieval Benchmarking (Stage 8)</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white">Quantitative Retrieval & Caching Evaluation</h2>
          <p className="text-sm text-slate-400 max-w-2xl mt-1">
            Comparing Lexical Retrieval (BM25), Semantic Vector Search (all-MiniLM-L6-v2), and Hybrid Reciprocal Rank Fusion (RRF) across 25 ground-truth benchmark queries.
          </p>
        </div>

        <button
          onClick={() => loadBenchmark(true)}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Evaluating Queries...' : 'Rerun Benchmark'}</span>
        </button>
      </div>

      {benchmark && (
        <>
          {/* Redis Caching Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass-panel rounded-2xl p-5 border-l-4 border-l-amber-500">
              <span className="text-xs text-slate-400 block mb-1">Cache Miss Latency (Full Retrieval)</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">
                  {benchmark.redis_cache_benchmark.cache_miss_latency_ms}
                </span>
                <span className="text-xs text-slate-400 font-mono">ms</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block">BM25 + pgvector + RRF</span>
            </div>

            <div className="glass-panel rounded-2xl p-5 border-l-4 border-l-emerald-500">
              <span className="text-xs text-slate-400 block mb-1">Cache Hit Latency (Redis In-Memory)</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-emerald-400 font-mono">
                  {benchmark.redis_cache_benchmark.cache_hit_latency_ms}
                </span>
                <span className="text-xs text-emerald-400 font-mono">ms</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block">Cache-Aside JSON deserialization</span>
            </div>

            <div className="glass-panel rounded-2xl p-5 border-l-4 border-l-blue-500">
              <span className="text-xs text-slate-400 block mb-1">Redis Speedup Factor</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-blue-400 font-mono">
                  {benchmark.redis_cache_benchmark.speedup_factor}x
                </span>
                <span className="text-xs text-blue-300 font-medium">faster</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block">
                Backend: {benchmark.redis_cache_benchmark.backend_in_use}
              </span>
            </div>
          </div>

          {/* Retrieval Quality Comparison Table */}
          <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Award className="w-5 h-5 text-amber-400" />
                <span>Strategy Retrieval Performance (Top K = {benchmark.k})</span>
              </h3>
              <span className="text-xs font-mono text-slate-400">
                {benchmark.total_queries} Benchmark Test Queries
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead className="bg-slate-800/80 text-slate-400 uppercase text-[11px] tracking-wider">
                  <tr>
                    <th className="py-3.5 px-5">Strategy</th>
                    <th className="py-3.5 px-4 font-mono">Precision@10</th>
                    <th className="py-3.5 px-4 font-mono">Recall@10</th>
                    <th className="py-3.5 px-4 font-mono">NDCG@10</th>
                    <th className="py-3.5 px-4 font-mono">MRR</th>
                    <th className="py-3.5 px-5 font-mono">Avg Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {Object.entries(benchmark.strategies).map(([key, item]) => {
                    const isHybrid = key === 'hybrid';
                    return (
                      <tr
                        key={key}
                        className={`${isHybrid ? 'bg-blue-600/10 font-semibold' : 'hover:bg-slate-800/40'}`}
                      >
                        <td className="py-4 px-5">
                          <div className="flex items-center space-x-2">
                            {key === 'hybrid' && <Layers className="w-4 h-4 text-blue-400" />}
                            {key === 'vector' && <Cpu className="w-4 h-4 text-indigo-400" />}
                            {key === 'bm25' && <KeyRound className="w-4 h-4 text-amber-400" />}
                            <span className="text-white uppercase font-bold text-xs">
                              {key === 'hybrid' ? 'Hybrid RRF (Combined)' : key}
                            </span>
                            {isHybrid && (
                              <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 text-[10px]">
                                Recommended
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-4 px-4 font-mono font-bold text-slate-100">
                          {(item.metrics.precision_at_k * 100).toFixed(1)}%
                        </td>
                        <td className="py-4 px-4 font-mono text-slate-300">
                          {(item.metrics.recall_at_k * 100).toFixed(1)}%
                        </td>
                        <td className="py-4 px-4 font-mono font-bold text-emerald-400">
                          {item.metrics.ndcg_at_k.toFixed(4)}
                        </td>
                        <td className="py-4 px-4 font-mono text-slate-300">
                          {item.metrics.mrr.toFixed(4)}
                        </td>
                        <td className="py-4 px-5 font-mono text-slate-400">
                          {item.avg_latency_ms} ms
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Visual Comparison Progress Bars */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Precision@10 */}
            <div className="glass-panel rounded-2xl p-6 space-y-4">
              <h4 className="text-sm font-bold text-white flex items-center justify-between">
                <span>Precision@10 Comparison</span>
                <span className="text-xs font-normal text-slate-400">Higher is better</span>
              </h4>

              <div className="space-y-3">
                {Object.entries(benchmark.strategies).map(([key, item]) => (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-300 uppercase">{key}</span>
                      <span className="text-slate-200 font-bold">
                        {(item.metrics.precision_at_k * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${
                          key === 'hybrid'
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-500'
                            : key === 'vector'
                            ? 'bg-indigo-500'
                            : 'bg-amber-500'
                        }`}
                        style={{ width: getBarWidth(item.metrics.precision_at_k) }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* NDCG@10 */}
            <div className="glass-panel rounded-2xl p-6 space-y-4">
              <h4 className="text-sm font-bold text-white flex items-center justify-between">
                <span>NDCG@10 Ranking Quality</span>
                <span className="text-xs font-normal text-slate-400">Discounted Cumulative Gain</span>
              </h4>

              <div className="space-y-3">
                {Object.entries(benchmark.strategies).map(([key, item]) => (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-300 uppercase">{key}</span>
                      <span className="text-emerald-400 font-bold">
                        {item.metrics.ndcg_at_k.toFixed(4)}
                      </span>
                    </div>
                    <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${
                          key === 'hybrid'
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-500'
                            : key === 'vector'
                            ? 'bg-emerald-500'
                            : 'bg-amber-500'
                        }`}
                        style={{ width: getBarWidth(item.metrics.ndcg_at_k) }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
