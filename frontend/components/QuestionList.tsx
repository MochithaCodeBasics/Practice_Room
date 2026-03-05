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
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
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
    if (pendingDeleteId !== id) {
      setPendingDeleteId(id);
      return;
    }

    try {
      await deleteQuestion(id);
      setQuestions((q) => q.filter((ques) => ques.id !== id));
      setPendingDeleteId(null);
    } catch (err) {
      console.error("Delete failed", err);
      alert("Failed to delete question");
    }
  };

  if (loading && questions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Skeleton className="h-12 w-12 rounded-full mb-4" />
        <p className="text-muted-foreground font-medium">Loading questions...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 mb-8">
        <h2 className="text-sm font-display font-black text-muted-foreground uppercase tracking-[0.2em] whitespace-nowrap">
          Available Questions ({questions.length})
        </h2>
        <div className="flex-1 h-px bg-border" />
      </div>
      {questions.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-xl border-2 border-dashed border">
          <p className="text-muted-foreground">No questions found matching your criteria.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {questions.map((q) => (
            <Card
              key={q.id}
              onClick={() => onSelectQuestion(q.id)}
              className={`hover:shadow-md hover:shadow-primary/5 hover:border-primary/30 hover:scale-[1.005] transition-all duration-200 cursor-pointer relative group overflow-hidden border-l-4 ${q.is_completed ? "border-l-cb-teal" : "border-l-transparent hover:border-l-primary"}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className={`text-[10px] font-black uppercase tracking-wider rounded-md border
                      ${q.difficulty === "Easy" ? "bg-cb-teal/10 text-cb-teal border-cb-teal/25" : q.difficulty === "Medium" ? "bg-cb-orange/10 text-cb-orange border-cb-orange/25" : "bg-cb-pink/10 text-cb-pink border-cb-pink/25"}`}
                    >
                      {q.difficulty}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4">
                    {user?.role !== "admin" &&
                      (q.is_completed ? (
                        <Badge variant="secondary" className="flex items-center gap-1.5 text-cb-teal bg-cb-teal/10 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight hover:bg-cb-teal/20">
                          <CheckCircle size={12} /> Completed
                        </Badge>
                      ) : q.is_attempted ? (
                        <Badge variant="secondary" className="flex items-center gap-1.5 text-cb-orange bg-cb-orange/10 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight hover:bg-cb-orange/20">
                          <Clock size={12} /> Attempted
                        </Badge>
                      ) : null)}
                    {user?.role === "admin" && (
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md border tracking-tighter ${q.is_verified ? "bg-cb-teal/10 text-cb-teal border-cb-teal/25" : "bg-destructive/10 text-destructive border-destructive/25"}`}>
                          {q.is_verified ? "Verified" : "Unverified"}
                        </Badge>
                        <Badge variant="outline" className="text-[10px] text-muted-foreground font-mono bg-muted px-2 py-0.5 border tracking-tighter font-normal hover:bg-muted">
                          {q.id}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
                <CardTitle className="text-lg font-display font-bold text-foreground group-hover:text-primary transition-colors pr-12 leading-tight">
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
                        className="text-[10px] font-medium text-muted-foreground bg-muted px-3 py-1 rounded-full border transition-colors group-hover:bg-secondary group-hover:text-foreground"
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
                      className="text-[10px] font-bold uppercase h-auto py-1.5 px-1.5 text-muted-foreground hover:text-primary hover:bg-primary/10"
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
                      className="text-[10px] font-bold uppercase h-auto py-1.5 px-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                      onClick={(e) => handleDelete(e, q.id)}
                      title={pendingDeleteId === q.id ? "Confirm delete" : "Delete Question"}
                    >
                      <Trash2 size={12} className="mr-1 inline" /> {pendingDeleteId === q.id ? "Confirm" : "Delete"}
                    </Button>
                    {pendingDeleteId === q.id && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="text-[10px] font-bold uppercase h-auto py-1.5 px-1.5 text-muted-foreground hover:text-foreground hover:bg-muted"
                        onClick={(e) => {
                          e.stopPropagation();
                          setPendingDeleteId(null);
                        }}
                        title="Cancel delete"
                      >
                        Cancel
                      </Button>
                    )}
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
