"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useUser } from '@/hooks/use-user'
import { useAuth } from '@/contexts/auth-context'
import { User, UserUpdate } from '@/lib/types'
import { getInitials } from '@/lib/utils'

interface ProfileFormProps {
  user: User
}

export function ProfileForm({ user }: ProfileFormProps) {
  const [username, setUsername] = useState(user.username)
  const [displayName, setDisplayName] = useState(user.display_name || '')
  const [avatarUrl, setAvatarUrl] = useState(user.avatar_url || '')
  
  const router = useRouter()
  const { isLoading, updateUser } = useUser()
  const { setUser } = useAuth()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!username.trim()) {
      return
    }
    
    const data: UserUpdate = {
      username: username.trim(),
      display_name: displayName.trim() || undefined,
      avatar_url: avatarUrl.trim() || undefined,
    }
    
    const updatedUser = await updateUser(data)
    if (updatedUser) {
      setUser(updatedUser)
      router.push('/library')
    }
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Thông tin cá nhân</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          <div className="flex flex-col items-center space-y-4">
            <Avatar className="h-24 w-24">
              <AvatarImage src={avatarUrl || undefined} alt={displayName || username} />
              <AvatarFallback className="text-2xl">{getInitials(displayName || username)}</AvatarFallback>
            </Avatar>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="avatar_url">URL ảnh đại diện</Label>
            <Input
              id="avatar_url"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              placeholder="https://example.com/avatar.jpg"
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground">Nhập URL ảnh đại diện của bạn</p>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="username">Tên người dùng <span className="text-destructive">*</span></Label>
            <Input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="username"
              disabled={isLoading}
              required
              className={!username.trim() ? "border-destructive" : ""}
            />
            {!username.trim() && (
              <p className="text-xs text-destructive">Tên người dùng không được để trống</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="display_name">Tên hiển thị</Label>
            <Input
              id="display_name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Tên hiển thị"
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground">Tên sẽ hiển thị cho người dùng khác</p>
          </div>
          
          <div className="p-4 bg-muted rounded-md">
            <p className="text-sm text-muted-foreground">Email: {user.email}</p>
            <p className="text-xs text-muted-foreground mt-1">Email không thể thay đổi</p>
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
          <Button type="submit" disabled={isLoading || !username.trim()}>
            {isLoading ? 'Đang lưu...' : 'Cập nhật'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}