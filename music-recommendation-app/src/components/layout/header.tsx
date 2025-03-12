"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Search, Library, User, Music, LogOut, Sun, Moon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/layout/theme-toggle'
import { useAuth } from '@/contexts/auth-context'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { getInitials } from '@/lib/utils'

export function Header() {
  const { user, signOut } = useAuth()
  const pathname = usePathname()
  
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6 md:gap-8">
          <Link href="/" className="flex items-center gap-2">
            <Music className="h-6 w-6" />
            <span className="hidden font-bold sm:inline-block">
              Nhạc Thông Minh
            </span>
          </Link>
          
          <nav className="hidden md:flex gap-6">
            <Link
              href="/discover"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                pathname?.startsWith('/discover')
                  ? 'text-primary'
                  : 'text-muted-foreground'
              }`}
            >
              Khám phá
            </Link>
            <Link
              href="/search"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                pathname?.startsWith('/search')
                  ? 'text-primary'
                  : 'text-muted-foreground'
              }`}
            >
              Tìm kiếm
            </Link>
            <Link
              href="/library"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                pathname?.startsWith('/library')
                  ? 'text-primary'
                  : 'text-muted-foreground'
              }`}
            >
              Thư viện
            </Link>
          </nav>
        </div>
        
        <div className="flex items-center gap-2">
          <ThemeToggle />
          
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="relative h-8 w-8 rounded-full"
                >
                  <Avatar>
                    <AvatarImage src={user.avatar_url || undefined} alt={user.display_name || user.username} />
                    <AvatarFallback>{getInitials(user.display_name || user.username)}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <div className="flex items-center justify-start gap-2 p-2">
                  <div className="flex flex-col space-y-1 leading-none">
                    <p className="font-medium">{user.display_name || user.username}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/taste-profile" className="cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    <span>Sở thích âm nhạc</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/recommendations" className="cursor-pointer">
                    <Music className="mr-2 h-4 w-4" />
                    <span>Đề xuất cho bạn</span>
                  </Link>
                </DropdownMenuItem>
                {user.is_admin && (
                  <DropdownMenuItem asChild>
                    <Link href="/admin/dashboard" className="cursor-pointer">
                      <span>Quản trị viên</span>
                    </Link>
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => signOut()}
                  className="cursor-pointer"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Đăng xuất</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link href="/login">
              <Button size="sm">Đăng nhập</Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}