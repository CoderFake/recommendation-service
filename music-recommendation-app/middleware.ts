
import { NextRequest, NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';

export const config = {
  matcher: [
    '/discover/:path*',
    '/library/:path*',
    '/playlists/:path*',
    '/recommendations/:path*',
    '/taste-profile/:path*',
    '/profile/:path*',
    '/admin/:path*',
  ],
};

export default async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;

  const sessionCookie = req.cookies.get('session');

  if (!sessionCookie?.value) {
    const loginUrl = new URL('/login', req.url);
    loginUrl.searchParams.set('callbackUrl', path);
    return NextResponse.redirect(loginUrl);
  }

  if (path.startsWith('/admin')) {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${sessionCookie.value}`,
        },
      });

      if (!response.ok) {
        throw new Error('Unauthorized');
      }

      const user = await response.json();

      if (!user.is_admin) {
        return NextResponse.redirect(new URL('/', req.url));
      }
    } catch (error) {
      const loginUrl = new URL('/login', req.url);
      loginUrl.searchParams.set('callbackUrl', path);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}