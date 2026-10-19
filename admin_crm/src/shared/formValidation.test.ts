import { describe, expect, it } from 'vitest';
import { validateFields } from './formValidation';

describe('Umumiy forma validatsiyasi', () => {
  it('checkbox roziligi va bir nechta yo‘nalish tanlanishini alohida tekshiradi', () => {
    const fields = [{ name: 'consent', label: 'Rozilik', type: 'checkbox' as const, required: true }, { name: 'categories', label: 'Yo‘nalishlar', type: 'multiselect' as const, required: true }];
    expect(Object.keys(validateFields(fields, { consent: false, categories: [] }))).toEqual(['consent', 'categories']);
    expect(validateFields(fields, { consent: true, categories: ['Ta’mirlash'] })).toEqual({});
  });

  it('foiz chegarasi, kasr va nol qiymatini to‘g‘ri ajratadi', () => {
    const fields = [{ name: 'rate', label: 'Komissiya', type: 'number' as const, min: 0, max: 100 }];
    expect(validateFields(fields, { rate: '0' })).toEqual({});
    expect(validateFields(fields, { rate: '-1' }).rate).toContain('kamida');
    expect(validateFields(fields, { rate: '101' }).rate).toContain('oshmasligi');
    expect(validateFields(fields, { rate: '1.5' }).rate).toBe('Butun son kiriting.');
    expect(validateFields(fields, { rate: '' })).toEqual({});
  });

  it('standart son tekshiruvidan keyin maxsus biznes validatsiyasini ham bajaradi', () => {
    expect(validateFields([{ name: 'advance', label: 'Avans', type: 'number', validate: value => Number(value) > 100 ? 'Foiz 100 dan oshmasin.' : null }], { advance: '101' }).advance).toBe('Foiz 100 dan oshmasin.');
  });
});
