import { PageHeader } from '@/components/layout/page-header'
import { TasteProfile } from '@/components/recommendations/taste-profile'
import { getUserTasteProfile } from '@/lib/api/recommendations'

export default async function TasteProfilePage() {
  let tasteProfile = {
    top_genres: [],
    top_artists: [],
    listening_patterns: {
      time_of_day: {},
      devices: {}
    },
    genre_distribution: {},
    feature_preferences: {}
  };
  
  try {
    tasteProfile = await getUserTasteProfile();
  } catch (error) {
    console.error('Error fetching taste profile:', error);
  }
  
  return (
    <div className="space-y-6 py-6">
      <PageHeader
        title="Sở thích âm nhạc của bạn"
        description="Phân tích về sở thích và thói quen nghe nhạc của bạn"
      />
      
      <TasteProfile tasteProfile={tasteProfile} />
      
      <div className="rounded-lg bg-muted p-4">
        <h3 className="mb-2 text-lg font-medium">Về sở thích âm nhạc</h3>
        <p className="text-sm text-muted-foreground">
          Sở thích âm nhạc của bạn được phân tích dựa trên lịch sử nghe nhạc và tương tác với các bài hát.
          Hệ thống sử dụng dữ liệu này để cung cấp đề xuất cá nhân hóa tốt hơn.
          Càng tương tác nhiều với hệ thống, đề xuất càng chính xác.
        </p>
      </div>
    </div>
  )
}

