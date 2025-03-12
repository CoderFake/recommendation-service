import { apiClient } from './client';
import { User, UserUpdate } from '@/lib/types';

export async function getCurrentUser(): Promise<User> {
  return apiClient('/auth/me');
}

export async function updateUser(data: UserUpdate): Promise<User> {
  return apiClient('/auth/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}