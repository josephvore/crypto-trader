import axios from "axios";
import { useUiStore } from "./store";

export const API_BASE = (import.meta as any).env.VITE_API_URL || "http://localhost:8080";

export const api = axios.create({
  baseURL: API_BASE
});

api.interceptors.request.use((config) => {
  try {
    const pwd = useUiStore.getState().password || localStorage.getItem("ct_api_password");
    if (pwd) {
      config.headers = config.headers ?? {};
      (config.headers as any)["X-API-Password"] = pwd;
    }
  } catch {
  }
  return config;
});
