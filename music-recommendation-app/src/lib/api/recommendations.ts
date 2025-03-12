import { apiClient } from './client';
import { RecommendationResponse, RecommendationRequest, SongRecommendation, UserTaste } from '@/lib/types';

export async function getRecommendations(params: Partial<RecommendationRequest> = {}): Promise<RecommendationResponse> {
  const searchParams = new URLSearchParams();
  
  if (params.limit) searchParams.append('limit', params.limit.toString());
  if (params.seed_songs) {
    params.seed_songs.forEach(songId => searchParams.append('seed_songs', songId.toString()));
  }
  if (params.seed_genres) {
    params.seed_genres.forEach(genre => searchParams.append('seed_genres', genre));
  }
  if (params.collaborative_weight !== undefined) {
    searchParams.append('collaborative_weight', params.collaborative_weight.toString());
  }
  if (params.content_based_weight !== undefined) {
    searchParams.append('content_based_weight', params.content_based_weight.toString());
  }
  if (params.diversity !== undefined) {
    searchParams.append('diversity', params.diversity.toString());
  }
  if (params.include_liked !== undefined) {
    searchParams.append('include_liked', params.include_liked.toString());
  }
  if (params.include_listened !== undefined) {
    searchParams.append('include_listened', params.include_listened.toString());
  }
  
  return apiClient(`/recommendations?${searchParams.toString()}`);
}

export async function getSimilarSongs(songId: number, limit = 10): Promise<SongRecommendation[]> {
  return apiClient(`/recommendations/similar/${songId}?limit=${limit}`);
}

export async function getUserTasteProfile(): Promise<UserTaste> {
  return apiClient('/recommendations/taste-profile');
}

export async function refreshRecommendationModel(): Promise<{status: string}> {
  return apiClient('/recommendations/refresh-model', {
    method: 'POST',
  });
}