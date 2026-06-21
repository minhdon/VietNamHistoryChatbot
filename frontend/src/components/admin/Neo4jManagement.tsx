import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Edit, Plus, X } from 'lucide-react';

interface Chunk {
  id: string;
  text: string;
}

export function Neo4jManagement() {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingChunkId, setEditingChunkId] = useState<string | null>(null);
  const [textInput, setTextInput] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetchChunks();
  }, []);

  const fetchChunks = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/neo4j/chunks', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setChunks(data);
      }
    } catch (error) {
      console.error('Failed to fetch Neo4j chunks', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (chunk?: Chunk) => {
    if (chunk) {
      setEditingChunkId(chunk.id);
      setTextInput(chunk.text);
    } else {
      setEditingChunkId(null);
      setTextInput('');
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingChunkId(null);
    setTextInput('');
  };

  const handleSave = async () => {
    if (!textInput.trim()) return;
    setIsSaving(true);

    try {
      if (editingChunkId) {
        // Update existing
        const res = await fetch(`http://localhost:8000/api/admin/neo4j/chunks/${editingChunkId}`, {
          method: 'PUT',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text: textInput })
        });
        if (res.ok) {
          const updatedChunk = await res.json();
          setChunks(chunks.map(c => c.id === editingChunkId ? updatedChunk : c));
          handleCloseModal();
        } else {
          alert('Failed to update document');
        }
      } else {
        // Create new
        const res = await fetch(`http://localhost:8000/api/admin/neo4j/chunks`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text: textInput })
        });
        if (res.ok) {
          const newChunk = await res.json();
          setChunks([newChunk, ...chunks]);
          handleCloseModal();
        } else {
          alert('Failed to create document');
        }
      }
    } catch (error) {
      console.error('Failed to save document', error);
      alert('An error occurred while saving the document.');
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) return <div>Loading documents...</div>;

  return (
    <div className="bg-[var(--color-sidebar)] rounded-lg border border-[var(--color-border)] p-4 shadow-sm relative">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-[var(--color-text-main)]">Neo4j Documents (Chunks)</h2>
        <button 
          onClick={() => handleOpenModal()}
          className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          Add Document
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-[var(--color-text-main)]">
          <thead className="bg-[var(--color-main)] text-[var(--color-text-secondary)] border-b border-[var(--color-border)]">
            <tr>
              <th className="px-4 py-3 font-medium w-1/4">ID</th>
              <th className="px-4 py-3 font-medium">Text</th>
              <th className="px-4 py-3 font-medium text-right w-24">Actions</th>
            </tr>
          </thead>
          <tbody>
            {chunks.map(chunk => (
              <tr key={chunk.id} className="border-b border-[var(--color-border)] hover:bg-[var(--color-main)]/50 transition-colors">
                <td className="px-4 py-3 font-mono text-xs text-blue-500">{chunk.id}</td>
                <td className="px-4 py-3 max-w-xl truncate" title={chunk.text}>{chunk.text}</td>
                <td className="px-4 py-3 text-right">
                  <button 
                    onClick={() => handleOpenModal(chunk)}
                    className="text-blue-500 hover:text-blue-600 p-1 rounded transition-colors"
                    title="Edit Document"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {chunks.length === 0 && (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-center text-[var(--color-text-secondary)]">
                  No documents found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[var(--color-sidebar)] border border-[var(--color-border)] rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)] bg-[var(--color-main)]">
              <h3 className="font-semibold text-[var(--color-text-main)]">
                {editingChunkId ? 'Edit Document' : 'New Document'}
              </h3>
              <button 
                onClick={handleCloseModal}
                className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-main)] p-1 rounded-lg hover:bg-[var(--color-border)] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4 flex-1">
              <label className="block text-sm font-medium text-[var(--color-text-main)] mb-2">
                Document Text
              </label>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                className="w-full h-64 p-3 bg-[var(--color-main)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-main)] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-sans"
                placeholder="Enter document text here..."
              />
            </div>
            <div className="p-4 border-t border-[var(--color-border)] bg-[var(--color-main)] flex justify-end gap-2">
              {isSaving && (
                <span className="mr-auto text-sm text-amber-500 font-medium self-center animate-pulse">
                  Đang nhờ AI đọc và trích xuất dữ liệu. Vui lòng chờ...
                </span>
              )}
              <button 
                onClick={handleCloseModal}
                disabled={isSaving}
                className="px-4 py-2 rounded-lg text-sm font-medium text-[var(--color-text-main)] hover:bg-[var(--color-border)] transition-colors border border-[var(--color-border)] disabled:opacity-50"
              >
                Cancel
              </button>
              <button 
                onClick={handleSave}
                disabled={!textInput.trim() || isSaving}
                className="px-4 py-2 rounded-lg text-sm font-medium bg-blue-500 hover:bg-blue-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
