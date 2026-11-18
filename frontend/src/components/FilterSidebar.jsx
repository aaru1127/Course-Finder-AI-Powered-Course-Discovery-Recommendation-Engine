import React from 'react';
import { Filter, RotateCcw, Clock, Award, DollarSign, FolderGit2 } from 'lucide-react';

export default function FilterSidebar({
  filters,
  setFilters,
  facets,
  onApplyFilters,
  onResetFilters
}) {
  const handleDifficultyChange = (diff) => {
    setFilters(prev => ({
      ...prev,
      difficulty: prev.difficulty === diff ? '' : diff
    }));
  };

  const handleCategoryChange = (e) => {
    setFilters(prev => ({
      ...prev,
      category: e.target.value
    }));
  };

  const handleDurationChange = (val) => {
    setFilters(prev => ({
      ...prev,
      max_duration: val ? Number(val) : null
    }));
  };

  return (
    <aside className="w-full lg:w-64 glass-panel rounded-2xl p-5 space-y-6 self-start">
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
        <div className="flex items-center space-x-2 text-slate-200 font-semibold text-sm">
          <Filter className="w-4 h-4 text-blue-400" />
          <span>Filters</span>
        </div>
        <button
          onClick={onResetFilters}
          className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      {/* Difficulty Level */}
      <div className="space-y-2">
        <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 uppercase tracking-wider">
          <Award className="w-3.5 h-3.5 text-blue-400" />
          <span>Difficulty</span>
        </label>
        <div className="grid grid-cols-3 gap-1.5">
          {['Beginner', 'Intermediate', 'Advanced'].map((diff) => (
            <button
              key={diff}
              onClick={() => handleDifficultyChange(diff)}
              className={`px-2 py-1.5 text-xs rounded-lg font-medium transition-all text-center border ${
                filters.difficulty === diff
                  ? 'bg-blue-600/30 text-blue-300 border-blue-500/60'
                  : 'bg-slate-800/60 text-slate-400 border-slate-700 hover:bg-slate-800'
              }`}
            >
              {diff}
            </button>
          ))}
        </div>
      </div>

      {/* Category */}
      <div className="space-y-2">
        <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 uppercase tracking-wider">
          <FolderGit2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Category</span>
        </label>
        <select
          value={filters.category || ''}
          onChange={handleCategoryChange}
          className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">All Categories</option>
          {facets?.categories?.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Max Duration Slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <label className="flex items-center space-x-1.5 font-semibold text-slate-300 uppercase tracking-wider">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>Max Duration</span>
          </label>
          <span className="font-mono text-blue-400 font-semibold">
            {filters.max_duration ? `< ${filters.max_duration} hrs` : 'Any'}
          </span>
        </div>
        <input
          type="range"
          min="5"
          max="50"
          step="5"
          value={filters.max_duration || 50}
          onChange={(e) => handleDurationChange(e.target.value === '50' ? null : e.target.value)}
          className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
          <span>5h</span>
          <span>15h</span>
          <span>30h</span>
          <span>Any</span>
        </div>
      </div>

      {/* Free Only Toggle */}
      <div className="pt-2 border-t border-slate-800">
        <label className="flex items-center justify-between cursor-pointer">
          <span className="flex items-center space-x-1.5 text-xs font-medium text-slate-300">
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
            <span>Free Courses Only</span>
          </span>
          <input
            type="checkbox"
            checked={filters.free_only || false}
            onChange={(e) => setFilters(prev => ({ ...prev, free_only: e.target.checked }))}
            className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-700 rounded focus:ring-blue-500 focus:ring-offset-slate-900"
          />
        </label>
      </div>

      {/* Provider Filter */}
      <div className="space-y-2 pt-2 border-t border-slate-800">
        <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
          Platform / Provider
        </label>
        <select
          value={filters.provider || ''}
          onChange={(e) => setFilters(prev => ({ ...prev, provider: e.target.value }))}
          className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">All Providers</option>
          {facets?.providers?.map((prov) => (
            <option key={prov} value={prov}>
              {prov}
            </option>
          ))}
        </select>
      </div>
    </aside>
  );
}
