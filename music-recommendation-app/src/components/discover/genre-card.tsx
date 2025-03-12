
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface GenreCardProps {
  genre: string
  color?: string
  count?: number
}

export function GenreCard({ genre, color = 'bg-primary', count }: GenreCardProps) {
  return (
    <Link
      href={`/search?genre=${encodeURIComponent(genre)}`}
      className={cn(
        'block rounded-lg p-6 text-white shadow-md transition-transform hover:scale-105',
        color
      )}
    >
      <h3 className="text-xl font-bold">{genre}</h3>
      {count !== undefined && (
        <p className="mt-2 text-sm opacity-80">{count} bài hát</p>
      )}
    </Link>
  )
}

