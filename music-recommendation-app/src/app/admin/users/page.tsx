import { PageHeader } from '@/components/layout/page-header'
import { getUsers } from '@/lib/api/admin'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatDate } from '@/lib/utils'

interface AdminUsersPageProps {
  searchParams: {
    page?: string;
    size?: string;
    q?: string;
  }
}

export default async function AdminUsersPage({ searchParams }: AdminUsersPageProps) {
  const page = parseInt(searchParams.page || '1', 10);
  const size = parseInt(searchParams.size || '10', 10);
  const query = searchParams.q || '';
  
  let usersData = { users: [], total: 0 };
  
  try {
    usersData = await getUsers({ page, size });
  } catch (error) {
    console.error('Error fetching users:', error);
  }
  
  const totalPages = Math.ceil(usersData.total / size);
  
  return (
    <div className="space-y-6">
      <PageHeader title="Quản lý người dùng" description="Xem và quản lý người dùng hệ thống" />
      
      <div className="flex items-center justify-between">
        <div className="flex w-full max-w-sm items-center space-x-2">
          <Input
            type="text"
            placeholder="Tìm kiếm theo tên, email..."
            defaultValue={query}
          />
          <Button type="submit">Tìm</Button>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            disabled={page <= 1}
            href={`/admin/users?page=${page - 1}&size=${size}&q=${query}`}
          >
            Trước
          </Button>
          <span className="text-sm">
            Trang {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            disabled={page >= totalPages}
            href={`/admin/users?page=${page + 1}&size=${size}&q=${query}`}
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
              <TableHead>Tên người dùng</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Ngày đăng ký</TableHead>
              <TableHead>Trạng thái</TableHead>
              <TableHead className="text-right">Thao tác</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {usersData.users.map((user) => (
              <TableRow key={user.id}>
                <TableCell className="font-medium">{user.id}</TableCell>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{formatDate(user.created_at)}</TableCell>
                <TableCell>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      user.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                    }`}
                  >
                    {user.is_active ? 'Hoạt động' : 'Bị khóa'}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm">
                    Chi tiết
                  </Button>
                  <Button variant="ghost" size="sm">
                    {user.is_active ? 'Khóa' : 'Mở khóa'}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            
            {usersData.users.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  Không tìm thấy người dùng nào.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

