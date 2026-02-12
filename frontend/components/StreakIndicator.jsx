"use client";

import { useState } from "react";
import { Flame } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function StreakIndicator() {
  const { user } = useAuth();
  const [showTooltip, setShowTooltip] = useState(false);

  if (user?.role !== "learner") return null;

  return (
    <div className="relative z-50">
      <div
        className="flex items-center gap-2 bg-gradient-to-r from-orange-50 to-amber-50 px-4 py-1.5 rounded-full border border-orange-100/50 shadow-sm transition-transform hover:scale-105 cursor-help"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
      >
        <Flame size={16} className={user.current_streak > 0 ? "text-orange-500 fill-orange-200" : "text-gray-300"} />
        <span className="text-sm font-black text-orange-600 tabular-nums">{user.current_streak || 0}</span>
        <span className="text-xs font-bold text-orange-400/80 uppercase tracking-wider">Streaks</span>
      </div>
      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-orange-100 p-4 z-50 animate-in fade-in zoom-in-95 duration-200">
          <div className="absolute top-0 right-6 -mt-1 w-2 h-2 bg-white border-t border-l border-orange-100 transform rotate-45" />
          <div className="flex items-start gap-3">
            <div>
              <h4 className="text-sm font-bold text-gray-800 mb-1">Keep it burning! 🔥</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                Solve at least one problem every day to build your streak and establish a consistent coding habit.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
