"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { PracticeRoomLogo } from "@/components/Branding";
import UserProfile from "@/components/UserProfile";
import StreakIndicator from "@/components/StreakIndicator";
import AuthPopup from "@/components/AuthPopup";

export default function Header() {
  const { user } = useAuth();
  const [showAuthPopup, setShowAuthPopup] = useState(false);

  return (
    <header className="sticky top-0 z-30 h-16 bg-background/80 backdrop-blur-md border-b border flex items-center px-8 justify-between">
      <Link href="/" className="flex items-center">
        <PracticeRoomLogo variant="horizontal" logoSize="h-8" className="text-lg" />
      </Link>
      <div className="flex items-center gap-4">
        {user ? (
          <>
            <StreakIndicator />
            <UserProfile />
          </>
        ) : (
          <button
            type="button"
            onClick={() => setShowAuthPopup(true)}
            className="px-5 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-display font-bold uppercase tracking-wide text-sm"
          >
            Sign In
          </button>
        )}
      </div>
      <AuthPopup open={showAuthPopup} onOpenChange={setShowAuthPopup} />
    </header>
  );
}
