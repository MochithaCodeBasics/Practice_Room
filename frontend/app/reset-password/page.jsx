"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { XCircle, CheckCircle } from "lucide-react";

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { verifyPasswordReset } = useAuth();
  const router = useRouter();

  const passwordChecks = {
    length: newPassword.length >= 8,
    uppercase: /[A-Z]/.test(newPassword),
    lowercase: /[a-z]/.test(newPassword),
    number: /[0-9]/.test(newPassword),
  };
  const isPasswordValid = Object.values(passwordChecks).every(Boolean);

  useEffect(() => {
    if (!token) setError("Invalid reset link. Please request a new password reset.");
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!isPasswordValid) {
      setError("Password does not meet requirements");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setIsSubmitting(true);
    try {
      const result = await verifyPasswordReset(token, newPassword);
      if (result) {
        setSuccess(true);
        setTimeout(() => router.push(`/login?message=${encodeURIComponent("Password reset successfully! Please login.")}`), 2000);
      } else {
        setError("Invalid or expired reset link. Please request a new password reset.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Card className="max-w-[400px] w-full border-gray-100 text-center">
          <CardContent className="pt-8">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
            <h1 className="text-xl font-bold text-gray-800 mb-2">Invalid Link</h1>
            <p className="text-gray-600 text-sm mb-4">This password reset link is invalid or has expired.</p>
            <Link href="/forgot-password" className="text-[#3c5e6e] hover:underline">Request a new reset link</Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Card className="max-w-[400px] w-full border-gray-100 text-center">
          <CardContent className="pt-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h1 className="text-xl font-bold text-gray-800 mb-2">Password Reset!</h1>
            <p className="text-gray-600 text-sm">Redirecting to login...</p>
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
          <CardTitle className="text-xl font-bold text-gray-800">Set New Password</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <Input id="newPassword" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="New Password" required autoComplete="new-password" className="bg-gray-50 border-gray-200" />
              {newPassword && (
                <div className="mt-2 text-xs space-y-1">
                  <p className={passwordChecks.length ? "text-green-600" : "text-gray-400"}>{passwordChecks.length ? "✓" : "○"} At least 8 characters</p>
                  <p className={passwordChecks.uppercase ? "text-green-600" : "text-gray-400"}>{passwordChecks.uppercase ? "✓" : "○"} One uppercase letter</p>
                  <p className={passwordChecks.lowercase ? "text-green-600" : "text-gray-400"}>{passwordChecks.lowercase ? "✓" : "○"} One lowercase letter</p>
                  <p className={passwordChecks.number ? "text-green-600" : "text-gray-400"}>{passwordChecks.number ? "✓" : "○"} One number</p>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmNewPassword">Confirm Password</Label>
              <Input id="confirmNewPassword" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Confirm Password" required autoComplete="new-password" className="bg-gray-50 border-gray-200" />
              {confirmPassword && (
                <p className={`mt-2 text-xs ${newPassword === confirmPassword ? "text-green-600" : "text-red-500"}`}>
                  {newPassword === confirmPassword ? "✓ Passwords match" : "✗ Passwords do not match"}
                </p>
              )}
            </div>
            {error && <div className="text-red-500 text-sm text-center bg-red-50 p-2 rounded">{error}</div>}
            <Button type="submit" disabled={isSubmitting} className={`w-full ${isSubmitting ? "bg-gray-400 cursor-not-allowed" : "bg-[#405c68] hover:bg-[#344b55]"} text-white font-medium`}>
              {isSubmitting ? "Resetting..." : "Reset Password"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
