"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import api from "@/services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    setToken(stored);
  }, []);

  useEffect(() => {
    const verifyToken = async () => {
      const t = token ?? (typeof window !== "undefined" ? localStorage.getItem("token") : null);
      if (t) {
        try {
          const response = await api.get("/v1/auth/me");
          setUser(response.data);
          setToken(t);
        } catch (error) {
          console.error("Token invalid", error);
          setToken(null);
          setUser(null);
          if (typeof window !== "undefined") {
            localStorage.removeItem("token");
            localStorage.removeItem("username");
            localStorage.removeItem("role");
          }
          delete axios.defaults.headers.common["Authorization"];
        }
      }
      setLoading(false);
    };
    verifyToken();
  }, [token]);

  const login = async (username, password) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);
    try {
      const response = await api.post("/v1/auth/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      const { access_token, role, username: returnedUsername, current_streak } = response.data;
      setToken(access_token);
      setUser({ username: returnedUsername, role, current_streak });
      if (typeof window !== "undefined") {
        localStorage.setItem("token", access_token);
        localStorage.setItem("username", returnedUsername);
        localStorage.setItem("role", role);
      }
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      return true;
    } catch (error) {
      console.error("Login failed", error);
      return false;
    }
  };

  const adminLogin = async (username, password) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);
    try {
      const response = await api.post("/v1/auth/admin/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      const { access_token, role, username: returnedUsername, current_streak } = response.data;
      setToken(access_token);
      setUser({ username: returnedUsername, role, current_streak });
      if (typeof window !== "undefined") {
        localStorage.setItem("token", access_token);
        localStorage.setItem("username", returnedUsername);
        localStorage.setItem("role", role);
      }
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      return true;
    } catch (error) {
      console.error("Admin login failed", error);
      return false;
    }
  };

  const signup = async (username, email, password) => {
    try {
      await api.post("/v1/auth/signup", { username, email, password });
      return true;
    } catch (error) {
      console.error("Signup failed", error);
      return false;
    }
  };

  const requestPasswordReset = async (email) => {
    try {
      await api.post("/v1/auth/request-password-reset", { email });
      return true;
    } catch (error) {
      console.error("Password reset request failed", error);
      return false;
    }
  };

  const verifyPasswordReset = async (token, newPassword) => {
    try {
      await api.post("/v1/auth/verify-password-reset", {
        token,
        new_password: newPassword,
      });
      return true;
    } catch (error) {
      console.error("Password reset verification failed", error);
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      localStorage.removeItem("role");
    }
    delete axios.defaults.headers.common["Authorization"];
  };

  const refreshUser = async () => {
    if (token) {
      try {
        const response = await api.get("/v1/auth/me");
        setUser(response.data);
      } catch (error) {
        console.error("Manual refresh failed", error);
        if (error.response?.status === 401) {
          logout();
        }
      }
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        adminLogin,
        logout,
        signup,
        loading,
        refreshUser,
        requestPasswordReset,
        verifyPasswordReset,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
