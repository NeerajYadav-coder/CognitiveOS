"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  GraduationCap, 
  Sliders, 
  Sparkles, 
  Plus, 
  Trash, 
  Save, 
  BrainCircuit, 
  Check, 
  Layers, 
  HelpCircle,
  AlertCircle
} from 'lucide-react';
import { api } from '@/services/api';

interface DomainExpertise {
  domain: string;
  level: string;
}

export default function SettingsWorkspace() {
  const [profession, setProfession] = useState("Software Engineer");
  const [level, setLevel] = useState("intermediate");
  const [verbosity, setVerbosity] = useState("balanced");
  const [reasoning, setReasoning] = useState("balanced");
  const [domainExpertise, setDomainExpertise] = useState<DomainExpertise[]>([
    { domain: "Software Architecture", level: "expert" },
    { domain: "Cosmology", level: "novice" }
  ]);
  
  const [newDomain, setNewDomain] = useState("");
  const [newLevel, setNewLevel] = useState("intermediate");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");

  // Interactive Prompt Preview Simulation
  const [testPrompt, setTestPrompt] = useState("Explain how the universe is expanding");
  const [simulatedVocab, setSimulatedVocab] = useState<string[]>([]);
  const [simulatedPrompt, setSimulatedPrompt] = useState("");
  const [simulating, setSimulating] = useState(false);

  // Fetch current profile from backend API
  useEffect(() => {
    const controller = new AbortController();
    const fetchProfile = async () => {
      try {
        const data = await api.getUserProfile(controller.signal);
        if (data) {
          const meta = data.profile_metadata || {};
          const prefs = data.cognition_preferences || {};
          
          if (meta.profession) setProfession(meta.profession);
          if (prefs.intellectual_level) setLevel(prefs.intellectual_level);
          
          if (prefs.cognitive_style) {
            if (prefs.cognitive_style.verbosity) setVerbosity(prefs.cognitive_style.verbosity);
            if (prefs.cognitive_style.reasoning_preference) setReasoning(prefs.cognitive_style.reasoning_preference);
          }
          
          if (meta.domain_expertise && Array.isArray(meta.domain_expertise)) {
            setDomainExpertise(meta.domain_expertise);
          }
        }
      } catch (err) {
        // Fall back to default profile settings
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
    return () => controller.abort();
  }, []);

  // Update simulation whenever inputs or settings change
  useEffect(() => {
    if (!testPrompt.trim()) return;

    setSimulating(true);
    const timer = setTimeout(() => {
      // Logic to dynamically generate mock preview values based on user's current settings
      const promptLower = testPrompt.toLowerCase();
      let terms: string[] = [];
      let finalPrompt = "";

      if (promptLower.includes("universe") || promptLower.includes("expand") || promptLower.includes("cosmology")) {
        const isCosmologyExpert = domainExpertise.some(d => d.domain.toLowerCase() === "cosmology" && (d.level === "expert" || d.level === "advanced")) || level === "expert";
        const isCosmologyNovice = domainExpertise.some(d => d.domain.toLowerCase() === "cosmology" && d.level === "novice") || level === "novice";

        if (isCosmologyExpert) {
          terms = ["FLRW metric", "Hubble parameter", "Cosmic expansion scale-factor", "Vacuum energy density", "Einstein field equations"];
          finalPrompt = `Conduct a rigorous, graduate-level analysis of cosmic expansion under the FLRW metric. Focus on the mathematical derivation of the Hubble parameter and incorporate vacuum energy density values. Explain structural topology using Einstein's field equations.`;
        } else if (isCosmologyNovice) {
          terms = ["Hubble's Observation", "Galaxies moving apart", "Baking raisin bread analogy", "Redshift"];
          finalPrompt = `Explain why the universe is expanding using intuitive, visual analogies (like baking raisin bread or inflating a balloon). Keep the language accessible for a hobbyist, focus on Hubble's basic redshift observation, and avoid complex equations.`;
        } else {
          terms = ["Cosmic expansion", "Dark energy", "Hubble-Lemaître law", "Redshift"];
          finalPrompt = `Provide a balanced overview of cosmic expansion. Explain the role of dark energy and state the Hubble-Lemaître law conceptually. Describe how redshift is measured without dive-bombing into advanced mathematics.`;
        }
      } else if (promptLower.includes("company") || promptLower.includes("ant") || promptLower.includes("software")) {
        const isSoftwareExpert = domainExpertise.some(d => d.domain.toLowerCase().includes("software") && (d.level === "expert" || d.level === "advanced")) || level === "expert";
        const isSoftwareNovice = domainExpertise.some(d => d.domain.toLowerCase().includes("software") && d.level === "novice") || level === "novice";

        if (isSoftwareExpert) {
          terms = ["Stigmergy", "Decentralized Autopoiesis", "Event-driven orchestration", "DAG state machine"];
          finalPrompt = `Deconstruct the target company structure using stigmergic design patterns and autopoietic loops. Design a decentralized microservice model that behaves like ant-colony pheromone trails, and map the coordination logic as a DAG state machine.`;
        } else if (isSoftwareNovice) {
          terms = ["Teamwork", "Coordinating together", "Ant colony rules", "System organization"];
          finalPrompt = `Explain how a company can work like an ant colony in simple terms. Focus on how individual small tasks sum up to a larger system, avoiding overly dense architectural jargon, and provide practical software team analogies.`;
        } else {
          terms = ["Swarm intelligence", "Distributed coordination", "Asynchronous messaging", "Self-organizing architecture"];
          finalPrompt = `Analyze the structural properties of self-organizing company models. Utilize distributed coordination patterns and map them to asynchronous messaging loops reminiscent of biological swarm intelligence.`;
        }
      } else {
        // Generic prompt
        if (level === "expert") {
          terms = ["Metacognitive framing", "First-principles analysis", "Heuristic validation"];
          finalPrompt = `Perform a first-principles analysis of the request: "${testPrompt}". Utilize precise terminology and outline heuristic validation bounds for the response framework.`;
        } else if (level === "novice") {
          terms = ["Basic concepts", "Step-by-step breakdown", "Analogy mapping"];
          finalPrompt = `Break down the core concept of "${testPrompt}" step-by-step. Use plain language and helpful comparisons to ensure a clear baseline understanding.`;
        } else {
          terms = ["Conceptual mapping", "Structured decomposition"];
          finalPrompt = `Analyze and answer the query: "${testPrompt}". Provide a structured breakdown with balanced detail.`;
        }
      }

      setSimulatedVocab(terms);
      setSimulatedPrompt(finalPrompt);
      setSimulating(false);
    }, 400);

    return () => clearTimeout(timer);
  }, [testPrompt, level, domainExpertise, verbosity, reasoning]);

  const handleSave = async () => {
    setSaving(true);
    setSaveStatus("idle");
    try {
      const success = await api.updateUserProfile({
        profession,
        intellectual_level: level,
        cognitive_style: { verbosity, reasoning_preference: reasoning },
        domain_expertise: domainExpertise
      });
      if (success) {
        setSaveStatus("success");
        setTimeout(() => setSaveStatus("idle"), 3000);
      } else {
        setSaveStatus("error");
      }
    } catch (err) {
      console.error("Failed to save cognitive profile changes:", err);
      setSaveStatus("error");
    } finally {
      setSaving(false);
    }
  };

  const addDomain = () => {
    if (!newDomain.trim()) return;
    if (domainExpertise.some(d => d.domain.toLowerCase() === newDomain.trim().toLowerCase())) return;
    
    setDomainExpertise(prev => [...prev, { domain: newDomain.trim(), level: newLevel }]);
    setNewDomain("");
  };

  const removeDomain = (index: number) => {
    setDomainExpertise(prev => prev.filter((_, i) => i !== index));
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-[#05070a]">
        <div className="flex flex-col items-center space-y-4">
          <BrainCircuit className="w-10 h-10 text-primary animate-pulse" />
          <p className="text-sm text-slate-400">Loading User Cognitive Profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 text-slate-800 dark:text-slate-200 font-sans">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200/60 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sliders className="w-5 h-5 text-primary" />
            <h2 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-400">
              Cognitive Profile Settings
            </h2>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Customize your professional persona, depth thresholds, and domain expertise to tune prompt optimization.
          </p>
        </div>
        
        <div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-xl font-bold shadow-lg shadow-primary/20 transition-all text-sm disabled:opacity-50"
          >
            {saving ? (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : saveStatus === "success" ? (
              <Check className="w-4 h-4" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {saving ? "Saving..." : saveStatus === "success" ? "Saved Successfully!" : "Save Profile"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Settings Form (Left) */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* Card 1: Core Persona */}
          <div className="bg-white dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-6 space-y-6 shadow-sm">
            <div className="flex items-center gap-3 border-b border-slate-100 dark:border-slate-800/50 pb-4">
              <User className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Core Cognitive Persona</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Profession / Background</label>
                <input 
                  type="text" 
                  value={profession} 
                  onChange={(e) => setProfession(e.target.value)}
                  placeholder="e.g. Software Architect, Biology Student"
                  className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary text-slate-800 dark:text-white"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Intellectual Depth Level</label>
                <select 
                  value={level} 
                  onChange={(e) => setLevel(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-white/5 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary text-slate-800 dark:text-slate-200"
                >
                  <option value="novice">Novice / Generalist (Analogies & Baselines)</option>
                  <option value="intermediate">Intermediate (Balanced Explanations)</option>
                  <option value="expert">Expert / Specialist (Jargon & Math depth)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Card 2: Cognitive Style */}
          <div className="bg-white dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-6 space-y-6 shadow-sm">
            <div className="flex items-center gap-3 border-b border-slate-100 dark:border-slate-800/50 pb-4">
              <Layers className="w-5 h-5 text-amber-500" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Explanation & Reasoning Style</h3>
            </div>

            <div className="space-y-6">
              {/* Verbosity Slider Selector */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Output Verbosity Preference</label>
                <div className="grid grid-cols-3 gap-2 bg-slate-50 dark:bg-white/5 p-1 rounded-xl">
                  {["concise", "balanced", "detailed"].map((v) => (
                    <button
                      key={v}
                      type="button"
                      onClick={() => setVerbosity(v)}
                      className={`py-2 rounded-lg text-xs font-bold capitalize transition-all ${
                        verbosity === v 
                          ? 'bg-white dark:bg-slate-850 text-primary shadow-sm' 
                          : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                      }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>

              {/* Reasoning Preference */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wide">Preferred Reasoning Framework</label>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { id: "analogy-driven", name: "Analogy-Driven", desc: "Prefers comparisons & everyday examples" },
                    { id: "first-principles", name: "First-Principles", desc: "Deconstructs concept from foundational truths" },
                    { id: "step-by-step", name: "Step-by-Step", desc: "Systematic, logical sequence explanation" },
                    { id: "balanced", name: "Adaptive / Balanced", desc: "Auto-select framework based on domain" },
                  ].map((r) => (
                    <div
                      key={r.id}
                      onClick={() => setReasoning(r.id)}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        reasoning === r.id 
                          ? 'border-primary/50 bg-primary/5' 
                          : 'border-slate-200 dark:border-white/5 hover:border-slate-350 hover:bg-slate-50/50 dark:hover:bg-white/[0.02]'
                      }`}
                    >
                      <p className="text-xs font-bold text-slate-800 dark:text-white">{r.name}</p>
                      <p className="text-[10px] text-slate-400 mt-1">{r.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Card 3: Domain Expertise */}
          <div className="bg-white dark:bg-slate-900/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-6 space-y-6 shadow-sm">
            <div className="flex items-center gap-3 border-b border-slate-100 dark:border-slate-800/50 pb-4">
              <GraduationCap className="w-5 h-5 text-emerald-500" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Domain-Specific Knowledge</h3>
            </div>

            {/* List domains */}
            <div className="space-y-3">
              {domainExpertise.map((item, index) => (
                <div 
                  key={index} 
                  className="flex items-center justify-between p-3.5 bg-slate-55 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 rounded-xl"
                >
                  <div>
                    <p className="text-xs font-bold text-slate-800 dark:text-white">{item.domain}</p>
                    <p className="text-[10px] text-slate-400 capitalize">Level: {item.level}</p>
                  </div>
                  <button 
                    onClick={() => removeDomain(index)}
                    className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-500/10 transition-colors"
                  >
                    <Trash size={14} />
                  </button>
                </div>
              ))}
            </div>

            {/* Add Domain Form */}
            <div className="flex flex-col sm:flex-row gap-3 pt-3 border-t border-slate-100 dark:border-slate-850">
              <input 
                type="text" 
                placeholder="Add domain (e.g. Physics, History)..." 
                value={newDomain}
                onChange={(e) => setNewDomain(e.target.value)}
                className="flex-1 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl px-4 py-2 text-xs focus:outline-none text-slate-800 dark:text-white"
              />
              <select 
                value={newLevel} 
                onChange={(e) => setNewLevel(e.target.value)}
                className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-white/5 rounded-xl px-3 py-2 text-xs focus:outline-none text-slate-800 dark:text-slate-200"
              >
                <option value="novice">Novice</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
              <button
                onClick={addDomain}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-600 dark:text-slate-200 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 border border-slate-200 dark:border-white/5"
              >
                <Plus size={14} /> Add
              </button>
            </div>
          </div>

        </div>

        {/* Live Simulator Preview Card (Right) */}
        <div className="lg:col-span-5">
          <div className="sticky top-6 bg-slate-900 border border-white/5 rounded-3xl p-6 shadow-2xl space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
            
            <div className="flex items-center justify-between border-b border-white/5 pb-4">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-primary" />
                <h3 className="text-base font-bold text-white uppercase tracking-wider">Pipeline Simulator</h3>
              </div>
              <div className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono">
                <Sparkles size={10} /> Active Preview
              </div>
            </div>

            {/* Test Input Prompt */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Test User Prompt</label>
              <textarea 
                value={testPrompt}
                onChange={(e) => setTestPrompt(e.target.value)}
                rows={2}
                className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-xs text-white focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
                placeholder="Type a testing query (e.g. cosmological expansion, build a software company)..."
              />
            </div>

            {/* Live Synthesis Output */}
            <div className="space-y-4 pt-2 border-t border-white/5">
              
              {/* Expanded Vocabulary Preview */}
              <div className="space-y-2">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Vocabulary Engine Output</p>
                <div className="flex flex-wrap gap-1.5">
                  {simulating ? (
                    <span className="text-xs text-slate-500 italic">Simulating semantic concepts...</span>
                  ) : simulatedVocab.length > 0 ? (
                    simulatedVocab.map((v, i) => (
                      <span key={i} className="text-[10px] font-bold font-mono px-2.5 py-1 bg-white/5 text-primary rounded-lg border border-white/5">
                        #{v}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500 italic">No domain terms extracted. Try terms like 'universe' or 'company'.</span>
                  )}
                </div>
              </div>

              {/* Synthesized Prompt Preview */}
              <div className="space-y-1">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Synthesized Prompt (Sent to LLM)</p>
                <div className="bg-white/[0.03] border border-white/5 rounded-2xl p-4 relative min-h-[120px]">
                  {simulating ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : (
                    <p className="text-xs text-slate-350 leading-relaxed font-semibold italic">
                      "{simulatedPrompt || "Enter a prompt above to see how CognitiveOS customizes the output prompt to match your profile settings."}"
                    </p>
                  )}
                </div>
              </div>

              {/* Persona Context Box */}
              <div className="bg-blue-500/5 border border-blue-500/10 rounded-2xl p-4 flex gap-3">
                <HelpCircle size={16} className="text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h5 className="text-xs font-bold text-blue-300">How is this custom-spliced?</h5>
                  <p className="text-[10px] text-slate-400 leading-relaxed mt-1">
                    When you submit a prompt, the system detects your background (<span className="text-white font-semibold">{profession}</span>) and intellectual level (<span className="text-white font-semibold">{level}</span>). The optimization engines adapt vocabulary density and complexity to match your capability level.
                  </p>
                </div>
              </div>

            </div>

          </div>
        </div>

      </div>

    </div>
  );
}
