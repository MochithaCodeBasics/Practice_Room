"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Mail } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { requestPasswordReset } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const success = await requestPasswordReset(email);
      if (success) setSubmitted(true);
      else setError("Failed to send reset email. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Card className="max-w-[400px] w-full border-gray-100 text-center">
          <CardContent className="pt-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-green-600" />
            </div>
            <h1 className="text-xl font-bold text-gray-800 mb-2">Check your email</h1>
            <p className="text-gray-600 text-sm">
              If an account exists for <strong>{email}</strong>, we&apos;ve sent a password reset link.
            </p>
            <p className="text-gray-500 text-xs mt-4 mb-6">Didn&apos;t receive the email? Check your spam folder or try again.</p>
            <Link href="/login" className="text-[#3c5e6e] text-sm hover:underline">Back to Login</Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="max-w-[400px] w-full border-gray-100 shadow-sm">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <img src="/assets/logo.png" alt="Logo" className="h-10 w-auto" />
          </div>
          <CardTitle className="text-xl font-bold text-gray-800">Reset Password</CardTitle>
          <p className="text-gray-500 text-sm mt-2">Enter your email to receive a reset link</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email Address" required autoComplete="email" className="bg-gray-50 border-gray-200" />
            </div>
            {error && <div className="text-red-500 text-sm text-center">{error}</div>}
            <Button type="submit" disabled={isSubmitting} className={`w-full ${isSubmitting ? "bg-gray-400 cursor-not-allowed" : "bg-[#405c68] hover:bg-[#344b55]"} text-white font-medium`}>
              {isSubmitting ? "Sending..." : "Send Reset Link"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center pt-4 border-t">
          <Link href="/login" className="text-[#3c5e6e] text-sm hover:underline">Back to Login</Link>
        </CardFooter>
      </Card>
    </div>
  );
}
