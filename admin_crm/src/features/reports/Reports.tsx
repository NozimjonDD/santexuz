import { useState } from 'react';
import { Download, FileSpreadsheet, FileText } from 'lucide-react';
import { useStore } from '../../app/store';
import { estimateTotal, financials } from '../../domain/rules';
import { categories, paymentLabels, statusLabels } from '../../domain/types';
import { dateTime, exportCsv, inDateRange, includesQuery } from '../../shared/format';
import { Badge, DataTable, DateRange, Money, Notice, PageHeader, Panel, SearchInput, SelectFilter, StatCard, type Column } from '../../shared/ui';

type Cell = string | number | null;
interface ReportRow { id: string; [key: string]: Cell }
interface ReportColumn { key: string; label: string; money?: boolean }
const reportTypes = [
  { value: 'orders', label: 'Buyurtmalar va konversiya' }, { value: 'lines', label: 'Material va xizmat summalari' },
  { value: 'payments', label: 'To‘lovlar, avans va qoldiq' }, { value: 'commissions', label: 'Hamkor komissiyalari' },
  { value: 'partners', label: 'Hamkorlarga to‘langan / qoldiq' }, { value: 'ratings', label: 'Hamkor reytinglari' },
];
export default function Reports() {
  const { db, notify, isMock } = useStore();
  const [type, setType] = useState('orders');
  const [status, setStatus] = useState('');
  const [plumber, setPlumber] = useState('');
  const [shop, setShop] = useState('');
  const [category, setCategory] = useState('');
  const [query, setQuery] = useState('');
  const [range, setRange] = useState({ from: '', to: '' });
  const orders = db.orders.filter(o => (!status || o.status === status) && (!plumber || o.plumberId === plumber) && (!shop || o.shopId === shop) && (!category || o.category === category) && inDateRange(o.createdAt, range.from, range.to));
  const orderIds = new Set(orders.map(o => o.id));
  let definitions: ReportColumn[];
  let report: ReportRow[];
  if (type === 'payments') {
    definitions = [{ key: 'order', label: 'Buyurtma' }, { key: 'type', label: 'To‘lov turi' }, { key: 'amount', label: 'Summa (UZS)', money: true }, { key: 'status', label: 'Holat' }, { key: 'date', label: 'Sana' }, { key: 'party', label: 'Tomon' }];
    report = db.payments.filter(p => orderIds.has(p.orderId) && inDateRange(p.timestamp, range.from, range.to)).map(p => ({ id: p.id, order: p.orderId, type: paymentLabels[p.type], amount: p.amount, status: p.status === 'confirmed' ? 'Tasdiqlangan' : 'Kutilmoqda', date: dateTime(p.timestamp), party: p.receivedBy }));
  } else if (type === 'ratings') {
    definitions = [{ key: 'name', label: 'Hamkor' }, { key: 'role', label: 'Rol' }, { key: 'rating', label: 'Tasdiqlangan reyting' }, { key: 'count', label: 'Baho soni' }];
    report = [...db.plumbers, ...db.shops].filter(p => (!plumber || p.id === plumber || p.id.startsWith('SH-')) && (!shop || p.id === shop || p.id.startsWith('P-'))).map(p => {
      const reviews = db.reviews.filter(r => r.targetId === p.id && r.status === 'published' && orderIds.has(r.orderId) && inDateRange(r.createdAt, range.from, range.to));
      return { id: p.id, name: p.name, role: 'categories' in p ? 'Santexnik' : 'Do‘kon', rating: reviews.length ? (reviews.reduce((s, r) => s + r.score, 0) / reviews.length).toFixed(1) : 'Baho yo‘q', count: reviews.length };
    });
  } else if (type === 'lines') {
    definitions = [{ key: 'order', label: 'Buyurtma' }, { key: 'name', label: 'Xizmat / material' }, { key: 'type', label: 'Tur' }, { key: 'quantity', label: 'Miqdor' }, { key: 'price', label: 'Birlik narxi (UZS)', money: true }, { key: 'total', label: 'Jami (UZS)', money: true }];
    report = orders.flatMap(o => {
      const estimate = o.confirmedEstimate ?? o.estimate;
      return [...estimate.services.map(l => ({ ...l, kind: 'Xizmat' })), ...estimate.materials.map(l => ({ ...l, kind: 'Material' }))].map(l => ({ id: `${o.id}-${l.id}`, order: o.id, name: l.name, type: l.kind, quantity: `${l.quantity} ${l.unit}`, price: l.price, total: l.price === null ? null : Math.round(l.quantity * l.price) }));
    });
  } else if (type === 'commissions') {
    definitions = [{ key: 'id', label: 'Buyurtma' }, { key: 'plumberRate', label: 'Usta stavkasi (%)' }, { key: 'plumberFee', label: 'Usta komissiyasi', money: true }, { key: 'shopRate', label: 'Do‘kon stavkasi (%)' }, { key: 'shopFee', label: 'Do‘kon komissiyasi', money: true }, { key: 'total', label: 'Jami komissiya', money: true }];
    report = orders.map(o => { const f = financials(o, db.payments); return { id: o.id, plumberRate: o.commissions.plumber, plumberFee: f.plumberFee, shopRate: o.commissions.shop, shopFee: f.shopFee, total: f.commission }; });
  } else if (type === 'partners') {
    definitions = [{ key: 'order', label: 'Buyurtma' }, { key: 'partner', label: 'Hamkor' }, { key: 'net', label: 'Sof summa', money: true }, { key: 'paid', label: 'To‘langan', money: true }, { key: 'due', label: 'Qoldiq', money: true }, { key: 'status', label: 'Holat' }];
    report = orders.flatMap(o => {
      const f = financials(o, db.payments);
      return [
        ...(o.plumberId ? [{ id: `${o.id}-P`, order: o.id, partner: db.plumbers.find(p => p.id === o.plumberId)?.name ?? '—', net: f.plumberNet, due: f.plumberDue, paid: f.plumberNet === null || f.plumberDue === null ? null : f.plumberNet - f.plumberDue, status: o.dispute.open ? 'Nizo · bloklangan' : o.status === 'completed' ? 'Hisob-kitob mumkin' : 'Yakunlanish kutilmoqda' }] : []),
        ...(o.shopId ? [{ id: `${o.id}-S`, order: o.id, partner: db.shops.find(s => s.id === o.shopId)?.name ?? '—', net: f.shopNet, due: f.shopDue, paid: f.shopNet === null || f.shopDue === null ? null : f.shopNet - f.shopDue, status: o.dispute.open ? 'Nizo · bloklangan' : o.status === 'completed' ? 'Hisob-kitob mumkin' : 'Yakunlanish kutilmoqda' }] : []),
      ];
    });
  } else {
    definitions = [{ key: 'id', label: 'Buyurtma' }, { key: 'customer', label: 'Mijoz' }, { key: 'service', label: 'Xizmat' }, { key: 'status', label: 'Status' }, { key: 'total', label: 'Jami', money: true }, { key: 'paid', label: 'To‘langan', money: true }, { key: 'balance', label: 'Qoldiq', money: true }];
    report = orders.map(o => { const f = financials(o, db.payments); return { id: o.id, customer: db.customers.find(c => c.id === o.customerId)?.name ?? '—', service: o.service, status: statusLabels[o.status], total: f.total, paid: f.paid, balance: f.balance }; });
  }
  const rows = report.filter(r => includesQuery(Object.values(r).join(' '), query));
  const columns: Column<ReportRow>[] = definitions.map(c => ({ key: c.key, label: c.label, className: c.money ? 'numeric' : '', sortValue: r => r[c.key] ?? -1, render: r => c.money ? <Money value={r[c.key] as number | null} /> : r[c.key] ?? 'Sozlanmagan' }));
  const complete = orders.filter(o => o.status === 'completed').length;
  const total = orders.reduce((s, o) => s + (estimateTotal(o.confirmedEstimate ?? o.estimate) ?? 0), 0);
  const title = reportTypes.find(r => r.value === type)?.label ?? '';
  return <><PageHeader eyebrow="KATALOG VA MOLIYA" title="Hisobotlar" description="Buyurtmalar, to‘lovlar va hamkorlar faoliyatini tahlil qiling." actions={<><button className="button secondary" onClick={() => notify('Excel eksporti demo: XLSX endpoint backend bosqichida ulanadi. CSV eksport hozir ishlaydi.', 'info')}><FileSpreadsheet size={16} />Excel eksport</button><button className="button primary" onClick={() => { exportCsv(`hisobot-${type}`, definitions.map(c => c.label), rows.map(r => definitions.map(c => r[c.key])), isMock); notify('Filtrlangan hisobot CSV fayliga chiqarildi.', 'info'); }}><Download size={16} />CSV eksport</button></>} /><Panel title="Hisobot parametrlari"><div className="report-filters"><label className="report-type"><span>Hisobot turi</span><select value={type} onChange={e => setType(e.target.value)}>{reportTypes.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}</select></label><DateRange {...range} onChange={(from, to) => setRange({ from, to })} /><SelectFilter label="Status" value={status} onChange={setStatus} options={Object.entries(statusLabels).map(([value, label]) => ({ value, label }))} /><SelectFilter label="Santexnik" value={plumber} onChange={setPlumber} options={db.plumbers.map(p => ({ value: p.id, label: p.name }))} /><SelectFilter label="Do‘kon" value={shop} onChange={setShop} options={db.shops.map(s => ({ value: s.id, label: s.name }))} /><SelectFilter label="Xizmat guruhi" value={category} onChange={setCategory} options={categories.map(c => ({ value: c, label: c }))} /></div></Panel><div className="stats-grid report-stats"><StatCard label="Tanlangan buyurtmalar" value={orders.length} detail="Hisobot filtrlariga mos" icon={<FileText size={19} />} /><StatCard label="Yakunlanish ulushi" value={`${orders.length ? Math.round(complete / orders.length * 100) : 0}%`} detail={`${complete} ta buyurtma yakunlangan`} icon={<FileText size={19} />} /><StatCard label="Smetalar jami" value={<Money value={total} />} detail="Sozlangan smeta summalari yig‘indisi" icon={<FileText size={19} />} /></div><Notice>{isMock ? 'Hisobot namuna ma’lumotlarga asoslangan.' : 'Hisobot yuklangan API ma’lumotlariga asoslangan.'} Sana filtri buyurtma yaratilgan vaqtiga, to‘lov va reytingda ularning sanasiga ham qo‘llanadi. Sozlanmagan summalar jamiga kiritilmaydi.</Notice><Panel title={title} action={<Badge tone="blue">{rows.length} ta yozuv · {isMock ? 'DEMO' : 'API'}</Badge>}><div className="filter-bar"><SearchInput value={query} onChange={setQuery} placeholder="Hisobot natijalaridan qidirish…" /></div><DataTable key={type} rows={rows} columns={columns} /></Panel></>;
}
