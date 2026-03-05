"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { getQuestionBySlug } from "@/services/api";
import NotFoundView from "@/components/NotFoundView";
import { Loader } from "lucide-react";
import type { QuestionDetail } from "@/types";
import api from "@/services/api";

// Dynamically import Workspace to avoid SSR issues with Monaco Editor
const Workspace = dynamic(() => import("@/components/Workspace"), { ssr: false });

export default function QuestionDetailPage({
    params,
}: {
    params: Promise<{ slug: string; questionSlug: string }>;
}) {
    const { slug, questionSlug } = use(params);
    const router = useRouter();

    const [question, setQuestion] = useState<QuestionDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [notFound, setNotFound] = useState(false);

    // Navigation state
    const [nextSlug, setNextSlug] = useState<string | null>(null);
    const [prevSlug, setPrevSlug] = useState<string | null>(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [totalQuestions, setTotalQuestions] = useState(0);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // 1. Fetch current question details
                const questionData = await getQuestionBySlug(slug, questionSlug);
                setQuestion(questionData);

                // 2. Fetch all questions in module to determine prev/next navigation
                // ideally this would be optimized, but for now fetching list is okay
                const questionsRes = await api.get(`/modules/${slug}/questions`);
                const allQuestions = questionsRes.data;

                const index = allQuestions.findIndex((q: any) => q.slug === questionSlug);
                setCurrentIndex(index);
                setTotalQuestions(allQuestions.length);

                if (index > 0) {
                    setPrevSlug(allQuestions[index - 1].slug);
                } else {
                    setPrevSlug(null);
                }

                if (index < allQuestions.length - 1) {
                    setNextSlug(allQuestions[index + 1].slug);
                } else {
                    setNextSlug(null);
                }

            } catch (err: any) {
                console.error("Failed to fetch question", err);
                if (err.response && err.response.status === 404) {
                    setNotFound(true);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [slug, questionSlug]);

    if (notFound) {
        return (
            <NotFoundView
                title="Question Not Found"
                message="The question you are looking for does not exist or has been moved."
            />
        );
    }

    if (loading || !question) {
        return (
            <div className="flex-1 flex items-center justify-center bg-background h-screen">
                <div className="flex flex-col items-center gap-3">
                    <Loader className="animate-spin text-primary" size={32} />
                    <p className="text-muted-foreground font-medium text-lg">Loading Question...</p>
                </div>
            </div>
        );
    }

    return (
        <Workspace
            questionId={question.id}
            initialQuestion={question}
            onBack={() => router.push(`/modules/${slug}`)}
            onPrev={prevSlug ? () => router.push(`/modules/${slug}/questions/${prevSlug}`) : null}
            onNext={nextSlug ? () => router.push(`/modules/${slug}/questions/${nextSlug}`) : null}
            currentIndex={currentIndex}
            totalQuestions={totalQuestions}
        />
    );
}
