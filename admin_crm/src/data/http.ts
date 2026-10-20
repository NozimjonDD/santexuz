export type Fetcher = typeof fetch;
const REQUEST_TIMEOUT_MS = 20000;

export class DataRequestError extends Error {
  constructor(message: string, readonly status?: number) { super(message); this.name = 'DataRequestError'; }
}

export async function getJson(url: string, signal: AbortSignal, fetcher: Fetcher = fetch, credentials: RequestCredentials = 'same-origin'): Promise<unknown> {
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal.addEventListener('abort', abort, { once: true });
  if (signal.aborted) controller.abort();
  let timedOut = false;
  const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, REQUEST_TIMEOUT_MS);
  try {
    const response = await fetcher(url, {
      method: 'GET', headers: { Accept: 'application/json' }, signal: controller.signal,
      credentials, cache: 'no-store', redirect: 'error',
    });
    if (!response.ok) {
      const message = response.status === 401 || response.status === 403
        ? 'APIga kirish ruxsati yo‘q yoki sessiya tugagan. Backenddagi kirishni tekshiring.'
        : `Ma’lumotni olish amalga oshmadi (HTTP ${response.status}).`;
      throw new DataRequestError(message, response.status);
    }
    const contentType = response.headers.get('content-type')?.split(';')[0].trim().toLowerCase() ?? '';
    if (contentType !== 'application/json' && !contentType.endsWith('+json')) {
      throw new DataRequestError('JSON javob kutilgan edi. API manzili va server yo‘naltirishini tekshiring.');
    }
    try { return await response.json(); }
    catch { throw new DataRequestError('Server javobi to‘g‘ri JSON emas.'); }
  } catch (error) {
    if (signal.aborted) throw error;
    if (timedOut) throw new DataRequestError('Javob kutish vaqti tugadi. Qayta urinib ko‘ring.');
    if (error instanceof DataRequestError) throw error;
    throw new DataRequestError('Ma’lumot manbasiga ulanib bo‘lmadi. Tarmoq va API sozlamalarini tekshiring.');
  } finally {
    clearTimeout(timeout);
    signal.removeEventListener('abort', abort);
  }
}
