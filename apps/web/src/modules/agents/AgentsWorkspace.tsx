"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  Swords, 
  ShieldAlert, 
  Sparkles, 
  Bot, 
  Play, 
  Copy, 
  Check, 
  RotateCcw, 
  Brain, 
  Scale, 
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  Zap
} from 'lucide-react';
import { 
  api, 
  DialecticalDebateResponse, 
  DebateTurn, 
  PreMortemFailureMode,
  CognitiveDriftReport
} from '@/services/api';

interface Persona {
  id: string;
  name: string;
  role: string;
  roleType: 'thesis' | 'antithesis' | 'pre_mortem' | 'synthesis';
  avatarColor: string;
  badgeColor: string;
  description: string;
}

const personas: Persona[] = [
  {
    id: 'proponent',
    name: 'Proponent Agent',
    role: 'Affirmative Thesis',
    roleType: 'thesis',
    avatarColor: 'bg-blue-500',
    badgeColor: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    description: 'Steel-mans the premise and highlights unfair scaling advantages.'
  },
  {
    id: 'adversary',
    name: "Devil's Advocate",
    role: 'Antithesis / Critique',
    roleType: 'antithesis',
    avatarColor: 'bg-rose-500',
    badgeColor: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
    description: 'Exposes hidden coordination taxes, fragility, and counter-examples.'
  },
  {
    id: 'pre_mortem',
    name: 'Failure Analyst',
    role: 'Pre-Mortem Failure Mode',
    roleType: 'pre_mortem',
    avatarColor: 'bg-amber-500',
    badgeColor: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    description: 'Answers: "If this completely crashes in 6 months, why did it fail?"'
  },
  {
    id: 'synthesizer',
    name: 'Dialectical Synthesizer',
    role: 'Higher-Order Resolution',
    roleType: 'synthesis',
    avatarColor: 'bg-emerald-500',
    badgeColor: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    description: 'Harmonizes tensions and constructs a hardened, balanced prompt.'
  }
];

const SUGGESTED_TOPICS = [
  "Decoupled Microservices vs Modular Monolith for early-stage AI architectures",
  "Autonomous Agent Swarms with direct write access vs Human-in-the-Loop gates",
  "Vector embeddings vs Knowledge Graphs for persistent cognitive memory",
  "Direct LLM prompting vs Middleware Cognitive Operating Layer"
];

