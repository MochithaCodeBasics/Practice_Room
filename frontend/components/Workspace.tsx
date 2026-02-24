"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Confetti from "react-confetti";
import { Download, ChevronDown, FileCode, FileText, Lock, Loader, CheckCircle, Clock, AlertTriangle } from "lucide-react";
import Layout from "@/components/Layout";
import UserProfile from "@/components/UserProfile";
import StreakIndicator from "@/components/StreakIndicator";
import { PracticeRoomLogo } from "@/components/Branding";
import AuthPopup from "@/components/AuthPopup";
import { getQuestion, runCode, validateCode, verifyQuestion } from "@/services/api";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import type { QuestionDetail, ExecutionResult } from "@/types";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

interface WorkspaceProps {
  questionId: string;
  onBack: () => void;
  onPrev: (() => void) | null;
  onNext: (() => void) | null;
  currentIndex?: number;
  totalQuestions?: number;
  initialQuestion?: QuestionDetail;
}

interface SavedArtifact {
  runId: string;
  filename: string;
}

function getOutputLineTone(line: string): "error" | "warning" | "success" | "default" {
  const text = line.toLowerCase();

  if (
    text.includes("error") ||
    text.includes("traceback") ||
    text.includes("exception") ||
    text.includes("failed") ||
    text.includes("quota exceeded") ||
    text.includes("rate limited")
  ) {
    return "error";
  }

  if (text.includes("warning") || text.includes("system notice")) {
    return "warning";
  }

  if (text.includes("[pass]") || text.includes("correct!") || text.includes("verified")) {
    return "success";
  }

  return "default";
}

function getOutputLineClass(tone: "error" | "warning" | "success" | "default"): string {
  if (tone === "error") {
    return "bg-rose-900/40 text-rose-200 border-l-2 border-rose-500 px-2 py-1 rounded-sm";
  }
  if (tone === "warning") {
    return "bg-amber-900/30 text-amber-100 border-l-2 border-amber-400 px-2 py-1 rounded-sm";
  }
  if (tone === "success") {
    return "bg-emerald-900/30 text-emerald-200 border-l-2 border-emerald-500 px-2 py-1 rounded-sm";
  }
  return "text-slate-300";
}

