import Link from 'next/link'
import { PlusCircle } from 'lucide-react'
import { PageHeader } from '@/components/layout/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDate } from '@/lib/utils'
import { getUserPlaylists } from '@/lib/api/playlists'

export default async function PlaylistsPage() {
  let playlists = []
  
  try {
    playlists = await getUserPlaylists()
  } catch (error) {
    console.error('Error fetching playlists:', error)
  }
  
  return (
    <div className="space-y-6 py-6">
      <div className="flex items-center justify-between">
        <PageHeader title="Playlist của bạn" />
        
        <Link href="/playlists/create">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            Tạo playlist
          </Button>
        </Link>
      </div>
      
      {playlists.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {playlists.map((playlist) => (
            <Link key={playlist.id} href={`/playlists/${playlist.id}`}>
              <Card className="h-full transition-colors hover:bg-accent cursor-pointer">
                <CardHeader className="pb-3">
                  <CardTitle className="line-clamp-1">{playlist.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground space-y-2">
                    <p>{playlist.song_count} bài hát</p>
                    <p className="line-clamp-2">{playlist.description || "Không có mô tả"}</p>
                    <p>Cập nhật: {formatDate(playlist.updated_at)}</p>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-md border p-8 text-center">
          <p className="mb-4 text-muted-foreground">Bạn chưa tạo playlist nào</p>
          <Link href="/playlists/create">
            <Button>
              <PlusCircle className="mr-2 h-4 w-4" />
              Tạo playlist đầu tiên
            </Button>
          </Link>
        </div>
      )}
    </div>
  )
}