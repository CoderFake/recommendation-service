// src/components/music/song-table.tsx
"use client"

import { Song } from '@/lib/types'
import { formatDuration } from '@/lib/utils'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Play, Heart, MoreHorizontal, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
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
import Image from 'next/image'

interface SongTableProps {
  songs: Song[]
  emptyMessage?: string
  onAddToPlaylist?: (song: Song) => void
}

export function SongTable({ songs, emptyMessage = "Không có bài hát nào", onAddToPlaylist }: SongTableProps) {
  const { playSong, currentSong, isPlaying, pauseSong, resumeSong } = usePlayer()
  const { toast } = useToast()
  const [likedSongs, setLikedSongs] = useState<Record<number, boolean>>({})
  
  if (!songs || songs.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center">
        <p className="text-center text-muted-foreground">{emptyMessage}</p>
      </div>
    )
  }
  
  const handlePlayClick = (song: Song) => {
    if (currentSong?.id === song.id) {
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
  
  const handleLikeClick = (song: Song) => {
    const newLikedState = !likedSongs[song.id]
    setLikedSongs({ ...likedSongs, [song.id]: newLikedState })
    
    trackInteractionEvent({
      event_type: newLikedState ? 'like' : 'unlike',
      song_id: song.id,
    })
    
    toast({
      title: newLikedState ? 'Đã thêm vào yêu thích' : 'Đã xóa khỏi yêu thích',
      description: `"${song.title}" - ${song.artist}`,
    })
  }
  
  const handleAddToPlaylist = (song: Song) => {
    if (onAddToPlaylist) {
      onAddToPlaylist(song)
    }
  }
  
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">#</TableHead>
            <TableHead>Bài hát</TableHead>
            <TableHead>Nghệ sĩ</TableHead>
            <TableHead className="hidden md:table-cell">Thể loại</TableHead>
            <TableHead className="hidden md:table-cell">Thời lượng</TableHead>
            <TableHead className="w-[100px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {songs.map((song, index) => (
            <TableRow
              key={song.id}
              className={currentSong?.id === song.id ? "bg-accent" : ""}
            >
              <TableCell className="font-medium">{index + 1}</TableCell>
              <TableCell>
                <div className="flex items-center space-x-3">
                  <div className="relative h-10 w-10 overflow-hidden rounded-md">
                    <Image
                      src={song.artwork_url || '/images/album-placeholder.png'}
                      alt={song.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                  <div className="font-medium">{song.title}</div>
                </div>
              </TableCell>
              <TableCell>{song.artist}</TableCell>
              <TableCell className="hidden md:table-cell">{song.genre || "Không xác định"}</TableCell>
              <TableCell className="hidden md:table-cell">{song.duration ? formatDuration(song.duration) : "--:--"}</TableCell>
              <TableCell>
                <div className="flex space-x-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handlePlayClick(song)}
                  >
                    <Play className="h-4 w-4" />
                    <span className="sr-only">Phát</span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className={likedSongs[song.id] ? "text-primary" : ""}
                    onClick={() => handleLikeClick(song)}
                  >
                    <Heart className="h-4 w-4" />
                    <span className="sr-only">Thích</span>
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">Thêm tùy chọn</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handlePlayClick(song)}>
                        <Play className="mr-2 h-4 w-4" />
                        <span>{isPlaying && currentSong?.id === song.id ? 'Tạm dừng' : 'Phát'}</span>
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleLikeClick(song)}>
                        <Heart className="mr-2 h-4 w-4" />
                        <span>{likedSongs[song.id] ? 'Bỏ thích' : 'Thích'}</span>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={() => handleAddToPlaylist(song)}>
                        <Plus className="mr-2 h-4 w-4" />
                        <span>Thêm vào playlist</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
