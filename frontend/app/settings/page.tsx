"use client";

import { useState, FormEvent } from "react";
import { useAuth } from "@/context/AuthContext";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Key, Save, AlertCircle, CheckCircle2, Trash2 } from "lucide-react";
import api from "@/services/api";

export default function SettingsPage() {
    const { user, refreshUser } = useAuth();
    const [groqKey, setGroqKey] = useState("");
    const [openaiKey, setOpenaiKey] = useState("");
    const [anthropicKey, setAnthropicKey] = useState("");
    const [defaultProvider, setDefaultProvider] = useState(user?.default_llm_provider || "groq");
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState<{ text: string; type: string }>({ text: "", type: "" });

    const handleSave = async (e: FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage({ text: "", type: "" });

        try {
            await api.put("/v1/auth/me/settings", {
                groq_api_key: groqKey || undefined,
                openai_api_key: openaiKey || undefined,
                anthropic_api_key: anthropicKey || undefined,
                default_llm_provider: defaultProvider
            });
            await refreshUser();
            setMessage({ text: "Environment settings updated successfully!", type: "success" });
            setGroqKey("");
            setOpenaiKey("");
            setAnthropicKey("");
        } catch (err: any) {
            console.error("Failed to update settings", err);
            setMessage({
                text: err.response?.data?.detail || "Failed to update settings. Please try again.",
                type: "error"
            });
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async (provider: string) => {
        const providerName = provider === 'groq' ? 'Groq' : provider === 'openai' ? 'OpenAI' : 'Anthropic';
        if (!window.confirm(`Are you sure you want to remove your ${providerName} API key?`)) return;

        setIsSaving(true);
        setMessage({ text: "", type: "" });

        try {
            const payload: Record<string, string> = {};
            payload[`${provider}_api_key`] = "";
            await api.put("/v1/auth/me/settings", payload);
            await refreshUser();
            setMessage({ text: `${providerName} API Key removed.`, type: "success" });
        } catch (err: any) {
            console.error("Failed to delete key", err);
            setMessage({
                text: err.response?.data?.detail || "Failed to delete key. Please try again.",
                type: "error"
            });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <Layout>
            <div className="max-w-3xl mx-auto py-12 px-4">
                <div className="mb-8 pl-1">
                    <h1 className="text-3xl font-display font-bold uppercase tracking-tight text-foreground">Environment Settings</h1>
                    <p className="text-muted-foreground mt-2">Configure your development environment and LLM Provider instructions.</p>
                </div>

                <Card className="border shadow-sm">
                    <CardHeader className="border-b border bg-muted/30 pb-8">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-primary/10 rounded-lg">
                                <Key className="w-5 h-5 text-primary" />
                            </div>
                            <div>
                                <CardTitle className="text-lg font-bold text-foreground">LLM Provider Setup</CardTitle>
                                <CardDescription>Provide your own API keys to enable AI capabilities.</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="p-8">
                        <form onSubmit={handleSave} className="space-y-10">
                            <div className="space-y-4">
                                <Label className="text-sm font-semibold text-foreground">
                                    Default LLM Provider
                                </Label>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {[
                                        { id: 'groq', name: 'Groq', color: 'indigo' },
                                        { id: 'openai', name: 'OpenAI', color: 'emerald' },
                                        { id: 'anthropic', name: 'Anthropic', color: 'orange' }
                                    ].map((p) => (
                                        <button
                                            key={p.id}
                                            type="button"
                                            onClick={() => setDefaultProvider(p.id)}
                                            className={`relative flex flex-col items-center justify-center h-28 rounded-xl border-2 transition-all ${defaultProvider === p.id
                                                ? `border-cb-teal bg-cb-teal/10 text-cb-teal`
                                                : "border hover:border-primary/30 hover:bg-primary/5 text-muted-foreground"
                                                }`}
                                        >
                                            {defaultProvider === p.id && (
                                                <div className="absolute top-2 right-2">
                                                    <CheckCircle2 size={16} className="text-cb-teal" />
                                                </div>
                                            )}
                                            <span className="font-bold text-lg">{p.name}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-8">
                                <div className="grid gap-3">
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="groq-key" className="flex items-center gap-2">
                                            Groq API Key
                                            {user?.has_groq_api_key && (
                                                <span className="text-[10px] font-bold text-cb-teal bg-cb-teal/10 px-2 py-0.5 rounded-full border border-cb-teal/25 uppercase tracking-wide">Active</span>
                                            )}
                                        </Label>
                                        <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-primary hover:text-primary/80 hover:underline">Get Key ↗</a>
                                    </div>
                                    <div className="flex gap-2">
                                        <Input
                                            id="groq-key"
                                            type="password"
                                            placeholder={user?.has_groq_api_key ? "••••••••••••••••••••" : "Enter your Groq key..."}
                                            value={groqKey}
                                            onChange={(e) => setGroqKey(e.target.value)}
                                            className="font-mono bg-muted/30"
                                        />
                                        {user?.has_groq_api_key && (
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="icon"
                                                onClick={() => handleDelete('groq')}
                                                disabled={isSaving}
                                                className="shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10 border"
                                            >
                                                <Trash2 size={16} />
                                            </Button>
                                        )}
                                    </div>
                                </div>

                                <div className="grid gap-3">
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="openai-key" className="flex items-center gap-2">
                                            OpenAI API Key
                                            {user?.has_openai_api_key && (
                                                <span className="text-[10px] font-bold text-cb-teal bg-cb-teal/10 px-2 py-0.5 rounded-full border border-cb-teal/25 uppercase tracking-wide">Active</span>
                                            )}
                                        </Label>
                                        <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-primary hover:text-primary/80 hover:underline">Get Key ↗</a>
                                    </div>
                                    <div className="flex gap-2">
                                        <Input
                                            id="openai-key"
                                            type="password"
                                            placeholder={user?.has_openai_api_key ? "••••••••••••••••••••" : "Enter your OpenAI key..."}
                                            value={openaiKey}
                                            onChange={(e) => setOpenaiKey(e.target.value)}
                                            className="font-mono bg-muted/30"
                                        />
                                        {user?.has_openai_api_key && (
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="icon"
                                                onClick={() => handleDelete('openai')}
                                                disabled={isSaving}
                                                className="shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10 border"
                                            >
                                                <Trash2 size={16} />
                                            </Button>
                                        )}
                                    </div>
                                </div>

                                <div className="grid gap-3">
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="anthropic-key" className="flex items-center gap-2">
                                            Anthropic API Key
                                            {user?.has_anthropic_api_key && (
                                                <span className="text-[10px] font-bold text-cb-teal bg-cb-teal/10 px-2 py-0.5 rounded-full border border-cb-teal/25 uppercase tracking-wide">Active</span>
                                            )}
                                        </Label>
                                        <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-primary hover:text-primary/80 hover:underline">Get Key ↗</a>
                                    </div>
                                    <div className="flex gap-2">
                                        <Input
                                            id="anthropic-key"
                                            type="password"
                                            placeholder={user?.has_anthropic_api_key ? "••••••••••••••••••••" : "Enter your Anthropic key..."}
                                            value={anthropicKey}
                                            onChange={(e) => setAnthropicKey(e.target.value)}
                                            className="font-mono bg-muted/30"
                                        />
                                        {user?.has_anthropic_api_key && (
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="icon"
                                                onClick={() => handleDelete('anthropic')}
                                                disabled={isSaving}
                                                className="shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10 border"
                                            >
                                                <Trash2 size={16} />
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {message.text && (
                                <div className={`p-4 rounded-lg flex items-center gap-3 text-sm font-medium ${message.type === 'success' ? 'bg-cb-teal/10 text-cb-teal border border-cb-teal/25' : 'bg-destructive/10 text-destructive border border-destructive/25'
                                    }`}>
                                    {message.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                                    <p>{message.text}</p>
                                </div>
                            )}

                            <div className="flex justify-end pt-2">
                                <Button
                                    type="submit"
                                    disabled={isSaving || (!groqKey && !openaiKey && !anthropicKey && defaultProvider === user?.default_llm_provider)}
                                    className="px-8 font-bold"
                                >
                                    {isSaving ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            <Save size={16} className="mr-2" />
                                            Update Environment
                                        </>
                                    )}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </Layout>
    );
}
