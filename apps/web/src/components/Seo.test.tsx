import { describe, it, expect } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { HelmetProvider } from 'react-helmet-async';
import { Seo } from './Seo';

const meta = (sel: string) => document.head.querySelector(sel)?.getAttribute('content') ?? document.head.querySelector(sel)?.getAttribute('href');

describe('Seo', () => {
  it('writes title, canonical and absolute Open Graph / Twitter tags', async () => {
    window.history.pushState({}, '', '/about/');
    render(<HelmetProvider><Seo title="About" description="Who built it" /></HelmetProvider>);
    await waitFor(() => expect(document.title).toBe('About | Flourish'));
    expect(meta('meta[name="description"]')).toBe('Who built it');
    expect(meta('link[rel="canonical"]')).toBe('https://flourish-web-iota.vercel.app/about');
    expect(meta('meta[property="og:url"]')).toBe('https://flourish-web-iota.vercel.app/about');
    expect(meta('meta[property="og:title"]')).toBe('About | Flourish');
    expect(meta('meta[property="og:image"]')).toBe('https://flourish-web-iota.vercel.app/og-image.png');
    expect(meta('meta[name="twitter:image"]')).toMatch(/^https:\/\//);
  });
});
