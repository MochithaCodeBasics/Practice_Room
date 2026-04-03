"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import AuthPopup from "@/components/AuthPopup";

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
}

export default function ProtectedRoute({ children, adminOnly = false }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const [showAuthPopup, setShowAuthPopup] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-4">
          <h2 className="text-xl font-bold text-gray-700">Authentication Required</h2>
          <p className="text-gray-500 text-sm">Please sign in to access this page.</p>
          <button
            type="button"
            onClick={() => setShowAuthPopup(true)}
            className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-bold text-sm"
          >
            Sign In with Codebasics
          </button>
          <AuthPopup open={showAuthPopup} onOpenChange={setShowAuthPopup} />
        </div>
      </div>
    );
  }

  if (adminOnly && !user.isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-4">
          <h2 className="text-xl font-bold text-gray-700">Access Denied</h2>
          <p className="text-gray-500 text-sm">You do not have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
