import { useState } from 'react';
import { useStore } from '../../app/store';
import type { Database, Order } from '../../domain/types';
import { id, now } from '../../shared/format';
import { ConfirmDialog, Modal, RecordForm, type Confirmation, type FieldSpec, type FormValues } from '../../shared/ui';

interface OrderForm { title: string; description?: string; fields: FieldSpec[]; initial?: FormValues; submitLabel?: string; submit: (values: FormValues) => void }
export function useOrderActions(orderId: string) {
  const { mutate, notify } = useStore();
  const [form, setForm] = useState<OrderForm | null>(null);
  const [confirm, setConfirm] = useState<Confirmation | null>(null);
  function update(summary: string, change: (order: Order, draft: Database) => void, action = 'Yangilash') {
    mutate({ action, objectType: 'Buyurtma', objectId: orderId, summary }, draft => {
      const order = draft.orders.find(o => o.id === orderId);
      if (!order) throw new Error('Buyurtma topilmadi.');
      const before = { status: order.status, estimateVersion: order.estimate.version, plumberId: order.plumberId, shopId: order.shopId };
      change(order, draft);
      order.timeline.unshift({ id: id('T'), at: now(), title: summary, detail: 'Demo administrator · lokal amal' });
      // Audit details include stable fields rather than copying private media.
      draft.audit.unshift({ id: id('DETAIL'), actor: 'Demo administrator', action: `${action} tafsiloti`, objectType: 'Buyurtma', objectId: orderId, timestamp: now(), summary, before, after: { status: order.status, estimateVersion: order.estimate.version, plumberId: order.plumberId, shopId: order.shopId } });
    });
  }
  return { update, setForm, setConfirm, notify, dialogs: <>{form && <Modal title={form.title} description={form.description ?? 'O‘zgarish faqat demo sessiyasida saqlanadi.'} onClose={() => setForm(null)} wide><RecordForm key={form.title} fields={form.fields} initial={form.initial} onCancel={() => setForm(null)} submitLabel={form.submitLabel} onSubmit={values => { form.submit(values); setForm(null); }} /></Modal>}{confirm && <ConfirmDialog value={confirm} onClose={() => setConfirm(null)} />}</> };
}
export type OrderActions = ReturnType<typeof useOrderActions>;
