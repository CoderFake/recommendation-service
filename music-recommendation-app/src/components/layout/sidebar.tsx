"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Heart, Library, ListMusic, Home, Search, Headphones } from 'lucide-react'
import { cn } from '@/lib/utils'
import { buttonVariants } from '@/components/ui/button'
import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const { user } = useAuth()
  const [playlists, setPlaylists] = useState<{ id: number; title: string }[]>([])

  useEffect(() => {
    if (user) {
      setPlaylists([
        { id: 1, title: 'Nhạc yêu thích' },
        { id: 2, title: 'Workout mix' },
        { id: 3, title: 'Nhạc thư giãn' },
      ])
    }
  }, [user])

  return (
    <div className={cn("pb-12", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            Khám phá
          </h2>
          <div className="space-y-1">
            <Link
              href="/discover"
              className={cn(
                buttonVariants({ variant: "ghost" }),
                "w-full justify-start",
                pathname === '/discover' && "bg-accent text-accent-foreground"
              )}
            >
              <Home className="mr-2 h-4 w-4" />
              Trang chủ
            </Link>
            <Link
              href="/search"
              className={cn(
                buttonVariants({ variant: "ghost" }),
                "w-full justify-start",
                pathname === '/search' && "bg-accent text-accent-foreground"
              )}
            >
              <Search className="mr-2 h-4 w-4" />
              Tìm kiếm
            </Link>
            <Link
              href="/recommendations"
              className={cn(
                buttonVariants({ variant: "ghost" }),
                "w-full justify-start",
                pathname === '/recommendations' && "bg-accent text-accent-foreground"
              )}
            >
              <Headphones className="mr-2 h-4 w-4" />
              Đề xuất
            </Link>
          </div>
        </div>
        
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            Thư viện
          </h2>
          <div className="space-y-1">
            <Link
              href="/library"
              className={cn(
                buttonVariants({ variant: "ghost" }),
                "w-full justify-start",
                pathname === '/library' && "bg-accent text-accent-foreground"
              )}
            >
              <Library className="mr-2 h-4 w-4" />
              Tổng quan
            </Link>
            <Link
              href="/library/liked"
              className={cn(
                buttonVariants({ variant: "ghost" }),
                "w-full justify-start",
                pathname === '/library/liked' && "bg-accent text-accent-foreground"
              )}
            >
              <Heart className="mr-2 h-4 w-4" />
              Bài hát đã thích
            </Link>
            <Link
              href="/playlists"
              className={cn(
                buttonVariants({ variant: "ghost" }),
                "w-full justify-start",
                pathname === '/playlists' && "bg-accent text-accent-foreground"
              )}
            >
              <ListMusic className="mr-2 h-4 w-4" />
              Danh sách phát
            </Link>
          </div>
        </div>
        
        {playlists.length > 0 && (
          <div className="px-3 py-2">
            <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
              Playlist của bạn
            </h2>
            <div className="space-y-1">
              {playlists.map((playlist) => (
                <Link
                  key={playlist.id}
                  href={`/playlists/${playlist.id}`}
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "w-full justify-start",
                    pathname === `/playlists/${playlist.id}` && "bg-accent text-accent-foreground"
                  )}
                >
                  <ListMusic className="mr-2 h-4 w-4" />
                  {playlist.title}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

