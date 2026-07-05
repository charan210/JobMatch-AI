import React from "react";
import { NavLink } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/shared/utils/cn";

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  to: string;
  onClick?: () => void;
  isCollapsed?: boolean;
}

export const SidebarItem: React.FC<SidebarItemProps> = ({ icon: Icon, label, to, onClick, isCollapsed }) => {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      title={isCollapsed ? label : undefined}
      className={({ isActive }) =>
        cn(
          "flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]",
          isActive
            ? "bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary))]"
            : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))] hover:text-[hsl(var(--foreground))]",
          isCollapsed ? "justify-center" : "space-x-3"
        )
      }
    >
      <Icon size={20} className={cn(isCollapsed && "mx-auto")} />
      {!isCollapsed && <span>{label}</span>}
    </NavLink>
  );
};
