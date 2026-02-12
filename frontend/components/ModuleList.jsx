"use client";

import { useEffect, useState } from "react";
import { updateModule } from "@/services/api";
import api from "@/services/api";
import { Trash2, Pencil } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

const SORT_ORDER_IDS = ["python", "math_stats", "ml", "dl", "nlp", "genai", "agentic"];

function slugify(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "_")
    .replace(/^-+|-+$/g, "");
}

const sortModules = (modules) => {
  return [...modules].sort((a, b) => {
    const idA = a.id.toLowerCase();
    const idB = b.id.toLowerCase();
    const indexA = SORT_ORDER_IDS.indexOf(idA);
    const indexB = SORT_ORDER_IDS.indexOf(idB);
    if (indexA !== -1 && indexB !== -1) return indexA - indexB;
    if (indexA !== -1) return -1;
    if (indexB !== -1) return 1;
    return a.name.localeCompare(b.name);
  });
};

export default function ModuleList({ onSelectModule }) {
  const [modules, setModules] = useState([]);
  const { user } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newModule, setNewModule] = useState({ id: "", name: "", base_image: "python-image" });
  const [isIdAuto, setIsIdAuto] = useState(true);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    api
      .get("/modules/")
      .then((res) => {
        setModules(sortModules(res.data));
      })
      .catch((err) => console.error(err));
  }, []);

  const handleEdit = (e, module) => {
    e.stopPropagation();
    const cleanName = module.name.replace(/practice/gi, "").trim();
    setNewModule({ ...module, name: cleanName });
    setIsIdAuto(false);
    setIsEditing(true);
    setShowCreateModal(true);
  };

  const handleNameChange = (val) => {
    const updates = { ...newModule, name: val };
    if (isIdAuto) updates.id = slugify(val);
    setNewModule(updates);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      if (isEditing) {
        const updated = await updateModule(newModule.id, { name: newModule.name, base_image: newModule.base_image });
        setModules((prev) => sortModules(prev.map((mod) => (mod.id === updated.id ? updated : mod))));
      } else {
        const created = await api.post("/modules/", newModule);
        setModules((prev) => sortModules([...prev, created.data]));
      }
      setShowCreateModal(false);
      setNewModule({ id: "", name: "", base_image: "python-image" });
      setIsIdAuto(true);
      setIsEditing(false);
    } catch (err) {
      console.error("Failed to save module", err);
      alert(isEditing ? "Failed to update module" : "Failed to create module (ID must be unique)");
    }
  };

  return (
    <div>
      {user?.role === "admin" && (
        <div className="flex justify-end mb-4">
          <Button onClick={() => setShowCreateModal(true)} className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 shadow-lg font-bold text-sm">
            + Create Module
          </Button>
        </div>
      )}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="sm:max-w-[24rem]">
          <DialogHeader>
            <DialogTitle>{isEditing ? "Edit Module" : "Create New Module"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreate}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input
                  type="text"
                  required
                  placeholder="e.g. Data Science Basics"
                  value={newModule.name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label className="flex justify-between">
                  <span>ID (URL Slug)</span>
                  {isIdAuto && <span className="text-xs text-indigo-500 font-normal">Auto-generating...</span>}
                </Label>
                <Input
                  type="text"
                  required
                  value={newModule.id}
                  onChange={(e) => {
                    setNewModule({ ...newModule, id: e.target.value });
                    setIsIdAuto(false);
                  }}
                  className={`w-full ${isIdAuto || isEditing ? "bg-gray-50 text-gray-500" : ""}`}
                  disabled={isEditing}
                />
                <p className="text-[10px] text-gray-400">This ID will be used in URLs and CSV files.</p>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)}>
                Cancel
              </Button>
              <Button type="submit">{isEditing ? "Update" : "Create"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {modules.map((module) => (
          <div
            key={module.id}
            onClick={() => onSelectModule(module.id)}
            className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm hover:shadow-xl hover:shadow-indigo-500/10 hover:-translate-y-1 transition-all duration-300 cursor-pointer group relative"
          >
            {user?.role === "admin" && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute top-4 right-4 p-2 text-gray-400 hover:text-indigo-500 hover:bg-indigo-50 rounded-full z-10"
                title="Edit Module"
                onClick={(e) => handleEdit(e, module)}
              >
                <Pencil size={16} />
              </Button>
            )}
            <div className="h-12 w-12 rounded-lg bg-blue-50 flex items-center justify-center mb-4 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
              {module.name.replace(/practice/gi, "").trim()}
            </h3>
            <p className="text-sm text-gray-500 mt-2">Master {module.name.replace(/practice/gi, "").trim()} with hands-on challenges</p>
          </div>
        ))}
      </div>
    </div>
  );
}
