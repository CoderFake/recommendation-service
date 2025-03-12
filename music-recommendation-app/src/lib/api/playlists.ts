import { apiClient } from './client';
import { 
    Playlist, 
    PlaylistCreate, 
    PlaylistUpdate, 
    PlaylistSong, 
    PlaylistWithSongs 
} from '@/lib/types';

export async function getUserPlaylists(
    params: { skip?: number; limit?: number } = {}
): Promise<Playlist[]> {
    const searchParams = new URLSearchParams();
    
    if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
    
    return apiClient(`/playlists?${searchParams.toString()}`);
}

export async function getPlaylist(
    playlistId: number,
    params: { skip?: number; limit?: number } = {}
): Promise<PlaylistWithSongs> {
    const searchParams = new URLSearchParams();
    
    if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
    
    return apiClient(`/playlists/${playlistId}?${searchParams.toString()}`);
}

export async function createPlaylist(data: PlaylistCreate): Promise<Playlist> {
    return apiClient('/playlists', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function updatePlaylist(playlistId: number, data: PlaylistUpdate): Promise<Playlist> {
    return apiClient(`/playlists/${playlistId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

export async function deletePlaylist(playlistId: number): Promise<void> {
    return apiClient(`/playlists/${playlistId}`, {
        method: 'DELETE',
    });
}

export async function addSongToPlaylist(playlistId: number, songId: number): Promise<PlaylistSong> {
    return apiClient(`/playlists/${playlistId}/songs?song_id=${songId}`, {
        method: 'POST',
    });
}

export async function removeSongFromPlaylist(playlistId: number, songId: number): Promise<void> {
    return apiClient(`/playlists/${playlistId}/songs/${songId}`, {
        method: 'DELETE',
    });
}

export async function updateSongPosition(
    playlistId: number, 
    songId: number, 
    position: number
): Promise<PlaylistSong> {
    return apiClient(`/playlists/${playlistId}/songs/${songId}/position?position=${position}`, {
        method: 'PUT',
    });
}