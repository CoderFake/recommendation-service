import { PageHeader } from '@/components/layout/page-header'
import { RecommendationList } from '@/components/recommendations/recommendation-list'
import { getRecommendations } from '@/lib/api/recommendations'

export default async function RecommendationsPage() {
  let recommendations = { recommendations: [], seed_info: {} };
  
  try {
    recommendations = await getRecommendations({
      limit: 20,
      include_liked: false,
    });
  } catch (error) {
    console.error('Error fetching recommendations:', error);
  }
  
  return (
    <div className="space-y-6 py-6">
      <PageHeader
        title="Đề xuất cho bạn"
        description="Bài hát được đề xuất dựa trên sở thích và lịch sử nghe của bạn"
      />
      
      <RecommendationList initialRecommendations={recommendations} />
    </div>
  )
}

