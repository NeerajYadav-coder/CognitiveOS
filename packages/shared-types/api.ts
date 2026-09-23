// ============================================================
// API Contract Types — CognitiveOS
// ============================================================

import type {
  CognitiveMode,
  AmbiguityLevel,
  SynthesizedPrompt,
  ReflectionInsight,
  IntentExtractionResult,
  AmbiguityAnalysis,
  VocabularyExpansion,
  ThoughtStructure,
  CognitiveModeResult,
} from "./cognitive";

// ---- Request / Response envelopes -------------------------

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta: ApiMeta;
  error?: ApiError;
}

export interface ApiMeta {
  requestId: string;
  processingTimeMs: number;
  pipelineVersion: string;
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

// ---- Cognitive Pipeline Endpoint --------------------------

export interface ProcessCognitiveRequest {
  rawInput: string;
  sessionId?: string;
  userId?: string;
  platformContext?: PlatformContext;
  userPreferences?: UserPreferences;
}

export interface PlatformContext {
  url?: string;
  platform?: string; // "chatgpt" | "claude" | "gemini" | "web"
  existingConversation?: string;
}

export interface UserPreferences {
  preferredMode?: CognitiveMode;
  verbosity?: "concise" | "balanced" | "detailed";
  domainFocus?: string[];
  skipAmbiguityCheck?: boolean;
}

export interface CognitivePipelineResponse {
  sessionId: string;
  stages: PipelineStageResult[];
  finalOutput: SynthesizedPrompt;
  reflection?: Partial<ReflectionInsight>;
}

export interface PipelineStageResult {
  stage: PipelineStage;
  status: "completed" | "skipped" | "failed";
  processingTimeMs: number;
  data:
    | IntentExtractionResult
    | CognitiveModeResult
    | AmbiguityAnalysis
    | VocabularyExpansion
    | ThoughtStructure
    | SynthesizedPrompt
    | null;
}

export type PipelineStage =
  | "intent-extraction"
  | "mode-detection"
  | "ambiguity-analysis"
  | "vocabulary-expansion"
  | "thought-structuring"
  | "prompt-synthesis"
  | "reflection";

// ---- Session & Feedback -----------------------------------

export interface SessionCreateRequest {
  userId: string;
  metadata?: Record<string, unknown>;
}

export interface SessionResponse {
  sessionId: string;
  userId: string;
  createdAt: string;
  expiresAt: string;
}

export interface FeedbackRequest {
  sessionId: string;
  rating: 1 | 2 | 3 | 4 | 5;
  usedFinalPrompt: boolean;
  comment?: string;
  suggestedImprovement?: string;
}

// ---- Clarification Flow -----------------------------------

export interface ClarificationRequest {
  sessionId: string;
  questionId: string;
  answer: string;
}

export interface ClarificationResponse {
  resolved: boolean;
  updatedPipeline?: Partial<CognitivePipelineResponse>;
  nextQuestion?: string;
}
