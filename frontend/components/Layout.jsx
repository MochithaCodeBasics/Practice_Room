"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { PracticeRoomLogo, PracticeRoomText } from "@/components/Branding";

export default function Layout({ children, sidebarExtra }) {
  return (
    <div className="flex min-h-screen bg-gray-50 text-gray-900 font-sans">
      <aside className="w-72 bg-white border-r border-gray-200 hidden lg:flex flex-col h-screen sticky top-0">
        <div className="pt-6 px-8 pb-8 border-b border-gray-100 flex flex-col items-center text-center">
          <PracticeRoomLogo variant="vertical" logoSize="h-10" className="text-xl" />
        </div>
        <div className="flex-1 flex flex-col overflow-y-auto">
          <nav className="p-4 space-y-1">
            <Link href="/dashboard" className="flex items-center px-4 py-2 text-sm font-semibold text-indigo-600 bg-indigo-50 rounded-lg">
              Dashboard
            </Link>
          </nav>
          {sidebarExtra}
        </div>
        <div className="p-4 border-t border-gray-100" />
      </aside>
      <main className="flex-1 overflow-auto">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-8 justify-between md:hidden">
          <h1 className="text-xl font-extrabold tracking-tight text-slate-700">
            <PracticeRoomText className="text-xl" />
          </h1>
        </header>
        <div className="p-8 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
}
