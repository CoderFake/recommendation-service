import { PageHeader } from '@/components/layout/page-header'
import { PlaylistForm } from '@/components/playlists/playlist-form'

export default function CreatePlaylistPage() {
  return (
    <div className="space-y-6 py-6">
      <PageHeader title="Tạo playlist mới" />
      
      <PlaylistForm />
    </div>
  )
}