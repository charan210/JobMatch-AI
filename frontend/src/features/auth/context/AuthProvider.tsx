import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { AuthState, LoginRequest, RegisterRequest } from "../types/auth";
import { login as apiLogin, register as apiRegister, logout as apiLogout, restoreSession } from "../api/authService";
import { AuthContext } from "./AuthContext";

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true, // Prevents UI flicker on startup
  });

  useEffect(() => {
    let mounted = true;

    const init = async () => {
      // restoreSession handles async delay, meaning setState is never called synchronously in effect.
      const user = await restoreSession();
      if (mounted) {
        setState({
          user,
          isAuthenticated: !!user,
          isLoading: false,
        });
      }
    };

    init();

    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(async (credentials: LoginRequest) => {
    await apiLogin(credentials);
    const user = await restoreSession();
    setState({
      user,
      isAuthenticated: !!user,
      isLoading: false,
    });
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    await apiRegister(data);
    // Note: Backend register does not return tokens.
    // The user must explicitly login after successful registration.
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  const contextValue = useMemo(
    () => ({
      ...state,
      login,
      register,
      logout,
    }),
    [state, login, register, logout]
  );

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};
