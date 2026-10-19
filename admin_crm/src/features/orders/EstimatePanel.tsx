import { useState } from 'react';
import { Plus, Trash2, Send, CheckCheck } from 'lucide-react';
import { useStore } from '../../app/store';
import { advanceRequired, estimateTotal, isClosed, lineTotal } from '../../domain/rules';
import type { Estimate, EstimateLine, Order } from '../../domain/types';
import { id, now, money } from '../../shared/format';
import { Badge, KeyValue, Modal, Money, Notice, Panel } from '../../shared/ui';
import type { OrderActions } from './useOrderActions';

export function EstimatePanel({ order, actions }: { order: Order; actions: OrderActions }) {
  const [editing, setEditing] = useState(false);
  const total = estimateTotal(order.estimate);
  const approvedTotal = order.confirmedEstimate ? estimateTotal(order.confirmedEstimate) : null;
  const editable = !order.preparationStarted && !order.workStarted && !isClosed(order.status) && !order.dispute.open;
  const summary = <dl className="estimate-summary"><KeyValue label="Xizmatlar"><Money value={lineTotal(order.estimate.services)} /></KeyValue><KeyValue label="Materiallar"><Money value={lineTotal(order.estimate.materials)} /></KeyValue><KeyValue label="Yetkazish (bir marta)"><Money value={order.estimate.deliveryFee} /></KeyValue><KeyValue label="Shoshilinch chaqiruv"><Money value={order.estimate.emergencyFee} /></KeyValue><KeyValue label="Platforma haqi"><Money value={0} /></KeyValue><KeyValue label="Yakuniy jami"><strong className="text-blue"><Money value={total} /></strong></KeyValue><KeyValue label="Talab qilinadigan avans"><Money value={advanceRequired(order)} /></KeyValue></dl>;
  const approveDemo = () => actions.setConfirm({ title: 'Mijoz tasdig‘ini demo qilish', description: 'Bu namoyish haqiqiy mijoz roziligini anglatmaydi. Faqat joriy smeta nusxasi lokal tasdiqlanadi.', action: () => actions.update('Mijoz smetani demo tasdiqladi', current => {
    if (current.status !== 'approval' || estimateTotal(current.estimate) === null) throw new Error('Narxlar to‘liq emas yoki smeta tasdiq bosqichida emas.');
    if (!current.plumberId || (current.estimate.materials.length > 0 && !current.shopId)) throw new Error('Avval santexnik va materiallar uchun do‘kon tayinlang.');
    if (advanceRequired(current) === null) throw new Error('Avans miqdori sozlanmagan. To‘lov va hisob-kitob bo‘limida avansni belgilang.');
    if (current.estimate.materials.some(l => l.available !== true)) throw new Error('Barcha materiallarning mavjudligi tasdiqlanishi kerak.');
    current.estimate.approved = true; current.confirmedEstimate = structuredClone(current.estimate); current.status = 'contract';
  }, 'Demo tasdiqlash') });
  return <><Panel title={`Smeta · ${order.estimate.version}-versiya`} caption="QQS barcha narxlarga kiritilgan · UZS" action={<div className="inline-actions"><Badge tone={order.estimate.approved ? 'success' : 'warning'}>{order.estimate.approved ? 'Demo tasdiqlangan' : 'Tasdiq kutilmoqda'}</Badge>{editable && <button className="button secondary" onClick={() => setEditing(true)}>Smetani tahrirlash</button>}</div>}>
    {!order.estimate.approved && order.confirmedEstimate && <div className="panel-padding"><Notice><strong>Yangi smeta qayta tasdiqlanishi kerak.</strong><br />Oldingi tasdiqlangan jami: {money(approvedTotal)}. Yangi taklif: {money(total)}. Farq: {total !== null && approvedTotal !== null ? money(total - approvedTotal) : 'Sozlanmagan'}.<br />Avans farqi: {advanceRequired(order) !== null && advanceRequired(order, order.confirmedEstimate) !== null ? money(advanceRequired(order)! - advanceRequired(order, order.confirmedEstimate)!) : 'Sozlanmagan'}.</Notice></div>}
    <EstimateLines title="Xizmatlar" lines={order.estimate.services} /><EstimateLines title="Materiallar" lines={order.estimate.materials} />{summary}
    <div className="panel-padding"><p className="muted small">Tasdiqlangan smeta katalogdan alohida nusxa sifatida saqlanadi. Katalog tahriri bu narxlarga ta’sir qilmaydi.</p>{order.status === 'approval' && <button className="button primary" onClick={approveDemo}><CheckCheck size={17} />Mijoz tasdig‘ini demo qilish</button>}</div>
  </Panel>{order.estimateHistory.length > 0 && <Panel title="Oldingi smeta versiyalari"><div className="panel-padding">{order.estimateHistory.map(e => <div className="history-row" key={`${e.version}-${e.createdAt}`}><span>{e.version}-versiya · {e.approved ? 'Tasdiqlangan nusxa' : 'Qoralama'}</span><Money value={estimateTotal(e)} /></div>)}</div></Panel>}{editing && <EstimateEditor order={order} onClose={() => setEditing(false)} onSubmit={estimate => { actions.update('Smeta yangi versiya sifatida taklif qilindi', current => {
    if (current.preparationStarted || current.workStarted || current.dispute.open || isClosed(current.status)) throw new Error('Ish yoki material tayyorlash boshlangan. Smetani o‘zgartirish bloklangan.');
    current.estimateHistory.unshift(structuredClone(current.estimate));
    current.estimate = { ...estimate, version: current.estimate.version + 1, approved: false, createdAt: now() };
    if (current.contract.signedAt) { current.contractHistory = [...(current.contractHistory ?? []), structuredClone(current.contract)]; }
    current.contract = { ...current.contract, signatures: [false, false, false, false], signedAt: null, signedBy: null };
    current.status = 'approval';
  }); setEditing(false); }} />}</>;
}
function EstimateLines({ title, lines }: { title: string; lines: EstimateLine[] }) {
  return <div className="estimate-lines"><h3>{title}</h3><div className="table-scroll"><table><thead><tr><th>Nomi / marka</th><th>Miqdor</th><th>Birlik narxi</th><th>Mavjudlik</th><th className="numeric">Jami</th></tr></thead><tbody>{lines.map(line => <tr key={line.id}><td><div className="cell-stack"><strong>{line.name}</strong>{line.brand && <small>{line.brand}</small>}</div></td><td>{line.quantity} {line.unit}</td><td><Money value={line.price} /></td><td>{line.available === undefined ? '—' : <Badge tone={line.available ? 'success' : 'warning'}>{line.available ? 'Mavjud' : 'Kutilmoqda'}</Badge>}</td><td className="numeric"><Money value={line.price === null ? null : Math.round(line.price * line.quantity)} /></td></tr>)}</tbody></table>{!lines.length && <p className="panel-padding muted">Hozircha qator qo‘shilmagan.</p>}</div></div>;
}
function EstimateEditor({ order, onClose, onSubmit }: { order: Order; onClose: () => void; onSubmit: (estimate: Estimate) => void }) {
  const { db } = useStore();
  const [estimate, setEstimate] = useState(() => structuredClone(order.estimate));
  const [error, setError] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [selectedMaterial, setSelectedMaterial] = useState('');
  const updateLine = (group: 'services' | 'materials', lineId: string, patch: Partial<EstimateLine>) => setEstimate(e => ({ ...e, [group]: e[group].map(l => l.id === lineId ? { ...l, ...patch } : l) }));
  return <Modal title="Smetaning yangi versiyasi" description="Yangi narxlar mijoz qayta tasdiqlamaguncha qo‘llanmaydi." onClose={onClose} wide><Notice>Yuborilganda eski nusxa saqlanadi, yangi smeta tasdig‘i va shartnoma imzolari qayta kutiladi.</Notice><form noValidate onSubmit={event => {
    event.preventDefault();
    const lines = [...estimate.services, ...estimate.materials];
    if (!estimate.services.length || lines.some(l => !l.name.trim() || !l.unit.trim() || !Number.isFinite(l.quantity) || l.quantity <= 0 || (!['metr', 'm²'].includes(l.unit) && !Number.isInteger(l.quantity)) || (l.price !== null && (!Number.isInteger(l.price) || l.price <= 0)))) { setError('Nom, birlik, musbat miqdor va narxni tekshiring. Dona/komplekt uchun butun miqdor kiriting.'); return; }
    if ([estimate.deliveryFee, estimate.emergencyFee].some(value => value === null || !Number.isInteger(value) || value < 0)) { setError('Yetkazish va shoshilinch haq uchun manfiy bo‘lmagan butun UZS kiriting. Qo‘llanmasa 0 yozing.'); return; }
    if (order.urgent && !order.urgencyApproved) { setError('Shoshilinch belgini avval umumiy bo‘limda tasdiqlang yoki olib tashlang.'); return; }
    if (!order.urgent && estimate.emergencyFee !== 0) { setError('Oddiy so‘rov uchun shoshilinch haq 0 bo‘lishi kerak.'); return; }
    try { onSubmit(estimate); } catch (e) { setError(e instanceof Error ? e.message : 'Smeta saqlanmadi.'); }
  }}>
    {(['services', 'materials'] as const).map(group => <section className="line-editor" key={group}><h3>{group === 'services' ? 'Xizmat qatorlari' : 'Material qatorlari'}</h3>{estimate[group].map((line, index) => <fieldset key={line.id}><legend>{index + 1}-qator</legend><div className="form-grid"><label>Nomi *<input aria-label={`${group} ${index + 1} nomi`} required value={line.name} onChange={e => updateLine(group, line.id, { name: e.target.value })} /></label><label>Miqdor *<input required type="number" min="0.01" step={['metr', 'm²'].includes(line.unit) ? 'any' : '1'} value={line.quantity} onChange={e => updateLine(group, line.id, { quantity: Number(e.target.value) })} /></label><label>Birlik *<input required value={line.unit} onChange={e => updateLine(group, line.id, { unit: e.target.value })} /></label><label>Birlik narxi (UZS)<input type="number" min="1" step="1" value={line.price ?? ''} placeholder="Sozlanmagan" onChange={e => updateLine(group, line.id, { price: e.target.value === '' ? null : Number(e.target.value) })} /></label>{group === 'materials' && <><label>Marka / muqobil izohi<input value={line.brand ?? ''} onChange={e => updateLine(group, line.id, { brand: e.target.value })} /></label><label className="checkbox"><input type="checkbox" checked={line.available ?? false} onChange={e => updateLine(group, line.id, { available: e.target.checked })} />Do‘kon mavjudlikni demo tasdiqladi</label></>}</div><button type="button" className="button ghost danger-text" onClick={() => setEstimate(e => ({ ...e, [group]: e[group].filter(l => l.id !== line.id) }))}><Trash2 size={15} />Qatorni olib tashlash</button></fieldset>)}<div className="inline-actions"><label className="grow"><span className="sr-only">{group === 'services' ? 'Katalog xizmati' : 'Katalog materiali'}</span><select value={group === 'services' ? selectedService : selectedMaterial} onChange={e => group === 'services' ? setSelectedService(e.target.value) : setSelectedMaterial(e.target.value)}><option value="">Katalogdan tanlash…</option>{(group === 'services' ? db.services : db.materials).filter(s => s.isActive).map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><button type="button" className="button secondary" onClick={() => {
      const selected = group === 'services' ? db.services.find(s => s.id === selectedService) : db.materials.find(m => m.id === selectedMaterial);
      if (!selected) { setError('Avval katalog qatorini tanlang.'); return; }
      const line: EstimateLine = { id: id('LINE'), name: selected.name, quantity: 1, unit: selected.unit, price: 'areaRate' in selected ? selected.areaRate : null, ...(group === 'materials' ? { brand: 'brand' in selected ? selected.brand : '', available: false } : {}) };
      setEstimate(e => ({ ...e, [group]: [...e[group], line] })); setError('');
    }}><Plus size={15} />Qo‘shish</button>{group === 'materials' && <button type="button" className="button secondary" onClick={() => setEstimate(e => ({ ...e, materials: [...e.materials, { id: id('LINE'), name: '', quantity: 1, unit: 'dona', price: null, available: false }] }))}>Erkin qator</button>}</div></section>)}
    <div className="form-grid"><label>Yetkazish haqi (UZS) *<input type="number" min="0" step="1" required value={estimate.deliveryFee ?? ''} onChange={e => setEstimate(v => ({ ...v, deliveryFee: e.target.value === '' ? null : Number(e.target.value) }))} /></label><label>Shoshilinch haq (UZS) *<input type="number" min="0" step="1" required value={estimate.emergencyFee ?? ''} onChange={e => setEstimate(v => ({ ...v, emergencyFee: e.target.value === '' ? null : Number(e.target.value) }))} /></label></div><p className="estimate-total">Yangi jami: <Money value={estimateTotal(estimate)} /></p>{error && <p className="field-error" role="alert">{error}</p>}<div className="form-actions"><button type="button" className="button secondary" onClick={onClose}>Bekor qilish</button><button className="button primary"><Send size={16} />Qayta tasdiqlash so‘rovini demo yuborish</button></div>
  </form></Modal>;
}
