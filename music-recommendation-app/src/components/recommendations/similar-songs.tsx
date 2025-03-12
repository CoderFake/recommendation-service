"use client"

import { SongRecommendation } from '@/lib/types'
import { useState, useEffect } from 'react'
import { SongCard } from '@/components/music/song-card'
import { Button } from '@/components/ui/button'
import { getSimilarSongs } from '@/lib/api/recommendations'
import { useToast } from '@/hooks/use-toast'

interface SimilarSongsProps {
  songId: number
  initialSongs?: SongRecommendation[]
  onAddToPlaylist?: (song: SongRecommendation['song']) => void
}

export function SimilarSongs({ songId, initialSongs = [], onAddToPlaylist }: SimilarSongsProps) {
  const [similarSongs, setSimilarSongs] = useState<SongRecommendation[]>(initialSongs)
  const [isLoading, setIsLoading] = useState(!initialSongs.length)
  const { toast } = useToast()
  
  useEffect(() => {
    if (!initialSongs.length) {
      loadSimilarSongs()
    }
  }, [songId, initialSongs.length])
  
  const loadSimilarSongs = async () => {
    try {
      setIsLoading(true)
      const songs = await getSimilarSongs(songId)
      setSimilarSongs(songs)
    } catch (error) {
      toast({
        title: 'Không thể tải bài hát tương tự',
        description: 'Đã xảy ra lỗi khi tải danh sách bài hát tương tự',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
      </div>
    )
  }
  
  if (similarSongs.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-muted-foreground">Không tìm thấy bài hát tương tự</p>
      </div>
    )
  }
  
  return (
    <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {similarSongs.map((recommendation) => (
        <SongCard
          key={recommendation.song.id}
          song={recommendation.song}
          onAddToPlaylist={onAddToPlaylist}
        />
      ))}
    </div>
  )
}

