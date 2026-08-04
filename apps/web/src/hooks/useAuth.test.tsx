import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './useAuth';

vi.mock('@/lib/firebase', () => ({
  auth: {},
  storage: {},
  db: {},
  googleProvider: {},
}));

let authStateCallback: ((user: any) => void) | null = null;

vi.mock('firebase/auth', () => ({
  signInWithPopup: vi.fn(() => Promise.reject(new Error('not mocked'))),
  signOut: vi.fn(() => Promise.resolve()),
  onAuthStateChanged: vi.fn((_auth: any, cb: (user: any) => void) => {
    authStateCallback = cb;
    return vi.fn();
  }),
}));

function TestConsumer() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(auth.loading)}</span>
      <span data-testid="user-exists">{String(auth.user !== null)}</span>
      <span data-testid="has-signin">{typeof auth.signInWithGoogle}</span>
      <span data-testid="has-signout">{typeof auth.signOut}</span>
      <span data-testid="has-getidtoken">{typeof auth.getIdToken}</span>
    </div>
  );
}

describe('useAuth', () => {
  beforeEach(() => {
    authStateCallback = null;
  });

  it('provides auth context with user, loading, signInWithGoogle, signOut', () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );
    expect(screen.getByTestId('has-signin')).toHaveTextContent('function');
    expect(screen.getByTestId('has-signout')).toHaveTextContent('function');
    expect(screen.getByTestId('has-getidtoken')).toHaveTextContent('function');
  });

  it('starts with no user and updates when onAuthStateChanged fires', async () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    expect(screen.getByTestId('user-exists')).toHaveTextContent('false');

    authStateCallback?.({
      uid: 'test-uid',
      email: 'test@test.com',
      displayName: 'Test User',
      photoURL: 'http://example.com/photo.jpg',
      getIdToken: () => Promise.resolve('test-token'),
    });

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });
  });

  it('AuthProvider wraps children without crashing', () => {
    render(
      <AuthProvider>
        <div data-testid="child">child content</div>
      </AuthProvider>
    );
    expect(screen.getByTestId('child')).toHaveTextContent('child content');
  });

  it('throws when useAuth is used outside AuthProvider', () => {
    expect(() => render(<TestConsumer />)).toThrow(
      'useAuth must be used within an AuthProvider'
    );
  });
});
