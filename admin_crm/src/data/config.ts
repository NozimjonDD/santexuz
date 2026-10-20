export interface PublicApiEnvironment {
  readonly PUBLIC_API_MOCK?: string;
  readonly PUBLIC_API_BASE_URL?: string;
}
export type DataConfig = { readonly mock: true } | { readonly mock: false; readonly baseUrl: string };

export function parseDataConfig(env: PublicApiEnvironment): DataConfig {
  const value = env.PUBLIC_API_MOCK?.trim().toLowerCase() ?? 'true';
  if (value === 'true') return { mock: true };
  if (value !== 'false') throw new Error('PUBLIC_API_MOCK qiymati True yoki False bo‘lishi kerak.');

  const baseUrl = env.PUBLIC_API_BASE_URL?.trim();
  if (!baseUrl) throw new Error('Real rejim uchun PUBLIC_API_BASE_URL kiriting.');
  if (!/^https?:\/\//i.test(baseUrl) && (!baseUrl.startsWith('/') || baseUrl.startsWith('//'))) {
    throw new Error('PUBLIC_API_BASE_URL / bilan boshlanuvchi yo‘l yoki HTTP(S) manzil bo‘lsin.');
  }
  const parsed = new URL(baseUrl, 'https://configuration.invalid');
  if (parsed.username || parsed.password || parsed.search || parsed.hash) {
    throw new Error('PUBLIC_API_BASE_URL ichida login, parol, query yoki fragment bo‘lmasin.');
  }
  return { mock: false, baseUrl: baseUrl.replace(/\/+$/, '') + '/' };
}
