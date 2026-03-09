"use client";

import React, { useState, useEffect, ChangeEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Module } from "@/types";

export default function AdminUploadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preSelectedModule = searchParams.get("moduleId");
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{ type: string; message: string }>({ type: "", message: "" });
  const [modules, setModules] = useState<Module[]>([]);
  const [formData, setFormData] = useState({
    title: "",
    difficulty: "Easy",
    module_id: preSelectedModule || "",
    tags: "",
    topic: "",
  });
  const [files, setFiles] = useState<{
    question_py: File | null;
    validator_py: File | null;
    data_files: File[];
  }>({
    question_py: null,
    validator_py: null,
    data_files: [],
  });

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const res = await api.get("/modules/");
        setModules(res.data);
        if (!preSelectedModule && res.data.length > 0) {
          setFormData((prev) => ({ ...prev, module_id: res.data[0].id }));
        }
      } catch (err) {
        console.error("Failed to fetch modules", err);
      }
    };
    fetchModules();
  }, [preSelectedModule]);

  const handleTextChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, files: selectedFiles } = e.target;
    if (!selectedFiles) return;
    if (name === "data_files") {
      setFiles((prev) => ({ ...prev, data_files: Array.from(selectedFiles) }));
    } else {
      setFiles((prev) => ({ ...prev, [name]: selectedFiles[0] }));
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!files.question_py) {
      setStatus({ type: "error", message: "question.py file is required" });
      return;
    }
    if (!files.validator_py) {
      setStatus({ type: "error", message: "validator.py file is required" });
      return;
    }
    setLoading(true);
    setStatus({ type: "", message: "" });
    const submitData = new FormData();
    submitData.append("title", formData.title);
    submitData.append("difficulty", formData.difficulty.toLowerCase());
    submitData.append("module_id", formData.module_id);
    submitData.append("topic", formData.topic);
    submitData.append("tags", formData.tags);
    submitData.append("question_py", files.question_py);
    submitData.append("validator_py", files.validator_py);
    if (files.data_files.length > 0) {
      files.data_files.forEach((file) => submitData.append("data_files", file));
    }
    try {
      await api.post("/v1/admin/questions", submitData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus({ type: "success", message: "Question created successfully!" });
    } catch (error: any) {
      console.error(error);
      setStatus({ type: "error", message: error.response?.data?.detail || "Failed to create question" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold uppercase text-foreground">Add New Question</h1>
          <p className="text-muted-foreground text-sm mt-1">Logged in as {user?.username}</p>
        </div>
        <Button variant="outline" onClick={() => router.push("/admin")} className="border text-primary hover:bg-primary/10">
          Back to Dashboard
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <Card className="border">
          <CardHeader>
            <CardTitle className="text-lg border-b pb-2">Question Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2 space-y-2">
                <Label>Question Title</Label>
                <Input name="title" value={formData.title} onChange={handleTextChange} placeholder="e.g. Analyze Customer Churn" required className="w-full" />
              </div>
              <div className="space-y-2">
                <Label>Module</Label>
                <select
                  name="module_id"
                  value={formData.module_id}
                  onChange={handleTextChange}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  {modules.map((mod) => (
                    <option key={mod.id} value={mod.id}>{mod.name}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Difficulty</Label>
                <select
                  name="difficulty"
                  value={formData.difficulty}
                  onChange={handleTextChange}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option>Easy</option>
                  <option>Medium</option>
                  <option>Hard</option>
                </select>
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label>Topic</Label>
                <Input name="topic" value={formData.topic} onChange={handleTextChange} placeholder="e.g. Statistics" className="w-full" />
              </div>
              <div className="space-y-2">
                <Label>Tags (comma separated)</Label>
                <Input name="tags" value={formData.tags} onChange={handleTextChange} placeholder="pandas, basic, plot" className="w-full" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border">
          <CardHeader>
            <CardTitle className="text-lg border-b pb-2">Files</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <Label>question.py <span className="text-red-500">*</span></Label>
                  <a href="/samples/question.py" download className="text-xs text-primary hover:text-primary/80 underline underline-offset-2">Download sample</a>
                </div>
                <Input type="file" name="question_py" accept=".py" onChange={handleFileChange} className="cursor-pointer" required />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <Label>validator.py <span className="text-red-500">*</span></Label>
                  <a href="/samples/validator.py" download className="text-xs text-primary hover:text-primary/80 underline underline-offset-2">Download sample</a>
                </div>
                <Input type="file" name="validator_py" accept=".py" onChange={handleFileChange} className="cursor-pointer" required />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Data Files (Optional)</Label>
              <Input type="file" name="data_files" multiple onChange={handleFileChange} className="cursor-pointer" />
            </div>
          </CardContent>
        </Card>

        {status.message && (
          <div className={`p-4 rounded-lg text-center ${status.type === "success" ? "bg-cb-teal/10 text-cb-teal" : "bg-destructive/10 text-destructive"}`}>
            {status.message}
          </div>
        )}

        <div className="flex justify-end pt-4">
          <Button type="submit" disabled={loading} className="px-8 py-4 bg-primary hover:bg-primary/90 text-lg font-bold" size="lg">
            {loading ? "Creating Question..." : "Create Question"}
          </Button>
        </div>
      </form>
    </div>
  );
}
