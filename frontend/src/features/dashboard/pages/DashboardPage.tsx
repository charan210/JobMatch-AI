import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/shared/components/ui/Card";
import { EmptyState } from "@/shared/components/feedback/EmptyState";

export const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-in fade-in-50">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-[hsl(var(--muted-foreground))]">Welcome to the ARAS platform.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Overview</CardTitle>
          <CardDescription>Your recent activity</CardDescription>
        </CardHeader>
        <CardContent>
          <EmptyState 
            title="No Data Available" 
            description="Dashboard widgets will be implemented in future milestones." 
          />
        </CardContent>
      </Card>
    </div>
  );
};
