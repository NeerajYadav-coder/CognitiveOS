import axios from "axios";

const API_BASE_URL = process.env.PLASMO_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface CognitiveAnalysisResponse {
  intent: {
    primary_intent: string;
    domain: string;
    confidence: number;
  };
  mode: {
    primary_mode: string;
  };
  ambiguity: {
    ambiguity_score: number;
  };
  vocabulary: {
    recommended_terms: string[];
  };
  synthesis: {
    final_prompt: string;
  };
  evolution: {
    recommendations: any[];
  };
}

class CognitiveAPIClient {
  private client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      "Content-Type": "application/json",
    },
  });

  async analyzePrompt(rawInput: string, sessionId: string): Promise<CognitiveAnalysisResponse> {
    try {
      const response = await this.client.post("/process", {
        raw_input: rawInput,
        session_id: sessionId,
      });
      return response.data;
    } catch (error) {
      console.error("[CognitiveAPI] Error analyzing prompt:", error);
      throw error;
    }
  }

  async getSessionHistory(sessionId: string) {
    const response = await this.client.get(`/sessions/${sessionId}/history`);
    return response.data;
  }
}

export const cognitiveApi = new CognitiveAPIClient();
