import { useState } from 'react';
import { MapPin, ShieldCheck } from 'lucide-react';
import { useStore } from '../../app/store';
import { Badge, ConfirmDialog, KeyValue, Notice, PageHeader, Panel, RecordForm, Tabs, type Confirmation, type FieldSpec, type FormValues } from '../../shared/ui';
import type { Settings as SettingsType } from '../../domain/types';

const sections = ['Hudud', 'Xizmat markazi', 'So‘rovlar', 'To‘lov', 'Komissiyalar', 'Til va bildirishnoma'];
const fieldsBySection: Record<string, FieldSpec[]> = {
  'Xizmat markazi': [
    { name: 'centerName', label: 'Markaz nomi', required: true, full: true }, { name: 'address', label: 'Manzil', full: true, hint: 'Aniq manzil tasdiqlanmagan. Faqat demo kiriting.' },
    { name: 'phone', label: 'Telefon', type: 'tel' }, { name: 'opens', label: 'Ish boshlanishi (Toshkent)', type: 'time' },
    { name: 'closes', label: 'Ish tugashi (Toshkent)', type: 'time', validate: (v, values) => v && values.opens && v <= String(values.opens) ? 'Tugash vaqti boshlanishdan keyin bo‘lsin.' : null },
  ],
  'So‘rovlar': [{ name: 'responseMinutes', label: 'Santexnik javob muddati (daqiqa)', type: 'number', min: 1, max: 1440, required: true, hint: 'Muddat o‘tsa faqat ogohlantiriladi. Avtomatik qayta tayinlash yo‘q.' }],
  'To‘lov': [
    { name: 'advanceMode', label: 'Standart avans turi', type: 'select', required: true, options: [{ value: 'percent', label: 'Foiz' }, { value: 'fixed', label: 'Qat’iy summa (UZS)' }] },
    { name: 'advanceValue', label: 'Avans qiymati', type: 'number', min: 1, hint: 'Bo‘sh bo‘lsa: Sozlanmagan.', validate: (v, values) => v && values.advanceMode === 'percent' && Number(v) > 100 ? 'Foiz 100 dan oshmasin.' : null },
  ],
  'Komissiyalar': [
    { name: 'plumberCommission', label: 'Santexnik standart komissiyasi (%)', type: 'number', max: 100, hint: 'Bo‘sh qiymat nolga teng emas. Hamkor individual stavkasi ustuvor.' },
    { name: 'shopCommission', label: 'Do‘kon standart komissiyasi (%)', type: 'number', max: 100, hint: 'Do‘kon komissiyasi faqat materiallar summasidan hisoblanadi.' },
  ],
  'Til va bildirishnoma': [
    { name: 'language', label: 'CRM tili', type: 'select', required: true, options: [{ value: 'uz', label: 'O‘zbekcha' }], hint: 'CRM MVP o‘zbekcha. Mini Appning UZ/RU/EN tanlovi alohida.' },
    { name: 'notifications', label: 'CRM ichidagi bildirishnomalarni yoqish', type: 'checkbox', hint: 'Telegram xabarnomalari backendga ulanmagan.' },
  ],
};
export default function Settings() {
  const { db, mutate } = useStore();
  const [tab, setTab] = useState(sections[0]);
  const [confirmation, setConfirmation] = useState<Confirmation | null>(null);
  const fields = fieldsBySection[tab] ?? [];
  const initial = Object.fromEntries(fields.map(f => {
    const value = db.settings[f.name as keyof SettingsType];
    return [f.name, value == null ? '' : typeof value === 'number' ? String(value) : value];
  })) as FormValues;
  return <><PageHeader eyebrow="BOSHQARUV" title="Sozlamalar" description="Pilot hudud, xizmat markazi va ish jarayoni qoidalari." /><Tabs items={sections.map(value => ({ value, label: value }))} value={tab} onChange={setTab} />{tab === 'Hudud' ? <Panel title="Pilot hudud" caption="MVPda bitta jismoniy xizmat markazi"><div className="panel-padding"><div className="region-card"><span><MapPin size={28} /></span><div><h3>Andijon viloyati</h3><p>Marhamat tumani</p></div><Badge tone="success">Faol pilot</Badge></div><Notice>Hudud pilotga mahkamlangan. Yangi hududlar MVPdan keyin qo‘shiladi.</Notice><dl><KeyValue label="Valyuta">O‘zbekiston so‘mi (UZS)</KeyValue><KeyValue label="Vaqt mintaqasi">Asia/Tashkent · UTC+5</KeyValue><KeyValue label="Platforma haqi">Mijoz uchun 0 so‘m</KeyValue></dl></div></Panel> : <Panel title={tab} caption="O‘zgarishlar faqat keyingi demo yozuvlariga qo‘llanadi"><div className="panel-padding"><Notice>Haqiqiy manzil, avans va standart komissiyalar hali tasdiqlanmagan. Kiritilmagan qiymatlar “Sozlanmagan” holatida.</Notice><RecordForm key={`${tab}-${JSON.stringify(initial)}`} fields={fields} initial={initial} onSubmit={values => {
    const next: Record<string, unknown> = {};
    fields.forEach(f => { next[f.name] = f.type === 'number' ? String(values[f.name] ?? '').trim() ? Number(values[f.name]) : null : f.type === 'checkbox' ? values[f.name] === true : String(values[f.name] ?? '').trim(); });
    if (tab === 'Xizmat markazi' && (!!next.opens !== !!next.closes)) throw new Error('Ish boshlanishi va tugashini birga kiriting.');
    const before = Object.fromEntries(fields.map(f => [f.name, db.settings[f.name as keyof SettingsType]]));
    setConfirmation({ title: 'Sozlamani saqlash', description: 'Eski va yangi qiymatlarni tekshiring. Oldingi buyurtmalarning saqlangan narxlari o‘zgarmaydi.', details: <div className="comparison-grid"><div><h3>Oldingi</h3>{fields.map(f => <p key={f.name}><small>{f.label}</small><br /><strong>{before[f.name] == null || before[f.name] === '' ? 'Sozlanmagan' : String(before[f.name])}</strong></p>)}</div><div><h3>Yangi</h3>{fields.map(f => <p key={f.name}><small>{f.label}</small><br /><strong>{next[f.name] == null || next[f.name] === '' ? 'Sozlanmagan' : String(next[f.name])}</strong></p>)}</div></div>, action: () => mutate({ action: 'Sozlama', objectType: 'Sozlamalar', objectId: tab, summary: `${tab} sozlamalari yangilandi`, before, after: next }, draft => { Object.assign(draft.settings, next); }) });
  }} /></div></Panel>}<div className="security-note"><ShieldCheck size={17} /><span>Server ruxsatlari va o‘zgarmas audit backendga ulanish bosqichida bajariladi.</span></div>{confirmation && <ConfirmDialog value={confirmation} onClose={() => setConfirmation(null)} />}</>;
}
