import axios from 'axios';
import { Story, PostResponse, ToneOption, ProviderOption, MediaValidationResult, InstagramPostResponse } from '../types';

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
  provider?: ProviderOption,
  source?: string,
  model?: string,
  customTitle?: string,
  customUrl?: string,
  generateImage: boolean = false
): Promise<PostResponse> => {
  const providerParam = provider === 'default' ? undefined : provider;
  const response = await axios.post<PostResponse>(`${API_BASE}/posts/generate`, {
    story_id: storyId,
    source,
    tone,
    provider: providerParam,
    model,
    custom_title: customTitle,
    custom_url: customUrl,
    generate_image: generateImage
  });
  return response.data;
};

export const uploadMedia = async (file: File): Promise<MediaValidationResult & { filename: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<MediaValidationResult>(`${API_BASE}/media/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  return { ...response.data, filename: file.name };
};

export const generateInstagramPost = async (
  prompt: string,
  mediaPath?: string,
  mediaType: 'image' | 'video' = 'image',
  provider?: ProviderOption,
  model?: string
): Promise<InstagramPostResponse> => {
  const providerParam = provider === 'default' ? undefined : provider;
  const response = await axios.post<InstagramPostResponse>(`${API_BASE}/posts/instagram/generate`, {
    prompt,
    media_path: mediaPath,
    media_type: mediaType,
    provider: providerParam,
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

export const publishPostToLinkedIn = async (postId: number): Promise<{ status: string; post_urn: string; message: string }> => {
  const response = await axios.post<{ status: string; post_urn: string; message: string }>(`${API_BASE}/posts/${postId}/publish`);
  return response.data;
};


