import { ChatGPTAdapter } from "./chatgpt";
import { ClaudeAdapter } from "./claude";
import { GeminiAdapter } from "./gemini";
import type { SiteAdapter } from "./base";

export * from "./base";
export * from "./chatgpt";
export * from "./claude";
export * from "./gemini";

export function getActiveAdapter(): SiteAdapter | null {
  if (typeof window === "undefined") return null;
  const host = window.location.hostname;
  if (host.includes("chatgpt.com") || host.includes("openai.com")) {
    return new ChatGPTAdapter();
  }
  if (host.includes("claude.ai")) {
    return new ClaudeAdapter();
  }
  if (host.includes("gemini.google.com")) {
    return new GeminiAdapter();
  }
  return null;
}
