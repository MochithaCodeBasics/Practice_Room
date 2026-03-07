"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useSession, signOut as nextAuthSignOut } from "next-auth/react";
import type { User, AuthContextType } from "@/types";

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const { data: session, status } = useSession();
  const [user, setUser] = useState<User | null>(null);
  const [showAuthPopup, setShowAuthPopup] = useState(false);

  const loading = status === "loading";
  const isAuthenticated = !!session?.user;

  // Auto sign-out when the OAuth refresh token is exhausted or invalid.
  useEffect(() => {
    if ((session as any)?.error === "RefreshAccessTokenError") {
      nextAuthSignOut({ callbackUrl: "/" });
    }
  }, [session]);

  useEffect(() => {
    if (session?.user) {
      setUser({
        id: session.user.id,
        name: session.user.name || undefined,
        username: session.user.name || session.user.email || undefined,
        email: session.user.email || undefined,
        image: session.user.image || undefined,
        role: session.user.role || "learner",
      });
    } else {
      setUser(null);
    }
  }, [session]);

  const logout = useCallback(() => {
    nextAuthSignOut({ callbackUrl: "/" });
  }, []);

  const openAuthPopup = useCallback(() => {
    setShowAuthPopup(true);
  }, []);

  const refreshUser = useCallback(async () => {
    // With Auth.js, session is managed automatically
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated,
        logout,
        openAuthPopup,
        refreshUser,
      }}
    >
      {children}
      {showAuthPopup && (
        <AuthPopupPortal
          open={showAuthPopup}
          onOpenChange={setShowAuthPopup}
        />
      )}
    </AuthContext.Provider>
  );
};

function AuthPopupPortal({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const [AuthPopup, setAuthPopup] = useState<React.ComponentType<{ open: boolean; onOpenChange: (v: boolean) => void }> | null>(null);

  useEffect(() => {
    import("@/components/AuthPopup").then((mod) => {
      setAuthPopup(() => mod.default);
    });
  }, []);

  if (!AuthPopup) return null;
  return <AuthPopup open={open} onOpenChange={onOpenChange} />;
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
};
