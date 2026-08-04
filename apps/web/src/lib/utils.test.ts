import { describe, it, expect } from 'vitest';
import { cn } from './utils';

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('merges conditional class names', () => {
    const falsy = false;
    expect(cn('foo', falsy && 'bar', 'baz')).toBe('foo baz');
  });

  it('handles tailwind-merge conflicts (later wins)', () => {
    expect(cn('px-4', 'px-2')).toBe('px-2');
  });

  it('handles undefined and null values', () => {
    expect(cn('foo', undefined, null, 'bar')).toBe('foo bar');
  });

  it('returns empty string for no inputs', () => {
    expect(cn()).toBe('');
  });
});
