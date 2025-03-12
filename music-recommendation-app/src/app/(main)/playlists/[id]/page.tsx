import { notFound } from 'next/navigation'
import { PlaylistDetail } from '@/components/playlists/playlist-detail'
import { getPlaylist } from '@/lib/api/playlists'

interface PlaylistPageProps {
  params: {
    id: string
  }
}

export default async function PlaylistPage({ params }: PlaylistPageProps) {
  const playlistId = parseInt(params.id, 10)
  
  if (isNaN(playlistId)) {
    notFound()
  }
  
  let playlistData
  
  try {
    playlistData = await getPlaylist(playlistId)
  } catch (error) {
    notFound()
  }
  
  return <PlaylistDetail playlistData={playlistData} />
}