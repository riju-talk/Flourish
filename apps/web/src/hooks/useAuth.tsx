import { useState, useEffect, createContext, useContext } from 'react';
import { auth, googleProvider } from '@/lib/firebase';
import {
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User as FirebaseUser
} from "firebase/auth";
import { getProfile, createProfile } from '@/integrations/api';

interface User {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  idToken?: string;
}

export interface Profile {
  id: string;
  email: string;
  full_name?: string;
  phone_number?: string;
  display_name?: string;
  photo_url?: string;
  bio?: string;
  total_score: number;
  level: number;
  tasks_completed: number;
  streak_days: number;
  achievements: string[];
  privacy?: {
    public_profile_enabled: boolean;
    show_email: boolean;
    show_phone: boolean;
  };
  notification_preferences?: Record<string, boolean>;
}

interface AuthContextType {
  user: User | null;
  profile: Profile | null;
  loading: boolean;
  needsOnboarding: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
  completeOnboarding: (fullName: string, phoneNumber: string) => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadProfile = async () => {
    try {
      const existing = await getProfile();
      setProfile(existing);
      setNeedsOnboarding(false);
    } catch (error: any) {
      if (error?.response?.status === 404) {
        setProfile(null);
        setNeedsOnboarding(true);
      } else {
        console.error('Failed to load profile:', error);
      }
    }
  };

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

        await loadProfile();
      } else {
        setUser(null);
        setProfile(null);
        setNeedsOnboarding(false);
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

  const completeOnboarding = async (fullName: string, phoneNumber: string) => {
    if (!user) {
      throw new Error('Not signed in');
    }
    const created = await createProfile({
      email: user.email,
      display_name: user.displayName || '',
      photo_url: user.photoURL || '',
      full_name: fullName,
      phone_number: phoneNumber
    });
    setProfile(created);
    setNeedsOnboarding(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        loading,
        needsOnboarding,
        signInWithGoogle,
        signOut,
        getIdToken,
        completeOnboarding,
        refreshProfile: loadProfile
      }}
    >
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
