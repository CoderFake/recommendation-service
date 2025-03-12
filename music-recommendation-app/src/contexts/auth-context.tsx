// Update src/contexts/auth-context.tsx

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '@/lib/types';
import { auth } from '@/lib/firebase';
import { onAuthStateChanged, signOut as firebaseSignOut, User as FirebaseUser, signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { registerUser, getCurrentUser } from '@/lib/api/auth';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/use-toast';
import Cookies from 'js-cookie';

interface AuthContextType {
  user: User | null;
  firebaseUser: FirebaseUser | null;
  isLoading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, username: string, displayName?: string) => Promise<void>;
  signOut: () => Promise<void>;
  setUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setFirebaseUser(firebaseUser);

      if (firebaseUser) {
        try {
          const token = await firebaseUser.getIdToken();
          Cookies.set('session', token, { expires: 7 });

          try {
            const userData = await getCurrentUser();
            setUser(userData);
          } catch (apiError) {
            console.error('Error fetching user data:', apiError);
            setUser(null);
          }
        } catch (tokenError) {
          console.error('Error getting token:', tokenError);
          setUser(null);
          Cookies.remove('session');
        }
      } else {
        setUser(null);
        Cookies.remove('session');
      }

      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signIn = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);

      // Get token and set cookie
      const token = await userCredential.user.getIdToken();
      Cookies.set('session', token, { expires: 7 });

      try {
        // Fetch user data from our API
        const userData = await getCurrentUser();
        setUser(userData);

        toast({
          title: "Đăng nhập thành công",
          description: "Chào mừng bạn trở lại!",
        });
      } catch (apiError: any) {
        // User exists in Firebase but not in our database
        // This is an error state - they need to complete registration
        setError("Tài khoản chưa được đăng ký đầy đủ");
        toast({
          title: "Lỗi đăng nhập",
          description: "Tài khoản chưa được đăng ký đầy đủ. Vui lòng hoàn tất quá trình đăng ký.",
          variant: "destructive",
        });

        await firebaseSignOut(auth);
        Cookies.remove('session');
      }
    } catch (error: any) {
      let errorMessage = "Đăng nhập thất bại";

      if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
        errorMessage = "Email hoặc mật khẩu không đúng";
      } else if (error.code === 'auth/too-many-requests') {
        errorMessage = "Quá nhiều lần thử đăng nhập không thành công. Vui lòng thử lại sau.";
      } else if (error.code === 'auth/user-disabled') {
        errorMessage = "Tài khoản đã bị vô hiệu hóa";
      } else {
        errorMessage = error.message || "Đăng nhập thất bại";
      }

      setError(errorMessage);
      toast({
        title: "Lỗi đăng nhập",
        description: errorMessage,
        variant: "destructive",
      });
      setIsLoading(false);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signUp = async (email: string, password: string, username: string, displayName?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      Cookies.set('session', token, { expires: 7 });

      try {
        const userData = await registerUser({
          firebase_uid: userCredential.user.uid,
          email,
          username,
          display_name: displayName || username,
          avatar_url: userCredential.user.photoURL || undefined,
        });

        setUser(userData);

        toast({
          title: "Đăng ký thành công",
          description: "Tài khoản của bạn đã được tạo thành công",
        });
      } catch (apiError: any) {
        console.error("API registration error:", apiError);
        try {
          await userCredential.user.delete();
        } catch (deleteError) {
          console.error("Could not delete Firebase user after registration failure:", deleteError);
        }

        setError(apiError.message || "Đăng ký thất bại");
        toast({
          title: "Lỗi đăng ký",
          description: apiError.message || "Đăng ký thất bại. Vui lòng thử lại.",
          variant: "destructive",
        });

        await firebaseSignOut(auth);
        Cookies.remove('session');
      }
    } catch (error: any) {
      let errorMessage = "Đăng ký thất bại";

      if (error.code === 'auth/email-already-in-use') {
        errorMessage = "Email đã được sử dụng";
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = "Email không hợp lệ";
      } else if (error.code === 'auth/weak-password') {
        errorMessage = "Mật khẩu không đủ mạnh";
      } else {
        errorMessage = error.message || "Đăng ký thất bại";
      }

      setError(errorMessage);
      toast({
        title: "Lỗi đăng ký",
        description: errorMessage,
        variant: "destructive",
      });
      setIsLoading(false);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await firebaseSignOut(auth);
      Cookies.remove('session');
      setUser(null);
      router.push('/login');

      toast({
        title: "Đăng xuất thành công",
        description: "Hẹn gặp lại bạn!",
      });
    } catch (error: any) {
      setError(error.message || "Đăng xuất thất bại");
      toast({
        title: "Lỗi đăng xuất",
        description: error.message || "Đăng xuất thất bại",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const updateUserData = (updatedUser: User) => {
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        firebaseUser,
        isLoading,
        error,
        signIn,
        signUp,
        signOut,
        setUser: updateUserData,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth phải được sử dụng trong AuthProvider');
  }
  return context;
}