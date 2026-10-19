import { useState } from 'react';
import { useStore } from '../../app/store';
import { paymentError } from '../../domain/rules';
import { paymentLabels, type Payment, type PaymentKind } from '../../domain/types';
import { id, money } from '../../shared/format';
import { ConfirmDialog, Modal, Notice, RecordForm, type Confirmation } from '../../shared/ui';

export function PaymentDialog({ orderId, initialType = 'advance', onClose }: { orderId?: string; initialType?: PaymentKind; onClose: () => void }) {
  const { db, mutate } = useStore();
  const [confirmation, setConfirmation] = useState<Confirmation | null>(null);
  return <>{!confirmation && <Modal title="Moliyaviy demo yozuv" description="Haqiqiy pul o‘tkazilmaydi. Yozuv alohida xodim tasdig‘ini kutadi." onClose={onClose} wide><Notice>Ichki kvitansiya fiskal chek o‘rnini bosmaydi. Naqd topshirish va hamkor hisob-kitobi uchun markaz xodimi tasdig‘i talab qilinadi.</Notice><RecordForm fields={[
    { name: 'orderId', label: 'Buyurtma', type: 'select', required: true, options: db.orders.map(o => ({ value: o.id, label: `${o.id} · ${db.customers.find(c => c.id === o.customerId)?.name}` })) },
    { name: 'type', label: 'To‘lov turi', type: 'select', required: true, options: Object.entries(paymentLabels).map(([value, label]) => ({ value, label })) },
    { name: 'amount', label: 'Summa (UZS)', type: 'number', required: true, min: 1 },
    { name: 'method', label: 'Usul', type: 'select', required: true, options: [{ value: 'cash', label: 'Naqd' }, { value: 'terminal', label: 'Karta-terminal' }] },
    { name: 'collector', label: 'Qabul joyi / pul yig‘uvchi', type: 'select', required: true, options: [{ value: 'center', label: 'Xizmat markazi' }, { value: 'plumber', label: 'Mijoz manzilida santexnik' }] },
    { name: 'receivedBy', label: 'Qabul qiluvchi / hamkor nomi', required: true },
    { name: 'timestamp', label: 'Sana va vaqt (Toshkent)', type: 'datetime-local', required: true },
    { name: 'note', label: 'Izoh / asos', type: 'textarea', required: true },
  ]} initial={{ orderId: orderId ?? '', type: initialType, method: 'cash', collector: 'center', timestamp: new Date(Date.now() + 5 * 3600000).toISOString().slice(0, 16) }} onCancel={onClose} submitLabel="Yozuvni tekshirish" onSubmit={values => {
    const data: Omit<Payment, 'id' | 'recordedBy' | 'status' | 'confirmedBy'> = {
      orderId: String(values.orderId), type: values.type as PaymentKind, method: values.method as Payment['method'],
      amount: Number(values.amount), timestamp: `${values.timestamp}:00+05:00`, receivedBy: String(values.receivedBy), note: String(values.note), collector: values.collector as Payment['collector'],
    };
    const error = paymentError(db, data);
    if (error) throw new Error(error);
    const order = db.orders.find(o => o.id === data.orderId)!;
    setConfirmation({ title: 'Moliyaviy yozuvni tasdiqlash', description: `${data.orderId} · ${paymentLabels[data.type]} · ${money(data.amount)}. Qabul qiluvchi: ${data.receivedBy}.`, details: <p className="muted">Do‘kon komissiyasi: {order.commissions.shop ?? 'sozlanmagan'}%; santexnik komissiyasi: {order.commissions.plumber ?? 'sozlanmagan'}%. Summa hisob-kitob chegaralariga tekshirildi.</p>, label: 'Demo yozuv yaratish', action: () => {
      mutate({ action: 'Moliyaviy yozuv', objectType: 'To‘lov', objectId: data.orderId, summary: `${paymentLabels[data.type]} · ${money(data.amount)} · xodim tasdig‘i kutilmoqda`, after: data }, draft => {
        const error = paymentError(draft, data); if (error) throw new Error(error);
        draft.payments.unshift({ ...data, id: id('PAY'), recordedBy: 'Demo administrator', status: 'recorded', confirmedBy: null });
      }); onClose();
    } });
  }} /></Modal>}{confirmation && <ConfirmDialog value={confirmation} onClose={() => { setConfirmation(null); onClose(); }} />}</>;
}
export function confirmPayment(payment: Payment, mutate: ReturnType<typeof useStore>['mutate'], setConfirm: (value: Confirmation) => void) {
  setConfirm({ title: 'Markaz xodimi tasdig‘i', description: `${payment.orderId} · ${paymentLabels[payment.type]} · ${money(payment.amount)}. Demo operator qabul/berilgan summani tasdiqlaydi.`, action: () => mutate({ actor: 'Demo operator', action: 'To‘lov tasdig‘i', objectType: 'To‘lov', objectId: payment.orderId, summary: `${payment.id} · Demo operator tasdiqladi`, before: { status: payment.status }, after: { status: 'confirmed' } }, draft => {
    const record = draft.payments.find(p => p.id === payment.id);
    if (!record || record.status === 'confirmed') throw new Error('Yozuv avval tasdiqlangan yoki topilmadi.');
    const withoutPending = { ...draft, payments: draft.payments.filter(p => p.id !== payment.id) };
    const error = paymentError(withoutPending, record); if (error) throw new Error(error);
    record.status = 'confirmed'; record.confirmedBy = 'Demo operator';
  }) });
}
