import { describe, expect, it, vi } from 'vitest';
import { createSeed, mockFixture } from './seed';
import { loadDatabase, resourcePaths } from './source';
import { parseDatabase } from './schema';
import type { Fetcher } from './http';

const origin = 'https://crm.test';
const baseUrl = 'https://backend.test/api/v1/admin/';
const mockUrl = '/mock/database.json';
const signal = () => new AbortController().signal;

describe('JSON yoki API ma’lumot manbasi', () => {
  it('mock rejimida faqat JSON oladi va snapshotlarni mustaqil nusxalaydi', async () => {
    const fetcher = vi.fn<Fetcher>(async () => Response.json(mockFixture()));
    const first = await loadDatabase({ mock: true }, signal(), origin, mockUrl, fetcher);
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher.mock.calls[0][0]).toBe(mockUrl);
    expect(first.orders).toHaveLength(18);
    const order = first.orders.find(item => item.status === 'completed')!;
    const saved = order.confirmedEstimate!.services[0].price;
    order.estimate.services[0].price = 1;
    expect(order.confirmedEstimate!.services[0].price).toBe(saved);
    expect(createSeed().orders.find(item => item.id === order.id)!.estimate.services[0].price).toBe(saved);
  });
  it('real rejimda base URL va barcha sahifalardagi API natijasidan foydalanadi', async () => {
    const db = createSeed();
    const fetcher = vi.fn<Fetcher>(async input => {
      const url = new URL(String(input));
      const key = Object.entries(resourcePaths).find(([, path]) => url.pathname === `/api/v1/admin/${path}`)?.[0] as keyof typeof resourcePaths | undefined;
      if (key === 'customers') return Response.json(url.search ? { results: db.customers.slice(1), next: null }
        : { results: db.customers.slice(0, 1), next: '?page=2' });
      if (key) return Response.json(db[key]);
      if (url.pathname === '/api/v1/admin/settings/') return Response.json(db.settings);
      throw new Error('Unexpected URL');
    });
    const result = await loadDatabase({ mock: false, baseUrl }, signal(), origin, mockUrl, fetcher);
    expect(result).toEqual(db);
    expect(fetcher.mock.calls.every(([url, init]) => String(url).startsWith(baseUrl) && init?.credentials === 'include')).toBe(true);
    expect(fetcher.mock.calls.some(([url]) => String(url).includes(mockUrl))).toBe(false);
  });
  it('API xatosida mockga qaytmaydi va HTML javobni rad etadi', async () => {
    const fetcher = vi.fn<Fetcher>(async () => new Response('<html>SPA fallback</html>', { headers: { 'Content-Type': 'text/html' } }));
    await expect(loadDatabase({ mock: false, baseUrl }, signal(), origin, mockUrl, fetcher)).rejects.toThrow('JSON');
    expect(fetcher.mock.calls.some(([url]) => String(url).includes(mockUrl))).toBe(false);
    const denied = vi.fn<Fetcher>(async () => new Response(null, { status: 403 }));
    await expect(loadDatabase({ mock: false, baseUrl }, signal(), origin, mockUrl, denied)).rejects.toThrow('ruxsati');
  });
  it('begona origin va takroriy pagination URLga o‘tmaydi', async () => {
    for (const next of ['https://untrusted.test/steal', `${baseUrl}customers/`]) {
      const fetcher = vi.fn<Fetcher>(async input => String(input).endsWith('customers/')
        ? Response.json({ results: [], next }) : Response.json([]));
      await expect(loadDatabase({ mock: false, baseUrl }, signal(), origin, mockUrl, fetcher)).rejects.toThrow();
      expect(fetcher.mock.calls.every(([url]) => String(url).startsWith(baseUrl))).toBe(true);
    }
  });
  it('noto‘g‘ri nested ma’lumot, reyting va takror IDni ekranga bermaydi', () => {
    const db = createSeed();
    expect(() => parseDatabase({ ...db, orders: [{ ...db.orders[0], estimate: null }] })).toThrow('orders[0].estimate');
    expect(() => parseDatabase({ ...db, reviews: [{ ...db.reviews[0], score: 8 }] })).toThrow('score');
    expect(() => parseDatabase({ ...db, customers: [db.customers[0], db.customers[0]] })).toThrow('takroriy');
  });
});
