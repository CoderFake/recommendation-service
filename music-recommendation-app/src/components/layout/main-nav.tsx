"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Search, Library, Music } from 'lucide-react'
import { cn } from '@/lib/utils'

export function MainNav() {
  const pathname = usePathname()
  
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 h-16 border-t bg-background md:hidden">
      <div className="grid h-full grid-cols-4">
        <Link
          href="/discover"
          className={cn(
            "flex flex-col items-center justify-center space-y-1",
            pathname?.startsWith('/discover')
              ? "text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Home className="h-5 w-5" />
          <span className="text-xs">Khám phá</span>
        </Link>
        <Link
          href="/search"
          className={cn(
            "flex flex-col items-center justify-center space-y-1",
            pathname?.startsWith('/search')
              ? "text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Search className="h-5 w-5" />
          <span className="text-xs">Tìm kiếm</span>
        </Link>
        <Link
          href="/library"
          className={cn(
            "flex flex-col items-center justify-center space-y-1",
            pathname?.startsWith('/library')
              ? "text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Library className="h-5 w-5" />
          <span className="text-xs">Thư viện</span>
        </Link>
        <Link
          href="/recommendations"
          className={cn(
            "flex flex-col items-center justify-center space-y-1",
            pathname?.startsWith('/recommendations')
              ? "text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Music className="h-5 w-5" />
          <span className="text-xs">Đề xuất</span>
        </Link>
      </div>
    </nav>
  )
}
