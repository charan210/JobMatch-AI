import React from "react";
import { Outlet } from "react-router-dom";

export const DashboardLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
      {/* Sidebar Placeholder */}
      <aside className="hidden w-64 flex-col border-r border-[hsl(var(--border))] bg-[hsl(var(--card))] md:flex p-6">
        <div className="text-xl font-bold tracking-tight text-[hsl(var(--primary))]">ARAS</div>
        <div className="mt-8 space-y-2 text-sm font-medium text-[hsl(var(--muted-foreground))]">
          <div>Navigation Placeholder</div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        {/* Top Navigation Placeholder */}
        <header className="flex h-16 items-center justify-between border-b border-[hsl(var(--border))] bg-[hsl(var(--card))] px-6">
          <div className="text-sm font-medium text-[hsl(var(--muted-foreground))]">Header Placeholder</div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
