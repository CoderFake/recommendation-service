import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/use-toast';
import { 
    Playlist, 
    PlaylistCreate, 
    PlaylistUpdate, 
    PlaylistWithSongs, 
    Song 
} from '@/lib/types';
import {
    getUserPlaylists,
    getPlaylist,
    createPlaylist,
    updatePlaylist,
    deletePlaylist,
    addSongToPlaylist,
    removeSongFromPlaylist,
    updateSongPosition
} from '@/lib/api/playlists';

export function usePlaylists() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { toast } = useToast();
    const router = useRouter();

    const fetchUserPlaylists = useCallback(async (
        params: { skip?: number; limit?: number } = {}
    ): Promise<Playlist[] | null> => {
        try {
            setIsLoading(true);
            setError(null);
            return await getUserPlaylists(params);
        } catch (err: any) {
            setError(err.message || 'Không thể tải danh sách playlist');
            return null;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchPlaylist = useCallback(async (
        playlistId: number,
        params: { skip?: number; limit?: number } = {}
    ): Promise<PlaylistWithSongs | null> => {
        try {
            setIsLoading(true);
            setError(null);
            return await getPlaylist(playlistId, params);
        } catch (err: any) {
            setError(err.message || 'Không thể tải thông tin playlist');
            return null;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const handleCreatePlaylist = useCallback(async (
        data: PlaylistCreate
    ): Promise<Playlist | null> => {
        try {
            setIsLoading(true);
            setError(null);
            const playlist = await createPlaylist(data);
            
            toast({
                title: 'Tạo playlist thành công',
                description: `Playlist "${playlist.title}" đã được tạo`,
            });
            
            return playlist;
        } catch (err: any) {
            const message = err.message || 'Không thể tạo playlist';
            setError(message);
            
            toast({
                title: 'Không thể tạo playlist',
                description: message,
                variant: 'destructive',
            });
            
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [toast]);

    const handleUpdatePlaylist = useCallback(async (
        playlistId: number,
        data: PlaylistUpdate
    ): Promise<Playlist | null> => {
        try {
            setIsLoading(true);
            setError(null);
            const playlist = await updatePlaylist(playlistId, data);
            
            toast({
                title: 'Cập nhật thành công',
                description: `Playlist "${playlist.title}" đã được cập nhật`,
            });
            
            return playlist;
        } catch (err: any) {
            const message = err.message || 'Không thể cập nhật playlist';
            setError(message);
            
            toast({
                title: 'Không thể cập nhật playlist',
                description: message,
                variant: 'destructive',
            });
            
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [toast]);

    const handleDeletePlaylist = useCallback(async (
        playlistId: number,
        navigateAfter: boolean = true
    ): Promise<boolean> => {
        try {
            setIsLoading(true);
            setError(null);
            await deletePlaylist(playlistId);
            
            toast({
                title: 'Xóa thành công',
                description: 'Playlist đã được xóa',
            });
            
            if (navigateAfter) {
                router.push('/playlists');
            }
            
            return true;
        } catch (err: any) {
            const message = err.message || 'Không thể xóa playlist';
            setError(message);
            
            toast({
                title: 'Không thể xóa playlist',
                description: message,
                variant: 'destructive',
            });
            
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [toast, router]);

    const handleAddSongToPlaylist = useCallback(async (
        playlistId: number,
        songId: number
    ): Promise<boolean> => {
        try {
            setIsLoading(true);
            setError(null);
            await addSongToPlaylist(playlistId, songId);
            
            toast({
                title: 'Đã thêm bài hát',
                description: 'Bài hát đã được thêm vào playlist',
            });
            
            return true;
        } catch (err: any) {
            const message = err.message || 'Không thể thêm bài hát vào playlist';
            setError(message);
            
            toast({
                title: 'Không thể thêm bài hát',
                description: message,
                variant: 'destructive',
            });
            
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [toast]);

    const handleRemoveSongFromPlaylist = useCallback(async (
        playlistId: number,
        songId: number
    ): Promise<boolean> => {
        try {
            setIsLoading(true);
            setError(null);
            await removeSongFromPlaylist(playlistId, songId);
            
            toast({
                title: 'Đã xóa bài hát',
                description: 'Bài hát đã được xóa khỏi playlist',
            });
            
            return true;
        } catch (err: any) {
            const message = err.message || 'Không thể xóa bài hát khỏi playlist';
            setError(message);
            
            toast({
                title: 'Không thể xóa bài hát',
                description: message,
                variant: 'destructive',
            });
            
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [toast]);

    const handleReorderSong = useCallback(async (
        playlistId: number,
        songId: number,
        newPosition: number
    ): Promise<boolean> => {
        try {
            setIsLoading(true);
            setError(null);
            await updateSongPosition(playlistId, songId, newPosition);
            return true;
        } catch (err: any) {
            const message = err.message || 'Không thể thay đổi vị trí bài hát';
            setError(message);
            
            toast({
                title: 'Không thể thay đổi vị trí',
                description: message,
                variant: 'destructive',
            });
            
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [toast]);

    return {
        isLoading,
        error,
        fetchUserPlaylists,
        fetchPlaylist,
        createPlaylist: handleCreatePlaylist,
        updatePlaylist: handleUpdatePlaylist,
        deletePlaylist: handleDeletePlaylist,
        addSongToPlaylist: handleAddSongToPlaylist,
        removeSongFromPlaylist: handleRemoveSongFromPlaylist,
        reorderSong: handleReorderSong,
    };
}