"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  GitMerge, 
  GitBranch, 
  CheckCircle2, 
  Search, 
  ChevronRight, 
  Plus, 
  Compass, 
  BookOpen, 
  Cpu, 
  Lightbulb, 
  Sparkles,
  X
} from 'lucide-react';
import { api } from '@/services/api';

interface ResearchNode {
  id: string;
  label: string;
  type: 'hypothesis' | 'evidence' | 'synthesis' | 'conclusion';
  status: 'proven' | 'investigating' | 'unexplored';
  summary: string;
  details: string;
  parentId?: string;
}

interface ResearchTree {
  id: string;
  title: string;
  description: string;
  nodes: ResearchNode[];
}

const mockTrees: ResearchTree[] = [
  {
    id: 'tree-1',
    title: 'Biomimetic Multi-Agent Coordination',
    description: 'Applying ant colony stigmergy optimization models to distributed LLM consensus protocols.',
    nodes: [
      {
        id: 'node-1',
        label: 'Central Premise: Stigmergic Communication',
        type: 'hypothesis',
        status: 'proven',
        summary: 'Agents coordinate asynchronously using shared environment trace markers rather than direct message busing.',
        details: 'Stigmergy is a mechanism of indirect coordination observed in ant colonies. In multi-agent LLM systems, this is realized by letting agents modify a shared semantic state canvas to guide subsequent inputs, reducing network overhead from O(N^2) to O(N).'
      },
      {
        id: 'node-2',
        label: 'Pheromone Evaporation in Vector DB',
        type: 'evidence',
        status: 'investigating',
        summary: 'Decay models for historical vectors to prevent context retrieval saturation.',
        details: 'Pheromone decay models decrease similarity scores over time: W = W_0 * e^(-0.05*t). Applying this decay rate to memory retrieval pruned stale loops by 41% in benchmark trials.',
        parentId: 'node-1'
      },
      {
        id: 'node-3',
        label: 'Semantic Graph Synthesis Protocol',
        type: 'synthesis',
        status: 'proven',
        summary: 'Resolving multi-agent conflicts via semantic consensus trees.',
        details: 'Evaluates parent-child nodes where critic agents identify logical gaps, expand alternate branches, and synthesize a single unified knowledge graph structure.',
        parentId: 'node-1'
      },
      {
        id: 'node-4',
        label: 'Swarm Memory Consolidation',
        type: 'conclusion',
        status: 'unexplored',
        summary: 'Consolidating parallel agent outputs into unified persistent knowledge graph nodes.',
        details: 'Final step of stigmergic execution: compiles separate concept tags into unified persistent knowledge graph nodes.',
        parentId: 'node-3'
      }
    ]
  },
  {
    id: 'tree-2',
    title: 'Self-Organizing Cognitive Architecture',
    description: 'Autonomous pipeline self-healing based on telemetry error rates and semantic feedback loops.',
    nodes: [
      {
        id: 't2-n1',
        label: 'Adaptive Routing Fallbacks',
        type: 'hypothesis',
        status: 'investigating',
        summary: 'API pipelines that automatically re-route requests between deep and fast models.',
        details: 'Maps active routes as a dynamic graph that an orchestration agent regenerates when latency spikes or HTTP error rate increases.'
      }
    ]
  }
];

