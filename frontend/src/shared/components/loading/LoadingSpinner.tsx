import * as React from "react";
import { cn } from "@/shared/utils/cn";
import { Loader2 } from "lucide-react";

export type LoadingSpinnerProps = React.SVGProps<SVGSVGElement>;

const LoadingSpinner = React.forwardRef<SVGSVGElement, LoadingSpinnerProps>(
  ({ className, ...props }, ref) => {
    return (
      <Loader2
        ref={ref}
        className={cn("h-6 w-6 animate-spin text-[hsl(var(--primary))]", className)}
        role="status"
        aria-label="Loading"
        {...props}
      />
    );
  }
);
LoadingSpinner.displayName = "LoadingSpinner";

export { LoadingSpinner };
