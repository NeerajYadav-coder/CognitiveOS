"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Database, 
  Search, 
  Tag, 
  Cpu, 
  GitBranch, 
  Fingerprint, 
  Layers, 
  Sparkles,
  SlidersHorizontal,
  ChevronRight
} from 'lucide-react';
import { api } from '@/services/api';

interface VectorMemory {
  id: string;
  chunk: string;
  similarity: number;
  metadata: {
    source: string;
    engine: string;
    dimensions: number;
    tokens: number;
  };
  tags: string[];
}

const mockMemories: VectorMemory[] = [
  {
    id: 'vec-1',
    chunk: 'Stigmergy is a mechanism of indirect coordination, human-observed in ant colonies. In multi-agent LLM systems, this is realized by letting agents modify a shared canvas (semantic space) to guide subsequent agent inputs.',
    similarity: 0.942,
    metadata: { source: 'research-tree-1', engine: 'text-embedding-3-small', dimensions: 1536, tokens: 46 },
    tags: ['stigmergy', 'multi-agent', 'coordination']
  },
  {
    id: 'vec-2',
    chunk: 'Decay models for historical vectors represent artificial pheromone evaporation, preventing semantic retrieval overload by decreasing retrieval weight scaling exponentially: W = W_0 * e^(-0.05 * t).',
    similarity: 0.887,
    metadata: { source: 'research-tree-1', engine: 'text-embedding-3-small', dimensions: 1536, tokens: 38 },
    tags: ['decay', 'vectors', 'pheromones']
  },
  {
    id: 'vec-3',
    chunk: 'Self-Organizing Pipeline Routings map active API endpoints as dynamic graph connections. The orchestrator rewrites execution routes dynamically when HTTP error rates or timeouts exceed threshold bounds.',
    similarity: 0.814,
    metadata: { source: 'research-tree-2', engine: 'text-embedding-3-small', dimensions: 1536, tokens: 35 },
    tags: ['dynamic-routing', 'self-healing', 'pipelines']
  },
  {
    id: 'vec-4',
    chunk: 'To implement a builder pattern macro in Rust, write a declarative macro that processes struct field identifiers, generating private setters alongside a build() method that enforces mandatory field parameters.',
    similarity: 0.725,
    metadata: { source: 'timeline-hist-2', engine: 'text-embedding-3-small', dimensions: 1536, tokens: 42 },
    tags: ['rust', 'macros', 'builder-pattern']
  }
];

