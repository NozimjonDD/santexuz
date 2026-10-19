import { useState } from 'react';
import { Link } from 'react-router';
import { Eye, Check } from 'lucide-react';
import { useStore } from '../../app/store';
import { paymentLabels, type Payment } from '../../domain/types';
import { dateTime } from '../../shared/format';
import { Badge, ConfirmDialog, DataTable, KeyValue, Modal, Money, Notice, type Confirmation } from '../../shared/ui';
import { confirmPayment } from './PaymentDialog';

export function PaymentTable({ rows }: { rows: Payment[] }) {
  const { mutate } = useStore();
  const [receipt, setReceipt] = useState<Payment | null>(null);
  const [confirmation, setConfirmation] = useState<Confirmation | null>(null);
  return <><DataTable rows={rows} columns={[
    { key: 'timestamp', label: 'Sana', sortValue: p => p.timestamp, render: p => <span className="small nowrap">{dateTime(p.timestamp)}</span> },
    { key: 'order', label: 'Buyurtma', sortValue: p => p.orderId, render: p => <Link className="text-link" to={`/orders/${p.orderId}`}>{p.orderId}</Link> },
    { key: 'party', label: 'Tomon / qayd qilgan', sortValue: p => p.receivedBy, render: p => <div className="cell-stack"><strong>{p.receivedBy}</strong><small>{p.recordedBy}</small></div> },
    { key: 'type', label: 'To‘lov turi', sortValue: p => p.type, render: p => <div className="cell-stack"><span>{paymentLabels[p.type]}</span><small>{p.method === 'cash' ? 'Naqd' : 'Karta-terminal'} · {p.collector === 'center' ? 'Markaz' : 'Santexnik'}</small></div> },
    { key: 'amount', label: 'Summa', className: 'numeric', sortValue: p => p.amount, render: p => <Money value={p.amount} /> },
    { key: 'status', label: 'Status', sortValue: p => p.status, render: p => <Badge tone={p.status === 'confirmed' ? 'success' : 'warning'}>{p.status === 'confirmed' ? 'Demo tasdiqlangan' : 'Xodim tasdig‘i'}</Badge> },
    { key: 'actions', label: 'Amallar', render: p => <div className="row-actions"><button className="icon-button" aria-label={`${p.id} kvitansiya`} onClick={() => setReceipt(p)}><Eye size={16} /></button>{p.status === 'recorded' && <button className="icon-button" aria-label={`${p.id} xodim tasdig‘i`} onClick={() => confirmPayment(p, mutate, setConfirmation)}><Check size={16} /></button>}</div> },
  ]} />{receipt && <Modal title="Ichki demo kvitansiya" onClose={() => setReceipt(null)}><Notice>Fiskal chek emas. Haqiqiy pul qabul qilinmagan.</Notice><dl><KeyValue label="Raqam">{receipt.id}</KeyValue><KeyValue label="Buyurtma">{receipt.orderId}</KeyValue><KeyValue label="Tur">{paymentLabels[receipt.type]}</KeyValue><KeyValue label="Summa"><Money value={receipt.amount} /></KeyValue><KeyValue label="Usul">{receipt.method === 'cash' ? 'Naqd' : 'Karta-terminal'}</KeyValue><KeyValue label="Vaqt">{dateTime(receipt.timestamp)}</KeyValue><KeyValue label="Qabul qiluvchi">{receipt.receivedBy}</KeyValue><KeyValue label="Tasdiqlovchi">{receipt.confirmedBy ?? 'Kutilmoqda'}</KeyValue><KeyValue label="Izoh">{receipt.note}</KeyValue></dl></Modal>}{confirmation && <ConfirmDialog value={confirmation} onClose={() => setConfirmation(null)} />}</>;
}
