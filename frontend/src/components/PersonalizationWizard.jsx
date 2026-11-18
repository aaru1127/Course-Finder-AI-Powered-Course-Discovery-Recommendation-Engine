import React, { useState } from 'react';
import { Sparkles, Award, Cpu, Clock, Target, CheckCircle2, ArrowRight } from 'lucide-react';
import { getPersonalizedRecommendations } from '../services/api';
import CourseCard from './CourseCard';

const POPULAR_TECH = [
  'Node.js', 'React', 'Python', 'FastAPI', 'Docker', 'Kubernetes',
  'AWS', 'PostgreSQL', 'PyTorch', 'LangChain', 'TypeScript', 'Go',
  'Apache Spark', 'Redis', 'Microservices', 'System Design'
];

export default function PersonalizationWizard({ onSelectCourse, onFindSimilar }) {
  const [skillLevel, setSkillLevel] = useState('Beginner');
  const [selectedTech, setSelectedTech] = useState(['Node.js', 'FastAPI']);
  const [goal, setGoal] = useState('Transition into backend engineering and build scalable REST APIs');
  const [weeklyHours, setWeeklyHours] = useState(10);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const toggleTech = (tech) => {
    setSelectedTech(prev =>
      prev.includes(tech) ? prev.filter(t => t !== tech) : [...prev, tech]
    );
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const res = await getPersonalizedRecommendations({
        skill_level: skillLevel,
        target_technologies: selectedTech,
        learning_goal: goal,
        available_weekly_hours: weeklyHours,
        top_k: 6
      });
      setRecommendations(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in">
      {/* Wizard Header */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/20">
            <Sparkles className="w-6 h-6 text-amber-300" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white">Personalized Learning Roadmap</h2>
            <p className="text-sm text-slate-400">
              Tell us your current background, target technologies, and available study hours.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
          {/* Skill Level */}
          <div className="space-y-2">
            <label className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
              <Award className="w-4 h-4 text-blue-400" />
              <span>Current Experience Level</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['Beginner', 'Intermediate', 'Advanced'].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setSkillLevel(lvl)}
                  className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                    skillLevel === lvl
                      ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-600/30'
                      : 'bg-slate-800/80 text-slate-400 border-slate-700 hover:bg-slate-800'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* Weekly Available Study Hours */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-300">
              <span className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-amber-400" />
                <span>Weekly Available Time</span>
              </span>
              <span className="font-mono text-blue-400 font-bold">{weeklyHours} Hours / Week</span>
            </div>
            <input
              type="range"
              min="3"
              max="30"
              step="1"
              value={weeklyHours}
              onChange={(e) => setWeeklyHours(Number(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500 mt-2"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>3h (Casual)</span>
              <span>10h (Balanced)</span>
              <span>20h+ (Bootcamp)</span>
            </div>
          </div>

          {/* Target Technologies */}
          <div className="space-y-2 md:col-span-2">
            <label className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span>Target Technologies & Topics</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {POPULAR_TECH.map((tech) => {
                const isSelected = selectedTech.includes(tech);
                return (
                  <button
                    key={tech}
                    onClick={() => toggleTech(tech)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all border ${
                      isSelected
                        ? 'bg-blue-600/30 text-blue-300 border-blue-500 shadow-sm'
                        : 'bg-slate-800/80 text-slate-400 border-slate-700 hover:bg-slate-800'
                    }`}
                  >
                    {tech}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Goal Statement */}
          <div className="space-y-2 md:col-span-2">
            <label className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
              <Target className="w-4 h-4 text-emerald-400" />
              <span>Learning Objective / Career Target</span>
            </label>
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g. Master backend engineering and build scalable production APIs"
              className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Generate Button */}
        <div className="pt-2">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-sm flex items-center justify-center space-x-2 shadow-xl shadow-blue-600/30 disabled:opacity-50 transition-all"
          >
            {loading ? (
              <span>Generating Targeted Roadmap...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-amber-300" />
                <span>Generate Personalized Recommendations</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Recommendations Results */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span>Recommended Courses For Your Profile</span>
            </h3>
            <span className="text-xs font-mono text-slate-400">
              {recommendations.length} Aligned Courses
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {recommendations.map((course) => (
              <div key={course.id} className="flex flex-col">
                {course.recommendation_reason && (
                  <div className="mb-2 px-3 py-1.5 rounded-lg bg-blue-900/30 border border-blue-800 text-blue-300 text-xs flex items-center space-x-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                    <span className="line-clamp-1">{course.recommendation_reason}</span>
                  </div>
                )}
                <CourseCard
                  course={course}
                  onSelectCourse={onSelectCourse}
                  onFindSimilar={onFindSimilar}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

