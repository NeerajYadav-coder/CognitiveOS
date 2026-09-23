"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  Cpu, 
  Terminal, 
  MessageSquare, 
  ShieldAlert, 
  BrainCircuit, 
  Bot,
  Activity,
  CheckCircle,
  Play,
  RotateCcw
} from 'lucide-react';
import { api } from '@/services/api';

interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'thinking' | 'communicating' | 'completed';
  avatarColor: string;
  description: string;
  cognitiveLoad: number;
}

interface AgentMessage {
  id: string;
  agentId: string;
  agentName: string;
  role: string;
  message: string;
  timestamp: string;
  isImportant?: boolean;
}

const initialAgents: Agent[] = [
  {
    id: 'agent-1',
    name: 'Intent Analyst',
    role: 'Deconstructs user thoughts, identifies hidden motivations and core domains.',
    status: 'completed',
    avatarColor: 'bg-blue-500',
    description: 'Finds the main goal in your raw prompt.',
    cognitiveLoad: 0
  },
  {
    id: 'agent-2',
    name: 'Research Crawler',
    role: 'Explores adjacent scientific nodes, facts, and queries semantic graph database.',
    status: 'idle',
    avatarColor: 'bg-purple-500',
    description: 'Connects your prompt with similar topics in your memory.',
    cognitiveLoad: 0
  },
  {
    id: 'agent-3',
    name: 'Synthesis Critic',
    role: 'Evaluates drafts for logical fallacies, ambiguities, or cognitive biases.',
    status: 'idle',
    avatarColor: 'bg-amber-500',
    description: 'Ensures the prompt design remains highly detailed and focused.',
    cognitiveLoad: 0
  },
  {
    id: 'agent-4',
    name: 'Prompt Constructor',
    role: 'Assembles context, taxonomy, constraints, and roles into a final optimal prompt.',
    status: 'idle',
    avatarColor: 'bg-emerald-500',
    description: 'Synthesizes structural prompt templates using markdown formatting.',
    cognitiveLoad: 0
  }
];

const mockConversation: AgentMessage[] = [
  {
    id: 'msg-1',
    agentId: 'agent-1',
    agentName: 'Intent Analyst',
    role: 'Intent Engine',
    message: 'Analyzing draft input. I detect multiple overlapping subjects: "Organic company structures", "Software architecture patterns", and "Ant colony stigmergy". The primary objective is educational research for blogging.',
    timestamp: '09:42:01'
  },
  {
    id: 'msg-2',
    agentId: 'agent-2',
    agentName: 'Research Crawler',
    role: 'Memory Search',
    message: 'Cross-referencing databases. Aligns with decentralized rules. Retrieving matched notes: (1) Pheromone-based trace decay, (2) Shared state memory canvas. Recommending related terms: "asynchronous coordination", "decentralized control".',
    timestamp: '09:42:03'
  },
  {
    id: 'msg-3',
    agentId: 'agent-3',
    agentName: 'Synthesis Critic',
    role: 'Critic Engine',
    message: 'CRITICAL ALERT: The original prompt mixes philosophical inquiry with technical paper writing. This introduces high ambiguity (70%). I recommend structuring the prompt to force the LLM to separate the theoretical biology model from the software routing architecture details.',
    timestamp: '09:42:05',
    isImportant: true
  },
  {
    id: 'msg-4',
    agentId: 'agent-4',
    agentName: 'Prompt Constructor',
    role: 'Synthesizer',
    message: 'Synthesis complete. Constructed a structured role-play prompt where the LLM acts as a biomimetic computer scientist. Injecting sections for: (1) Stigmergic coordination framework, (2) Software architecture application, and (3) Blog-formatted discussion.',
    timestamp: '09:42:08'
  }
];

