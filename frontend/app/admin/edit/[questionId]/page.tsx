"use client";

import React, { useState, useEffect, ChangeEvent } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { Module } from "@/types";

export default function AdminEditQuestionPage() {
  const router = useRouter();
  const { questionId } = useParams<{ questionId: string }>();
  useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<{ type: string; message: string }>({ type: "", message: "" });
  const [modules, setModules] = useState<Module[]>([]);
  const [formData, setFormData] = useState({
    title: "",
    difficulty: "Easy",
    module_id: "",
    tags: "",
    topic: "",
    is_active: true,
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
  const [existingFiles, setExistingFiles] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modulesRes, questionRes] = await Promise.all([
          api.get("/modules/"),
          api.get(`/questions/${questionId}`),
        ]);
        setModules(modulesRes.data);
        const q = questionRes.data;
        setFormData({
          title: q.title || "",
          difficulty: q.difficulty || "Easy",
          module_id: q.module_id || "",
          tags: q.tags || "",
          topic: q.topic || "",
          is_active: q.is_active ?? true,
        });
        if (q.data_files?.length > 0) setExistingFiles(q.data_files);
      } catch (err) {
        console.error("Failed to fetch data", err);
        setStatus({ type: "error", message: "Failed to load question data" });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [questionId]);

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
    setSaving(true);
    setStatus({ type: "", message: "" });
    const submitData = new FormData();
    submitData.append("title", formData.title);
    submitData.append("difficulty", formData.difficulty);
    submitData.append("topic", formData.topic);
    submitData.append("tags", formData.tags);
    submitData.append("is_active", String(formData.is_active));
    if (files.question_py) submitData.append("question_py", files.question_py);
    if (files.validator_py) submitData.append("validator_py", files.validator_py);
    if (files.data_files?.length > 0) {
      files.data_files.forEach((file) => submitData.append("data_files", file));
    }
    try {
      await api.put(`/v1/admin/questions/${questionId}`, submitData, { headers: { "Content-Type": "multipart/form-data" } });
      setStatus({ type: "success", message: "Question updated successfully!" });
    } catch (error: any) {
      console.error(error);
      setStatus({ type: "error", message: error.response?.data?.detail || "Failed to update question" });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Skeleton className="h-12 w-12 rounded-full" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold uppercase text-foreground">Edit Question</h1>
          <p className="text-muted-foreground text-sm mt-1">Editing: {questionId}</p>
        </div>
        <Button variant="outline" onClick={() => router.push("/")} className="border text-primary hover:bg-primary/10">
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
                <Input name="title" value={formData.title} onChange={handleTextChange} required className="w-full" />
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
              <div className="space-y-2">
                <Label>Topic</Label>
                <Input name="topic" value={formData.topic} onChange={handleTextChange} className="w-full" />
              </div>
              <div className="space-y-2">
                <Label>Tags (comma separated)</Label>
                <Input name="tags" value={formData.tags} onChange={handleTextChange} className="w-full" />
              </div>
              <div className="md:col-span-2 flex items-center justify-between p-3 rounded-lg border bg-muted/20">
                <div>
                  <p className="text-sm font-medium text-foreground">Active</p>
                  <p className="text-xs text-muted-foreground">Inactive questions are hidden from learners</p>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={formData.is_active}
                  onClick={() => setFormData((prev) => ({ ...prev, is_active: !prev.is_active }))}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${formData.is_active ? "bg-primary" : "bg-muted-foreground/30"}`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${formData.is_active ? "translate-x-6" : "translate-x-1"}`} />
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border">
          <CardHeader>
            <CardTitle className="text-lg border-b pb-2">Files</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted/30 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-foreground mb-3">Current Files</h3>
              <div className="flex flex-wrap gap-2">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-cb-teal/10 text-cb-teal">{"\u2713"} question.py</span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-cb-teal/10 text-cb-teal">{"\u2713"} validator.py</span>
                {existingFiles.map((file, idx) => (
                  <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                    {file}
                  </span>
                ))}
              </div>
            </div>
            <p className="text-sm text-muted-foreground">Upload new files only if you want to replace the existing ones.</p>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <Label>Replace question.py</Label>
                  <a href="/samples/question.py" download className="text-xs text-primary hover:text-primary/80 underline underline-offset-2">Download sample</a>
                </div>
                <Input type="file" name="question_py" accept=".py" onChange={handleFileChange} className="cursor-pointer" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <Label>Replace validator.py</Label>
                  <a href="/samples/validator.py" download className="text-xs text-primary hover:text-primary/80 underline underline-offset-2">Download sample</a>
                </div>
                <Input type="file" name="validator_py" accept=".py" onChange={handleFileChange} className="cursor-pointer" />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Add/Replace Data Files</Label>
              <Input type="file" name="data_files" multiple onChange={handleFileChange} className="cursor-pointer" />
            </div>
          </CardContent>
        </Card>

        {status.message && (
          <div className={`p-4 rounded-lg text-center ${status.type === "success" ? "bg-cb-teal/10 text-cb-teal" : "bg-destructive/10 text-destructive"}`}>
            {status.message}
          </div>
        )}

        <div className="flex justify-end gap-4 pt-4">
          <Button type="button" variant="secondary" onClick={() => router.push("/")}>
            Cancel
          </Button>
          <Button type="submit" disabled={saving} className="bg-primary hover:bg-primary/90 font-bold">
            {saving ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    </div>
  );
}
