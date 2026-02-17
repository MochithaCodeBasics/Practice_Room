"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getQuestions, deleteQuestion } from "@/services/api";
import { Trash2, Pencil, CheckCircle, Clock } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { QuestionRead, Filters } from "@/types";

interface QuestionListProps {
  moduleId: string;
  onSelectQuestion: (id: string) => void;
  filters: Filters;
  searchTerm: string;
}

export default function QuestionList({ moduleId, onSelectQuestion, filters, searchTerm }: QuestionListProps) {
  const [questions, setQuestions] = useState<QuestionRead[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true);
      try {
        const data = await getQuestions(filters);
        let filtered = data.filter((q) => q.module_id === moduleId || (!q.module_id && moduleId === "math_stats"));
        if (searchTerm) {
          filtered = filtered.filter(
            (q) =>
              q.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
              q.id.toLowerCase().includes(searchTerm.toLowerCase())
          );
        }
        if (filters.topic) {
          filtered = filtered.filter((q) => q.topic && q.topic.trim() === filters.topic.trim());
        }
        setQuestions(filtered);
      } catch (error) {
        console.error("Failed to fetch questions", error);
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, [moduleId, filters, searchTerm]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (typeof window !== "undefined" && window.confirm("Are you sure? This will delete the question permanently.")) {
      try {
        await deleteQuestion(id);
        setQuestions((q) => q.filter((ques) => ques.id !== id));
      } catch (err) {
        console.error("Delete failed", err);
        alert("Failed to delete question");
      }
    }
  };

  if (loading && questions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Skeleton className="h-12 w-12 rounded-full mb-4" />
        <p className="text-gray-500 font-medium">Loading questions...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 mb-8">
        <h2 className="text-sm font-black text-gray-400 uppercase tracking-[0.2em] whitespace-nowrap">
          Available Questions ({questions.length})
        </h2>
        <div className="flex-1 h-px bg-gray-200/60" />
      </div>
      {questions.length === 0 ? (
        <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
          <p className="text-gray-500">No questions found matching your criteria.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {questions.map((q) => (
            <Card
              key={q.id}
              onClick={() => onSelectQuestion(q.id)}
              className="hover:shadow-md hover:shadow-indigo-500/5 hover:border-indigo-500/30 hover:scale-[1.005] transition-all duration-200 cursor-pointer relative group overflow-hidden border-l-4 border-l-transparent hover:border-l-indigo-600"
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className={`text-[10px] font-black uppercase tracking-wider rounded-md border
                      ${q.difficulty === "Easy" ? "bg-emerald-50 text-emerald-700 border-emerald-100" : q.difficulty === "Medium" ? "bg-amber-50 text-amber-700 border-amber-100" : "bg-rose-50 text-rose-700 border-rose-100"}`}
                    >
                      {q.difficulty}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4">
                    {user?.role !== "admin" &&
                      (q.is_completed ? (
                        <Badge variant="secondary" className="flex items-center gap-1.5 text-green-600 bg-green-50 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight hover:bg-green-100">
                          <CheckCircle size={12} className="fill-green-100" /> Completed
                        </Badge>
                      ) : q.is_attempted ? (
                        <Badge variant="secondary" className="flex items-center gap-1.5 text-amber-600 bg-amber-50 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight hover:bg-amber-100">
                          <Clock size={12} className="fill-amber-100" /> Attempted
                        </Badge>
                      ) : null)}
                    {user?.role === "admin" && (
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md border tracking-tighter ${q.is_verified ? "bg-green-50 text-green-700 border-green-100" : "bg-red-50 text-red-700 border-red-100"}`}>
                          {q.is_verified ? "Verified" : "Unverified"}
                        </Badge>
                        <Badge variant="outline" className="text-[10px] text-gray-400 font-mono bg-gray-50 px-2 py-0.5 border-gray-100 tracking-tighter font-normal hover:bg-gray-50">
                          {q.id}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
                <CardTitle className="text-lg font-bold text-slate-800 group-hover:text-indigo-600 transition-colors pr-12 leading-tight">
                  {q.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="pb-3 pt-0">
                <div className="flex flex-wrap gap-1.5">
                  {q.tags &&
                    q.tags.split(",").map((tag) => (
                      <Badge
                        key={tag}
                        variant="secondary"
                        className="text-[10px] font-medium text-slate-500 bg-slate-50 px-3 py-1 rounded-full border border-slate-100/50 transition-colors group-hover:bg-slate-100 group-hover:text-slate-600"
                      >
                        {tag.trim().toLowerCase()}
                      </Badge>
                    ))}
                </div>
              </CardContent>
              <CardFooter className="flex justify-end items-center pt-0 pb-3 pr-6 gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                {user?.role === "admin" && (
                  <>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="text-[10px] font-bold uppercase h-auto py-1.5 px-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50"
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/admin/edit/${q.id}`);
                      }}
                      title="Edit Question"
                    >
                      <Pencil size={12} className="mr-1 inline" /> Edit
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="text-[10px] font-bold uppercase h-auto py-1.5 px-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50"
                      onClick={(e) => handleDelete(e, q.id)}
                      title="Delete Question"
                    >
                      <Trash2 size={12} className="mr-1 inline" /> Delete
                    </Button>
                  </>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