export default function ResearchWorkspace() {
  const [trees, setTrees] = useState<ResearchTree[]>(mockTrees);
  const [selectedTreeId, setSelectedTreeId] = useState(mockTrees[0].id);
  const [activeNodeId, setActiveNodeId] = useState<string | null>(mockTrees[0].nodes[0].id);
  const [searchQuery, setSearchQuery] = useState('');
  const [branchInput, setBranchInput] = useState('');
  const [branchSuccess, setBranchSuccess] = useState<string | null>(null);

  // Add Node Modal Form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newNodeLabel, setNewNodeLabel] = useState('');
  const [newNodeType, setNewNodeType] = useState<ResearchNode['type']>('hypothesis');
  const [newNodeSummary, setNewNodeSummary] = useState('');
  const [newNodeDetails, setNewNodeDetails] = useState('');

  // Hydrate latest user interaction from telemetry API
  useEffect(() => {
    const controller = new AbortController();
    const fetchLatest = async () => {
      const data = await api.getInteractions(controller.signal);
      if (data && data.length > 0) {
        const latest = data[0];
        const title = latest.intent_output?.domain && latest.intent_output.domain !== "Unknown"
          ? `Organic Systems: ${latest.intent_output.domain}`
          : "Active Cognitive Inquiry";

        const userTree: ResearchTree = {
          id: 'user-tree',
          title: title,
          description: `Research path compiled from prompt: "${latest.raw_input.substring(0, 60)}..."`,
          nodes: [
            {
              id: 'user-node-1',
              label: `Core Hypothesis: ${latest.intent_output?.primary_intent || 'Structured Cognitive Interaction'}`,
              type: 'hypothesis',
              status: 'investigating',
              summary: `Deconstructing: "${latest.raw_input.substring(0, 90)}..."`,
              details: `Input evaluated by cognitive pipeline:\n\nDomain: ${latest.intent_output?.domain || 'General'}\nMode: ${latest.cognitive_mode?.primary_mode || 'Exploratory'}\nDepth Level: ${latest.intent_output?.depth_level || 'Deep'}`
            },
            {
              id: 'user-node-2',
              label: 'Clarity & Entropy Assessment',
              type: 'evidence',
              status: latest.ambiguity_score > 0.5 ? 'investigating' : 'proven',
              summary: `Ambiguity index of ${(latest.ambiguity_score * 100).toFixed(0)}% measured by parser.`,
              details: latest.ambiguity_score > 0.5
                ? `The parser flagged high ambiguity (${(latest.ambiguity_score * 100).toFixed(0)}%). Recommendation: decompose multi-subject queries into distinct task boundaries.`
                : `The parser measured high clarity (${(100 - latest.ambiguity_score * 100).toFixed(0)}% confidence). Intent mapping is clear and ready for synthesis.`
            }
          ]
        };

        setTrees(prev => [userTree, ...prev.filter(t => t.id !== 'user-tree')]);
        setSelectedTreeId('user-tree');
        setActiveNodeId('user-node-1');
      }
    };

    fetchLatest();
    return () => controller.abort();
  }, []);

  const activeTree = trees.find(t => t.id === selectedTreeId) || trees[0];
  const activeNode = activeTree.nodes.find(n => n.id === activeNodeId) || null;

  const handleAddNode = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNodeLabel.trim() || !newNodeSummary.trim()) return;

    const newNode: ResearchNode = {
      id: `node-${Date.now()}`,
      label: newNodeLabel,
      type: newNodeType,
      status: 'unexplored',
      summary: newNodeSummary,
      details: newNodeDetails,
      parentId: activeNodeId || undefined
    };

    setTrees(trees.map(t => {
      if (t.id === selectedTreeId) {
        return { ...t, nodes: [...t.nodes, newNode] };
      }
      return t;
    }));

    setActiveNodeId(newNode.id);
    setShowAddForm(false);
    setNewNodeLabel('');
    setNewNodeSummary('');
    setNewNodeDetails('');
  };

  const submitBranch = () => {
    if (!branchInput.trim()) return;
    setBranchSuccess("Thought branch pinned! This concept is now linked to your browser extension overlay.");
    setTimeout(() => {
      setBranchSuccess(null);
      setBranchInput('');
    }, 4000);
  };

  const getNodeIcon = (type: ResearchNode['type']) => {
    switch (type) {
      case 'hypothesis': return <Lightbulb className="w-4 h-4 text-amber-500" />;
      case 'evidence': return <BookOpen className="w-4 h-4 text-blue-500" />;
      case 'synthesis': return <Cpu className="w-4 h-4 text-purple-500" />;
      case 'conclusion': return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
    }
  };

  const getStatusBadge = (status: ResearchNode['status']) => {
    switch (status) {
      case 'proven':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">Proven</span>;
      case 'investigating':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">Active</span>;
      case 'unexplored':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-white/5 text-slate-500 border border-slate-200 dark:border-white/10">Unexplored</span>;
    }
  };

  return (
    <div className="w-full h-full flex flex-col md:flex-row overflow-hidden bg-slate-50 dark:bg-[#05070a] font-sans">
      {/* Sidebar: Thought Paths */}
      <div className="w-full md:w-80 border-r border-slate-200 dark:border-white/5 bg-white dark:bg-[#0a0c10] flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-slate-200 dark:border-white/5 space-y-3">
          <div className="flex items-center gap-2">
            <GitMerge className="w-4 h-4 text-primary" />
            <h2 className="text-sm font-bold tracking-tight">Thought Paths</h2>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/5">
            <Search size={13} className="text-slate-400" />
            <input 
              type="text" 
              placeholder="Search paths..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none text-xs focus:ring-0 outline-none w-full text-slate-700 dark:text-slate-200"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {trees
            .filter(t => t.title.toLowerCase().includes(searchQuery.toLowerCase()))
            .map(t => (
              <button
                key={t.id}
                onClick={() => {
                  setSelectedTreeId(t.id);
                  if (t.nodes.length > 0) setActiveNodeId(t.nodes[0].id);
                }}
                className={`w-full text-left p-3 rounded-2xl border transition-all ${
                  selectedTreeId === t.id 
                    ? 'bg-primary/5 border-primary/20 text-primary shadow-sm'
                    : 'border-transparent text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5'
                }`}
              >
                <h3 className="text-xs font-bold truncate leading-snug">{t.title}</h3>
                <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                  {t.description}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[10px] bg-slate-100 dark:bg-white/5 px-2 py-0.5 rounded-full text-slate-500 font-mono">
                    {t.nodes.length} nodes
                  </span>
                </div>
              </button>
            ))}
        </div>
      </div>

      {/* Main Graph / Hierarchy */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto border-r border-slate-200 dark:border-white/5">
        <div className="h-14 px-6 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/50 dark:bg-black/20 backdrop-blur-md sticky top-0 z-10">
          <div>
            <h2 className="text-xs font-bold tracking-tight text-slate-800 dark:text-slate-100">{activeTree.title}</h2>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 truncate max-w-md">{activeTree.description}</p>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-xl text-xs font-semibold shadow-sm hover:opacity-95 active:scale-95 transition-all"
          >
            <Plus size={13} />
            Add Node
          </button>
        </div>

        <div className="flex-1 p-6 flex flex-col justify-start">
          <div className="max-w-xl mx-auto w-full space-y-4">
            <AnimatePresence mode="popLayout">
              {activeTree.nodes.map((node, index) => {
                const isActive = activeNodeId === node.id;
                return (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.04 }}
                    onClick={() => setActiveNodeId(node.id)}
                    className={`cursor-pointer w-full p-4 bg-white dark:bg-[#0a0c10] border rounded-2xl shadow-sm transition-all duration-200 flex items-start gap-3.5 hover:shadow-md ${
                      isActive 
                        ? 'border-primary ring-1 ring-primary/20 shadow-md' 
                        : 'border-slate-200 dark:border-white/5 hover:border-slate-300 dark:hover:border-white/10'
                    }`}
                  >
                    <div className="p-2 bg-slate-100 dark:bg-white/5 rounded-xl flex-shrink-0">
                      {getNodeIcon(node.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{node.type}</span>
                        {getStatusBadge(node.status)}
                      </div>
                      <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100 mt-1">{node.label}</h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed line-clamp-2">{node.summary}</p>
                    </div>
                    <ChevronRight size={15} className={`text-slate-400 self-center transition-transform ${isActive ? 'rotate-90 text-primary' : ''}`} />
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Right Drawer: Node Deep Dive / Branching */}
      <div className="w-full md:w-96 bg-white dark:bg-[#0a0c10] flex flex-col flex-shrink-0">
        <AnimatePresence mode="wait">
          {showAddForm ? (
            <motion.form
              key="add-form"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              onSubmit={handleAddNode}
              className="p-5 space-y-4 overflow-y-auto flex-1"
            >
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-white/5 pb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">New Thought Node</h3>
                <button 
                  type="button" 
                  onClick={() => setShowAddForm(false)}
                  className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
                >
                  <X size={15} />
                </button>
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Node Title</label>
                <input 
                  type="text"
                  required
                  placeholder="e.g. Adaptive Prompt Routing"
                  value={newNodeLabel}
                  onChange={(e) => setNewNodeLabel(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary outline-none text-slate-800 dark:text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Node Type</label>
                <select
                  value={newNodeType}
                  onChange={(e) => setNewNodeType(e.target.value as any)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary outline-none text-slate-800 dark:text-slate-200"
                >
                  <option value="hypothesis">Hypothesis</option>
                  <option value="evidence">Evidence / Telemetry</option>
                  <option value="synthesis">Synthesis Strategy</option>
                  <option value="conclusion">Final Principle</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Core Summary</label>
                <textarea
                  required
                  rows={2}
                  placeholder="One sentence summary of this insight."
                  value={newNodeSummary}
                  onChange={(e) => setNewNodeSummary(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary outline-none text-slate-800 dark:text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Detailed Evidence & Context</label>
                <textarea
                  rows={4}
                  placeholder="Additional observations, prompt context, or notes..."
                  value={newNodeDetails}
                  onChange={(e) => setNewNodeDetails(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary outline-none text-slate-800 dark:text-slate-200"
                />
              </div>

              <button 
                type="submit"
                className="w-full py-2 bg-primary text-white rounded-xl text-xs font-semibold shadow-sm hover:opacity-95 transition-all flex items-center justify-center gap-1.5"
              >
                <Sparkles size={13} />
                Save Node to Path
              </button>
            </motion.form>
          ) : activeNode ? (
            <motion.div
              key="node-details"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="p-5 space-y-5 flex-1 overflow-y-auto"
            >
              <div>
                <span className="text-[10px] font-bold text-primary uppercase tracking-wider bg-primary/10 px-2 py-0.5 rounded-full">
                  {activeNode.type}
                </span>
                <h3 className="text-base font-bold text-slate-800 dark:text-slate-100 mt-2">
                  {activeNode.label}
                </h3>
              </div>

              <div className="space-y-1">
                <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Premise</h4>
                <p className="text-xs font-medium text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-white/5 p-3 rounded-xl border border-slate-200/60 dark:border-white/5">
                  {activeNode.summary}
                </p>
              </div>

              <div className="space-y-1">
                <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Analysis & Notes</h4>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-line bg-slate-50/50 dark:bg-black/20 p-3 rounded-xl border border-slate-200/40 dark:border-white/5">
                  {activeNode.details}
                </p>
              </div>

              {/* Branching Section */}
              <div className="pt-4 border-t border-slate-200 dark:border-white/5 space-y-3">
                <div className="flex items-center gap-2">
                  <GitBranch size={14} className="text-primary" />
                  <h4 className="text-xs font-bold text-slate-700 dark:text-slate-200">Branch Sub-Thread</h4>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Fork this scientific node to explore an alternative hypothesis. Pinned branches automatically feed into your browser extension overlay.
                </p>

                <textarea
                  value={branchInput}
                  onChange={(e) => setBranchInput(e.target.value)}
                  placeholder="e.g. Test this with second-principles mathematical proofs..."
                  rows={2}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary outline-none text-slate-800 dark:text-slate-200"
                />

                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={submitBranch}
                    className="flex-1 py-2 bg-primary text-white rounded-xl text-xs font-semibold shadow-sm hover:opacity-95 transition-all flex items-center justify-center gap-1.5"
                  >
                    <Sparkles size={13} />
                    Pin Branch Context
                  </button>
                </div>

                {branchSuccess && (
                  <motion.div
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-600 dark:text-emerald-400 text-xs font-medium"
                  >
                    {branchSuccess}
                  </motion.div>
                )}
              </div>
            </motion.div>
          ) : (
            <div className="p-6 text-center text-slate-400 flex flex-col items-center justify-center h-full">
              <Compass size={24} className="mb-2 text-slate-300 animate-spin" />
              <p className="text-xs">Select a thought node to view research traces.</p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
