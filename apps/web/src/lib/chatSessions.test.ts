import { describe, it, expect } from 'vitest';
import { groupSessionsByDate } from './chatSessions';
import type { ChatSessionSummary } from '@/integrations/api';

const NOW = new Date(2026, 5, 15, 12, 0, 0); // 15 Jun 2026, noon local
const daysAgo = (n: number, hour = 9) => new Date(2026, 5, 15 - n, hour).toISOString();
const s = (id: string, updated: string | null): ChatSessionSummary => ({
  id, title: id, created_at: updated, updated_at: updated, message_count: 2,
});

describe('groupSessionsByDate', () => {
  it('buckets by recency and omits empty groups', () => {
    const groups = groupSessionsByDate(
      [s('old', daysAgo(90)), s('today', daysAgo(0)), s('yday', daysAgo(1)), s('week', daysAgo(5)), s('month', daysAgo(20))],
      NOW,
    );
    expect(groups.map((g) => g.label)).toEqual(['Today', 'Yesterday', 'Previous 7 days', 'Previous 30 days', 'Older']);
    expect(groups.map((g) => g.sessions[0].id)).toEqual(['today', 'yday', 'week', 'month', 'old']);
  });

  it('sorts newest first within a bucket', () => {
    const [today] = groupSessionsByDate([s('a', daysAgo(0, 8)), s('b', daysAgo(0, 11))], NOW);
    expect(today.sessions.map((x) => x.id)).toEqual(['b', 'a']);
  });

  it('returns nothing for no sessions and tolerates missing timestamps', () => {
    expect(groupSessionsByDate([], NOW)).toEqual([]);
    expect(groupSessionsByDate([s('x', null)], NOW)[0].label).toBe('Older');
  });
});
