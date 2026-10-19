import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useStore } from '../../app/store';
import { advanceRequired, cashOutstanding, financials, isClosed } from '../../domain/rules';
import type { Order, PaymentKind } from '../../domain/types';
import { KeyValue, Money, Panel } from '../../shared/ui';
import { PaymentDialog } from '../finance/PaymentDialog';
import { PaymentTable } from '../finance/PaymentTable';
import type { OrderActions } from './useOrderActions';

export function OrderFinance({ order, actions }: { order: Order; actions: OrderActions }) {
  const { db } = useStore();
  const [paymentType, setPaymentType] = useState<PaymentKind | null>(null);
  const f = financials(order, db.payments);

  function configureAdvance() {
    actions.setForm({
      title: 'Buyurtma avansini belgilash',
      fields: [
        { name: 'mode', label: 'Avans turi', type: 'select', required: true, options: [{ value: 'percent', label: 'Foiz' }, { value: 'fixed', label: 'Qat’iy summa (UZS)' }] },
        { name: 'value', label: 'Qiymat', type: 'number', min: 1, required: true, validate: (v, values) => values.mode === 'percent' && Number(v) > 100 ? 'Foiz 100 dan oshmasin.' : null },
      ],
      initial: { mode: order.advance.mode, value: order.advance.value?.toString() ?? '' },
      submit: values => actions.setConfirm({
        title: 'Avans shartini o‘zgartirish',
        description: `Oldingi: ${order.advance.value ?? 'sozlanmagan'}. Yangi: ${values.value} (${values.mode}).`,
        action: () => actions.update('Buyurtma avansi sozlandi', current => {
          if (isClosed(current.status) || current.estimate.approved) throw new Error('Avans sharti smeta tasdiqlanishidan oldin belgilanadi.');
          current.advance = { mode: values.mode as 'percent' | 'fixed', value: Number(values.value) };
        }),
      }),
    });
  }

  return (
    <>
      <div className="detail-columns">
        <Panel title="Mijoz to‘lovlari">
          <dl className="panel-padding">
            <KeyValue label="Tasdiqlangan smeta jami"><Money value={order.confirmedEstimate ? f.total : null} /></KeyValue>
            <KeyValue label="Avans talabi"><Money value={advanceRequired(order)} /></KeyValue>
            <KeyValue label="Qabul qilingan"><Money value={f.paid} /></KeyValue>
            <KeyValue label="Qoldiq"><Money value={f.balance} /></KeyValue>
            <KeyValue label="Santexnikdagi naqd"><Money value={cashOutstanding(order.id, db.payments)} /></KeyValue>
            {order.status === 'cancelled' && <KeyValue label="Qaytarilishi kerak bo‘lgan avans"><Money value={f.refundDue} /></KeyValue>}
          </dl>
          <div className="panel-padding top-border inline-actions">
            <button className="button primary" disabled={order.dispute.open} onClick={() => setPaymentType(order.status === 'cancelled' ? 'refund' : 'advance')}><Plus size={16} />{order.status === 'cancelled' ? 'Avans qaytarishni qayd etish' : 'To‘lov qayd etish'}</button>
            <button className="button secondary" onClick={() => setPaymentType('cash_handover')}>Naqd pulni qabul qilish</button>
          </div>
        </Panel>
        <Panel title="Komissiya va hamkor hisob-kitobi" caption="Faqat admin ko‘rinishi · buyurtmadagi stavka nusxasi">
          <dl className="panel-padding">
            <KeyValue label={`Santexnik komissiyasi (${order.commissions.plumber ?? '—'}%)`}><Money value={f.plumberFee} /></KeyValue>
            <KeyValue label={`Do‘kon komissiyasi (${order.commissions.shop ?? '—'}%)`}><Money value={f.shopFee} /></KeyValue>
            <KeyValue label="Santexnikka sof / qoldiq"><Money value={f.plumberNet} /> / <Money value={f.plumberDue} /></KeyValue>
            <KeyValue label="Do‘konga sof / qoldiq"><Money value={f.shopNet} /> / <Money value={f.shopDue} /></KeyValue>
          </dl>
          <div className="panel-padding top-border inline-actions">
            <button className="button secondary" disabled={order.status !== 'completed' || order.dispute.open} onClick={() => setPaymentType('shop_settlement')}>Hamkorga hisob-kitob</button>
            <button className="button secondary" disabled={isClosed(order.status) || order.estimate.approved} onClick={configureAdvance}>Avansni sozlash</button>
          </div>
        </Panel>
      </div>
      <Panel title="Moliyaviy yozuvlar"><PaymentTable rows={db.payments.filter(p => p.orderId === order.id)} /></Panel>
      {paymentType && <PaymentDialog orderId={order.id} initialType={paymentType} onClose={() => setPaymentType(null)} />}
    </>
  );
}
