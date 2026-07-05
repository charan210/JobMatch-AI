import * as React from "react";
import { cn } from "@/shared/utils/cn";
import { LoadingSpinner } from "./LoadingSpinner";

export type LoadingScreenProps = React.HTMLAttributes<HTMLDivElement>;

const LoadingScreen = React.forwardRef<HTMLDivElement, LoadingScreenProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("fixed inset-0 z-50 flex items-center justify-center bg-[hsl(var(--background))]/80 backdrop-blur-sm", className)}
        role="status"
        aria-live="polite"
        aria-busy="true"
        aria-label="Loading screen"
        {...props}
      >
        <LoadingSpinner className="h-12 w-12" />
      </div>
    );
  }
);
LoadingScreen.displayName = "LoadingScreen";

export { LoadingScreen };
