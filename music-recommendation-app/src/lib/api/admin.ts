import { apiClient } from './client';
import { User, Song, RecommendationResponse, ModelStats } from '@/lib/types';

export async function getUsers(params: {
  page?: number;
  size?: number;
} = {}): Promise<{users: User[], total: number}> {
  const searchParams = new URLSearchParams();
  
  if (params.page) searchParams.append('page', params.page.toString());
  if (params.size) searchParams.append('size', params.size.toString());
  
  return apiClient(`/admin/users?${searchParams.toString()}`);
}

export async function getUser(userId: number): Promise<User> {
  return apiClient(`/admin/users/${userId}`);
}

export async function updateUserStatus(userId: number, isActive: boolean): Promise<User> {
  return apiClient(`/admin/users/${userId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ is_active: isActive }),
  });
}

export async function getSystemStats(): Promise<any> {
  return apiClient('/admin/stats');
}

export async function getModelStats(): Promise<ModelStats> {
  return apiClient('/admin/model/stats');
}

export async function retrainModel(): Promise<{status: string}> {
  return apiClient('/admin/model/retrain', {
    method: 'POST',
  });
}