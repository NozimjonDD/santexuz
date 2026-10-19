import { Clock3, Plus } from 'lucide-react';
import type { Delivery, Order } from '../../domain/types';
import { isClosed } from '../../domain/rules';
import { dateTime, id } from '../../shared/format';
import { Badge, KeyValue, Notice, Panel } from '../../shared/ui';
import type { OrderActions } from './useOrderActions';

const inputDate = (value: string) => value ? new Date(new Date(value).getTime() + 5 * 3600000).toISOString().slice(0, 16) : '';
const fromInput = (value: unknown) => value ? `${String(value)}:00+05:00` : '';
function assertDeliveryEditable(order: Order) {
  if (!order.preparationStarted || isClosed(order.status) || order.dispute.open) {
    throw new Error('Yetkazish faqat tayyorlash boshlangan, ochiq va nizosiz buyurtmada yangilanadi.');
  }
}

export function ProcessPanel({ order, actions }: { order: Order; actions: OrderActions }) {
  const locked = isClosed(order.status) || order.dispute.open;

  function editSchedule() {
    actions.setForm({
      title: 'Vaqtlarni yangilash',
      fields: [
        { name: 'inspectionAt', label: 'Bepul ko‘rik vaqti (Toshkent)', type: 'datetime-local', required: true },
        { name: 'workStart', label: 'Taxminiy ish boshlanishi', type: 'datetime-local' },
        { name: 'workEnd', label: 'Taxminiy ish tugashi', type: 'datetime-local', validate: (value, values) => value && values.workStart && value < String(values.workStart) ? 'Tugash vaqti boshlanishdan keyin bo‘lsin.' : null },
        { name: 'reason', label: 'O‘zgarish sababi', type: 'textarea', required: true },
      ],
      initial: { inspectionAt: inputDate(order.inspectionAt), workStart: inputDate(order.workStart), workEnd: inputDate(order.workEnd) },
      submit: values => actions.update('Ko‘rik/ish vaqti yangilandi — demo xabarnoma', current => {
        if (isClosed(current.status) || current.dispute.open) throw new Error('Buyurtma tahrir uchun yopiq.');
        current.inspectionAt = fromInput(values.inspectionAt);
        current.workStart = fromInput(values.workStart);
        current.workEnd = fromInput(values.workEnd);
        current.etaReason = String(values.reason);
      }),
    });
  }

  function addDelivery() {
    actions.setForm({
      title: 'Yetkazish qismini qo‘shish',
      fields: [
        { name: 'label', label: 'Qism nomi', required: true },
        { name: 'eta', label: 'Taxminiy vaqt (Toshkent)', type: 'datetime-local', required: true },
        { name: 'note', label: 'Izoh', type: 'textarea', required: true },
      ],
      submit: values => actions.update('Yetkazish qismi qo‘shildi', current => {
        assertDeliveryEditable(current);
        if (current.workStarted) throw new Error('Ish boshlanganidan keyin yangi yetkazish qismi qo‘shilmaydi.');
        current.deliveries.push({ id: id('D'), label: String(values.label), eta: fromInput(values.eta), note: String(values.note), status: 'preparing' });
        if (current.deliveries.some(d => d.status === 'delivered')) current.status = 'partial';
        current.materialReceived = false;
      }),
    });
  }

  function editDelivery(delivery: Delivery) {
    actions.setForm({
      title: 'Yetkazish statusi va ETA',
      fields: [
        { name: 'status', label: 'Status', type: 'select', required: true, options: [{ value: 'preparing', label: 'Tayyorlanmoqda' }, { value: 'transit', label: 'Yo‘lda' }, { value: 'delivered', label: 'Yetkazildi' }] },
        { name: 'eta', label: 'Yangi ETA (Toshkent)', type: 'datetime-local', required: true },
        { name: 'note', label: 'Sabab / izoh', type: 'textarea', required: true },
      ],
      initial: { status: delivery.status, eta: inputDate(delivery.eta), note: delivery.note },
      submit: values => actions.update('Yetkazish/ETA yangilandi — demo xabarnoma', current => {
        assertDeliveryEditable(current);
        const item = current.deliveries.find(d => d.id === delivery.id);
        if (!item) throw new Error('Yetkazish qismi topilmadi.');
        if (item.status === 'delivered' && values.status !== 'delivered') throw new Error('Yetkazilgan qismni orqaga qaytarib bo‘lmaydi.');
        item.status = values.status as Delivery['status'];
        item.eta = fromInput(values.eta);
        item.note = String(values.note);
        const delivered = current.deliveries.filter(d => d.status === 'delivered').length;
        if (['preparing', 'transit', 'partial', 'delivered'].includes(current.status)) {
          current.status = delivered === current.deliveries.length ? 'delivered' : delivered > 0 ? 'partial' : current.deliveries.some(d => d.status === 'transit') ? 'transit' : 'preparing';
        }
      }),
    });
  }

  return (
    <div className="detail-columns">
      <div>
        <Panel title="Ko‘rik va ish vaqtlari" action={<button className="button secondary" disabled={locked || !order.plumberId} onClick={editSchedule}><Clock3 size={16} />Vaqtni belgilash</button>}>
          <dl className="panel-padding detail-grid">
            <KeyValue label="Ko‘rik">{dateTime(order.inspectionAt)}</KeyValue>
            <KeyValue label="Ish boshlanishi">{dateTime(order.workStart)}</KeyValue>
            <KeyValue label="Ish tugashi">{dateTime(order.workEnd)}</KeyValue>
            <KeyValue label="O‘zgarish sababi">{order.etaReason || '—'}</KeyValue>
          </dl>
        </Panel>
        <Panel title="Do‘kon tayyorlash vaqti" caption="Do‘kon qo‘lda kiritadigan namuna vaqt">
          <div className="panel-padding">
            <p>{order.preparationMinutes === null ? 'Tayyorlash vaqti belgilanmagan.' : `${order.preparationMinutes} daqiqa (demo)`}</p>
            <button className="button secondary" disabled={locked || !order.shopId} onClick={() => actions.setForm({
              title: 'Tayyorlash vaqtini belgilash',
              fields: [{ name: 'minutes', label: 'Tayyorlash vaqti (daqiqa)', type: 'number', min: 1, required: true }, { name: 'reason', label: 'Izoh / sabab', type: 'textarea', required: true }],
              initial: { minutes: order.preparationMinutes?.toString() ?? '' },
              submit: values => actions.update('Do‘kon tayyorlash vaqti yangilandi', current => { current.preparationMinutes = Number(values.minutes); current.etaReason = String(values.reason); }),
            })}>Vaqtni kiritish</button>
          </div>
        </Panel>
        <Panel title="Qisman yetkazishlar" caption="Yetkazish haqi bir marta olinadi. ETA — qo‘lda berilgan demo." action={<button className="button secondary" disabled={locked || !order.preparationStarted || order.workStarted} onClick={addDelivery}><Plus size={16} />Qism qo‘shish</button>}>
          <div className="panel-padding">
            {order.deliveries.map(delivery => (
              <div className="delivery-card" key={delivery.id}>
                <div className="section-row"><h3>{delivery.label}</h3><Badge tone={delivery.status === 'delivered' ? 'success' : 'warning'}>{delivery.status === 'delivered' ? 'Yetkazildi' : delivery.status === 'transit' ? 'Yo‘lda' : 'Tayyorlanmoqda'}</Badge></div>
                <p>{dateTime(delivery.eta)}</p>
                <p className="muted small">{delivery.note}</p>
                <button disabled={locked || !order.preparationStarted} className="button secondary" onClick={() => editDelivery(delivery)}>Status / ETA yangilash</button>
              </div>
            ))}
            {!order.deliveries.length && <p className="muted">Tayyorlash boshlangach yetkazish qismlarini qo‘shish mumkin.</p>}
            <Notice>Yo‘l ETA provayderi ulanmagan. Kuryerning jonli joylashuvi ko‘rsatilmaydi. Telegram xabari haqiqiy yuborilmaydi.</Notice>
          </div>
        </Panel>
      </div>
      <Panel title="Jarayon tarixi" caption="Muhim hodisalar · Toshkent vaqti">
        <ol className="timeline">
          {[...order.timeline].sort((a, b) => b.at.localeCompare(a.at)).map(event => (
            <li key={event.id}><span className="timeline-dot" /><time>{dateTime(event.at)}</time><strong>{event.title}</strong><p>{event.detail}</p></li>
          ))}
        </ol>
      </Panel>
    </div>
  );
}
