import React, { useRef, useEffect, useState } from 'react';
import { ArrowUp, Paperclip, X, Loader2 } from 'lucide-react';
import { cn } from './Sidebar';

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  selectedFile: File | null;
  setSelectedFile: (file: File | null) => void;
}

export function ChatInput({ input, setInput, onSubmit, isLoading, selectedFile, setSelectedFile }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loadingOcr, setLoadingOcr] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Tự động giãn dòng cho textarea dựa theo độ dài văn bản nhập vào
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  // Hàm xử lý gọi API OCR bóc tách chữ từ file
  const processOcrFile = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    setLoadingOcr(false);
    setLoadingOcr(true);
    
    try {
      const response = await fetch("http://localhost:8000/api/ocr/extract", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // Đổ thẳng văn bản lịch sử bóc được vào khung chat
        setInput(data.extracted_text);
      } else {
        const errorData = await response.json();
        alert(`Lỗi OCR: ${errorData.detail}`);
        setSelectedFile(null);
      }
    } catch (error) {
      console.error("Lỗi kết nối API OCR:", error);
      alert("Không thể kết nối đến máy chủ xử lý OCR.");
      setSelectedFile(null);
    } finally {
      setLoadingOcr(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isLoading && !loadingOcr) {
        onSubmit();
      }
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    if (e.clipboardData.files && e.clipboardData.files.length > 0) {
      const file = e.clipboardData.files[0];
      if (file.type.startsWith('image/') || file.type === 'application/pdf') {
        setSelectedFile(file);
        processOcrFile(file); // Chạy OCR ngay khi paste
        e.preventDefault();
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      processOcrFile(file); // Chạy OCR ngay khi chọn file thành công
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/') || file.type === 'application/pdf') {
        setSelectedFile(file);
        processOcrFile(file);
      }
    }
  };

  return (
    <div 
      className="w-full max-w-3xl mx-auto px-4 pb-6 pt-2"
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className={cn(
        "relative flex flex-col w-full border rounded-2xl shadow-sm transition-all",
        isDragging 
          ? "border-blue-500 bg-blue-500/5 shadow-md" 
          : "border-[var(--color-border)] bg-[var(--color-input)] hover:shadow-md focus-within:shadow-md focus-within:border-[var(--color-text-secondary)]"
      )}>
        
        {/* Thanh hiển thị File đang được tải lên / xử lý */}
        {selectedFile && (
          <div className="mx-4 mt-3 px-3 py-2 bg-[var(--color-border)] rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-2 max-w-[80%]">
              {loadingOcr && <Loader2 className="w-4 h-4 animate-spin text-blue-500 flex-shrink-0" />}
              <span className="text-sm truncate text-[var(--color-text-main)]">
                {selectedFile.name || 'Pasted file'} 
                {loadingOcr && <span className="text-xs text-blue-400 ml-2">(Đang quét chữ...)</span>}
              </span>
            </div>
            <button 
              type="button"
              disabled={loadingOcr}
              onClick={() => {
                setSelectedFile(null);
                setInput("");
              }}
              className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-main)] disabled:opacity-50"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <div className="flex items-end w-full">
          {/* Nút đính kèm File */}
          <button
            type="button"
            disabled={isLoading || loadingOcr}
            onClick={() => fileInputRef.current?.click()}
            className="p-3 ml-2 mb-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-text-main)] transition-colors disabled:opacity-40"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          
          <input 
            type="file" 
            ref={fileInputRef} 
            className="hidden" 
            accept="image/*,.pdf"
            onChange={handleFileChange}
          />

          {/* Ô nhập câu hỏi dạng văn bản */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder={loadingOcr ? "Extracting text from document, please wait..." : "Ask me about Vietnam History..."}
            className="w-full max-h-[200px] min-h-[56px] py-4 pl-2 pr-14 bg-transparent border-none resize-none focus:outline-none focus:ring-0 text-[var(--color-text-main)] placeholder-[var(--color-text-secondary)]"
            rows={1}
            disabled={isLoading || loadingOcr}
          />

          {/* Nút Gửi tin nhắn */}
          <div className="absolute right-3 bottom-3">
            <button
              type="button"
              onClick={() => {
                if (input.trim() && !isLoading && !loadingOcr) onSubmit();
              }}
              disabled={!input.trim() || isLoading || loadingOcr}
              className={cn(
                "p-1.5 rounded-full flex items-center justify-center transition-colors",
                input.trim() && !isLoading && !loadingOcr
                  ? "bg-[var(--color-accent)] text-[var(--color-main)] hover:bg-[var(--color-accent-hover)]"
                  : "bg-[var(--color-border)] text-[var(--color-text-secondary)] opacity-50 cursor-not-allowed"
              )}
            >
              <ArrowUp className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="text-center mt-2 text-xs text-[var(--color-text-secondary)]">
        History Chatbot can make mistakes. Consider verifying important information.
      </div>
    </div>
  );
}