import { describe, expect, it, vi } from 'vitest';
import { getJson, type Fetcher } from './http';

describe('HTTP JSON transport', () => {
  it('tugatilgan yuklashni signal orqali bekor qiladi', async () => {
    const controller = new AbortController();
    const fetcher = vi.fn<Fetcher>((_url, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
    }));
    const request = getJson('/mock/database.json', controller.signal, fetcher);
    const rejected = expect(request).rejects.toMatchObject({ name: 'AbortError' });
    controller.abort();
    await rejected;
    expect(fetcher.mock.calls[0][1]?.signal?.aborted).toBe(true);
  });
  it('noto‘g‘ri JSON yoki tarmoq xatosini aniq bildiradi', async () => {
    const broken = vi.fn<Fetcher>(async () => new Response('{ broken', { headers: { 'Content-Type': 'application/json' } }));
    await expect(getJson('/mock/database.json', new AbortController().signal, broken)).rejects.toThrow('to‘g‘ri JSON emas');
    const offline = vi.fn<Fetcher>(async () => { throw new TypeError('Network error'); });
    await expect(getJson('/mock/database.json', new AbortController().signal, offline)).rejects.toThrow('ulanib bo‘lmadi');
  });
});
