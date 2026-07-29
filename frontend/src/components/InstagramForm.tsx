import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, Video as VideoIcon, Sparkles, AlertCircle, AlertTriangle, CheckCircle2, RefreshCw, X, Lightbulb } from 'lucide-react';
import { ProviderOption, MediaValidationResult } from '../types';
import { ProviderSelector } from './ProviderSelector';
import { uploadMedia } from '../api/client';

interface InstagramFormProps {
  onGenerate: (prompt: string, mediaPath?: string, mediaType?: 'image' | 'video', provider?: ProviderOption) => void;
  isGenerating: boolean;
  provider: ProviderOption;
  onSelectProvider: (p: ProviderOption) => void;
}

const SAMPLE_IDEAS = [
  "Launching our AI automation platform",
  "Sharing product update",
  "Announcing new feature",
  "Behind-the-scenes",
  "Developer tip",
  "Startup milestone"
];

export const InstagramForm: React.FC<InstagramFormProps> = ({
  onGenerate,
  isGenerating,
  provider,
  onSelectProvider
}) => {
  const [prompt, setPrompt] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [mediaPreviewUrl, setMediaPreviewUrl] = useState<string | null>(null);
  const [mediaType, setMediaType] = useState<'image' | 'video'>('image');
  const [uploadedPath, setUploadedPath] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [validationResult, setValidationResult] = useState<MediaValidationResult | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (file: File) => {
    setUploadError(null);
    setSelectedFile(file);
    const isVid = file.type.startsWith('video/') || file.name.endsWith('.mp4') || file.name.endsWith('.mov');
    const type: 'image' | 'video' = isVid ? 'video' : 'image';
    setMediaType(type);

    // Create local object URL for instant preview
    const previewUrl = URL.createObjectURL(file);
    setMediaPreviewUrl(previewUrl);

    // Upload & validate via backend MediaValidationService
    setIsUploading(true);
    try {
      const res = await uploadMedia(file);
      setValidationResult(res);
      setUploadedPath(res.filename);
      if (!res.is_valid && res.errors.length > 0) {
        setUploadError(res.errors.join(' '));
      }
    } catch (err: any) {
      setUploadError(err?.response?.data?.detail || 'Failed to upload and validate media.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveMedia = () => {
    setSelectedFile(null);
    if (mediaPreviewUrl) {
      URL.revokeObjectURL(mediaPreviewUrl);
    }
    setMediaPreviewUrl(null);
    setUploadedPath(null);
    setValidationResult(null);
    setUploadError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onGenerate(prompt.trim(), uploadedPath || undefined, mediaType, provider);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-pink-500 to-amber-500 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-pink-500/20">
            IG
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Instagram Post Creator</h2>
            <p className="text-[11px] text-slate-400">Generate creative 2-sentence captions & dynamic hashtags</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* 1. Media Upload Section */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-200 flex items-center justify-between">
            <span className="flex items-center space-x-1.5">
              <ImageIcon className="w-4 h-4 text-pink-400" />
              <span>Media Upload (Image or Reel Video)</span>
            </span>
            <span className="text-[10px] text-slate-400">JPEG, PNG, WEBP, MP4, MOV</span>
          </label>

          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileChange(e.target.files[0]);
              }
            }}
            accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime"
            className="hidden"
          />

          {!mediaPreviewUrl ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  handleFileChange(e.dataTransfer.files[0]);
                }
              }}
              className="border-2 border-dashed border-slate-700 hover:border-pink-500/50 bg-slate-950/50 hover:bg-slate-900 rounded-xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center space-y-2 group"
            >
              <div className="w-12 h-12 rounded-full bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 group-hover:scale-110 transition-transform">
                <Upload className="w-5 h-5" />
              </div>
              <div className="text-xs font-medium text-slate-200">
                Click to upload or drag & drop media file
              </div>
              <p className="text-[11px] text-slate-500 max-w-xs">
                Images (1:1, 4:5, 1.91:1) or Short Video Reels (up to 90s)
              </p>
            </div>
          ) : (
            <div className="relative rounded-xl border border-slate-700 overflow-hidden bg-slate-950 p-2">
              <div className="flex items-center justify-between pb-2 px-1">
                <span className="text-xs font-medium text-slate-300 flex items-center space-x-1">
                  {mediaType === 'video' ? <VideoIcon className="w-3.5 h-3.5 text-purple-400" /> : <ImageIcon className="w-3.5 h-3.5 text-pink-400" />}
                  <span className="truncate max-w-[200px]">{selectedFile?.name}</span>
                  {selectedFile && <span className="text-[10px] text-slate-500">({(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)</span>}
                </span>

                <button
                  type="button"
                  onClick={handleRemoveMedia}
                  className="flex items-center space-x-1 text-xs text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 px-2 py-0.5 rounded border border-red-500/20 transition-colors"
                >
                  <X className="w-3 h-3" />
                  <span>Replace</span>
                </button>
              </div>

              {/* Media Preview Box */}
              <div className="relative max-h-48 rounded-lg overflow-hidden bg-black flex items-center justify-center">
                {mediaType === 'video' ? (
                  <video src={mediaPreviewUrl} controls className="max-h-48 w-full object-contain" />
                ) : (
                  <img src={mediaPreviewUrl} alt="Upload preview" className="max-h-48 w-full object-contain" />
                )}
                {isUploading && (
                  <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center space-x-2 text-xs text-pink-400">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Validating media specs...</span>
                  </div>
                )}
              </div>

              {/* Validation Badges & Warnings */}
              {validationResult && (
                <div className="mt-2 space-y-1 text-xs">
                  {validationResult.aspect_ratio && (
                    <div className="flex items-center space-x-1 text-[11px] text-slate-400">
                      <span className="font-semibold text-slate-300">Detected Ratio:</span>
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-pink-300 font-mono">
                        {validationResult.aspect_ratio}
                      </span>
                    </div>
                  )}

                  {validationResult.warnings.map((w, idx) => (
                    <div key={idx} className="flex items-start space-x-1 text-amber-400 text-[11px] bg-amber-500/10 p-2 rounded border border-amber-500/20">
                      <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                      <span>{w}</span>
                    </div>
                  ))}

                  {validationResult.is_valid && validationResult.warnings.length === 0 && (
                    <div className="flex items-center space-x-1 text-emerald-400 text-[11px] bg-emerald-500/10 p-1.5 rounded border border-emerald-500/20">
                      <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                      <span>Media fully complies with Instagram standard requirements.</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {uploadError && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* 2. Content Prompt TextArea */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-200 flex items-center justify-between">
            <span className="flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-pink-400" />
              <span>Content Prompt / Post Idea</span>
            </span>
            <span className="text-[10px] text-slate-400">User idea only — AI crafts final post</span>
          </label>

          <textarea
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="What would you like this post to communicate?"
            className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-pink-500 transition-colors"
          />

          {/* Sample Idea Chips */}
          <div className="space-y-1">
            <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
              <Lightbulb className="w-3 h-3 text-amber-400" />
              <span>Example Prompts (click to copy):</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {SAMPLE_IDEAS.map((idea, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPrompt(idea)}
                  className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-2 py-1 rounded-lg border border-slate-700 transition-colors"
                >
                  {idea}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 3. Provider Selector */}
        <ProviderSelector selectedProvider={provider} onSelectProvider={onSelectProvider} />

        {/* 4. Generate Button */}
        <button
          type="submit"
          disabled={isGenerating || !prompt.trim() || isUploading}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-pink-500 via-purple-500 to-amber-500 hover:from-pink-400 hover:via-purple-400 hover:to-amber-400 text-white font-bold text-sm shadow-lg shadow-pink-500/25 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
          <span>{isGenerating ? 'Generating Instagram Post...' : 'Generate Instagram Post'}</span>
        </button>
      </form>
    </div>
  );
};
