import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Chat from './Chat';
import * as api from '@/integrations/api';

vi.mock('@/components/Navbar', () => ({ Navbar: () => <nav data-testid="navbar" /> }));
vi.mock('@/components/Seo', () => ({ Seo: () => null }));
vi.mock('@/integrations/api');

const now = new Date().toISOString();
const session = (id: string, title: string) => ({ id, title, created_at: now, updated_at: now, message_count: 2 });
const msg = (id: string, role: 'user' | 'assistant', content: string, suggestions: string[] = []) =>
  ({ id, role, content, suggestions, created_at: now });

function Where() {
  return <div data-testid="path">{useLocation().pathname}</div>;
}

function renderAt(path: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/chat/:sessionId?" element={<><Chat /><Where /></>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.resetAllMocks();
  Element.prototype.scrollIntoView = vi.fn();
  vi.mocked(api.listChatSessions).mockResolvedValue([session('s1', 'Fern watering'), session('s2', 'Monstera pests')]);
  vi.mocked(api.getChatSession).mockResolvedValue({
    ...session('s1', 'Fern watering'),
    messages: [msg('m1', 'user', 'How often do I water a fern?'), msg('m2', 'assistant', 'About once a week.', ['More tips?'])],
  });
});

describe('Chat page (persistent sessions)', () => {
  it('lists past chats in the sidebar and loads the selected conversation', async () => {
    renderAt('/chat/s1');
    expect(await screen.findByText('About once a week.')).toBeInTheDocument();
    expect(screen.getByText('How often do I water a fern?')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Monstera pests' })).toBeInTheDocument();
    expect(screen.getAllByText('Today').length).toBeGreaterThan(0);
  });

  it('sends a follow-up to the open session and appends the reply', async () => {
    vi.mocked(api.sendSessionMessage).mockResolvedValue({
      session: session('s1', 'Fern watering'),
      user_message: msg('m3', 'user', 'And in winter?'),
      assistant_message: msg('m4', 'assistant', 'Every two weeks.'),
      error: false,
    });
    renderAt('/chat/s1');
    await screen.findByText('About once a week.');
    await userEvent.type(screen.getByLabelText('Message PlantMind'), 'And in winter?');
    await userEvent.click(screen.getByRole('button', { name: 'Send message' }));
    expect(await screen.findByText('Every two weeks.')).toBeInTheDocument();
    expect(api.sendSessionMessage).toHaveBeenCalledWith('s1', 'And in winter?');
    expect(api.createChatSession).not.toHaveBeenCalled();
  });

  it('a first message creates a session, then navigates to it', async () => {
    vi.mocked(api.createChatSession).mockResolvedValue(session('new1', 'New chat'));
    vi.mocked(api.sendSessionMessage).mockResolvedValue({
      session: session('new1', 'Watering a cactus'),
      user_message: msg('m1', 'user', 'Water a cactus?'),
      assistant_message: msg('m2', 'assistant', 'Sparingly.'),
      error: false,
    });
    renderAt('/chat');
    await userEvent.type(await screen.findByLabelText('Message PlantMind'), 'Water a cactus?');
    await userEvent.click(screen.getByRole('button', { name: 'Send message' }));
    await waitFor(() => expect(screen.getByTestId('path')).toHaveTextContent('/chat/new1'));
    expect(await screen.findByText('Sparingly.')).toBeInTheDocument();
  });

  it('shows a notice and restores the text when the AI turn fails, without saving anything', async () => {
    vi.mocked(api.sendSessionMessage).mockResolvedValue({
      session: session('s1', 'Fern watering'),
      user_message: null,
      assistant_message: msg('error', 'assistant', "I'm having trouble reaching PlantMind right now."),
      error: true,
    });
    renderAt('/chat/s1');
    await screen.findByText('About once a week.');
    await userEvent.type(screen.getByLabelText('Message PlantMind'), 'retry me');
    await userEvent.click(screen.getByRole('button', { name: 'Send message' }));
    expect(await screen.findByText(/trouble reaching PlantMind/)).toBeInTheDocument();
    expect(screen.getByLabelText('Message PlantMind')).toHaveValue('retry me');
  });

  it('New chat returns to the welcome screen', async () => {
    renderAt('/chat/s1');
    await screen.findByText('About once a week.');
    await userEvent.click(screen.getAllByRole('button', { name: /New chat/ })[0]);
    expect(await screen.findByText(/How can I help your garden today/)).toBeInTheDocument();
    expect(screen.getByTestId('path')).toHaveTextContent(/^\/chat$/);
  });
});
