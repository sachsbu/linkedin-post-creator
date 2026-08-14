import React, { useState, useEffect } from 'react';
import { X, Calendar, ArrowRight, FileText, Trash2, CheckSquare, Square, RefreshCw } from 'lucide-react';
import { PostResponse } from '../types';
import { deletePost, deletePostsBatch } from '../api/client';

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: PostResponse[];
  onSelectPost: (post: PostResponse) => void;
  onRefreshHistory: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelectPost,
  onRefreshHistory
}) => {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [isBatchDeleting, setIsBatchDeleting] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      onRefreshHistory();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const toggleSelect = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === history.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(history.map((p) => p.id));
    }
  };

  const handleDeleteSingle = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this post from database and local disk?')) return;

    setDeletingId(id);
    try {
      await deletePost(id);
      setSelectedIds((prev) => prev.filter((item) => item !== id));
      onRefreshHistory();
    } catch (err) {
      console.error('Delete post error:', err);
      alert('Failed to delete post.');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedIds.length === 0) return;
    if (!window.confirm(`Are you sure you want to delete ${selectedIds.length} selected post(s) from database and local storage?`)) return;

    setIsBatchDeleting(true);
    try {
      await deletePostsBatch(selectedIds);
      setSelectedIds([]);
      onRefreshHistory();
    } catch (err) {
      console.error('Batch delete error:', err);
      alert('Failed to delete selected posts.');
    } finally {
      setIsBatchDeleting(false);
    }
  };

  const allSelected = history.length > 0 && selectedIds.length === history.length;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl">
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-sky-400" />
            <h3 className="text-base font-bold text-slate-100">Generated Post History ({history.length})</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Toolbar Actions: Select All & Batch Delete */}
        {history.length > 0 && (
          <div className="px-4 py-2.5 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between">
            <button
              type="button"
              onClick={toggleSelectAll}
              className="flex items-center space-x-1.5 text-xs text-slate-300 hover:text-white transition-colors"
            >
              {allSelected ? (
                <CheckSquare className="w-4 h-4 text-sky-400" />
              ) : (
                <Square className="w-4 h-4 text-slate-500" />
              )}
              <span>{allSelected ? 'Deselect All' : 'Select All'}</span>
            </button>

            {selectedIds.length > 0 && (
              <button
                type="button"
                onClick={handleDeleteSelected}
                disabled={isBatchDeleting}
                className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 text-xs font-semibold transition-colors disabled:opacity-50"
              >
                {isBatchDeleting ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Trash2 className="w-3.5 h-3.5" />
                )}
                <span>Delete Selected ({selectedIds.length})</span>
              </button>
            )}
          </div>
        )}

        {/* Post List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {history.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-sm">
              No historical posts found.
            </div>
          ) : (
            history.map((post) => {
              const isSelected = selectedIds.includes(post.id);
              const isItemDeleting = deletingId === post.id;

              return (
                <div
                  key={post.id}
                  onClick={() => {
                    onSelectPost(post);
                    onClose();
                  }}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer group relative ${
                    isSelected
                      ? 'bg-sky-500/10 border-sky-500/40'
                      : 'bg-slate-800/40 border-slate-800 hover:bg-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
                    <div className="flex items-center space-x-2">
                      <button
                        type="button"
                        onClick={(e) => toggleSelect(post.id, e)}
                        className="text-slate-400 hover:text-sky-400"
                      >
                        {isSelected ? (
                          <CheckSquare className="w-4 h-4 text-sky-400" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-600 group-hover:text-slate-400" />
                        )}
                      </button>
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-3.5 h-3.5" />
                        <span>{new Date(post.created_at).toLocaleDateString()}</span>
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="uppercase text-[10px] font-bold px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                        {post.platform || 'linkedin'}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => handleDeleteSingle(post.id, e)}
                        disabled={isItemDeleting}
                        title="Delete post"
                        className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                      >
                        {isItemDeleting ? (
                          <RefreshCw className="w-3.5 h-3.5 animate-spin text-red-400" />
                        ) : (
                          <Trash2 className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <h4 className="text-sm font-semibold text-slate-200 group-hover:text-sky-300 line-clamp-2 pr-2">
                    {post.title}
                  </h4>

                  <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                    <span>{post.word_count} words</span>
                    <span className="flex items-center space-x-1 text-sky-400 font-medium group-hover:translate-x-1 transition-transform">
                      <span>View</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

