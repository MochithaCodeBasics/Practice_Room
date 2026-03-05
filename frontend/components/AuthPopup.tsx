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
    quote: "Every expert was once a beginner.",
    author: "Helen Hayes",
  },
  {
    quote: "The only way to learn mathematics is to do mathematics.",
    author: "Paul Halmos",
  },
  {
    quote: "Code is like humor. When you have to explain it, it's bad.",
    author: "Cory House",
  },
  {
    quote: "First, solve the problem. Then, write the code.",
    author: "John Johnson",
  },
  {
    quote: "The beautiful thing about learning is that nobody can take it away from you.",
    author: "B.B. King",
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
            Sign in to continue
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground mt-1">
            Authentication is required to run code on the Practice Room.
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
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-3 text-sm"
          >
            Sign in with Codebasics
          </Button>
          <p className="text-[11px] text-muted-foreground text-center">
            You will be redirected to codebasics.io to authenticate.
            After signing in, you&apos;ll be brought back here automatically.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
