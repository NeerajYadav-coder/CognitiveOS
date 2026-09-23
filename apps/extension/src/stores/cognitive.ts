import { create } from "zustand";

interface CognitiveAnalysis {
  intent: string;
  ambiguityScore: number;
  mode: string;
  suggestions: string[];
  vocabulary: string[];
  structuredPrompt: string;
  memoryContext: string[];
}

interface CognitiveStore {
  isActive: boolean;
  rawPrompt: string;
  analysis: CognitiveAnalysis | null;
  isAnalyzing: boolean;
  
  setActive: (active: boolean) => void;
  updatePrompt: (text: string) => void;
  setAnalysis: (analysis: CognitiveAnalysis) => void;
  setAnalyzing: (loading: boolean) => void;
  reset: () => void;
}

export const useCognitiveStore = create<CognitiveStore>((set) => ({
  isActive: true,
  rawPrompt: "",
  analysis: null,
  isAnalyzing: false,

  setActive: (active) => set({ isActive: active }),
  updatePrompt: (text) => set({ rawPrompt: text }),
  setAnalysis: (analysis) => set({ analysis, isAnalyzing: false }),
  setAnalyzing: (loading) => set({ isAnalyzing: loading }),
  reset: () => set({ rawPrompt: "", analysis: null, isAnalyzing: false }),
}));
