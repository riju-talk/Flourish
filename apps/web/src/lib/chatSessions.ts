import type { ChatSessionSummary } from '@/integrations/api';

export interface SessionGroup {
  label: 'Today' | 'Yesterday' | 'Previous 7 days' | 'Previous 30 days' | 'Older';
  sessions: ChatSessionSummary[];
}

const startOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
const DAY = 24 * 60 * 60 * 1000;

/**
 * Buckets sessions the way ChatGPT's sidebar does (Today / Yesterday / Previous 7 days /
 * Previous 30 days / Older), newest first inside each bucket. Empty buckets are omitted.
 */
export function groupSessionsByDate(sessions: ChatSessionSummary[], now: Date = new Date()): SessionGroup[] {
  const today = startOfDay(now);
  const order: SessionGroup['label'][] = ['Today', 'Yesterday', 'Previous 7 days', 'Previous 30 days', 'Older'];
  const buckets = new Map<SessionGroup['label'], ChatSessionSummary[]>(order.map((l) => [l, []]));

  const stamp = (s: ChatSessionSummary) => Date.parse(s.updated_at || s.created_at || '') || 0;

  for (const s of [...sessions].sort((a, b) => stamp(b) - stamp(a))) {
    const t = stamp(s);
    const age = today - startOfDay(new Date(t));
    const label: SessionGroup['label'] =
      t >= today ? 'Today' : age <= DAY ? 'Yesterday' : age <= 7 * DAY ? 'Previous 7 days' : age <= 30 * DAY ? 'Previous 30 days' : 'Older';
    buckets.get(label)!.push(s);
  }
  return order.map((label) => ({ label, sessions: buckets.get(label)! })).filter((g) => g.sessions.length > 0);
}
