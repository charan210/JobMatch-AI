import axios, { AxiosError } from "axios";
import { getAccessToken } from "./tokenManager";
import { ApiError } from "@/shared/types";

const baseURL = import.meta.env.VITE_API_BASE_URL;
const timeoutStr = import.meta.env.VITE_API_TIMEOUT;

if (!baseURL) {
  throw new Error("VITE_API_BASE_URL is not defined in environment variables. Fail fast.");
}

const timeout = parseInt(timeoutStr, 10);
if (isNaN(timeout)) {
  throw new Error("VITE_API_TIMEOUT is invalid or missing in environment variables. Fail fast.");
}

export const apiClient = axios.create({
  baseURL,
  timeout,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    let message = error.message || "An unexpected error occurred";
    const status = error.response?.status || 500;
    
    if (error.response?.data && typeof error.response.data === "object") {
      const data = error.response.data as Record<string, unknown>;
      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (typeof data.message === "string") {
        message = data.message;
      }
    }

    if (status === 401) {
      // TODO(Milestone 5):
      // Refresh access token here.
    }
    
    return Promise.reject(new ApiError(message, status));
  }
);
