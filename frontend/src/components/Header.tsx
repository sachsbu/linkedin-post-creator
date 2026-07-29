import React from 'react';
import { Sparkles, History, Linkedin, Instagram, Twitter, Facebook, MessageSquare, BookOpen, Code2 } from 'lucide-react';
import { PlatformOption } from '../types';

interface HeaderProps {
  selectedPlatform: PlatformOption;
  onSelectPlatform: (platform: PlatformOption) => void;
  onOpenHistory: () => void;
}

export const Header: React.FC<HeaderProps> = ({ selectedPlatform, onSelectPlatform, onOpenHistory }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Logo & App Title */}
        <div className="flex items-center space-x-3 shrink-0">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold text-slate-100 flex items-center space-x-2">
              <span>AI Social Post Generator</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium">
                Multi-Platform
              </span>
            </h1>
            <p className="text-xs text-slate-400 hidden sm:block">Generate engaging content tailored for social platforms</p>
          </div>
        </div>

        {/* Platform Selector Tabs */}
        <div className="flex items-center space-x-1 sm:space-x-2 bg-slate-950/80 p-1 rounded-xl border border-slate-800 overflow-x-auto">
          {/* Active Platform: LinkedIn */}
          <button
            onClick={() => onSelectPlatform('linkedin')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedPlatform === 'linkedin'
                ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Linkedin className="w-3.5 h-3.5 text-sky-400" />
            <span>LinkedIn</span>
          </button>

          {/* Active Platform: Instagram */}
          <button
            onClick={() => onSelectPlatform('instagram')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedPlatform === 'instagram'
                ? 'bg-gradient-to-r from-pink-500/20 via-purple-500/20 to-amber-500/20 text-pink-300 border border-pink-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Instagram className="w-3.5 h-3.5 text-pink-400" />
            <span>Instagram</span>
          </button>

          {/* Extensible Future Platforms (Disabled state) */}
          <div className="hidden lg:flex items-center space-x-1 pl-1 border-l border-slate-800">
            <span
              title="X (Twitter) - Coming Soon"
              className="flex items-center space-x-1 px-2 py-1 rounded text-[11px] text-slate-600 cursor-not-allowed opacity-60"
            >
              <Twitter className="w-3 h-3" />
              <span>X</span>
            </span>
            <span
              title="Facebook - Coming Soon"
              className="flex items-center space-x-1 px-2 py-1 rounded text-[11px] text-slate-600 cursor-not-allowed opacity-60"
            >
              <Facebook className="w-3 h-3" />
              <span>FB</span>
            </span>
            <span
              title="Threads - Coming Soon"
              className="flex items-center space-x-1 px-2 py-1 rounded text-[11px] text-slate-600 cursor-not-allowed opacity-60"
            >
              <MessageSquare className="w-3 h-3" />
              <span>Threads</span>
            </span>
            <span
              title="Medium - Coming Soon"
              className="flex items-center space-x-1 px-2 py-1 rounded text-[11px] text-slate-600 cursor-not-allowed opacity-60"
            >
              <BookOpen className="w-3 h-3" />
              <span>Medium</span>
            </span>
            <span
              title="Dev.to - Coming Soon"
              className="flex items-center space-x-1 px-2 py-1 rounded text-[11px] text-slate-600 cursor-not-allowed opacity-60"
            >
              <Code2 className="w-3 h-3" />
              <span>Dev.to</span>
            </span>
          </div>
        </div>

        {/* History Action */}
        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={onOpenHistory}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/60 hover:bg-slate-800 text-slate-200 text-xs font-medium transition-colors"
          >
            <History className="w-4 h-4 text-sky-400" />
            <span>History</span>
          </button>
        </div>
      </div>
    </header>
  );
};