export default function MemoryWorkspace() {
  const [memories, setMemories] = useState<VectorMemory[]>(mockMemories);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeId, setActiveId] = useState<string | null>(mockMemories[0].id);

  React.useEffect(() => {
    const controller = new AbortController();
    const fetchLatest = async () => {
      try {
        const data = await api.getInteractions(controller.signal);
        if (data && data.length > 0) {
          const latest = data[0];
          
          const userMemory: VectorMemory = {
            id: latest.id,
            chunk: latest.raw_input,
            similarity: 0.995,
            metadata: {
              source: `telemetry-${latest.session_id.substring(0, 6)}`,
              engine: 'text-embedding-3-small',
              dimensions: 1536,
              tokens: Math.round(latest.raw_input.split(' ').length * 1.3)
            },
            tags: latest.intent_output?.domain && latest.intent_output.domain !== "Unknown" 
              ? [latest.intent_output.domain.toLowerCase().replace(/[^a-z0-9]/g, '-'), 'user-prompt', 'active-context']
              : ['user-prompt', 'active-context']
          };

          setMemories(prev => {
            const filtered = prev.filter(m => m.id !== latest.id && m.id !== 'user-memory');
            return [userMemory, ...filtered];
          });
          setActiveId(latest.id);
        }
      } catch (err) {
        // Fall back to default mock memories
      }
    };
    fetchLatest();
    return () => controller.abort();
  }, []);

  const activeMemory = memories.find(m => m.id === activeId) || null;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setMemories(mockMemories);
      return;
    }
    // Simulate vector query by filtering and giving randomized similarity scores
    const query = searchQuery.toLowerCase();
    const results = mockMemories.map(m => {
      const matchCount = m.chunk.toLowerCase().split(query).length - 1;
      const tagMatches = m.tags.filter(t => t.toLowerCase().includes(query)).length;
      let score = m.similarity;
      
      if (matchCount > 0 || tagMatches > 0) {
        score = Math.min(0.99, m.similarity + 0.05 * (matchCount + tagMatches));
      } else {
        score = Math.max(0.35, m.similarity - 0.3);
      }
      
      return { ...m, similarity: score };
    }).sort((a, b) => b.similarity - a.similarity);

    setMemories(results);
    if (results.length > 0) setActiveId(results[0].id);
  };

  return (
    <div className="w-full h-full flex flex-col md:flex-row overflow-hidden bg-slate-50 dark:bg-[#05070a] font-sans">
      
      {/* Vector Queries Sidebar */}
      <div className="w-full md:w-[450px] border-r border-slate-200 dark:border-white/5 bg-white dark:bg-[#0a0c10] flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-slate-200 dark:border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-bold tracking-tight">Memory Bank</h2>
          </div>
          
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <div className="flex-1 flex items-center gap-2 px-3 py-2 bg-slate-100 dark:bg-white/5 rounded-lg border border-slate-200 dark:border-white/5">
              <Search size={14} className="text-slate-400" />
              <input 
                type="text" 
                placeholder="Search saved memory..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent border-none text-xs focus:ring-0 outline-none w-full text-slate-700 dark:text-slate-200"
              />
            </div>
            <button 
              type="submit"
              className="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-lg text-slate-400 border border-slate-200 dark:border-white/5"
            >
              <SlidersHorizontal size={14} />
            </button>
          </form>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 uppercase mb-2">
            <span>Query Results</span>
            <span>Relevance Score</span>
          </div>

          <AnimatePresence>
            {memories.map((item) => {
              const isSelected = item.id === activeId;
              const simPercent = (item.similarity * 100).toFixed(1);
              
              return (
                <motion.div
                  key={item.id}
                  onClick={() => setActiveId(item.id)}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className={`p-4 rounded-2xl border transition-all duration-200 cursor-pointer bg-white dark:bg-[#0a0c10] hover:shadow-md ${
                    isSelected 
                      ? 'border-primary/30 ring-1 ring-primary/10' 
                      : 'border-slate-200 dark:border-white/5 hover:border-slate-300 dark:hover:border-white/10'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-200 line-clamp-2 leading-relaxed flex-1">
                      "{item.chunk}"
                    </p>
                    <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded ${
                      item.similarity > 0.85 ? 'text-emerald-500 bg-emerald-500/10' :
                      item.similarity > 0.70 ? 'text-blue-500 bg-blue-500/10' :
                      'text-slate-500 bg-slate-100 dark:bg-white/5'
                    }`}>
                      {simPercent}%
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 mt-3 flex-wrap">
                    {item.tags.map(t => (
                      <span key={t} className="text-[9px] font-bold text-primary/70 bg-primary/5 px-2 py-0.5 rounded">
                        #{t}
                      </span>
                    ))}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>

      {/* Vector Metadata Inspection Pane */}
      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-[#06080c] overflow-y-auto">
        <AnimatePresence mode="wait">
          {activeMemory ? (
            <motion.div
              key={activeMemory.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-8 space-y-8"
            >
              {/* Header */}
              <div className="border-b border-slate-200 dark:border-white/5 pb-6">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
                  <Fingerprint size={14} className="text-primary" />
                  <span>Memory Details</span>
                </div>
                <h3 className="text-2xl font-extrabold tracking-tight text-slate-800 dark:text-white leading-tight">
                  Memory Log Details
                </h3>
                <p className="text-xs font-mono text-slate-400 dark:text-slate-500 mt-2">
                  ID: {activeMemory.id}
                </p>
              </div>

              {/* Chunk Text */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Saved Text</h4>
                <div className="bg-slate-50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 p-5 rounded-2xl">
                  <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed font-semibold italic">
                    "{activeMemory.chunk}"
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-[#0a0c10] rounded-xl flex items-start gap-3">
                  <GitBranch size={16} className="text-slate-400 mt-0.5" />
                  <div>
                    <h5 className="text-[10px] font-bold text-slate-400 uppercase">Source</h5>
                    <p className="text-xs font-bold text-primary mt-1">{activeMemory.metadata.source}</p>
                  </div>
                </div>
                
                <div className="p-4 border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-[#0a0c10] rounded-xl flex items-start gap-3">
                  <Layers size={16} className="text-slate-400 mt-0.5" />
                  <div>
                    <h5 className="text-[10px] font-bold text-slate-400 uppercase">Memory Size</h5>
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mt-1">
                      {activeMemory.metadata.dimensions} Points
                    </p>
                  </div>
                </div>
              </div>

              <div className="border border-dashed border-slate-200 dark:border-white/5 rounded-2xl p-6 bg-slate-50/50 dark:bg-[#0a0c10]/40">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">System Info</h4>
                <div className="font-mono text-xs text-slate-500 dark:text-slate-400 space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-200/40 dark:border-white/5 pb-2">
                    <span>AI Model Name:</span>
                    <span>{activeMemory.metadata.engine}</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-200/40 dark:border-white/5 pb-2">
                    <span>Word/Token Count:</span>
                    <span>{activeMemory.metadata.tokens} tokens</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Status:</span>
                    <span className="text-emerald-500 font-bold flex items-center gap-1">
                      Active / Saved <Sparkles size={12} />
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="p-8 text-center text-slate-400 flex flex-col items-center justify-center h-full">
              <Database size={36} className="mb-3 text-slate-300 animate-pulse" />
              <p className="text-sm">Select a memory result to view vector metadata details.</p>
            </div>
          )}
        </AnimatePresence>
      </div>

    </div>
  );
}
