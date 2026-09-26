import React, { useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Brain, Sparkles, AlertCircle, Zap, RotateCcw, X, Compass, Mic, MicOff, Check } from "lucide-react"
import { useCognitiveStore } from "~stores/cognitive"
import { getActiveAdapter } from "~adapters"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"


function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const CognitiveOverlay = () => {
  const { rawPrompt, analysis, isAnalyzing, setAnalyzing } = useCognitiveStore()
  const [isOpen, setIsOpen] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [anchorNotice, setAnchorNotice] = useState("")
  const recognitionRef = useRef<any>(null)

  const toggleVoice = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert("Web Speech API not supported in this browser.")
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
    } else {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.lang = "en-US"
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        const adapter = getActiveAdapter()
        if (adapter) {
          const input = adapter.getPromptInput()
          const current =
            input instanceof HTMLTextAreaElement ? input.value : input?.innerText || ""
          const updated = current ? `${current} ${transcript}` : transcript
          adapter.injectEnhancedPrompt(updated)
          useCognitiveStore.getState().updatePrompt(updated)
        }
        setIsListening(false)
      }
      recognition.onerror = () => setIsListening(false)
      recognition.onend = () => setIsListening(false)
      recognitionRef.current = recognition
      try {
        recognition.start()
        setIsListening(true)
      } catch (e) {
        setIsListening(false)
      }
    }
  }

  const handleAnchorContext = () => {
    const selection = window.getSelection()?.toString().trim()
    const pageTitle = document.title
    const contextSnippet = selection
      ? `\n[Context: "${selection.slice(0, 200)}"]`
      : `\n[Page: "${pageTitle}"]`

    const adapter = getActiveAdapter()
    if (adapter) {
      const input = adapter.getPromptInput()
      const current =
        input instanceof HTMLTextAreaElement ? input.value : input?.innerText || ""
      const updated = `${current}${contextSnippet}`
      adapter.injectEnhancedPrompt(updated)
      useCognitiveStore.getState().updatePrompt(updated)
      setAnchorNotice(selection ? "Selection anchored" : "Page title anchored")
      setTimeout(() => setAnchorNotice(""), 2500)
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-[99999] pointer-events-none font-sans">
      <AnimatePresence>
        {!isOpen ? (
          /* Sleek Minimal Pill Trigger Button */
          <motion.button
            key="pill-trigger"
            initial={{ opacity: 0, scale: 0.8, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 10 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(true)}
            className="pointer-events-auto flex items-center gap-2 px-3 py-2.5 rounded-full bg-slate-900/90 dark:bg-white text-white dark:text-slate-950 shadow-lg border border-white/10 dark:border-slate-200/50 backdrop-blur-md cursor-pointer"
          >
            <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-primary">
              <Brain size={14} className={cn(isAnalyzing && "animate-pulse")} />
            </div>
            <span className="text-[11px] font-bold tracking-tight pr-1">CognitiveOS</span>
            {isAnalyzing && (
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping mr-1" />
            )}
          </motion.button>
        ) : (
          /* Ultra-Compact Dashboard Card */
          <motion.div
            key="compact-card"
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="pointer-events-auto w-[290px] bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border border-slate-200/50 dark:border-white/10 shadow-2xl rounded-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="p-3.5 flex items-center justify-between border-b border-slate-200/50 dark:border-white/10 bg-gradient-to-r from-primary/5 to-transparent">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                  <Brain size={14} />
                </div>
                <div>
                  <h3 className="text-xs font-bold tracking-tight text-slate-800 dark:text-slate-100">
                    CognitiveOS
                  </h3>
                </div>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-slate-100 dark:hover:bg-white/5 rounded-md transition-colors text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X size={14} />
              </button>
            </div>

            {/* Content Area */}
            <div className="p-3.5 space-y-3">
              {!analysis && !isAnalyzing && (
                <div className="space-y-2">
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={toggleVoice}
                      title={isListening ? "Stop Voice Dictation" : "Dictate Prompt"}
                      className={cn(
                        "flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer",
                        isListening
                          ? "bg-red-500 text-white border-red-600 animate-pulse"
                          : "bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-white/10"
                      )}
                    >
                      {isListening ? <MicOff size={13} /> : <Mic size={13} className="text-primary" />}
                      <span>{isListening ? "Listening..." : "Dictate"}</span>
                    </button>
                    <button
                      onClick={handleAnchorContext}
                      title="Anchor highlighted text or active page title as context"
                      className="flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2 bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold border border-slate-200 dark:border-white/10 transition-all cursor-pointer"
                    >
                      <Compass size={13} className="text-primary" />
                      <span>Anchor</span>
                    </button>
                  </div>

                  {anchorNotice && (
                    <p className="text-[10px] text-emerald-500 text-center font-semibold">
                      ✓ {anchorNotice}
                    </p>
                  )}

                  <button 
                    onClick={() => {
                      const adapter = getActiveAdapter();
                      if (adapter) {
                        const currentText = adapter.getPromptInput()?.innerText || (adapter.getPromptInput() as HTMLTextAreaElement)?.value || "";
                        useCognitiveStore.getState().updatePrompt(currentText);
                      }
                      setAnalyzing(true);
                    }}
                    className="w-full group flex items-center justify-center gap-2 py-2 px-3 bg-primary text-white rounded-xl font-bold text-xs transition-all hover:opacity-90 active:scale-95 shadow-sm cursor-pointer"
                  >
                    <Sparkles size={12} className="group-hover:rotate-12 transition-transform" />
                    Analyze Draft Thought
                  </button>
                </div>
              )}

              {isAnalyzing && (
                <div className="py-6 flex flex-col items-center justify-center space-y-2">
                  <div className="relative">
                    <div className="w-8 h-8 rounded-full border-2 border-primary/20 border-t-primary animate-spin" />
                    <Zap size={12} className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-primary animate-pulse" />
                  </div>
                  <p className="text-[10px] font-bold text-slate-400 animate-pulse uppercase tracking-wider">
                    Profiling Thought...
                  </p>
                </div>
              )}

              {analysis && (
                <div className="space-y-3">
                  {/* Intent Brief */}
                  <div className="bg-slate-50 dark:bg-white/5 rounded-xl p-2.5 border border-slate-200/50 dark:border-white/5">
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wide block mb-0.5">Intent Insight</span>
                    <p className="text-xs text-slate-700 dark:text-slate-300 font-semibold leading-snug">
                      {analysis.intent}
                    </p>
                  </div>

                  {/* Ambiguity Alert */}
                  {analysis.ambiguityScore > 0.5 && (
                    <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-2.5 flex items-start gap-2">
                      <AlertCircle size={14} className="text-amber-500 flex-shrink-0 mt-0.5" />
                      <div>
                        <span className="text-[9px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wide block">Ambiguity Alert</span>
                        <p className="text-[11px] text-amber-700 dark:text-amber-300 leading-snug mt-0.5">
                          High entropy. Expand parameters for cleaner LLM output.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Suggestions Pill Grid */}
                  <div className="space-y-1">
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wide block">Vocabulary Expansion</span>
                    <div className="flex flex-wrap gap-1">
                      {analysis.vocabulary.slice(0, 3).map((term, i) => (
                        <div 
                          key={i}
                          className="px-2 py-1 bg-primary/5 border border-primary/10 rounded-lg text-[10px] font-medium text-slate-700 dark:text-slate-300"
                        >
                          {term}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="pt-1 flex items-center gap-1.5">
                    <button 
                      onClick={() => {
                        const adapter = getActiveAdapter();
                        if (adapter) {
                          adapter.injectEnhancedPrompt(analysis.structuredPrompt);
                        }
                        useCognitiveStore.getState().reset();
                      }}
                      className="flex-1 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-bold transition-all hover:opacity-90 active:scale-95 shadow-sm cursor-pointer"
                    >
                      Inject Optimized Prompt
                    </button>
                    <button 
                      onClick={() => useCognitiveStore.getState().reset()}
                      className="p-2 bg-slate-100 dark:bg-white/5 text-slate-500 rounded-xl hover:bg-slate-200 dark:hover:bg-white/10 transition-colors"
                    >
                      <RotateCcw size={12} />
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Footer Info */}
            <div className="px-3.5 py-2 bg-slate-50/50 dark:bg-white/5 border-t border-slate-200/50 dark:border-white/10 flex items-center justify-between text-[9px] text-slate-400 font-bold uppercase">
              <span>Secure Telemetry</span>
              <span>v1.1</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
