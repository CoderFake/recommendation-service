import { PageHeader } from '@/components/layout/page-header'
import { FeaturedSongs } from '@/components/discover/featured-songs'
import { GenresGrid } from '@/components/discover/genres-grid'
import { getRecommendations } from '@/lib/api/recommendations'
import { searchSongs } from '@/lib/api/songs'
import { getUserTasteProfile } from '@/lib/api/recommendations'
import { auth } from '@/lib/firebase'
import { cookies } from 'next/headers'

export const revalidate = 3600 

async function getAuthToken() {
  const currentUser = await auth.currentUser;
  if (currentUser) {
    return await currentUser.getIdToken();
  }
  
  // Thử lấy token từ cookie
  const cookieStore = cookies();
  const token = cookieStore.get('session')?.value;
  return token || null;
}

export default async function DiscoverPage() {
  let recentlyAdded = [];
  let recommendations = { recommendations: [] };
  let tasteProfile = { top_genres: [] };
  
  try {

    const songsResponse = await searchSongs({
      page: 1,
      size: 10,
    });
    recentlyAdded = songsResponse.songs;
    
    // Lấy đề xuất cho người dùng
    recommendations = await getRecommendations({
      limit: 10,
      include_liked: false,
    });
    
    // Lấy thông tin sở thích người dùng
    tasteProfile = await getUserTasteProfile();
  } catch (error) {
    console.error('Error fetching data:', error);
    // Không làm gì, hiển thị giao diện với dữ liệu rỗng nếu có lỗi
  }
  
  // Chuẩn bị dữ liệu thể loại từ sở thích người dùng
  const topGenres = tasteProfile.top_genres || [];
  
  return (
    <div className="space-y-12 py-6">
      <PageHeader
        title="Khám phá"
        description="Tìm kiếm âm nhạc mới và trải nghiệm đề xuất cá nhân hóa"
      />
      
      {recommendations.recommendations.length > 0 && (
        <FeaturedSongs
          title="Đề xuất cho bạn"
          description="Đề xuất dựa trên sở thích của bạn"
          songs={recommendations.recommendations.map(rec => rec.song)}
        />
      )}
      
      {recentlyAdded.length > 0 && (
        <FeaturedSongs
          title="Mới thêm gần đây"
          description="Bài hát mới thêm vào thư viện"
          songs={recentlyAdded}
        />
      )}
      
      {topGenres.length > 0 && (
        <GenresGrid genres={topGenres} />
      )}
    </div>
  )
}

