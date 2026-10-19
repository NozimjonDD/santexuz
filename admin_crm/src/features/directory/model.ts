import { isClosed } from '../../domain/rules';
import type { Customer, Database, EntityCollection, Material, Order, Payment, Plumber, Review, Service, Shop } from '../../domain/types';
import { now } from '../../shared/format';
import type { FieldSpec, FormValues } from '../../shared/ui';

type DirectoryFields = Customer & Plumber & Shop & Service & Material;
export type DirectoryFieldName = keyof DirectoryFields;
export type DirectoryField = Omit<FieldSpec, 'name'> & { name: DirectoryFieldName };
export type DirectoryRow = Pick<DirectoryFields, 'id' | 'name'> & Partial<DirectoryFields>;
export type DirectoryChange = {
  [Kind in EntityCollection]: { kind: Kind; entity: Database[Kind][number] }
}[EntityCollection];

export interface OrderSummary {
  orders: Order[];
  lastOrderAt: string;
  paid: number;
  active: number;
  accepted: number;
  rejected: number;
}

export const emptyOrderSummary: OrderSummary = {
  orders: [], lastOrderAt: '', paid: 0, active: 0, accepted: 0, rejected: 0,
};

export const isPartner = (kind: EntityCollection) => kind === 'plumbers' || kind === 'shops';
export const isCatalog = (kind: EntityCollection) => kind === 'services' || kind === 'materials';
export const pathFor = (kind: EntityCollection) => isCatalog(kind) ? `/catalog/${kind}` : `/${kind}`;
export const fieldText = (row: DirectoryRow, field: DirectoryFieldName) => String(row[field] ?? '');

// Build once per data change; table cells and sorting use constant-time lookups.
export function indexDirectoryOrders(kind: EntityCollection, orders: Order[], payments: Payment[]) {
  const summaries = new Map<string, OrderSummary>();
  if (isCatalog(kind)) return summaries;

  const paidByOrder = new Map<string, number>();
  for (const payment of payments) {
    if (payment.status !== 'confirmed') continue;
    const amount = payment.type === 'advance' || payment.type === 'balance'
      ? payment.amount : payment.type === 'refund' ? -payment.amount : 0;
    paidByOrder.set(payment.orderId, (paidByOrder.get(payment.orderId) ?? 0) + amount);
  }

  for (const order of orders) {
    const entityId = kind === 'customers' ? order.customerId : kind === 'plumbers' ? order.plumberId : order.shopId;
    if (!entityId) continue;
    let summary = summaries.get(entityId);
    if (!summary) {
      summary = { ...emptyOrderSummary, orders: [] };
      summaries.set(entityId, summary);
    }
    summary.orders.push(order);
    summary.paid += paidByOrder.get(order.id) ?? 0;
    if (!isClosed(order.status)) summary.active += 1;
    if (order.status === 'rejected') summary.rejected += 1;
    else summary.accepted += 1;
    if (order.createdAt.localeCompare(summary.lastOrderAt) > 0) summary.lastOrderAt = order.createdAt;
  }
  return summaries;
}

export function indexDirectoryRatings(reviews: Review[]) {
  const totals = new Map<string, { score: number; count: number }>();
  for (const review of reviews) {
    if (review.status !== 'published') continue;
    const total = totals.get(review.targetId) ?? { score: 0, count: 0 };
    total.score += review.score;
    total.count += 1;
    totals.set(review.targetId, total);
  }
  const ratings = new Map<string, string>();
  for (const [targetId, total] of totals) ratings.set(targetId, (total.score / total.count).toFixed(1));
  return ratings;
}

export function directoryFormValues(row: DirectoryRow, fields: DirectoryField[]): FormValues {
  const values: FormValues = {};
  for (const field of fields) {
    const value = row[field.name];
    values[field.name] = value == null ? '' : typeof value === 'number' ? String(value) : value;
  }
  return values;
}

// Explicit entity shapes keep form strings and optional fields out of the database.
export function normalizeDirectoryChange(kind: EntityCollection, values: FormValues, previous: DirectoryRow | null, entityId: string): DirectoryChange {
  const text = (field: DirectoryFieldName) => String(values[field] ?? '');
  const numeric = (field: DirectoryFieldName) => text(field).trim() ? Number(values[field]) : null;
  const base = { id: entityId, name: text('name').trim() };

  switch (kind) {
    case 'customers':
      return { kind, entity: {
        ...base, phone: text('phone'), telegramId: text('telegramId'), notes: text('notes'),
        consent: values.consent === true, createdAt: previous?.createdAt ?? now(),
      } };
    case 'plumbers':
      return { kind, entity: {
        ...base, phone: text('phone'), telegramId: text('telegramId'), district: text('district'),
        categories: Array.isArray(values.categories) ? [...values.categories] : [],
        experience: numeric('experience') ?? 0, photo: text('photo'), notes: text('notes'),
        commission: numeric('commission'), isActive: values.isActive === true,
      } };
    case 'shops':
      return { kind, entity: {
        ...base, contactName: text('contactName'), address: text('address'), district: text('district'),
        phone: text('phone'), telegramId: text('telegramId'), description: text('description'),
        commission: numeric('commission'), isActive: values.isActive === true,
      } };
    case 'services':
      return { kind, entity: {
        ...base, nameRu: text('nameRu'), nameEn: text('nameEn'), category: text('category'), unit: text('unit'),
        areaRate: numeric('areaRate'), emergencyFee: numeric('emergencyFee'), warranty: text('warranty'),
        description: text('description'), isActive: values.isActive === true, visible: values.visible === true,
      } };
    case 'materials':
      return { kind, entity: {
        ...base, category: text('category'), brand: text('brand'), size: text('size'), unit: text('unit'),
        description: text('description'), isActive: values.isActive === true,
      } };
  }
}

function upsert<Entity extends { id: string }>(entities: Entity[], entity: Entity): Entity[] {
  return entities.some(item => item.id === entity.id)
    ? entities.map(item => item.id === entity.id ? entity : item)
    : [entity, ...entities];
}

export function applyDirectoryChange(db: Database, change: DirectoryChange) {
  switch (change.kind) {
    case 'customers': db.customers = upsert(db.customers, change.entity); break;
    case 'plumbers': db.plumbers = upsert(db.plumbers, change.entity); break;
    case 'shops': db.shops = upsert(db.shops, change.entity); break;
    case 'services': db.services = upsert(db.services, change.entity); break;
    case 'materials': db.materials = upsert(db.materials, change.entity); break;
  }
}

export function setDirectoryActive(db: Database, kind: EntityCollection, entityId: string, isActive: boolean) {
  const update = <Entity extends { id: string; isActive: boolean }>(items: Entity[]) =>
    items.map(item => item.id === entityId ? { ...item, isActive } : item);
  switch (kind) {
    case 'plumbers': db.plumbers = update(db.plumbers); break;
    case 'shops': db.shops = update(db.shops); break;
    case 'services': db.services = update(db.services); break;
    case 'materials': db.materials = update(db.materials); break;
    case 'customers': break;
  }
}
