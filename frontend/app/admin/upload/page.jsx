"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminUploadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preSelectedModule = searchParams.get("moduleId");
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: "", message: "" });
  const [modules, setModules] = useState([]);
  const [formData, setFormData] = useState({
    title: "",
    difficulty: "Easy",
    module_id: preSelectedModule || "",
    tags: "",
    topic: "",
  });
  const [files, setFiles] = useState({
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

  const handleTextChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    const { name, files: selectedFiles } = e.target;
    if (name === "data_files") {
      setFiles((prev) => ({ ...prev, data_files: Array.from(selectedFiles) }));
    } else {
      setFiles((prev) => ({ ...prev, [name]: selectedFiles[0] }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: "", message: "" });
    const submitData = new FormData();
    Object.keys(formData).forEach((key) => submitData.append(key, formData[key]));
    if (files.question_py) submitData.append("question_py", files.question_py);
    if (files.validator_py) submitData.append("validator_py", files.validator_py);
    if (files.data_files?.length > 0) {
      files.data_files.forEach((file) => submitData.append("data_files", file));
    }
    try {
      await api.post("/v1/admin/questions", submitData, { headers: { "Content-Type": "multipart/form-data" } });
      setStatus({ type: "success", message: "Question created successfully!" });
    } catch (error) {
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
          <h1 className="text-3xl font-bold text-gray-800">Add New Question</h1>
          <p className="text-gray-500 text-sm mt-1">Logged in as {user?.username}</p>
        </div>
        <Button variant="outline" onClick={() => router.push("/dashboard")} className="border-indigo-100 text-indigo-600 hover:bg-indigo-50">
          Back to Dashboard
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <Card className="border-gray-100">
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
              <div className="space-y-2">
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="border-gray-100">
            <CardHeader>
              <CardTitle className="text-lg">question.py</CardTitle>
              <p className="text-xs text-gray-500">Defines the problem statement and stub.</p>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 flex flex-col items-center justify-center text-center hover:border-indigo-300 transition-colors">
                <Input type="file" name="question_py" accept=".py" onChange={handleFileChange} required className="cursor-pointer" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-gray-100">
            <CardHeader>
              <CardTitle className="text-lg">validator.py</CardTitle>
              <p className="text-xs text-gray-500">Logic to validate the user solution.</p>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 flex flex-col items-center justify-center text-center hover:border-indigo-300 transition-colors">
                <Input type="file" name="validator_py" accept=".py" onChange={handleFileChange} required className="cursor-pointer" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="border-gray-100">
          <CardHeader>
            <CardTitle className="text-lg border-b pb-2">Data Files (Optional)</CardTitle>
          </CardHeader>
          <CardContent>
            <Label className="block mb-2">Upload Files (CSV, TXT, etc.)</Label>
            <Input type="file" name="data_files" multiple onChange={handleFileChange} className="cursor-pointer" />
            <p className="text-xs text-gray-400 mt-1">Select one or more files.</p>
          </CardContent>
        </Card>

        {status.message && (
          <div className={`p-4 rounded-lg text-center ${status.type === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {status.message}
          </div>
        )}

        <div className="flex justify-end pt-4">
          <Button type="submit" disabled={loading} className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-lg font-bold" size="lg">
            {loading ? "Creating Question..." : "Create Question"}
          </Button>
        </div>
      </form>
    </div>
  );
}
