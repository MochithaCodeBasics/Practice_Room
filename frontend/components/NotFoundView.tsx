"use client";

import Link from "next/link";
import Image from "next/image";
import { ArrowLeft } from "lucide-react";

interface NotFoundViewProps {
    title?: string;
    message?: string;
}

export default function NotFoundView({
    title = "Ooopss!! Not found!",
    message = "The page you're looking for doesn't exist or has been moved.",
}: NotFoundViewProps) {
    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
            <div className="flex justify-end p-6">
                <Link
                    href="/"
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg font-bold text-sm"
                >
                    <ArrowLeft size={16} />
                    Back to home
                </Link>
            </div>
            <div className="flex-1 flex flex-col items-center justify-center -mt-16">
                <h1 className="text-[10rem] font-black text-gray-900 leading-none tracking-tighter select-none">
                    404
                </h1>
                <div className="my-6">
                    <Image
                        src="/sleeping-panda-404.png"
                        alt="Sleeping panda"
                        width={280}
                        height={280}
                        priority
                        className="drop-shadow-lg"
                    />
                </div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mt-2">
                    {title}
                </h2>
                {message && (
                    <p className="text-gray-500 mt-3 text-center max-w-md">
                        {message}
                    </p>
                )}
            </div>
        </div>
    );
}
