"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/auth-context'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Music } from 'lucide-react'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { signUp } = useAuth()
  const { toast } = useToast()
  const router = useRouter()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !password || !username) {
      toast({
        title: 'Lỗi đăng ký',
        description: 'Vui lòng điền đầy đủ thông tin bắt buộc',
        variant: 'destructive',
      })
      return
    }
    
    try {
      setIsLoading(true)
      await signUp(email, password, username, displayName || username)
      toast({
        title: 'Đăng ký thành công',
        description: 'Tài khoản của bạn đã được tạo thành công',
      })
      router.push('/discover')
    } catch (error: any) {
      toast({
        title: 'Lỗi đăng ký',
        description: error.message || 'Đăng ký thất bại. Vui lòng thử lại sau.',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <Music className="mx-auto h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">Tạo tài khoản</h1>
          <p className="text-sm text-muted-foreground">
            Nhập thông tin của bạn để tạo tài khoản mới
          </p>
        </div>
        
        <Card>
          <form onSubmit={handleSubmit}>
            <CardContent className="pt-6">
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="username">Tên người dùng</Label>
                  <Input
                    id="username"
                    placeholder="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="displayName">Tên hiển thị (không bắt buộc)</Label>
                  <Input
                    id="displayName"
                    placeholder="Tên hiển thị"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    disabled={isLoading}
                  />
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="password">Mật khẩu</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
                
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Đang đăng ký...' : 'Đăng ký'}
                </Button>
              </div>
            </CardContent>
          </form>
          
          <CardFooter className="flex flex-col">
            <div className="mt-2 text-center text-sm text-muted-foreground">
              <p>
                Đã có tài khoản?{' '}
                <Link
                  href="/login"
                  className="text-primary underline-offset-4 transition-colors hover:underline"
                >
                  Đăng nhập
                </Link>
              </p>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}