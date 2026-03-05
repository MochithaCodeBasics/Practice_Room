"use client";
import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import Layout from "@/components/Layout";
import NotFoundView from "@/components/NotFoundView";
import Link from "next/link";
import { ArrowLeft, Search, Filter, Tag } from "lucide-react";
import { CheckCircle, Clock } from "lucide-react";
import api from "@/services/api";
import axios from "axios";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import type { Module as ModuleType, Filters } from "@/types";

interface ModuleQuestion {
    id: string;
    slug: string;
    title: string;
    difficulty: string;
    topic?: string;
    tags?: string;
    is_verified?: boolean;
    is_completed?: boolean;
    is_attempted?: boolean;
    created_at?: string;
}

export default function ModuleQuestionsPage({
    params,
}: {
    params: Promise<{ slug: string }>;
}) {
    const { slug } = use(params);
    const router = useRouter();


    const [module, setModule] = useState<ModuleType | null>(null);
    const [questions, setQuestions] = useState<ModuleQuestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [notFound, setNotFound] = useState(false);

    const [searchTerm, setSearchTerm] = useState("");
    const [filters, setFilters] = useState<Filters>({ difficulty: "", status: "", topic: "" });
    const [availableTopics, setAvailableTopics] = useState<string[]>([]);

    // Fetch module metadata
    useEffect(() => {
        api
            .get<ModuleType[]>("/modules/")
            .then((res) => {
                const found = res.data.find((m) => m.slug === slug);
                if (!found) {
                    setNotFound(true);
                } else {
                    setModule(found);
                }
            })
            .catch((err) => {
                console.error("Failed to fetch module", err);
                setNotFound(true);
            });
    }, [slug]);

    // Fetch questions for this module
    useEffect(() => {
        if (notFound) return;

        const fetchQuestions = async () => {
            setLoading(true);
            try {
                const params: Record<string, string> = {};
                if (filters.difficulty) params.difficulty = filters.difficulty;
                if (filters.topic) params.topic = filters.topic;
                if (searchTerm) params.search = searchTerm;

                const res = await api.get<ModuleQuestion[]>(`/modules/${slug}/questions`, { params });
                const data = res.data;
                setQuestions(data);

                // Extract available topics
                const topics = new Set<string>();
                data.forEach((q) => {
                    if (q.topic) topics.add(q.topic.trim());
                });
                setAvailableTopics(Array.from(topics).sort());
            } catch (err) {
                if (axios.isAxiosError(err) && err.response?.status === 404) {
                    setNotFound(true);
                }
                console.error("Failed to fetch questions", err);
            } finally {
                setLoading(false);
            }
        };
        fetchQuestions();
    }, [slug, filters.difficulty, filters.topic, searchTerm, notFound]);

    const resetFilters = () => {
        setSearchTerm("");
        setFilters({ difficulty: "", status: "", topic: "" });
    };

    // Navigation
    const handleQuestionClick = (questionSlug: string) => {
        router.push(`/modules/${slug}/questions/${questionSlug}`);
    };

    if (notFound) {
        return (
            <NotFoundView
                title="Ooopss!! Not found!"
                message="The module you're looking for doesn't exist or has been removed."
            />
        );
    }

    const moduleName = module
        ? module.name.replace(/practice/gi, "").trim()
        : slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

    // Sidebar filters
    const sidebarFilters = (
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
                    <p className="text-[10px] font-bold text-gray-500 uppercase ml-1">Difficulty</p>
                    <div className="flex flex-wrap gap-1.5">
                        {[
                            { id: "", label: "All" },
                            { id: "easy", label: "Easy" },
                            { id: "medium", label: "Medium" },
                            { id: "hard", label: "Hard" },
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
                {availableTopics.length > 0 && (
                    <div className="space-y-2">
                        <p className="text-[10px] font-bold text-gray-500 uppercase ml-1">Topic</p>
                        <div className="flex flex-wrap gap-1">
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
                )}
            </div>
        </div>
    );

    return (
        <Layout sidebarExtra={sidebarFilters}>
            <div className="mb-10 flex justify-between items-start">
                <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                        <Link
                            href="/"
                            className="p-2 hover:bg-gray-100 rounded-full transition-colors group"
                            title="Back to Modules"
                        >
                            <ArrowLeft size={20} className="text-gray-400 group-hover:text-gray-600" />
                        </Link>
                        <h1 className="text-lg font-bold text-gray-700 tracking-tight">{moduleName}</h1>
                    </div>
                </div>
                <div className="flex flex-col items-end gap-3">
                </div>
            </div>

            {/* Question List */}
            <div className="space-y-4">
                <div className="flex items-center gap-4 mb-8">
                    <h2 className="text-sm font-black text-gray-400 uppercase tracking-[0.2em] whitespace-nowrap">
                        Available Questions ({questions.length})
                    </h2>
                    <div className="flex-1 h-px bg-gray-200/60" />
                </div>

                {loading && questions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <Skeleton className="h-12 w-12 rounded-full mb-4" />
                        <p className="text-gray-500 font-medium">Loading questions...</p>
                    </div>
                ) : questions.length === 0 ? (
                    <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                        <p className="text-gray-500">No questions found for this module yet.</p>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {questions.map((q) => (
                            <Card
                                key={q.id}
                                onClick={() => handleQuestionClick(q.slug)}
                                className="hover:shadow-md hover:shadow-indigo-500/5 hover:border-indigo-500/30 hover:scale-[1.005] transition-all duration-200 cursor-pointer relative group overflow-hidden border-l-4 border-l-transparent hover:border-l-indigo-600"
                            >
                                <CardHeader className="pb-2">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="flex items-center gap-2">
                                            <Badge
                                                variant="outline"
                                                className={`text-[10px] font-black uppercase tracking-wider rounded-md border
                        ${q.difficulty === "easy" ? "bg-emerald-50 text-emerald-700 border-emerald-100" : q.difficulty === "medium" ? "bg-amber-50 text-amber-700 border-amber-100" : "bg-rose-50 text-rose-700 border-rose-100"}`}
                                            >
                                                {q.difficulty}
                                            </Badge>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            {q.is_completed ? (
                                                <Badge variant="secondary" className="flex items-center gap-1.5 text-green-600 bg-green-50 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight hover:bg-green-100">
                                                    <CheckCircle size={12} className="fill-green-100" /> Completed
                                                </Badge>
                                            ) : q.is_attempted ? (
                                                <Badge variant="secondary" className="flex items-center gap-1.5 text-amber-600 bg-amber-50 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight hover:bg-amber-100">
                                                    <Clock size={12} className="fill-amber-100" /> Attempted
                                                </Badge>
                                            ) : null}
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
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
}
