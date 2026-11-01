import { describe, it, expect } from 'vitest';
import { rateLimitMessage } from './apiError';

describe('rateLimitMessage', () => {
  it('uses the server detail for a 429', () => {
    expect(rateLimitMessage({ response: { status: 429, data: { detail: 'Please wait 12 seconds' } } })).toBe('Please wait 12 seconds');
  });
  it('falls back to Retry-After, then to a generic message', () => {
    expect(rateLimitMessage({ response: { status: 429, data: {}, headers: { 'retry-after': '1' } } })).toMatch(/wait 1 second and/);
    expect(rateLimitMessage({ response: { status: 429 } })).toMatch(/a moment/);
  });
  it('returns null for anything that is not a 429', () => {
    expect(rateLimitMessage({ response: { status: 500 } })).toBeNull();
    expect(rateLimitMessage(new Error('network'))).toBeNull();
    expect(rateLimitMessage(undefined)).toBeNull();
  });
});