export default function Workspace({ questionId, onBack, onPrev, onNext, currentIndex = 0, totalQuestions = 0, initialQuestion }: WorkspaceProps) {
  const { user, refreshUser, isAuthenticated } = useAuth();
  const [showAuthPopup, setShowAuthPopup] = useState<boolean>(false);
  const [question, setQuestion] = useState<QuestionDetail | null>(initialQuestion || null);
  const [code, setCode] = useState<string>(initialQuestion?.initial_code || "");
  const [output, setOutput] = useState<string>("");
  const [runResult, setRunResult] = useState<ExecutionResult | null>(null);
  const [showConfetti, setShowConfetti] = useState<boolean>(false);
  const [isValidationPassed, setIsValidationPassed] = useState<boolean>(false);
  const [isVerified, setIsVerified] = useState<boolean>(initialQuestion?.is_verified || false);
  const [lastRunOutput, setLastRunOutput] = useState<string>("");
  const [isDownloadMenuOpen, setIsDownloadMenuOpen] = useState<boolean>(false);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState<boolean>(false);
  const [savedArtifacts, setSavedArtifacts] = useState<SavedArtifact[]>([]);

  useEffect(() => {
    if (initialQuestion && initialQuestion.id === questionId) {
      setQuestion(initialQuestion);
      setCode(initialQuestion.initial_code || "# Write your solution here\n");
      setIsValidationPassed(false);
      setIsVerified(initialQuestion.is_verified || false);
      setRunResult(null);
      setOutput("");
      setLastRunOutput("");
      setSavedArtifacts([]);
      setShowConfetti(false);
      return;
    }

    getQuestion(questionId).then((data) => {
      setQuestion(data);
      setCode(data.initial_code || "# Write your solution here\n");
      setIsValidationPassed(false);
      setIsVerified(data.is_verified || false);
      setRunResult(null);
      setOutput("");
      setLastRunOutput("");
      setSavedArtifacts([]);
      setShowConfetti(false);
    });
  }, [questionId, initialQuestion]);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.title = "Practice Room";
      return () => {
        document.title = "Practice Room";
      };
    }
  }, []);

  const handleRun = async () => {
    if (!question) return;
    if (!isAuthenticated) {
      setShowAuthPopup(true);
      return;
    }
    setOutput("Running code...");
    setSavedArtifacts([]);
    try {
      const result = await runCode({ code, question_id: question.id, module_id: question.module_id });
      setRunResult(result);
      // Smarter stderr handling
      let runOut = result.stdout || "";
      if (result.stderr) {
        const stderrLow = result.stderr.toLowerCase();
        const isWarning = stderrLow.includes("warning");
        const isInfo = stderrLow.includes("font cache") || stderrLow.includes("building the font cache");
        const isQuota = stderrLow.includes("insufficient_quota") || stderrLow.includes("exceeded your current quota");
        const isRateLimit = stderrLow.includes("rate_limit_exceeded") || stderrLow.includes("rate limit reached");

        if (isInfo) {
          runOut += `\n--- SYSTEM NOTICE ---\n${result.stderr}`;
        } else if (isQuota) {
          runOut += `\n--- QUOTA EXCEEDED ---\nYour Groq API key has run out of credits or reached its limit. Please check your billing at console.groq.com.\n\nRaw Error:\n${result.stderr}`;
        } else if (isRateLimit) {
          runOut += `\n--- RATE LIMITED ---\nYou are making requests too fast. Please wait a moment before running again.\n\nRaw Error:\n${result.stderr}`;
        } else {
          runOut += `\n${isWarning ? "--- SYSTEM NOTICE ---" : "ERROR:"}\n${result.stderr}`;
        }
      }
      setOutput(runOut);
      setLastRunOutput(runOut);
      if (result.artifacts && result.artifacts.length > 0) {
        setSavedArtifacts(result.artifacts.map((a) => ({ runId: result.run_id || "", filename: a })));
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setOutput("System Error: " + message);
    }
  };

  const handleValidate = async () => {
    if (!question) return;
    if (!isAuthenticated) {
      setShowAuthPopup(true);
      return;
    }
    setOutput("Validating...");
    setSavedArtifacts([]);
    try {
      const result = await validateCode({ code, question_id: question.id, module_id: question.module_id });
      setRunResult(result);
      const text = (result.stdout || "") + (result.stderr ? "\nVALIDATION ERROR:\n" + result.stderr : "");
      setOutput(`Validation Result:\n${text}`);
      if (result.artifacts && result.artifacts.length > 0) {
        setSavedArtifacts(result.artifacts.map((a) => ({ runId: result.run_id || "", filename: a })));
      }
      if (result.stdout && (result.stdout.includes("[PASS]") || result.stdout.includes("Correct!") || result.stdout.includes("\u2705"))) {
        setIsValidationPassed(true);
        setShowConfetti(true);
        if (refreshUser) refreshUser();
        setTimeout(() => setShowConfetti(false), 5000);
      } else {
        setIsValidationPassed(false);
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setOutput(`Error during validation: ${message}`);
    }
  };

  const handleVerify = async () => {
    if (!question) return;
    try {
      const newStatus = !isVerified;
      await verifyQuestion(question.id, newStatus);
      setIsVerified(newStatus);
      setOutput((prev) => prev + `\n\n--- System ---\nQuestion marked as ${newStatus ? "VERIFIED" : "UNVERIFIED"}.`);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setOutput((prev) => prev + `\nError updating verification status: ${message}`);
    }
  };

  const handleDownloadPy = () => {
    if (!question) return;
    setIsDownloadMenuOpen(false);
    const blob = new Blob([code], { type: "text/x-python" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${question.title ? question.title.replace(/\s+/g, "_") : "solution"}.py`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleDownloadPdf = () => {
    setIsDownloadMenuOpen(false);
    setIsGeneratingPdf(true);
  };

  if (!question) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white h-screen">
        <div className="flex flex-col items-center gap-3">
          <Loader className="animate-spin text-indigo-600" size={32} />
          <p className="text-gray-500 font-medium text-lg">Loading Codebasics Practice Room...</p>
        </div>
      </div>
    );
  }

  const today = typeof window !== "undefined" ? new Date().toLocaleString("en-US", { dateStyle: "long", timeStyle: "short" }) : "";
  const pdfArtifacts = savedArtifacts;
  const pdfOutputText = lastRunOutput;

  return (
    <div id="workspace-root" className="h-screen flex flex-col bg-white overflow-hidden relative">
      {showConfetti && typeof window !== "undefined" && (
        <Confetti width={window.innerWidth} height={window.innerHeight} recycle={false} numberOfPieces={500} gravity={0.2} />
      )}

      {isGeneratingPdf && (
        <style>{`
          @media print {
            @page { margin: 7.5mm; size: auto; }
            html, body, #__next, #workspace-root {
              height: auto !important; width: 100% !important;
              overflow: visible !important; position: static !important;
              display: block !important;
            }
            #workspace-root > * { display: none !important; }
            header { display: none !important; }
            #workspace-root > #pdf-report-overlay {
              display: block !important; visibility: visible !important;
              position: absolute !important; left: 0; top: 0;
              width: 100% !important; height: auto !important;
              overflow: visible !important; background: white;
              z-index: 99999; padding: 0 !important; margin: 0 !important;
            }
            #pdf-report-overlay > div {
              position: static !important; display: block !important;
              width: 100% !important; margin: 0 !important; padding: 0 !important;
            }
            #pdf-report-final {
              display: block !important; visibility: visible !important;
              width: 100% !important; max-width: none !important;
              margin: 0 !important; padding: 0 !important;
              box-shadow: none !important; height: auto !important;
            }
            #pdf-report-final * { visibility: visible !important; }
            #pdf-controls, #pdf-loading { display: none !important; }
            .page-break-inside-avoid { page-break-inside: avoid; }
          }
        `}</style>
      )}

      <div className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-4 flex-shrink-0 z-40 shadow-sm sticky top-0">
        <div className="flex items-center gap-5">
          <PracticeRoomLogo />
        </div>
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <StreakIndicator />
              <UserProfile />
            </>
          ) : (
            <button
              type="button"
              onClick={() => setShowAuthPopup(true)}
              className="px-4 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-bold text-xs"
            >
              Sign In
            </button>
          )}
        </div>
      </div>

      <header className="h-10 border-b border-gray-200 flex items-center justify-between px-4 bg-gray-50 flex-shrink-0 z-30">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onBack}
            className="h-7 px-2 text-slate-500 hover:text-slate-900 hover:bg-slate-200/50 flex items-center gap-1 font-medium transition-all group"
          >
            <span className="text-slate-400 group-hover:translate-x-[-2px] transition-transform">&larr;</span>
            <span className="text-[11px] uppercase tracking-wider font-bold">Back</span>
          </Button>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={onPrev ?? undefined}
              disabled={!onPrev}
              className={`w-6 h-6 flex items-center justify-center rounded text-sm font-bold transition-all ${onPrev ? "text-gray-500 hover:text-indigo-600 hover:bg-indigo-50" : "text-gray-300 cursor-not-allowed"}`}
              title="Previous Question"
            >
              &lt;
            </button>
            {totalQuestions > 0 && (
              <span className="text-[10px] text-gray-400 font-medium tabular-nums px-1">
                {currentIndex + 1}/{totalQuestions}
              </span>
            )}
            <button
              type="button"
              onClick={onNext ?? undefined}
              disabled={!onNext}
              className={`w-6 h-6 flex items-center justify-center rounded text-sm font-bold transition-all ${onNext ? "text-gray-500 hover:text-indigo-600 hover:bg-indigo-50" : "text-gray-300 cursor-not-allowed"}`}
              title="Next Question"
            >
              &gt;
            </button>
          </div>
          <h1 className="text-sm font-bold text-gray-800 truncate max-w-xl">{question.title}</h1>
          {user?.role !== "admin" &&
            (isValidationPassed || question.is_completed ? (
              <span className="flex items-center gap-1 text-green-600 bg-green-50 px-2 py-0.5 rounded-full text-[10px] font-bold border border-green-100">
                <CheckCircle size={10} /> COMPLETED
              </span>
            ) : question.is_attempted ? (
              <span className="flex items-center gap-1 text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full text-[10px] font-bold border border-amber-100">
                <Clock size={10} /> ATTEMPTED
              </span>
            ) : null)}
          {user?.role === "admin" && (
            <div
              onClick={isValidationPassed ? handleVerify : undefined}
              className={`ml-2 px-3 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest select-none transition-all border shadow-sm flex items-center gap-1 ${!isValidationPassed
                ? "bg-slate-50 text-slate-300 border-slate-100 cursor-not-allowed opacity-60"
                : isVerified
                  ? "bg-emerald-50 text-emerald-600 border-emerald-200 hover:bg-emerald-100 ring-1 ring-emerald-500/20 cursor-pointer"
                  : "bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200 hover:text-slate-700 cursor-pointer"
                }`}
              title={!isValidationPassed ? "Pass validation to enable verification" : "Click to toggle verification status"}
            >
              {isVerified ? "Verified \u2713" : "Unverified"}
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-hidden relative flex">
        <ResizablePanelGroup direction="horizontal">
          <ResizablePanel defaultSize={33} minSize={20} className="bg-gray-50">
            <div className="h-full border-r border-gray-200 overflow-hidden flex flex-col">
              <div className="h-8 bg-gray-50 border-b border-gray-200 flex items-center px-4 shrink-0">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Question Details</span>
              </div>
              <div className="flex-1 overflow-y-auto p-4">
                <div className="prose prose-sm max-w-none text-gray-700 prose-headings:text-base prose-headings:font-bold prose-h1:text-lg prose-h2:text-base prose-h3:text-sm prose-h4:text-sm">
                  {/* AI Key Warning */}
                  {(question.module_id === "genai" || question.module_id === "agentic") && (!user?.has_groq_api_key && !user?.has_openai_api_key && !user?.has_anthropic_api_key) && (
                    <div className="mb-6 p-5 bg-amber-50 border border-amber-100 rounded-2xl flex gap-4 animate-pulse">
                      <AlertTriangle className="text-amber-600 shrink-0" size={20} />
                      <div className="space-y-2">
                        <p className="text-xs font-black text-amber-900 uppercase tracking-[0.05em]">
                          API KEY REQUIRED
                        </p>
                        <p className="text-[11px] text-amber-700 font-medium leading-relaxed">
                          This question requires a specialized engine. Please set your <strong>LLM Provider API Key</strong> in{" "}
                          <a href="/settings" className="text-amber-800 font-bold underline hover:text-amber-950">
                            Environment Settings
                          </a>{" "}
                          to run this code.
                        </p>
                      </div>
                    </div>
                  )}
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{question.question_py}</ReactMarkdown>
                </div>
                {question.hint && (
                  <div className="mt-8 pt-4 border-t border-gray-200">
                    <details className="group">
                      <summary className="cursor-pointer text-xs font-bold text-gray-600">{"\uD83D\uDCA1"} Show Hint</summary>
                      <div className="mt-2 text-xs text-gray-600 bg-yellow-50 p-3 rounded border border-yellow-200">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{question.hint}</ReactMarkdown>
                      </div>
                    </details>
                  </div>
                )}
                {question.sample_data && (
                  <div className="mt-6">
                    <h4 className="font-bold text-gray-800 text-xs mb-2">{"\uD83D\uDCCA"} Sample Data (First 5 Rows)</h4>
                    <div className="overflow-x-auto border border-gray-200 rounded p-2 bg-gray-50">
                      <div className="prose prose-xs max-w-none prose-table:border-collapse prose-table:text-xs prose-td:border prose-td:px-2 prose-th:bg-gray-100">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{question.sample_data}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          <ResizablePanel defaultSize={67} minSize={30}>
            <ResizablePanelGroup direction="vertical">
              <ResizablePanel defaultSize={70} minSize={20}>
                <div className="w-full h-full relative flex flex-col">
                  <div className="h-8 bg-slate-50 border-b border-slate-200 flex items-center justify-between shrink-0">
                    <div className="flex items-center gap-2 px-4 h-full bg-white rounded-t-md border-l border-t border-r border-slate-200 relative -mb-px z-10">
                      <img src="/assets/python.png" alt="Python" className="h-3.5 w-3.5 object-contain" />
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Python</span>
                    </div>
                    <div className="flex items-center gap-2 pr-2">
                      <div className="w-px h-4 bg-slate-300 mx-1" />
                      <Button type="button" variant="secondary" size="sm" onClick={handleRun} className="h-7 text-[10px] uppercase font-bold tracking-wider bg-white border-slate-200 text-slate-600 hover:bg-slate-50">
                        Run Code
                      </Button>
                      <Button type="button" size="sm" onClick={handleValidate} className="h-7 text-[10px] uppercase font-bold tracking-wider bg-indigo-600 hover:bg-indigo-700 text-white border-none">
                        Submit & Validate
                      </Button>
                    </div>
                  </div>
                  <div className="flex-1 min-h-0 border-l border-r border-b border-slate-200 bg-white relative">
                    <Editor
                      height="100%"
                      defaultLanguage="python"
                      value={code}
                      onChange={(value) => setCode(value || "")}
                      options={{ minimap: { enabled: false }, fontSize: 12, automaticLayout: true }}
                    />
                  </div>
                </div>
              </ResizablePanel>

              <ResizableHandle withHandle />

              <ResizablePanel defaultSize={30} minSize={10} className="bg-slate-900 border-t border-slate-800">
                <div className="flex flex-col h-full bg-slate-900 text-slate-300 text-sm overflow-hidden shadow-inner">
                  <div className="flex justify-between items-center bg-slate-950/50 border-b border-slate-800 p-2 shrink-0">
                    <span className="uppercase text-[10px] font-bold tracking-wider text-indigo-400 flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                      Console Output
                    </span>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          setOutput("");
                          setLastRunOutput("");
                          setSavedArtifacts([]);
                        }}
                        className="text-gray-400 hover:text-white uppercase text-[10px]"
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                  <div className="flex-1 overflow-auto p-4 font-mono">
                    {savedArtifacts?.map((item, i) => (
                      <div key={i} className="mb-4 bg-slate-800/50 border border-slate-700 p-2 rounded-lg">
                        <span className="text-xs text-slate-400 block mb-2 font-medium">Image: {item.filename}</span>
                        <img src={`/api/execute/runs/${item.runId}/${item.filename}`} alt="Output" className="max-w-full h-auto" />
                      </div>
                    ))}
                    <div className="text-xs space-y-1">
                      {(output || "")
                        .split("\n")
                        .map((line, idx) => {
                          const tone = getOutputLineTone(line);
                          return (
                            <div
                              key={`${idx}-${line.slice(0, 16)}`}
                              className={`whitespace-pre-wrap break-words ${getOutputLineClass(tone)}`}
                            >
                              {line || " "}
                            </div>
                          );
                        })}
                    </div>
                  </div>
                </div>
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>

      {isGeneratingPdf && (
        <div id="pdf-report-overlay" className="fixed inset-0 z-[100] bg-gray-800 bg-opacity-75 flex justify-center overflow-auto p-8 backdrop-blur-sm">
          <div className="relative shrink-0 flex flex-col items-center">
            <div id="pdf-controls" className="bg-white p-2 rounded shadow-lg mb-4 flex flex-col gap-2 w-fit items-center">
              <div className="flex gap-2">
                <Button onClick={() => typeof window !== "undefined" && window.print()} className="bg-blue-600 hover:bg-blue-700 text-white font-bold">
                  <Download size={16} className="mr-2" /> Print / Save as PDF
                </Button>
                <Button variant="secondary" onClick={() => setIsGeneratingPdf(false)} className="font-bold">
                  Close
                </Button>
              </div>
            </div>
            <div
              id="pdf-report-final"
              className="bg-white text-gray-800 font-sans shadow-2xl relative w-[816px] shrink-0 origin-top h-fit mb-20"
              style={{ WebkitPrintColorAdjust: "exact", printColorAdjust: "exact" } as React.CSSProperties}
            >
              <div className="bg-slate-50 border-b border-slate-200 px-8 py-3 flex justify-between items-center">
                <span className="text-[10px] font-medium text-slate-500 tracking-wider">
                  Generated by <span className="font-bold text-blue-500">codebasics</span> Practice Room
                </span>
                <span className="text-[10px] font-medium text-slate-400">{today}</span>
              </div>
              <div className="px-12 pt-6 pb-4 border-b-4 border-indigo-500">
                <h1 className="text-2xl font-bold text-gray-900 leading-tight text-left">{question.title}</h1>
              </div>
              <div className="px-12 py-10 space-y-8 min-h-[600px]">
                <div className="space-y-2">
                  <div className="border-b border-blue-50 pb-1 mb-2">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-blue-500 border-l-[5px] border-blue-300 pl-3">Problem Statement</h3>
                  </div>
                  <div className="prose prose-sm max-w-none text-gray-600 text-xs leading-relaxed text-left prose-headings:text-gray-500 prose-headings:text-xs prose-headings:font-bold prose-headings:uppercase prose-headings:tracking-widest prose-headings:mb-2 prose-headings:mt-4 prose-pre:bg-slate-900 prose-pre:text-emerald-300 prose-pre:rounded-lg prose-pre:shadow-sm prose-pre:p-4 prose-pre:border prose-pre:border-slate-800">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{question.question_py}</ReactMarkdown>
                  </div>
                </div>
                {question.sample_data && (
                  <div className="space-y-2">
                    <div className="border-b border-rose-50 pb-1 mb-2">
                      <h3 className="text-sm font-bold uppercase tracking-widest text-rose-500 border-l-[5px] border-rose-300 pl-3">Dataset Preview</h3>
                    </div>
                    <div className="border border-gray-100 rounded-lg overflow-hidden inline-block w-fit">
                      <div className="prose prose-sm max-w-none prose-table:w-auto prose-table:text-[10px] prose-table:m-0 prose-thead:bg-rose-50 prose-thead:text-rose-900 prose-thead:border-b prose-thead:border-rose-100 prose-th:p-2 prose-th:uppercase prose-th:font-semibold prose-th:tracking-wider prose-th:text-left prose-tr:border-b prose-tr:border-gray-50 last:prose-tr:border-0 prose-td:p-2 prose-td:text-gray-600 font-mono prose-td:text-left">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{question.sample_data}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}
                <div className="space-y-2">
                  <div className="border-b border-emerald-50 pb-1 mb-2">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-emerald-500 border-l-[5px] border-emerald-300 pl-3">Solution Code</h3>
                  </div>
                  <div className="bg-[#1e1e1e] rounded-lg overflow-hidden shadow-sm">
                    <div className="flex gap-1.5 px-3 py-1.5 bg-[#252526] border-b border-[#333]">
                      <div className="w-2 h-2 rounded-full bg-rose-400 opacity-80" />
                      <div className="w-2 h-2 rounded-full bg-amber-400 opacity-80" />
                      <div className="w-2 h-2 rounded-full bg-emerald-400 opacity-80" />
                    </div>
                    <pre className="p-3 text-[10px] font-mono text-gray-300 whitespace-pre-wrap leading-relaxed border-none m-0">{code}</pre>
                  </div>
                </div>
                {(pdfOutputText || (pdfArtifacts && pdfArtifacts.length > 0)) && (
                  <div className="space-y-2">
                    <div className="border-b border-amber-50 pb-1 mb-2">
                      <h3 className="text-sm font-bold uppercase tracking-widest text-amber-500 border-l-[5px] border-amber-300 pl-3">Output</h3>
                    </div>
                    {pdfArtifacts?.map((item, i) => (
                      <div key={i} className="mb-4 bg-gray-50 p-2 rounded-lg border border-gray-100 page-break-inside-avoid break-inside-avoid" style={{ pageBreakInside: "avoid" }}>
                        <img
                          src={`/api/execute/runs/${item.runId}/${item.filename}`}
                          alt="Graph"
                          className="max-w-full h-auto max-h-[500px] object-contain mx-auto"
                          crossOrigin="anonymous"
                          onError={(e) => ((e.target as HTMLImageElement).style.display = "none")}
                        />
                      </div>
                    ))}
                    {pdfOutputText && (
                      <div className="bg-gray-50 border-l-2 border-gray-300 p-3 text-[10px] font-mono text-gray-600 whitespace-pre-wrap page-break-inside-avoid break-inside-avoid">
                        {pdfOutputText}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      <AuthPopup open={showAuthPopup} onOpenChange={setShowAuthPopup} />
    </div>
  );
}
