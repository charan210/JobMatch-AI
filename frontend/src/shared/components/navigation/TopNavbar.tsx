import React from "react";
import { Menu } from "lucide-react";
import { UserMenu } from "./UserMenu";
import { useLocation } from "react-router-dom";
import { NAV_ITEMS } from "@/shared/config/navigation";

interface TopNavbarProps {
  onOpenMobileMenu: () => void;
  onToggleDesktopSidebar: () => void;
  onLogout: () => void;
  menuButtonRef?: React.RefObject<HTMLButtonElement | null>;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({ onOpenMobileMenu, onToggleDesktopSidebar, onLogout, menuButtonRef }) => {
  const location = useLocation();
  const currentItem = NAV_ITEMS.find((item) => location.pathname.startsWith(item.to));
  const title = currentItem ? currentItem.label : "ARAS Platform";

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-[hsl(var(--border))] bg-[hsl(var(--card))]/80 px-4 backdrop-blur-sm sm:px-6">
      <div className="flex items-center space-x-4">
        <button
          ref={menuButtonRef as React.RefObject<HTMLButtonElement>}
          onClick={onOpenMobileMenu}
          className="md:hidden rounded-md p-2 hover:bg-[hsl(var(--secondary))] text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          aria-label="Open mobile menu"
        >
          <Menu size={20} />
        </button>
        
        <button
          onClick={onToggleDesktopSidebar}
          className="hidden md:block rounded-md p-2 hover:bg-[hsl(var(--secondary))] text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          aria-label="Toggle desktop sidebar"
        >
          <Menu size={20} />
        </button>
        
        <h1 className="text-lg font-semibold tracking-tight hidden sm:block">
          {title}
        </h1>
      </div>

      <div className="flex items-center">
        <UserMenu onLogout={onLogout} />
      </div>
    </header>
  );
};
