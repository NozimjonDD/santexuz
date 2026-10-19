import { useState } from 'react';
import { Eye } from 'lucide-react';
import { useStore } from '../../app/store';
import type { AuditEvent } from '../../domain/types';
import { dateTime, includesQuery, inDateRange } from '../../shared/format';
import { DataTable, DateRange, KeyValue, Modal, Notice, PageHeader, Panel, SearchInput, SelectFilter } from '../../shared/ui';

export function AuditTable({ rows }: { rows: AuditEvent[] }) {
  const [selected, setSelected] = useState<AuditEvent | null>(null);
  return <><DataTable rows={[...rows].sort((a, b) => b.timestamp.localeCompare(a.timestamp))} columns={[
    { key: 'time', label: 'Sana / vaqt', sortValue: r => r.timestamp, render: r => <span className="nowrap small">{dateTime(r.timestamp)}</span> },
    { key: 'actor', label: 'Akkaunt', sortValue: r => r.actor, render: r => r.actor },
    { key: 'action', label: 'Amal turi', sortValue: r => r.action, render: r => r.action },
    { key: 'object', label: 'Obyekt / ID', sortValue: r => r.objectType, render: r => <div className="cell-stack"><span>{r.objectType}</span><small>{r.objectId}</small></div> },
    { key: 'summary', label: 'Tafsilot', render: r => <span className="audit-summary">{r.summary}</span> },
    { key: 'actions', label: 'Ko‘rish', render: r => <button className="icon-button" aria-label={`${r.id} audit tafsiloti`} onClick={() => setSelected(r)}><Eye size={17} /></button> },
  ]} />{selected && <Modal title="Audit hodisasi" description="Bu jurnal UI’dan tahrirlanmaydi yoki o‘chirilmaydi." onClose={() => setSelected(null)} wide><dl><KeyValue label="Vaqt">{dateTime(selected.timestamp)}</KeyValue><KeyValue label="Akkaunt">{selected.actor}</KeyValue><KeyValue label="Amal">{selected.action}</KeyValue><KeyValue label="Tafsilot">{selected.summary}</KeyValue></dl><div className="comparison-grid"><div><h3>Oldingi qiymat</h3><pre>{selected.before == null ? 'Ma’lumot yo‘q' : JSON.stringify(selected.before, null, 2)}</pre></div><div><h3>Yangi qiymat</h3><pre>{selected.after == null ? 'Ma’lumot yo‘q' : JSON.stringify(selected.after, null, 2)}</pre></div></div></Modal>}</>;
}
export default function Audit() {
  const { db } = useStore();
  const [query, setQuery] = useState('');
  const [actor, setActor] = useState('');
  const [action, setAction] = useState('');
  const [object, setObject] = useState('');
  const [range, setRange] = useState({ from: '', to: '' });
  const options = (key: 'actor' | 'action' | 'objectType') => Array.from(new Set(db.audit.map(a => a[key]))).map(v => ({ value: v, label: v }));
  const rows = db.audit.filter(a => includesQuery(`${a.summary} ${a.objectId} ${a.actor}`, query) && (!actor || a.actor === actor) && (!action || a.action === action) && (!object || a.objectType === object) && inDateRange(a.timestamp, range.from, range.to));
  return <><PageHeader eyebrow="BOSHQARUV" title="Audit jurnali" description="Kim, qachon va nimani o‘zgartirgan — muhim amallar tarixi." /><Notice>Audit yozuvlari faqat o‘qiladi. Demo jurnali xotirada saqlanadi; o‘zgarmas server jurnali backend bosqichida ulanadi.</Notice><Panel><div className="filter-bar"><SearchInput value={query} onChange={setQuery} placeholder="Obyekt raqami yoki tafsilot…" /><SelectFilter label="Akkaunt" value={actor} onChange={setActor} options={options('actor')} /><SelectFilter label="Amal" value={action} onChange={setAction} options={options('action')} /><SelectFilter label="Obyekt" value={object} onChange={setObject} options={options('objectType')} /></div><div className="list-date-row"><span className="muted small">{rows.length} ta hodisa</span><DateRange {...range} onChange={(from, to) => setRange({ from, to })} /></div><AuditTable rows={rows} /></Panel></>;
}
