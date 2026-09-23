"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lightbulb, 
  TrendingUp, 
  Brain, 
  CheckCircle, 
  BarChart, 
  HelpCircle, 
  Activity, 
  UserCheck,
  Compass,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { api } from '@/services/api';

interface CognitiveMetric {
  name: string;
  score: number;
  description: string;
  change: string;
  trend: 'up' | 'down' | 'stable';
}

interface CognitiveInsight {
  id: string;
  title: string;
  category: 'efficiency' | 'clarity' | 'scope';
  text: string;
  impact: 'high' | 'medium' | 'low';
  resolved: boolean;
}

const mockMetrics: CognitiveMetric[] = [
  {
    name: 'Clarity Rating',
    score: 84,
    description: 'Measures how clear and precise your prompt inputs are.',
    change: '+12%',
    trend: 'up'
  },
  {
    name: 'Vocabulary Growth',
    score: 71,
    description: 'Tracks the variety of new and helpful terms you adopt in your prompts.',
    change: '+5%',
    trend: 'up'
  },
  {
    name: 'Prompt Focus',
    score: 92,
    description: 'Ensures the system stays focused on your main topic without drifting.',
    change: 'Stable',
    trend: 'stable'
  }
];

const mockInsights: CognitiveInsight[] = [
  {
    id: 'ins-1',
    title: 'Unclear Prompts when Mixing Topics',
    category: 'clarity',
    text: 'Your prompts containing code development and philosophy simultaneously have low clarity ratings. Recommend trying the Critic Agent first to help refine.',
    impact: 'high',
    resolved: false
  },
  {
    id: 'ins-2',
    title: 'Memory Word Matches',
    category: 'efficiency',
    text: 'Prompts containing Rust macros saw a 30% increase in code accuracy when recommended terms (like "procedural token stream") were injected.',
    impact: 'medium',
    resolved: true
  },
  {
    id: 'ins-3',
    title: 'Highly Exploratory Style',
    category: 'scope',
    text: 'Most of your prompts use an Exploratory style. This is great for brainstorming, but switching to Technical style sooner can help get faster results.',
    impact: 'low',
    resolved: false
  }
];

