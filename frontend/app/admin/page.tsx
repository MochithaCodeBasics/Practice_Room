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
        <h1 className="text-3xl font-display font-bold uppercase text-foreground">Admin Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Welcome, {user?.username || user?.name || "Admin"}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl">
        <Card
          className="hover:shadow-md hover:border-primary/30 transition-all cursor-pointer"
          onClick={() => router.push("/admin/questions")}
        >
          <CardContent className="p-6 flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-cb-purple/10 flex items-center justify-center">
              <List size={24} className="text-cb-purple" />
            </div>
            <div>
              <p className="font-bold text-foreground">All Questions</p>
              <p className="text-xs text-muted-foreground">View, edit &amp; manage questions</p>
            </div>
          </CardContent>
        </Card>

        <Card
          className="hover:shadow-md hover:border-primary/30 transition-all cursor-pointer"
          onClick={() => router.push("/admin/upload")}
        >
          <CardContent className="p-6 flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <Upload size={24} className="text-primary" />
            </div>
            <div>
              <p className="font-bold text-foreground">Add a Question</p>
              <p className="text-xs text-muted-foreground">Add a new question to a module</p>
            </div>
          </CardContent>
        </Card>

        <Card
          className="hover:shadow-md hover:border-primary/30 transition-all cursor-pointer"
          onClick={() => router.push("/")}
        >
          <CardContent className="p-6 flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center">
              <ArrowLeft size={24} className="text-muted-foreground" />
            </div>
            <div>
              <p className="font-bold text-foreground">Practice Room</p>
              <p className="text-xs text-muted-foreground">Back to the learner dashboard</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
