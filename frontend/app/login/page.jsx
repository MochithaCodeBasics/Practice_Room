"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Eye, EyeOff } from "lucide-react";
import { PracticeRoomLogo, PracticeRoomText } from "@/components/Branding";

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginForm />
    </Suspense>
  );
}

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const { login, user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const rawMessage = searchParams.get("message");
  const successMessage = rawMessage ? decodeURIComponent(rawMessage) : null;

  useEffect(() => {
    if (user) {
      if (user.role === "admin") {
        router.replace("/admin/login");
      } else {
        router.replace("/dashboard");
      }
    }
  }, [user, router]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const success = await login(username, password);
    if (success) {
      const role = typeof window !== "undefined" ? localStorage.getItem("role") : null;
      if (role === "learner" || !role) {
        router.push("/dashboard");
      } else if (role === "admin") {
        setError("Please use the Admin login page");
        return;
      }
    } else {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="max-w-[400px] w-full border-gray-100 shadow-sm">
        <CardHeader className="text-center pb-2">
          <PracticeRoomLogo variant="vertical" logoSize="h-10" className="text-3xl" />
        </CardHeader>
        <CardContent className="space-y-4">
          {successMessage && (
            <div className="text-green-600 text-sm text-center mb-4 bg-green-50 p-2 rounded-md">
              {successMessage}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
            <div className="space-y-2">
              <Label htmlFor="learner-username">Username or E-mail</Label>
              <Input
                id="learner-username"
                name="learner-username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username or E-mail"
                required
                autoComplete="off"
                className="bg-gray-50 border-gray-200 focus:ring-gray-300 focus:bg-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="learner-password">Password</Label>
              <div className="relative">
                <Input
                  id="learner-password"
                  name="learner-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  required
                  autoComplete="new-password"
                  className="pr-10 bg-gray-50 border-gray-200 focus:ring-gray-300 focus:bg-white"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 text-gray-400 hover:text-gray-600"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </Button>
              </div>
            </div>
            {error && (
              <div className="text-red-500 text-sm text-center">{error}</div>
            )}
            <Button
              type="submit"
              className="w-full bg-[#405c68] hover:bg-[#344b55] text-white font-medium"
            >
              Sign In
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-between items-center pt-4 border-t">
          <Link href="/forgot-password" className="text-[#3c5e6e] text-sm hover:underline" title="Check your email for reset link">
            Forgot Password?
          </Link>
          <Link href="/signup" className="text-[#3c5e6e] text-sm hover:underline">
            Sign Up
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
