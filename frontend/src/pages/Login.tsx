import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BookOpen } from 'lucide-react';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error('Tài khoản hoặc mật khẩu không chính xác');
      }

      const data = await response.json();
      login(data.access_token, data.user);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Có lỗi xảy ra khi đăng nhập');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-main)] p-4">
      <div className="w-full max-w-md bg-[var(--color-sidebar)] rounded-2xl p-8 border border-[var(--color-border)] shadow-xl relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
        
        <div className="flex flex-col items-center justify-center mb-8">
          <div className="w-12 h-12 bg-black/5 dark:bg-white/5 rounded-xl flex items-center justify-center mb-4">
             <BookOpen className="w-6 h-6 text-[var(--color-text-main)]" />
          </div>
          <h1 className="text-2xl font-bold text-[var(--color-text-main)]">Chào mừng trở lại</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">Đăng nhập để tiếp tục trò chuyện</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-500 text-sm rounded-lg text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">
              Tên đăng nhập
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-[var(--color-input)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-[var(--color-text-main)] focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
              placeholder="Nhập tên đăng nhập..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">
              Mật khẩu
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[var(--color-input)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-[var(--color-text-main)] focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[var(--color-text-main)] text-[var(--color-main)] font-medium rounded-lg px-4 py-2.5 hover:opacity-90 transition-opacity disabled:opacity-50 mt-6"
          >
            {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>

        <p className="text-center text-sm text-[var(--color-text-secondary)] mt-6">
          Chưa có tài khoản?{' '}
          <Link to="/register" className="text-[var(--color-text-main)] font-medium hover:underline">
            Đăng ký ngay
          </Link>
        </p>
      </div>
    </div>
  );
};
