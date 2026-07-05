import React, { useRef, useEffect } from "react";
import { X } from "lucide-react";
import { SidebarItem } from "./SidebarItem";
import { cn } from "@/shared/utils/cn";
import { NAV_ITEMS } from "@/shared/config/navigation";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isDesktopCollapsed: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, isDesktopCollapsed }) => {
  const sidebarRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const focusableElements = sidebarRef.current?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusableElements || focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Tab") {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    
    // Focus first element after animation
    const timer = setTimeout(() => {
      firstElement.focus();
    }, 100);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      clearTimeout(timer);
    };
  }, [isOpen]);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden animate-in fade-in"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar container */}
      <aside
        ref={sidebarRef}
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-[hsl(var(--border))] bg-[hsl(var(--card))] transition-transform duration-200 ease-in-out md:static md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
          isDesktopCollapsed && "md:w-20"
        )}
        aria-label="Sidebar navigation"
      >
        <div className={cn("flex h-16 items-center px-6 border-b border-[hsl(var(--border))]", isDesktopCollapsed ? "justify-center" : "justify-between")}>
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] font-bold">
              A
            </div>
            {!isDesktopCollapsed && <span className="text-xl font-bold tracking-tight text-[hsl(var(--primary))]">ARAS</span>}
          </div>
          {!isDesktopCollapsed && (
            <button
              onClick={onClose}
              className="md:hidden rounded-md p-1 hover:bg-[hsl(var(--secondary))] text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              aria-label="Close sidebar"
            >
              <X size={20} />
            </button>
          )}
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-4">
          {NAV_ITEMS.map((item) => (
            <SidebarItem
              key={item.to}
              to={item.to}
              icon={item.icon}
              label={item.label}
              isCollapsed={isDesktopCollapsed}
              onClick={onClose}
            />
          ))}
        </nav>
      </aside>
    </>
  );
};
