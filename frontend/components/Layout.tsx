"use client";

import React from "react";
import Header from "@/components/Header";

interface LayoutProps {
  children: React.ReactNode;
  sidebarExtra?: React.ReactNode;
}

export default function Layout({ children, sidebarExtra }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <main className="overflow-auto">
        <Header />
        <div className="p-8 max-w-7xl mx-auto">
          {sidebarExtra && (
            <div className="mb-8 rounded-xl border border-gray-200 bg-white">
              {sidebarExtra}
            </div>
          )}
          {children}
        </div>
      </main>
    </div>
  );
}
