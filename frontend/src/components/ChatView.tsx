import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot } from 'lucide-react';
import { cn } from './Sidebar';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
}

interface ChatViewProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatView({ messages, isLoading }: ChatViewProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto w-full px-4 pt-6 pb-2">
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex w-full gap-4",
              message.role === 'user' ? "justify-end" : "justify-start"
            )}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-[var(--color-border)] flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 text-[var(--color-text-main)]" />
              </div>
            )}
            
            <div className={cn(
              "max-w-[85%] rounded-2xl px-5 py-3.5",
              message.role === 'user' 
                ? "bg-[var(--color-user-bg)] text-[var(--color-text-main)] rounded-tr-sm"
                : "bg-[var(--color-assistant-bg)] border border-[var(--color-border)] rounded-tl-sm"
            )}>
              {message.role === 'user' ? (
                <div className="whitespace-pre-wrap">{message.content}</div>
              ) : (
                <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
                  {message.content ? (
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  ) : (
                    <div className="flex items-center gap-1 h-6">
                      <span className="w-2 h-2 rounded-full bg-[var(--color-text-secondary)] animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 rounded-full bg-[var(--color-text-secondary)] animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 rounded-full bg-[var(--color-text-secondary)] animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  )}
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-[var(--color-border)]">
                      <p className="text-xs font-semibold text-[var(--color-text-secondary)] mb-2 uppercase tracking-wider">Sources</p>
                      <div className="flex flex-col gap-2">
                        {message.sources.map((source, idx) => (
                          <div key={idx} className="text-xs p-2 rounded-md bg-[var(--color-border)] opacity-80 truncate">
                            {source.text}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  );
}
