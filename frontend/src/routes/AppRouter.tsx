import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthLayout } from "@/shared/layouts/AuthLayout";
import { DashboardLayout } from "@/shared/layouts/DashboardLayout";
import { ProtectedRoute } from "./ProtectedRoute";
import { PublicRoute } from "./PublicRoute";
import { NotFoundPage } from "@/shared/pages/NotFoundPage";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { RegisterPage } from "@/features/auth/pages/RegisterPage";

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Root Redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Public Routes (Only accessible if unauthenticated) */}
        <Route element={<PublicRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
        </Route>

        {/* Protected Routes (Only accessible if authenticated) */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="/404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
