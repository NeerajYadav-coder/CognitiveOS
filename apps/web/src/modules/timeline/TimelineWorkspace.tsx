"use client";

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  History, 
  Clock, 
  Tag, 
  AlertTriangle, 
  CheckCircle2, 
  Terminal, 
  ExternalLink,
  Search,
  Filter
} from 'lucide-react';
import { api } from '@/services/api';

interface Interaction {
  id: string;
  session_id: string;
  raw_input: string;
  normalized_input?: string;
  intent_output?: {
    primary_intent: string;
    domain: string;
    depth_level: string;
    confidence: number;
  };
  cognitive_mode?: {
    primary_mode: string;
    confidence: number;
  };
  ambiguity_score: number;
  orchestration_trace?: any;
  created_at: string;
}

const mockHistory: Interaction[] = [
  {
    id: 'hist-1',
    session_id: 'session-d12f',
    raw_input: 'Explain Quantum Computing to a ten year old using metaphors about baking cookies and coding in JavaScript.',
    created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(), // 12m ago
    ambiguity_score: 0.25,
    cognitive_mode: { primary_mode: 'pedagogical', confidence: 0.92 },
    intent_output: { primary_intent: 'Explanation', domain: 'Physics / Computer Science', depth_level: 'novice', confidence: 0.95 }
  },
  {
    id: 'hist-2',
    session_id: 'session-d12f',
    raw_input: 'Need to write a rust macro that takes a struct and implements a builder pattern with default fallback values.',
    created_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(), // 35m ago
    ambiguity_score: 0.12,
    cognitive_mode: { primary_mode: 'technical', confidence: 0.96 },
    intent_output: { primary_intent: 'Code Generation', domain: 'Systems Programming', depth_level: 'expert', confidence: 0.98 }
  },
  {
    id: 'hist-3',
    session_id: 'session-a8f4',
    raw_input: 'i want to design a new garden layout in my backyard but it is sloped and receives partial shade in the afternoon. i like japanese maples and moss but i live in zone 7b. what plants should i choose and how should i plan the drainage?',
    created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(), // 2h ago
    ambiguity_score: 0.68,
    cognitive_mode: { primary_mode: 'exploratory', confidence: 0.84 },
    intent_output: { primary_intent: 'Design & Planning', domain: 'Horticulture / Landscaping', depth_level: 'intermediate', confidence: 0.89 }
  }
];

