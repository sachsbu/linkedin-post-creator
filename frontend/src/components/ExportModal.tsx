import React from 'react';
import { X, Download, FileCode, FileText } from 'lucide-react';
import { PostResponse } from '../types';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  post: PostResponse | null;
}

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose, post }) => {
  if (!isOpen || !post) return null;

  const downloadFile = (format: 'md' | 'txt' | 'json' | 'html') => {
    const url = `/api/posts/${post.id}/export?format=${format}`;
    window.open(url, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <Download className="w-5 h-5 text-sky-400" />
            <span>Export LinkedIn Post</span>
          </h3>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-slate-400 mb-4">
          Download artifacts and captions in your preferred file format:
        </p>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => downloadFile('md')}
            className="flex flex-col items-center justify-center p-4 rounded-xl border border-slate-800 bg-slate-800/40 hover:bg-slate-800 hover:border-sky-500/50 transition-all text-slate-200 group"
          >
            <FileText className="w-8 h-8 text-sky-400 mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-bold">Markdown (.md)</span>
            <span className="text-[10px] text-slate-500 mt-1">Full post + metadata</span>
          </button>

          <button
            onClick={() => downloadFile('html')}
            className="flex flex-col items-center justify-center p-4 rounded-xl border border-slate-800 bg-slate-800/40 hover:bg-slate-800 hover:border-sky-500/50 transition-all text-slate-200 group"
          >
            <FileCode className="w-8 h-8 text-purple-400 mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-bold">HTML Card (.html)</span>
            <span className="text-[10px] text-slate-500 mt-1">Styled preview layout</span>
          </button>

          <button
            onClick={() => downloadFile('txt')}
            className="flex flex-col items-center justify-center p-4 rounded-xl border border-slate-800 bg-slate-800/40 hover:bg-slate-800 hover:border-sky-500/50 transition-all text-slate-200 group"
          >
            <FileText className="w-8 h-8 text-emerald-400 mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-bold">Plain Text (.txt)</span>
            <span className="text-[10px] text-slate-500 mt-1">Caption + hashtags</span>
          </button>

          <button
            onClick={() => downloadFile('json')}
            className="flex flex-col items-center justify-center p-4 rounded-xl border border-slate-800 bg-slate-800/40 hover:bg-slate-800 hover:border-sky-500/50 transition-all text-slate-200 group"
          >
            <FileCode className="w-8 h-8 text-amber-400 mb-2 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-bold">Metadata (.json)</span>
            <span className="text-[10px] text-slate-500 mt-1">Full schema data</span>
          </button>
        </div>
      </div>
    </div>
  );
};
