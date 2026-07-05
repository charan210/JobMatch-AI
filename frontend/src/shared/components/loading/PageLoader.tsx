import * as React from "react";
import { cn } from "@/shared/utils/cn";
import { LoadingSpinner } from "./LoadingSpinner";

export interface PageLoaderProps extends React.HTMLAttributes<HTMLDivElement> {
  text?: string;
}

const PageLoader = React.forwardRef<HTMLDivElement, PageLoaderProps>(
  ({ className, text = "Loading...", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("flex min-h-[50vh] flex-col items-center justify-center space-y-4", className)}
        role="status"
        aria-live="polite"
        aria-busy="true"
        {...props}
      >
        <LoadingSpinner className="h-8 w-8" />
        <p className="text-sm text-[hsl(var(--muted-foreground))]">{text}</p>
      </div>
    );
  }
);
PageLoader.displayName = "PageLoader";

export { PageLoader };
