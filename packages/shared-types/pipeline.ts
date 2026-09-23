// ============================================================
// Pipeline Orchestration Types — CognitiveOS
// ============================================================

import type { PipelineStage } from "./api";

export interface PipelineConfig {
  version: string;
  stages: PipelineStageConfig[];
  timeoutMs: number;
  retryPolicy: RetryPolicy;
  fallbackBehavior: FallbackBehavior;
}

export interface PipelineStageConfig {
  stage: PipelineStage;
  enabled: boolean;
  timeoutMs: number;
  required: boolean;
  dependencies: PipelineStage[];
  llmConfig?: LLMConfig;
}

export interface LLMConfig {
  model: string;
  maxTokens: number;
  temperature: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  structuredOutput: boolean;
}

export interface RetryPolicy {
  maxAttempts: number;
  backoffMs: number;
  backoffMultiplier: number;
  retryableErrors: string[];
}

export type FallbackBehavior =
  | "fail-fast"       // Abort pipeline on any stage failure
  | "skip-stage"      // Skip failed stage and continue
  | "use-heuristics"  // Use rule-based fallback for failed stage
  | "partial-output"; // Return what was computed so far

export interface PipelineExecutionContext {
  requestId: string;
  sessionId: string;
  userId?: string;
  startTime: number;
  config: PipelineConfig;
  stageResults: Map<PipelineStage, StageExecutionResult>;
  sharedMemory: Record<string, unknown>;
}

export interface StageExecutionResult<T = unknown> {
  stage: PipelineStage;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  startTime: number;
  endTime?: number;
  output?: T;
  error?: {
    message: string;
    code: string;
    retryable: boolean;
  };
  tokenUsage?: TokenUsage;
}

export interface TokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  estimatedCostUsd: number;
}

export interface OrchestratorMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageProcessingTimeMs: number;
  stageMetrics: Record<PipelineStage, StageMetrics>;
  tokenUsageSummary: TokenUsage;
}

export interface StageMetrics {
  totalExecutions: number;
  successRate: number;
  averageTimeMs: number;
  skipRate: number;
  failureRate: number;
}
