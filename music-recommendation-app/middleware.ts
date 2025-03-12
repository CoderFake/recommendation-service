import { NextRequest, NextResponse } from 'next/server';

export const config = {
  matcher: [
    '/discover/:path*',
    '/library/:path*',
    '/playlists/:path*',
    '/recommendations/:path*',
    '/taste-profile/:path*',
    '/admin/:path*',
  ],
};

export default async function middleware(req: NextRequest) {
  const token = req.cookies.get('session');
  const isAdminPath = req.nextUrl.pathname.startsWith('/admin');
  
  if (!token) {
    const loginUrl = new URL('/login', req.url);
    loginUrl.searchParams.set('callbackUrl', req.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  if (isAdminPath) {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Không phải admin');
      }
      
      const user = await response.json();
      
      if (!user.is_admin) {
        return NextResponse.redirect(new URL('/', req.url));
      }
    } catch (error) {
      return NextResponse.redirect(new URL('/', req.url));
    }
  }
  
  return NextResponse.next();
}