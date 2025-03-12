import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Header } from '@/components/layout/header'
import { ThemeProvider } from '@/providers/theme-provider'
import { AuthProvider } from '@/contexts/auth-context'
import { PlayerProvider } from '@/contexts/player-context'
import { ToastContainer } from '@/providers/toast-provider'
import MusicPlayer from '@/components/music/music-player'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Nhạc Thông Minh - Hệ thống đề xuất nhạc cá nhân hóa',
  description: 'Khám phá âm nhạc phù hợp với gu âm nhạc của bạn với AI thông minh',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            <PlayerProvider>
              <div className="relative flex min-h-screen flex-col">
                <Header />
                <main className="flex-1">{children}</main>
                <MusicPlayer />
                <ToastContainer />
              </div>
            </PlayerProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}