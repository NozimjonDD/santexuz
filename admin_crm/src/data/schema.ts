import { statusLabels, type Database } from '../domain/types';

type Check = (value: unknown, path: string) => void;
const invalid = (path: string): never => { throw new Error(`Ma’lumot formati mos emas: ${path}.`); };
const text: Check = (value, path) => { if (typeof value !== 'string') invalid(path); };
const numeric: Check = (value, path) => { if (typeof value !== 'number' || !Number.isFinite(value)) invalid(path); };
const boolean: Check = (value, path) => { if (typeof value !== 'boolean') invalid(path); };
const nullable = (check: Check): Check => (value, path) => { if (value !== null) check(value, path); };
const optional = (check: Check): Check => (value, path) => { if (value !== undefined) check(value, path); };
const list = (check: Check): Check => (value, path) => {
  if (!Array.isArray(value)) return invalid(path);
  value.forEach((item, index) => check(item, `${path}[${index}]`));
};
const shape = (fields: Record<string, Check>): Check => (value, path) => {
  if (!isRecord(value)) return invalid(path);
  Object.entries(fields).forEach(([key, check]) => check(value[key], `${path}.${key}`));
};
const oneOf = (values: readonly string[]): Check => (value, path) => { if (typeof value !== 'string' || !values.includes(value)) invalid(path); };
const date: Check = (value, path) => { text(value, path); if (!Number.isFinite(Date.parse(value as string))) invalid(path); };
const optionalDate: Check = (value, path) => { if (value !== '') date(value, path); };
const money = nullable(numeric);
const unknownValue: Check = () => {};
export function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

const line = shape({ id: text, name: text, quantity: numeric, unit: text, price: money, brand: optional(text), available: optional(boolean) });
const estimate = shape({ version: numeric, services: list(line), materials: list(line), deliveryFee: money, emergencyFee: money, approved: boolean, createdAt: date });
const signatures: Check = (value, path) => { list(boolean)(value, path); if ((value as unknown[]).length !== 4) invalid(path); };
const contract = shape({ templateId: text, version: numeric, language: text, text, signatures, signedAt: nullable(date), signedBy: nullable(text) });
const status = oneOf(Object.keys(statusLabels));

export const databaseChecks: Record<keyof Database, Check> = {
  customers: list(shape({ id: text, name: text, phone: text, telegramId: text, createdAt: date, notes: text, consent: boolean })),
  plumbers: list(shape({ id: text, name: text, phone: text, telegramId: text, district: text, categories: list(text), experience: numeric, photo: text, notes: text, isActive: boolean, commission: money })),
  shops: list(shape({ id: text, name: text, contactName: text, address: text, district: text, phone: text, telegramId: text, description: text, isActive: boolean, commission: money })),
  services: list(shape({ id: text, name: text, nameRu: text, nameEn: text, category: text, unit: text, areaRate: money, emergencyFee: money, warranty: text, description: text, isActive: boolean, visible: boolean })),
  materials: list(shape({ id: text, name: text, category: text, brand: text, size: text, unit: text, description: text, isActive: boolean })),
  orders: list(shape({
    id: text, createdAt: date, customerId: text, plumberId: nullable(text), shopId: nullable(text), category: text, service: text,
    address: text, coordinates: text, description: text, status, urgent: boolean, urgencyApproved: boolean, consent: boolean,
    assignedAt: nullable(date), inspectionAt: optionalDate, workStart: optionalDate, workEnd: optionalDate, etaReason: text, preparationMinutes: money,
    estimate, confirmedEstimate: nullable(estimate), estimateHistory: list(estimate), advance: shape({ mode: oneOf(['percent', 'fixed']), value: money }),
    commissions: shape({ plumber: money, shop: money }), contract, contractHistory: optional(list(contract)),
    deliveries: list(shape({ id: text, label: text, status: oneOf(['preparing', 'transit', 'delivered']), eta: optionalDate, note: text })),
    timeline: list(shape({ id: text, at: date, title: text, detail: text })), notes: list(text),
    dispute: shape({ open: boolean, reason: text, resolution: text, previousStatus: nullable(status) }),
    materialReceived: boolean, customerCompleted: boolean, preparationStarted: boolean, workStarted: boolean,
    cancelReason: text, refundDecision: nullable(oneOf(['pending', 'full', 'none'])),
  })),
  payments: list(shape({
    id: text, orderId: text, type: oneOf(['advance', 'balance', 'cash_handover', 'shop_settlement', 'plumber_settlement', 'refund']),
    method: oneOf(['cash', 'terminal']), amount: numeric, timestamp: date, receivedBy: text, recordedBy: text, note: text,
    status: oneOf(['recorded', 'confirmed']), collector: oneOf(['center', 'plumber']), confirmedBy: nullable(text),
  })),
  reviews: list(shape({ id: text, orderId: text, customerId: text, targetType: oneOf(['plumber', 'shop']), targetId: text, score: (value, path) => { if (typeof value !== 'number' || !Number.isInteger(value) || value < 1 || value > 5) invalid(path); }, comment: text, createdAt: date, status: oneOf(['pending', 'published', 'hidden']) })),
  templates: list(shape({ id: text, name: text, language: text, version: numeric, note: text, text, status: oneOf(['draft', 'active', 'archived']), createdAt: date, author: text })),
  audit: list(shape({ id: text, actor: text, action: text, objectType: text, objectId: text, timestamp: date, summary: text, before: unknownValue, after: unknownValue })),
  settings: shape({ centerName: text, address: text, phone: text, opens: text, closes: text, responseMinutes: numeric, advanceMode: oneOf(['percent', 'fixed']), advanceValue: money, plumberCommission: money, shopCommission: money, language: text, notifications: boolean }),
};

export function parseDatabase(value: unknown): Database {
  if (!isRecord(value)) return invalid('database');
  for (const key of Object.keys(databaseChecks) as (keyof Database)[]) {
    databaseChecks[key](value[key], key);
    if (key !== 'settings') {
      const records = value[key] as { id: string }[];
      if (new Set(records.map(item => item.id)).size !== records.length) invalid(`${key}.id (takroriy)`);
    }
  }
  return value as unknown as Database;
}