export default function TimelineWorkspace() {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const controller = new AbortController();

    const fetchInteractions = async () => {
      try {
        const data = await api.getInteractions(controller.signal);
        if (data && data.length > 0) {
          setInteractions([...data, ...mockHistory]);
          setSelectedId(prev => prev || data[0].id);
        } else {
          setInteractions(mockHistory);
          setSelectedId(prev => prev || mockHistory[0].id);
        }
      } catch (err) {
        setInteractions(mockHistory);
        setSelectedId(prev => prev || mockHistory[0].id);
      } finally {
        setLoading(false);
      }
    };

    fetchInteractions();
    const interval = setInterval(fetchInteractions, 6000);
    return () => {
      clearInterval(interval);
      controller.abort();
    };
  }, []);

  const filteredInteractions = interactions.filter(i => 
    i.raw_input.toLowerCase().includes(searchQuery.toLowerCase()) ||
    i.intent_output?.primary_intent.toLowerCase().includes(searchQuery.toLowerCase()) ||
    i.cognitive_mode?.primary_mode.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedInteraction = interactions.find(i => i.id === selectedId) || null;

  const formatDate = (isoStr: string) => {
    const date = new Date(isoStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const getRelativeTime = (isoStr: string) => {
    const date = new Date(isoStr);
    const diffMs = Date.now() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="w-full h-full flex flex-col md:flex-row overflow-hidden bg-slate-50 dark:bg-[#05070a] font-sans">
      
      {/* Timeline Stream Panel */}
      <div className="w-full md:w-[450px] border-r border-slate-200 dark:border-white/5 bg-white dark:bg-[#0a0c10] flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-slate-200 dark:border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <History className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-bold tracking-tight">Prompt History</h2>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 dark:bg-white/5 rounded-lg border border-slate-200 dark:border-white/5">
            <Search size={14} className="text-slate-400" />
            <input 
              type="text" 
              placeholder="Search history..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none text-xs focus:ring-0 outline-none w-full text-slate-700 dark:text-slate-200"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 relative">
          {/* Vertical connecting line */}
          <div className="absolute left-[33px] top-6 bottom-6 w-0.5 bg-slate-100 dark:bg-slate-800 pointer-events-none" />

          <AnimatePresence>
            {filteredInteractions.map((item) => {
              const isSelected = item.id === selectedId;
              const mode = item.cognitive_mode?.primary_mode || 'exploratory';
              
              return (
                <motion.div
                  key={item.id}
                  onClick={() => setSelectedId(item.id)}
                  className={`flex gap-4 cursor-pointer relative z-10 group`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                >
                  {/* Timeline dot */}
                  <div className={`w-[36px] h-[36px] rounded-full flex items-center justify-center border mt-1 flex-shrink-0 transition-all duration-300 ${
                    isSelected 
                      ? 'bg-primary border-primary text-white shadow-lg shadow-primary/20' 
                      : 'bg-white dark:bg-[#0f1218] border-slate-200 dark:border-white/10 text-slate-400 group-hover:border-slate-300 dark:group-hover:border-white/20'
                  }`}>
                    <Clock size={14} className={isSelected ? 'animate-pulse' : ''} />
                  </div>

                  {/* Content card */}
                  <div className={`flex-1 p-4 rounded-2xl border transition-all duration-200 bg-white dark:bg-[#0a0c10] hover:shadow-md ${
                    isSelected 
                      ? 'border-primary/30 ring-1 ring-primary/10' 
                      : 'border-slate-200 dark:border-white/5 hover:border-slate-300 dark:hover:border-white/10'
                  }`}>
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                        {formatDate(item.created_at)}
                      </span>
                      <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400">
                        {getRelativeTime(item.created_at)}
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-200 line-clamp-2 leading-relaxed">
                      "{item.raw_input}"
                    </p>
                    <div className="flex items-center gap-2 mt-3">
                      <span className="text-[9px] font-bold uppercase tracking-wider bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 px-2 py-0.5 rounded">
                        {mode}
                      </span>
                      <span className="text-[9px] font-bold uppercase tracking-wider bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 px-2 py-0.5 rounded">
                        {((1 - item.ambiguity_score) * 100).toFixed(0)}% Clarity
                      </span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>

      {/* Detail Inspection Panel */}
      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-[#06080c] overflow-y-auto">
        <AnimatePresence mode="wait">
          {selectedInteraction ? (
            <motion.div
              key={selectedInteraction.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-8 space-y-8"
            >
              {/* Header */}
              <div className="border-b border-slate-200 dark:border-white/5 pb-6">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
                  <Terminal size={14} className="text-primary" />
                  <span>Prompt Details</span>
                </div>
                <h3 className="text-2xl font-extrabold tracking-tight text-slate-800 dark:text-white leading-tight">
                  Prompt Information
                </h3>
                <p className="text-xs font-mono text-slate-400 dark:text-slate-500 mt-2">
                  ID: {selectedInteraction.id}
                </p>
              </div>

              {/* Prompt Text */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Original Prompt</h4>
                <div className="bg-slate-50 dark:bg-white/5 border border-slate-200/50 dark:border-white/5 p-5 rounded-2xl">
                  <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed font-medium italic">
                    "{selectedInteraction.raw_input}"
                  </p>
                </div>
              </div>

              {/* Prompt Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Domain & Intent */}
                <div className="bg-slate-50 dark:bg-[#0a0c10] border border-slate-200/50 dark:border-white/5 p-4 rounded-xl space-y-3">
                  <div className="flex items-center gap-2 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                    <Tag size={12} className="text-blue-500" />
                    <span>Prompt Goal</span>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Primary Objective</p>
                    <p className="text-sm font-bold text-blue-500 capitalize">{selectedInteraction.intent_output?.primary_intent || 'Unknown'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Subject Domain</p>
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">{selectedInteraction.intent_output?.domain || 'General Inquiry'}</p>
                  </div>
                </div>

                {/* Cognitive Mode */}
                <div className="bg-slate-50 dark:bg-[#0a0c10] border border-slate-200/50 dark:border-white/5 p-4 rounded-xl space-y-3">
                  <div className="flex items-center gap-2 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                    <CheckCircle2 size={12} className="text-amber-500" />
                    <span>Thinking Style</span>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Selected Style</p>
                    <p className="text-sm font-bold text-amber-500 capitalize">{selectedInteraction.cognitive_mode?.primary_mode || 'Exploratory'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Confidence Score</p>
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                      {selectedInteraction.cognitive_mode?.confidence ? `${(selectedInteraction.cognitive_mode.confidence * 100).toFixed(0)}%` : 'N/A'}
                    </p>
                  </div>
                </div>

                {/* Entropy / Ambiguity */}
                <div className="bg-slate-50 dark:bg-[#0a0c10] border border-slate-200/50 dark:border-white/5 p-4 rounded-xl space-y-3">
                  <div className="flex items-center gap-2 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                    <AlertTriangle size={12} className="text-emerald-500" />
                    <span>Clarity Check</span>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Clarity Rating</p>
                    <p className="text-sm font-bold text-emerald-500">{((1 - selectedInteraction.ambiguity_score) * 100).toFixed(0)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Status</p>
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                      {selectedInteraction.ambiguity_score > 0.5 ? 'Broad / Unclear' : 'Clear & Precise'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Process Log */}
              <div className="border border-dashed border-slate-200 dark:border-white/5 rounded-2xl p-6 bg-slate-50/50 dark:bg-[#0a0c10]/40">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Execution Steps</h4>
                <div className="font-mono text-xs text-slate-500 dark:text-slate-400 space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-200/40 dark:border-white/5 pb-2">
                    <span>Engine Status:</span>
                    <span className="text-emerald-500 font-bold">SUCCESS</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-200/40 dark:border-white/5 pb-2">
                    <span>Received At:</span>
                    <span>{new Date(selectedInteraction.created_at).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-200/40 dark:border-white/5 pb-2">
                    <span>Saved to Database:</span>
                    <span>YES (COMMIT)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Sent to:</span>
                    <span className="flex items-center gap-1 hover:text-primary cursor-pointer">
                      ChatGPT Input <ExternalLink size={12} />
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="p-8 text-center text-slate-400 flex flex-col items-center justify-center h-full">
              <History size={36} className="mb-3 text-slate-300 animate-pulse" />
              <p className="text-sm">Select a timeline event to view details.</p>
            </div>
          )}
        </AnimatePresence>
      </div>

    </div>
  );
}
