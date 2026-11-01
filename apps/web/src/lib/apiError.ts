/**
 * If `error` is an HTTP 429 from the API's AI rate limiter, returns a friendly message
 * (the server's own wording when present); otherwise null so callers can show their
 * normal error. The backend sends the wait time in both `detail` and `Retry-After`.
 */
export function rateLimitMessage(error: unknown): string | null {
  const res = (error as { response?: { status?: number; data?: { detail?: unknown }; headers?: Record<string, string> } })?.response;
  if (res?.status !== 429) return null;
  if (typeof res.data?.detail === 'string' && res.data.detail) return res.data.detail;
  const wait = Number(res.headers?.['retry-after']);
  return Number.isFinite(wait) && wait > 0
    ? `You're going a little fast. Please wait ${wait} second${wait === 1 ? '' : 's'} and try again.`
    : "You're going a little fast. Please wait a moment and try again.";
}
