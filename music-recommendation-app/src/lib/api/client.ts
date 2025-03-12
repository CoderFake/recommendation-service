import { auth } from '@/lib/firebase';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:22222';

export class APIError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

export async function getAuthToken(): Promise<string | null> {
  try {
    const currentUser = auth.currentUser;
    if (currentUser) {
      return await currentUser.getIdToken(true);
    }

    const cookieToken = Cookies.get('session');
    if (cookieToken) {
      return cookieToken;
    }

    return null;
  } catch (error) {
    console.error('Lỗi lấy token:', error);
    return null;
  }
}

export async function apiClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else if (!endpoint.startsWith('/auth/register') && !endpoint.startsWith('/auth/login')) {
    throw new APIError(
      'Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn',
      401
    );
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_URL}/api/v1${endpoint}`, config);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { detail: response.statusText || 'Lỗi không xác định' };
      }

      if (response.status === 401) {
        Cookies.remove('session');
      }

      throw new APIError(
        errorData.detail || 'Đã xảy ra lỗi khi gọi API',
        response.status
      );
    }

    if (response.status === 204) {
      return {} as T;
    }

    try {
      const text = await response.text();
      const data = text ? JSON.parse(text) : {};
      return data as T;
    } catch (e) {
      throw new APIError(
        'Lỗi khi xử lý dữ liệu trả về',
        500
      );
    }
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    throw new APIError(
      error instanceof Error ? error.message : 'Lỗi kết nối đến server',
      500
    );
  }
}


