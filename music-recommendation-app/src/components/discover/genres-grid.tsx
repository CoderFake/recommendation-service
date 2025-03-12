"use client"

import { GenreCard } from './genre-card'

interface GenresGridProps {
  genres: Array<{ genre: string; count: number }>;
}

const GENRE_COLORS = [
  'bg-blue-600',
  'bg-purple-600',
  'bg-pink-600',
  'bg-red-600',
  'bg-orange-600',
  'bg-yellow-600',
  'bg-green-600',
  'bg-teal-600',
  'bg-cyan-600',
  'bg-indigo-600',
]

export function GenresGrid({ genres }: GenresGridProps) {
  if (genres.length === 0) return null
  
  return (
    <div>
      <h2 className="mb-4 text-2xl font-bold">Thể loại phổ biến</h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {genres.map((item, index) => (
          <GenreCard
            key={item.genre}
            genre={item.genre}
            count={item.count}
            color={GENRE_COLORS[index % GENRE_COLORS.length]}
          />
        ))}
      </div>
    </div>
  )
}
