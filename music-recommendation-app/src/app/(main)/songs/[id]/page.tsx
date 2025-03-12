import { PageHeader } from '@/components/layout/page-header'
import { SimilarSongs } from '@/components/recommendations/similar-songs'
import { getSong } from '@/lib/api/songs'
import { getSimilarSongs } from '@/lib/api/recommendations'
import { Button } from '@/components/ui/button'
import { Heart, Play, Plus } from 'lucide-react'
import Image from 'next/image'
import { formatDate, formatDuration } from '@/lib/utils'

interface SongPageProps {
  params: {
    id: string;
  }
}

export default async function SongPage({ params }: SongPageProps) {
  const songId = parseInt(params.id, 10);
  let song = null;
  let similarSongs = [];
  
  try {
    song = await getSong(songId);

    similarSongs = await getSimilarSongs(songId);
  } catch (error) {
    console.error('Error fetching song:', error);
  }
  
  if (!song) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Không tìm thấy bài hát</h1>
          <p className="text-muted-foreground">Bài hát không tồn tại hoặc đã bị xóa.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-8 py-6">
      <div className="flex flex-col md:flex-row md:items-center md:space-x-8">
        <div className="relative aspect-square h-64 w-64 overflow-hidden rounded-lg shadow-md">
          <Image
            src={song.artwork_url || '/images/album-placeholder.png'}
            alt={song.title}
            fill
            className="object-cover"
            priority
          />
        </div>
        
        <div className="mt-4 md:mt-0">
          <h1 className="text-3xl font-bold">{song.title}</h1>
          <p className="text-xl text-muted-foreground">{song.artist}</p>
          
          {song.genre && (
            <p className="mt-2 text-sm text-muted-foreground">
              Thể loại: {song.genre}
            </p>
          )}
          
          {song.duration && (
            <p className="mt-1 text-sm text-muted-foreground">
              Thời lượng: {formatDuration(song.duration)}
            </p>
          )}
          
          <div className="mt-6 flex space-x-4">
            <Button className="gap-2">
              <Play className="h-4 w-4" />
              Phát
            </Button>
            <Button variant="outline" className="gap-2">
              <Heart className="h-4 w-4" />
              Thích
            </Button>
            <Button variant="outline" className="gap-2">
              <Plus className="h-4 w-4" />
              Thêm vào playlist
            </Button>
          </div>
        </div>
      </div>
      
      {song.features && (
        <div className="rounded-lg border p-4">
          <h2 className="mb-4 text-xl font-medium">Thông tin chi tiết</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {song.features.popularity !== undefined && (
              <div>
                <p className="text-sm font-medium">Độ phổ biến</p>
                <p className="text-2xl font-bold">{song.features.popularity}/100</p>
              </div>
            )}
            
            {song.features.danceability !== undefined && (
              <div>
                <p className="text-sm font-medium">Khả năng nhảy</p>
                <p className="text-2xl font-bold">{Math.round(song.features.danceability * 100)}%</p>
              </div>
            )}
            
            {song.features.energy !== undefined && (
              <div>
                <p className="text-sm font-medium">Năng lượng</p>
                <p className="text-2xl font-bold">{Math.round(song.features.energy * 100)}%</p>
              </div>
            )}
            
            {song.features.tempo !== undefined && (
              <div>
                <p className="text-sm font-medium">Tempo</p>
                <p className="text-2xl font-bold">{Math.round(song.features.tempo)} BPM</p>
              </div>
            )}
            
            {song.features.valence !== undefined && (
              <div>
                <p className="text-sm font-medium">Tính tích cực</p>
                <p className="text-2xl font-bold">{Math.round(song.features.valence * 100)}%</p>
              </div>
            )}
            
            {song.features.acousticness !== undefined && (
              <div>
                <p className="text-sm font-medium">Âm thanh acoustic</p>
                <p className="text-2xl font-bold">{Math.round(song.features.acousticness * 100)}%</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      <div>
        <h2 className="mb-4 text-2xl font-bold">Bài hát tương tự</h2>
        <SimilarSongs songId={songId} initialSongs={similarSongs} />
      </div>
    </div>
  )
}

