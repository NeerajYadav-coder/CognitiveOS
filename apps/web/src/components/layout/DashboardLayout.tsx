"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  Network, 
  GitBranch, 
  History, 
  Users, 
  Database, 
  Activity, 
  Lightbulb, 
  Settings, 
  BrainCircuit, 
  PanelLeftClose, 
  PanelLeftOpen,
  Sun,
  Moon,
  Radio,
  Mic
} from "lucide-react";
import { useWorkspaceStore, WorkspaceModule } from "@/stores/workspace";
import { cn } from "@cognitive-os/ui";
import { VoiceThoughtInput } from "@/components/voice/VoiceThoughtInput";
import { AnimatePresence } from "framer-motion";


const navItems: { id: WorkspaceModule; label: string; icon: React.ElementType }[] = [
  { id: "graph", label: "Mind Map", icon: Network },
  { id: "research", label: "Thought Paths", icon: GitBranch },
  { id: "timeline", label: "Prompt History", icon: History },
  { id: "agents", label: "AI Agents", icon: Users },
  { id: "memory", label: "Memory Bank", icon: Database },
  { id: "orchestration", label: "Process Monitor", icon: Activity },
  { id: "reflection", label: "Thinking Insights", icon: Lightbulb },
  { id: "strategic", label: "Roadmap", icon: BrainCircuit },
];

export const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const { activeModule, setModule, isSidebarOpen, toggleSidebar } = useWorkspaceStore();
  const [isDark, setIsDark] = useState(true);
  const [showVoiceModal, setShowVoiceModal] = useState(false);


  // Initialize theme from system or class
  useEffect(() => {
    if (typeof window !== "undefined") {
      const isDarkActive = document.documentElement.classList.contains("dark") || 
        window.matchMedia("(prefers-color-scheme: dark)").matches;
      setIsDark(isDarkActive);
      if (isDarkActive) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  }, []);

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const activeItem = navItems.find(item => item.id === activeModule) || {
    id: activeModule,
    label: activeModule === "settings" ? "Settings" : "Workspace",
    icon: Settings
  };
  const ActiveIcon = activeItem.icon;

  return (
    <div className="flex h-screen w-full bg-slate-50 dark:bg-[#05070a] overflow-hidden font-sans text-slate-900 dark:text-slate-100 transition-colors duration-200">
      {/* Sidebar Navigation */}
      <motion.aside
        initial={false}
        animate={{ width: isSidebarOpen ? 260 : 76 }}
        transition={{ duration: 0.2, ease: "easeInOut" }}
        className="relative flex flex-col border-r border-slate-200 dark:border-white/5 bg-white dark:bg-[#0a0c10] shadow-sm z-50 flex-shrink-0"
      >
        {/* Header Branding */}
        <div className="h-16 flex items-center px-5 border-b border-slate-200 dark:border-white/5 justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary shadow-sm flex-shrink-0">
              <BrainCircuit size={18} />
            </div>
            {isSidebarOpen && (
              <motion.div 
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-1.5 overflow-hidden"
              >
                <span className="font-bold text-base tracking-tight truncate">CognitiveOS</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-mono font-bold">
                  v1.0
                </span>
              </motion.div>
            )}
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = activeModule === item.id;
            const Icon = item.icon;
            
            return (
              <button
                key={item.id}
                onClick={() => setModule(item.id)}
                title={!isSidebarOpen ? item.label : undefined}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150 group relative text-left",
                  isActive 
                    ? "bg-primary/10 text-primary font-semibold" 
                    : "text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-slate-200"
                )}
              >
                <Icon size={18} className={cn(isActive ? "text-primary" : "text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 flex-shrink-0")} />
                {isSidebarOpen && (
                  <span className="text-xs font-semibold tracking-tight truncate">
                    {item.label}
                  </span>
                )}
                {isActive && (
                  <motion.div 
                    layoutId="active-pill"
                    className="absolute left-0 w-1 h-5 bg-primary rounded-r-full" 
                  />
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-200 dark:border-white/5 space-y-1">
          <button 
            onClick={() => setModule("settings")}
            title={!isSidebarOpen ? "Settings" : undefined}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all duration-150 group relative text-left",
              activeModule === "settings" 
                ? "bg-primary/10 text-primary font-semibold" 
                : "text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-slate-200"
            )}
          >
            <Settings size={18} className={activeModule === "settings" ? "text-primary flex-shrink-0" : "text-slate-400 flex-shrink-0"} />
            {isSidebarOpen && <span className="text-xs font-semibold tracking-tight">Settings</span>}
          </button>

          <button 
            onClick={toggleSidebar}
            title={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
            className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl transition-all text-xs font-medium"
          >
            {isSidebarOpen ? <PanelLeftClose size={18} className="flex-shrink-0" /> : <PanelLeftOpen size={18} className="flex-shrink-0" />}
            {isSidebarOpen && <span>Collapse</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <main className="flex-1 relative flex flex-col min-w-0 overflow-hidden bg-slate-50 dark:bg-[#05070a]">
        {/* Top Navbar */}
        <header className="h-16 px-6 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-white/70 dark:bg-[#0a0c10]/70 backdrop-blur-md z-20 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              <ActiveIcon size={16} />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-slate-800 dark:text-slate-100">
                {activeItem.label}
              </h1>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">
                CognitiveOS &bull; Human-AI Operating Layer
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Live Pipeline Status Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
              <Radio size={12} className="animate-pulse text-emerald-500" />
              <span>Cognitive Pipeline Active</span>
            </div>

            {/* Voice Thought Ingestion Button */}
            <button
              onClick={() => setShowVoiceModal(true)}
              title="Record Spoken Thought"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 transition-colors text-xs font-semibold cursor-pointer"
            >
              <Mic size={15} />
              <span className="hidden md:inline">Voice Input</span>
            </button>

            {/* Dark / Light Mode Toggle */}
            <button
              onClick={toggleTheme}
              title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
              className="p-2 rounded-xl bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-white/10 transition-colors cursor-pointer"
            >
              {isDark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>
        </header>

        {/* Global Voice Modal */}
        <AnimatePresence>
          {showVoiceModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
              <VoiceThoughtInput onClose={() => setShowVoiceModal(false)} />
            </div>
          )}
        </AnimatePresence>

        {/* Work Area Viewport */}
        <div className="flex-1 overflow-auto relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
};
