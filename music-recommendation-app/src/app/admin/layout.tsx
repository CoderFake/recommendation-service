import { AdminNav } from '@/components/layout/admin-nav'

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <div className="container py-8">
        <AdminNav />
        <main>{children}</main>
      </div>
    </div>
  )
}