export default function AgentsWorkspace() {
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [conversation, setConversation] = useState<AgentMessage[]>(mockConversation);
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const fetchLatest = async () => {
      try {
        const data = await api.getInteractions(controller.signal);
        if (data && data.length > 0) {
          const latest = data[0];
          const primaryIntent = latest.intent_output?.primary_intent || "Educational Research";
          const domain = latest.intent_output?.domain || "Organic System Design";
          const ambiguity = (latest.ambiguity_score * 100).toFixed(0);
          
          const dynamicConversation: AgentMessage[] = [
            {
              id: 'msg-1',
              agentId: 'agent-1',
              agentName: 'Intent Analyst',
              role: 'Intent Engine',
              message: `Analyzing draft input: "${latest.raw_input}"\n\nDetected intent: "${primaryIntent}" under the domain "${domain}". Primary mode is ${latest.cognitive_mode?.primary_mode || 'Exploratory'}.`,
              timestamp: '09:42:01'
            },
            {
              id: 'msg-2',
              agentId: 'agent-2',
              agentName: 'Research Crawler',
              role: 'Memory Search',
              message: `Searching saved terms and notes for matching keywords in your draft. Matching notes include stigmergic canvas pathways, biological ant trail models, and database persistence patterns.`,
              timestamp: '09:42:03'
            },
            {
              id: 'msg-3',
              agentId: 'agent-3',
              agentName: 'Synthesis Critic',
              role: 'Critic Engine',
              message: `CRITICAL ALERT: The original prompt is flagged with clarity rating of ${100 - parseInt(ambiguity)}%. ${latest.ambiguity_score > 0.5 ? "Recommend separating software details from conceptual sections." : "Clear draft. Perfect clarity."}`,
              timestamp: '09:42:05',
              isImportant: latest.ambiguity_score > 0.5
            },
            {
              id: 'msg-4',
              agentId: 'agent-4',
              agentName: 'Prompt Constructor',
              role: 'Synthesizer',
              message: `Synthesis complete. Assembled optimized prompt incorporating specific subheadings and role playing parameters. Injected back into LLM platform prompt area.`,
              timestamp: '09:42:08'
            }
          ];
          setConversation(dynamicConversation);
        }
      } catch (err) {
        // Fall back to default mock conversation
      }
    };
    fetchLatest();
    return () => controller.abort();
  }, []);

  const startCollaboration = () => {
    setIsRunning(true);
    setMessages([]);
    setCurrentStep(0);
    
    // Reset agent statuses
    setAgents(initialAgents.map(a => ({ ...a, status: 'idle', cognitiveLoad: 0 })));
  };

  useEffect(() => {
    if (!isRunning) return;

    if (currentStep < conversation.length) {
      const timeout = setTimeout(() => {
        const nextMsg = conversation[currentStep];
        setMessages(prev => [...prev, nextMsg]);

        // Update agent states dynamically
        setAgents(prevAgents => prevAgents.map(a => {
          if (a.id === nextMsg.agentId) {
            return { ...a, status: 'thinking', cognitiveLoad: 85 };
          }
          // Mark previous agent as completed
          const prevMsg = currentStep > 0 ? conversation[currentStep - 1] : null;
          if (prevMsg && a.id === prevMsg.agentId) {
            return { ...a, status: 'completed', cognitiveLoad: 0 };
          }
          return a;
        }));

        setCurrentStep(prev => prev + 1);
      }, 2500);

      return () => clearTimeout(timeout);
    } else {
      // Completed all steps
      setIsRunning(false);
      setAgents(prevAgents => prevAgents.map(a => ({ ...a, status: 'completed', cognitiveLoad: 0 })));
    }
  }, [isRunning, currentStep, conversation]);

  return (
    <div className="w-full h-full flex flex-col md:flex-row overflow-hidden bg-slate-50 dark:bg-[#05070a] font-sans">
      
      {/* Agents Listing Sidebar */}
      <div className="w-full md:w-80 border-r border-slate-200 dark:border-white/5 bg-white dark:bg-[#0a0c10] flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-bold tracking-tight">AI Agents</h2>
          </div>
          <button
            onClick={startCollaboration}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-bold shadow-lg shadow-primary/10 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 disabled:pointer-events-none"
          >
            {isRunning ? <Activity size={12} className="animate-spin" /> : <Play size={12} />}
            Simulate
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`p-3.5 rounded-2xl border transition-all duration-350 bg-white dark:bg-[#0a0c10] ${
                agent.status === 'thinking' 
                  ? 'border-primary shadow-md ring-1 ring-primary/10 bg-primary/[0.01]' 
                  : 'border-slate-200 dark:border-white/5'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${agent.avatarColor}`} />
                  <h3 className="text-xs font-bold tracking-tight text-slate-800 dark:text-slate-200">
                    {agent.name}
                  </h3>
                </div>
                <span className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                  agent.status === 'completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
                  agent.status === 'thinking' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse' :
                  'bg-slate-100 text-slate-400 dark:bg-white/5 border-transparent'
                }`}>
                  {agent.status}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-2 leading-relaxed">
                {agent.role}
              </p>

              {agent.cognitiveLoad > 0 && (
                <div className="mt-3 space-y-1">
                  <div className="flex items-center justify-between text-[9px] font-mono text-slate-400">
                    <span>WORKLOAD:</span>
                    <span>{agent.cognitiveLoad}%</span>
                  </div>
                  <div className="h-1 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-primary"
                      animate={{ width: `${agent.cognitiveLoad}%` }}
                      transition={{ duration: 1.5, repeat: Infinity, repeatType: 'reverse' }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agent Dialogue Screen */}
      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-[#06080c]">
        {/* Header */}
        <div className="h-16 px-6 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/50 dark:bg-black/20 backdrop-blur-md sticky top-0 z-10">
          <div>
            <h2 className="text-base font-bold tracking-tight">AI Discussion</h2>
            <p className="text-xs text-slate-400 dark:text-slate-500">Watch the AI agents discuss and build your prompt.</p>
          </div>
          {messages.length > 0 && (
            <button 
              onClick={() => { setMessages([]); setAgents(initialAgents); }}
              className="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
            >
              <RotateCcw size={14} />
            </button>
          )}
        </div>

        {/* Message Thread */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          <AnimatePresence>
            {messages.length === 0 ? (
              <motion.div 
                key="empty-state"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex flex-col items-center justify-center text-center text-slate-400"
              >
                <Bot size={36} className="mb-3 text-slate-300 animate-bounce" />
                <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300">AI Agents Offline</h3>
                <p className="text-xs text-slate-400 max-w-sm mt-1 leading-relaxed">
                  Click the **Simulate** button to watch how the AI agents work together to refine your prompt.
                </p>
              </motion.div>
            ) : (
              messages.map((msg) => {
                const agent = agents.find(a => a.name === msg.agentName);
                
                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    className={`flex items-start gap-4 p-5 rounded-2xl border ${
                      msg.isImportant 
                        ? 'bg-amber-500/5 border-amber-500/20 text-amber-900 dark:text-amber-100' 
                        : 'bg-slate-50/50 dark:bg-[#0a0c10]/40 border-slate-200/50 dark:border-white/5'
                    }`}
                  >
                    <div className={`p-2.5 rounded-xl flex-shrink-0 text-white ${agent?.avatarColor || 'bg-slate-500'}`}>
                      <Cpu size={16} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <div>
                          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{msg.agentName}</span>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 ml-2 font-mono uppercase">
                            ({msg.role})
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400 dark:text-slate-500">
                          {msg.timestamp}
                        </span>
                      </div>
                      
                      {msg.isImportant && (
                        <div className="flex items-center gap-1.5 mt-2 text-xs font-bold text-amber-500">
                          <ShieldAlert size={12} />
                          <span>CRITIC WARNING</span>
                        </div>
                      )}

                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed font-sans whitespace-pre-wrap">
                        {msg.message}
                      </p>
                    </div>
                  </motion.div>
                );
              })
            )}
          </AnimatePresence>
        </div>
      </div>

    </div>
  );
}
