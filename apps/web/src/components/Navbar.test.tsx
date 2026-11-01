import { describe, it, expect, vi } from 'vitest';
import { render, screen, within, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { Navbar } from './Navbar';

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: {
      uid: 'test-uid',
      email: 'test@test.com',
      displayName: 'Test User',
      photoURL: 'https://example.com/photo.jpg',
    },
    profile: {
      full_name: 'Test User',
    },
    loading: false,
    signInWithGoogle: vi.fn(),
    signOut: vi.fn(),
    getIdToken: vi.fn(),
  }),
}));

vi.mock('./NotificationCenter', () => ({
  default: () => <div data-testid="notification-center" />,
}));

describe('Navbar', () => {
  it('renders the Flourish logo/title', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );
    expect(screen.getByText('Flourish')).toBeInTheDocument();
  });

  it('shows user avatar when user is logged in', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );
    const avatar = screen.getByAltText('User Avatar');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', 'https://example.com/photo.jpg');
  });

  it('shows sign out option in the account menu', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    await user.click(screen.getByAltText('User Avatar'));
    expect(await screen.findByText('Sign Out')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    expect(screen.getByText('Explore')).toBeInTheDocument();
    expect(screen.getByText('Calendar')).toBeInTheDocument();
    expect(screen.getByText('For You')).toBeInTheDocument();
    expect(screen.getByText('Leaderboard')).toBeInTheDocument();
  });

  it('renders NotificationCenter', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );
    expect(screen.getByTestId('notification-center')).toBeInTheDocument();
  });

  it('offers a phone menu with every destination, closing when one is chosen', async () => {
    render(
      <MemoryRouter initialEntries={['/calendar']}>
        <Navbar />
      </MemoryRouter>
    );
    await userEvent.click(screen.getByRole('button', { name: 'Open menu' }));
    const mobile = await screen.findByRole('navigation', { name: 'Mobile' });
    for (const label of ['Dashboard', 'AI Assistant', 'Calendar', 'Explore', 'For You', 'Leaderboard']) {
      expect(within(mobile).getByRole('link', { name: label })).toBeInTheDocument();
    }
    expect(within(mobile).getByRole('link', { name: 'Calendar' })).toHaveAttribute('aria-current', 'page');
    await userEvent.click(within(mobile).getByRole('link', { name: 'Explore' }));
    await waitFor(() => expect(screen.queryByRole('navigation', { name: 'Mobile' })).not.toBeInTheDocument());
  });
});
