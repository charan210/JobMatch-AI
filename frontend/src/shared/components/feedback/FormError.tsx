import React from "react";

interface FormErrorProps {
  message?: string | null;
}

export const FormError: React.FC<FormErrorProps> = ({ message }) => {
  if (!message) return null;

  return (
    <div className="rounded-md bg-[hsl(var(--destructive)/0.1)] p-3 text-sm font-medium text-[hsl(var(--destructive))]">
      {message}
    </div>
  );
};
