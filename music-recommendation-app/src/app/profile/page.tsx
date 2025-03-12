import { PageHeader } from '@/components/layout/page-header'
import { ProfileForm } from '@/components/user/profile-form'
import { getCurrentUser } from '@/lib/api/user'

export default async function ProfilePage() {
  let user

  try {
    user = await getCurrentUser()
  } catch (error) {
    console.error('Error fetching user:', error)
    return {
      redirect: {
        destination: '/login',
        permanent: false,
      },
    }
  }

  return (
    <div className="space-y-6 py-6">
      <PageHeader
        title="Thông tin cá nhân"
        description="Xem và chỉnh sửa thông tin của bạn"
      />
      
      <ProfileForm user={user} />
    </div>
  )
}