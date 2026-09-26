"use client";

import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  useNodesState, 
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  MarkerType,
  BackgroundVariant
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Plus, Share2, Sparkles, X, Mic, Copy, Check, Info } from 'lucide-react';
import { api, type GraphSynthesisResponse } from '@/services/api';
import { VoiceThoughtInput } from '@/components/voice/VoiceThoughtInput';

const initialNodes = [
  { 
    id: '1', 
    type: 'input', 
    data: { label: 'CognitiveOS Core' }, 
    position: { x: 260, y: 20 },
    className: 'bg-primary/10 border-2 border-primary/40 text-primary font-bold rounded-2xl p-4 shadow-sm'
  },
  { 
    id: '2', 
    data: { label: 'Semantic Memory Nervous System' }, 
    position: { x: 80, y: 160 },
    className: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 text-slate-800 dark:text-slate-100 rounded-2xl p-4 shadow-lg'
  },
  { 
    id: '3', 
    data: { label: 'Knowledge Graph Topology' }, 
    position: { x: 420, y: 160 },
    className: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 text-slate-800 dark:text-slate-100 rounded-2xl p-4 shadow-lg'
  },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1-3', source: '1', target: '3', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
];

export const SemanticGraphWorkspace = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newConceptName, setNewConceptName] = useState("");
  const [shareNotice, setShareNotice] = useState(false);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [showSynthesizeModal, setShowSynthesizeModal] = useState(false);
  const [synthesizing, setSynthesizing] = useState(false);
  const [synthesisResult, setSynthesisResult] = useState<GraphSynthesisResponse | null>(null);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  // Poll database for dynamic concept nodes and relationships
  useEffect(() => {
    const controller = new AbortController();

    const fetchGraphData = async () => {
      const data = await api.getInteractions(controller.signal);
      if (data && data.length > 0) {
        const dynamicNodes = [...initialNodes];
        const dynamicEdges = [...initialEdges];
        const nodeIds = new Set(initialNodes.map(n => n.id));
        const edgeIds = new Set(initialEdges.map(e => e.id));

        data.forEach((interaction: any, idx: number) => {
          const graph = interaction.orchestration_trace?.semantic_graph;
          if (graph) {
            const conceptNodes = graph.concept_nodes || [];
            const relationships = graph.semantic_relationships || [];

            conceptNodes.forEach((node: any, nodeIdx: number) => {
              const id = node.id || `node-${node.label}`;
              if (!nodeIds.has(id)) {
                nodeIds.add(id);
                const angle = (nodeIdx / Math.max(conceptNodes.length, 1)) * 2 * Math.PI + idx;
                const radius = 220 + idx * 30;
                dynamicNodes.push({
                  id,
                  data: { label: node.label },
                  position: { 
                    x: 260 + Math.cos(angle) * radius, 
                    y: 160 + Math.sin(angle) * radius 
                  },
                  className: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 text-slate-800 dark:text-slate-100 rounded-2xl p-4 shadow-md text-xs font-semibold'
                });
              }
            });

            relationships.forEach((rel: any) => {
              const edgeId = `e-${rel.source}-${rel.target}`;
              if (!edgeIds.has(edgeId)) {
                edgeIds.add(edgeId);
                dynamicEdges.push({
                  id: edgeId,
                  source: rel.source,
                  target: rel.target,
                  animated: true,
                  markerEnd: { type: MarkerType.ArrowClosed }
                });
              }
            });
          }
        });

        setNodes(dynamicNodes);
        setEdges(dynamicEdges);
      }
    };

    fetchGraphData();
    const interval = setInterval(fetchGraphData, 6000);
    return () => {
      clearInterval(interval);
      controller.abort();
    };
  }, [setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleCreateConcept = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newConceptName.trim()) return;

    const id = `concept-${Date.now()}`;
    const newNode = {
      id,
      data: { label: newConceptName.trim() },
      position: { 
        x: 250 + (Math.random() - 0.5) * 300, 
        y: 220 + (Math.random() - 0.5) * 200 
      },
      className: 'bg-white dark:bg-slate-900 border border-primary/30 text-slate-800 dark:text-slate-100 rounded-2xl p-4 shadow-md text-xs font-semibold'
    };

    setNodes((nds) => [...nds, newNode]);
    setEdges((eds) => [
      ...eds,
      {
        id: `e-1-${id}`,
        source: '1',
        target: id,
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed }
      }
    ]);

    setNewConceptName("");
    setShowAddModal(false);
  };

  const handleShare = () => {
    setShareNotice(true);
    setTimeout(() => setShareNotice(false), 3000);
  };

  const handleSynthesizeGraph = async () => {
    setSynthesizing(true);
    try {
      const graphNodes = nodes.map(n => ({ id: n.id, label: (n.data?.label as string) || n.id }));
      const graphEdges = edges.map(e => ({ source: e.source, target: e.target }));
      const result = await api.synthesizeGraph(graphNodes, graphEdges);
      if (result) {
        setSynthesisResult(result);
        setShowSynthesizeModal(true);
      }
    } catch (err) {
      console.error("Failed to synthesize graph:", err);
    } finally {
      setSynthesizing(false);
    }
  };

  const handleApplyVoicePrompt = (prompt: string) => {
    const id = `voice-${Date.now()}`;
    const newNode = {
      id,
      data: { label: prompt.slice(0, 45) + "..." },
      position: { x: 260 + (Math.random() - 0.5) * 200, y: 220 + (Math.random() - 0.5) * 150 },
      className: 'bg-emerald-500/10 border border-emerald-500/30 text-slate-800 dark:text-slate-100 rounded-2xl p-4 shadow-lg text-xs font-semibold'
    };
    setNodes(nds => [...nds, newNode]);
    setShowVoiceModal(false);
  };

  const copyPrompt = () => {
    if (!synthesisResult?.synthesized_prompt) return;
    navigator.clipboard.writeText(synthesisResult.synthesized_prompt);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  return (
    <div className="w-full h-full flex flex-col relative overflow-hidden">
      {/* Action Toolbar */}
      <div className="h-14 px-6 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/60 dark:bg-[#0a0c10]/60 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/5">
            <Search size={14} className="text-slate-400" />
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter concepts..." 
              className="bg-transparent border-none text-xs focus:ring-0 outline-none w-48 text-slate-800 dark:text-slate-200"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={() => setShowVoiceModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold transition-all cursor-pointer"
            title="Spoken Thought Dictation"
          >
            <Mic size={14} className="text-primary" />
            <span className="hidden sm:inline">Voice Thought</span>
          </button>
          <button 
            onClick={handleSynthesizeGraph}
            disabled={synthesizing}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all cursor-pointer disabled:opacity-50"
            title="Synthesize all canvas nodes into a multi-perspective LLM prompt"
          >
            <Sparkles size={14} className={synthesizing ? "animate-spin" : ""} />
            <span>{synthesizing ? "Synthesizing..." : "Synthesize Canvas"}</span>
          </button>
          <button 
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-primary text-white rounded-xl text-xs font-semibold shadow-sm hover:opacity-95 active:scale-95 transition-all cursor-pointer"
          >
            <Plus size={14} />
            New Concept
          </button>
          <button 
            onClick={handleShare}
            title="Export Graph State"
            className="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl text-slate-500 dark:text-slate-400 transition-colors"
          >
            <Share2 size={15} />
          </button>
        </div>
      </div>

      {/* Share Toast */}
      <AnimatePresence>
        {shareNotice && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-slate-900 text-white dark:bg-white dark:text-slate-900 rounded-full text-xs font-medium shadow-xl flex items-center gap-2"
          >
            <Sparkles size={14} className="text-primary" />
            Graph snapshot copied to clipboard!
          </motion.div>
        )}
      </AnimatePresence>

      {/* Voice Thought Ingestion Modal */}
      <AnimatePresence>
        {showVoiceModal && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <VoiceThoughtInput
              onClose={() => setShowVoiceModal(false)}
              onApplyPrompt={handleApplyVoicePrompt}
            />
          </div>
        )}
      </AnimatePresence>

      {/* Synthesized Prompt Modal */}
      <AnimatePresence>
        {showSynthesizeModal && synthesisResult && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-2xl bg-white dark:bg-[#0a0c10] border border-slate-200 dark:border-white/10 rounded-2xl p-6 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">
                      Synthesized Mental Model Prompt
                    </h3>
                    <p className="text-xs text-slate-400">
                      Framework: <span className="font-semibold text-emerald-500">{synthesisResult.recommended_framework}</span>
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowSynthesizeModal(false)}
                  className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-white/5"
                >
                  <X size={16} />
                </button>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Conceptual Pathways ({synthesisResult.conceptual_pathways.length})
                  </span>
                  <button
                    onClick={copyPrompt}
                    className="inline-flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 font-medium cursor-pointer"
                  >
                    {copiedPrompt ? <Check size={14} /> : <Copy size={14} />}
                    {copiedPrompt ? "Copied!" : "Copy LLM Prompt"}
                  </button>
                </div>
                <div className="bg-slate-900 border border-white/10 rounded-xl p-4 font-mono text-xs text-emerald-400 whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
                  {synthesisResult.synthesized_prompt}
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setShowSynthesizeModal(false)}
                  className="px-4 py-2 bg-slate-100 dark:bg-white/10 hover:bg-slate-200 dark:hover:bg-white/15 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl"
                >
                  Done
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Modern In-Canvas Concept Creation Modal (Eliminates window.prompt) */}
      <AnimatePresence>
        {showAddModal && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-sm bg-white dark:bg-[#0a0c10] border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-2xl space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">Add Concept Node</h3>
                <button 
                  onClick={() => setShowAddModal(false)}
                  className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg"
                >
                  <X size={16} />
                </button>
              </div>
              <form onSubmit={handleCreateConcept} className="space-y-3">
                <input
                  type="text"
                  autoFocus
                  required
                  placeholder="e.g. Distributed Consensus Protocol"
                  value={newConceptName}
                  onChange={(e) => setNewConceptName(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 focus:ring-1 focus:ring-primary outline-none text-slate-800 dark:text-slate-100"
                />
                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-3 py-1.5 text-xs text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 text-xs font-semibold bg-primary text-white rounded-xl shadow-sm hover:opacity-95 transition-all cursor-pointer"
                  >
                    Add to Graph
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Interactive Flow Canvas */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes.map(n => ({
            ...n,
            style: searchQuery && !n.data.label.toLowerCase().includes(searchQuery.toLowerCase())
              ? { opacity: 0.25 }
              : { opacity: 1 }
          }))}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={(_, node) => setSelectedNode(node)}
          fitView
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#94a3b8" className="opacity-30" />
          <Controls className="bg-white/80 dark:bg-[#0a0c10]/80 border border-slate-200 dark:border-white/10 rounded-xl" />
          <MiniMap 
            className="bg-white/80 dark:bg-[#0a0c10]/80 border border-slate-200 dark:border-white/10 rounded-xl"
            nodeColor={(n: any) => (n.id === '1' ? '#3b82f6' : '#64748b')}
          />
        </ReactFlow>

        {/* Selected Node Details Card */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="absolute bottom-5 left-5 z-20 w-64 bg-white/95 dark:bg-[#0a0c10]/95 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl p-3 shadow-lg space-y-2 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                  <Info size={13} className="text-primary" />
                  Concept Details
                </span>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-0.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  <X size={12} />
                </button>
              </div>
              <p className="font-semibold text-primary">{selectedNode.data?.label}</p>
              <div className="text-[11px] text-slate-500 dark:text-slate-400 space-y-0.5">
                <div>Node ID: <span className="font-mono text-slate-700 dark:text-slate-300">{selectedNode.id}</span></div>
                <div>Connected Edges: <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).length}
                </span></div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Real Dynamic Stats Badge */}
        <div className="absolute bottom-5 right-5 px-3 py-2 bg-white/90 dark:bg-[#0a0c10]/90 backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl shadow-md text-[11px] font-medium text-slate-500 dark:text-slate-400 flex items-center gap-3 pointer-events-none">
          <div><span className="font-bold text-slate-800 dark:text-slate-200">{nodes.length}</span> Concepts</div>
          <div className="w-1 h-1 rounded-full bg-slate-300 dark:bg-white/20" />
          <div><span className="font-bold text-slate-800 dark:text-slate-200">{edges.length}</span> Semantic Links</div>
        </div>
      </div>
    </div>
  );
};
