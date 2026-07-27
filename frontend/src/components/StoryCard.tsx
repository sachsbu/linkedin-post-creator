import React from 'react';
import { ExternalLink, MessageSquare, Flame, User, ArrowUpRight } from 'lucide-react';
import { Story } from '../types';

interface StoryCardProps {
  story: Story;
  isSelected: boolean;
  onSelect: (story: Story) => void;
  onGenerate: (story: Story) => void;
  isGenerating: boolean;
}

export const StoryCard: React.FC<StoryCardProps> = ({
  story,
  isSelected,
  onSelect,
  onGenerate,
  isGenerating
}) => {
  return (
    <div
      onClick={() => onSelect(story)}
      className={`group relative p-4 rounded-xl border transition-all cursor-pointer ${
        isSelected
          ? 'bg-slate-800/90 border-sky-500 shadow-md shadow-sky-500/10'
          : 'bg-slate-800/40 border-slate-700/60 hover:bg-slate-800/80 hover:border-slate-600'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-100 group-hover:text-sky-300 transition-colors line-clamp-2">
          {story.title}
        </h3>
        <a
          href={story.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="text-slate-400 hover:text-slate-200 p-1"
          title="Open Source Article"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1 text-amber-400 font-medium">
            <Flame className="w-3.5 h-3.5" />
            <span>{story.score}</span>
          </span>
          <span className="flex items-center space-x-1">
            <MessageSquare className="w-3.5 h-3.5 text-slate-400" />
            <span>{story.comments_count}</span>
          </span>
          <span className="flex items-center space-x-1 text-slate-400">
            <User className="w-3.5 h-3.5" />
            <span>{story.author}</span>
          </span>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-700/60 text-slate-300 border border-slate-600/50">
            {story.source_name}
          </span>
        </div>


        <button
          onClick={(e) => {
            e.stopPropagation();
            onGenerate(story);
          }}
          disabled={isGenerating}
          className="flex items-center space-x-1 text-xs font-semibold text-sky-400 hover:text-sky-300 bg-sky-500/10 hover:bg-sky-500/20 px-2.5 py-1 rounded-md border border-sky-500/20 transition-all"
        >
          <span>Generate</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
