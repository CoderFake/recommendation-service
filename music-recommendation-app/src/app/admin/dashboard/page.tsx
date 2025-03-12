import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getSystemStats } from '@/lib/api/admin'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default async function AdminDashboardPage() {
  let stats = {
    users: {
      total: 0,
      active: 0,
      new_last_week: 0,
      growth_rate: 0
    },
    songs: {
      total: 0,
      genres: {}
    },
    interactions: {
      total: 0,
      likes: 0,
      plays: 0,
      by_day: []
    },
    system: {
      model_version: '',
      last_training: '',
      api_requests_today: 0
    }
  };
  
  try {
    stats = await getSystemStats();
  } catch (error) {
    console.error('Error fetching system stats:', error);
  }
  
  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" description="Tổng quan hệ thống" />
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tổng người dùng</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.users.total}</div>
            <p className="text-xs text-muted-foreground">
              {stats.users.active} người dùng đang hoạt động
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Người dùng mới</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.users.new_last_week}</div>
            <p className="text-xs text-muted-foreground">
              {stats.users.growth_rate > 0 ? '+' : ''}{stats.users.growth_rate}% so với tuần trước
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tổng bài hát</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.songs.total}</div>
            <p className="text-xs text-muted-foreground">
              {Object.keys(stats.songs.genres).length} thể loại
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tổng tương tác</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.interactions.total}</div>
            <p className="text-xs text-muted-foreground">
              {stats.interactions.plays} lượt nghe, {stats.interactions.likes} lượt thích
            </p>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Thống kê người dùng</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={stats.interactions.by_day}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="active_users" stroke="#8884d8" name="Người dùng hoạt động" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Tương tác hàng ngày</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={stats.interactions.by_day}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="plays" fill="#8884d8" name="Lượt nghe" />
                  <Bar dataKey="likes" fill="#82ca9d" name="Lượt thích" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Thông tin hệ thống</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <h3 className="text-sm font-medium">Phiên bản mô hình</h3>
              <p className="text-lg font-bold">{stats.system.model_version || 'v1.0.0'}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium">Huấn luyện gần nhất</h3>
              <p className="text-lg font-bold">{stats.system.last_training || 'Chưa có'}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium">API requests hôm nay</h3>
              <p className="text-lg font-bold">{stats.system.api_requests_today}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium">Trạng thái hệ thống</h3>
              <p className="text-lg font-bold text-green-500">Hoạt động</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
