import { auth } from '@/lib/firebase';

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
    if (!currentUser) return null;
    
    return await currentUser.getIdToken(true);
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
  }
  
  const config: RequestInit = {
    ...options,
    headers,
  };
  
  try {
    const response = await fetch(`${API_URL}/api/v1${endpoint}`, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: 'Lỗi không xác định'
      }));
      
      throw new APIError(
        errorData.detail || 'Đã xảy ra lỗi khi gọi API',
        response.status
      );
    }
    
    const text = await response.text();
    const data = text ? JSON.parse(text) : {};
    
    return data as T;
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

import { apiClient } from './client';
import { UserRegistration, User } from '@/lib/types';

export async function registerUser(userData: UserRegistration): Promise<User> {
  return apiClient('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

export async function getCurrentUser(): Promise<User> {
  return apiClient('/auth/me');
}

export async function updateUser(userData: Partial<User>): Promise<User> {
  return apiClient('/auth/me', {
    method: 'PUT',
    body: JSON.stringify(userData),
  });
}



