"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { PlaylistCreate, PlaylistUpdate, Playlist } from '@/lib/types'
import { usePlaylists } from '@/hooks/use-playlists'

interface PlaylistFormProps {
  initialData?: Playlist
  isEditing?: boolean
}

export function PlaylistForm({ initialData, isEditing = false }: PlaylistFormProps) {
  const [title, setTitle] = useState(initialData?.title || '')
  const [description, setDescription] = useState(initialData?.description || '')
  const [isPublic, setIsPublic] = useState(initialData?.is_public !== false)
  
  const router = useRouter()
  const { 
    isLoading, 
    createPlaylist, 
    updatePlaylist 
  } = usePlaylists()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!title.trim()) {
      return
    }
    
    if (isEditing && initialData) {
      const data: PlaylistUpdate = {
        title: title.trim(),
        description: description.trim() || undefined,
        is_public: isPublic,
      }
      
      const updatedPlaylist = await updatePlaylist(initialData.id, data)
      if (updatedPlaylist) {
        router.push(`/playlists/${initialData.id}`)
      }
    } else {
      const data: PlaylistCreate = {
        title: title.trim(),
        description: description.trim() || undefined,
        is_public: isPublic,
      }
      
      const newPlaylist = await createPlaylist(data)
      if (newPlaylist) {
        router.push(`/playlists/${newPlaylist.id}`)
      }
    }
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEditing ? 'Chỉnh sửa playlist' : 'Tạo playlist mới'}</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Tiêu đề <span className="text-destructive">*</span></Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Nhập tiêu đề playlist"
              disabled={isLoading}
              required
              className={!title.trim() ? "border-destructive" : ""}
            />
            {!title.trim() && (
              <p className="text-xs text-destructive">Tiêu đề không được để trống</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Mô tả (tùy chọn)</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Mô tả về playlist này"
              disabled={isLoading}
              rows={3}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              id="is-public"
              checked={isPublic}
              onCheckedChange={setIsPublic}
              disabled={isLoading}
            />
            <Label htmlFor="is-public">Công khai</Label>
            <p className="text-xs text-muted-foreground ml-2">
              {isPublic 
                ? "Mọi người đều có thể xem playlist này" 
                : "Chỉ bạn mới có thể xem playlist này"}
            </p>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
            disabled={isLoading}
          >
            Hủy
          </Button>
          <Button type="submit" disabled={isLoading || !title.trim()}>
            {isLoading ? 'Đang lưu...' : isEditing ? 'Cập nhật' : 'Tạo playlist'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}