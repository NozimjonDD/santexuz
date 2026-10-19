import { useState } from 'react';
import { Link } from 'react-router';
import { Check, Eye, EyeOff, Star } from 'lucide-react';
import { useStore } from '../../app/store';
import type { Review } from '../../domain/types';
import { dateTime } from '../../shared/format';
import { Badge, ConfirmDialog, DataTable, Modal, Notice, PageHeader, Panel, Tabs, type Confirmation } from '../../shared/ui';

const labels = { pending: 'Tekshirish kutilmoqda', published: 'Ko‘rsatilgan', hidden: 'Yashirilgan' };
export default function Reviews() {
  const { db, mutate } = useStore();
  const [tab, setTab] = useState('pending');
  const [selected, setSelected] = useState<Review | null>(null);
  const [confirm, setConfirm] = useState<Confirmation | null>(null);
  const moderate = (review: Review, status: Review['status']) => setConfirm({ title: status === 'published' ? 'Bahoni ommaga chiqarish' : 'Bahoni yashirish', description: review.comment, danger: status === 'hidden', action: () => mutate({ action: 'Moderatsiya', objectType: 'Reyting', objectId: review.id, summary: `${review.orderId} · ${labels[status]}`, before: { status: review.status }, after: { status } }, draft => {
    const item = draft.reviews.find(r => r.id === review.id)!;
    const order = draft.orders.find(o => o.id === review.orderId);
    if (status === 'published' && order?.status !== 'completed') throw new Error('Faqat yakunlangan buyurtma bahosi ommaga chiqariladi.');
    item.status = status;
  }) });
  return <><PageHeader eyebrow="BOSHQARUV" title="Reytinglar" description="Mijoz fikrlarini tekshiring va tasdiqlangan reytinglarni boshqaring." /><Notice>Faqat moderatsiyadan o‘tgan baholar hamkorning umumiy reytingida hisoblanadi.</Notice><Panel><Tabs items={Object.entries(labels).map(([value, label]) => ({ value, label, count: db.reviews.filter(r => r.status === value).length }))} value={tab} onChange={setTab} /><DataTable rows={db.reviews.filter(r => r.status === tab)} searchText={r => `${r.comment} ${r.orderId} ${db.customers.find(c => c.id === r.customerId)?.name}`} columns={[
    { key: 'date', label: 'Sana', sortValue: r => r.createdAt, render: r => dateTime(r.createdAt) },
    { key: 'customer', label: 'Mijoz / buyurtma', sortValue: r => db.customers.find(c => c.id === r.customerId)?.name ?? '', render: r => <div className="cell-stack"><span>{db.customers.find(c => c.id === r.customerId)?.name}</span><Link className="text-link" to={`/orders/${r.orderId}`}>{r.orderId}</Link></div> },
    { key: 'target', label: 'Baholangan tomon', render: r => <div className="cell-stack"><strong>{r.targetType === 'plumber' ? db.plumbers.find(p => p.id === r.targetId)?.name : db.shops.find(s => s.id === r.targetId)?.name}</strong><small>{r.targetType === 'plumber' ? 'Santexnik' : 'Do‘kon'}</small></div> },
    { key: 'score', label: 'Baho', sortValue: r => r.score, render: r => <span className="rating"><Star size={15} />{r.score} / 5</span> },
    { key: 'comment', label: 'Izoh', render: r => <span className="audit-summary">{r.comment}</span> },
    { key: 'status', label: 'Holat', render: r => <Badge tone={r.status === 'published' ? 'success' : 'warning'}>{labels[r.status]}</Badge> },
    { key: 'actions', label: 'Amallar', render: r => <div className="row-actions"><button className="icon-button" aria-label="Izohni to‘liq ko‘rish" onClick={() => setSelected(r)}><Eye size={16} /></button>{r.status !== 'published' && <button className="icon-button" aria-label="Ommaga chiqarish" onClick={() => moderate(r, 'published')}><Check size={16} /></button>}{r.status !== 'hidden' && <button className="icon-button" aria-label="Yashirish" onClick={() => moderate(r, 'hidden')}><EyeOff size={16} /></button>}</div> },
  ]} /></Panel>{selected && <Modal title="Mijoz izohi" onClose={() => setSelected(null)}><span className="rating">{'★'.repeat(selected.score)}{'☆'.repeat(5 - selected.score)}</span><p>{selected.comment}</p><Link className="text-link" to={`/orders/${selected.orderId}`}>{selected.orderId} ni ochish</Link></Modal>}{confirm && <ConfirmDialog value={confirm} onClose={() => setConfirm(null)} />}</>;
}
