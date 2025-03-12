"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { buttonVariants } from '@/components/ui/button'

export function AdminNav() {
  const pathname = usePathname()
  
  return (
    <nav className="flex items-center space-x-4 lg:space-x-6 mb-8">
      <Link
        href="/admin/dashboard"
        className={cn(
          "text-sm font-medium transition-colors hover:text-primary",
          pathname === '/admin/dashboard'
            ? "text-primary"
            : "text-muted-foreground"
        )}
      >
        Dashboard
      </Link>
      <Link
        href="/admin/users"
        className={cn(
          "text-sm font-medium transition-colors hover:text-primary",
          pathname === '/admin/users'
            ? "text-primary"
            : "text-muted-foreground"
        )}
      >
        Người dùng
      </Link>
      <Link
        href="/admin/songs"
        className={cn(
          "text-sm font-medium transition-colors hover:text-primary",
          pathname === '/admin/songs'
            ? "text-primary"
            : "text-muted-foreground"
        )}
      >
        Bài hát
      </Link>
      <Link
        href="/admin/recommendations"
        className={cn(
          "text-sm font-medium transition-colors hover:text-primary",
          pathname === '/admin/recommendations'
            ? "text-primary"
            : "text-muted-foreground"
        )}
      >
        Đề xuất
      </Link>
      <Link
        href="/admin/model"
        className={cn(
          "text-sm font-medium transition-colors hover:text-primary",
          pathname === '/admin/model'
            ? "text-primary"
            : "text-muted-foreground"
        )}
      >
        Mô hình ML
      </Link>
    </nav>
  )
}