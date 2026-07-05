import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { RegisterForm } from "../components/RegisterForm";

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col space-y-6 animate-in fade-in-50">
      <RegisterForm onSuccess={() => navigate("/login", { replace: true })} />
      <p className="px-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
        Already have an account?{" "}
        <Link to="/login" className="underline underline-offset-4 hover:text-[hsl(var(--primary))]">
          Login
        </Link>
      </p>
    </div>
  );
};
