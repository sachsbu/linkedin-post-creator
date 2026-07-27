import axios from 'axios';
import { Story, PostResponse, ToneOption } from '../types';

const API_BASE = '/api';

export const fetchTrendingStories = async (source: string = 'hacker_news', limit: number = 15): Promise<Story[]> => {
  const response = await axios.get<Story[]>(`${API_BASE}/stories/trending`, {
    params: { source, limit }
  });
  return response.data;
};

export const generatePost = async (
  storyId?: string,
  tone: ToneOption = 'professional',
  provider?: string,
  model?: string
): Promise<PostResponse> => {
  const response = await axios.post<PostResponse>(`${API_BASE}/posts/generate`, {
    story_id: storyId,
    tone,
    provider,
    model
  });
  return response.data;
};

export const fetchPostHistory = async (limit: number = 20): Promise<PostResponse[]> => {
  const response = await axios.get<PostResponse[]>(`${API_BASE}/posts/history`, {
    params: { limit }
  });
  return response.data;
};
