"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Layout from "@/components/Layout";
import QuestionList from "@/components/QuestionList";
import ModuleList from "@/components/ModuleList";
import UserProfile from "@/components/UserProfile";
import StreakIndicator from "@/components/StreakIndicator";
import { Search, Filter, Tag } from "lucide-react";
import api from "@/services/api";
import dynamic from "next/dynamic";

const Workspace = dynamic(() => import("@/components/Workspace"), { ssr: false });

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [selectedModule, setSelectedModule] = useState(null);
  const [selectedQuestionId, setSelectedQuestionId] = useState(null);
  const [modules, setModules] = useState([]);
  const [questionIds, setQuestionIds] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({ difficulty: "", status: "", topic: "" });
  const [availableTopics, setAvailableTopics] = useState([]);

  useEffect(() => {
    api.get("/modules/").then((res) => setModules(res.data)).catch((err) => console.error("Failed to fetch modules", err));
  }, []);

  useEffect(() => {
    if (selectedModule) {
      const fetchTopics = async () => {
        try {
          const res = await api.get("/questions/");
          const allQuestions = res.data.filter((q) => q.module_id === selectedModule || (!q.module_id && selectedModule === "math_stats"));
          const topics = new Set();
          allQuestions.forEach((q) => {
            if (q.topic) topics.add(q.topic.trim());
          });
          setAvailableTopics(Array.from(topics).sort());
          setQuestionIds(allQuestions.map((q) => q.id));
        } catch (err) {
          console.error("Failed to fetch topics", err);
        }
      };
      fetchTopics();
    }
  }, [selectedModule]);

  const resetFilters = () => {
    setSearchTerm("");
    setFilters({ difficulty: "", status: "", topic: "" });
  };

  const handleNavigatePrev = () => {
    const currentIndex = questionIds.indexOf(selectedQuestionId);
    if (currentIndex > 0) setSelectedQuestionId(questionIds[currentIndex - 1]);
  };

  const handleNavigateNext = () => {
    const currentIndex = questionIds.indexOf(selectedQuestionId);
    if (currentIndex < questionIds.length - 1) setSelectedQuestionId(questionIds[currentIndex + 1]);
  };

  if (selectedQuestionId) {
    const currentIndex = questionIds.indexOf(selectedQuestionId);
    return (
      <Workspace
        questionId={selectedQuestionId}
        onBack={() => setSelectedQuestionId(null)}
        onPrev={currentIndex > 0 ? handleNavigatePrev : null}
        onNext={currentIndex < questionIds.length - 1 ? handleNavigateNext : null}
        currentIndex={currentIndex}
        totalQuestions={questionIds.length}
      />
    );
  }

  const handleBackToModules = () => {
    resetFilters();
    setSelectedModule(null);
  };

  const handleModuleSelect = (moduleId) => {
    resetFilters();
    setSelectedModule(moduleId);
  };

  const sidebarFilters = selectedModule ? (
    <div className="p-4 space-y-8 border-t border-gray-100 mt-4">
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-[10px] font-black text-gray-400 uppercase tracking-widest px-2">
          <Search size={12} className="text-gray-400" /> Quick Search
        </label>
        <div className="relative group px-2">
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all placeholder:text-gray-400 group-hover:bg-white"
          />
        </div>
      </div>
      <div className="space-y-4 px-2">
        <label className="flex items-center gap-2 text-[10px] font-black text-gray-400 uppercase tracking-widest">
          <Filter size={12} className="text-indigo-500" /> Filtering
        </label>
        <div className="space-y-2">
          <p className="text-[10px] font-bold text-gray-500 uppercase ml-1">Status</p>
          <div className="flex flex-wrap gap-1.5">
            {[
              { id: "", label: "All" },
              { id: "todo", label: "Todo" },
              { id: "attempted", label: "Attempted" },
              { id: "completed", label: "Completed" },
            ].map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => setFilters({ ...filters, status: s.id })}
                className={`px-3 py-1 text-[10px] font-bold rounded-md transition-all border ${filters.status === s.id ? "bg-indigo-600 text-white border-indigo-600 shadow-sm" : "bg-white text-gray-500 border-gray-200 hover:border-indigo-300 hover:text-indigo-600"}`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-[10px] font-bold text-gray-500 uppercase ml-1">Difficulty</p>
          <div className="flex flex-wrap gap-1.5">
            {[
              { id: "", label: "All" },
              { id: "Easy", label: "Easy" },
              { id: "Medium", label: "Medium" },
              { id: "Hard", label: "Hard" },
            ].map((d) => (
              <button
                key={d.id}
                type="button"
                onClick={() => setFilters({ ...filters, difficulty: d.id })}
                className={`px-3 py-1 text-[10px] font-bold rounded-md transition-all border ${filters.difficulty === d.id ? "bg-violet-600 text-white border-violet-600 shadow-sm" : "bg-white text-gray-500 border-gray-200 hover:border-violet-300 hover:text-violet-600"}`}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-[10px] font-bold text-gray-500 uppercase ml-1">Topic</p>
          <div className="grid grid-cols-1 gap-1">
            <button
              type="button"
              onClick={() => setFilters({ ...filters, topic: "" })}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all text-left ${filters.topic === "" ? "bg-indigo-50 text-indigo-700" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Tag size={12} className={`shrink-0 ${filters.topic === "" ? "text-indigo-500" : "text-gray-400"}`} />
              <span className="truncate">All Topics</span>
            </button>
            {availableTopics.map((topic) => (
              <button
                key={topic}
                type="button"
                onClick={() => setFilters({ ...filters, topic })}
                className={`flex items-start gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all text-left ${filters.topic === topic ? "bg-indigo-50 text-indigo-700" : "text-gray-600 hover:bg-gray-50"}`}
              >
                <Tag size={12} className={`shrink-0 mt-0.5 ${filters.topic === topic ? "text-indigo-500" : "text-gray-400"}`} />
                <span className="leading-tight">{topic}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  ) : null;

  return (
    <Layout sidebarExtra={sidebarFilters}>
      <div className="mb-10 flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-2">
            {selectedModule && (
              <button
                type="button"
                onClick={handleBackToModules}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors group"
                title="Back to Modules"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400 group-hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            )}
            {selectedModule && (
              <div className="flex items-center gap-3 group">
                <h1 className="text-lg font-bold text-gray-700 tracking-tight">
                  {(modules.find((m) => m.id === selectedModule)?.name || selectedModule.replace(/_/g, " "))
                    .replace(/practice/gi, "")
                    .trim()}
                </h1>
              </div>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-3">
          <div className="flex items-center gap-4 relative">
            <StreakIndicator />
            <UserProfile />
          </div>
          {selectedModule && user?.role === "admin" && (
            <button
              type="button"
              onClick={() => router.push(`/admin/upload?moduleId=${selectedModule}`)}
              className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white px-6 py-2.5 rounded-xl hover:from-indigo-700 hover:to-violet-700 transition-all shadow-lg shadow-indigo-500/20 font-bold text-sm transform hover:-translate-y-0.5 active:translate-y-0 flex items-center gap-2"
            >
              <span>+</span>
              <span>Add New Question</span>
            </button>
          )}
        </div>
      </div>
      {!selectedModule ? (
        <div className="mt-8">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-1 h-6 bg-indigo-400/60 rounded-full" />
            <h2 className="text-2xl font-black text-gray-800 tracking-tight">Modules</h2>
          </div>
          <ModuleList onSelectModule={handleModuleSelect} />
        </div>
      ) : (
        <QuestionList moduleId={selectedModule} onSelectQuestion={setSelectedQuestionId} filters={filters} searchTerm={searchTerm} />
      )}
    </Layout>
  );
}
