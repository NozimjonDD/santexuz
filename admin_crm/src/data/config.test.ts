import { describe, expect, it } from 'vitest';
import { parseDataConfig } from './config';

describe('Public API sozlamalari', () => {
  it('True/False qiymatlarini boolean sifatida o‘qiydi', () => {
    expect(parseDataConfig({ PUBLIC_API_MOCK: 'True' })).toEqual({ mock: true });
    expect(parseDataConfig({ PUBLIC_API_MOCK: ' false ', PUBLIC_API_BASE_URL: '/api/v1/admin' }))
      .toEqual({ mock: false, baseUrl: '/api/v1/admin/' });
    expect(parseDataConfig({})).toEqual({ mock: true });
  });
  it('noto‘g‘ri qiymat yoki API manzilini demo rejimiga aylantirmaydi', () => {
    for (const value of ['', 'yes', '0', '1']) expect(() => parseDataConfig({ PUBLIC_API_MOCK: value })).toThrow('True yoki False');
    for (const url of [undefined, '', 'api/admin', '//other.test/api/', 'ftp://other.test/', 'https://user:pass@other.test/', '/api/?token=secret', '/api/#fragment']) {
      expect(() => parseDataConfig({ PUBLIC_API_MOCK: 'False', PUBLIC_API_BASE_URL: url })).toThrow();
    }
  });
});
