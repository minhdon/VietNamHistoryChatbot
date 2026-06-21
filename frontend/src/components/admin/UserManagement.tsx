import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Trash2 } from 'lucide-react';

interface User {
  id: number;
  username: string;
  created_at: string;
}

export function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Failed to fetch users', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      const res = await fetch(`http://localhost:8000/api/admin/users/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setUsers(users.filter(u => u.id !== id));
      } else {
        alert('Failed to delete user');
      }
    } catch (error) {
      console.error('Failed to delete user', error);
    }
  };

  if (loading) return <div>Loading users...</div>;

  return (
    <div className="bg-[var(--color-sidebar)] rounded-lg border border-[var(--color-border)] p-4 shadow-sm">
      <h2 className="text-xl font-bold mb-4 text-[var(--color-text-main)]">User Management</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-[var(--color-text-main)]">
          <thead className="bg-[var(--color-main)] text-[var(--color-text-secondary)] border-b border-[var(--color-border)]">
            <tr>
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Username</th>
              <th className="px-4 py-3 font-medium">Created At</th>
              <th className="px-4 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className="border-b border-[var(--color-border)] hover:bg-[var(--color-main)]/50 transition-colors">
                <td className="px-4 py-3">{user.id}</td>
                <td className="px-4 py-3 font-medium">{user.username}</td>
                <td className="px-4 py-3">{new Date(user.created_at).toLocaleString()}</td>
                <td className="px-4 py-3 text-right">
                  {user.username !== 'admin' && (
                    <button 
                      onClick={() => deleteUser(user.id)}
                      className="text-red-500 hover:text-red-600 p-1 rounded transition-colors"
                      title="Delete User"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {users.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-[var(--color-text-secondary)]">
                  No users found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
