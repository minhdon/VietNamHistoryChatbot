import React from 'react';
import { BookOpen, Map, Users, Clock } from 'lucide-react';

interface HomepageProps {
  onSelectPrompt: (prompt: string) => void;
}

const SUGGESTIONS = [
  {
    icon: BookOpen,
    title: "Khởi nghĩa Hai Bà Trưng",
    prompt: "Tóm tắt nguyên nhân và diễn biến chính của cuộc khởi nghĩa Hai Bà Trưng."
  },
  {
    icon: Map,
    title: "Trận Bạch Đằng năm 938",
    prompt: "Trình bày chi tiết chiến thuật cắm cọc trên sông Bạch Đằng của Ngô Quyền."
  },
  {
    icon: Users,
    title: "Triều đại nhà Trần",
    prompt: "Những thành tựu nổi bật về văn hóa và quân sự dưới thời nhà Trần là gì?"
  },
  {
    icon: Clock,
    title: "Cách mạng tháng Tám",
    prompt: "Phân tích ý nghĩa lịch sử của Cách mạng tháng Tám năm 1945."
  }
];

export function Homepage({ onSelectPrompt }: HomepageProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 w-full">
      <div className="max-w-3xl w-full space-y-12">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-semibold text-[var(--color-text-main)] tracking-tight">
            How can I help you today?
          </h1>
          <p className="text-[var(--color-text-secondary)] text-lg">
            I am your intelligent assistant for Vietnam History. Ask me anything.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {SUGGESTIONS.map((suggestion, idx) => {
            const Icon = suggestion.icon;
            return (
              <button
                key={idx}
                onClick={() => onSelectPrompt(suggestion.prompt)}
                className="group flex flex-col items-start text-left p-5 rounded-2xl border border-[var(--color-border)] bg-[var(--color-input)] hover:bg-[var(--color-border)] transition-colors"
              >
                <div className="flex items-center gap-3 mb-2 text-[var(--color-text-main)]">
                  <Icon className="w-5 h-5 text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-main)] transition-colors" />
                  <span className="font-medium">{suggestion.title}</span>
                </div>
                <div className="text-sm text-[var(--color-text-secondary)] line-clamp-2">
                  {suggestion.prompt}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
