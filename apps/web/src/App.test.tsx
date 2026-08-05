import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

import React from 'react';

// Mock Firebase auth
vi.mock('@/hooks/useAuth', () => {
  const AuthProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;
  return {
    AuthProvider,
    useAuth: () => ({
      user: { uid: 'test-uid', email: 'test@test.com', displayName: 'Test User' },
      loading: false,
      signInWithGoogle: vi.fn(),
      signOut: vi.fn(),
      getIdToken: vi.fn(),
    }),
  };
});

// Mock Firebase init
vi.mock('@/lib/firebase', () => ({
  app: {},
  auth: {},
  storage: {},
  db: {},
  googleProvider: {},
}));

describe('App', () => {
  beforeEach(() => {
    // Suppress console errors during rendering
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(document.body).toBeTruthy();
  });

  it('renders the app shell without throwing', () => {
    expect(() => render(<App />)).not.toThrow();
    // "Flourish" legitimately appears more than once (navbar wordmark + footer).
    expect(screen.getAllByText('Flourish').length).toBeGreaterThan(0);
  });
});
