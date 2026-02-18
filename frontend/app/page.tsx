"use client";

import Layout from "@/components/Layout";
import ModuleList from "@/components/ModuleList";

export default function HomePage() {
  return (
    <Layout>
      <div className="mt-4">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-1 h-6 bg-indigo-400/60 rounded-full" />
          <h2 className="text-2xl font-black text-gray-800 tracking-tight">Modules</h2>
        </div>
        <ModuleList />
      </div>
    </Layout>
  );
}
