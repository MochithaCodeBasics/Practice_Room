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
      const newFiles = Array.from(selectedFiles);
      setFiles((prev) => {
        // Filter out duplicates based on name
        const uniqueNewFiles = newFiles.filter(
          (nf) => !prev.data_files.some((pf) => pf.name === nf.name)
        );
        return { ...prev, data_files: [...prev.data_files, ...uniqueNewFiles] };
      });
      // Reset input value to allow selecting the same file again if needed (though we filter duplicates)
      e.target.value = "";
    } else {
      setFiles((prev) => ({ ...prev, [name]: selectedFiles[0] }));
    }
  };

  const removeDataFile = (index) => {
    setFiles((prev) => ({
      ...prev,
      data_files: prev.data_files.filter((_, i) => i !== index),
    }));
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

  const [activeTab, setActiveTab] = useState("single");
  const [bulkFile, setBulkFile] = useState(null);
  const [bulkStatus, setBulkStatus] = useState(null);

  const handleBulkUpload = async (e) => {
    e.preventDefault();
    if (!bulkFile) return;

    setLoading(true);
    setBulkStatus(null);

    const submitData = new FormData();
    submitData.append("file", bulkFile);

    try {
      const res = await api.post("/v1/admin/questions/bulk", submitData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setBulkStatus({ type: "success", data: res.data });
    } catch (err) {
      console.error(err);
      setBulkStatus({ type: "error", message: err.response?.data?.detail || "Upload failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Add New Question</h1>
          <p className="text-gray-500 text-sm mt-1">Logged in as {user?.username}</p>
        </div>
        <Button variant="outline" onClick={() => router.back()} className="border-indigo-100 text-indigo-600 hover:bg-indigo-50">
          Back
        </Button>
      </div>

      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-8 w-fit">
        <button
          onClick={() => setActiveTab("single")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "single" ? "bg-white text-indigo-600 shadow-sm" : "text-gray-500 hover:text-gray-700"
            }`}
        >
          Single Question
        </button>
        <button
          onClick={() => setActiveTab("bulk")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "bulk" ? "bg-white text-indigo-600 shadow-sm" : "text-gray-500 hover:text-gray-700"
            }`}
        >
          Bulk Upload (ZIP)
        </button>
      </div>

      {activeTab === "single" ? (
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
              <Label className="block mb-2">Upload Files (CSV, TXT, PT, etc.)</Label>

              <div className="space-y-4">
                <Input
                  type="file"
                  name="data_files"
                  multiple
                  accept=".csv,.txt,.json,.py,.pt,.xlsx"
                  onChange={handleFileChange}
                  className="cursor-pointer"
                />

                {files.data_files.length > 0 && (
                  <div className="bg-gray-50 p-4 rounded-md space-y-2">
                    <p className="text-sm font-medium text-gray-700">Selected Files ({files.data_files.length}):</p>
                    <ul className="space-y-2">
                      {files.data_files.map((file, idx) => (
                        <li key={idx} className="flex items-center justify-between text-sm bg-white p-2 rounded border">
                          <span className="truncate max-w-[200px]">{file.name}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeDataFile(idx)}
                            className="text-red-500 hover:text-red-700 h-8 px-2"
                          >
                            Remove
                          </Button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-400 mt-1">Select files to add them to the list. You can add multiple files from different folders.</p>
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
      ) : (
        <div className="space-y-6 max-w-3xl mx-auto">
          <Card className="border-gray-100">
            <CardHeader>
              <CardTitle className="text-xl">Bulk Upload Questions</CardTitle>
              <p className="text-gray-500">Upload a ZIP file containing questions and metadata.</p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-md text-sm text-blue-800">
                <div className="flex justify-between items-start mb-2">
                  <p className="font-semibold">ZIP File Structure:</p>
                  <Button
                    variant="link"
                    className="h-auto p-0 text-blue-700 font-bold hover:text-blue-900 flex items-center gap-1"
                    onClick={async () => {
                      try {
                        const response = await api.get('/v1/admin/questions/sample-template', {
                          responseType: 'blob'
                        });
                        const url = window.URL.createObjectURL(new Blob([response.data]));
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', 'sample_questions.zip');
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        window.URL.revokeObjectURL(url);
                      } catch (err) {
                        console.error("Download failed", err);
                        alert("Failed to download template. Please check the console.");
                      }
                    }}
                  >
                    <span>Download Sample ZIP Template</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
                  </Button>
                </div>

                <pre className="bg-blue-100/50 p-3 rounded text-xs font-mono mb-4 text-blue-900">
                  {`questions.zip
├── metadata.xlsx
├── question_folder_1/
│   ├── question.py
│   ├── validator.py
│   └── data.csv (optional)
└── question_folder_2/
    ├── question.py
    └── validator.py`}
                </pre>

                <p className="font-semibold mb-2">Metadata Excel Columns:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li><strong>Title</strong>: e.g., Analyze Customer Churn</li>
                  <li><strong>Module</strong>: <code>python</code>, <code>math_stats</code>, <code>nlp</code>, <code>ml</code>, <code>dl</code>, <code>genai</code>, <code>agentic</code></li>
                  <li><strong>Difficulty</strong>: Easy, Medium, Hard</li>
                  <li><strong>Topic</strong>: e.g., Statistics</li>
                  <li><strong>Tags</strong>: e.g., pandas, array</li>
                  <li><strong>Folder Name</strong>: Name of the folder in the ZIP (Required)</li>
                </ul>
              </div>

              <div className="border-2 border-dashed border-gray-200 rounded-lg p-12 flex flex-col items-center justify-center text-center hover:border-indigo-300 transition-colors bg-gray-50">
                <Input
                  type="file"
                  accept=".zip"
                  onChange={(e) => setBulkFile(e.target.files[0])}
                  className="cursor-pointer max-w-xs"
                />
                <p className="mt-4 text-xs text-gray-400">Supported format: .zip (containing metadata.xlsx and folders)</p>
              </div>

              <Button
                onClick={handleBulkUpload}
                disabled={loading || !bulkFile}
                className="w-full py-6 text-lg bg-indigo-600 hover:bg-indigo-700"
              >
                {loading ? "Processing Upload..." : "Upload Questions"}
              </Button>
            </CardContent>
          </Card>

          {bulkStatus && (
            <Card className={`border ${bulkStatus.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
              <CardContent className="p-6">
                {bulkStatus.type === 'success' ? (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <div className="h-8 w-8 rounded-full bg-green-200 flex items-center justify-center text-green-700 font-bold">✓</div>
                      <h3 className="font-bold text-green-800 text-lg">Upload Complete</h3>
                    </div>
                    <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                      <div className="bg-white p-3 rounded shadow-sm">
                        <p className="text-xs text-gray-500 uppercase">Total</p>
                        <p className="text-xl font-bold text-gray-800">{bulkStatus.data.total}</p>
                      </div>
                      <div className="bg-white p-3 rounded shadow-sm">
                        <p className="text-xs text-gray-500 uppercase">Success</p>
                        <p className="text-xl font-bold text-green-600">{bulkStatus.data.success}</p>
                      </div>
                      <div className="bg-white p-3 rounded shadow-sm">
                        <p className="text-xs text-gray-500 uppercase">Failed</p>
                        <p className="text-xl font-bold text-red-600">{bulkStatus.data.failed}</p>
                      </div>
                    </div>

                    {bulkStatus.data.errors.length > 0 && (
                      <div className="bg-white p-4 rounded border border-red-100 max-h-60 overflow-y-auto">
                        <p className="font-semibold text-red-700 mb-2">Errors:</p>
                        <ul className="space-y-1 text-sm text-red-600">
                          {bulkStatus.data.errors.map((err, i) => <li key={i}>• {err}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-red-800 font-medium">{bulkStatus.message}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
