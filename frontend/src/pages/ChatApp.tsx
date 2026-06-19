import React, { useState } from 'react';
import { Menu } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { Homepage } from '../components/Homepage';
import { ChatView, type Message } from '../components/ChatView';
import { ChatInput } from '../components/ChatInput';
import { useAuth } from '../context/AuthContext';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { token, logout, user } = useAuth();

  const handleNewChat = () => {
    setMessages([]);
    setInput('');
    setSelectedFile(null);
    setIsSidebarOpen(false);
    setSessionId(crypto.randomUUID());
  };

  const handleSelectSession = async (id: string) => {
    setSessionId(id);
    setIsSidebarOpen(false);
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/sessions/${id}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Error fetching session messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPrompt = (prompt: string) => {
    setInput(prompt);
    // Optionally auto-submit:
    // submitMessage(prompt);
  };

  const submitMessage = async (textToSubmit: string = input) => {
    if (!textToSubmit.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSubmit.trim()
    };

    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      sources: []
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('question', textToSubmit.trim());
      if (sessionId) formData.append('session_id', sessionId);
      if (selectedFile) formData.append('file', selectedFile);

      setSelectedFile(null); // Clear after sending

      const response = await fetch('http://localhost:8000/api/stream', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      if (!response.body) {
        throw new Error('No readable stream available');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6).trim();
            if (!dataStr) continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'sources') {
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMessageId 
                    ? { ...msg, sources: data.data }
                    : msg
                ));
              } else if (data.type === 'content') {
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMessageId 
                    ? { ...msg, content: msg.content + data.delta }
                    : msg
                ));
              }
            } catch (err) {
              console.error('Error parsing SSE data:', err, dataStr);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error in chat stream:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessageId 
          ? { ...msg, content: msg.content + '\n\n**Error:** Failed to connect to server.' }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-[var(--color-main)] overflow-hidden font-sans">
      <Sidebar 
        isOpen={isSidebarOpen} 
        setIsOpen={setIsSidebarOpen} 
        onNewChat={handleNewChat} 
        onSelectSession={handleSelectSession}
      />

      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Mobile Header */}
        <div className="md:hidden flex items-center justify-between p-3 border-b border-[var(--color-border)] bg-[var(--color-main)] z-10 sticky top-0">
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 -ml-2 rounded-lg hover:bg-[var(--color-border)] text-[var(--color-text-main)]"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="font-medium text-sm">History Chatbot</div>
          <button onClick={logout} className="p-2 -mr-2 rounded-lg hover:bg-[var(--color-border)] text-red-500 text-sm font-medium">
            Đăng xuất
          </button>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col relative overflow-hidden">
          {messages.length === 0 ? (
            <Homepage onSelectPrompt={handleSelectPrompt} />
          ) : (
            <ChatView messages={messages} isLoading={isLoading} />
          )}

          <div className="w-full bg-gradient-to-t from-[var(--color-main)] via-[var(--color-main)] to-transparent pt-6">
            <ChatInput 
              input={input} 
              setInput={setInput} 
              onSubmit={() => submitMessage()} 
              isLoading={isLoading} 
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
