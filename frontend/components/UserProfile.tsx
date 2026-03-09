"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { QuestionRead } from "@/types";

interface UserStats {
  completed: number;
  attempted: number;
  todo: number;
}

export default function UserProfile() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [userStats, setUserStats] = useState<UserStats>({ completed: 0, attempted: 0, todo: 0 });

  useEffect(() => {
    if (isOpen) {
      api
        .get<QuestionRead[]>("/questions/")
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

  const imagePrefix = process.env.NEXT_PUBLIC_CB_IMAGE_PREFIX;
  const avatarUrl = user.image && imagePrefix ? `${imagePrefix}/${user.image}` : undefined;

  const total = userStats.completed + userStats.attempted + userStats.todo;
  const completedPct = total > 0 ? (userStats.completed / total) * 100 : 0;
  const attemptedPct = total > 0 ? ((userStats.completed + userStats.attempted) / total) * 100 : 0;

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold border border-primary/20 shadow-sm hover:ring-2 hover:ring-primary/30 transition-all outline-none"
          title={user.username || "User"}
        >
          <Avatar className="h-9 w-9">
            {avatarUrl && <AvatarImage src={avatarUrl} alt={user.username || "User"} />}
            <AvatarFallback className="bg-primary/10 text-primary text-sm font-bold">
              {user.username?.[0]?.toUpperCase() || "U"}
            </AvatarFallback>
          </Avatar>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-64 p-0 rounded-xl overflow-hidden" align="end" forceMount>
        <div className="p-4 border-b border bg-muted/30">
          <p className="text-sm text-muted-foreground">Hi,</p>
          <p className="text-lg font-bold text-foreground truncate">{user.username}</p>
        </div>

        {user.role !== "admin" && (
          <div className="p-4 flex flex-col items-center gap-4">
            <div
              className="relative w-24 h-24 rounded-full"
              style={{
                background: `conic-gradient(
                  #20C997 0% ${completedPct}%,
                  #FD7E15 ${completedPct}% ${attemptedPct}%,
                  rgba(255,255,255,0.08) ${attemptedPct}% 100%
                )`,
              }}
            >
              <div className="absolute inset-2 bg-card rounded-full flex items-center justify-center flex-col">
                <span className="text-xs font-bold text-muted-foreground">Total</span>
                <span className="text-xl font-black text-foreground">{total}</span>
              </div>
            </div>
            <div className="w-full space-y-2">
              <div className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5 font-medium text-muted-foreground">
                  <span className="w-2 h-2 rounded-full bg-cb-teal" /> Completed
                </span>
                <span className="font-bold text-foreground">{userStats.completed}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5 font-medium text-muted-foreground">
                  <span className="w-2 h-2 rounded-full bg-cb-orange" /> Attempted
                </span>
                <span className="font-bold text-foreground">{userStats.attempted}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5 font-medium text-muted-foreground">
                  <span className="w-2 h-2 rounded-full bg-muted-foreground/20" /> Todo
                </span>
                <span className="font-bold text-foreground">{userStats.todo}</span>
              </div>
            </div>
          </div>
        )}

        <div className="p-2 border-t border bg-muted/20 flex flex-col gap-1">
          {user.role === "admin" && (
            <DropdownMenuItem asChild>
              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs font-bold border-primary/20 text-primary hover:bg-primary/10 cursor-pointer justify-center"
                onClick={() => router.push("/admin")}
              >
                Admin Panel
              </Button>
            </DropdownMenuItem>
          )}
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
