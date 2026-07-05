import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { LoginForm } from "../components/LoginForm";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col space-y-6 animate-in fade-in-50">
      <LoginForm onSuccess={() => navigate("/dashboard", { replace: true })} />
      <p className="px-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
        Don't have an account?{" "}
        <Link to="/register" className="underline underline-offset-4 hover:text-[hsl(var(--primary))]">
          Sign up
        </Link>
      </p>
    </div>
  );
};
