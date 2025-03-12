import { notFound } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { PlaylistForm } from '@/components/playlists/playlist-form'
import { getPlaylist } from '@/lib/api/playlists'

interface EditPlaylistPageProps {
  params: {
    id: string
  }
}

export default async function EditPlaylistPage({ params }: EditPlaylistPageProps) {
  const playlistId = parseInt(params.id, 10)
  
  if (isNaN(playlistId)) {
    notFound()
  }
  
  let playlistData
  
  try {
    const data = await getPlaylist(playlistId)
    playlistData = data.playlist
  } catch (error) {
    notFound()
  }
  
  return (
    <div className="space-y-6 py-6">
      <PageHeader title="Chỉnh sửa playlist" />
      
      <PlaylistForm 
        initialData={playlistData} 
        isEditing={true} 
      />
    </div>
  )
}