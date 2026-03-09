"use client";

import { signIn } from "next-auth/react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface AuthPopupProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const INSPIRATIONAL_QUOTES = [
  {
    quote: "The only way to learn is to do. Not watch. Not read. Do.",
    author: "Codebasics",
  },
  {
    quote: "Real projects beat 100 tutorials. Every time.",
    author: "Codebasics",
  },
  {
    quote: "First, solve the problem. Then, write the code.",
    author: "John Johnson",
  },
  {
    quote: "The beautiful thing about learning is that nobody can take it away from you.",
    author: "B.B. King",
  },
  {
    quote: "Code is like humor. When you have to explain it, it's bad.",
    author: "Cory House",
  },
];

function getRandomQuote() {
  return INSPIRATIONAL_QUOTES[Math.floor(Math.random() * INSPIRATIONAL_QUOTES.length)];
}

export default function AuthPopup({ open, onOpenChange }: AuthPopupProps) {
  const quote = getRandomQuote();

  const handleSignIn = () => {
    signIn("codebasics", { callbackUrl: window.location.href });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="text-center sm:text-center">
          <DialogTitle className="text-xl font-display font-bold text-foreground uppercase">
            Your Code. Your Progress.
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground mt-1">
            Sign in to run code, track your streak, and save progress across sessions.
          </DialogDescription>
        </DialogHeader>

        <div className="my-4 p-5 bg-primary/10 rounded-xl border border-primary/20">
          <p className="text-sm text-foreground/80 italic leading-relaxed text-center">
            &ldquo;{quote.quote}&rdquo;
          </p>
          <p className="text-xs text-primary font-semibold mt-2 text-center">
            &mdash; {quote.author}
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <Button
            onClick={handleSignIn}
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-display font-bold uppercase tracking-wide py-3 text-sm"
          >
            Continue with Codebasics →
          </Button>
          <p className="text-[11px] text-muted-foreground text-center">
            Redirects to codebasics.io to authenticate — you&apos;ll be brought back automatically.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
