import type { PlasmoCSConfig } from "plasmo"
import { useEffect } from "react"
import { ChatGPTAdapter } from "~adapters/chatgpt"
import { useCognitiveStore } from "~stores/cognitive"
import { CognitiveOverlay } from "~overlay/CognitiveOverlay"
import cssText from "data-text:./style.css"

export const config: PlasmoCSConfig = {
  matches: [
    "https://chatgpt.com/*",
    "https://chat.openai.com/*",
    "https://openai.com/*",
    "https://claude.ai/*",
    "https://gemini.google.com/*"
  ],
  all_frames: true
}

export const getStyle = () => {
  const style = document.createElement("style")
  style.textContent = cssText
  return style
}

const CognitiveContentScript = () => {
  const { rawPrompt, updatePrompt, isAnalyzing, setAnalysis, setAnalyzing } = useCognitiveStore()

  useEffect(() => {
    const interval = setInterval(() => {
      const adapter = new ChatGPTAdapter()
      const input = adapter.getPromptInput()
      if (adapter.isMatch() && input) {
        console.log("[CognitiveOS] Input Box Linked");
        adapter.onPromptChange((text) => updatePrompt(text))
        clearInterval(interval)
      }
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const triggerAnalysis = async () => {
      if (isAnalyzing && rawPrompt) {
        console.log("[CognitiveOS] 📡 PINGING BRAIN...");
        try {
          chrome.runtime.sendMessage({
            type: "PROCESS_THOUGHT",
            payload: { raw_input: rawPrompt, session_id: "dev-session" }
          }, (response) => {
            if (chrome.runtime.lastError) {
              const msg = chrome.runtime.lastError.message;
              if (msg?.includes("context invalidated")) {
                alert("CognitiveOS updated! Please refresh the page.");
                setAnalyzing(false);
                return;
              }
              console.error("[CognitiveOS] ❌ Bridge Error:", msg);
              setAnalyzing(false);
              return;
            }

            if (response?.success) {
              console.log("[CognitiveOS] ✅ BRAIN RESPONDED!");
              const { data } = response;
              setAnalysis({
                intent: data.structured_thought?.intent?.primary_intent || "Analysis Complete",
                ambiguityScore: data.structured_thought?.ambiguity?.ambiguity_score || 0,
                mode: data.structured_thought?.mode?.primary_mode || "exploratory",
                suggestions: data.structured_thought?.vocabulary?.adjacent_concepts || [],
                vocabulary: data.structured_thought?.vocabulary?.recommended_terms || [],
                structuredPrompt: data.synthesized_prompt || rawPrompt,
                memoryContext: []
              });
            } else {
              console.error("[CognitiveOS] ❌ Brain failed:", response?.error);
              setAnalyzing(false);
            }
          });
        } catch (e) {
          console.error("[CognitiveOS] Runtime exception:", e);
          setAnalyzing(false);
        }
      }
    }
    triggerAnalysis();
  }, [isAnalyzing])

  return (
    <div id="cognitive-os-root">
      <CognitiveOverlay />
    </div>
  )
}

export default CognitiveContentScript
