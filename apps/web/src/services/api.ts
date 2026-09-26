/**
 * CognitiveOS Central Web API Client
 * Normalizes all communication with the FastAPI cognitive infrastructure.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Interaction {
  id: string;
  session_id: string;
  raw_input: string;
  normalized_input?: string;
  intent_output?: {
    primary_intent: string;
    domain: string;
    depth_level: string;
    confidence: number;
    secondary_intents?: string[];
  };
  cognitive_mode?: {
    primary_mode: string;
    confidence: number;
    modes?: Array<{ name: string; score: number }>;
  };
  ambiguity_score: number;
  orchestration_trace?: any;
  created_at: string;
}

export interface UserProfileResponse {
  user_id: string;
  email: string;
  profile_metadata: {
    profession?: string;
    domain_expertise?: Array<{ domain: string; level: string }>;
  };
  cognition_preferences: {
    intellectual_level?: string;
    cognitive_style?: {
      verbosity?: string;
      reasoning_preference?: string;
    };
  };
}

export interface ReflectionAnalyticsResponse {
  total_interactions: number;
  average_ambiguity: number;
  dominant_mode: string;
  clarity_score: number;
  insights: Array<{
    title: string;
    category: "clarity" | "efficiency" | "scope";
    text: string;
    impact: "high" | "medium" | "low";
  }>;
}

export interface ProfileUpdateRequest {
  profession?: string;
  intellectual_level?: string;
  cognitive_style?: {
    verbosity?: string;
    reasoning_preference?: string;
  };
  domain_expertise?: Array<{ domain: string; level: string }>;
}

export const api = {
  baseUrl: API_BASE_URL,

  async getInteractions(signal?: AbortSignal): Promise<Interaction[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/interactions`, { signal });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (err: any) {
      if (err.name === "AbortError") return [];
      console.warn("[CognitiveAPI] Failed to fetch interactions:", err.message);
      return [];
    }
  },

  async getUserProfile(signal?: AbortSignal): Promise<UserProfileResponse | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/user/profile`, { signal });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (err: any) {
      if (err.name === "AbortError") return null;
      console.warn("[CognitiveAPI] Failed to fetch user profile:", err.message);
      return null;
    }
  },

  async updateUserProfile(payload: ProfileUpdateRequest): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE_URL}/user/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      return res.ok;
    } catch (err: any) {
      console.error("[CognitiveAPI] Failed to update user profile:", err.message);
      return false;
    }
  },

  async getReflectionAnalytics(signal?: AbortSignal): Promise<ReflectionAnalyticsResponse | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/reflection/analytics`, { signal });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (err: any) {
      if (err.name === "AbortError") return null;
      console.warn("[CognitiveAPI] Failed to fetch reflection analytics:", err.message);
      return null;
    }
  },

  async processThought(rawInput: string, platformContext: Record<string, any> = {}): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        raw_input: rawInput,
        platform_context: platformContext,
      }),
    });
    if (!res.ok) throw new Error(`Pipeline execution failed: ${res.status}`);
    return await res.json();
  },

  async processSpokenThought(rawSpeech: string, signal?: AbortSignal): Promise<SpokenThoughtAnalysis | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/cognitive/voice-stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_speech: rawSpeech }),
        signal,
      });
      if (!res.ok) throw new Error(`Voice processing error: ${res.status}`);
      return await res.json();
    } catch (err: any) {
      if (err.name === "AbortError") return null;
      console.warn("[CognitiveAPI] Spoken thought processing failed:", err.message);
      return null;
    }
  },

  async synthesizeGraph(
    nodes: Array<{ id: string; label: string; type?: string }>,
    edges: Array<{ source: string; target: string; relation?: string }>,
    goal?: string,
    signal?: AbortSignal
  ): Promise<GraphSynthesisResponse | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/cognitive/graph/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nodes, edges, goal }),
        signal,
      });
      if (!res.ok) throw new Error(`Graph synthesis error: ${res.status}`);
      return await res.json();
    } catch (err: any) {
      if (err.name === "AbortError") return null;
      console.warn("[CognitiveAPI] Graph synthesis failed:", err.message);
      return null;
    }
  },

  async runDialecticalDebate(
    topic: string,
    strategy: string = "dialectical_debate",
    depth: string = "deep",
    signal?: AbortSignal
  ): Promise<DialecticalDebateResponse | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/cognitive/dialectical-debate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, strategy, depth }),
        signal,
      });
      if (!res.ok) throw new Error(`Dialectical debate error: ${res.status}`);
      return await res.json();
    } catch (err: any) {
      if (err.name === "AbortError") return null;
      console.warn("[CognitiveAPI] Dialectical debate failed:", err.message);
      return null;
    }
  },

  async getEvolutionDriftAnalysis(signal?: AbortSignal): Promise<CognitiveDriftReport | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/cognitive/evolution/drift-analysis`, { signal });
      if (!res.ok) throw new Error(`Drift analysis error: ${res.status}`);
      return await res.json();
    } catch (err: any) {
      if (err.name === "AbortError") return null;
      console.warn("[CognitiveAPI] Drift analysis failed:", err.message);
      return null;
    }
  },
};

export interface SpokenThoughtAnalysis {
  cleaned_transcript: string;
  filler_words_removed: string[];
  implicit_intent: string;
  latent_hypotheses: string[];
  spoken_ambiguity_score: number;
  focal_question: string;
  suggested_prompt: string;
}

export interface GraphSynthesisResponse {
  title: string;
  core_theme: string;
  conceptual_pathways: string[];
  synthesized_prompt: string;
  recommended_framework: string;
}

export interface DebateTurn {
  speaker: string;
  role: "thesis" | "antithesis" | "pre_mortem" | "synthesis" | string;
  argument: string;
  key_assumptions: string[];
  confidence: number;
}

export interface PreMortemFailureMode {
  failure_scenario: string;
  probability: "high" | "medium" | "low" | string;
  mitigation_strategy: string;
}

export interface DialecticalDebateResponse {
  topic: string;
  strategy: string;
  thesis: string;
  antithesis: string;
  pre_mortem_failure_modes: PreMortemFailureMode[];
  debate_rounds: DebateTurn[];
  dialectical_synthesis: string;
  blindspots_exposed: string[];
  battle_tested_prompt: string;
  cognitive_rigor_score: number;
}

export interface CognitiveDriftReport {
  total_interactions_analyzed: number;
  semantic_drift_score: number;
  dominant_thought_patterns: string[];
  stagnation_risk: "low" | "moderate" | "elevated" | string;
  evolutionary_recommendations: string[];
  next_cognitive_frontier: string;
}


