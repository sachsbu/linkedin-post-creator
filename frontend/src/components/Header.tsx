import React from 'react';
import { Sparkles, History, SlidersHorizontal } from 'lucide-react';


interface HeaderProps {
  onOpenHistory: () => void;
  onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenHistory, onOpenSettings }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
              <span>LinkedIn Tech Post Generator</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium">
                Auto AI
              </span>
            </h1>
            <p className="text-xs text-slate-400">Discover trending news & generate high-converting posts</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenSettings}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            title="Settings & Provider Config"
          >
            <SlidersHorizontal className="w-5 h-5" />
          </button>
          
          <button
            onClick={onOpenHistory}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/60 hover:bg-slate-800 text-slate-200 text-sm font-medium transition-colors"
          >
            <History className="w-4 h-4 text-sky-400" />
            <span>History</span>
          </button>
        </div>
      </div>
    </header>
  );
};
