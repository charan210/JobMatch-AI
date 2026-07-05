import * as React from "react";
import { cn } from "@/shared/utils/cn";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/shared/components/ui/Button";

export interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

const ErrorState = React.forwardRef<HTMLDivElement, ErrorStateProps>(
  ({ className, title = "Something went wrong", description = "An unexpected error occurred while loading this data.", onRetry, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex min-h-[300px] flex-col items-center justify-center rounded-md border border-dashed border-[hsl(var(--destructive))]/50 p-8 text-center",
          className
        )}
        role="alert"
        {...props}
      >
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[hsl(var(--destructive))]/10">
          <AlertTriangle className="h-6 w-6 text-[hsl(var(--destructive))]" />
        </div>
        <h3 className="mt-4 text-lg font-semibold text-[hsl(var(--foreground))]">{title}</h3>
        <p className="mb-4 mt-2 text-sm text-[hsl(var(--muted-foreground))]">
          {description}
        </p>
        {onRetry && (
          <Button variant="outline" onClick={onRetry} className="mt-2">
            Try again
          </Button>
        )}
      </div>
    );
  }
);
ErrorState.displayName = "ErrorState";

export { ErrorState };
