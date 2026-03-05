"use client";

import React, { useEffect, useState, FormEvent } from "react";
import { updateModule } from "@/services/api";
import api from "@/services/api";
import Link from "next/link";
import { Pencil } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import type { Module } from "@/types";

const SORT_ORDER_IDS = ["python", "math_stats", "ml", "dl", "nlp", "genai", "agentic"];
const ENABLE_MODULE_MANAGEMENT = false;

function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "_")
    .replace(/^-+|-+$/g, "");
}

const sortModules = (modules: Module[]): Module[] => {
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

interface NewModuleForm {
  id: string;
  name: string;
}

export default function ModuleList() {
  const [modules, setModules] = useState<Module[]>([]);
  const { user } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [newModule, setNewModule] = useState<NewModuleForm>({ id: "", name: "" });
  const [isIdAuto, setIsIdAuto] = useState<boolean>(true);
  const [isEditing, setIsEditing] = useState<boolean>(false);

  useEffect(() => {
    api
      .get<Module[]>("/modules/")
      .then((res) => {
        setModules(sortModules(res.data));
      })
      .catch((err) => console.error(err));
  }, []);

  const handleEdit = (e: React.MouseEvent, module: Module) => {
    if (!ENABLE_MODULE_MANAGEMENT) return;
    e.preventDefault();
    e.stopPropagation();
    const cleanName = module.name.replace(/practice/gi, "").trim();
    setNewModule({ id: module.id, name: cleanName });
    setIsIdAuto(false);
    setIsEditing(true);
    setShowCreateModal(true);
  };

  const handleNameChange = (val: string) => {
    const updates = { ...newModule, name: val };
    if (isIdAuto) updates.id = slugify(val);
    setNewModule(updates);
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!ENABLE_MODULE_MANAGEMENT) return;
    try {
      if (isEditing) {
        const updated = await updateModule(newModule.id, { name: newModule.name } as Partial<Module>);
        setModules((prev) => sortModules(prev.map((mod) => (mod.id === updated.id ? updated : mod))));
      } else {
        const created = await api.post<Module>("/modules/", newModule);
        setModules((prev) => sortModules([...prev, created.data]));
      }
      setShowCreateModal(false);
      setNewModule({ id: "", name: "" });
      setIsIdAuto(true);
      setIsEditing(false);
    } catch (err) {
      console.error("Failed to save module", err);
      alert(isEditing ? "Failed to update module" : "Failed to create module (ID must be unique)");
    }
  };

  return (
    <div>
      {user?.role === "admin" && ENABLE_MODULE_MANAGEMENT && (
        <div className="flex justify-end mb-4">
          <Button onClick={() => setShowCreateModal(true)} className="bg-primary hover:bg-primary/90 font-bold text-sm">
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
                  {isIdAuto && <span className="text-xs text-primary font-normal">Auto-generating...</span>}
                </Label>
                <Input
                  type="text"
                  required
                  value={newModule.id}
                  onChange={(e) => {
                    setNewModule({ ...newModule, id: e.target.value });
                    setIsIdAuto(false);
                  }}
                  className={`w-full ${isIdAuto || isEditing ? "bg-muted text-muted-foreground" : ""}`}
                  disabled={isEditing}
                />
                <p className="text-[10px] text-muted-foreground">This ID will be used in URLs.</p>
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
          <Link
            key={module.id}
            href={`/modules/${module.slug}`}
            className="bg-card p-6 rounded-xl border hover:shadow-xl hover:shadow-primary/10 hover:-translate-y-1 transition-all duration-300 cursor-pointer group relative block"
          >
            {user?.role === "admin" && ENABLE_MODULE_MANAGEMENT && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute top-4 right-4 p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-full z-10"
                title="Edit Module"
                onClick={(e) => handleEdit(e, module)}
              >
                <Pencil size={16} />
              </Button>
            )}
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 text-primary group-hover:bg-primary group-hover:text-white transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <h3 className="text-xl font-display font-bold text-foreground group-hover:text-primary transition-colors uppercase">
              {module.name.replace(/practice/gi, "").trim()}
            </h3>
            {module.description ? (
              <p className="text-sm text-muted-foreground mt-2">{module.description}</p>
            ) : (
              <p className="text-sm text-muted-foreground mt-2">Master {module.name.replace(/practice/gi, "").trim()} with hands-on challenges</p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
