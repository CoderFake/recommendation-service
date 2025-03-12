"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { 
  Edit, 
  Trash2, 
  Play,
  Share,
  MoreHorizontal,
  ListPlus,
  ListMinus,
  ExternalLink
} from 'lucide-react'
import { usePlayer } from '@/contexts/player-context'
import { usePlaylists } from '@/hooks/use-playlists'
import { PlaylistWithSongs, Song } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { SongTable } from '@/components/music/song-table'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { formatDate } from '@/lib/utils'
import { useAuth } from '@/contexts/auth-context'

interface PlaylistDetailProps {
  playlistData: PlaylistWithSongs
}

export function PlaylistDetail({ playlistData }: PlaylistDetailProps) {
  const [playlist, setPlaylist] = useState<PlaylistWithSongs>(playlistData)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const { playSong, addToQueue } = usePlayer()
  const { user } = useAuth()
  const { 
    isLoading, 
    deletePlaylist, 
    removeSongFromPlaylist 
  } = usePlaylists()
  const router = useRouter()
  
  useEffect(() => {
    setPlaylist(playlistData)
  }, [playlistData])
  
  const isOwner = user?.id === playlist.playlist.user_id
  
  const handlePlayAll = () => {
    if (playlist.songs.length === 0) return
    
    const firstSong = playlist.songs[0]
    const remainingSongs = playlist.songs.slice(1)
    
    playSong(firstSong, remainingSongs)
  }
  
  const handleDeletePlaylist = async () => {
    if (await deletePlaylist(playlist.playlist.id)) {
      router.push('/playlists')
    }
  }
  
  const handleRemoveSong = async (songId: number) => {
    if (await removeSongFromPlaylist(playlist.playlist.id, songId)) {
      // Update local state to remove the song
      setPlaylist(prev => ({
        ...prev,
        songs: prev.songs.filter(song => song.id !== songId),
        total_songs: prev.total_songs - 1
      }))
    }
  }
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">{playlist.playlist.title}</h1>
          {playlist.playlist.description && (
            <p className="mt-2 text-muted-foreground">{playlist.playlist.description}</p>
          )}
          <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
            <span>{playlist.total_songs} bài hát</span>
            <span>•</span>
            <span>
              {playlist.playlist.is_public ? "Công khai" : "Riêng tư"}
            </span>
            <span>•</span>
            <span>Cập nhật: {formatDate(playlist.playlist.updated_at)}</span>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Button 
            onClick={handlePlayAll}
            disabled={playlist.songs.length === 0}
          >
            <Play className="mr-2 h-4 w-4" />
            Phát tất cả
          </Button>
          
          {isOwner && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link href={`/playlists/${playlist.playlist.id}/edit`}>
                    <Edit className="mr-2 h-4 w-4" />
                    Chỉnh sửa
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => setIsDeleteDialogOpen(true)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Xóa playlist
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
      
      {playlist.songs.length > 0 ? (
        <SongTable 
          songs={playlist.songs} 
          isPlaylist={true}
          onRemoveSong={isOwner ? handleRemoveSong : undefined}
        />
      ) : (
        <div className="rounded-md border p-8 text-center">
          <p className="mb-4 text-muted-foreground">Playlist này chưa có bài hát nào</p>
          <Link href="/search">
            <Button>
              <ListPlus className="mr-2 h-4 w-4" />
              Thêm bài hát
            </Button>
          </Link>
        </div>
      )}
      
      <AlertDialog 
        open={isDeleteDialogOpen} 
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Bạn có chắc chắn muốn xóa?</AlertDialogTitle>
            <AlertDialogDescription>
              Playlist "{playlist.playlist.title}" sẽ bị xóa vĩnh viễn.
              Hành động này không thể hoàn tác.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeletePlaylist}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={isLoading}
            >
              {isLoading ? 'Đang xóa...' : 'Xóa playlist'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}