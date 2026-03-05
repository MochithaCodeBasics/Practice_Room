"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Pencil, Trash2, ChevronLeft, ChevronRight, CheckCircle, Power } from "lucide-react";
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
          api.get<QuestionRead[]>("/v1/admin/questions"),
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

  const moduleMap = new Map(modules.map((m) => [String(m.id), m.name]));

  const filtered = useMemo(() => {
    return questions.filter((q) => {
      const matchesModule = !filterModule || String(q.module_id) === filterModule;
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

  const handleDelete = async (id: string) => {
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

  const handleMarkVerified = async (id: string) => {
    try {
      await api.post(`/v1/admin/questions/${id}/verify`, {
        verified: true,
      });
      setQuestions((prev) =>
        prev.map((q) =>
          q.id === id ? { ...q, is_verified: true } : q
        )
      );
    } catch (err) {
      console.error("Failed to verify question", err);
    }
  };

  const handleActivation = async (id: string, currentStatus: boolean) => {
    try {
      await api.post(`/v1/admin/questions/${id}/activate`, {
        active: !currentStatus,
      });
      setQuestions((prev) =>
        prev.map((q) =>
          q.id === id ? { ...q, is_active: !currentStatus } : q
        )
      );
    } catch (err) {
      console.error("Failed to update activation", err);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold uppercase text-foreground">All Questions</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {filtered.length} question{filtered.length !== 1 ? "s" : ""}
            {(filterModule || filterDifficulty) && ` (filtered from ${questions.length})`}
          </p>
        </div>
        <Button
          onClick={() => router.push("/admin/upload")}
          className="bg-primary hover:bg-primary/90 font-bold"
        >
          + Add Question
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={filterModule}
          onChange={(e) => setFilterModule(e.target.value)}
          className="px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none bg-background text-foreground"
        >
          <option value="">All Modules</option>
          {modules.map((m) => (
            <option key={m.id} value={String(m.id)}>
              {m.name}
            </option>
          ))}
        </select>
        <select
          value={filterDifficulty}
          onChange={(e) => setFilterDifficulty(e.target.value)}
          className="px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none bg-background text-foreground"
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
            className="px-3 py-2 text-sm text-muted-foreground hover:text-foreground underline"
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
        <div className="text-center py-20 bg-card rounded-xl border-2 border-dashed border">
          <p className="text-muted-foreground">No questions found.</p>
        </div>
      ) : (
        <>
          <div className="bg-card rounded-xl border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border bg-muted/30">
                  <th className="text-left px-4 py-3 font-bold text-muted-foreground text-xs uppercase tracking-wider">
                    Title
                  </th>
                  <th className="text-left px-4 py-3 font-bold text-muted-foreground text-xs uppercase tracking-wider hidden md:table-cell">
                    Module
                  </th>
                  <th className="text-center px-4 py-3 font-bold text-muted-foreground text-xs uppercase tracking-wider">
                    Difficulty
                  </th>
                  <th className="text-center px-4 py-3 font-bold text-muted-foreground text-xs uppercase tracking-wider">
                    Status
                  </th>
                  <th className="text-right px-4 py-3 font-bold text-muted-foreground text-xs uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedQuestions.map((q) => (
                  <tr
                    key={q.id}
                    className="border-b border hover:bg-muted/20 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <p className="font-semibold text-foreground truncate max-w-xs">
                        {q.title}
                      </p>
                      <p className="text-xs text-muted-foreground font-mono">{q.id}</p>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-xs text-muted-foreground">
                        {moduleMap.get(String(q.module_id)) || q.module_id}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge
                        variant="outline"
                        className={`text-[10px] font-black uppercase tracking-wider rounded-md border ${
                          q.difficulty.toLowerCase() === "easy"
                            ? "bg-cb-teal/10 text-cb-teal border-cb-teal/25"
                            : q.difficulty.toLowerCase() === "medium"
                              ? "bg-cb-orange/10 text-cb-orange border-cb-orange/25"
                              : "bg-cb-pink/10 text-cb-pink border-cb-pink/25"
                        }`}
                      >
                        {q.difficulty}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex flex-col items-center gap-1">
                        <Badge
                          variant="outline"
                          className={`text-[10px] font-bold uppercase ${
                            q.is_verified
                              ? "bg-cb-teal/10 text-cb-teal border-cb-teal/25"
                              : "bg-destructive/10 text-destructive border-destructive/25"
                          }`}
                        >
                          {q.is_verified ? "Verified" : "Unverified"}
                        </Badge>
                        <Badge
                          variant="outline"
                          className={`text-[10px] font-bold uppercase ${
                            q.is_active
                              ? "bg-cb-teal/10 text-cb-teal border-cb-teal/25"
                              : "bg-muted text-muted-foreground border"
                          }`}
                        >
                          {q.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1 flex-wrap">
                        {!q.is_verified && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 px-2 text-[11px] text-muted-foreground hover:text-cb-teal hover:bg-cb-teal/10"
                            onClick={() => handleMarkVerified(q.id)}
                            title="Mark as verified"
                          >
                            <CheckCircle size={13} className="mr-1" />
                            Verify
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 px-2 text-[11px] text-muted-foreground hover:text-cb-teal hover:bg-cb-teal/10"
                          onClick={() => handleActivation(q.id, !!q.is_active)}
                          title={q.is_active ? "Inactivate" : "Activate"}
                        >
                          <Power size={13} className="mr-1" />
                          {q.is_active ? "Inactivate" : "Activate"}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-muted-foreground hover:text-primary hover:bg-primary/10"
                          onClick={() => router.push(`/admin/edit/${q.id}`)}
                          title="Edit"
                        >
                          <Pencil size={14} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                          onClick={() => handleDelete(q.id)}
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
                            className="h-8 px-2 text-xs text-muted-foreground hover:text-foreground"
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
              <p className="text-xs text-muted-foreground">
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
                        className="px-1 text-xs text-muted-foreground"
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
