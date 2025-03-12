import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { Song } from '@/lib/types';
import { trackInteractionEvent } from '@/lib/api/interactions';

interface PlayerContextType {
  currentSong: Song | null;
  queue: Song[];
  isPlaying: boolean;
  volume: number;
  progress: number;
  duration: number;
  playSong: (song: Song, newQueue?: Song[]) => void;
  pauseSong: () => void;
  resumeSong: () => void;
  nextSong: () => void;
  previousSong: () => void;
  setVolume: (volume: number) => void;
  seekTo: (time: number) => void;
  addToQueue: (song: Song) => void;
  clearQueue: () => void;
}

const PlayerContext = createContext<PlayerContextType | undefined>(undefined);

export function PlayerProvider({ children }: { children: React.ReactNode }) {
  const [currentSong, setCurrentSong] = useState<Song | null>(null);
  const [queue, setQueue] = useState<Song[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolumeState] = useState(0.7);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    audioRef.current = new Audio();
    
    const audio = audioRef.current;
    
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleSongEnd);
    
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleSongEnd);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      audio.pause();
      audio.src = '';
    };
  }, []);

  useEffect(() => {
    if (!audioRef.current || !currentSong) return;
    
    const audioUrl = currentSong.features?.preview_url;
    if (!audioUrl) {
      console.error('Không có URL preview cho bài hát:', currentSong.title);
      return;
    }
    
    audioRef.current.src = audioUrl;
    audioRef.current.load();
    
    if (isPlaying) {
      audioRef.current.play().catch(err => {
        console.error('Lỗi khi phát:', err);
        setIsPlaying(false);
      });
      
      trackInteractionEvent({
        event_type: 'play',
        song_id: currentSong.id,
        context: {
          time_of_day: getTimeOfDay(),
          device: 'web',
        }
      });
    }
  }, [currentSong]);

  useEffect(() => {
    if (!audioRef.current) return;
    audioRef.current.volume = volume;
  }, [volume]);

  useEffect(() => {
    if (!audioRef.current || !currentSong) return;
    
    if (isPlaying) {
      audioRef.current.play().catch(err => {
        console.error('Lỗi khi phát:', err);
        setIsPlaying(false);
      });
    } else {
      audioRef.current.pause();
    }
  }, [isPlaying]);

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setProgress(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return;
    setDuration(audioRef.current.duration);
  };

  const handleSongEnd = () => {
    if (queue.length > 0) {
      nextSong();
    } else {
      setIsPlaying(false);
      setProgress(0);
    }
  };

  const getTimeOfDay = (): string => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 21) return 'evening';
    return 'night';
  };

  const playSong = (song: Song, newQueue: Song[] = []) => {
    setCurrentSong(song);
    setQueue(newQueue);
    setIsPlaying(true);
  };

  const pauseSong = () => {
    setIsPlaying(false);
  };

  const resumeSong = () => {
    setIsPlaying(true);
  };

  const nextSong = () => {
    if (queue.length === 0) return;
    
    const nextSong = queue[0];
    const newQueue = queue.slice(1);
    
    if (currentSong) {
      setQueue([...newQueue]);
    }
    
    setCurrentSong(nextSong);
    setIsPlaying(true);
    setProgress(0);
  };

  const previousSong = () => {
    if (progress > 3) {
      seekTo(0);
      return;
    }
  };

  const setVolume = (newVolume: number) => {
    setVolumeState(newVolume);
  };

  const seekTo = (time: number) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = time;
    setProgress(time);
  };

  const addToQueue = (song: Song) => {
    setQueue([...queue, song]);
  };

  const clearQueue = () => {
    setQueue([]);
  };

  return (
    <PlayerContext.Provider
      value={{
        currentSong,
        queue,
        isPlaying,
        volume,
        progress,
        duration,
        playSong,
        pauseSong,
        resumeSong,
        nextSong,
        previousSong,
        setVolume,
        seekTo,
        addToQueue,
        clearQueue,
      }}
    >
      {children}
    </PlayerContext.Provider>
  );
}

export function usePlayer() {
  const context = useContext(PlayerContext);
  if (context === undefined) {
    throw new Error('usePlayer phải được sử dụng trong PlayerProvider');
  }
  return context;
}