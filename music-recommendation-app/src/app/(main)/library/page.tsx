import { PageHeader } from '@/components/layout/page-header'
import { SongTable } from '@/components/music/song-table'
import { getUserInteractions } from '@/lib/api/interactions'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { PlusCircle } from 'lucide-react'

export default async function LibraryPage() {
  let interactions = [];
  let likedSongs = [];
  let recentlyPlayed = [];
  
  try {
    interactions = await getUserInteractions({ limit: 50 });

    likedSongs = interactions
      .filter(interaction => interaction.like_score > 0.7)
      .map(interaction => interaction.song)
      .slice(0, 10);
    
    recentlyPlayed = interactions
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .map(interaction => interaction.song)
      .slice(0, 10);
  } catch (error) {
    console.error('Error fetching interactions:', error);
  }
  
  return (
    <div className="space-y-8 py-6">
      <PageHeader title="Thư viện của bạn" />
      
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Bài hát đã thích</h2>
            <Link href="/library/liked">
              <Button variant="ghost">Xem tất cả</Button>
            </Link>
          </div>
          
          {likedSongs.length > 0 ? (
            <SongTable
              songs={likedSongs}
              emptyMessage="Bạn chưa thích bài hát nào"
            />
          ) : (
            <div className="rounded-md border p-8 text-center">
              <p className="mb-4 text-muted-foreground">Bạn chưa thích bài hát nào</p>
              <Link href="/discover">
                <Button>Khám phá bài hát</Button>
              </Link>
            </div>
          )}
        </div>
        
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Nghe gần đây</h2>
          
          {recentlyPlayed.length > 0 ? (
            <SongTable
              songs={recentlyPlayed}
              emptyMessage="Bạn chưa nghe bài hát nào"
            />
          ) : (
            <div className="rounded-md border p-8 text-center">
              <p className="mb-4 text-muted-foreground">Bạn chưa nghe bài hát nào</p>
              <Link href="/discover">
                <Button>Bắt đầu nghe nhạc</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Playlist của bạn</h2>
          <Link href="/playlists/create">
            <Button>
              <PlusCircle className="mr-2 h-4 w-4" />
              Tạo playlist
            </Button>
          </Link>
        </div>
        
        <div className="rounded-md border p-8 text-center">
          <p className="text-muted-foreground">
            Playlists sẽ hiển thị ở đây. Hãy tạo playlist đầu tiên của bạn!
          </p>
        </div>
      </div>
    </div>
  )
}
