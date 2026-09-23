// ============================================================
// Cognitive Pipeline — Core Types
// CognitiveOS shared-types package
// ============================================================

export type CognitiveMode =
  | "exploratory"       // Open-ended curiosity, divergent thinking
  | "analytical"        // Breaking down problems, structured reasoning
  | "creative"          // Generative, metaphorical, associative
  | "critical"          // Evaluating, debating, questioning assumptions
  | "synthetic"         // Integrating multiple ideas into unified understanding
  | "procedural"        // Step-by-step, task-oriented, sequential
  | "reflective"        // Introspective, metacognitive
  | "unknown";          // Could not determine

export type AmbiguityLevel = "none" | "low" | "medium" | "high" | "critical";
export type ConfidenceScore = number; // 0.0 – 1.0

export interface CognitiveModeResult {
  primary: CognitiveMode;
  secondary?: CognitiveMode;
  confidence: ConfidenceScore;
  reasoning: string;
  signals: string[];
}

export interface IntentSignal {
  type: "question" | "command" | "exploration" | "clarification" | "task" | "emotional";
  weight: ConfidenceScore;
}

export interface IntentExtractionResult {
  rawInput: string;
  coreIntent: string;
  subIntents: string[];
  signals: IntentSignal[];
  domainHints: string[];
  confidence: ConfidenceScore;
  ambiguityLevel: AmbiguityLevel;
}

export interface AmbiguityAnalysis {
  level: AmbiguityLevel;
  score: number; // 0–100
  ambiguousTerms: AmbiguousTerm[];
  missingContext: string[];
  clarifyingQuestions: string[];
  canProceedWithoutClarification: boolean;
}

export interface AmbiguousTerm {
  term: string;
  possibleMeanings: string[];
  recommendedInterpretation: string;
  confidence: ConfidenceScore;
}

export interface VocabularyExpansion {
  originalTerms: string[];
  expandedVocabulary: VocabEntry[];
  domainTerminology: string[];
  conceptualSynonyms: Record<string, string[]>;
  semanticClusters: SemanticCluster[];
}

export interface VocabEntry {
  term: string;
  synonyms: string[];
  relatedConcepts: string[];
  technicalVariants: string[];
  domain: string;
}

export interface SemanticCluster {
  centroid: string;
  members: string[];
  relevanceScore: ConfidenceScore;
}

export interface ThoughtStructure {
  framework: ThoughtFramework;
  sections: ThoughtSection[];
  logicalFlow: string[];
  keyConstraints: string[];
  outputFormat: string;
}

export type ThoughtFramework =
  | "chain-of-thought"
  | "problem-solution"
  | "compare-contrast"
  | "cause-effect"
  | "five-ws"
  | "socratic"
  | "first-principles"
  | "tree-of-thought"
  | "custom";

export interface ThoughtSection {
  id: string;
  title: string;
  content: string;
  weight: number; // Importance 0–1
}

export interface SynthesizedPrompt {
  finalPrompt: string;
  systemContext: string;
  userMessage: string;
  metadata: PromptMetadata;
  alternatives: string[];
}

export interface PromptMetadata {
  wordCount: number;
  estimatedTokens: number;
  cognitiveMode: CognitiveMode;
  framework: ThoughtFramework;
  ambiguityScore: number;
  qualityScore: number; // 0–100
}

export interface ReflectionInsight {
  userId: string;
  sessionId: string;
  patterns: CognitivePatternsAnalysis;
  growthMetrics: GrowthMetrics;
  recommendations: string[];
  curiosityIndex: number; // 0–100
}

export interface CognitivePatternsAnalysis {
  dominantModes: CognitiveMode[];
  frequentDomains: string[];
  averageAmbiguityLevel: AmbiguityLevel;
  thinkingEvolution: string;
  strengthAreas: string[];
  growthAreas: string[];
}

export interface GrowthMetrics {
  promptQualityTrend: "improving" | "stable" | "declining";
  conceptualDepthTrend: "deepening" | "stable" | "shallow";
  vocabularyGrowthRate: number;
  sessionCount: number;
  totalInteractions: number;
}
