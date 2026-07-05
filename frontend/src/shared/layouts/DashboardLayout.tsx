import React, { useState, useEffect, useRef, useCallback } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { Sidebar } from "../components/navigation/Sidebar";
import { TopNavbar } from "../components/navigation/TopNavbar";
import { useAuth } from "@/features/auth";

export const DashboardLayout: React.FC = () => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isDesktopCollapsed, setIsDesktopCollapsed] = useState(false);
  
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();
  
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const closeSidebar = useCallback(() => {
    setIsMobileOpen((prev) => {
      if (prev && menuButtonRef.current) {
        menuButtonRef.current.focus();
      }
      return false;
    });
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      closeSidebar();
    }, 0);
    return () => clearTimeout(timer);
  }, [location.pathname, closeSidebar]);

  // Handle escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeSidebar();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [closeSidebar]);

  return (
    <div className="flex min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
      <Sidebar 
        isOpen={isMobileOpen} 
        onClose={closeSidebar} 
        isDesktopCollapsed={isDesktopCollapsed} 
      />
      
      <div className="flex flex-1 flex-col min-w-0">
        <TopNavbar 
          onOpenMobileMenu={() => setIsMobileOpen(true)}
          onToggleDesktopSidebar={() => setIsDesktopCollapsed((prev) => !prev)}
          onLogout={handleLogout}
          menuButtonRef={menuButtonRef}
        />
        
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
