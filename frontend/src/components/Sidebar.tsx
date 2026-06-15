import React from 'react';
import { History, MessageSquare, Settings, PlusCircle, Compass } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

interface SidebarProps {
  onNewChat: () => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export function Sidebar({ onNewChat, isOpen, setIsOpen }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar container */}
      <div className={cn(
        "fixed md:static inset-y-0 left-0 z-50 w-[260px] bg-[var(--color-sidebar)] border-r border-[var(--color-border)] flex flex-col transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        {/* New Chat Button */}
        <div className="p-3">
          <button 
            onClick={onNewChat}
            className="flex items-center gap-2 w-full p-3 rounded-lg hover:bg-[var(--color-border)] transition-colors text-sm font-medium"
          >
            <PlusCircle className="w-4 h-4" />
            New chat
          </button>
        </div>

        {/* Navigation items */}
        <div className="flex-1 overflow-y-auto px-3 py-2">
          <div className="text-xs font-semibold text-[var(--color-text-secondary)] mb-3 px-3 uppercase tracking-wider">
            History
          </div>
          <div className="space-y-1">
            <button className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-[var(--color-border)] transition-colors text-sm text-left truncate text-[var(--color-text-main)]">
              <MessageSquare className="w-4 h-4 shrink-0" />
              <span className="truncate">Tóm tắt bối cảnh Bộ luật Hồng Đức</span>
            </button>
            <button className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-[var(--color-border)] transition-colors text-sm text-left truncate text-[var(--color-text-main)]">
              <MessageSquare className="w-4 h-4 shrink-0" />
              <span className="truncate">Sự kiện Đổi quốc hiệu Đại Nam</span>
            </button>
          </div>
        </div>

        {/* Bottom actions */}
        <div className="p-3 border-t border-[var(--color-border)] space-y-1">
          <button className="flex items-center gap-2 w-full p-3 rounded-lg hover:bg-[var(--color-border)] transition-colors text-sm font-medium">
            <Compass className="w-4 h-4" />
            Explore
          </button>
          <button className="flex items-center gap-2 w-full p-3 rounded-lg hover:bg-[var(--color-border)] transition-colors text-sm font-medium">
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </div>
    </>
  );
}
