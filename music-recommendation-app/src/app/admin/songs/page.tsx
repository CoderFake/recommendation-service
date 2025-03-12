import { useState } from 'react';
import { PageHeader } from '@/components/layout/page-header';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { formatDate } from '@/lib/utils';
import { searchSongs } from '@/lib/api/songs';

interface AdminSongsPageProps {
  searchParams: {
    q?: string;
    page?: string;
    size?: string;
  };
}

export default async function AdminSongsPage({ searchParams }: AdminSongsPageProps) {
  const query = searchParams.q || '';
  const page = parseInt(searchParams.page || '1', 10);
  const size = parseInt(searchParams.size || '20', 10);
  
  let songsData = { songs: [], total: 0 };
  
  try {
    songsData = await searchSongs({
      q: query,
      page,
      size
    });
  } catch (error) {
    console.error('Error fetching songs:', error);
  }
  
  const totalPages = Math.ceil(songsData.total / size);
  
  return (
    <div className="space-y-6">
      <PageHeader title="Quản lý bài hát" description="Xem và quản lý tất cả bài hát trong hệ thống" />
      
      <div className="flex items-center justify-between">
        <div className="flex w-full max-w-sm items-center space-x-2">
          <Input
            type="text"
            placeholder="Tìm kiếm bài hát..."
            defaultValue={query}
          />
          <Button type="submit">Tìm</Button>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            disabled={page <= 1}
            href={`/admin/songs?page=${page - 1}&size=${size}&q=${query}`}
          >
            Trước
          </Button>
          <span className="text-sm">
            Trang {page} / {totalPages || 1}
          </span>
          <Button
            variant="outline"
            disabled={page >= totalPages}
            href={`/admin/songs?page=${page + 1}&size=${size}&q=${query}`}
          >
            Sau
          </Button>
        </div>
      </div>
      
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Tiêu đề</TableHead>
              <TableHead>Nghệ sĩ</TableHead>
              <TableHead>Thể loại</TableHead>
              <TableHead>Số lượt nghe</TableHead>
              <TableHead>Thời gian thêm</TableHead>
              <TableHead className="text-right">Thao tác</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {songsData.songs.map((song) => (
              <TableRow key={song.id}>
                <TableCell className="font-medium">{song.id}</TableCell>
                <TableCell>{song.title}</TableCell>
                <TableCell>{song.artist}</TableCell>
                <TableCell>{song.genre || 'N/A'}</TableCell>
                <TableCell>{song.listen_count || 0}</TableCell>
                <TableCell>{formatDate(song.created_at)}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm" href={`/songs/${song.id}`}>
                    Chi tiết
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            
            {songsData.songs.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  Không tìm thấy bài hát nào.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}