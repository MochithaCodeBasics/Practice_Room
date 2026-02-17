"use client";

import { useAuth } from "@/context/AuthContext";
import Layout from "@/components/Layout";
import ModuleList from "@/components/ModuleList";
import UserProfile from "@/components/UserProfile";
import StreakIndicator from "@/components/StreakIndicator";
import Link from "next/link";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <Layout>
      <div className="mb-10 flex justify-between items-start">
        <div className="flex-1" />
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <StreakIndicator />
              <UserProfile />
            </>
          ) : (
            <Link
              href="/login"
              className="px-5 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-bold text-sm"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>
      <div className="mt-8">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-1 h-6 bg-indigo-400/60 rounded-full" />
          <h2 className="text-2xl font-black text-gray-800 tracking-tight">Modules</h2>
        </div>
        <ModuleList />
      </div>
    </Layout>
  );
}
