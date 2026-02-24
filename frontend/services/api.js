import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 5 minutes timeout for heavy Deep Learning tasks
});

api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        console.log("Attaching token to request:", config.url);
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        console.warn("No token found in localStorage for request:", config.url);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const getQuestions = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.difficulty) params.append("difficulty", filters.difficulty);
  if (filters.status) params.append("status", filters.status);
  const response = await api.get(`/questions/?${params.toString()}`);
  return response.data;
};

export const getQuestion = async (id) => {
  const response = await api.get(`/questions/${id}`);
  return response.data;
};

export const runCode = async (data) => {
  const response = await api.post("/execute/run", data);
  return response.data;
};

export const validateCode = async (data) => {
  const response = await api.post("/execute/validate", data);
  return response.data;
};

export const createModule = async (data) => {
  const response = await api.post("/modules/", data);
  return response.data;
};

export const updateModule = async (id, data) => {
  const response = await api.patch(`/modules/${id}`, data);
  return response.data;
};

export const deleteModule = async (id) => {
  await api.delete(`/modules/${id}`);
};

export const deleteQuestion = async (id) => {
  await api.delete(`/v1/admin/questions/${id}`);
};

export const verifyQuestion = async (id, verified) => {
  const response = await api.post(`/v1/admin/questions/${id}/verify`, { verified });
  return response.data;
};

export default api;
