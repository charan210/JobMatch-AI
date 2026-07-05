import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/Button";

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[hsl(var(--background))] p-4 text-center">
      <h1 className="text-8xl font-bold tracking-tighter text-[hsl(var(--primary))]">404</h1>
      <h2 className="mt-4 text-2xl font-semibold tracking-tight">Page Not Found</h2>
      <p className="mt-2 text-[hsl(var(--muted-foreground))] max-w-sm">
        The page you are looking for does not exist, has been removed, or is temporarily unavailable.
      </p>
      <Button onClick={() => navigate("/")} className="mt-8">
        Return to Safety
      </Button>
    </div>
  );
};
