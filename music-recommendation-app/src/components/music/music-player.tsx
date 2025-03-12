"use client"

import { usePlayer } from '@/contexts/player-context'
import { formatDuration } from '@/lib/utils'
import { useState, useEffect, useRef } from 'react'
import { Slider } from '@/components/ui/slider'
import { Button } from '@/components/ui/button'
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  VolumeX,
  List
} from 'lucide-react'
import Image from 'next/image'

export default function MusicPlayer() {
  const { 
    currentSong,
    isPlaying,
    volume,
    progress,
    duration,
    pauseSong,
    resumeSong,
    nextSong,
    previousSong,
    setVolume,
    seekTo,
    queue
  } = usePlayer()
  
  const [showQueue, setShowQueue] = useState(false)
  const [prevVolume, setPrevVolume] = useState(volume)
  const progressBarRef = useRef<HTMLDivElement>(null)
  
  const isMuted = volume === 0
  
  const toggleMute = () => {
    if (isMuted) {
      setVolume(prevVolume || 0.7)
    } else {
      setPrevVolume(volume)
      setVolume(0)
    }
  }
  
  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current || !duration) return
    
    const rect = progressBarRef.current.getBoundingClientRect()
    const percent = Math.min(Math.max(0, e.clientX - rect.left), rect.width) / rect.width
    seekTo(percent * duration)
  }

  if (!currentSong) return null
  
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background/95 backdrop-blur-md p-2 md:p-4 mb-16 md:mb-0">
      <div className="flex flex-col space-y-2">
        <div className="flex items-center justify-between">
          {/* Thông tin bài hát */}
          <div className="flex items-center space-x-3 w-1/3">
            <div className="relative h-12 w-12 overflow-hidden rounded-md">
              <Image
                src={currentSong.artwork_url || '/images/album-placeholder.png'}
                alt={currentSong.title}
                fill
                className="object-cover"
              />
            </div>
            <div className="overflow-hidden">
              <p className="truncate font-medium">{currentSong.title}</p>
              <p className="truncate text-xs text-muted-foreground">{currentSong.artist}</p>
            </div>
          </div>
          
          {/* Điều khiển phát nhạc */}
          <div className="flex items-center space-x-4 w-1/3 justify-center">
            <Button
              variant="ghost"
              size="icon"
              onClick={previousSong}
              disabled={queue.length === 0}
            >
              <SkipBack className="h-5 w-5" />
              <span className="sr-only">Bài trước</span>
            </Button>
            <Button
              variant="secondary"
              size="icon"
              className="h-10 w-10 rounded-full"
              onClick={isPlaying ? pauseSong : resumeSong}
            >
              {isPlaying ? (
                <Pause className="h-5 w-5" />
              ) : (
                <Play className="h-5 w-5" />
              )}
              <span className="sr-only">{isPlaying ? 'Tạm dừng' : 'Phát'}</span>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={nextSong}
              disabled={queue.length === 0}
            >
              <SkipForward className="h-5 w-5" />
              <span className="sr-only">Bài tiếp</span>
            </Button>
          </div>
          
          {/* Điều khiển âm lượng */}
          <div className="flex items-center space-x-4 w-1/3 justify-end">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleMute}
            >
              {isMuted ? (
                <VolumeX className="h-5 w-5" />
              ) : (
                <Volume2 className="h-5 w-5" />
              )}
              <span className="sr-only">{isMuted ? 'Bật âm' : 'Tắt âm'}</span>
            </Button>
            <Slider
              className="w-24"
              value={[volume * 100]}
              max={100}
              step={1}
              onValueChange={(values) => setVolume(values[0] / 100)}
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowQueue(!showQueue)}
            >
              <List className="h-5 w-5" />
              <span className="sr-only">Danh sách phát</span>
            </Button>
          </div>
        </div>
        
        {/* Thanh tiến trình */}
        <div className="flex items-center space-x-2">
          <span className="text-xs tabular-nums text-muted-foreground">
            {formatDuration(progress * 1000)}
          </span>
          <div
            className="relative h-1.5 flex-1 rounded-full bg-secondary"
            ref={progressBarRef}
            onClick={handleProgressClick}
          >
            <div
              className="absolute h-full rounded-full bg-primary"
              style={{ width: `${(progress / duration) * 100}%` }}
            />
          </div>
          <span className="text-xs tabular-nums text-muted-foreground">
            {formatDuration(duration * 1000)}
          </span>
        </div>
      </div>
      
      {/* Danh sách phát (hiển thị khi showQueue = true) */}
      {showQueue && queue.length > 0 && (
        <div className="mt-4 max-h-48 overflow-auto border rounded-md">
          <div className="p-2 text-sm font-medium">Sắp phát ({queue.length})</div>
          <div className="divide-y">
            {queue.map((song, index) => (
              <div key={`${song.id}-${index}`} className="flex items-center p-2 hover:bg-accent">
                <div className="relative h-8 w-8 overflow-hidden rounded-md">
                  <Image
                    src={song.artwork_url || '/images/album-placeholder.png'}
                    alt={song.title}
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="ml-3 overflow-hidden">
                  <p className="truncate text-sm">{song.title}</p>
                  <p className="truncate text-xs text-muted-foreground">{song.artist}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}