"use client";

import { useState, useEffect, Suspense, FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Eye, EyeOff } from "lucide-react";
import { PracticeRoomLogo, PracticeRoomText } from "@/components/Branding";

export default function AdminLoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AdminLoginForm />
    </Suspense>
  );
}

function AdminLoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const { adminLogin, user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const successMessage = searchParams.get("message") || null;

  useEffect(() => {
    if (user) router.replace("/");
  }, [user, router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    const success = await adminLogin(username, password);
    if (success) router.push("/");
    else setError("Invalid credentials or access denied");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 p-4">
      <Card className="max-w-[400px] w-full border-gray-100 shadow-xl">
        <CardHeader className="text-center pb-2">
          <PracticeRoomLogo variant="vertical" logoSize="h-10" />
          <CardTitle className="text-3xl font-black text-gray-900 tracking-tight mt-4">Admin Portal</CardTitle>
          <div className="text-gray-500 mt-2 flex items-center justify-center gap-1">
            Sign in to manage the <PracticeRoomText className="text-base" />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {successMessage && (
            <div className="text-green-600 text-sm text-center mb-4 bg-green-50 p-2 rounded"> {successMessage}</div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="admin-username">Admin Username</Label>
              <Input id="admin-username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Admin Username" required className="bg-gray-50 border-gray-200 focus:ring-slate-500" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="admin-password">Password</Label>
              <div className="relative">
                <Input id="admin-password" type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" required className="pr-10 bg-gray-50 border-gray-200 focus:ring-slate-500" />
                <Button type="button" variant="ghost" size="icon" className="absolute right-0 top-0 h-full px-3 text-gray-400 hover:text-gray-600" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Hide password" : "Show password"}>
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </Button>
              </div>
            </div>
            {error && <div className="text-red-500 text-sm text-center">{error}</div>}
            <Button type="submit" className="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium">
              Login
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
