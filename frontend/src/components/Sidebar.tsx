import React, { useState, useEffect } from 'react';
import { History, MessageSquare, Settings, PlusCircle, Compass } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
}

interface SidebarProps {
  onNewChat: () => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  onSelectSession: (id: string) => void;
}

import { useAuth } from '../context/AuthContext';

export function Sidebar({ onNewChat, isOpen, setIsOpen, onSelectSession }: SidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;
    fetch('http://localhost:8000/api/sessions', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setSessions(data);
        }
      })
      .catch(err => console.error('Failed to fetch sessions:', err));
  }, [token]);
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
    className="flex items-center gap-2 w-full p-3 rounded-lg hover:bg-[var(--color-border)] transition-colors text-sm font-medium text-blue-500" // 💡 Thêm text-blue-500 ở đây
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
            {sessions.map(session => (
              <button 
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className="flex items-center gap-2 w-full p-3 rounded-lg hover:bg-[var(--color-border)] transition-colors text-sm font-medium text-[var(--color-text-main)] text-left truncate"
                title={session.title}
              >
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{session.title}</span>
              </button>
            ))}
            {sessions.length === 0 && (
              <div className="px-3 text-sm text-[var(--color-text-secondary)]">
                No chat history
              </div>
            )}
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
