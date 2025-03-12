"use client"

import { Song } from '@/lib/types'
import { SongCard } from '@/components/music/song-card'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useRef, useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface FeaturedSongsProps {
  title: string
  description?: string
  songs: Song[]
  onAddToPlaylist?: (song: Song) => void
}

export function FeaturedSongs({ title, description, songs, onAddToPlaylist }: FeaturedSongsProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [showLeftButton, setShowLeftButton] = useState(false)
  const [showRightButton, setShowRightButton] = useState(false)
  
  // Kiểm tra nếu cần hiển thị nút điều hướng
  useEffect(() => {
    const checkScroll = () => {
      if (!containerRef.current) return
      
      setShowLeftButton(containerRef.current.scrollLeft > 0)
      setShowRightButton(
        containerRef.current.scrollLeft <
          containerRef.current.scrollWidth - containerRef.current.clientWidth - 10
      )
    }
    
    const container = containerRef.current
    if (container) {
      checkScroll()
      container.addEventListener('scroll', checkScroll)
      window.addEventListener('resize', checkScroll)
      
      return () => {
        container.removeEventListener('scroll', checkScroll)
        window.removeEventListener('resize', checkScroll)
      }
    }
  }, [songs])
  
  const scroll = (direction: 'left' | 'right') => {
    if (!containerRef.current) return
    
    const { current: container } = containerRef
    const scrollAmount = direction === 'left' ? -300 : 300
    
    container.scrollBy({
      left: scrollAmount,
      behavior: 'smooth',
    })
  }
  
  if (songs.length === 0) return null
  
  return (
    <div className="relative">
      <div className="mb-4">
        <h2 className="text-2xl font-bold">{title}</h2>
        {description && <p className="text-muted-foreground">{description}</p>}
      </div>
      
      <div className="relative group">
        {showLeftButton && (
          <Button
            variant="outline"
            size="icon"
            className="absolute left-0 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background shadow-md"
            onClick={() => scroll('left')}
          >
            <ChevronLeft className="h-4 w-4" />
            <span className="sr-only">Bên trái</span>
          </Button>
        )}
        
        <div
          ref={containerRef}
          className="flex space-x-4 overflow-x-auto pb-4 scrollbar-hide"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {songs.map((song) => (
            <div key={song.id} className="w-[250px] flex-shrink-0">
              <SongCard song={song} onAddToPlaylist={onAddToPlaylist} />
            </div>
          ))}
        </div>
        
        {showRightButton && (
          <Button
            variant="outline"
            size="icon"
            className="absolute right-0 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background shadow-md"
            onClick={() => scroll('right')}
          >
            <ChevronRight className="h-4 w-4" />
            <span className="sr-only">Bên phải</span>
          </Button>
        )}
      </div>
    </div>
  )
}