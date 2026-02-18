"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Header from "@/components/Header";
import { LayoutDashboard, Upload, List } from "lucide-react";

interface AdminLayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/questions", label: "Questions", icon: List },
  { href: "/admin/upload", label: "Add a Question", icon: Upload },
];

export default function AdminLayout({ children }: AdminLayoutProps) {
  const pathname = usePathname();

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 text-gray-900 font-sans">
      <Header />
      <div className="flex flex-1">
        <aside className="w-64 bg-white border-r border-gray-200 hidden lg:flex flex-col">
          <div className="p-4 border-b border-gray-100">
            <p className="text-xs font-black text-gray-400 uppercase tracking-widest">Admin Panel</p>
          </div>
          <nav className="p-4 space-y-1 flex-1">
            {navItems.map((item) => {
              const isActive =
                item.href === "/admin"
                  ? pathname === "/admin"
                  : pathname.startsWith(item.href) ||
                    (item.href === "/admin/questions" && pathname.startsWith("/admin/edit"));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-2.5 text-sm font-semibold rounded-lg transition-colors ${
                    isActive
                      ? "text-indigo-600 bg-indigo-50"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
                  }`}
                >
                  <item.icon size={16} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="p-4 border-t border-gray-100">
            <Link
              href="/"
              className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-gray-400 hover:text-gray-600 transition-colors"
            >
              &larr; Back to Practice Room
            </Link>
          </div>
        </aside>
        <main className="flex-1 overflow-auto">
          <div className="p-8 max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
}
