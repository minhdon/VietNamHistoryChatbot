import React, { useState } from 'react';
import { Users, Database, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { UserManagement } from '../components/admin/UserManagement';
import { Neo4jManagement } from '../components/admin/Neo4jManagement';

export function Admin() {
  const [activeTab, setActiveTab] = useState<'users' | 'neo4j'>('users');
  const { logout } = useAuth();

  return (
    <div className="flex h-screen w-full bg-[var(--color-main)] text-[var(--color-text-main)] font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-[var(--color-sidebar)] border-r border-[var(--color-border)] flex flex-col">
        <div className="p-4 border-b border-[var(--color-border)]">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Admin Dashboard
          </h1>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          <button 
            onClick={() => setActiveTab('users')}
            className={`flex items-center gap-3 w-full p-3 rounded-lg transition-colors text-sm font-medium ${
              activeTab === 'users' 
                ? 'bg-[var(--color-border)] text-blue-500' 
                : 'hover:bg-[var(--color-border)]/50'
            }`}
          >
            <Users className="w-5 h-5" />
            User Management
          </button>
          
          <button 
            onClick={() => setActiveTab('neo4j')}
            className={`flex items-center gap-3 w-full p-3 rounded-lg transition-colors text-sm font-medium ${
              activeTab === 'neo4j' 
                ? 'bg-[var(--color-border)] text-emerald-500' 
                : 'hover:bg-[var(--color-border)]/50'
            }`}
          >
            <Database className="w-5 h-5" />
            Neo4j Documents
          </button>
        </div>

        <div className="p-4 border-t border-[var(--color-border)]">
          <button 
            onClick={logout}
            className="flex items-center justify-center gap-2 w-full p-2 bg-red-500/10 text-red-500 hover:bg-red-500/20 rounded-lg transition-colors text-sm font-medium"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-8 bg-[var(--color-main)]">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold">
              {activeTab === 'users' ? 'User Management' : 'Neo4j Document Management'}
            </h1>
            <p className="text-[var(--color-text-secondary)] mt-2">
              {activeTab === 'users' 
                ? 'View and manage registered users in the system.' 
                : 'Manage the underlying graph database knowledge chunks directly.'}
            </p>
          </div>

          {activeTab === 'users' ? <UserManagement /> : <Neo4jManagement />}
        </div>
      </div>
    </div>
  );
}
