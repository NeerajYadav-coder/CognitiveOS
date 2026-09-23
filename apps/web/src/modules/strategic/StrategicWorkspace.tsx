"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BrainCircuit, 
  Plus, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  TrendingUp, 
  Sliders, 
  Calendar,
  Layers,
  Sparkles
} from 'lucide-react';
import { api } from '@/services/api';

interface StrategicMilestone {
  id: string;
  title: string;
  quarter: string;
  progress: number;
  status: 'planning' | 'in-progress' | 'completed';
  tasksCount: number;
}

interface StrategicTask {
  id: string;
  milestoneId: string;
  title: string;
  priority: 'high' | 'medium' | 'low';
  dueDate: string;
  done: boolean;
}

const initialMilestones: StrategicMilestone[] = [
  {
    id: 'mile-1',
    title: 'Self-Organizing Pipeline Infrastructure',
    quarter: 'Q2 2026',
    progress: 80,
    status: 'in-progress',
    tasksCount: 4
  },
  {
    id: 'mile-2',
    title: 'Stigmergic Swarm Agent Integration',
    quarter: 'Q3 2026',
    progress: 35,
    status: 'in-progress',
    tasksCount: 3
  },
  {
    id: 'mile-3',
    title: 'Local Embedding Vector Evaporation',
    quarter: 'Q4 2026',
    progress: 0,
    status: 'planning',
    tasksCount: 2
  }
];

const initialTasks: StrategicTask[] = [
  { id: 'task-1', milestoneId: 'mile-1', title: 'Verify FastAPI Uvicorn local endpoint connectivity', priority: 'high', dueDate: 'May 25, 2026', done: true },
  { id: 'task-2', milestoneId: 'mile-1', title: 'Connect Next.js telemetry polling to postgres database', priority: 'high', dueDate: 'June 02, 2026', done: true },
  { id: 'task-3', milestoneId: 'mile-1', title: 'Implement dynamic HNSW indexing in pgvector schema', priority: 'medium', dueDate: 'June 15, 2026', done: false },
  { id: 'task-4', milestoneId: 'mile-1', title: 'Deploy core API gateway onto development Kubernetes cluster', priority: 'low', dueDate: 'June 30, 2026', done: false },
  
  { id: 'task-5', milestoneId: 'mile-2', title: 'Build pheromone decay models inside search crawler', priority: 'high', dueDate: 'July 10, 2026', done: false },
  { id: 'task-6', milestoneId: 'mile-2', title: 'Refactor client adapter overlay UI script for Gemini compatibility', priority: 'medium', dueDate: 'July 25, 2026', done: false },
  
  { id: 'task-7', milestoneId: 'mile-3', title: 'Verify vector index decay benchmarks', priority: 'medium', dueDate: 'October 15, 2026', done: false }
];

