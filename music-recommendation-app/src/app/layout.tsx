import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Header } from '@/components/layout/header'
import { ThemeProvider } from '@/providers/theme-provider'
import { ToastContainer } from '@/providers/toast-provider'
import ClientProviders from '@/providers/client-providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Music song',
  description: 'Khám phá âm nhạc phù hợp với gu âm nhạc của bạn',
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
          <ClientProviders>
            <div className="relative flex min-h-screen flex-col">
              <Header />
              <main className="flex-1">{children}</main>
              <ToastContainer />
            </div>
          </ClientProviders>
        </ThemeProvider>
      </body>
    </html>
  )
}