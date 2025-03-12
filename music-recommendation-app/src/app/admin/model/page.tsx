import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { getModelStats, retrainModel } from '@/lib/api/admin'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatDate } from '@/lib/utils'

export const revalidate = 0  

export default async function AdminModelPage() {
  let modelStats = {
    last_training_time: null,
    total_users: 0,
    total_songs: 0,
    total_interactions: 0,
    training_history: {
      train_loss: [],
      val_loss: [],
      epochs_completed: 0,
      best_val_loss: 0
    },
    performance_metrics: {
      precision: 0,
      recall: 0,
      ndcg: 0,
      diversity: 0,
      coverage: 0
    }
  };
  
  try {
    modelStats = await getModelStats();
  } catch (error) {
    console.error('Error fetching model stats:', error);
  }
  
  // Chuẩn bị dữ liệu biểu đồ
  const lossChartData = [];
  for (let i = 0; i < modelStats.training_history.train_loss.length; i++) {
    lossChartData.push({
      epoch: i + 1,
      train_loss: modelStats.training_history.train_loss[i],
      val_loss: modelStats.training_history.val_loss[i],
    });
  }
  
  const retrainModelAction = async () => {
    'use server';
    try {
      await retrainModel();
    } catch (error) {
      console.error('Error retraining model:', error);
    }
  };
  
  return (
    <div className="space-y-6">
      <PageHeader title="Quản lý mô hình" description="Giám sát và huấn luyện mô hình đề xuất" />
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Số lượng người dùng</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{modelStats.total_users}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Số lượng bài hát</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{modelStats.total_songs}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Số lượng tương tác</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{modelStats.total_interactions}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Huấn luyện gần nhất</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {modelStats.last_training_time 
                ? formatDate(modelStats.last_training_time)
                : 'Chưa có'}
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quá trình huấn luyện</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              {lossChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={lossChartData}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="train_loss" stroke="#8884d8" name="Train Loss" />
                    <Line type="monotone" dataKey="val_loss" stroke="#82ca9d" name="Validation Loss" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center">
                  <p className="text-muted-foreground">Không có dữ liệu huấn luyện</p>
                </div>
              )}
            </div>
            
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium">Epochs hoàn thành</h3>
                <p className="text-xl font-bold">{modelStats.training_history.epochs_completed}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium">Best Validation Loss</h3>
                <p className="text-xl font-bold">{modelStats.training_history.best_val_loss?.toFixed(4) || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Độ chính xác</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="text-sm font-medium">Precision</h3>
                <p className="text-xl font-bold">{(modelStats.performance_metrics.precision * 100).toFixed(2) || 'N/A'}%</p>
              </div>
              <div>
                <h3 className="text-sm font-medium">Recall</h3>
                <p className="text-xl font-bold">{(modelStats.performance_metrics.recall * 100).toFixed(2) || 'N/A'}%</p>
              </div>
              <div>
                <h3 className="text-sm font-medium">NDCG</h3>
                <p className="text-xl font-bold">{(modelStats.performance_metrics.ndcg * 100).toFixed(2) || 'N/A'}%</p>
              </div>
              <div>
                <h3 className="text-sm font-medium">Diversity</h3>
                <p className="text-xl font-bold">{(modelStats.performance_metrics.diversity * 100).toFixed(2) || 'N/A'}%</p>
              </div>
              <div>
                <h3 className="text-sm font-medium">Coverage</h3>
                <p className="text-xl font-bold">{(modelStats.performance_metrics.coverage * 100).toFixed(2) || 'N/A'}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="flex justify-center">
        <form action={retrainModelAction}>
          <Button type="submit" size="lg">
            Huấn luyện lại mô hình
          </Button>
        </form>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Thông tin phương pháp học máy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium">Neural Collaborative Filtering</h3>
              <p className="text-muted-foreground">
                Mô hình sử dụng mạng neural kết hợp với phương pháp matrix factorization để dự đoán điểm số người dùng đối với các bài hát.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium">Content-based Filtering</h3>
              <p className="text-muted-foreground">
                Sử dụng đặc trưng âm thanh và metadata của bài hát để tìm kiếm các bài hát tương tự.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium">Hybrid Recommender</h3>
              <p className="text-muted-foreground">
                Kết hợp cả hai phương pháp trên với trọng số tùy chỉnh để tạo ra đề xuất tốt nhất.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium">Incremental Learning</h3>
              <p className="text-muted-foreground">
                Mô hình được cập nhật liên tục theo thời gian thực dựa trên tương tác người dùng.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
