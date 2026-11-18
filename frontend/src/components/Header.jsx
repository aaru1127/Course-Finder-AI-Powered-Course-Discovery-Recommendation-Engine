import React, { useState } from 'react';
import { Compass, Sparkles, BarChart3, Database, RefreshCw, Zap, Check } from 'lucide-react';
import { clearCache } from '../services/api';

export default function Header({ activeTab, setActiveTab, health }) {
  const [clearing, setClearing] = useState(false);
  const [clearedNotice, setClearedNotice] = useState(false);

  const handleClearCache = async () => {
    try {
      setClearing(true);
      await clearCache();
      setClearedNotice(true);
      setTimeout(() => setClearedNotice(false), 2500);
    } catch (e) {
      console.error(e);
    } finally {
      setClearing(false);
    }
  };

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/85 backdrop-blur-md shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('search')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20">
              <Compass className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-slate-900">CourseFinder</span>
                <span className="px-2 py-0.5 text-xs font-semibold bg-blue-50 text-blue-600 border border-blue-200 rounded-full">
                  Hybrid IR
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">Semantic Discovery & Recommendation Engine</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveTab('search')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'search'
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Compass className="w-4 h-4" />
              <span>Search Engine</span>
            </button>

            <button
              onClick={() => setActiveTab('recommend')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'recommend'
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>Personalized</span>
            </button>

            <button
              onClick={() => setActiveTab('benchmark')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'benchmark'
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <BarChart3 className="w-4 h-4 text-emerald-600" />
              <span>IR Evaluation</span>
            </button>
          </nav>

          {/* System Status Indicators */}
          <div className="hidden lg:flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700">
              <span className={`w-2 h-2 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span>{health?.courses_loaded || 358} Courses Indexed</span>
            </div>

            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700">
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              <span>Cache: {health?.cache_backend || 'Redis'}</span>
            </div>

            <button
              onClick={handleClearCache}
              disabled={clearing}
              title="Clear Redis Search Cache"
              className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 transition-colors"
            >
              {clearedNotice ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-emerald-600 font-medium">Flushed!</span>
                </>
              ) : (
                <>
                  <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${clearing ? 'animate-spin' : ''}`} />
                  <span>Flush Cache</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

