"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Pencil, Trash2, ChevronLeft, ChevronRight } from "lucide-react";
import type { QuestionRead, Module } from "@/types";

const PAGE_SIZE = 20;

export default function AdminQuestionsPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<QuestionRead[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterModule, setFilterModule] = useState("");
  const [filterDifficulty, setFilterDifficulty] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [questionsRes, modulesRes] = await Promise.all([
          api.get<QuestionRead[]>("/modules/questions"),
          api.get<Module[]>("/modules/"),
        ]);
        setQuestions(questionsRes.data);
        setModules(modulesRes.data);
      } catch (err) {
        console.error("Failed to fetch data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const moduleMap = new Map(modules.map((m) => [m.id, m.name]));

  const filtered = useMemo(() => {
    return questions.filter((q) => {
      const matchesModule = !filterModule || q.module_id === filterModule;
      const matchesDifficulty =
        !filterDifficulty || q.difficulty.toLowerCase() === filterDifficulty;
      return matchesModule && matchesDifficulty;
    });
  }, [questions, filterModule, filterDifficulty]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginatedQuestions = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  );

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filterModule, filterDifficulty]);

  const handleDelete = async (id: string, title: string) => {
    if (pendingDeleteId !== id) {
      setPendingDeleteId(id);
      return;
    }

    try {
      await api.delete(`/v1/admin/questions/${id}`);
      setQuestions((prev) => prev.filter((q) => q.id !== id));
      setPendingDeleteId(null);
    } catch (err) {
      console.error("Failed to delete question", err);
    }
  };

  const handleVerify = async (id: string, currentStatus: boolean) => {
    try {
      await api.post(`/v1/admin/questions/${id}/verify`, {
        verified: !currentStatus,
      });
      setQuestions((prev) =>
        prev.map((q) =>
          q.id === id ? { ...q, is_verified: !currentStatus } : q
        )
      );
    } catch (err) {
      console.error("Failed to update verification", err);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">All Questions</h1>
          <p className="text-gray-500 text-sm mt-1">
            {filtered.length} question{filtered.length !== 1 ? "s" : ""}
            {(filterModule || filterDifficulty) && ` (filtered from ${questions.length})`}
          </p>
        </div>
        <Button
          onClick={() => router.push("/admin/upload")}
          className="bg-indigo-600 hover:bg-indigo-700 font-bold"
        >
          + Add Question
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={filterModule}
          onChange={(e) => setFilterModule(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none bg-white"
        >
          <option value="">All Modules</option>
          {modules.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
        <select
          value={filterDifficulty}
          onChange={(e) => setFilterDifficulty(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none bg-white"
        >
          <option value="">All Difficulties</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        {(filterModule || filterDifficulty) && (
          <button
            type="button"
            onClick={() => {
              setFilterModule("");
              setFilterDifficulty("");
            }}
            className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Table */}
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full rounded-lg" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
          <p className="text-gray-500">No questions found.</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50/50">
                  <th className="text-left px-4 py-3 font-bold text-gray-500 text-xs uppercase tracking-wider">
                    Title
                  </th>
                  <th className="text-left px-4 py-3 font-bold text-gray-500 text-xs uppercase tracking-wider hidden md:table-cell">
                    Module
                  </th>
                  <th className="text-center px-4 py-3 font-bold text-gray-500 text-xs uppercase tracking-wider">
                    Difficulty
                  </th>
                  <th className="text-center px-4 py-3 font-bold text-gray-500 text-xs uppercase tracking-wider">
                    Status
                  </th>
                  <th className="text-right px-4 py-3 font-bold text-gray-500 text-xs uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedQuestions.map((q) => (
                  <tr
                    key={q.id}
                    className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <p className="font-semibold text-gray-800 truncate max-w-xs">
                        {q.title}
                      </p>
                      <p className="text-xs text-gray-400 font-mono">{q.id}</p>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-xs text-gray-500">
                        {moduleMap.get(q.module_id) || q.module_id}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge
                        variant="outline"
                        className={`text-[10px] font-black uppercase tracking-wider rounded-md border ${
                          q.difficulty.toLowerCase() === "easy"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-100"
                            : q.difficulty.toLowerCase() === "medium"
                              ? "bg-amber-50 text-amber-700 border-amber-100"
                              : "bg-rose-50 text-rose-700 border-rose-100"
                        }`}
                      >
                        {q.difficulty}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        type="button"
                        onClick={() => handleVerify(q.id, !!q.is_verified)}
                        title={
                          q.is_verified
                            ? "Click to unverify"
                            : "Click to verify"
                        }
                      >
                        <Badge
                          variant="outline"
                          className={`text-[10px] font-bold uppercase cursor-pointer ${
                            q.is_verified
                              ? "bg-green-50 text-green-700 border-green-100"
                              : "bg-red-50 text-red-700 border-red-100"
                          }`}
                        >
                          {q.is_verified ? "Verified" : "Unverified"}
                        </Badge>
                      </button>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50"
                          onClick={() => router.push(`/admin/edit/${q.id}`)}
                          title="Edit"
                        >
                          <Pencil size={14} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-gray-400 hover:text-red-600 hover:bg-red-50"
                          onClick={() => handleDelete(q.id, q.title)}
                          title={
                            pendingDeleteId === q.id
                              ? `Confirm delete "${q.title}"`
                              : "Delete"
                          }
                        >
                          <Trash2 size={14} />
                        </Button>
                        {pendingDeleteId === q.id && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 px-2 text-xs text-gray-500 hover:text-gray-700"
                            onClick={() => setPendingDeleteId(null)}
                            title="Cancel delete"
                          >
                            Cancel
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 px-1">
              <p className="text-xs text-gray-500">
                Page {currentPage} of {totalPages}
              </p>
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 w-8 p-0"
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage((p) => p - 1)}
                >
                  <ChevronLeft size={16} />
                </Button>
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((page) => {
                    // Show first, last, current, and neighbors
                    return (
                      page === 1 ||
                      page === totalPages ||
                      Math.abs(page - currentPage) <= 1
                    );
                  })
                  .reduce<(number | "...")[]>((acc, page, idx, arr) => {
                    if (idx > 0 && page - (arr[idx - 1] as number) > 1) {
                      acc.push("...");
                    }
                    acc.push(page);
                    return acc;
                  }, [])
                  .map((item, idx) =>
                    item === "..." ? (
                      <span
                        key={`ellipsis-${idx}`}
                        className="px-1 text-xs text-gray-400"
                      >
                        ...
                      </span>
                    ) : (
                      <Button
                        key={item}
                        variant={currentPage === item ? "default" : "outline"}
                        size="sm"
                        className="h-8 w-8 p-0 text-xs"
                        onClick={() => setCurrentPage(item as number)}
                      >
                        {item}
                      </Button>
                    )
                  )}
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 w-8 p-0"
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage((p) => p + 1)}
                >
                  <ChevronRight size={16} />
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
