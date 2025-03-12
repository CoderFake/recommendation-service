"use client"

import { Song, SpotifyTrack } from '@/lib/types'
import { SongTable } from '@/components/music/song-table'
import { useState } from 'react'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { importSpotifyTrack } from '@/lib/api/songs'
import { useToast } from '@/hooks/use-toast'

interface SearchResultsProps {
  localResults: Song[]
  spotifyResults: SpotifyTrack[]
  isLoading: boolean
  onAddToPlaylist?: (song: Song) => void
}

export function SearchResults({ localResults, spotifyResults, isLoading, onAddToPlaylist }: SearchResultsProps) {
  const [importingIds, setImportingIds] = useState<Set<string>>(new Set())
  const { toast } = useToast()
  const [importedSongs, setImportedSongs] = useState<Song[]>([])
  

  const handleImportSpotify = async (track: SpotifyTrack) => {
    if (importingIds.has(track.id)) return
    
    try {
      setImportingIds(prev => new Set(prev).add(track.id))
      
      const importedSong = await importSpotifyTrack(track.id)
      
      toast({
        title: 'Đã thêm bài hát',
        description: `"${track.name}" - ${track.artists[0].name} đã được thêm vào thư viện`,
      })
      
      setImportedSongs(prev => [...prev, importedSong])
    } catch (error) {
      toast({
        title: 'Không thể thêm bài hát',
        description: 'Đã xảy ra lỗi khi thêm bài hát vào thư viện',
        variant: 'destructive',
      })
    } finally {
      setImportingIds(prev => {
        const next = new Set(prev)
        next.delete(track.id)
        return next
      })
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
      </div>
    )
  }
  
  const allLocalResults = [...localResults, ...importedSongs]
  
  return (
    <Tabs defaultValue="local" className="w-full">
      <TabsList className="grid w-full grid-cols-2 mb-4">
        <TabsTrigger value="local">Thư viện ({allLocalResults.length})</TabsTrigger>
        <TabsTrigger value="spotify">Spotify ({spotifyResults.length})</TabsTrigger>
      </TabsList>
      
      <TabsContent value="local">
        {allLocalResults.length > 0 ? (
          <SongTable
            songs={allLocalResults}
            emptyMessage="Không tìm thấy bài hát nào trong thư viện"
            onAddToPlaylist={onAddToPlaylist}
          />
        ) : (
          <div className="flex flex-col items-center justify-center py-12">
            <p className="mb-4 text-muted-foreground">Không tìm thấy bài hát nào trong thư viện</p>
            <p className="text-sm text-muted-foreground">Hãy thử chuyển sang tab Spotify để tìm và thêm bài hát mới</p>
          </div>
        )}
      </TabsContent>
      
      <TabsContent value="spotify">
        {spotifyResults.length > 0 ? (
          <div className="rounded-md border">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="p-4 text-left font-medium">Bài hát</th>
                  <th className="p-4 text-left font-medium hidden md:table-cell">Nghệ sĩ</th>
                  <th className="p-4 text-left font-medium hidden md:table-cell">Album</th>
                  <th className="p-4 text-left font-medium w-[100px]"></th>
                </tr>
              </thead>
              <tbody>
                {spotifyResults.map((track) => (
                  <tr key={track.id} className="border-b hover:bg-muted/50">
                    <td className="p-4">
                      <div className="flex items-center">
                        <img
                          src={track.album.images[0]?.url || '/images/album-placeholder.png'}
                          alt={track.name}
                          className="h-10 w-10 rounded object-cover mr-3"
                        />
                        <div>
                          <p className="font-medium">{track.name}</p>
                          <p className="text-sm text-muted-foreground md:hidden">
                            {track.artists[0].name}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4 hidden md:table-cell">{track.artists[0].name}</td>
                    <td className="p-4 hidden md:table-cell">{track.album.name}</td>
                    <td className="p-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleImportSpotify(track)}
                        disabled={importingIds.has(track.id)}
                      >
                        {importingIds.has(track.id) ? (
                          <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-primary"></div>
                        ) : (
                          <Plus className="h-4 w-4 mr-2" />
                        )}
                        <span className="sr-only md:not-sr-only text-xs">Thêm</span>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12">
            <p className="mb-2 text-muted-foreground">Không tìm thấy bài hát nào trên Spotify</p>
            <p className="text-sm text-muted-foreground">Hãy thử tìm kiếm với từ khóa khác</p>
          </div>
        )}
      </TabsContent>
    </Tabs>
  )
}