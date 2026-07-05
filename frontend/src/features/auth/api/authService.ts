import { apiClient } from "@/shared/services/apiClient";
import { setAccessToken, setRefreshToken, removeTokens, hasAccessToken } from "@/shared/services/tokenManager";
import type { LoginRequest, RegisterRequest, AuthTokens, User } from "../types/auth";

export async function login(credentials: LoginRequest): Promise<void> {
  const response = await apiClient.post<AuthTokens>("/api/v1/auth/login", credentials);
  setAccessToken(response.data.access_token);
  setRefreshToken(response.data.refresh_token);
}

export async function register(data: RegisterRequest): Promise<User> {
  const response = await apiClient.post<User>("/api/v1/auth/register", data);
  return response.data;
}

export function logout(): void {
  // No backend logout endpoint exists currently.
  // Purge local session tokens.
  removeTokens();
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>("/api/v1/users/me");
  return response.data;
}

export async function restoreSession(): Promise<User | null> {
  if (!hasAccessToken()) {
    return null;
  }
  
  try {
    return await getCurrentUser();
  } catch {
    removeTokens();
    return null;
  }
}