export default function StrategicWorkspace() {
  const [milestones, setMilestones] = useState<StrategicMilestone[]>(initialMilestones);
  const [tasks, setTasks] = useState<StrategicTask[]>(initialTasks);
  const [selectedMilestoneId, setSelectedMilestoneId] = useState<string>(initialMilestones[0].id);

  React.useEffect(() => {
    const controller = new AbortController();
    const fetchLatest = async () => {
      try {
        const data = await api.getInteractions(controller.signal);
        if (data && data.length > 0) {
          const latest = data[0];
          const primaryIntent = latest.intent_output?.primary_intent || "Educational Research";
          
          const userTask: StrategicTask = {
            id: 'user-task',
            milestoneId: 'mile-1',
            title: `Deploy synthesis loop: "${latest.raw_input.substring(0, 55)}..." (Intent: ${primaryIntent})`,
            priority: latest.ambiguity_score > 0.5 ? 'high' : 'medium',
            dueDate: 'Today',
            done: false
          };
          
          setTasks(prev => {
            const filtered = prev.filter(t => t.id !== 'user-task');
            return [userTask, ...filtered];
          });
        }
      } catch (err) {
        // Fall back to defaults
      }
    };
    fetchLatest();
    return () => controller.abort();
  }, []);

  // Form states
  const [showAddTask, setShowAddTask] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<StrategicTask['priority']>('medium');
  const [newTaskDueDate, setNewTaskDueDate] = useState('');

  const activeMilestone = milestones.find(m => m.id === selectedMilestoneId) || milestones[0];
  const activeTasks = tasks.filter(t => t.milestoneId === selectedMilestoneId);

  const toggleTask = (taskId: string) => {
    const updatedTasks = tasks.map(t => t.id === taskId ? { ...t, done: !t.done } : t);
    setTasks(updatedTasks);
    
    // Recalculate milestone progress
    const activeTasksUpdated = updatedTasks.filter(t => t.milestoneId === selectedMilestoneId);
    const completedCount = activeTasksUpdated.filter(t => t.done).length;
    const progress = activeTasksUpdated.length > 0 
      ? Math.round((completedCount / activeTasksUpdated.length) * 100) 
      : 0;

    setMilestones(milestones.map(m => m.id === selectedMilestoneId 
      ? { ...m, progress, status: progress === 100 ? 'completed' : progress > 0 ? 'in-progress' : 'planning' } 
      : m
    ));
  };

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    const newTask: StrategicTask = {
      id: `task-${Date.now()}`,
      milestoneId: selectedMilestoneId,
      title: newTaskTitle,
      priority: newTaskPriority,
      dueDate: newTaskDueDate || 'No Due Date',
      done: false
    };

    const updatedTasks = [...tasks, newTask];
    setTasks(updatedTasks);
    
    // Recalculate milestone progress
    const activeTasksUpdated = updatedTasks.filter(t => t.milestoneId === selectedMilestoneId);
    const completedCount = activeTasksUpdated.filter(t => t.done).length;
    const progress = Math.round((completedCount / activeTasksUpdated.length) * 100);

    setMilestones(milestones.map(m => m.id === selectedMilestoneId 
      ? { 
          ...m, 
          progress, 
          tasksCount: activeTasksUpdated.length,
          status: progress === 100 ? 'completed' : progress > 0 ? 'in-progress' : 'planning' 
        } 
      : m
    ));

    // Reset form
    setNewTaskTitle('');
    setNewTaskPriority('medium');
    setNewTaskDueDate('');
    setShowAddTask(false);
  };

  const getPriorityColor = (p: StrategicTask['priority']) => {
    switch (p) {
      case 'high': return 'text-rose-500 bg-rose-500/10 border-rose-500/20';
      case 'medium': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'low': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
    }
  };

  const getStatusBadge = (status: StrategicMilestone['status']) => {
    switch (status) {
      case 'completed': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'in-progress': return 'bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse';
      case 'planning': return 'bg-slate-100 dark:bg-white/5 text-slate-400 border-transparent';
    }
  };

  return (
    <div className="w-full h-full flex flex-col md:flex-row overflow-hidden bg-slate-50 dark:bg-[#05070a] font-sans">
      
      {/* Strategic Milestones Sidebar */}
      <div className="w-full md:w-80 border-r border-slate-200 dark:border-white/5 bg-white dark:bg-[#0a0c10] flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-slate-200 dark:border-white/5">
          <div className="flex items-center gap-2 mb-1">
            <BrainCircuit className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-bold tracking-tight">Strategic Roadmap</h2>
          </div>
          <p className="text-xs text-slate-400 dark:text-slate-500">Long-term objectives and research targets.</p>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          {milestones.map((item) => {
            const isSelected = item.id === selectedMilestoneId;
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  setSelectedMilestoneId(item.id);
                  setShowAddTask(false);
                }}
                className={`w-full text-left p-3.5 rounded-2xl border transition-all duration-200 ${
                  isSelected 
                    ? 'bg-primary/5 border-primary/20 text-primary shadow-sm'
                    : 'border-transparent text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">{item.quarter}</span>
                  <span className={`text-[9px] px-2 py-0.5 rounded-full border font-bold uppercase tracking-wide ${getStatusBadge(item.status)}`}>
                    {item.status}
                  </span>
                </div>
                <h3 className="text-xs font-bold leading-snug line-clamp-2">{item.title}</h3>
                
                <div className="mt-4 space-y-1">
                  <div className="flex justify-between text-[9px] text-slate-400 font-mono">
                    <span>PROGRESS:</span>
                    <span>{item.progress}%</span>
                  </div>
                  <div className="h-1 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-primary"
                      animate={{ width: `${item.progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Task List Board */}
      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-[#06080c]">
        {/* Header */}
        <div className="h-16 px-6 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/50 dark:bg-black/20 backdrop-blur-md sticky top-0 z-10">
          <div>
            <h2 className="text-base font-bold tracking-tight">Milestone Action Items</h2>
            <p className="text-xs text-slate-400 dark:text-slate-500">Deconstructed requirements for {activeMilestone.title}.</p>
          </div>
          <button
            onClick={() => setShowAddTask(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-bold shadow-lg shadow-primary/10 hover:scale-[1.02] active:scale-95 transition-all"
          >
            <Plus size={14} />
            Add Task
          </button>
        </div>

        {/* Tasks View */}
        <div className="flex-1 p-6 overflow-y-auto">
          <AnimatePresence mode="wait">
            {showAddTask ? (
              <motion.form
                key="add-task-form"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                onSubmit={handleAddTask}
                className="max-w-xl mx-auto p-6 border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-[#0a0c10] rounded-2xl space-y-4 shadow-sm"
              >
                <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-white/5 pb-2">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500">Add Task to Milestone</h3>
                  <button 
                    type="button" 
                    onClick={() => setShowAddTask(false)}
                    className="text-xs text-slate-400 hover:text-slate-600"
                  >
                    Cancel
                  </button>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-400 uppercase font-sans">Task Name</label>
                  <input 
                    type="text"
                    required
                    placeholder="e.g. Set up local Docker cluster for Redis caching"
                    value={newTaskTitle}
                    onChange={(e) => setNewTaskTitle(e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary focus:border-primary outline-none text-slate-800 dark:text-slate-200"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase">Priority</label>
                    <select
                      value={newTaskPriority}
                      onChange={(e) => setNewTaskPriority(e.target.value as any)}
                      className="w-full px-3 py-2 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary focus:border-primary outline-none text-slate-800 dark:text-slate-200"
                    >
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase">Due Date</label>
                    <input 
                      type="text"
                      placeholder="e.g. June 15, 2026"
                      value={newTaskDueDate}
                      onChange={(e) => setNewTaskDueDate(e.target.value)}
                      className="w-full px-3 py-2 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs focus:ring-1 focus:ring-primary focus:border-primary outline-none text-slate-800 dark:text-slate-200"
                    />
                  </div>
                </div>

                <button 
                  type="submit"
                  className="w-full py-2.5 bg-primary hover:bg-primary-dark text-white rounded-xl text-xs font-bold shadow-lg shadow-primary/10 active:scale-[0.98] transition-all flex items-center justify-center gap-1.5"
                >
                  <Sparkles size={14} />
                  Add Milestone Task
                </button>
              </motion.form>
            ) : (
              <motion.div 
                key="task-list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="max-w-xl mx-auto space-y-4"
              >
                {activeTasks.length === 0 ? (
                  <div className="text-center py-12 text-slate-400 flex flex-col items-center justify-center">
                    <AlertCircle size={24} className="mb-2 text-slate-300" />
                    <p className="text-xs">No tasks added to this milestone yet.</p>
                  </div>
                ) : (
                  activeTasks.map((task) => (
                    <motion.div
                      key={task.id}
                      onClick={() => toggleTask(task.id)}
                      className={`p-4 rounded-2xl border transition-all duration-300 flex items-start gap-4 cursor-pointer bg-white dark:bg-[#0a0c10] hover:shadow-sm ${
                        task.done 
                          ? 'border-slate-200 dark:border-white/5 opacity-65 bg-slate-50/20' 
                          : 'border-slate-200 dark:border-white/5 hover:border-slate-300 dark:hover:border-white/10'
                      }`}
                    >
                      <button 
                        className={`mt-0.5 rounded-full p-0.5 border transition-all ${
                          task.done 
                            ? 'border-emerald-500 bg-emerald-500 text-white' 
                            : 'border-slate-300 dark:border-slate-700 hover:border-emerald-500 text-transparent'
                        }`}
                      >
                        <CheckCircle2 size={14} className="stroke-[3px]" />
                      </button>

                      <div className="flex-1 min-w-0">
                        <h4 className={`text-xs font-bold text-slate-800 dark:text-slate-200 leading-snug ${task.done ? 'line-through' : ''}`}>
                          {task.title}
                        </h4>
                        
                        <div className="flex items-center gap-3 mt-3">
                          <span className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${getPriorityColor(task.priority)}`}>
                            {task.priority} priority
                          </span>
                          <span className="text-[10px] text-slate-400 flex items-center gap-1">
                            <Calendar size={11} />
                            {task.dueDate}
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

    </div>
  );
}
