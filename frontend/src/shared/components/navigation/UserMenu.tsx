import React, { useState, useRef, useEffect } from "react";
import { LogOut, User } from "lucide-react";
import { useAuth } from "@/features/auth";

interface UserMenuProps {
  onLogout: () => void;
}

export const UserMenu: React.FC<UserMenuProps> = ({ onLogout }) => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 rounded-full bg-[hsl(var(--secondary))] p-2 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2"
        aria-expanded={isOpen}
        aria-haspopup="menu"
        aria-label="User menu"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]">
          <User size={16} />
        </div>
      </button>

      {isOpen && (
        <div 
          className="absolute right-0 mt-2 w-56 rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-lg z-50 animate-in fade-in slide-in-from-top-2"
          role="menu"
        >
          <div className="border-b border-[hsl(var(--border))] px-4 py-3">
            <p className="text-sm font-medium leading-none text-[hsl(var(--foreground))]">
              {user?.name || "User"}
            </p>
            <p className="mt-1 text-xs leading-none text-[hsl(var(--muted-foreground))]">
              {user?.email || "No email"}
            </p>
          </div>
          <div className="p-1">
            <button
              onClick={onLogout}
              className="flex w-full items-center space-x-2 rounded-sm px-3 py-2 text-sm text-[hsl(var(--destructive))] hover:bg-[hsl(var(--destructive)/0.1)] focus:bg-[hsl(var(--destructive)/0.1)] focus:outline-none"
              role="menuitem"
            >
              <LogOut size={16} />
              <span>Log out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
