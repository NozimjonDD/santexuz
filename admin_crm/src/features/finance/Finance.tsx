import { useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { Banknote, Coins, Download, HandCoins, Plus, Receipt, ShieldAlert, Wallet } from 'lucide-react';
import { useStore } from '../../app/store';
import { cashOutstanding, financials } from '../../domain/rules';
import { paymentLabels, type PaymentKind } from '../../domain/types';
import { dateTime, exportCsv, inDateRange, includesQuery } from '../../shared/format';
import { Badge, DataTable, DateRange, Money, Notice, PageHeader, Panel, SearchInput, StatCard, Tabs } from '../../shared/ui';
import { PaymentDialog } from './PaymentDialog';
import { PaymentTable } from './PaymentTable';

const tabs = [{ value: 'orders', label: 'Buyurtmalar bo‘yicha' }, { value: 'payments', label: 'Mijoz to‘lovlari' }, { value: 'cash', label: 'Naqd topshirishlar' }, { value: 'partners', label: 'Hamkor hisob-kitobi' }, { value: 'debts', label: 'Qarzdorlik' }];
export default function Finance() {
  const { db, notify } = useStore();
  const [params, setParams] = useSearchParams();
  const tab = params.get('tab') ?? 'orders';
  const [range, setRange] = useState({ from: '', to: '' });
  const [query, setQuery] = useState('');
  const [paymentType, setPaymentType] = useState<PaymentKind | null>(null);
  const payments = db.payments.filter(p => inDateRange(p.timestamp, range.from, range.to) && includesQuery(`${p.orderId} ${p.receivedBy} ${paymentLabels[p.type]}`, query));
  const confirmed = payments.filter(p => p.status === 'confirmed');
  const sum = (...types: PaymentKind[]) => confirmed.filter(p => types.includes(p.type)).reduce((s, p) => s + p.amount, 0);
  const orders = db.orders.filter(o => inDateRange(o.createdAt, range.from, range.to) && includesQuery(`${o.id} ${db.customers.find(c => c.id === o.customerId)?.name}`, query));
  const values = orders.map(o => ({ ...o, f: financials(o, db.payments), cash: cashOutstanding(o.id, db.payments) }));
  const due = values.reduce((s, o) => s + (o.f.shopDue ?? 0) + (o.f.plumberDue ?? 0), 0);
  const balance = values.reduce((s, o) => s + (o.f.balance ?? 0), 0);
  const commission = values.filter(o => o.status === 'completed').reduce((s, o) => s + (o.f.commission ?? 0), 0);
  const cash = values.reduce((s, o) => s + o.cash, 0);
  const filteredPayments = payments.filter(p => tab === 'payments' ? ['advance', 'balance', 'refund'].includes(p.type) : tab === 'cash' ? p.type === 'cash_handover' : p.type.endsWith('_settlement'));
  return <><PageHeader eyebrow="KATALOG VA MOLIYA" title="Moliya" description="Tushum, komissiyalar va hamkorlar bilan shaffof hisob-kitob." actions={<><button className="button secondary" onClick={() => {
    if (['orders', 'debts'].includes(tab)) exportCsv('moliya-buyurtmalar', ['Buyurtma', 'Jami UZS', 'Qabul qilingan UZS', 'Qoldiq UZS', 'Komissiya UZS', 'Santexnikka UZS', 'Do‘konga UZS', 'Nizo'], values.filter(v => tab !== 'debts' || (v.f.balance ?? 0) > 0 || (v.f.shopDue ?? 0) > 0 || (v.f.plumberDue ?? 0) > 0).map(v => [v.id, v.f.total, v.f.paid, v.f.balance, v.f.commission, v.f.plumberDue, v.f.shopDue, v.dispute.open ? 'Bloklangan' : 'Yo‘q']));
    else exportCsv('moliya-yozuvlar', ['ID', 'Buyurtma', 'Tur', 'Summa UZS', 'Status', 'Sana'], filteredPayments.map(p => [p.id, p.orderId, paymentLabels[p.type], p.amount, p.status, dateTime(p.timestamp)]));
    notify('Joriy bo‘limning filtrlangan demo ma’lumotlari eksport qilindi.', 'info');
  }}><Download size={16} />CSV eksport</button><button className="button primary" onClick={() => setPaymentType(tab === 'cash' ? 'cash_handover' : tab === 'partners' ? 'shop_settlement' : 'advance')}><Plus size={17} />{tab === 'cash' ? 'Pulni qabul qilish' : tab === 'partners' ? 'Hisob-kitob qayd etish' : 'To‘lov qayd etish'}</button></>} />
  <div className="stats-grid finance-stats"><StatCard label="Davr tushumi" value={<Money value={sum('advance', 'balance') - sum('refund')} />} detail="Qaytarishlar ayirilgan" icon={<Wallet size={19} />} /><StatCard label="Mijozlardan avans" value={<Money value={sum('advance')} />} detail="Tasdiqlangan demo yozuvlar" icon={<Banknote size={19} />} /><StatCard label="Mijozlar qoldig‘i" value={<Money value={balance} />} detail="Buyurtma yaratilgan davr" icon={<Receipt size={19} />} /><StatCard label="Hamkorlarga qoldiq" value={<Money value={due} />} detail="Nizodagi summa ham kiritilgan" icon={<HandCoins size={19} />} /><StatCard label="Hamkorlarga to‘langan" value={<Money value={sum('shop_settlement', 'plumber_settlement')} />} detail="Faqat xodim tasdiqlagan" icon={<Coins size={19} />} /><StatCard label="Platforma komissiyasi" value={<Money value={commission} />} detail="Yakunlangan buyurtmalar" icon={<Wallet size={19} />} /><StatCard label="Topshirilmagan naqd" value={<Money value={cash} />} detail="Santexnikdan olinishi kerak" icon={<ShieldAlert size={19} />} /></div>
  <Notice>Haqiqiy tranzaksiya bajarilmaydi. Barcha summalar namuna. Qoldiq va hamkor hisob-kitobi ochiq nizoda bloklanadi. Ichki kvitansiya fiskal chek emas.</Notice><Panel><Tabs items={tabs} value={tab} onChange={value => setParams({ tab: value })} /><div className="filter-bar"><SearchInput value={query} onChange={setQuery} placeholder="Buyurtma yoki tomon nomi…" /><DateRange {...range} onChange={(from, to) => setRange({ from, to })} /></div>{['orders', 'debts'].includes(tab) ? <DataTable rows={values.filter(v => tab !== 'debts' || (v.f.balance ?? 0) > 0 || (v.f.shopDue ?? 0) > 0 || (v.f.plumberDue ?? 0) > 0)} columns={[
    { key: 'order', label: 'Buyurtma / mijoz', sortValue: o => o.id, render: o => <div className="cell-stack"><Link className="text-link" to={`/orders/${o.id}`}>{o.id}</Link><small>{db.customers.find(c => c.id === o.customerId)?.name}</small></div> },
    { key: 'total', label: 'Jami', sortValue: o => o.f.total ?? -1, className: 'numeric', render: o => <Money value={o.f.total} /> },
    { key: 'paid', label: 'Qabul qilingan', sortValue: o => o.f.paid, className: 'numeric', render: o => <Money value={o.f.paid} /> },
    { key: 'balance', label: 'Mijoz qoldig‘i', sortValue: o => o.f.balance ?? -1, className: 'numeric', render: o => <Money value={o.f.balance} /> },
    { key: 'commission', label: 'Komissiya', sortValue: o => o.f.commission ?? -1, className: 'numeric', render: o => <Money value={o.f.commission} /> },
    { key: 'partners', label: 'Santexnik / do‘kon qoldig‘i', render: o => <div className="cell-stack"><Money value={o.f.plumberDue} /><Money value={o.f.shopDue} /></div> },
    { key: 'status', label: 'Hisob holati', render: o => <Badge tone={o.dispute.open ? 'danger' : o.f.balance === 0 ? 'success' : 'warning'}>{o.dispute.open ? 'Nizo · bloklangan' : o.f.balance === 0 ? 'Mijoz to‘lagan' : 'Qoldiq mavjud'}</Badge> },
  ]} /> : <PaymentTable rows={filteredPayments} />}</Panel>{tab === 'cash' && <Panel title="Santexnikdan topshirilishi kutilayotgan naqd"><DataTable rows={values.filter(v => v.cash > 0)} columns={[{ key: 'id', label: 'Buyurtma', render: v => <Link to={`/orders/${v.id}`}>{v.id}</Link> }, { key: 'plumber', label: 'Santexnik', render: v => db.plumbers.find(p => p.id === v.plumberId)?.name }, { key: 'cash', label: 'Naqd qoldiq', sortValue: v => v.cash, render: v => <Money value={v.cash} /> }]} /></Panel>}{paymentType && <PaymentDialog initialType={paymentType} onClose={() => setPaymentType(null)} />}</>;
}
