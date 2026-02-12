"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export default function SignupPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const { signup } = useAuth();
  const router = useRouter();

  const passwordChecks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
  };
  const isPasswordValid = Object.values(passwordChecks).every(Boolean);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!isPasswordValid) {
      setError("Password does not meet requirements");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    const success = await signup(username, email, password);
    if (success) {
      router.push(`/login?message=${encodeURIComponent("Signup successful! Please login.")}`);
    } else {
      setError("Signup failed. Username or email might already be taken.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="max-w-[400px] w-full border-gray-100 shadow-sm">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <img src="/assets/logo.png" alt="Logo" className="h-10 w-auto" />
          </div>
          <CardTitle className="text-3xl font-extrabold tracking-tight text-slate-700">
            Practice <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Room</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
            <div className="space-y-2">
              <Label htmlFor="username_new">Username</Label>
              <Input id="username_new" name="username_new" type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" required autoComplete="off" className="bg-gray-50 border-gray-200" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" required autoComplete="new-password" className="bg-gray-50 border-gray-200" />
              {password && (
                <div className="mt-2 text-xs space-y-1">
                  <p className={passwordChecks.length ? "text-green-600" : "text-gray-400"}>{passwordChecks.length ? "✓" : "○"} At least 8 characters</p>
                  <p className={passwordChecks.uppercase ? "text-green-600" : "text-gray-400"}>{passwordChecks.uppercase ? "✓" : "○"} One uppercase letter</p>
                  <p className={passwordChecks.lowercase ? "text-green-600" : "text-gray-400"}>{passwordChecks.lowercase ? "✓" : "○"} One lowercase letter</p>
                  <p className={passwordChecks.number ? "text-green-600" : "text-gray-400"}>{passwordChecks.number ? "✓" : "○"} One number</p>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input id="confirmPassword" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Confirm Password" required autoComplete="new-password" className="bg-gray-50 border-gray-200" />
              {confirmPassword && (
                <p className={`mt-2 text-xs ${password === confirmPassword ? "text-green-600" : "text-red-500"}`}>
                  {password === confirmPassword ? "✓ Passwords match" : "✗ Passwords do not match"}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email_new">E-mail Address</Label>
              <Input id="email_new" name="email_new" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="E-mail Address" required autoComplete="off" className="bg-gray-50 border-gray-200" />
            </div>
            {error && <div className="text-red-500 text-sm text-center">{error}</div>}
            <Button type="submit" className="w-full bg-[#405c68] hover:bg-[#344b55] text-white font-medium">
              Sign Up
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center pt-4 border-t">
          <span className="text-gray-400 text-sm">Have an account? </span>
          <Link href="/login" className="text-[#3c5e6e] text-sm hover:underline ml-1">Sign In</Link>
        </CardFooter>
      </Card>
    </div>
  );
}
