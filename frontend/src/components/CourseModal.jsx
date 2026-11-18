import React, { useEffect, useState } from 'react';
import { X, Star, Clock, Award, ExternalLink, Sparkles, BookOpen, Layers, CheckCircle2 } from 'lucide-react';
import { getSimilarCourses } from '../services/api';

export default function CourseModal({ course, onClose, onSelectCourse }) {
  const [similarCourses, setSimilarCourses] = useState([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);

  useEffect(() => {
    if (course) {
      loadSimilar(course.id);
    }
  }, [course]);

  const loadSimilar = async (id) => {
    try {
      setLoadingSimilar(true);
      const res = await getSimilarCourses(id, { top_k: 4 });
      setSimilarCourses(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSimilar(false);
    }
  };

  if (!course) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-3xl shadow-2xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto space-y-6">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header Metadata */}
        <div>
          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 mb-2">
            <span className="font-semibold text-blue-400">{course.provider}</span>
            <span>•</span>
            <span>{course.category}</span>
            <span>•</span>
            <span className="font-mono text-slate-500">ID: {course.id}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white leading-snug">
            {course.title}
          </h2>
        </div>

        {/* Stat Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-[11px] text-slate-400 block mb-1">Difficulty</span>
            <span className="text-sm font-semibold text-white">{course.difficulty}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-[11px] text-slate-400 block mb-1">Duration</span>
            <span className="text-sm font-semibold text-white">{course.duration_hours} Hours</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-[11px] text-slate-400 block mb-1">Rating</span>
            <div className="flex items-center space-x-1 text-amber-400">
              <Star className="w-4 h-4 fill-amber-400" />
              <span className="text-sm font-semibold text-white">{course.rating} / 5.0</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <span className="text-[11px] text-slate-400 block mb-1">Tuition</span>
            <span className="text-sm font-semibold text-emerald-400">
              {course.price === 0 ? 'Free' : `$${course.price.toFixed(2)}`}
            </span>
          </div>
        </div>

        {/* Overview Description */}
        <div className="space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Course Overview
          </h4>
          <p className="text-sm text-slate-300 leading-relaxed">
            {course.description}
          </p>
        </div>

        {/* Skills Covered */}
        <div className="space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Technologies & Skills Taught
          </h4>
          <div className="flex flex-wrap gap-2">
            {course.skills?.map((s, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-blue-500/10 text-blue-300 border border-blue-500/20"
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* External Link */}
        <div className="pt-2">
          <a
            href={course.course_url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/30 transition-all"
          >
            <span>Visit Official Course Page</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>

        {/* Similar Courses Subsection (pgvector semantic similarity) */}
        <div className="pt-4 border-t border-slate-800 space-y-3">
          <div className="flex items-center space-x-2 text-sm font-bold text-slate-200">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span>Similar Courses (Dense Vector Nearest Neighbors)</span>
          </div>

          {loadingSimilar ? (
            <div className="text-xs text-slate-400 animate-pulse">Calculating vector cosine similarity...</div>
          ) : similarCourses.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {similarCourses.map((sim) => (
                <div
                  key={sim.id}
                  onClick={() => onSelectCourse(sim)}
                  className="p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-blue-500/40 cursor-pointer transition-all space-y-1.5"
                >
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{sim.provider}</span>
                    <span className="text-emerald-400 font-mono font-bold">
                      {Math.round(sim.score * 100)}% Match
                    </span>
                  </div>
                  <h5 className="text-xs font-bold text-slate-200 line-clamp-1">{sim.title}</h5>
                  <div className="flex items-center space-x-2 text-[10px] text-slate-400">
                    <span>{sim.difficulty}</span>
                    <span>•</span>
                    <span>{sim.duration_hours}h</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-slate-500">No similar courses found.</div>
          )}
        </div>
      </div>
    </div>
  );
}
