"use client"

import { useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';
import { User, UserUpdate } from '@/lib/types';
import { updateUser } from '@/lib/api/user';

export function useUser() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const handleUpdateUser = useCallback(async (data: UserUpdate): Promise<User | null> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const updatedUser = await updateUser(data);
      
      toast({
        title: 'Cập nhật thành công',
        description: 'Thông tin của bạn đã được cập nhật',
      });
      
      return updatedUser;
    } catch (err: any) {
      const message = err.message || 'Không thể cập nhật thông tin người dùng';
      setError(message);
      
      toast({
        title: 'Không thể cập nhật',
        description: message,
        variant: 'destructive',
      });
      
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  return {
    isLoading,
    error,
    updateUser: handleUpdateUser,
  };
}