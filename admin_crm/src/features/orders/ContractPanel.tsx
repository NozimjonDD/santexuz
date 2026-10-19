import { useState } from 'react';
import { FileText, Check, Eye } from 'lucide-react';
import { useStore } from '../../app/store';
import type { Order } from '../../domain/types';
import { dateTime, now } from '../../shared/format';
import { Badge, KeyValue, Modal, Notice, Panel } from '../../shared/ui';
import type { OrderActions } from './useOrderActions';

export function ContractPanel({ order, actions }: { order: Order; actions: OrderActions }) {
  const { db } = useStore();
  const [preview, setPreview] = useState<string | null>(null);
  const parties = ['Mijoz', 'Santexnik', 'Do‘kon vakili', 'Xizmat markazi vakili'];
  function bindTemplate() {
    actions.setForm({ title: 'Shartnoma andozasini tanlash', fields: [{ name: 'template', label: 'Faol andoza', type: 'select', required: true, options: db.templates.filter(t => t.status === 'active').map(t => ({ value: t.id, label: `${t.name} · ${t.language} · v${t.version}` })) }], submit: values => actions.update('Shartnoma andozasi nusxalandi', (current, draft) => {
      if (current.contract.signedAt) throw new Error('Imzolangan nusxani o‘zgartirib bo‘lmaydi.');
      const template = draft.templates.find(t => t.id === values.template && t.status === 'active');
      if (!template) throw new Error('Faol andoza topilmadi.');
      current.contract = { templateId: template.id, version: template.version, language: template.language, text: template.text, signatures: [false, false, false, false], signedAt: null, signedBy: null };
    }) });
  }
  return <Panel title="Shartnoma" caption="Qog‘ozdagi imzolarni qayd etish · statik hujjat" action={<Badge tone={order.contract.signedAt ? 'success' : 'warning'}>{order.contract.signedAt ? 'Demo imzolangan' : 'Imzolar kutilmoqda'}</Badge>}><div className="panel-padding"><Notice>Bu andoza yuridik hujjat emas. O‘zbekcha matn ustuvor; RU va EN nusxalari tarjima. Haqiqiy PDF yaratish backendga ulanadi.</Notice><dl className="detail-grid"><KeyValue label="Andoza / versiya">{order.contract.templateId || 'Tanlanmagan'} · v{order.contract.version}</KeyValue><KeyValue label="Til">{order.contract.language}</KeyValue><KeyValue label="Qayd qilgan xodim">{order.contract.signedBy ?? 'Kutilmoqda'}</KeyValue><KeyValue label="Imzolangan vaqt">{dateTime(order.contract.signedAt)}</KeyValue></dl><div className="signature-grid">{parties.map((party, i) => <div key={party} className={order.contract.signatures[i] ? 'signed' : ''}><span>{order.contract.signatures[i] ? <Check size={18} /> : i + 1}</span><strong>{party}</strong><small>{order.contract.signatures[i] ? 'Imzo qayd etilgan (demo)' : 'Imzo kutilmoqda'}</small></div>)}</div><div className="inline-actions"><button className="button secondary" disabled={!order.contract.text} onClick={() => setPreview(order.contract.text)}><Eye size={16} />PDF statik preview</button>{!order.contract.signedAt && !['cancelled', 'completed'].includes(order.status) && <><button className="button secondary" onClick={bindTemplate}><FileText size={16} />Andoza tanlash</button><button className="button primary" disabled={!order.estimate.approved || !order.contract.text || order.dispute.open} onClick={() => actions.setForm({ title: 'To‘rt tomon imzosini qayd etish', description: 'Qog‘oz hujjatdagi imzolar tekshirilganini faqat demo sifatida qayd eting.', fields: parties.map((party, i) => ({ name: `party${i}`, label: `${party} qog‘oz nusxani imzolagan (demo)`, type: 'checkbox', required: true })), submit: () => actions.setConfirm({ title: 'Shartnomani imzolangan deb belgilash', description: 'To‘rt tomonning qog‘oz imzolari lokal qayd etiladi. Imzolangan nusxa o‘zgarmasdan saqlanadi.', action: () => actions.update('To‘rt tomon imzosi demo qayd etildi', current => {
        if (!current.estimate.approved || current.dispute.open) throw new Error('Smeta tasdiqlanmagan yoki nizo ochiq.');
        current.contract.signatures = [true, true, true, true]; current.contract.signedAt = now(); current.contract.signedBy = 'Demo administrator';
      }) }) })}>Imzolandi deb qayd etish</button></>}</div>{order.contractHistory?.length ? <div className="history-list"><h3>Oldingi imzolangan nusxalar</h3>{order.contractHistory.map((c, i) => <button className="history-row button ghost" key={i} onClick={() => setPreview(c.text)}>{c.templateId} · v{c.version} · {dateTime(c.signedAt)}<Eye size={15} /></button>)}</div> : null}</div>{preview !== null && <Modal title="Shartnoma · statik PDF ko‘rinishi" description="Haqiqiy PDF fayl yaratilmagan. Matn buyurtmadagi saqlangan nusxadan olingan." onClose={() => setPreview(null)} wide><article className="document-preview"><div className="document-brand">SANTEX / DEMO</div><h3>Xizmat ko‘rsatish shartnomasi</h3><p>{order.id} · {order.contract.language}</p><pre>{preview}</pre><div className="signature-grid">{parties.map(p => <div key={p}>{p}<hr />Imzo / sana</div>)}</div></article></Modal>}</Panel>;
}
