"use client";

import { useState } from "react";
import { Flame } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function StreakIndicator() {
  const { user } = useAuth();
  const [showTooltip, setShowTooltip] = useState<boolean>(false);

  if (!user || user.isAdmin) return null;

  return (
    <div className="relative z-50">
      <div
        className="flex items-center gap-2 bg-gradient-to-r from-cb-orange/10 to-cb-orange/5 px-4 py-1.5 rounded-full border border-cb-orange/25 shadow-sm transition-transform hover:scale-105 cursor-help"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
      >
        <Flame size={16} className={user.current_streak > 0 ? "text-cb-orange fill-cb-orange/30" : "text-muted-foreground/30"} />
        <span className="text-sm font-black text-cb-orange tabular-nums">{user.current_streak || 0}</span>
        <span className="text-xs font-bold text-cb-orange/60 uppercase tracking-wider">Streaks</span>
      </div>
      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-popover rounded-xl shadow-xl border border-cb-orange/20 p-4 z-50 animate-in fade-in zoom-in-95 duration-200">
          <div className="absolute top-0 right-6 -mt-1 w-2 h-2 bg-popover border-t border-l border-cb-orange/20 transform rotate-45" />
          <div className="flex items-start gap-3">
            <div>
              <h4 className="text-sm font-bold text-foreground mb-1">Keep it burning! 🔥</h4>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Solve at least one problem every day to build your streak and establish a consistent coding habit.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
