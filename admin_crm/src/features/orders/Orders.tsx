import { useDeferredValue, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router';
import { Download, Plus, SlidersHorizontal, X } from 'lucide-react';
import { useStore } from '../../app/store';
import { categories, statusLabels, type Order } from '../../domain/types';
import { estimateTotal, financials } from '../../domain/rules';
import { matchesOrderTab } from '../../domain/orderQueries';
import { dateTime, exportCsv, id, inDateRange, includesQuery, now } from '../../shared/format';
import { Badge, DateRange, Modal, Notice, PageHeader, Panel, RecordForm, SearchInput, SelectFilter, Tabs, type FieldSpec } from '../../shared/ui';
import { OrderTable } from './OrderTable';

const baseTabOptions = [{ value: 'all', label: 'Barchasi' }, { value: 'new', label: 'Yangi so‘rovlar' }, { value: 'unassigned', label: 'Tayinlash kerak' }, { value: 'active', label: 'Faol' }, { value: 'dispute', label: 'Nizo' }, { value: 'completed', label: 'Yakunlangan' }, { value: 'cancelled', label: 'Bekor qilingan' }];
const additionalTabLabels = new Map([
  ['waiting', 'Kutilmoqda'], ['progress', 'Jarayonda'],
  ['estimate', 'Smeta / do‘kon javobi'], ['attention', 'Nizo / bekor / rad'],
]);
export const matchesTab = matchesOrderTab;
export default function Orders() {
  const { db, mutate, notify } = useStore();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);
  const [more, setMore] = useState(false);
  const [status, setStatus] = useState('');
  const [category, setCategory] = useState('');
  const [plumber, setPlumber] = useState('');
  const [shop, setShop] = useState('');
  const [urgency, setUrgency] = useState('');
  const [payment, setPayment] = useState('');
  const requestedTab = params.get('tab') ?? 'all';
  const tab = baseTabOptions.some(option => option.value === requestedTab) || additionalTabLabels.has(requestedTab) ? requestedTab : 'all';
  const tabOptions = useMemo(() => {
    const label = additionalTabLabels.get(tab);
    return label ? [...baseTabOptions, { value: tab, label }] : baseTabOptions;
  }, [tab]);
  const from = params.get('from') ?? '';
  const to = params.get('to') ?? '';
  const lookup = useMemo(() => ({
    customers: new Map(db.customers.map(customer => [customer.id, customer])),
    plumbers: new Map(db.plumbers.map(plumber => [plumber.id, plumber])),
    shops: new Map(db.shops.map(shop => [shop.id, shop])),
  }), [db.customers, db.plumbers, db.shops]);
  const rows = useMemo(() => db.orders.filter(o => {
    const c = lookup.customers.get(o.customerId);
    const p = o.plumberId ? lookup.plumbers.get(o.plumberId) : undefined;
    const s = o.shopId ? lookup.shops.get(o.shopId) : undefined;
    const balance = payment ? financials(o, db.payments).balance : null;
    return matchesTab(o, tab) && includesQuery(`${o.id} ${c?.name ?? ''} ${c?.phone ?? ''} ${p?.name ?? ''} ${s?.name ?? ''} ${o.service}`, deferredQuery)
      && (!status || o.status === status) && (!category || o.category === category) && (!plumber || o.plumberId === plumber)
      && (!shop || o.shopId === shop) && (!urgency || o.urgent === (urgency === 'yes'))
      && (!payment || (payment === 'paid' ? balance === 0 : balance !== null && balance > 0)) && inDateRange(o.createdAt, from, to);
  }), [db.orders, db.payments, lookup, tab, deferredQuery, status, category, plumber, shop, urgency, payment, from, to]);
  const setParam = (name: string, value: string) => setParams(p => { value ? p.set(name, value) : p.delete(name); return p; });
  const closeNew = () => setParam('new', '');
  const fields: FieldSpec[] = [
    { name: 'customerId', label: 'Namuna mijoz', type: 'select', required: true, options: db.customers.map(c => ({ value: c.id, label: `${c.name} · ${c.phone}` })) },
    { name: 'serviceId', label: 'Xizmat', type: 'select', required: true, options: db.services.filter(s => s.isActive).map(s => ({ value: s.id, label: s.name })) },
    { name: 'address', label: 'Manzil', required: true, full: true }, { name: 'description', label: 'Muammo izohi', type: 'textarea' },
    { name: 'urgent', label: 'Shoshilinch so‘rov', type: 'checkbox', hint: 'Ish vaqti sozlanmaguncha shoshilinch belgi tasdiqlanmaydi.' },
    { name: 'consent', label: 'Demo telefon, manzil va media buyurtma ishtirokchilariga ko‘rsatilishiga rozilik qayd etildi', type: 'checkbox', required: true, full: true },
  ];
  return <><PageHeader eyebrow="ISH JARAYONI" title="Buyurtmalar" description="So‘rovdan yakuniy hisob-kitobgacha barcha buyurtmalar." actions={<><button className="button secondary" onClick={() => { exportCsv('buyurtmalar', ['Buyurtma', 'Mijoz', 'Xizmat', 'Holat', 'Jami UZS', 'Yaratilgan vaqt'], rows.map(o => [o.id, db.customers.find(c => c.id === o.customerId)?.name, o.service, statusLabels[o.status], estimateTotal(o.confirmedEstimate ?? o.estimate), dateTime(o.createdAt)])); notify('Filtrlangan demo buyurtmalar CSV fayliga chiqarildi.', 'info'); }}><Download size={16} />CSV eksport</button><button className="button primary" onClick={() => setParam('new', '1')}><Plus size={18} />Yangi so‘rov</button></>} />
    <Panel><div className="list-topline"><Tabs items={tabOptions.map(t => ({ ...t, count: db.orders.filter(o => matchesTab(o, t.value)).length }))} value={tab} onChange={v => setParam('tab', v)} />{!tabOptions.some(t => t.value === tab) && <Badge tone="blue">Qo‘shimcha filtr: {tab}</Badge>}</div><div className="filter-bar"><SearchInput value={query} onChange={setQuery} placeholder="Buyurtma, mijoz, telefon yoki hamkor…" /><SelectFilter label="Status" value={status} options={Object.entries(statusLabels).map(([value, label]) => ({ value, label }))} onChange={setStatus} /><button className={`button secondary ${more ? 'selected' : ''}`} aria-expanded={more} onClick={() => setMore(!more)}><SlidersHorizontal size={16} />Filtrlar</button><button className="icon-button" aria-label="Barcha filtrlarni tozalash" onClick={() => { setQuery(''); setStatus(''); setCategory(''); setPlumber(''); setShop(''); setUrgency(''); setPayment(''); setParams({}); }}><X size={17} /></button></div>{more && <div className="expanded-filters"><SelectFilter label="Xizmat guruhi" value={category} options={categories.map(c => ({ value: c, label: c }))} onChange={setCategory} /><SelectFilter label="Santexnik" value={plumber} options={db.plumbers.map(p => ({ value: p.id, label: p.name }))} onChange={setPlumber} /><SelectFilter label="Do‘kon" value={shop} options={db.shops.map(s => ({ value: s.id, label: s.name }))} onChange={setShop} /><SelectFilter label="Shoshilinch" value={urgency} options={[{ value: 'yes', label: 'Shoshilinch' }, { value: 'no', label: 'Oddiy' }]} onChange={setUrgency} /><SelectFilter label="To‘lov" value={payment} options={[{ value: 'paid', label: 'To‘langan' }, { value: 'due', label: 'Qoldiq bor' }]} onChange={setPayment} /></div>}<div className="list-date-row"><span className="muted small">{rows.length} ta demo buyurtma</span><DateRange from={from} to={to} onChange={(f, t) => setParams(p => { f ? p.set('from', f) : p.delete('from'); t ? p.set('to', t) : p.delete('to'); return p; })} /></div><OrderTable rows={rows} /></Panel>
    {params.get('new') === '1' && <Modal title="Yangi demo so‘rov" description="Haqiqiy buyurtma yoki Telegram xabari yaratilmaydi." onClose={closeNew} wide><Notice>Faqat sun’iy ma’lumot kiriting. Yangi so‘rov raqami DEMO bilan boshlanadi.</Notice><RecordForm fields={fields} onCancel={closeNew} onSubmit={values => {
      const service = db.services.find(s => s.id === values.serviceId)!;
      const orderId = id('DEMO');
      const timestamp = now();
      const newOrder: Order = {
        id: orderId, createdAt: timestamp, customerId: String(values.customerId), plumberId: null, shopId: null,
        category: service.category, service: service.name, address: String(values.address).trim(), coordinates: '', description: String(values.description ?? ''),
        status: 'new', urgent: values.urgent === true, urgencyApproved: false, consent: true, assignedAt: null, inspectionAt: '', workStart: '', workEnd: '', etaReason: '', preparationMinutes: null,
        estimate: { version: 1, services: [{ id: id('LINE'), name: service.name, quantity: 1, unit: service.unit, price: service.areaRate }], materials: [], deliveryFee: null, emergencyFee: values.urgent ? service.emergencyFee : 0, approved: false, createdAt: timestamp },
        confirmedEstimate: null, estimateHistory: [], advance: { mode: db.settings.advanceMode, value: db.settings.advanceValue },
        commissions: { plumber: db.settings.plumberCommission, shop: db.settings.shopCommission },
        contract: { templateId: '', version: 0, language: 'UZ', text: '', signatures: [false, false, false, false], signedAt: null, signedBy: null },
        deliveries: [], timeline: [{ id: id('T'), at: timestamp, title: 'So‘rov yaratildi', detail: 'CRM orqali demo so‘rov' }], notes: [],
        dispute: { open: false, reason: '', resolution: '', previousStatus: null }, materialReceived: false, customerCompleted: false,
        preparationStarted: false, workStarted: false, cancelReason: '', refundDecision: null,
      };
      mutate({ action: 'Yaratish', objectType: 'Buyurtma', objectId: orderId, summary: 'CRM orqali demo so‘rov yaratildi', after: { status: 'new' } }, draft => { draft.orders.unshift(newOrder); });
      navigate(`/orders/${orderId}`);
    }} submitLabel="Demo so‘rov yaratish" /></Modal>}
  </>;
}
