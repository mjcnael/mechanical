import axios from "axios";
import { clearToken, getToken } from "@/shared/auth";
import { FALLBACK_ERROR_MESSAGE, resolveApiErrorMessage } from "@/shared/errors";

export const apiInstance = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

apiInstance.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken();
      if (window.location.pathname !== "/") {
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  },
);

export const getApiErrorMessage = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    return resolveApiErrorMessage(error.response?.data);
  }
  return FALLBACK_ERROR_MESSAGE;
};
