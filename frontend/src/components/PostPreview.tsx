import React, { useState } from 'react';
import {
  Copy,
  Check,
  ExternalLink,
  ImageIcon,
  RefreshCw,
  Share2,
  FileText,
  ThumbsUp,
  MessageCircle,
  Repeat2,
  Send,
  Globe
} from 'lucide-react';
import { PostResponse } from '../types';

interface PostPreviewProps {
  post: PostResponse | null;
  onRegenerate: () => void;
  isGenerating: boolean;
  onOpenExport: () => void;
}

export const PostPreview: React.FC<PostPreviewProps> = ({
  post,
  onRegenerate,
  isGenerating,
  onOpenExport
}) => {
  const [copied, setCopied] = useState(false);

  if (!post) {
    return (
      <div className="bg-slate-800/30 border border-dashed border-slate-700/80 rounded-2xl p-12 flex flex-col items-center justify-center text-center h-[520px]">
        <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500 mb-4">
          <FileText className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-semibold text-slate-300">No Post Generated Yet</h3>
        <p className="text-sm text-slate-500 max-w-sm mt-1">
          Select a trending news story from the left panel and click &quot;Generate Post&quot; to build an engaging LinkedIn update.
        </p>
      </div>
    );
  }

  const copyToClipboard = () => {
    const fullText = `${post.linkedin_caption}\n\n${post.hashtags.join(' ')}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const imgUrl = post.image_path.startsWith('http')
    ? post.image_path
    : `/output/${post.output_folder.split(/[\\/]/).pop()}/${post.image_path.split(/[\\/]/).pop()}`;

  return (
    <div className="flex flex-col space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-800/60 border border-slate-700/80 p-3.5 rounded-2xl">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20">
            Tone: {post.tone.toUpperCase()}
          </span>
          <span
            className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${
              post.word_count <= 180
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
            }`}
          >
            {post.word_count} / 180 Words
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onRegenerate}
            disabled={isGenerating}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isGenerating ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>

          <button
            onClick={onOpenExport}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Export</span>
          </button>

          <button
            onClick={copyToClipboard}
            className="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold shadow-md shadow-sky-600/20 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-white" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied!' : 'Copy Caption'}</span>
          </button>
        </div>
      </div>

      {/* Realistic LinkedIn Feed Card Preview */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        {/* LinkedIn User Profile Header */}
        <div className="p-4 border-b border-slate-800/80 flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-blue-600 to-sky-400 text-white flex items-center justify-center font-bold text-base shadow">
              TC
            </div>
            <div>
              <div className="flex items-center space-x-1">
                <h4 className="text-sm font-bold text-slate-100">Tech Curator</h4>
                <span className="text-xs text-slate-500">• 1st</span>
              </div>
              <p className="text-xs text-slate-400">Engineering Thought Leadership | AI & Tech Trends</p>
              <div className="flex items-center space-x-1 text-[10px] text-slate-500 mt-0.5">
                <span>Just now</span>
                <span>•</span>
                <Globe className="w-3 h-3 text-slate-500" />
              </div>
            </div>
          </div>
        </div>

        {/* Post Text Body */}
        <div className="p-4 text-sm text-slate-200 leading-relaxed whitespace-pre-wrap font-sans">
          {post.linkedin_caption}
          <div className="mt-3 flex flex-wrap gap-1.5">
            {post.hashtags.map((tag, idx) => (
              <span key={idx} className="text-sky-400 font-medium hover:underline cursor-pointer">
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Attached Article / Social Image Preview */}
        {imgUrl && (
          <div className="relative group border-t border-slate-800 bg-black/40">
            <img
              src={imgUrl}
              alt="Post image preview"
              className="w-full max-h-[380px] object-cover"
              onError={(e) => {
                // If image load fails, hide image element
                (e.target as HTMLElement).style.display = 'none';
              }}
            />
            <div className="p-3 bg-slate-900/90 border-t border-slate-800 flex items-center justify-between text-xs">
              <div className="truncate max-w-md">
                <div className="font-semibold text-slate-200 truncate">{post.title}</div>
                <div className="text-slate-500 text-[11px] truncate">{post.source_url}</div>
              </div>
              <div className="flex items-center space-x-2">
                <a
                  href={imgUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-xs text-sky-400 hover:text-sky-300 font-medium px-2.5 py-1 rounded bg-sky-500/10 border border-sky-500/20"
                >
                  <ImageIcon className="w-3.5 h-3.5" />
                  <span>Open Image</span>
                </a>
                <a
                  href={post.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-xs text-slate-300 hover:text-white font-medium px-2.5 py-1 rounded bg-slate-800 border border-slate-700"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Source</span>
                </a>
              </div>
            </div>
          </div>
        )}

        {/* LinkedIn Mock Reactions Footer */}
        <div className="p-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 bg-slate-900/40">
          <div className="flex items-center space-x-6 w-full justify-around">
            <button className="flex items-center space-x-1.5 hover:text-slate-200 py-1 px-2 rounded hover:bg-slate-800/60">
              <ThumbsUp className="w-4 h-4 text-sky-400" />
              <span>Like</span>
            </button>
            <button className="flex items-center space-x-1.5 hover:text-slate-200 py-1 px-2 rounded hover:bg-slate-800/60">
              <MessageCircle className="w-4 h-4" />
              <span>Comment</span>
            </button>
            <button className="flex items-center space-x-1.5 hover:text-slate-200 py-1 px-2 rounded hover:bg-slate-800/60">
              <Repeat2 className="w-4 h-4" />
              <span>Repost</span>
            </button>
            <button className="flex items-center space-x-1.5 hover:text-slate-200 py-1 px-2 rounded hover:bg-slate-800/60">
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>

      {/* AI Structured Summary Accordion Box */}
      <div className="bg-slate-800/30 border border-slate-700/60 rounded-2xl p-4">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          AI Summarization Insights
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/40">
            <span className="font-semibold text-sky-400 block mb-1">What Happened:</span>
            <p className="text-slate-300">{post.summary.what_happened}</p>
          </div>
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/40">
            <span className="font-semibold text-purple-400 block mb-1">Why It Matters:</span>
            <p className="text-slate-300">{post.summary.why_it_matters}</p>
          </div>
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/40">
            <span className="font-semibold text-emerald-400 block mb-1">Impact:</span>
            <p className="text-slate-300">{post.summary.impact}</p>
          </div>
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/40">
            <span className="font-semibold text-amber-400 block mb-1">Key Takeaway:</span>
            <p className="text-slate-300">{post.summary.key_takeaway}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
