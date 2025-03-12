"use client"

import { SongRecommendation, RecommendationResponse } from '@/lib/types'
import { useState } from 'react'
import { SongTable } from '@/components/music/song-table'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { RefreshCw } from 'lucide-react'
import { getRecommendations } from '@/lib/api/recommendations'
import { useToast } from '@/hooks/use-toast'

interface RecommendationListProps {
  initialRecommendations: RecommendationResponse
  onAddToPlaylist?: (song: SongRecommendation['song']) => void
}

export function RecommendationList({ initialRecommendations, onAddToPlaylist }: RecommendationListProps) {
  const [recommendations, setRecommendations] = useState<RecommendationResponse>(initialRecommendations)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const { toast } = useToast()
  
  // Các tham số cho recommendations
  const [settings, setSettings] = useState({
    collaborativeWeight: recommendations.seed_info.collaborative_weight * 100,
    contentBasedWeight: recommendations.seed_info.content_based_weight * 100,
    includeLiked: recommendations.seed_info.include_liked,
    diversity: recommendations.seed_info.diversity ? recommendations.seed_info.diversity * 100 : 50,
  })
  
  const refreshRecommendations = async () => {
    try {
      setIsRefreshing(true)
      
      const newRecommendations = await getRecommendations({
        collaborative_weight: settings.collaborativeWeight / 100,
        content_based_weight: settings.contentBasedWeight / 100,
        include_liked: settings.includeLiked,
        diversity: settings.diversity / 100,
        seed_songs: recommendations.seed_info.seed_songs,
        seed_genres: recommendations.seed_info.seed_genres,
      })
      
      setRecommendations(newRecommendations)
      toast({
        title: 'Đã làm mới đề xuất',
        description: 'Danh sách đề xuất đã được cập nhật',
      })
    } catch (error) {
      toast({
        title: 'Không thể làm mới đề xuất',
        description: 'Đã xảy ra lỗi khi tải đề xuất mới',
        variant: 'destructive',
      })
    } finally {
      setIsRefreshing(false)
    }
  }
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
        <div>
          <h2 className="text-2xl font-bold">Đề xuất cho bạn</h2>
          <p className="text-muted-foreground">{recommendations.recommendations.length} bài hát được đề xuất dựa trên sở thích của bạn</p>
        </div>
        <Button
          onClick={refreshRecommendations}
          disabled={isRefreshing}
          className="md:w-auto"
        >
          {isRefreshing ? (
            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-4 w-4" />
          )}
          Làm mới đề xuất
        </Button>
      </div>
      
      {recommendations.explanation && (
        <div className="rounded-lg bg-muted p-4">
          <p>{recommendations.explanation}</p>
        </div>
      )}
      
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Trọng số hợp tác (Collaborative)</Label>
              <span className="text-sm text-muted-foreground">{Math.round(settings.collaborativeWeight)}%</span>
            </div>
            <Slider
              value={[settings.collaborativeWeight]}
              min={0}
              max={100}
              step={5}
              onValueChange={(values) => {
                const collaborative = values[0]
                const contentBased = 100 - collaborative
                setSettings({
                  ...settings,
                  collaborativeWeight: collaborative,
                  contentBasedWeight: contentBased,
                })
              }}
            />
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Trọng số nội dung (Content-based)</Label>
              <span className="text-sm text-muted-foreground">{Math.round(settings.contentBasedWeight)}%</span>
            </div>
            <Slider
              value={[settings.contentBasedWeight]}
              min={0}
              max={100}
              step={5}
              onValueChange={(values) => {
                const contentBased = values[0]
                const collaborative = 100 - contentBased
                setSettings({
                  ...settings,
                  contentBasedWeight: contentBased,
                  collaborativeWeight: collaborative,
                })
              }}
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Độ đa dạng</Label>
              <span className="text-sm text-muted-foreground">{Math.round(settings.diversity)}%</span>
            </div>
            <Slider
              value={[settings.diversity]}
              min={0}
              max={100}
              step={5}
              onValueChange={(values) => {
                setSettings({
                  ...settings,
                  diversity: values[0],
                })
              }}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              id="include-liked"
              checked={settings.includeLiked}
              onCheckedChange={(checked) => {
                setSettings({
                  ...settings,
                  includeLiked: checked,
                })
              }}
            />
            <Label htmlFor="include-liked">Bao gồm bài hát đã thích</Label>
          </div>
        </div>
      </div>
      
      <SongTable
        songs={recommendations.recommendations.map(rec => rec.song)}
        onAddToPlaylist={onAddToPlaylist ? song => onAddToPlaylist(song) : undefined}
      />
    </div>
  )
}

