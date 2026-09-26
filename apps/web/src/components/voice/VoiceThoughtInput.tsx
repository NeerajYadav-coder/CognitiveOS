"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Mic, 
  MicOff, 
  Sparkles, 
  Copy, 
  Check, 
  AlertCircle, 
  ArrowRight, 
  Volume2, 
  X,
  Brain,
  HelpCircle
} from "lucide-react";
import { api, SpokenThoughtAnalysis } from "@/services/api";

interface VoiceThoughtInputProps {
  onClose?: () => void;
  onApplyPrompt?: (prompt: string) => void;
}

export const VoiceThoughtInput: React.FC<VoiceThoughtInputProps> = ({ onClose, onApplyPrompt }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimText, setInterimText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<SpokenThoughtAnalysis | null>(null);
  const [copied, setCopied] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check Web Speech API support
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: any) => {
      let finalStr = "";
      let interimStr = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const item = event.results[i];
        if (item.isFinal) {
          finalStr += item[0].transcript + " ";
        } else {
          interimStr += item[0].transcript;
        }
      }

      if (finalStr) {
        setTranscript((prev) => prev + finalStr);
      }
      setInterimText(interimStr);
    };

    recognition.onerror = (err: any) => {
      console.warn("[VoiceThoughtInput] Speech recognition error:", err.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimText("");
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (!speechSupported) {
      // Fallback demo speech if browser doesn't have Web Speech API
      setTranscript("Um, so basically, I am thinking about how to connect distributed autonomous agents with first-principles cognitive models, like, how do they synchronize memory without drift?");
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      setTranscript("");
      setResult(null);
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (e) {
        console.error("Failed to start speech recognition:", e);
      }
    }
  };

  const handleSynthesize = async () => {
    const speechToProcess = transcript.trim();
    if (!speechToProcess) return;

    setAnalyzing(true);
    try {
      const data = await api.processSpokenThought(speechToProcess);
      if (data) {
        setResult(data);
      }
    } catch (e) {
      console.error("Voice synthesis failed:", e);
    } finally {
      setAnalyzing(false);
    }
  };

  const copyPrompt = () => {
    if (!result?.suggested_prompt) return;
    navigator.clipboard.writeText(result.suggested_prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-2xl max-w-2xl w-full mx-auto relative overflow-hidden text-slate-800 dark:text-slate-100">
      {/* Background Accent */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold tracking-tight">Spoken Thought Ingestion</h3>
            <p className="text-xs text-slate-400">Speak your raw stream-of-consciousness. We strip fillers and extract intent.</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Mic Trigger & Waveform */}
      <div className="my-6 flex flex-col items-center justify-center gap-4">
        <div className="relative">
          {isListening && (
            <div className="absolute -inset-4 rounded-full bg-primary/20 animate-ping" />
          )}
          <button
            onClick={toggleListening}
            className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl cursor-pointer ${
              isListening
                ? "bg-red-500 text-white shadow-red-500/25 animate-pulse"
                : "bg-primary text-white hover:bg-primary/90 shadow-primary/25"
            }`}
          >
            {isListening ? <MicOff size={32} /> : <Mic size={32} />}
          </button>
        </div>

        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {isListening ? "Listening... Speak freely" : "Click Microphone to Begin Speaking"}
        </p>

        {!speechSupported && (
          <div className="flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 text-amber-500 border border-amber-500/20 rounded-full text-xs">
            <AlertCircle size={14} />
            <span>Web Speech API not detected in this browser. Demo transcript provided.</span>
          </div>
        )}
      </div>

      {/* Live Transcript / Speech Input Area */}
      <div className="space-y-3">
        <div className="relative">
          <textarea
            value={transcript + (interimText ? ` (${interimText})` : "")}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Your spoken words will appear here in real-time, or you can paste stream-of-consciousness notes..."
            rows={4}
            className="w-full text-sm bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 focus:outline-none focus:ring-2 focus:ring-primary/40 leading-relaxed text-slate-800 dark:text-slate-200 resize-none font-sans"
          />
        </div>

        {transcript && (
          <div className="flex items-center justify-between">
            <button
              onClick={() => { setTranscript(""); setResult(null); }}
              className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              Clear transcript
            </button>
            <button
              onClick={handleSynthesize}
              disabled={analyzing}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-white font-semibold text-xs rounded-xl shadow-md hover:bg-primary/90 disabled:opacity-50 transition-all cursor-pointer"
            >
              <Sparkles size={14} className={analyzing ? "animate-spin" : ""} />
              {analyzing ? "Synthesizing Cognitive Model..." : "Formulate Structured Thought"}
            </button>
          </div>
        )}
      </div>

      {/* Synthesis Result Display */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 15 }}
            className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800 space-y-4"
          >
            {/* Fillers & Ambiguity Score */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-slate-50 dark:bg-slate-950/40 rounded-xl border border-slate-200/60 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-500">Fillers Stripped:</span>
                {result.filler_words_removed.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {result.filler_words_removed.map((filler, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 font-mono">
                        "{filler}"
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-xs text-slate-400">None detected</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-500">Clarity:</span>
                <span className="text-xs font-mono font-bold text-emerald-500">
                  {((1 - result.spoken_ambiguity_score) * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Implicit Intent */}
            <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-xl">
              <span className="text-[10px] font-bold text-blue-500 uppercase tracking-wider block mb-1">
                Extracted Implicit Goal
              </span>
              <p className="text-xs font-medium text-slate-800 dark:text-slate-200">
                {result.implicit_intent}
              </p>
            </div>

            {/* Latent Hypotheses */}
            {result.latent_hypotheses.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                  Latent Hypotheses & Inherent Assumptions:
                </span>
                {result.latent_hypotheses.map((hyp, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                    <span>{hyp}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Synthesized Prompt */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Synthesized LLM Prompt
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={copyPrompt}
                    className="inline-flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 font-medium"
                  >
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                    {copied ? "Copied!" : "Copy Prompt"}
                  </button>
                  {onApplyPrompt && (
                    <button
                      onClick={() => onApplyPrompt(result.suggested_prompt)}
                      className="inline-flex items-center gap-1 text-xs text-emerald-500 hover:text-emerald-600 font-medium"
                    >
                      <span>Send to Canvas</span>
                      <ArrowRight size={12} />
                    </button>
                  )}
                </div>
              </div>
              <div className="bg-slate-900 border border-white/10 rounded-xl p-4 font-mono text-xs text-emerald-400 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                {result.suggested_prompt}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
