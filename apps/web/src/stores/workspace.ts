import { create } from "zustand";

export type WorkspaceModule = 
  | "graph" 
  | "research" 
  | "timeline" 
  | "agents" 
  | "memory" 
  | "orchestration" 
  | "reflection"
  | "strategic"
  | "settings";

interface WorkspaceState {
  activeModule: WorkspaceModule;
  isSidebarOpen: boolean;
  activeSessionId: string | null;
  activeConceptId: string | null;
  
  // UI State
  theme: "light" | "dark" | "cognitive";
  
  setModule: (module: WorkspaceModule) => void;
  toggleSidebar: () => void;
  setSession: (id: string | null) => void;
  setConcept: (id: string | null) => void;
  setTheme: (theme: "light" | "dark" | "cognitive") => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeModule: "graph",
  isSidebarOpen: true,
  activeSessionId: null,
  activeConceptId: null,
  theme: "cognitive",

  setModule: (module) => set({ activeModule: module }),
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSession: (id) => set({ activeSessionId: id }),
  setConcept: (id) => set({ activeConceptId: id }),
  setTheme: (theme) => set({ theme }),
}));
