"use client"

import Image from 'next/image'
import { Play, Heart, MoreHorizontal, Plus } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Song } from '@/lib/types'
import { formatDuration } from '@/lib/utils'
import { usePlayer } from '@/contexts/player-context'
import { useState } from 'react'
import { trackInteractionEvent } from '@/lib/api/interactions'
import { useToast } from '@/hooks/use-toast'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'

interface SongCardProps {
  song: Song
  onAddToPlaylist?: (song: Song) => void
}

export function SongCard({ song, onAddToPlaylist }: SongCardProps) {
  const { playSong, currentSong, isPlaying, pauseSong, resumeSong } = usePlayer()
  const { toast } = useToast()
  const [isLiked, setIsLiked] = useState(false)
  
  const isCurrentSong = currentSong?.id === song.id
  
  const handlePlayClick = () => {
    if (isCurrentSong) {
      if (isPlaying) {
        pauseSong()
      } else {
        resumeSong()
      }
    } else {
      playSong(song)
      trackInteractionEvent({
        event_type: 'play',
        song_id: song.id,
      })
    }
  }
  
  const handleLikeClick = () => {
    setIsLiked(!isLiked)
    trackInteractionEvent({
      event_type: isLiked ? 'unlike' : 'like',
      song_id: song.id,
    })
    
    toast({
      title: isLiked ? 'Đã xóa khỏi yêu thích' : 'Đã thêm vào yêu thích',
      description: `"${song.title}" - ${song.artist}`,
    })
  }
  
  const handleAddToPlaylist = () => {
    if (onAddToPlaylist) {
      onAddToPlaylist(song)
    }
  }
  
  return (
    <Card className="overflow-hidden transition-all hover:bg-accent">
      <CardContent className="p-0">
        <div className="grid grid-cols-[auto_1fr_auto] items-center gap-4 p-4">
          <div className="relative h-16 w-16 overflow-hidden rounded-md">
            <Image
              src={song.artwork_url || '/images/album-placeholder.png'}
              alt={song.title}
              fill
              className="object-cover"
            />
            <div 
              className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 transition-opacity hover:opacity-100"
              onClick={handlePlayClick}
            >
              <Play className="h-8 w-8 text-white" />
            </div>
          </div>
          <div className="space-y-1 overflow-hidden">
            <p className="truncate font-medium">{song.title}</p>
            <p className="truncate text-sm text-muted-foreground">
              {song.artist}
            </p>
            {song.duration && (
              <p className="text-xs text-muted-foreground">
                {formatDuration(song.duration)}
              </p>
            )}
          </div>
          <div className="flex space-x-2">
            <Button
              variant="ghost"
              size="icon"
              className={isLiked ? "text-primary" : "text-muted-foreground"}
              onClick={handleLikeClick}
            >
              <Heart className="h-5 w-5" />
              <span className="sr-only">Thích</span>
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-5 w-5" />
                  <span className="sr-only">Thêm tùy chọn</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handlePlayClick}>
                  <Play className="mr-2 h-4 w-4" />
                  <span>{isPlaying && isCurrentSong ? 'Tạm dừng' : 'Phát'}</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLikeClick}>
                  <Heart className="mr-2 h-4 w-4" />
                  <span>{isLiked ? 'Bỏ thích' : 'Thích'}</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleAddToPlaylist}>
                  <Plus className="mr-2 h-4 w-4" />
                  <span>Thêm vào playlist</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// src/components/music/song-list.tsx
"use client"

import { Song } from '@/lib/types'
import { SongCard } from './song-card'
import { useEffect, useState } from 'react'

interface SongListProps {
  songs: Song[]
  emptyMessage?: string
  onAddToPlaylist?: (song: Song) => void
}

export function SongList({ songs, emptyMessage = "Không có bài hát nào", onAddToPlaylist }: SongListProps) {
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  if (!mounted) return null
  
  if (!songs || songs.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center">
        <p className="text-center text-muted-foreground">{emptyMessage}</p>
      </div>
    )
  }
  
  return (
    <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-1 lg:grid-cols-1">
      {songs.map((song) => (
        <SongCard
          key={song.id}
          song={song}
          onAddToPlaylist={onAddToPlaylist}
        />
      ))}
    </div>
  )
}
