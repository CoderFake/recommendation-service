import Link from 'next/link'
import { ArrowRight, Headphones, Search, Heart } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  return (
    <div>
      <section className="py-12 md:py-24 lg:py-32 xl:py-48">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
            <div className="flex flex-col justify-center space-y-4">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl">
                  Khám Phá Âm Nhạc Phù Hợp Với Bạn
                </h1>
                <p className="max-w-[600px] text-muted-foreground md:text-xl">
                  Nghe càng nhiều, đề xuất càng chính xác.
                </p>
              </div>
              <div className="flex flex-col gap-2 min-[400px]:flex-row">
                <Link href="/discover">
                  <Button size="lg" className="gap-1">
                    Bắt đầu ngay
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/recommendations">
                  <Button size="lg" variant="outline">
                    Xem đề xuất
                  </Button>
                </Link>
              </div>
            </div>
            <div className="bg-muted rounded-lg p-8 flex flex-col items-center justify-center space-y-6">
              <div className="grid grid-cols-3 gap-4 w-full">
                <div className="bg-background rounded-lg p-4 text-center">
                  <Headphones className="h-8 w-8 mx-auto mb-2" />
                  <p className="text-sm font-medium">Đề xuất thông minh</p>
                </div>
                <div className="bg-background rounded-lg p-4 text-center">
                  <Search className="h-8 w-8 mx-auto mb-2" />
                  <p className="text-sm font-medium">Tìm kiếm nhanh</p>
                </div>
                <div className="bg-background rounded-lg p-4 text-center">
                  <Heart className="h-8 w-8 mx-auto mb-2" />
                  <p className="text-sm font-medium">Nhạc yêu thích</p>
                </div>
              </div>
              <div className="space-y-2 text-center">
                <h3 className="text-xl font-bold">Tìm hiểu tính năng</h3>
                <p className="text-sm text-muted-foreground">
                  Khám phá các tính năng độc đáo để tận hưởng âm nhạc theo cách của bạn.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-muted py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6">
          <div className="mx-auto grid items-center gap-6 md:max-w-[64rem] md:grid-cols-2 lg:grid-cols-3">
            <div className="flex flex-col items-center justify-center space-y-2 border-border p-4 rounded-lg">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Headphones className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold">AI Học Tập</h3>
              <p className="text-center text-muted-foreground">
                Hệ thống học hỏi theo thời gian để hiểu sở thích âm nhạc của bạn ngày càng tốt hơn.
              </p>
            </div>
            <div className="flex flex-col items-center justify-center space-y-2 border-border p-4 rounded-lg">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Search className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold">Tích Hợp Spotify</h3>
              <p className="text-center text-muted-foreground">
                Dễ dàng tìm kiếm và thêm bài hát từ thư viện rộng lớn của Spotify.
              </p>
            </div>
            <div className="flex flex-col items-center justify-center space-y-2 border-border p-4 rounded-lg">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Heart className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold">Playlist Cá Nhân</h3>
              <p className="text-center text-muted-foreground">
                Tạo và quản lý các danh sách phát tùy chỉnh theo sở thích của bạn.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}