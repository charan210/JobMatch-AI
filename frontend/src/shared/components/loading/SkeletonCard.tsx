import * as React from "react";
import { cn } from "@/shared/utils/cn";
import { Card, CardContent, CardHeader } from "@/shared/components/ui/Card";

export type SkeletonCardProps = React.HTMLAttributes<HTMLDivElement>;

const SkeletonCard = React.forwardRef<HTMLDivElement, SkeletonCardProps>(
  ({ className, ...props }, ref) => {
    return (
      <Card ref={ref} className={cn("overflow-hidden", className)} aria-hidden="true" {...props}>
        <CardHeader className="gap-2">
          <div className="h-5 w-1/3 animate-pulse rounded bg-[hsl(var(--muted))]" />
          <div className="h-4 w-1/2 animate-pulse rounded bg-[hsl(var(--muted))]" />
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="h-4 w-full animate-pulse rounded bg-[hsl(var(--muted))]" />
          <div className="h-4 w-[90%] animate-pulse rounded bg-[hsl(var(--muted))]" />
          <div className="h-4 w-[80%] animate-pulse rounded bg-[hsl(var(--muted))]" />
        </CardContent>
      </Card>
    );
  }
);
SkeletonCard.displayName = "SkeletonCard";

export { SkeletonCard };
