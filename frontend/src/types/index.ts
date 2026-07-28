export interface Story {
  id: string;
  title: string;
  url: string;
  hn_url: string;
  author: string;
  score: number;
  comments_count: number;
  published_at?: string;
  rank_score: number;
  source_name: string;
}

export interface ArticleSummary {
  what_happened: string;
  why_it_matters: string;
  impact: string;
  key_takeaway: string;
}

export interface PostResponse {
  id: number;
  story_id: string;
  source_name: string;
  title: string;
  source_url: string;
  hn_url: string;
  author: string;
  score: number;
  comments_count: number;
  summary: ArticleSummary;
  linkedin_caption: string;
  hashtags: string[];
  word_count: number;
  tone: string;
  image_path: string;
  image_type: string;
  output_folder: string;
  model_used: string;
  created_at: string;
}

export type ToneOption = 'professional' | 'founder' | 'developer' | 'investor';
export type ProviderOption = 'default' | 'gemini' | 'openai' | 'ollama' | 'lmstudio';

