import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { StoryCard } from './components/StoryCard';
import { ToneSelector } from './components/ToneSelector';
import { PostPreview } from './components/PostPreview';
import { HistoryDrawer } from './components/HistoryDrawer';
import { ExportModal } from './components/ExportModal';
import { Story, PostResponse, ToneOption } from './types';
import { fetchTrendingStories, generatePost, fetchPostHistory } from './api/client';
import { RefreshCw, Sparkles, Newspaper, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [currentPost, setCurrentPost] = useState<PostResponse | null>(null);
  const [tone, setTone] = useState<ToneOption>('professional');

  const [isFetchingStories, setIsFetchingStories] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [history, setHistory] = useState<PostResponse[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  const loadStories = async () => {
    setIsFetchingStories(true);
    setErrorMsg(null);
    try {
      const data = await fetchTrendingStories('hacker_news', 15);
      setStories(data);
      if (data.length > 0 && !selectedStory) {
        setSelectedStory(data[0]);
      }
    } catch (err: any) {
      setErrorMsg('Failed to load Hacker News stories. Ensure backend server is running.');
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
    const storyToUse = targetStory || selectedStory || stories[0];
    if (!storyToUse) return;

    setIsGenerating(true);
    setErrorMsg(null);

    try {
      const result = await generatePost(storyToUse.id, tone);
      setCurrentPost(result);
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
        onOpenSettings={() => alert('Backend configured with default provider Gemini / env options.')}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Hacker News Feed & Controls (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-6">
          {/* Top Control Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Newspaper className="w-5 h-5 text-sky-400" />
                <h2 className="text-sm font-bold text-slate-200">Trending Hacker News</h2>
              </div>
              <button
                onClick={loadStories}
                disabled={isFetchingStories}
                className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded-lg border border-slate-700 transition-colors"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isFetchingStories ? 'animate-spin' : ''}`} />
                <span>Fetch News</span>
              </button>
            </div>

            <ToneSelector selectedTone={tone} onSelectTone={setTone} />

            <button
              onClick={() => handleGenerate()}
              disabled={isGenerating || stories.length === 0}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-sky-500/25 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              <Sparkles className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
              <span>{isGenerating ? 'Analyzing & Generating...' : 'Generate Post for Top Story'}</span>
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
              Front-Page Ranked Stories ({stories.length})
            </div>

            <div className="space-y-3 overflow-y-auto max-h-[600px] pr-1">
              {isFetchingStories && stories.length === 0 ? (
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
