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
      <div className="glass-panel rounded-3xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-blue-600 mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>Information Retrieval Benchmarking (Stage 8)</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Quantitative Retrieval & Caching Evaluation</h2>
          <p className="text-sm text-slate-600 max-w-2xl mt-1">
            Comparing Lexical Retrieval (BM25), Semantic Vector Search (all-MiniLM-L6-v2), and Hybrid Reciprocal Rank Fusion (RRF) across 25 ground-truth benchmark queries.
          </p>
        </div>

        <button
          onClick={() => loadBenchmark(true)}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Evaluating Queries...' : 'Rerun Benchmark'}</span>
        </button>
      </div>

      {benchmark && (
        <>
          {/* Redis Caching Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass-panel rounded-2xl p-5 border-l-4 border-l-amber-500 shadow-sm">
              <span className="text-xs text-slate-500 block mb-1">Cache Miss Latency (Full Retrieval)</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-mono">
                  {benchmark.redis_cache_benchmark.cache_miss_latency_ms}
                </span>
                <span className="text-xs text-slate-500 font-mono">ms</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block">BM25 + pgvector + RRF</span>
            </div>

            <div className="glass-panel rounded-2xl p-5 border-l-4 border-l-emerald-500 shadow-sm">
              <span className="text-xs text-slate-500 block mb-1">Cache Hit Latency (Redis In-Memory)</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-emerald-600 font-mono">
                  {benchmark.redis_cache_benchmark.cache_hit_latency_ms}
                </span>
                <span className="text-xs text-emerald-600 font-mono">ms</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block">Cache-Aside JSON deserialization</span>
            </div>

            <div className="glass-panel rounded-2xl p-5 border-l-4 border-l-blue-500 shadow-sm">
              <span className="text-xs text-slate-500 block mb-1">Redis Speedup Factor</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-blue-600 font-mono">
                  {benchmark.redis_cache_benchmark.speedup_factor}x
                </span>
                <span className="text-xs text-blue-600 font-medium">faster</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block">
                Backend: {benchmark.redis_cache_benchmark.backend_in_use}
              </span>
            </div>
          </div>

          {/* Retrieval Quality Comparison Table */}
          <div className="glass-panel rounded-2xl overflow-hidden border border-slate-200 shadow-sm">
            <div className="p-5 border-b border-slate-200 flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <Award className="w-5 h-5 text-amber-500" />
                <span>Strategy Retrieval Performance (Top K = {benchmark.k})</span>
              </h3>
              <span className="text-xs font-mono text-slate-500">
                {benchmark.total_queries} Benchmark Test Queries
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead className="bg-slate-100/80 text-slate-600 uppercase text-[11px] tracking-wider">
                  <tr>
                    <th className="py-3.5 px-5">Strategy</th>
                    <th className="py-3.5 px-4 font-mono">Precision@10</th>
                    <th className="py-3.5 px-4 font-mono">Recall@10</th>
                    <th className="py-3.5 px-4 font-mono">NDCG@10</th>
                    <th className="py-3.5 px-4 font-mono">MRR</th>
                    <th className="py-3.5 px-5 font-mono">Avg Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {Object.entries(benchmark.strategies).map(([key, item]) => {
                    const isHybrid = key === 'hybrid';
                    return (
                      <tr
                        key={key}
                        className={`${isHybrid ? 'bg-blue-50/70 font-semibold' : 'hover:bg-slate-50'}`}
                      >
                        <td className="py-4 px-5">
                          <div className="flex items-center space-x-2">
                            {key === 'hybrid' && <Layers className="w-4 h-4 text-blue-600" />}
                            {key === 'vector' && <Cpu className="w-4 h-4 text-indigo-600" />}
                            {key === 'bm25' && <KeyRound className="w-4 h-4 text-amber-600" />}
                            <span className="text-slate-900 uppercase font-bold text-xs">
                              {key === 'hybrid' ? 'Hybrid RRF (Combined)' : key}
                            </span>
                            {isHybrid && (
                              <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 border border-blue-200 text-[10px]">
                                Recommended
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-4 px-4 font-mono font-bold text-slate-900">
                          {(item.metrics.precision_at_k * 100).toFixed(1)}%
                        </td>
                        <td className="py-4 px-4 font-mono text-slate-600">
                          {(item.metrics.recall_at_k * 100).toFixed(1)}%
                        </td>
                        <td className="py-4 px-4 font-mono font-bold text-emerald-600">
                          {item.metrics.ndcg_at_k.toFixed(4)}
                        </td>
                        <td className="py-4 px-4 font-mono text-slate-600">
                          {item.metrics.mrr.toFixed(4)}
                        </td>
                        <td className="py-4 px-5 font-mono text-slate-500">
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
            <div className="glass-panel rounded-2xl p-6 space-y-4 shadow-sm">
              <h4 className="text-sm font-bold text-slate-900 flex items-center justify-between">
                <span>Precision@10 Comparison</span>
                <span className="text-xs font-normal text-slate-500">Higher is better</span>
              </h4>

              <div className="space-y-3">
                {Object.entries(benchmark.strategies).map(([key, item]) => (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-700 uppercase font-semibold">{key}</span>
                      <span className="text-slate-900 font-bold">
                        {(item.metrics.precision_at_k * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full h-3 bg-slate-100 border border-slate-200 rounded-full overflow-hidden">
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
            <div className="glass-panel rounded-2xl p-6 space-y-4 shadow-sm">
              <h4 className="text-sm font-bold text-slate-900 flex items-center justify-between">
                <span>NDCG@10 Ranking Quality</span>
                <span className="text-xs font-normal text-slate-500">Discounted Cumulative Gain</span>
              </h4>

              <div className="space-y-3">
                {Object.entries(benchmark.strategies).map(([key, item]) => (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-700 uppercase font-semibold">{key}</span>
                      <span className="text-emerald-600 font-bold">
                        {item.metrics.ndcg_at_k.toFixed(4)}
                      </span>
                    </div>
                    <div className="w-full h-3 bg-slate-100 border border-slate-200 rounded-full overflow-hidden">
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

