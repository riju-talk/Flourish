import { useState, useEffect, createContext, useContext } from 'react';
import { auth, googleProvider } from '@/lib/firebase';
import {
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User as FirebaseUser
} from "firebase/auth";

interface User {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  idToken?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      if (firebaseUser) {
        const idToken = await firebaseUser.getIdToken();
        const mappedUser: User = {
          uid: firebaseUser.uid,
          email: firebaseUser.email || '',
          displayName: firebaseUser.displayName || '',
          photoURL: firebaseUser.photoURL || '',
          idToken
        };
        
        setUser(mappedUser);
        localStorage.setItem('flourish_user', JSON.stringify(mappedUser));
        localStorage.setItem('flourish_token', idToken);
        
        // Create user profile in database on sign in
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/profile`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${idToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              email: firebaseUser.email,
              display_name: firebaseUser.displayName || '',
              photo_url: firebaseUser.photoURL || ''
            })
          });
          
          if (response.ok) {
            const profileData = await response.json();
            console.log('='.repeat(60));
            console.log('👤 ACCOUNT CREATED/UPDATED IN DATABASE');
            console.log('='.repeat(60));
            console.log('🆔 User ID:', profileData.id);
            console.log('📧 Email:', profileData.email);
            console.log('👤 Display Name:', profileData.display_name);
            console.log('🖼️  Photo URL:', profileData.photo_url);
            console.log('🎯 Level:', profileData.level);
            console.log('⭐ Total Score:', profileData.total_score);
            console.log('🏆 Tasks Completed:', profileData.tasks_completed);
            console.log('🔥 Streak Days:', profileData.streak_days);
            console.log('🏅 Achievements:', profileData.achievements);
            console.log('='.repeat(60));
          } else {
            const errorText = await response.text();
            console.error('❌ Profile creation failed:', response.status, errorText);
          }
        } catch (error) {
          console.error('❌ Profile creation error:', error);
        }
      } else {
        setUser(null);
        localStorage.removeItem('flourish_user');
        localStorage.removeItem('flourish_token');
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    try {
      setLoading(true);
      const result = await signInWithPopup(auth, googleProvider);
      const idToken = await result.user.getIdToken();
      localStorage.setItem('flourish_token', idToken);
    } catch (error) {
      console.error('Error signing in:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      await firebaseSignOut(auth);
      localStorage.removeItem('flourish_token');
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    }
  };

  const getIdToken = async (): Promise<string | null> => {
    if (auth.currentUser) {
      return await auth.currentUser.getIdToken();
    }
    return localStorage.getItem('flourish_token');
  };

  return (
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, signOut, getIdToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};