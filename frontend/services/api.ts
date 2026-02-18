import axios from "axios";
import type { Filters, QuestionRead, QuestionDetail, ExecutionResult, Module } from "@/types";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});


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
