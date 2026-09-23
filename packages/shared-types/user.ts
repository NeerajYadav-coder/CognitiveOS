// ============================================================
// User Domain Types — CognitiveOS
// ============================================================

import type { CognitiveMode, GrowthMetrics } from "./cognitive";

export interface User {
  id: string;
  email: string;
  displayName: string;
  avatarUrl?: string;
  createdAt: string;
  updatedAt: string;
  cognitiveProfile: CognitiveProfile;
  preferences: UserPreferencesStore;
  subscription: SubscriptionTier;
}

export interface CognitiveProfile {
  userId: string;
  dominantMode: CognitiveMode;
  secondaryMode?: CognitiveMode;
  thinkingPersona: ThinkingPersona;
  domainExpertise: DomainExpertise[];
  cognitiveStyle: CognitiveStyle;
  growthMetrics: GrowthMetrics;
  lastUpdated: string;
}

export type ThinkingPersona =
  | "analyst"       // Logical, data-driven, structured
  | "explorer"      // Curious, wide-ranging, associative
  | "creator"       // Generative, imaginative, novel
  | "synthesizer"   // Integrative, cross-domain, holistic
  | "critic"        // Evaluative, questioning, rigorous
  | "executor"      // Task-focused, practical, sequential
  | "undefined";

export interface DomainExpertise {
  domain: string;
  level: "novice" | "intermediate" | "advanced" | "expert";
  sessionCount: number;
}

export interface CognitiveStyle {
  verbosityPreference: "concise" | "balanced" | "detailed";
  structurePreference: "free-form" | "guided" | "strict";
  feedbackFrequency: "minimal" | "moderate" | "frequent";
  learningOrientation: "breadth" | "depth" | "balanced";
}

export interface UserPreferencesStore {
  theme: "light" | "dark" | "system";
  language: string;
  defaultCognitiveMode?: CognitiveMode;
  autoStructure: boolean;
  showPipelineDetails: boolean;
  enableReflection: boolean;
  platformIntegrations: PlatformIntegration[];
}

export interface PlatformIntegration {
  platform: string;
  enabled: boolean;
  autoInject: boolean;
  customInstructions?: string;
}

export type SubscriptionTier = "free" | "pro" | "team" | "enterprise";

export interface UserSession {
  sessionId: string;
  userId: string;
  startedAt: string;
  endedAt?: string;
  interactionCount: number;
  averageQualityScore: number;
  platform: string;
}
