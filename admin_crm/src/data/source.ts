import type { Database } from '../domain/types';
import { parseDataConfig, type DataConfig, type PublicApiEnvironment } from './config';
import { getJson, type Fetcher } from './http';
import { isRecord, parseDatabase } from './schema';
import { parseMockDatabase } from './mock';

export const resourcePaths = {
  customers: 'customers/', plumbers: 'plumbers/', shops: 'shops/', services: 'services/', materials: 'materials/',
  orders: 'orders/', payments: 'payments/', reviews: 'reviews/', templates: 'contract-templates/', audit: 'audit-events/',
} as const;
const MAX_COLLECTION_RECORDS = 10000;
const MAX_COLLECTION_PAGES = 200;

async function readCollection(path: string, base: URL, signal: AbortSignal, fetcher: Fetcher): Promise<unknown[]> {
  let url: URL | null = new URL(path, base);
  const seen = new Set<string>();
  const rows: unknown[] = [];
  while (url) {
    if (url.origin !== base.origin || !url.pathname.startsWith(base.pathname) || url.username || url.password || url.hash) {
      throw new Error('API sahifalash manzili sozlangan API chegarasidan tashqarida.');
    }
    if (seen.has(url.href) || seen.size >= MAX_COLLECTION_PAGES) throw new Error('API sahifalash chekloviga yetildi.');
    seen.add(url.href);
    const page: unknown = await getJson(url.href, signal, fetcher, 'include');
    let batch: unknown[];
    if (Array.isArray(page)) { batch = page; url = null; }
    else if (isRecord(page) && Array.isArray(page.results) && (page.next === null || typeof page.next === 'string')) {
      batch = page.results;
      url = page.next ? new URL(page.next, url) : null;
    } else throw new Error('API ro‘yxati massiv yoki { results, next } formatida bo‘lishi kerak.');
    if (rows.length + batch.length > MAX_COLLECTION_RECORDS) throw new Error('API ro‘yxati joriy UI hajm chegarasidan oshdi. Server sahifalash integratsiyasi kerak.');
    rows.push(...batch);
  }
  return rows;
}

export async function loadDatabase(config: DataConfig, signal: AbortSignal, origin: string, mockUrl: string, fetcher: Fetcher = fetch): Promise<Database> {
  if (config.mock) return parseMockDatabase(await getJson(mockUrl, signal, fetcher));
  const base = new URL(config.baseUrl, origin);
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal.addEventListener('abort', abort, { once: true });
  if (signal.aborted) controller.abort();
  try {
    const [entries, settings] = await Promise.all([
      Promise.all(Object.entries(resourcePaths).map(async ([key, path]) => [key, await readCollection(path, base, controller.signal, fetcher)] as const)),
      getJson(new URL('settings/', base).href, controller.signal, fetcher, 'include'),
    ]);
    return parseDatabase({ ...Object.fromEntries(entries), settings });
  } catch (error) {
    controller.abort();
    throw error;
  } finally { signal.removeEventListener('abort', abort); }
}

export async function loadApplicationData(signal: AbortSignal): Promise<{ config: DataConfig; db: Database }> {
  const config = parseDataConfig(import.meta.env as PublicApiEnvironment);
  const db = await loadDatabase(config, signal, window.location.origin, `${import.meta.env.BASE_URL}mock/database.json`);
  return { config, db };
}
