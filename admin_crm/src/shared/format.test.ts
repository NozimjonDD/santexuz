import { describe, expect, it, vi } from 'vitest';
import { id, inDateRange, localDate, money, phoneValid } from './format';

describe('Mahalliy formatlar', () => {
  it('kiritilmagan summa va nolni ajratadi', () => {
    expect(money(null)).toBe('Sozlanmagan');
    expect(money(0)).toBe('0 so‘m');
  });
  it('sana filtrida Toshkent yarim tunini hisobga oladi', () => {
    const utc = '2026-10-17T20:30:00Z';
    expect(localDate(utc)).toBe('2026-10-18');
    expect(inDateRange(utc, '2026-10-18', '2026-10-18')).toBe(true);
    expect(inDateRange(utc, '', '2026-10-17')).toBe(false);
  });
  it('O‘zbekiston telefon formatini tekshiradi', () => {
    expect(phoneValid('+998 00 000 00 01')).toBe(true);
    expect(phoneValid('998000000001')).toBe(false);
    expect(phoneValid('+998000')).toBe(false);
  });
  it('randomUUID bo‘lmagan lokal HTTP muhitida ID yaratadi', () => {
    const getRandomValues = vi.fn((values: Uint32Array) => {
      values[0] = 42;
      return values;
    });
    vi.stubGlobal('crypto', { getRandomValues });
    try {
      expect(id('DEMO')).toBe('DEMO-0000002a');
      expect(getRandomValues).toHaveBeenCalledOnce();
    } finally {
      vi.unstubAllGlobals();
    }
  });
  it('crypto mavjud bo‘lmasa ham bir vaqtda turli demo ID beradi', () => {
    vi.stubGlobal('crypto', undefined);
    try {
      const first = id('DEMO');
      const second = id('DEMO');
      expect(first).toMatch(/^DEMO-/);
      expect(second).not.toBe(first);
    } finally {
      vi.unstubAllGlobals();
    }
  });
});
