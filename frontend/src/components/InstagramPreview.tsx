import React, { useState } from 'react';
import { Copy, Download, Check, Sparkles, Instagram, Hash, Image as ImageIcon, Video as VideoIcon } from 'lucide-react';
import { InstagramPostResponse } from '../types';

interface InstagramPreviewProps {
  post: InstagramPostResponse | null;
  isGenerating: boolean;
}

export const InstagramPreview: React.FC<InstagramPreviewProps> = ({ post, isGenerating }) => {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  if (isGenerating) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center shadow-xl space-y-4 flex flex-col items-center justify-center min-h-[480px]">
        <div className="relative">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-pink-500 via-purple-500 to-amber-500 flex items-center justify-center text-white shadow-xl shadow-pink-500/25 animate-pulse">
            <Instagram className="w-8 h-8" />
          </div>
        </div>
        <div className="space-y-1">
          <h3 className="text-base font-bold text-slate-100">Crafting Instagram Post...</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Generating creative 2-sentence caption and 8–10 dynamic hashtags tuned for maximum engagement.
          </p>
        </div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center shadow-xl space-y-4 flex flex-col items-center justify-center min-h-[480px]">
        <div className="w-16 h-16 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-pink-400 mx-auto">
          <Instagram className="w-8 h-8" />
        </div>
        <div className="space-y-1">
          <h3 className="text-base font-bold text-slate-200">No Post Generated Yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Fill in your post idea and upload media on the left form, then click &quot;Generate Instagram Post&quot;.
          </p>
        </div>
      </div>
    );
  }

  const fullText = `${post.caption}\n\n${post.hashtags.join(' ')}`;

  const handleCopy = (text: string, sectionName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(sectionName);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const handleDownloadTxt = () => {
    const element = document.createElement('a');
    const file = new Blob([fullText], { type: 'text/plain;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = `instagram_post_${post.id || 'draft'}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Resolve media URL for display
  const mediaUrl = post.media_path
    ? post.media_path.startsWith('http') || post.media_path.startsWith('blob:')
      ? post.media_path
      : `/output/uploads/${post.media_path.split(/[/\\]/).pop()}`
    : null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col space-y-6">
      {/* Top Header & Metadata */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-pink-500 via-purple-500 to-amber-500 flex items-center justify-center text-white shadow-md">
            <Instagram className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Instagram Post Output</h2>
            <p className="text-[11px] text-slate-400">Model used: {post.model_used}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[10px] px-2.5 py-1 rounded-full bg-pink-500/10 text-pink-400 border border-pink-500/20 font-mono">
            {post.hashtags.length} Hashtags
          </span>
        </div>
      </div>

      {/* Main Grid: Uploaded Media Preview + Generated Content */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Sub-column: Media Preview (5 cols) */}
        <div className="md:col-span-5 flex flex-col space-y-2">
          <div className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
            {post.media_type === 'video' ? <VideoIcon className="w-4 h-4 text-purple-400" /> : <ImageIcon className="w-4 h-4 text-pink-400" />}
            <span>Uploaded Media Preview</span>
          </div>

          <div className="rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center min-h-[220px] max-h-[340px] p-2">
            {mediaUrl ? (
              post.media_type === 'video' ? (
                <video src={mediaUrl} controls className="max-h-[320px] w-full object-contain rounded-lg" />
              ) : (
                <img src={mediaUrl} alt="Uploaded social media post" className="max-h-[320px] w-full object-contain rounded-lg" />
              )
            ) : (
              <div className="text-center p-6 text-slate-500 text-xs space-y-2">
                <ImageIcon className="w-8 h-8 mx-auto text-slate-600" />
                <p>No media attached to this post.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Sub-column: Caption & Hashtags (7 cols) */}
        <div className="md:col-span-7 flex flex-col space-y-4">
          {/* Caption Box */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-pink-400" />
                <span>Generated Caption (Max 2 Sentences)</span>
              </span>
              <button
                onClick={() => handleCopy(post.caption, 'caption')}
                className="flex items-center space-x-1 text-[11px] text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded transition-colors"
              >
                {copiedSection === 'caption' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSection === 'caption' ? 'Copied' : 'Copy Caption'}</span>
              </button>
            </div>
            <p className="text-xs sm:text-sm text-slate-100 leading-relaxed font-normal whitespace-pre-wrap">
              {post.caption}
            </p>
          </div>

          {/* Hashtags Box */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Hash className="w-3.5 h-3.5 text-purple-400" />
                <span>Dynamic Hashtags ({post.hashtags.length})</span>
              </span>
              <button
                onClick={() => handleCopy(post.hashtags.join(' '), 'hashtags')}
                className="flex items-center space-x-1 text-[11px] text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded transition-colors"
              >
                {copiedSection === 'hashtags' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSection === 'hashtags' ? 'Copied' : 'Copy Hashtags'}</span>
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {post.hashtags.map((tag, idx) => (
                <span
                  key={idx}
                  className="text-xs bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 px-2 py-1 rounded-md font-mono"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons Toolbar */}
      <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => handleCopy(post.caption, 'caption')}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            {copiedSection === 'caption' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-pink-400" />}
            <span>Copy Caption</span>
          </button>

          <button
            onClick={() => handleCopy(post.hashtags.join(' '), 'hashtags')}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            {copiedSection === 'hashtags' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Hash className="w-3.5 h-3.5 text-purple-400" />}
            <span>Copy Hashtags</span>
          </button>

          <button
            onClick={() => handleCopy(fullText, 'all')}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            {copiedSection === 'all' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-sky-400" />}
            <span>Copy All</span>
          </button>
        </div>

        <button
          onClick={handleDownloadTxt}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-400 hover:to-purple-500 text-white text-xs font-bold shadow-md transition-all"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Download Caption (.txt)</span>
        </button>
      </div>
    </div>
  );
};
