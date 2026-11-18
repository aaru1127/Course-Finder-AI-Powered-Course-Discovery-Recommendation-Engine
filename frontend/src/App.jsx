import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import FilterSidebar from './components/FilterSidebar';
import CourseCard from './components/CourseCard';
import CourseModal from './components/CourseModal';
import PersonalizationWizard from './components/PersonalizationWizard';
import EvaluationDashboard from './components/EvaluationDashboard';
import { searchCourses, getFilterFacets, getSystemHealth } from './services/api';
import { Compass, Sparkles, AlertCircle, BookOpen } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [query, setQuery] = useState('Node.js backend practical beginner');
  const [searchMode, setSearchMode] = useState('hybrid');
  const [filters, setFilters] = useState({
    difficulty: '',
    category: '',
    max_duration: null,
    min_duration: null,
    provider: '',
    free_only: false,
  });

  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchMeta, setSearchMeta] = useState(null);
  const [facets, setFacets] = useState(null);
  const [health, setHealth] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [error, setError] = useState(null);

  // Initial load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [facetsData, healthData] = await Promise.all([
        getFilterFacets(),
        getSystemHealth()
      ]);
      setFacets(facetsData);
      setHealth(healthData);
      // Run initial search
      executeSearch('Node.js backend practical beginner', 'hybrid', filters);
    } catch (e) {
      console.error('Initialization error:', e);
      // Fallback search attempt
      executeSearch('Node.js backend practical beginner', 'hybrid', filters);
    }
  };

  const executeSearch = async (searchQuery, mode = searchMode, currentFilters = filters) => {
    const q = searchQuery !== undefined ? searchQuery : query;
    if (!q.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const res = await searchCourses({
        query: q,
        mode: mode,
        difficulty: currentFilters.difficulty || null,
        category: currentFilters.category || null,
        max_duration: currentFilters.max_duration || null,
        min_duration: currentFilters.min_duration || null,
        provider: currentFilters.provider || null,
        free_only: currentFilters.free_only || false,
        top_k: 12
      });

      setCourses(res.results || []);
      setSearchMeta({
        cache_status: res.cache_status,
        execution_time_ms: res.execution_time_ms,
        total_results: res.total_results,
        extracted_filters: res.extracted_filters
      });
    } catch (err) {
      console.error(err);
      setError('Search request failed. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (customQuery) => {
    executeSearch(customQuery);
  };

  const handleModeChange = (newMode) => {
    setSearchMode(newMode);
    executeSearch(query, newMode, filters);
  };

  const handleResetFilters = () => {
    const cleared = {
      difficulty: '',
      category: '',
      max_duration: null,
      min_duration: null,
      provider: '',
      free_only: false,
    };
    setFilters(cleared);
    executeSearch(query, searchMode, cleared);
  };

  const handleFindSimilar = (course) => {
    setSelectedCourse(course);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Top Navbar */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* TAB 1: Search & Discovery */}
        {activeTab === 'search' && (
          <div className="space-y-8 animate-in fade-in">
            {/* Search Header Banner */}
            <div className="text-center max-w-3xl mx-auto space-y-3 pt-2 pb-4">
              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900">
                Intelligent Course Discovery
              </h1>
              <p className="text-sm sm:text-base text-slate-600">
                Discover courses by semantic intent, technology, and learning preference powered by{' '}
                <span className="text-blue-600 font-semibold">BM25 + pgvector Hybrid RRF</span> and{' '}
                <span className="text-amber-600 font-semibold">Redis In-Memory Caching</span>.
              </p>
            </div>

            {/* Natural-Language Search Bar */}
            <SearchBar
              query={query}
              setQuery={setQuery}
              searchMode={searchMode}
              setSearchMode={handleModeChange}
              onSearch={() => handleSearchSubmit()}
              loading={loading}
              searchMeta={searchMeta}
            />

            {/* Layout: Filters Sidebar + Results Grid */}
            <div className="flex flex-col lg:flex-row gap-8 items-start">
              {/* Filter Sidebar */}
              <FilterSidebar
                filters={filters}
                setFilters={setFilters}
                facets={facets}
                onApplyFilters={() => executeSearch()}
                onResetFilters={handleResetFilters}
              />

              {/* Course Cards Grid */}
              <div className="flex-1 w-full space-y-4">
                {/* Results count header */}
                <div className="flex items-center justify-between text-xs text-slate-500 px-1">
                  <span>
                    Showing <strong className="text-slate-800">{courses.length}</strong> ranked courses
                  </span>
                  {searchMeta && (
                    <span className="font-mono">
                      Retrieval time: <strong className="text-blue-600">{searchMeta.execution_time_ms} ms</strong>
                    </span>
                  )}
                </div>

                {error && (
                  <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 flex items-center space-x-3 text-sm">
                    <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-500" />
                    <span>{error}</span>
                  </div>
                )}

                {loading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {[1, 2, 3, 4].map((n) => (
                      <div key={n} className="glass-panel rounded-2xl p-5 h-64 animate-pulse space-y-4">
                        <div className="h-4 bg-slate-200 rounded w-1/3" />
                        <div className="h-6 bg-slate-200 rounded w-3/4" />
                        <div className="h-16 bg-slate-200 rounded" />
                        <div className="h-8 bg-slate-200 rounded w-1/2" />
                      </div>
                    ))}
                  </div>
                ) : courses.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {courses.map((course) => (
                      <CourseCard
                        key={course.id}
                        course={course}
                        onSelectCourse={setSelectedCourse}
                        onFindSimilar={handleFindSimilar}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="glass-panel rounded-3xl p-12 text-center space-y-3">
                    <Compass className="w-12 h-12 text-slate-400 mx-auto" />
                    <h3 className="text-base font-bold text-slate-800">No matching courses found</h3>
                    <p className="text-xs text-slate-500 max-w-md mx-auto">
                      Try adjusting your search terms or resetting the difficulty and duration filters.
                    </p>
                    <button
                      onClick={handleResetFilters}
                      className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all mt-2 shadow-sm"
                    >
                      Clear Filters
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Personalized Recommender */}
        {activeTab === 'recommend' && (
          <PersonalizationWizard
            onSelectCourse={setSelectedCourse}
            onFindSimilar={handleFindSimilar}
          />
        )}

        {/* TAB 3: IR Evaluation & Metrics */}
        {activeTab === 'benchmark' && (
          <EvaluationDashboard />
        )}
      </main>

      {/* Course Detail Modal */}
      {selectedCourse && (
        <CourseModal
          course={selectedCourse}
          onClose={() => setSelectedCourse(null)}
          onSelectCourse={setSelectedCourse}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-slate-200/80 bg-white/60 py-6 mt-12 text-xs text-slate-500 text-center">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-700">CourseFinder</span>
            <span>—</span>
            <span>Intelligent Semantic Retrieval & Recommendation Platform</span>
          </div>
          <div className="font-mono text-[11px] text-slate-500">
            BM25 Okapi • pgvector (HNSW) • Reciprocal Rank Fusion (k=60) • Redis Cache-Aside
          </div>
        </div>
      </footer>
    </div>
  );
}

