"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Upload, ArrowLeft, List } from "lucide-react";

export default function AdminDashboardPage() {
  const router = useRouter();
  const { user } = useAuth();

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">
          Welcome, {user?.username || user?.name || "Admin"}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl">
        <Card
          className="hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer"
          onClick={() => router.push("/admin/questions")}
        >
          <CardContent className="p-6 flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-violet-50 flex items-center justify-center">
              <List size={24} className="text-violet-600" />
            </div>
            <div>
              <p className="font-bold text-gray-800">All Questions</p>
              <p className="text-xs text-gray-500">View, edit &amp; manage questions</p>
            </div>
          </CardContent>
        </Card>

        <Card
          className="hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer"
          onClick={() => router.push("/admin/upload")}
        >
          <CardContent className="p-6 flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-indigo-50 flex items-center justify-center">
              <Upload size={24} className="text-indigo-600" />
            </div>
            <div>
              <p className="font-bold text-gray-800">Add a Question</p>
              <p className="text-xs text-gray-500">Add a new question to a module</p>
            </div>
          </CardContent>
        </Card>

        <Card
          className="hover:shadow-md hover:border-gray-300 transition-all cursor-pointer"
          onClick={() => router.push("/")}
        >
          <CardContent className="p-6 flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-gray-100 flex items-center justify-center">
              <ArrowLeft size={24} className="text-gray-600" />
            </div>
            <div>
              <p className="font-bold text-gray-800">Practice Room</p>
              <p className="text-xs text-gray-500">Back to the learner dashboard</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
