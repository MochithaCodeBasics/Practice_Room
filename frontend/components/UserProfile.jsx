"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export default function UserProfile() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [userStats, setUserStats] = useState({ completed: 0, attempted: 0, todo: 0 });

  useEffect(() => {
    if (isOpen) {
      api
        .get("/questions/")
        .then((res) => {
          const all = res.data;
          const completed = all.filter((q) => q.is_completed).length;
          const attempted = all.filter((q) => q.is_attempted && !q.is_completed).length;
          const todo = all.length - completed - attempted;
          setUserStats({ completed, attempted, todo });
        })
        .catch((err) => console.error("Failed to fetch stats", err));
    }
  }, [isOpen]);

  if (!user) return null;

  const total = userStats.completed + userStats.attempted + userStats.todo;
  const completedPct = total > 0 ? (userStats.completed / total) * 100 : 0;
  const attemptedPct = total > 0 ? ((userStats.completed + userStats.attempted) / total) * 100 : 0;

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className="h-9 w-9 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold border border-blue-200 shadow-sm hover:ring-2 hover:ring-blue-300 transition-all outline-none"
          title={user.username || "User"}
        >
          <Avatar className="h-9 w-9">
            <AvatarFallback className="bg-blue-100 text-blue-600 text-sm font-bold">
              {user.username?.[0]?.toUpperCase() || "U"}
            </AvatarFallback>
          </Avatar>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-64 p-0 rounded-xl overflow-hidden" align="end" forceMount>
        <div className="p-4 border-b border-gray-50 bg-gray-50/50">
          <p className="text-sm text-gray-500">Hi,</p>
          <p className="text-lg font-bold text-gray-800 truncate">{user.username}</p>
        </div>

        {user.role !== "admin" && (
          <div className="p-4 flex flex-col items-center gap-4">
            <div
              className="relative w-24 h-24 rounded-full"
              style={{
                background: `conic-gradient(
                  #22c55e 0% ${completedPct}%,
                  #f59e0b ${completedPct}% ${attemptedPct}%,
                  #e5e7eb ${attemptedPct}% 100%
                )`,
              }}
            >
              <div className="absolute inset-2 bg-white rounded-full flex items-center justify-center flex-col">
                <span className="text-xs font-bold text-gray-400">Total</span>
                <span className="text-xl font-black text-gray-800">{total}</span>
              </div>
            </div>
            <div className="w-full space-y-2">
              <div className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5 font-medium text-gray-600">
                  <span className="w-2 h-2 rounded-full bg-green-500" /> Completed
                </span>
                <span className="font-bold text-gray-800">{userStats.completed}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5 font-medium text-gray-600">
                  <span className="w-2 h-2 rounded-full bg-amber-500" /> Attempted
                </span>
                <span className="font-bold text-gray-800">{userStats.attempted}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5 font-medium text-gray-600">
                  <span className="w-2 h-2 rounded-full bg-gray-200" /> Todo
                </span>
                <span className="font-bold text-gray-800">{userStats.todo}</span>
              </div>
            </div>
          </div>
        )}

        <div className="p-2 border-t border-gray-100 bg-gray-50 flex flex-col gap-1">
          <DropdownMenuItem asChild>
            <Button
              variant="outline"
              size="sm"
              className="w-full text-xs font-bold border-gray-200 hover:bg-white cursor-pointer justify-center"
              onClick={() => router.push("/dashboard/settings")}
            >
              Environment Settings
            </Button>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Button
              variant="destructive"
              size="sm"
              className="w-full h-7 text-[10px] font-bold cursor-pointer justify-center mt-1"
              onClick={logout}
            >
              Sign Out
            </Button>
          </DropdownMenuItem>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
