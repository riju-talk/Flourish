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

// Rendering the real "/" route pulls in Index, Navbar/NotificationCenter, and
// LeaderboardPreview, all of which call real API functions on mount. Without this,
// those fire real axios requests against a nonexistent backend in jsdom, and their
// rejections can surface as unhandled-rejection failures depending on exactly when
// they settle relative to test teardown. Only the functions actually invoked during
// initial mount of "/" are stubbed with resolved values matching their real shape -
// some callers (e.g. LeaderboardPreview) call these directly and .then() the result
// rather than going through react-query, so an unconfigured automock returning
// `undefined` would crash them instead of just leaving data empty.
vi.mock('@/integrations/api', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/integrations/api')>()),
  getPlants: vi.fn().mockResolvedValue([]),
  getTodayProgress: vi.fn().mockResolvedValue({ tasks: [], date: '', completed_count: 0, total_count: 0, completion_percent: 0 }),
  getNotifications: vi.fn().mockResolvedValue([]),
  getLeaderboard: vi.fn().mockResolvedValue({ leaderboard: [] }),
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

  it('renders the app shell without throwing', async () => {
    expect(() => render(<App />)).not.toThrow();
    // Routes are lazy-loaded (see App.tsx) - the Suspense fallback renders first, so
    // wait for the real page content instead of asserting synchronously.
    // "Flourish" legitimately appears more than once (navbar wordmark + footer).
    expect((await screen.findAllByText('Flourish')).length).toBeGreaterThan(0);
  });
});
