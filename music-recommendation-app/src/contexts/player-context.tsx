'use client';

import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { Song } from '@/lib/types';
import { trackInteractionEvent } from '@/lib/api/interactions';

interface PlayerContextType {
  currentSong: Song | null;
  queue: Song[];
  history: Song[];
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
  playlistMode: boolean;
  togglePlaylistMode: () => void;
  repeatMode: 'off' | 'all' | 'one';
  setRepeatMode: (mode: 'off' | 'all' | 'one') => void;
}

// Constants
const PLAYER_STATE_KEY = 'music_player_state';
const MAX_HISTORY_LENGTH = 20;

// Default values
const defaultVolume = 0.7;

const PlayerContext = createContext<PlayerContextType | undefined>(undefined);

export function PlayerProvider({ children }: { children: React.ReactNode }) {
  // State
  const [currentSong, setCurrentSong] = useState<Song | null>(null);
  const [queue, setQueue] = useState<Song[]>([]);
  const [history, setHistory] = useState<Song[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolumeState] = useState(defaultVolume);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playlistMode, setPlaylistMode] = useState(false);
  const [repeatMode, setRepeatMode] = useState<'off' | 'all' | 'one'>('off');
  const [isClient, setIsClient] = useState(false);
  
  // Refs
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize client-side state
  useEffect(() => {
    setIsClient(true);

    // Create audio element
    audioRef.current = new Audio();
    
    // Add event listeners
    const audio = audioRef.current;
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleSongEnd);
    
    // Load saved state from localStorage
    try {
      const savedState = localStorage.getItem(PLAYER_STATE_KEY);
      if (savedState) {
        const state = JSON.parse(savedState);
        
        if (state.volume !== undefined) {
          setVolumeState(state.volume);
          if (audio) audio.volume = state.volume;
        }
        
        if (state.repeatMode) {
          setRepeatMode(state.repeatMode);
        }
        
        if (state.playlistMode !== undefined) {
          setPlaylistMode(state.playlistMode);
        }
      }
    } catch (error) {
      console.error('Error loading player state:', error);
    }
    
    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleSongEnd);
      
      audio.pause();
      audio.src = '';
    };
  }, []);

  // Save settings to localStorage when they change (client-side only)
  useEffect(() => {
    if (!isClient) return;
    
    const state = {
      volume,
      repeatMode,
      playlistMode
    };
    
    try {
      localStorage.setItem(PLAYER_STATE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Error saving player state:', error);
    }
  }, [volume, repeatMode, playlistMode, isClient]);

  // Update audio source when current song changes
  useEffect(() => {
    if (!isClient || !audioRef.current || !currentSong) return;
    
    // Get audio URL from song - using preview_url if available
    const audioUrl = currentSong.features?.preview_url;
    if (!audioUrl) {
      console.error('Không có URL preview cho bài hát:', currentSong.title);
      nextSong(); // Skip to next song if no audio URL
      return;
    }
    
    // Set source and load audio
    audioRef.current.src = audioUrl;
    audioRef.current.load();
    
    // Auto-play if isPlaying is true
    if (isPlaying) {
      audioRef.current.play().catch(err => {
        console.error('Lỗi khi phát nhạc:', err);
        setIsPlaying(false);
      });
      
      // Track play event
      trackInteractionEvent({
        event_type: 'play',
        song_id: currentSong.id,
        context: {
          time_of_day: getTimeOfDay(),
          device: 'web',
          player_mode: playlistMode ? 'playlist' : 'standard',
        }
      }).catch(err => console.error('Error tracking play event:', err));
    }
  }, [currentSong, isPlaying, isClient, playlistMode]);

  // Update volume when it changes
  useEffect(() => {
    if (!isClient || !audioRef.current) return;
    audioRef.current.volume = volume;
  }, [volume, isClient]);

  // Handle play/pause state changes
  useEffect(() => {
    if (!isClient || !audioRef.current || !currentSong) return;
    
    if (isPlaying) {
      audioRef.current.play().catch(err => {
        console.error('Lỗi khi phát nhạc:', err);
        setIsPlaying(false);
      });
    } else {
      audioRef.current.pause();
    }
  }, [isPlaying, currentSong, isClient]);

  // Handler functions
  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setProgress(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return;
    setDuration(audioRef.current.duration);
  };

  const handleSongEnd = () => {
    if (repeatMode === 'one') {
      // Repeat the same song
      if (audioRef.current) {
        audioRef.current.currentTime = 0;
        audioRef.current.play().catch(err => {
          console.error('Lỗi khi phát lại bài hát:', err);
        });
      }
      return;
    }
    
    if (queue.length > 0 || repeatMode === 'all') {
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

  // Player control functions
  const playSong = (song: Song, newQueue: Song[] = []) => {
    // Add current song to history if it exists
    if (currentSong) {
      setHistory(prev => {
        const newHistory = [currentSong, ...prev].slice(0, MAX_HISTORY_LENGTH);
        return newHistory;
      });
    }
    
    // Set the current song and queue
    setCurrentSong(song);
    setQueue(newQueue);
    setIsPlaying(true);
    setProgress(0);
  };

  const pauseSong = () => {
    setIsPlaying(false);
  };

  const resumeSong = () => {
    setIsPlaying(true);
  };

  const nextSong = () => {
    if (queue.length === 0) {
      // If queue is empty but repeat all is on, restart from history
      if (repeatMode === 'all' && history.length > 0) {
        // Reverse the history to play from oldest to newest
        const historySongs = [...history].reverse();
        if (currentSong) {
          playSong(historySongs[0], historySongs.slice(1));
        }
        return;
      }
      
      // Otherwise, nothing to play next
      return;
    }
    
    // Get next song and update queue
    const nextSong = queue[0];
    const newQueue = queue.slice(1);
    
    // If current song exists, add to history
    if (currentSong) {
      setHistory(prev => {
        const newHistory = [currentSong, ...prev].slice(0, MAX_HISTORY_LENGTH);
        return newHistory;
      });
    }
    
    // Set the next song and update queue
    setCurrentSong(nextSong);
    setQueue(newQueue);
    setIsPlaying(true);
    setProgress(0);
  };

  const previousSong = () => {
    // If the current progress is more than 3 seconds, restart the song
    if (progress > 3) {
      seekTo(0);
      return;
    }
    
    // If there's no history, nothing to go back to
    if (history.length === 0) {
      return;
    }
    
    // Get the previous song from history
    const prevSong = history[0];
    const newHistory = history.slice(1);
    
    // If there's a current song, add it to the front of the queue
    if (currentSong) {
      setQueue(prev => [currentSong, ...prev]);
    }
    
    // Set the previous song and update history
    setCurrentSong(prevSong);
    setHistory(newHistory);
    setIsPlaying(true);
    setProgress(0);
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
    setQueue(prev => [...prev, song]);
  };

  const clearQueue = () => {
    setQueue([]);
  };

  const togglePlaylistMode = () => {
    setPlaylistMode(prev => !prev);
  };

  return (
    <PlayerContext.Provider
      value={{
        currentSong,
        queue,
        history,
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
        playlistMode,
        togglePlaylistMode,
        repeatMode,
        setRepeatMode,
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