export default function ReflectionWorkspace() {
  const [metrics, setMetrics] = useState<CognitiveMetric[]>(mockMetrics);
  const [insights, setInsights] = useState<CognitiveInsight[]>(mockInsights);
  const [dominantModes, setDominantModes] = useState<{name: string, score: number}[]>([]);
  const [promptEvolution, setPromptEvolution] = useState<{before: string, after: string} | null>(null);
  const [activeCategory, setActiveCategory] = useState<'all' | 'clarity' | 'efficiency' | 'scope'>('all');

  const [calibrating, setCalibrating] = useState<string | null>(null);
  const [calibrationMessage, setCalibrationMessage] = useState<string | null>(null);

  const handleCalibrate = async (type: string) => {
    setCalibrating(type);
    
    let updatedStyle = {};
    let message = "";
    if (type === 'ambiguity') {
      updatedStyle = { reasoning_preference: 'first-principles', verbosity: 'detailed' };
      message = "Clarity calibrated: Set style to step-by-step logic and enabled precise filtering.";
    } else if (type === 'synergy') {
      updatedStyle = { reasoning_preference: 'analogy-driven', verbosity: 'balanced' };
      message = "Synapses optimized: Prompt helper will bridge your topics using clear analogies.";
    } else if (type === 'dexterity') {
      updatedStyle = { reasoning_preference: 'balanced', verbosity: 'balanced' };
      message = "Dexterity tuned: System will now adjust styles automatically for complex tasks.";
    } else if (type === 'vocab') {
      updatedStyle = { reasoning_preference: 'first-principles', verbosity: 'detailed' };
      message = "Vocabulary yield updated: Increased the importance of your saved terms.";
    }

    try {
      const res = await fetch(`${api.baseUrl}/user/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profession: "Software Engineer",
          intellectual_level: "expert",
          cognitive_style: updatedStyle,
          domain_expertise: [
            { domain: "Software Architecture", level: "expert" },
            { domain: "Cosmology", level: "novice" }
          ]
        })
      });
      if (res.ok) {
        setCalibrationMessage(message);
        setTimeout(() => setCalibrationMessage(null), 6000);
      }
    } catch (err) {
      console.error("Failed to update user profile calibration:", err);
    } finally {
      setCalibrating(null);
    }
  };

  React.useEffect(() => {
    const controller = new AbortController();
    const fetchLatest = async () => {
      try {
        const res = await fetch(`${api.baseUrl}/reflection/analytics`, { signal: controller.signal });
        if (res.ok) {
          const data = await res.json();
          if (data) {
            if (data.metrics) setMetrics(data.metrics);
            if (data.insights) setInsights(data.insights);
            if (data.dominant_modes) setDominantModes(data.dominant_modes);
            if (data.prompt_evolution) setPromptEvolution(data.prompt_evolution);
          }
        }
      } catch (err) {
        // Fall back to default mock reflection metrics
      }
    };
    fetchLatest();
    return () => controller.abort();
  }, []);

  const toggleResolve = (id: string) => {
    setInsights(insights.map(ins => {
      if (ins.id === id) {
        return { ...ins, resolved: !ins.resolved };
      }
      return ins;
    }));
  };

  const filteredInsights = insights.filter(ins => {
    if (activeCategory === 'all') return true;
    return ins.category === activeCategory;
  });

  const getImpactColor = (impact: CognitiveInsight['impact']) => {
    switch (impact) {
      case 'high': return 'text-rose-500 bg-rose-500/10 border-rose-500/20';
      case 'medium': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'low': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 text-slate-800 dark:text-slate-200 font-sans">
      
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200/60 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Lightbulb className="w-5 h-5 text-amber-500" />
            <h2 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-400">
              Cognitive Reflections
            </h2>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Insights on cognitive patterns, concept growth analytics, and feedback loops.
          </p>
        </div>
      </div>

      {/* Metrics Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {metrics.map((metric) => (
          <div 
            key={metric.name}
            className="relative overflow-hidden bg-white/70 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300 group"
          >
            <div className="flex items-center justify-between gap-2 mb-3">
              <div className="flex items-center gap-2 text-slate-400">
                <Brain className="w-4 h-4 text-primary" />
                <p className="text-xs font-bold uppercase tracking-wider">{metric.name}</p>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                metric.trend === 'up' ? 'text-emerald-500 bg-emerald-500/10' : 'text-slate-500 bg-slate-100 dark:bg-white/5'
              }`}>
                {metric.change}
              </span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">{metric.score}</span>
              <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">/ 100</span>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-3 leading-relaxed">
              {metric.description}
            </p>
          </div>
        ))}
      </div>

      {/* Main Analysis Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Insight List */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200/60 dark:border-slate-800/80 pb-3">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500">Cognitive Insights</h3>
            
            {/* Filter buttons */}
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-white/5 p-1 rounded-lg">
              {(['all', 'clarity', 'efficiency', 'scope'] as const).map(cat => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider transition-colors ${
                    activeCategory === cat 
                      ? 'bg-white dark:bg-slate-800 text-primary shadow-sm' 
                      : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {filteredInsights.map((ins) => (
                <motion.div
                  key={ins.id}
                  layout
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className={`p-5 rounded-2xl border bg-white dark:bg-[#0a0c10] transition-all duration-300 flex items-start gap-4 ${
                    ins.resolved 
                      ? 'border-slate-200 dark:border-white/5 opacity-60' 
                      : 'border-slate-200 dark:border-white/5 hover:border-slate-300 dark:hover:border-white/10 hover:shadow-sm'
                  }`}
                >
                  <button 
                    onClick={() => toggleResolve(ins.id)}
                    className={`mt-1 rounded-full p-0.5 border transition-all ${
                      ins.resolved 
                        ? 'border-emerald-500 bg-emerald-500 text-white' 
                        : 'border-slate-300 dark:border-slate-700 hover:border-emerald-500 text-transparent'
                    }`}
                  >
                    <CheckCircle size={14} className="stroke-[3px]" />
                  </button>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{ins.category}</span>
                      <span className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${getImpactColor(ins.impact)}`}>
                        {ins.impact} impact
                      </span>
                    </div>

                    <h4 className={`text-sm font-bold text-slate-800 dark:text-slate-200 mt-2 ${ins.resolved ? 'line-through' : ''}`}>
                      {ins.title}
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                      {ins.text}
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Thinking Evolution & Calibration Panel */}
          <div className="bg-white/70 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-6 mt-8">
            <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-indigo-500" />
                <h3 className="text-sm font-bold uppercase tracking-wider">Thinking Style Settings</h3>
              </div>
              <span className="text-[10px] bg-indigo-500/10 text-indigo-500 px-2 py-0.5 rounded-full font-bold">
                Calibrate
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Parameter 1: Ambiguity Evaporation */}
              <div className="p-4 bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 rounded-2xl space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start">
                    <h4 className="text-xs font-bold text-slate-700 dark:text-white uppercase">Clarity Improvement Rate</h4>
                    <span className="text-xs font-mono font-bold text-indigo-505 dark:text-indigo-400">74%</span>
                  </div>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 leading-relaxed mt-1">
                    Tracks how quickly your prompts go from broad brainstorming to clear, precise instructions.
                  </p>
                </div>
                <div className="space-y-3 pt-2">
                  <div className="w-full bg-slate-200 dark:bg-white/5 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-gradient-to-r from-indigo-500 to-violet-500 h-1.5 rounded-full" style={{ width: '74%' }} />
                  </div>
                  <button
                    type="button"
                    onClick={() => handleCalibrate('ambiguity')}
                    disabled={calibrating === 'ambiguity'}
                    className="w-full py-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-650 dark:text-indigo-300 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1 border border-indigo-500/20"
                  >
                    {calibrating === 'ambiguity' ? 'Optimizing Clarity...' : 'Optimize Clarity'}
                  </button>
                </div>
              </div>

              {/* Parameter 2: Cross-Domain Synergy */}
              <div className="p-4 bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 rounded-2xl space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start">
                    <h4 className="text-xs font-bold text-slate-700 dark:text-white uppercase">Topic Connecting Strength</h4>
                    <span className="text-xs font-mono font-bold text-emerald-500">88%</span>
                  </div>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 leading-relaxed mt-1">
                    Measures how well you connect different subjects (e.g. biology and software). Higher scores mean better analogies.
                  </p>
                </div>
                <div className="space-y-3 pt-2">
                  <div className="w-full bg-slate-200 dark:bg-white/5 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-gradient-to-r from-emerald-500 to-teal-500 h-1.5 rounded-full" style={{ width: '88%' }} />
                  </div>
                  <button
                    type="button"
                    onClick={() => handleCalibrate('synergy')}
                    disabled={calibrating === 'synergy'}
                    className="w-full py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1 border border-emerald-500/20"
                  >
                    {calibrating === 'synergy' ? 'Optimizing Synapses...' : 'Balance Analogies'}
                  </button>
                </div>
              </div>

              {/* Parameter 3: Cognitive Dexterity */}
              <div className="p-4 bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 rounded-2xl space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start">
                    <h4 className="text-xs font-bold text-slate-700 dark:text-white uppercase">Thinking Style Flexibility</h4>
                    <span className="text-xs font-mono font-bold text-amber-500">62%</span>
                  </div>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 leading-relaxed mt-1">
                    Measures how easily you switch between different thinking styles (brainstorming, planning, coding) depending on the task.
                  </p>
                </div>
                <div className="space-y-3 pt-2">
                  <div className="w-full bg-slate-200 dark:bg-white/5 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-gradient-to-r from-amber-500 to-orange-500 h-1.5 rounded-full" style={{ width: '62%' }} />
                  </div>
                  <button
                    type="button"
                    onClick={() => handleCalibrate('dexterity')}
                    disabled={calibrating === 'dexterity'}
                    className="w-full py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-600 dark:text-amber-300 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1 border border-amber-500/20"
                  >
                    {calibrating === 'dexterity' ? 'Calibrating...' : 'Tune Automatic Switching'}
                  </button>
                </div>
              </div>

              {/* Parameter 4: Vocab Expansion Yield */}
              <div className="p-4 bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 rounded-2xl space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start">
                    <h4 className="text-xs font-bold text-slate-700 dark:text-white uppercase">New Words Adoption</h4>
                    <span className="text-xs font-mono font-bold text-rose-500">81%</span>
                  </div>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 leading-relaxed mt-1">
                    How often you reuse the helpful terms recommended by the system in your next prompts.
                  </p>
                </div>
                <div className="space-y-3 pt-2">
                  <div className="w-full bg-slate-200 dark:bg-white/5 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-gradient-to-r from-rose-500 to-pink-500 h-1.5 rounded-full" style={{ width: '81%' }} />
                  </div>
                  <button
                    type="button"
                    onClick={() => handleCalibrate('vocab')}
                    disabled={calibrating === 'vocab'}
                    className="w-full py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 dark:text-rose-300 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1 border border-rose-500/20"
                  >
                    {calibrating === 'vocab' ? 'Updating Profiles...' : 'Optimize Word Recommendations'}
                  </button>
                </div>
              </div>
            </div>

            {/* Calibration Success Toast Banner */}
            {calibrationMessage && (
              <motion.div
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl flex items-center gap-3 text-indigo-650 dark:text-indigo-350 text-xs font-semibold"
              >
                <Sparkles size={16} className="text-indigo-500 animate-pulse flex-shrink-0" />
                <p>{calibrationMessage}</p>
              </motion.div>
            )}
          </div>

        </div>

        {/* Right Side: Growth & Advisor Panel */}
        <div className="space-y-6">
          <div className="border-b border-slate-200/60 dark:border-slate-800/80 pb-3">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500">AI Advisor</h3>
          </div>

          <div className="bg-slate-900 border border-white/5 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
            
            <div className="flex items-center gap-2 text-slate-300 mb-4 border-b border-white/5 pb-3">
              <Compass className="w-4 h-4 text-amber-500 animate-spin" />
              <p className="text-xs font-bold uppercase tracking-widest">Active Action Plan</p>
            </div>

            <div className="space-y-4">
              <div className="flex gap-3">
                <span className="text-xs font-mono font-bold text-slate-500 mt-0.5">01</span>
                <div>
                  <h4 className="text-xs font-bold text-white uppercase">Decouple Code & Theory</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    Write separate prompt thoughts for Rust build configuration and biology frameworks.
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3">
                <span className="text-xs font-mono font-bold text-slate-500 mt-0.5">02</span>
                <div>
                  <h4 className="text-xs font-bold text-white uppercase">Calibrate Mode Shifts</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    Set default prompt environment to "Technical" mode when testing API connections.
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <span className="text-xs font-mono font-bold text-slate-500 mt-0.5">03</span>
                <div>
                  <h4 className="text-xs font-bold text-white uppercase">Verify Persistence Loop</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    Submit prompts to the ChatGPT overlay to ensure postgres pgvector indexing remains live.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Dominant Cognitive Styles */}
          {dominantModes.length > 0 && (
            <div className="bg-white/70 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400 mb-4 border-b border-slate-200/60 dark:border-slate-800/80 pb-3">
                <Brain className="w-4 h-4 text-primary" />
                <p className="text-xs font-bold uppercase tracking-widest">Cognitive Styles</p>
              </div>
              <div className="space-y-4">
                {dominantModes.map(mode => (
                  <div key={mode.name} className="space-y-1">
                    <div className="flex justify-between text-xs font-bold">
                      <span className="text-slate-600 dark:text-slate-300">{mode.name}</span>
                      <span className="text-slate-500">{mode.score}%</span>
                    </div>
                    <div className="w-full bg-slate-100 dark:bg-white/5 rounded-full h-1.5 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-violet-500 to-indigo-500 h-1.5 rounded-full" 
                        style={{ width: `${mode.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prompt Evolution */}
          {promptEvolution && (
            <div className="bg-white/70 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm space-y-4">
              <div className="flex items-center gap-2 text-slate-400 border-b border-slate-200/60 dark:border-slate-800/80 pb-3">
                <TrendingUp className="w-4 h-4 text-emerald-500" />
                <p className="text-xs font-bold uppercase tracking-widest">Thinking Evolution</p>
              </div>
              <div className="space-y-3">
                <div className="p-3 bg-rose-500/5 dark:bg-rose-500/10 border border-rose-500/10 rounded-xl space-y-1">
                  <span className="text-[9px] font-bold text-rose-500 uppercase tracking-widest">Earliest Prompt (Vague)</span>
                  <p className="text-xs italic text-slate-500 dark:text-slate-400 leading-relaxed font-mono">
                    "{promptEvolution.before}"
                  </p>
                </div>
                <div className="flex justify-center text-slate-400">
                  <ArrowRight className="w-4 h-4 rotate-90" />
                </div>
                <div className="p-3 bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/10 rounded-xl space-y-1">
                  <span className="text-[9px] font-bold text-emerald-500 uppercase tracking-widest">Latest Prompt (Refined)</span>
                  <p className="text-xs italic text-slate-700 dark:text-slate-300 leading-relaxed font-mono font-bold">
                    "{promptEvolution.after}"
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
