import { useMemo, useState } from 'react';
import { Link } from 'react-router';
import { ArrowLeft, Pencil } from 'lucide-react';
import type { Database, EntityCollection, Order, PaymentKind } from '../../domain/types';
import { Badge, EmptyState, KeyValue, Notice, PageHeader, Panel, Tabs } from '../../shared/ui';
import { OrderTable } from '../orders/OrderTable';
import { PaymentTable } from '../finance/PaymentTable';
import { AuditTable } from '../management/Audit';
import { directoryConfig } from './config';
import { fieldText, isCatalog, pathFor, type DirectoryField, type DirectoryRow } from './model';

const profileTabs = ['Profil', 'Buyurtmalar', 'Reytinglar', 'Hisob-kitob', 'Audit'].map(value => ({ value, label: value }));
const catalogTabs = profileTabs.filter(tab => tab.value === 'Profil' || tab.value === 'Audit');
const paymentTypes: Partial<Record<EntityCollection, readonly PaymentKind[]>> = {
  customers: ['advance', 'balance', 'refund'],
  plumbers: ['plumber_settlement', 'cash_handover'],
  shops: ['shop_settlement'],
};

function profileValue(row: DirectoryRow, field: DirectoryField) {
  const value = row[field.name];
  if (field.type === 'checkbox') return value ? 'Ha (demo)' : 'Yo‘q';
  if (field.type === 'number' && value == null) return 'Sozlanmagan';
  return Array.isArray(value) ? value.join(', ') : fieldText(row, field.name) || 'Belgilanmagan';
}

interface DirectoryProfileProps {
  kind: EntityCollection;
  row: DirectoryRow;
  orders: Order[];
  db: Database;
  onEdit: (row: DirectoryRow) => void;
}

export function DirectoryProfile({ kind, row, orders, db, onEdit }: DirectoryProfileProps) {
  const config = directoryConfig[kind];
  const [tab, setTab] = useState('Profil');
  const { reviews, payments, audit } = useMemo(() => {
    const orderIds = new Set(orders.map(order => order.id));
    const allowedPaymentTypes = paymentTypes[kind] ?? [];
    const catalog = isCatalog(kind);
    return {
      reviews: catalog ? [] : db.reviews.filter(review => review.targetId === row.id || (kind === 'customers' && review.customerId === row.id)),
      payments: catalog ? [] : db.payments.filter(payment => orderIds.has(payment.orderId) && allowedPaymentTypes.includes(payment.type)),
      audit: db.audit.filter(event => event.objectId === row.id || orderIds.has(event.objectId)),
    };
  }, [row.id, kind, orders, db.reviews, db.payments, db.audit]);

  return <>
    <Link className="back-link" to={pathFor(kind)}><ArrowLeft size={16} aria-hidden="true" />{config.title}</Link>
    <PageHeader
      eyebrow={`${config.title.toLocaleUpperCase('uz')} / DEMO PROFIL`}
      title={row.name}
      description={row.description || row.notes || config.description}
      actions={<button className="button primary" onClick={() => onEdit(row)}><Pencil size={16} aria-hidden="true" />Tahrirlash</button>}
    />
    <Tabs items={isCatalog(kind) ? catalogTabs : profileTabs} value={tab} onChange={setTab} />
    {tab === 'Profil' && <Panel title="Profil ma’lumotlari">
      <div className="panel-padding">
        <dl className="detail-grid">{config.fields.map(field => <KeyValue key={field.name} label={field.label}>{profileValue(row, field)}</KeyValue>)}</dl>
        {kind === 'shops' && <Notice>Bu do‘konga bitta umumiy Telegram akkaunti biriktiriladi. Alohida do‘kon xodimi aniqlanmaydi.</Notice>}
        {kind === 'customers' && <Notice>Telefon va manzil faqat ruxsatli admin kontekstida. Ma’lumotlar sun’iy.</Notice>}
      </div>
    </Panel>}
    {tab === 'Buyurtmalar' && <Panel title="Faol va yakunlangan buyurtmalar"><OrderTable rows={orders} /></Panel>}
    {tab === 'Reytinglar' && <Panel title="Reytinglar">
      <div className="panel-padding">
        {reviews.map(review => <div className="review-card" key={review.id}>
          <span className="rating" aria-label={`${review.score} yulduz`}>{'★'.repeat(review.score)}</span>
          <p>{review.comment}</p>
          <Badge>{review.status === 'published' ? 'Ko‘rsatilgan' : review.status === 'pending' ? 'Kutilmoqda' : 'Yashirilgan'}</Badge>
        </div>)}
        {!reviews.length && <EmptyState title="Baho yo‘q" text="Faqat moderatsiyadan o‘tgan baholar umumiy reytingda hisoblanadi." />}
      </div>
    </Panel>}
    {tab === 'Hisob-kitob' && <Panel title="To‘lov va hisob-kitob tarixi"><PaymentTable rows={payments} /></Panel>}
    {tab === 'Audit' && <Panel title="Audit tarixi"><AuditTable rows={audit} /></Panel>}
  </>;
}
