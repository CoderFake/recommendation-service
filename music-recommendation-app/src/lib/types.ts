export interface UserRegistration {
    firebase_uid: string;
    email: string;
    username: string;
    display_name?: string;
    avatar_url?: string;
  }
  
  export interface User {
    id: number;
    firebase_uid: string;
    email: string;
    username: string;
    display_name?: string;
    avatar_url?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    is_admin?: boolean; 
  }
  
  // Song Types
  export interface Song {
    id: number;
    spotify_id: string;
    title: string;
    artist: string;
    artwork_url?: string;
    duration?: number;
    genre?: string;
    features?: Record<string, any>;
    created_at: string;
    updated_at: string;
  }
  
  export interface SongSearchResult {
    songs: Song[];
    total: number;
    page: number;
    size: number;
  }
  
  export interface SpotifyArtist {
    id: string;
    name: string;
  }
  
  export interface SpotifyAlbum {
    id: string;
    name: string;
    images: Array<{
      url: string;
      height: number;
      width: number;
    }>;
  }
  
  export interface SpotifyTrack {
    id: string;
    name: string;
    href: string;
    duration_ms: number;
    popularity?: number;
    album: SpotifyAlbum;
    artists: SpotifyArtist[];
    preview_url?: string;
    explicit: boolean;
  }
  
  // Interaction Types
  export interface InteractionBase {
    user_id: number;
    song_id: number;
    listen_count?: number;
    like_score?: number;
    saved?: boolean;
    context?: Record<string, any>;
  }
  
  export interface InteractionCreate {
    song_id: number;
    listen_count?: number;
    like_score?: number;
    saved?: boolean;
    context?: Record<string, any>;
  }
  
  export interface InteractionUpdate {
    listen_count?: number;
    like_score?: number;
    saved?: boolean;
    context?: Record<string, any>;
  }
  
  export interface Interaction extends InteractionBase {
    id: number;
    timestamp: string;
  }
  
  export interface InteractionEvent {
    event_type: 'play' | 'like' | 'unlike' | 'skip' | 'save' | 'unsave';
    song_id: number;
    timestamp?: string;
    duration?: number;
    position?: number;
    context?: Record<string, any>;
  }
  
  // Recommendation Types
  export interface RecommendationRequest {
    limit?: number;
    seed_songs?: number[];
    seed_genres?: string[];
    collaborative_weight?: number;
    content_based_weight?: number;
    diversity?: number;
    include_liked?: boolean;
    include_listened?: boolean;
  }
  
  export interface SongRecommendation {
    song: Song;
    score: number;
    relevance_factors: Record<string, number>;
  }
  
  export interface RecommendationResponse {
    recommendations: SongRecommendation[];
    seed_info: {
      seed_songs: number[];
      seed_genres: string[];
      collaborative_weight: number;
      content_based_weight: number;
      diversity?: number;
      include_liked: boolean;
      include_listened: boolean;
    };
    explanation?: string;
  }
  
  export interface UserTaste {
    top_genres: Array<{
      genre: string;
      count: number;
      score: number;
    }>;
    top_artists: Array<{
      artist: string;
      count: number;
      score: number;
    }>;
    listening_patterns: {
      time_of_day: Record<string, number>;
      devices: Record<string, number>;
    };
    genre_distribution: Record<string, number>;
    feature_preferences: Record<string, number>;
  }
  
  // Playlist Types
  export interface Playlist {
    id: number;
    user_id: number;
    title: string;
    description?: string;
    is_public: boolean;
    song_count: number;
    created_at: string;
    updated_at: string;
  }
  
  export interface PlaylistSong {
    id: number;
    playlist_id: number;
    song_id: number;
    position: number;
    added_at: string;
    song?: Song; // Expanded song data when needed
  }
  
  export interface PlaylistCreate {
    title: string;
    description?: string;
    is_public?: boolean;
  }
  
  export interface PlaylistUpdate {
    title?: string;
    description?: string;
    is_public?: boolean;
  }
  
  // Admin Types
  export interface ModelStats {
    last_training_time?: string;
    total_users: number;
    total_songs: number;
    total_interactions: number;
    training_history: {
      train_loss: number[];
      val_loss: number[];
      epochs_completed: number;
      best_val_loss: number;
    };
    performance_metrics: {
      precision?: number;
      recall?: number;
      ndcg?: number;
      diversity?: number;
      coverage?: number;
    };
  }