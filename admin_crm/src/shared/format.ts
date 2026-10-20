const numberFormatter = new Intl.NumberFormat('uz-UZ');
const dateTimeFormatter = new Intl.DateTimeFormat('uz-UZ', {
  timeZone: 'Asia/Tashkent', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
});
const localDateFormatter = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Tashkent', year: 'numeric', month: '2-digit', day: '2-digit',
});

export const number = (value: number) => numberFormatter.format(value).replace(/\u00a0/g, ' ');
export const money = (value: number | null | undefined) => value == null ? 'Sozlanmagan' : `${number(value)} so‘m`;
export const dateTime = (value: string | null | undefined) => value ? dateTimeFormatter.format(new Date(value)) : 'Belgilanmagan';
export const localDate = (value: string) => localDateFormatter.format(new Date(value));
export function inDateRange(value: string, from: string, to: string) {
  const date = localDate(value);
  return (!from || date >= from) && (!to || date <= to);
}
export const includesQuery = (value: unknown, query: string) => String(value ?? '').toLocaleLowerCase('uz').includes(query.trim().toLocaleLowerCase('uz'));
let fallbackIdSequence = 0;
export function id(prefix: string) {
  const random = globalThis.crypto;
  if (typeof random?.randomUUID === 'function') return `${prefix}-${random.randomUUID().slice(0, 8)}`;
  // Local HTTP previews may expose getRandomValues without randomUUID.
  if (typeof random?.getRandomValues === 'function') {
    const value = random.getRandomValues(new Uint32Array(1))[0];
    return `${prefix}-${value.toString(16).padStart(8, '0')}`;
  }
  fallbackIdSequence += 1;
  return `${prefix}-${Date.now().toString(36)}-${fallbackIdSequence.toString(36)}`;
}
export const phoneValid = (phone: string) => /^\+998\d{9}$/.test(phone.replace(/[\s()-]/g, ''));
export const now = () => new Date().toISOString();
export function exportCsv(name: string, headers: string[], rows: unknown[][], demo = true) {
  const escape = (value: unknown) => {
    let text = String(value ?? 'Sozlanmagan');
    // Prevent spreadsheet formula execution, including whitespace-prefixed cells.
    if (/^[\s]*[=+@-]/.test(text)) text = `'${text}`;
    return `"${text.replace(/"/g, '""')}"`;
  };
  const content = '\uFEFF' + [headers, ...rows].map(row => row.map(escape).join(';')).join('\r\n');
  const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8;' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `${name}${demo ? '-DEMO' : ''}.csv`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
