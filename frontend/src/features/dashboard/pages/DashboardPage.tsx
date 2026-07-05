import React from "react";
import { Briefcase, Users, FileText, BarChart3 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/ui/Card";
import { EmptyState } from "@/shared/components/feedback/EmptyState";

const PLACEHOLDER_CARDS = [
  { title: "Jobs", icon: Briefcase, desc: "Active job postings" },
  { title: "Candidates", icon: Users, desc: "Pending reviews" },
  { title: "Resumes", icon: FileText, desc: "Processed this week" },
  { title: "Analytics", icon: BarChart3, desc: "Pipeline efficiency" },
];

export const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-8 animate-in fade-in-50">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-2 text-[hsl(var(--muted-foreground))]">
          Welcome to the ARAS platform overview.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {PLACEHOLDER_CARDS.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <card.icon className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
            </CardHeader>
            <CardContent>
              <div className="text-xl font-bold italic text-[hsl(var(--muted-foreground))]">
                Coming Soon
              </div>
              <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
                {card.desc}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-8">
        <EmptyState 
          title="No Data Available" 
          description="Dashboard widgets and live data streams will be implemented in future milestones." 
        />
      </div>
    </div>
  );
};
