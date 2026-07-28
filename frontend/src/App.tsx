import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { StoryCard } from './components/StoryCard';
import { ToneSelector } from './components/ToneSelector';
import { ProviderSelector } from './components/ProviderSelector';
import { PostPreview } from './components/PostPreview';
import { HistoryDrawer } from './components/HistoryDrawer';
import { ExportModal } from './components/ExportModal';
import { Story, PostResponse, ToneOption, ProviderOption } from './types';
import { fetchTrendingStories, generatePost, fetchPostHistory } from './api/client';
import { RefreshCw, Sparkles, Newspaper, AlertCircle, Type } from 'lucide-react';

export const App: React.FC = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [currentPost, setCurrentPost] = useState<PostResponse | null>(null);
  const [tone, setTone] = useState<ToneOption>('professional');
  const [provider, setProvider] = useState<ProviderOption>('default');

  const [newsSource, setNewsSource] = useState<string>('hacker_news');
  const [customTitle, setCustomTitle] = useState<string>('');
  const [isFetchingStories, setIsFetchingStories] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [history, setHistory] = useState<PostResponse[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  const loadStories = async (sourceToUse?: string) => {
    const targetSource = sourceToUse || newsSource;
    if (targetSource === 'self') {
      setIsFetchingStories(false);
      setStories([]);
      setSelectedStory(null);
      return;
    }

    setIsFetchingStories(true);
    setErrorMsg(null);
    try {
      const data = await fetchTrendingStories(targetSource, 15);
      setStories(data);
      if (data.length > 0) {
        setSelectedStory(data[0]);
      }
    } catch (err: any) {
      setErrorMsg(`Failed to load stories from source. Ensure backend server is running.`);
    } finally {
      setIsFetchingStories(false);
    }
  };

  const loadHistory = async () => {
    try {
      const data = await fetchPostHistory(20);
      setHistory(data);
      if (data.length > 0 && !currentPost) {
        setCurrentPost(data[0]);
      }
    } catch (err) {
      console.error('History fetch error:', err);
    }
  };

  useEffect(() => {
    loadStories();
    loadHistory();
  }, []);

  const handleGenerate = async (targetStory?: Story) => {
    setIsGenerating(true);
    setErrorMsg(null);

    try {
      if (customTitle.trim() || newsSource === 'self') {
        const titleToUse = customTitle.trim() || selectedStory?.title || 'Self-authored Post';
        const result = await generatePost(
          undefined,
          tone,
          provider,
          'self',
          undefined,
          titleToUse,
          'self'
        );
        setCurrentPost(result);
      } else {
        const storyToUse = targetStory || selectedStory || stories[0];
        if (!storyToUse) return;
        const storySource = storyToUse.source_name.toLowerCase().includes('cnet') ? 'cnet' : newsSource;
        const result = await generatePost(
          storyToUse.id,
          tone,
          provider,
          storySource
        );
        setCurrentPost(result);
      }
      loadHistory();
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Failed to generate LinkedIn post.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header
        onOpenHistory={() => setIsHistoryOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: News Feed & Controls (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-6">
          {/* Top Control Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Newspaper className="w-5 h-5 text-sky-400" />
                <h2 className="text-sm font-bold text-slate-200">Content Source & Settings</h2>
              </div>
              <div className="flex items-center space-x-2">
                <select
                  value={newsSource}
                  onChange={(e) => {
                    const newSource = e.target.value;
                    setNewsSource(newSource);
                    loadStories(newSource);
                  }}
                  className="bg-slate-800 text-slate-200 text-xs font-semibold rounded-lg px-2.5 py-1 border border-slate-700 focus:outline-none focus:border-sky-500 cursor-pointer"
                >
                  <option value="hacker_news">Hacker News</option>
                  <option value="cnet">CNET Tech News</option>
                  <option value="self">Custom Title (Self)</option>
                </select>
                {newsSource !== 'self' && (
                  <button
                    onClick={() => loadStories(newsSource)}
                    disabled={isFetchingStories}
                    className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded-lg border border-slate-700 transition-colors"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isFetchingStories ? 'animate-spin' : ''}`} />
                    <span>Fetch</span>
                  </button>
                )}
              </div>
            </div>

            {/* Custom Title Input Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                <span className="flex items-center space-x-1.5">
                  <Type className="w-3.5 h-3.5 text-sky-400" />
                  <span>Custom Title / Topic Input</span>
                </span>
                {customTitle.trim() && (
                  <span className="text-[10px] bg-sky-500/10 text-sky-400 border border-sky-500/20 px-1.5 py-0.5 rounded font-mono">
                    Source: self
                  </span>
                )}
              </label>
              <input
                type="text"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder="Type custom post title/topic (e.g. Why we switched from React to Svelte)..."
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
              />
            </div>

            <ProviderSelector selectedProvider={provider} onSelectProvider={setProvider} />

            <ToneSelector selectedTone={tone} onSelectTone={setTone} />

            <button
              onClick={() => handleGenerate()}
              disabled={
                isGenerating ||
                (newsSource === 'self' && !customTitle.trim()) ||
                (newsSource !== 'self' && !customTitle.trim() && stories.length === 0)
              }
              className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-sky-500/25 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              <Sparkles className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
              <span>
                {isGenerating
                  ? 'Analyzing & Generating...'
                  : customTitle.trim() || newsSource === 'self'
                  ? 'Generate Post from Title (Self)'
                  : 'Generate Post for Top Story'}
              </span>
            </button>
          </div>

          {errorMsg && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Trending Stories List */}
          <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-1">
              {newsSource === 'self' ? 'Custom Title Mode' : `Front-Page Ranked Stories (${stories.length})`}
            </div>

            <div className="space-y-3 overflow-y-auto max-h-[600px] pr-1">
              {newsSource === 'self' ? (
                <div className="text-center py-12 px-4 text-slate-400 text-xs space-y-3 border border-dashed border-slate-800 rounded-xl">
                  <div className="w-10 h-10 rounded-full bg-sky-500/10 border border-sky-500/20 flex items-center justify-center mx-auto text-sky-400">
                    <Type className="w-5 h-5" />
                  </div>
                  <p className="font-semibold text-slate-200">Custom Title Mode (Source: Self)</p>
                  <p className="text-slate-500 max-w-xs mx-auto">
                    Type your post title or topic in the title input box above and click &quot;Generate Post from Title (Self)&quot;.
                  </p>
                </div>
              ) : isFetchingStories && stories.length === 0 ? (
                <div className="text-center py-12 text-slate-500 text-sm">
                  Loading trending stories...
                </div>
              ) : (
                stories.map((story) => (
                  <StoryCard
                    key={story.id}
                    story={story}
                    isSelected={selectedStory?.id === story.id}
                    onSelect={(s) => setSelectedStory(s)}
                    onGenerate={(s) => {
                      setSelectedStory(s);
                      handleGenerate(s);
                    }}
                    isGenerating={isGenerating}
                  />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: LinkedIn Post Preview & Actions (7 Cols) */}
        <div className="lg:col-span-7">
          <PostPreview
            post={currentPost}
            onRegenerate={() => handleGenerate()}
            isGenerating={isGenerating}
            onOpenExport={() => setIsExportOpen(true)}
          />
        </div>
      </main>

      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelectPost={(post) => setCurrentPost(post)}
      />

      <ExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        post={currentPost}
      />
    </div>
  );
};
