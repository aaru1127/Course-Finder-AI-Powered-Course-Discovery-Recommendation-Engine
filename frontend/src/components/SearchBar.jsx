import React from 'react';
import { Search, Sparkles, X, Zap, Cpu, KeyRound, Layers } from 'lucide-react';

const EXAMPLE_QUERIES = [
  "Beginner backend development using Node.js under 20 hours",
  "Advanced React performance optimization and architecture",
  "Machine learning with Python and PyTorch",
  "Docker and Kubernetes cluster deployment for beginners",
  "Building RAG applications with LangChain and vector databases",
  "High performance system design with Redis caching"
];

export default function SearchBar({
  query,
  setQuery,
  searchMode,
  setSearchMode,
  onSearch,
  loading,
  searchMeta
}) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Search Input Box */}
      <div className="relative flex items-center">
        <div className="absolute left-4 text-slate-400 pointer-events-none">
          <Search className="w-5 h-5 text-blue-400" />
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe what you want to learn (e.g. 'I am a beginner who wants to learn backend with Node.js under 20 hours')..."
          className="w-full pl-12 pr-28 py-4 bg-slate-800/90 border border-slate-700/80 rounded-2xl text-slate-100 placeholder-slate-400 text-base focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-xl transition-all"
        />

        {query && (
          <button
            onClick={() => setQuery('')}
            className="absolute right-24 text-slate-400 hover:text-slate-200 p-1"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          onClick={onSearch}
          disabled={loading || !query.trim()}
          className="absolute right-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-xl text-sm shadow-md shadow-blue-600/30 disabled:opacity-50 transition-all"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Mode Switcher & Diagnostics Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Search Mode Radios */}
        <div className="flex items-center space-x-1 p-1 bg-slate-800/80 rounded-xl border border-slate-700/60">
          <button
            onClick={() => setSearchMode('hybrid')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              searchMode === 'hybrid'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-blue-300" />
            <span>Hybrid RRF (BM25 + pgvector)</span>
          </button>

          <button
            onClick={() => setSearchMode('semantic')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              searchMode === 'semantic'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-indigo-300" />
            <span>Dense Vector (all-MiniLM)</span>
          </button>

          <button
            onClick={() => setSearchMode('keyword')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              searchMode === 'keyword'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <KeyRound className="w-3.5 h-3.5 text-amber-300" />
            <span>BM25 Okapi (Lexical)</span>
          </button>
        </div>

        {/* Cache status badge */}
        {searchMeta && (
          <div className="flex items-center space-x-2">
            <div
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-mono text-xs border ${
                searchMeta.cache_status === 'HIT'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              <span>
                {searchMeta.cache_status === 'HIT' ? 'CACHE HIT (Redis)' : 'CACHE MISS (Dual Retrieval)'}
              </span>
              <span className="text-slate-400 font-sans">• {searchMeta.execution_time_ms} ms</span>
            </div>

            {searchMeta.extracted_filters && Object.keys(searchMeta.extracted_filters).length > 0 && (
              <div className="flex items-center space-x-1 text-slate-400">
                <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                <span>Extracted:</span>
                {searchMeta.extracted_filters.difficulty && (
                  <span className="px-1.5 py-0.5 rounded bg-blue-900/40 text-blue-300 border border-blue-800 text-[10px]">
                    {searchMeta.extracted_filters.difficulty}
                  </span>
                )}
                {searchMeta.extracted_filters.max_duration && (
                  <span className="px-1.5 py-0.5 rounded bg-blue-900/40 text-blue-300 border border-blue-800 text-[10px]">
                    &le; {searchMeta.extracted_filters.max_duration}h
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Suggested Prompt Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs text-slate-400">
        <span className="font-semibold whitespace-nowrap text-slate-500">Try queries:</span>
        {EXAMPLE_QUERIES.map((example, i) => (
          <button
            key={i}
            onClick={() => {
              setQuery(example);
              setTimeout(() => onSearch(example), 50);
            }}
            className="px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 hover:text-slate-200 border border-slate-700/60 whitespace-nowrap transition-colors"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}

