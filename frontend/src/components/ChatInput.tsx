import React, { useRef, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';
import { cn } from './Sidebar';

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

export function ChatInput({ input, setInput, onSubmit, isLoading }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isLoading) {
        onSubmit();
      }
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-6 pt-2">
      <div className="relative flex items-end w-full border border-[var(--color-border)] bg-[var(--color-input)] rounded-2xl shadow-sm hover:shadow-md transition-shadow focus-within:shadow-md focus-within:border-[var(--color-text-secondary)]">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me about Vietnam History..."
          className="w-full max-h-[200px] min-h-[56px] py-4 pl-4 pr-12 bg-transparent border-none resize-none focus:outline-none focus:ring-0 text-[var(--color-text-main)] placeholder-[var(--color-text-secondary)]"
          rows={1}
          disabled={isLoading}
        />
        <div className="absolute right-3 bottom-3">
          <button
            onClick={() => {
              if (input.trim() && !isLoading) onSubmit();
            }}
            disabled={!input.trim() || isLoading}
            className={cn(
              "p-1.5 rounded-full flex items-center justify-center transition-colors",
              input.trim() && !isLoading
                ? "bg-[var(--color-accent)] text-[var(--color-main)] hover:bg-[var(--color-accent-hover)]"
                : "bg-[var(--color-border)] text-[var(--color-text-secondary)] opacity-50 cursor-not-allowed"
            )}
          >
            <ArrowUp className="w-5 h-5" />
          </button>
        </div>
      </div>
      <div className="text-center mt-2 text-xs text-[var(--color-text-secondary)]">
        History Chatbot can make mistakes. Consider verifying important information.
      </div>
    </div>
  );
}
