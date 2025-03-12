'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

interface ErrorBoundaryProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorBoundary({ error, reset }: ErrorBoundaryProps) {
  useEffect(() => {
    console.error('Error boundary caught error:', error);
  }, [error]);

  let errorMessage = 'Đã có lỗi xảy ra';

  if (error.message.includes('unauthorized') || error.message.includes('Unauthorized')) {
    errorMessage = 'Bạn không có quyền truy cập vào trang này';
  } else if (error.message.includes('not found') || error.message.includes('Not found')) {
    errorMessage = 'Không tìm thấy trang hoặc nội dung yêu cầu';
  } else if (error.message.includes('timeout') || error.message.includes('Timeout')) {
    errorMessage = 'Kết nối bị gián đoạn hoặc máy chủ mất quá nhiều thời gian phản hồi';
  } else if (error.message.includes('network') || error.message.includes('Network')) {
    errorMessage = 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet của bạn';
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center text-center">
      <div className="space-y-6 max-w-md mx-auto p-6 rounded-lg border bg-card">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Đã xảy ra lỗi</h1>
          <p className="text-muted-foreground">{errorMessage}</p>

          {process.env.NODE_ENV === 'development' && (
            <div className="mt-6 overflow-x-auto rounded-md bg-slate-950 p-4 text-left text-xs text-slate-50">
              <p className="font-mono">{error.message}</p>
              {error.stack && (
                <pre className="mt-2 text-xs text-slate-400">{error.stack}</pre>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-center gap-2">
          <Button onClick={() => reset()}>Thử lại</Button>
          <Button variant="outline" onClick={() => window.location.href = "/"}>
            Về trang chủ
          </Button>
        </div>
      </div>
    </div>
  );
}