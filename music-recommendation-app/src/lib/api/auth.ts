import { apiClient } from './client';
import { User, UserRegistration } from '@/lib/types';

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
