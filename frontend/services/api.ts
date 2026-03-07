import axios from "axios";
import { getSession, signOut } from "next-auth/react";
import type { Filters, QuestionRead, QuestionDetail, ExecutionResult, Module } from "@/types";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(async (config) => {
  const session = await getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

// 401 response interceptor — fires when the backend rejects a token.
// The jwt callback in auth.ts proactively refreshes tokens before expiry, so
// a 401 at runtime means the refresh itself failed (RefreshAccessTokenError)
// or the session cookie is gone. Sign the user out to clear stale state.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const session = await getSession();
      // Only sign out if we actually had a session — avoids redirect loops on
      // public endpoints that return 401 when no user is logged in.
      if (session) {
        await signOut({ callbackUrl: "/" });
      }
    }
    return Promise.reject(error);
  }
);


export const getQuestions = async (filters: Partial<Filters> = {}): Promise<QuestionRead[]> => {
  const params = new URLSearchParams();
  if (filters.difficulty) params.append("difficulty", filters.difficulty);
  if (filters.status) params.append("status", filters.status);
  const response = await api.get<QuestionRead[]>(`/questions/?${params.toString()}`);
  return response.data;
};

export const getQuestion = async (id: string): Promise<QuestionDetail> => {
  const response = await api.get<QuestionDetail>(`/questions/${id}`);
  return response.data;
};

export const getQuestionBySlug = async (moduleSlug: string, questionSlug: string): Promise<QuestionDetail> => {
  const response = await api.get<QuestionDetail>(`/modules/${moduleSlug}/questions/${questionSlug}`);
  return response.data;
};

export const runCode = async (data: { code: string; question_id: string; module_id: string }): Promise<ExecutionResult> => {
  const response = await api.post<ExecutionResult>("/execute/run", data);
  return response.data;
};

export const validateCode = async (data: { code: string; question_id: string; module_id: string }): Promise<ExecutionResult> => {
  const response = await api.post<ExecutionResult>("/execute/validate", data);
  return response.data;
};

export const createModule = async (data: Partial<Module>): Promise<Module> => {
  const response = await api.post<Module>("/modules/", data);
  return response.data;
};

export const updateModule = async (id: string, data: Partial<Module>): Promise<Module> => {
  const response = await api.patch<Module>(`/modules/${id}`, data);
  return response.data;
};

export const deleteModule = async (id: string): Promise<void> => {
  await api.delete(`/modules/${id}`);
};

export const deleteQuestion = async (id: string): Promise<void> => {
  await api.delete(`/v1/admin/questions/${id}`);
};

export const verifyQuestion = async (id: string, verified: boolean): Promise<unknown> => {
  const response = await api.post(`/v1/admin/questions/${id}/verify`, { verified });
  return response.data;
};

export default api;