export default function AgentsWorkspace() {
  const [topic, setTopic] = useState(SUGGESTED_TOPICS[0]);
  const [strategy, setStrategy] = useState("dialectical_debate");
  const [isDebating, setIsDebating] = useState(false);
  const [debateResult, setDebateResult] = useState<DialecticalDebateResponse | null>(null);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [driftReport, setDriftReport] = useState<CognitiveDriftReport | null>(null);
  const [activeTab, setActiveTab] = useState<'arena' | 'drift'>('arena');

  // Load initial evolution & drift analysis
  useEffect(() => {
    const controller = new AbortController();
    const fetchDrift = async () => {
      const data = await api.getEvolutionDriftAnalysis(controller.signal);
      if (data) setDriftReport(data);
    };
    fetchDrift();
    return () => controller.abort();
  }, []);

  const handleRunDebate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!topic.trim()) return;

    setIsDebating(true);
    try {
      const result = await api.runDialecticalDebate(topic.trim(), strategy, "deep");
      if (result) {
        setDebateResult(result);
      }
    } catch (err) {
      console.error("Dialectical debate failed:", err);
    } finally {
      setIsDebating(false);
    }
  };

  const copyPrompt = () => {
    if (!debateResult?.battle_tested_prompt) return;
    navigator.clipboard.writeText(debateResult.battle_tested_prompt);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 text-slate-800 dark:text-slate-200">
      {/* Workspace Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200/60 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Swords className="w-5 h-5 text-primary" />
            <h2 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-400">
              Dialectical Co-Reasoning Arena
            </h2>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Adversarial multi-agent stress-testing: Thesis, Antithesis, Pre-Mortem failure analysis, and Synthesis.
          </p>
        </div>

        {/* View Switcher: Arena vs Drift Prevention */}
        <div className="flex items-center p-1 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/5 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('arena')}
            className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
              activeTab === 'arena'
                ? 'bg-white dark:bg-slate-900 text-primary shadow-sm font-bold'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            Debate Arena
          </button>
          <button
            onClick={() => setActiveTab('drift')}
            className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'drift'
                ? 'bg-white dark:bg-slate-900 text-primary shadow-sm font-bold'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            <TrendingUp size={13} />
            <span>Drift Prevention</span>
          </button>
        </div>
      </div>

      {activeTab === 'arena' ? (
        <>
          {/* Topic Input Bar & Strategy Selector */}
          <div className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
            <form onSubmit={handleRunDebate} className="space-y-3">
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Enter a concept, prompt, or architectural hypothesis to stress-test..."
                  className="flex-1 px-4 py-2.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl text-xs sm:text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary/40 font-medium"
                />

                <select
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value)}
                  className="px-3 py-2.5 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 focus:outline-none cursor-pointer"
                >
                  <option value="dialectical_debate">⚔️ Dialectical Debate (Thesis vs Antithesis)</option>
                  <option value="adversarial_reasoning">🛡️ Adversarial Stress Test (Pre-Mortem Focus)</option>
                  <option value="consensus_building">🤝 Consensus Building (Cooperative)</option>
                </select>

                <button
                  type="submit"
                  disabled={isDebating}
                  className="flex items-center justify-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-xl text-xs font-bold shadow-md disabled:opacity-50 transition-all cursor-pointer flex-shrink-0"
                >
                  <Sparkles size={14} className={isDebating ? "animate-spin" : ""} />
                  <span>{isDebating ? "Agents Debating..." : "Start Co-Reasoning"}</span>
                </button>
              </div>

              {/* Suggestion Chips */}
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-[11px] font-bold text-slate-400 mr-1">Suggestions:</span>
                {SUGGESTED_TOPICS.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setTopic(item)}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 transition-colors cursor-pointer"
                  >
                    {item.split(" vs ")[0]}...
                  </button>
                ))}
              </div>
            </form>
          </div>

          {/* Socratic Personas Roster */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {personas.map((persona) => {
              const isActive = isDebating || !!debateResult;
              return (
                <div
                  key={persona.id}
                  className="bg-white/70 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-4 shadow-sm space-y-2 relative overflow-hidden"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className={`w-7 h-7 rounded-lg ${persona.avatarColor} text-white flex items-center justify-center font-bold text-xs shadow-sm`}>
                        <Bot size={15} />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100">{persona.name}</h4>
                        <span className={`inline-block text-[9px] font-semibold px-2 py-0.5 rounded-full border ${persona.badgeColor}`}>
                          {persona.role}
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-snug">
                    {persona.description}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Debate Rounds Transcript */}
          {debateResult ? (
            <div className="space-y-6">
              <div className="bg-white/95 dark:bg-slate-950/70 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-md p-6 space-y-6">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
                  <div className="flex items-center gap-2">
                    <Scale className="w-5 h-5 text-primary" />
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-200">
                      Multi-Agent Deliberation Transcript
                    </h3>
                  </div>
                  <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                    Rigor Score: {(debateResult.cognitive_rigor_score * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="space-y-4">
                  {debateResult.debate_rounds.map((round, idx) => {
                    const isThesis = round.role === 'thesis';
                    const isAntithesis = round.role === 'antithesis';
                    const isPreMortem = round.role === 'pre_mortem';
                    const isSynthesis = round.role === 'synthesis';

                    const borderClass = isThesis 
                      ? 'border-blue-500/30 bg-blue-500/[0.02]' 
                      : isAntithesis 
                      ? 'border-rose-500/30 bg-rose-500/[0.02]' 
                      : isPreMortem 
                      ? 'border-amber-500/30 bg-amber-500/[0.02]' 
                      : 'border-emerald-500/30 bg-emerald-500/[0.02]';

                    const speakerColor = isThesis 
                      ? 'text-blue-500' 
                      : isAntithesis 
                      ? 'text-rose-500' 
                      : isPreMortem 
                      ? 'text-amber-500' 
                      : 'text-emerald-500';

                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`p-4 rounded-xl border ${borderClass} space-y-2`}
                      >
                        <div className="flex items-center justify-between">
                          <span className={`text-xs font-bold uppercase tracking-wider ${speakerColor}`}>
                            {round.speaker} ({round.role.toUpperCase()})
                          </span>
                          <span className="text-[10px] font-mono text-slate-400">
                            Confidence: {(round.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-relaxed font-medium">
                          {round.argument}
                        </p>
                        {round.key_assumptions.length > 0 && (
                          <div className="pt-1 flex flex-wrap items-center gap-1.5 text-[10px]">
                            <span className="font-semibold text-slate-400">Challenged Assumptions:</span>
                            {round.key_assumptions.map((assump, aIdx) => (
                              <span key={aIdx} className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300">
                                {assump}
                              </span>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Pre-Mortem Failure Modes Table */}
              {debateResult.pre_mortem_failure_modes.length > 0 && (
                <div className="bg-white/95 dark:bg-slate-950/70 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-6 shadow-md space-y-4">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-200">
                      Pre-Mortem Failure Modes & Mitigations
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {debateResult.pre_mortem_failure_modes.map((fm, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-amber-500">Failure Vector #{idx + 1}</span>
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-600 dark:text-amber-400 font-bold uppercase">
                            {fm.probability} Risk
                          </span>
                        </div>
                        <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-snug">
                          {fm.failure_scenario}
                        </p>
                        <div className="pt-1 text-[11px] text-slate-500 dark:text-slate-400">
                          <span className="font-bold text-slate-600 dark:text-slate-300">Mitigation: </span>
                          {fm.mitigation_strategy}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Battle-Tested Prompt Output */}
              <div className="bg-slate-900 border border-white/10 rounded-2xl p-6 shadow-2xl space-y-4 text-white">
                <div className="flex items-center justify-between border-b border-white/10 pb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-emerald-400" />
                    <div>
                      <h4 className="text-sm font-bold">Synthesized Dialectical LLM Prompt</h4>
                      <p className="text-[11px] text-slate-400">Hardened against confirmation bias and edge-case failure modes.</p>
                    </div>
                  </div>
                  <button
                    onClick={copyPrompt}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-primary text-white text-xs font-semibold hover:bg-primary/90 transition-all cursor-pointer"
                  >
                    {copiedPrompt ? <Check size={14} /> : <Copy size={14} />}
                    <span>{copiedPrompt ? "Copied!" : "Copy Hardened Prompt"}</span>
                  </button>
                </div>

                <div className="bg-slate-950/80 rounded-xl p-4 font-mono text-xs text-emerald-400 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto border border-white/5">
                  {debateResult.battle_tested_prompt}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 dark:bg-slate-900/10 border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-12 text-center space-y-2">
              <Scale className="w-8 h-8 text-slate-400 mx-auto animate-pulse" />
              <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">
                Awaiting Co-Reasoning Topic
              </p>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Select or type a premise above and click "Start Co-Reasoning" to launch multi-agent Socratic deliberation.
              </p>
            </div>
          )}
        </>
      ) : (
        /* Cognitive Drift Prevention Tab */
        <div className="space-y-6">
          <div className="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md border border-slate-200/80 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-slate-800 dark:text-slate-100">
                  Longitudinal Cognitive Drift & Evolution
                </h3>
                <p className="text-xs text-slate-400">
                  Monitors prompt entropy, detects schema stagnation, and suggests higher-order thinking leaps.
                </p>
              </div>
              {driftReport && (
                <span className="text-xs font-mono px-3 py-1 bg-primary/10 text-primary rounded-full font-bold">
                  {driftReport.total_interactions_analyzed} Interactions Analyzed
                </span>
              )}
            </div>

            {driftReport ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200/60 dark:border-slate-800 space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Semantic Drift Rate</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-extrabold text-slate-800 dark:text-white">
                      {(driftReport.semantic_drift_score * 100).toFixed(0)}%
                    </span>
                    <span className="text-xs font-semibold text-emerald-500">Stable</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Low drift indicates consistent cognitive discipline and domain grounding.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200/60 dark:border-slate-800 space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Stagnation Risk</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-extrabold capitalize text-slate-800 dark:text-white">
                      {driftReport.stagnation_risk}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Calculated from vocabulary variation and inquiry depth across sessions.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200/60 dark:border-slate-800 space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Next Cognitive Frontier</span>
                  <p className="text-xs font-bold text-primary pt-1">
                    {driftReport.next_cognitive_frontier}
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-400">
                Loading cognitive drift telemetry...
              </div>
            )}

            {driftReport && (
              <div className="space-y-3 pt-4 border-t border-slate-100 dark:border-slate-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Evolutionary Recommendations for Mental Growth:
                </h4>
                <div className="space-y-2">
                  {driftReport.evolutionary_recommendations.map((rec, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-950/40 rounded-xl border border-slate-200/60 dark:border-slate-800 text-xs">
                      <Lightbulb size={16} className="text-amber-500 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-700 dark:text-slate-300 font-medium">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
