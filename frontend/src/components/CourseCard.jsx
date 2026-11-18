import React from 'react';
import { Star, Clock, Award, ExternalLink, Sparkles, BookOpen, Layers } from 'lucide-react';

export default function CourseCard({ course, onSelectCourse, onFindSimilar }) {
  const scorePercent = course.score != null ? Math.round(course.score * 100) : null;

  const getScoreColor = (pct) => {
    if (pct >= 90) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (pct >= 75) return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
    return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
  };

  const getDifficultyColor = (diff) => {
    switch (diff?.toLowerCase()) {
      case 'beginner': return 'text-emerald-300 bg-emerald-950/60 border-emerald-800';
      case 'intermediate': return 'text-blue-300 bg-blue-950/60 border-blue-800';
      case 'advanced': return 'text-purple-300 bg-purple-950/60 border-purple-800';
      default: return 'text-slate-300 bg-slate-800 border-slate-700';
    }
  };

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-5 flex flex-col justify-between transition-all group">
      <div>
        {/* Top Header: Category, Provider & Relevance Gauge */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="font-semibold text-slate-400">{course.provider}</span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">{course.category}</span>
          </div>

          {scorePercent != null && (
            <div className={`flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-mono font-bold border ${getScoreColor(scorePercent)}`}>
              <Sparkles className="w-3 h-3" />
              <span>{scorePercent}% Match</span>
            </div>
          )}
        </div>

        {/* Course Title */}
        <h3
          onClick={() => onSelectCourse(course)}
          className="text-base font-bold text-slate-100 group-hover:text-blue-400 cursor-pointer line-clamp-2 transition-colors mb-2"
        >
          {course.title}
        </h3>

        {/* Course Description */}
        <p className="text-xs text-slate-400 line-clamp-2 mb-4">
          {course.description}
        </p>

        {/* Matched Skills / Tags */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {course.skills?.slice(0, 4).map((skill, i) => {
            const isMatched = course.matched_skills?.some(ms => ms.toLowerCase() === skill.toLowerCase());
            return (
              <span
                key={i}
                className={`text-[11px] px-2 py-0.5 rounded-md font-medium ${
                  isMatched
                    ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                    : 'bg-slate-800 text-slate-400 border border-slate-700/50'
                }`}
              >
                {skill}
              </span>
            );
          })}
          {course.skills?.length > 4 && (
            <span className="text-[11px] px-1.5 py-0.5 text-slate-500">
              +{course.skills.length - 4} more
            </span>
          )}
        </div>
      </div>

      {/* Footer Info & Actions */}
      <div className="pt-3 border-t border-slate-800/80 flex flex-col gap-3">
        {/* Meta badges: Difficulty, Duration, Rating, Price */}
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-3">
            <span className={`px-2 py-0.5 rounded text-[11px] font-medium border ${getDifficultyColor(course.difficulty)}`}>
              {course.difficulty}
            </span>

            <span className="flex items-center space-x-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{course.duration_hours}h</span>
            </span>

            <span className="flex items-center space-x-1 text-amber-400 font-medium">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span>{course.rating}</span>
            </span>
          </div>

          <span className="font-semibold text-slate-200">
            {course.price === 0 ? (
              <span className="text-emerald-400 font-bold">Free</span>
            ) : (
              `$${course.price.toFixed(2)}`
            )}
          </span>
        </div>

        {/* Retrieval Sources provenance */}
        {course.retrieval_sources && course.retrieval_sources.length > 0 && (
          <div className="flex items-center space-x-1.5 text-[10px] text-slate-500 font-mono">
            <Layers className="w-3 h-3 text-slate-400" />
            <span>Retrieved via: {course.retrieval_sources.join(' + ')}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between gap-2 pt-1">
          <button
            onClick={() => onFindSimilar(course)}
            className="flex-1 text-xs font-semibold py-1.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-blue-300 border border-slate-700 transition-colors flex items-center justify-center space-x-1.5"
          >
            <Sparkles className="w-3 h-3 text-blue-400" />
            <span>Find Similar</span>
          </button>

          <a
            href={course.course_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 transition-colors"
            title="Open external course"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}

