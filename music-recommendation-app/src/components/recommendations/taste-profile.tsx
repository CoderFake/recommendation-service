"use client"

import { UserTaste } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import Link from 'next/link'

interface TasteProfileProps {
  tasteProfile: UserTaste
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#ff6361', '#bc5090', '#58508d', '#003f5c', '#444e86', '#955196'];

export function TasteProfile({ tasteProfile }: TasteProfileProps) {
  const genreData = Object.entries(tasteProfile.genre_distribution).map(([name, value], index) => ({
    name,
    value: Math.round(value * 100),
    color: COLORS[index % COLORS.length],
  })).sort((a, b) => b.value - a.value).slice(0, 10);
  
  const artistData = tasteProfile.top_artists.map((artist, index) => ({
    name: artist.artist,
    value: artist.count,
    score: artist.score,
    color: COLORS[index % COLORS.length],
  }));
  
  const timeData = Object.entries(tasteProfile.listening_patterns.time_of_day).map(([name, value]) => ({
    name: name === 'morning' ? 'Sáng' 
      : name === 'afternoon' ? 'Chiều'
      : name === 'evening' ? 'Tối'
      : 'Đêm',
    value,
  }));
  
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Thể loại yêu thích</CardTitle>
            <CardDescription>
              Phân tích thể loại nhạc bạn nghe
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={genreData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {genreData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2">
              <h4 className="font-medium">Thể loại nổi bật</h4>
              <ul className="mt-2 space-y-1">
                {tasteProfile.top_genres.slice(0, 5).map((genre) => (
                  <li key={genre.genre}>
                    <Link
                      href={`/search?genre=${encodeURIComponent(genre.genre)}`}
                      className="text-primary hover:underline"
                    >
                      {genre.genre}
                    </Link>
                    <span className="ml-1 text-sm text-muted-foreground">
                      ({genre.count} bài hát, điểm: {genre.score.toFixed(1)})
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Nghệ sĩ yêu thích</CardTitle>
            <CardDescription>
              Nghệ sĩ bạn nghe nhiều nhất
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={artistData.slice(0, 5)}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" name="Số bài hát">
                    {artistData.slice(0, 5).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2">
              <h4 className="font-medium">Nghệ sĩ nổi bật</h4>
              <ul className="mt-2 space-y-1">
                {tasteProfile.top_artists.slice(0, 5).map((artist) => (
                  <li key={artist.artist}>
                    <Link
                      href={`/search?artist=${encodeURIComponent(artist.artist)}`}
                      className="text-primary hover:underline"
                    >
                      {artist.artist}
                    </Link>
                    <span className="ml-1 text-sm text-muted-foreground">
                      ({artist.count} bài hát, điểm: {artist.score.toFixed(1)})
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Thời gian nghe nhạc</CardTitle>
            <CardDescription>
              Khi nào bạn nghe nhạc nhiều nhất
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" name="Số lần nghe" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 text-sm text-muted-foreground">
              <p>Bạn thường nghe nhạc vào {
                timeData.sort((a, b) => b.value - a.value)[0]?.name.toLowerCase() || "buổi tối"
              }</p>
              <p className="mt-1">
                Thiết bị sử dụng nhiều nhất: {
                  Object.entries(tasteProfile.listening_patterns.devices)
                    .sort((a, b) => b[1] - a[1])[0]?.[0] || "web"
                }
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}