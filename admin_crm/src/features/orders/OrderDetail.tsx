import { useEffect, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router';
import { ArrowLeft, ArrowRight, MapPin, MessageSquarePlus, Store, Wrench, XCircle } from 'lucide-react';
import { useStore } from '../../app/store';
import { isClosed, nextStatuses, transitionError } from '../../domain/rules';
import { statusLabels, type Order } from '../../domain/types';
import { dateTime, now, id } from '../../shared/format';
import { Avatar, Badge, EmptyState, FilePreview, KeyValue, Notice, PageHeader, Panel, StatusBadge, Tabs } from '../../shared/ui';
import { useOrderActions, type OrderActions } from './useOrderActions';
import { EstimatePanel } from './EstimatePanel';
import { ContractPanel } from './ContractPanel';
import { ProcessPanel } from './ProcessPanel';
import { OrderFinance } from './OrderFinancePanel';
import { AuditTable } from '../management/Audit';

const tabs = ['Umumiy', 'Smeta va materiallar', 'Jarayon', 'Shartnoma', 'To‘lov va hisob-kitob', 'Nizo va baho', 'Audit'];
export default function OrderDetail() {
  const { id: orderId = '' } = useParams();
  const { db } = useStore();
  const actions = useOrderActions(orderId);
  const [tab, setTab] = useState(tabs[0]);
  const [params, setParams] = useSearchParams();
  const order = db.orders.find(o => o.id === orderId);
  useEffect(() => {
    if (!order) return;
    const request = params.get('action');
    if (request === 'plumber' || request === 'shop') assign(request);
    if (request === 'cancel') requestCancellation();
    if (params.get('section') === 'general') setTab('Umumiy');
    if (request || params.has('section')) setParams({}, { replace: true });
  }, [orderId, params]);
  if (!order) return <EmptyState title="Buyurtma topilmadi" text="Bu raqam joriy demo to‘plamida yo‘q." action={<Link to="/orders" className="button primary">Buyurtmalarga qaytish</Link>} />;
  const customer = db.customers.find(c => c.id === order.customerId);
  const next = nextStatuses[order.status];
  const nextError = next ? transitionError(order, next, db.payments) : null;
  const changeStatus = () => next && actions.setConfirm({ title: `Bosqich: ${statusLabels[next]}`, description: 'Jarayonning navbatdagi bosqichi lokal demo sifatida qayd etiladi. Mijoz yoki hamkor amali haqiqiy bajarilmaydi.', action: () => actions.update(`Bosqich o‘zgardi: ${statusLabels[next]}`, (current, draft) => {
    const error = transitionError(current, next, draft.payments); if (error) throw new Error(error);
    current.status = next;
    if (next === 'preparing') {
      current.preparationStarted = true;
      if (!current.deliveries.length) current.deliveries.push({ id: id('D'), label: 'Asosiy yetkazish', status: 'preparing', eta: new Date(Date.now() + 3600000).toISOString(), note: 'Namuna ETA. Xarita provayderi ulanmagan.' });
    }
    if (next === 'transit') current.deliveries.forEach(d => { if (d.status !== 'delivered') d.status = 'transit'; });
    if (next === 'delivered') current.deliveries.forEach(d => { d.status = 'delivered'; });
    if (next === 'working') current.workStarted = true;
  }) });
  const locked = isClosed(order.status) || order.dispute.open;
  function assign(kind: 'plumber' | 'shop') {
    const options = kind === 'plumber' ? db.plumbers.filter(p => p.isActive && p.district === 'Marhamat' && p.categories.includes(order!.category)).map(p => ({ value: p.id, label: `${p.name} · ${p.experience} yil tajriba` })) : db.shops.filter(s => s.isActive).map(s => ({ value: s.id, label: `${s.name} · ${s.district}` }));
    actions.setForm({ title: kind === 'plumber' ? 'Santexnik tayinlash / qayta tayinlash' : 'Do‘kon tayinlash / qayta tayinlash', description: kind === 'plumber' ? 'Faqat Marhamat va xizmat yo‘nalishiga mos faol ustalar. Avtomatik tayinlash yo‘q.' : 'Barcha hududlardagi faol do‘konlar. Har buyurtmaga bitta umumiy do‘kon akkaunti.', fields: [{ name: 'partner', label: kind === 'plumber' ? 'Mos santexnik' : 'Do‘kon', type: 'select', required: true, options }, { name: 'reason', label: 'Tayinlash sababi / izoh', type: 'textarea', required: true }], submit: values => actions.setConfirm({ title: 'Tayinlashni tasdiqlash', description: options.find(o => o.value === values.partner)?.label ?? '', action: () => actions.update(kind === 'plumber' ? 'Santexnik tayinlandi' : 'Do‘kon tayinlandi', (current, draft) => {
      if (isClosed(current.status) || current.preparationStarted || current.workStarted || current.dispute.open) throw new Error('Bu bosqichda qayta tayinlash mumkin emas.');
      if (kind === 'plumber') {
        const partner = draft.plumbers.find(p => p.id === values.partner && p.isActive && p.district === 'Marhamat' && p.categories.includes(current.category));
        if (!partner) throw new Error('Santexnik hudud/xizmatga mos emas.');
        current.plumberId = partner.id; current.assignedAt = now(); current.status = 'assigned';
        current.commissions.plumber = partner.commission ?? draft.settings.plumberCommission;
      } else {
        if (!current.plumberId) throw new Error('Avval santexnik tayinlang.');
        const partner = draft.shops.find(s => s.id === values.partner && s.isActive); if (!partner) throw new Error('Do‘kon faol emas.');
        current.shopId = partner.id; current.status = 'shop_pending'; current.commissions.shop = partner.commission ?? draft.settings.shopCommission;
      }
      if (current.estimate.approved) {
        current.estimateHistory.unshift(structuredClone(current.estimate)); current.estimate = { ...structuredClone(current.estimate), version: current.estimate.version + 1, approved: false, createdAt: now() };
      }
      if (current.contract.signedAt) current.contractHistory = [...(current.contractHistory ?? []), structuredClone(current.contract)];
      current.contract = { ...current.contract, signatures: [false, false, false, false], signedAt: null, signedBy: null };
      current.notes.push(String(values.reason));
    }, 'Tayinlash') }) });
  }
  function requestCancellation() {
    actions.setForm({
      title: 'Buyurtmani bekor qilish',
      fields: [
        { name: 'initiator', label: 'Sababchi tomon', type: 'select', required: true, options: [{ value: 'customer', label: 'Mijoz' }, { value: 'company', label: 'Kompaniya / do‘kon / santexnik' }] },
        { name: 'reason', label: 'Bekor qilish sababi', type: 'textarea', required: true },
      ],
      submit: values => actions.setConfirm({
        title: 'Buyurtma bekor qilinsinmi?', danger: true,
        description: order!.preparationStarted || order!.workStarted ? 'Tayyorlash yoki ish boshlangan. Mijoz sababli bo‘lsa avans qaytarilmaydi; hamkor sababli bo‘lsa alohida qaror kerak.' : 'Tayyorlash va ish boshlanmagan. Mijoz bekor qilsa avans to‘liq qaytariladi.',
        action: () => actions.update('Buyurtma bekor qilindi', current => {
          if (isClosed(current.status)) throw new Error('Buyurtma allaqachon yopilgan.');
          if (current.dispute.open) throw new Error('Avval ochiq nizo bo‘yicha qarorni qayd eting.');
          current.status = 'cancelled';
          current.cancelReason = String(values.reason);
          current.refundDecision = values.initiator === 'company' ? 'pending' : current.preparationStarted || current.workStarted ? 'none' : 'full';
        }, 'Bekor qilish'),
      }),
    });
  }
  return <><Link className="back-link" to="/orders"><ArrowLeft size={16} />Buyurtmalar ro‘yxatiga</Link><PageHeader eyebrow="BUYURTMA TAFSILOTI / DEMO" title={order.id} description={`Yaratilgan: ${dateTime(order.createdAt)} · ${customer?.name}`} actions={<StatusBadge status={order.status} />} />
    <div className="order-actions"><div className="inline-actions"><button className="button secondary" disabled={locked || order.preparationStarted || order.workStarted} onClick={() => assign('plumber')}><Wrench size={16} />{order.plumberId ? 'Santexnikni almashtirish' : 'Santexnik tayinlash'}</button><button className="button secondary" disabled={locked || !order.plumberId || order.preparationStarted || order.workStarted} onClick={() => assign('shop')}><Store size={16} />{order.shopId ? 'Do‘konni almashtirish' : 'Do‘kon tayinlash'}</button><button className="button secondary" onClick={() => actions.setForm({ title: 'Admin izohi', fields: [{ name: 'note', label: 'Ichki izoh', type: 'textarea', required: true }], submit: values => actions.update('Admin izohi qo‘shildi', current => { current.notes.push(String(values.note)); }) })}><MessageSquarePlus size={16} />Izoh</button></div>{!isClosed(order.status) && <button className="button ghost danger-text" disabled={order.dispute.open} onClick={requestCancellation}><XCircle size={16} />Bekor qilish</button>}</div>
    {order.dispute.open && <Notice danger>Ochiq nizo: qoldiq to‘lov va hamkorlarning yakuniy hisob-kitobi bloklangan.</Notice>}{order.cancelReason && <Notice>Bekor qilish sababi: {order.cancelReason}. Avans qarori: {order.refundDecision === 'full' ? 'to‘liq qaytarish' : order.refundDecision === 'none' ? 'qaytarilmaydi' : 'admin qarori kutilmoqda'}.</Notice>}
    {next && !order.dispute.open && <div className="next-step"><div><strong>Keyingi bosqich: {statusLabels[next]}</strong><p>{nextError ?? 'Talablar bajarilgan. O‘tish faqat namoyish uchun.'}</p></div><button className="button primary" disabled={!!nextError} title={nextError ?? ''} onClick={changeStatus}>Demo bosqichni qayd etish<ArrowRight size={16} /></button></div>}
    <Tabs items={tabs.map(t => ({ value: t, label: t }))} value={tab} onChange={setTab} />
    {tab === 'Umumiy' && <GeneralPanel order={order} actions={actions} />}{tab === 'Smeta va materiallar' && <EstimatePanel order={order} actions={actions} />}{tab === 'Jarayon' && <ProcessPanel order={order} actions={actions} />}{tab === 'Shartnoma' && <ContractPanel order={order} actions={actions} />}{tab === 'To‘lov va hisob-kitob' && <OrderFinance order={order} actions={actions} />}{tab === 'Nizo va baho' && <DisputePanel order={order} actions={actions} />}{tab === 'Audit' && <Panel title="Buyurtma auditi"><AuditTable rows={db.audit.filter(a => a.objectId === order.id)} /></Panel>}{actions.dialogs}
  </>;
}
function GeneralPanel({ order, actions }: { order: Order; actions: OrderActions }) {
  const { db } = useStore();
  const customer = db.customers.find(c => c.id === order.customerId)!;
  const plumber = db.plumbers.find(p => p.id === order.plumberId);
  const shop = db.shops.find(s => s.id === order.shopId);
  const locked = isClosed(order.status) || order.dispute.open;
  return <div className="detail-columns"><div><Panel title="So‘rov ma’lumotlari"><dl className="panel-padding detail-grid"><KeyValue label="Xizmat">{order.service}</KeyValue><KeyValue label="Xizmat guruhi">{order.category}</KeyValue><KeyValue label="Manzil">{order.address}</KeyValue><KeyValue label="Shoshilinch">{order.urgent ? order.urgencyApproved ? 'Demo tasdiqlangan' : 'Admin tasdig‘i kutilmoqda' : 'Oddiy so‘rov'}</KeyValue></dl><div className="panel-padding top-border"><h3>Muammo izohi</h3><p>{order.description || 'Izoh kiritilmagan.'}</p><div className="map-placeholder"><MapPin size={27} /><strong>Marhamat tumani · demo xarita nuqtasi</strong><span>{order.coordinates || 'Xarita nuqtasi kiritilmagan'}</span><small>Xarita integratsiyasi keyingi bosqichda</small></div><FilePreview label="Muammo surati uchun namuna joy" />{order.urgent && !order.urgencyApproved && <div className="inline-actions"><button className="button secondary" disabled={locked || order.estimate.approved} onClick={() => actions.setConfirm({ title: 'Shoshilinch so‘rovni tasdiqlash', description: 'Markazning sozlangan ish vaqti tekshiriladi. Tarif smetada alohida ko‘rsatiladi.', action: () => actions.update('Shoshilinch belgi tasdiqlandi', (current, draft) => {
    const { opens, closes } = draft.settings;
    const time = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Tashkent', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(new Date());
    if (!opens || !closes) throw new Error('Markaz ish vaqti sozlanmagan. Sozlamalarda kiriting.');
    if (time < opens || time >= closes) throw new Error('Shoshilinch so‘rov faqat markaz ish vaqtida tasdiqlanadi.');
    current.urgencyApproved = true;
  }) })}>Shoshilinchni tasdiqlash</button><button className="button secondary" disabled={locked || order.estimate.approved} onClick={() => actions.setConfirm({ title: 'Shoshilinch belgini olib tashlash', description: 'So‘rov oddiy bo‘ladi, shoshilinch haq nolga tenglanadi.', action: () => actions.update('Shoshilinch belgi olib tashlandi', current => { current.urgent = false; current.urgencyApproved = false; current.estimate.emergencyFee = 0; }) })}>Oddiy so‘rovga o‘tkazish</button></div>}</div></Panel><Panel title="Ichki admin izohlari"><div className="panel-padding">{order.notes.length ? order.notes.map((note, i) => <p className="note-item" key={i}>{note}</p>) : <p className="muted">Hozircha ichki izoh yo‘q.</p>}</div></Panel></div><div><Panel title="Mijoz"><div className="panel-padding"><div className="profile-heading"><Avatar name={customer.name} /><div><Link className="text-link" to={`/customers/${customer.id}`}>{customer.name}</Link><p>{customer.phone}</p></div></div><dl><KeyValue label="Telegram">{customer.telegramId ? 'Demo bog‘langan' : 'Bog‘lanmagan'}</KeyValue><KeyValue label="Ma’lumot ulashish roziligi"><Badge tone={order.consent ? 'success' : 'danger'}>{order.consent ? 'Qayd etilgan (demo)' : 'Rozilik yo‘q'}</Badge></KeyValue></dl><Notice>Telefon raqami sun’iy namuna. Haqiqiy qo‘ng‘iroq amalga oshirmang.</Notice></div></Panel><Panel title="Biriktirilgan hamkorlar"><div className="panel-padding"><div className="partner-summary"><Wrench size={19} /><div><small>Santexnik</small>{plumber ? <Link className="text-link" to={`/plumbers/${plumber.id}`}>{plumber.name}</Link> : <strong>Tayinlanmagan</strong>}</div></div><div className="partner-summary"><Store size={19} /><div><small>Do‘kon · umumiy akkaunt</small>{shop ? <Link className="text-link" to={`/shops/${shop.id}`}>{shop.name}</Link> : <strong>Tayinlanmagan</strong>}</div></div><p className="small muted">Do‘kon xodimlari alohida aniqlanmaydi. CRM admin ko‘rinishida hamkor kontaktlari ochiq.</p></div></Panel></div></div>;
}
function DisputePanel({ order, actions }: { order: Order; actions: OrderActions }) {
  const { db } = useStore();
  return <div className="detail-columns"><Panel title="Nizo va admin qarori"><div className="panel-padding">{order.dispute.reason ? <><Badge tone={order.dispute.open ? 'danger' : 'success'}>{order.dispute.open ? 'Nizo ochiq' : 'Hal qilingan'}</Badge><p>{order.dispute.reason}</p><FilePreview label="Nizo dalili uchun demo media" />{order.dispute.resolution && <Notice>Admin qarori: {order.dispute.resolution}</Notice>}</> : <p className="muted">Nizo qayd etilmagan.</p>}{order.dispute.open ? <button className="button primary" onClick={() => actions.setForm({ title: 'Nizo bo‘yicha qaror', description: 'Qaror tomonlar bilan tizimdan tashqarida kelishiladi.', fields: [{ name: 'resolution', label: 'Kelishilgan qaror / admin izohi', type: 'textarea', required: true }], submit: values => actions.setConfirm({ title: 'Nizoni yopish va blokni yechish', description: String(values.resolution), action: () => actions.update('Nizo hal qilindi', current => { current.dispute.open = false; current.dispute.resolution = String(values.resolution); current.status = current.dispute.previousStatus ?? 'completion'; }) }) })}>Qarorni qayd etish</button> : <button disabled={isClosed(order.status)} className="button secondary" onClick={() => actions.setForm({ title: 'Demo nizo ochish', fields: [{ name: 'reason', label: 'Mijoz e’tirozi', type: 'textarea', required: true }], submit: values => actions.setConfirm({ title: 'Nizo ochilsinmi?', description: 'Qoldiq to‘lov va hamkor hisob-kitobi bloklanadi.', danger: true, action: () => actions.update('Mijoz nizosi ochildi', current => { current.dispute = { open: true, reason: String(values.reason), resolution: '', previousStatus: current.status }; current.status = 'dispute'; }) }) })}>Nizo ochish</button>}{order.refundDecision === 'pending' && <button className="button secondary" onClick={() => actions.setForm({ title: 'Avansni qaytarish qarori', fields: [{ name: 'decision', label: 'Qaror', type: 'select', required: true, options: [{ value: 'full', label: 'To‘liq qaytarish' }, { value: 'none', label: 'Qaytarilmaydi' }] }, { name: 'reason', label: 'Qaror asosi', type: 'textarea', required: true }], submit: values => actions.setConfirm({ title: 'Qaytarish qarorini tasdiqlash', description: String(values.reason), action: () => actions.update('Avansni qaytarish qarori qayd etildi', current => { current.refundDecision = values.decision as 'full' | 'none'; current.notes.push(String(values.reason)); }) }) })}>Avans qarorini qayd etish</button>}</div></Panel><Panel title="Mijoz tasdiqlari va reyting"><div className="panel-padding"><dl><KeyValue label="Material qabul qilingan">{order.materialReceived ? 'Demo tasdiqlangan' : 'Kutilmoqda'}</KeyValue><KeyValue label="Ish mijoz tomonidan qabul qilingan">{order.customerCompleted ? 'Demo tasdiqlangan' : 'Kutilmoqda'}</KeyValue></dl><div className="inline-actions"><button className="button secondary" disabled={order.materialReceived || order.status !== 'delivered' || order.dispute.open} onClick={() => actions.setConfirm({ title: 'Material qabulini demo qilish', description: 'Mijozning haqiqiy tasdig‘i olinmaydi.', action: () => actions.update('Mijoz material qabulini demo tasdiqladi', current => { current.materialReceived = true; }) })}>Material qabulini demo tasdiqlash</button><button className="button secondary" disabled={order.customerCompleted || order.status !== 'completion' || order.dispute.open} onClick={() => actions.setConfirm({ title: 'Ish qabulini demo qilish', description: 'Mijozning haqiqiy tasdig‘i olinmaydi.', action: () => actions.update('Mijoz ish yakunini demo tasdiqladi', current => { current.customerCompleted = true; }) })}>Ish qabulini demo tasdiqlash</button></div>{db.reviews.filter(r => r.orderId === order.id).map(r => <div className="review-card" key={r.id}><strong>{'★'.repeat(r.score)}{'☆'.repeat(5 - r.score)}</strong><p>{r.comment}</p><Badge tone={r.status === 'published' ? 'success' : 'warning'}>{r.status === 'published' ? 'Ko‘rsatilgan' : r.status === 'pending' ? 'Moderatsiya kutilmoqda' : 'Yashirilgan'}</Badge></div>)}<Link className="text-link" to="/reviews">Reytinglar moderatsiyasi <ArrowRight size={15} /></Link></div></Panel></div>;
}
