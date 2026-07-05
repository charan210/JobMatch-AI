import { LayoutDashboard, Briefcase, Users, FileText, type LucideIcon } from "lucide-react";

export interface NavItem {
  label: string;
  icon: LucideIcon;
  to: string;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Jobs", icon: Briefcase, to: "/jobs" },
  { label: "Candidates", icon: Users, to: "/candidates" },
  { label: "Resumes", icon: FileText, to: "/resumes" },
];
