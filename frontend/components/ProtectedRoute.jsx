"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useEffect } from "react";

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      if (adminOnly) {
        router.replace("/admin/login");
      } else {
        router.replace("/login");
      }
      return;
    }
    if (adminOnly && user.role !== "admin") {
      router.replace("/dashboard");
    }
  }, [user, loading, adminOnly, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!user) return null;
  if (adminOnly && user.role !== "admin") return null;

  return children;
}
