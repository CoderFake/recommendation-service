import { apiClient } from './client';
import { SongSearchResult, Song, SpotifyTrack } from '@/lib/types';

export async function searchSongs(params: {
  q?: string;
  genre?: string;
  artist?: string;
  page?: number;
  size?: number;
}): Promise<SongSearchResult> {
  const searchParams = new URLSearchParams();
  
  if (params.q) searchParams.append('q', params.q);
  if (params.genre) searchParams.append('genre', params.genre);
  if (params.artist) searchParams.append('artist', params.artist);
  if (params.page) searchParams.append('page', params.page.toString());
  if (params.size) searchParams.append('size', params.size.toString());
  
  return apiClient(`/songs?${searchParams.toString()}`);
}

export async function getSong(songId: number): Promise<Song> {
  return apiClient(`/songs/${songId}`);
}

export async function searchSpotify(query: string, limit = 10): Promise<SpotifyTrack[]> {
  return apiClient(`/songs/spotify/search?q=${encodeURIComponent(query)}&limit=${limit}`, {
    method: 'POST',
  });
}

export async function importSpotifyTrack(trackId: string): Promise<Song> {
  return apiClient(`/songs/spotify/import?track_id=${trackId}`, {
    method: 'POST',
  });
}

export async function getSpotifyRecommendations(songId: number, limit = 10): Promise<SpotifyTrack[]> {
  return apiClient(`/songs/spotify/recommendations/${songId}?limit=${limit}`);
}