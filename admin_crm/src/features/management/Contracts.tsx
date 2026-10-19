import { useState } from 'react';
import { Eye, FilePlus2, Plus } from 'lucide-react';
import { useStore } from '../../app/store';
import type { ContractTemplate } from '../../domain/types';
import { dateTime, id, now } from '../../shared/format';
import { Badge, ConfirmDialog, DataTable, Modal, Notice, PageHeader, Panel, RecordForm, SelectFilter, type Confirmation } from '../../shared/ui';

const labels = { draft: 'Qoralama', active: 'Faol', archived: 'Arxiv' };
export default function Contracts() {
  const { db, mutate } = useStore();
  const [editor, setEditor] = useState<ContractTemplate | 'new' | null>(null);
  const [preview, setPreview] = useState<ContractTemplate | null>(null);
  const [status, setStatus] = useState('');
  const [language, setLanguage] = useState('');
  const [confirm, setConfirm] = useState<Confirmation | null>(null);
  const activate = (template: ContractTemplate) => setConfirm({ title: 'Shartnoma versiyasini faollashtirish', description: `${template.name} · ${template.language} · v${template.version}. Shu nom va tildagi oldingi faol versiya arxivlanadi. Imzolangan buyurtmalar o‘zgarmaydi.`, action: () => mutate({ action: 'Faollashtirish', objectType: 'Shartnoma', objectId: template.id, summary: `v${template.version} ${template.language} faollashtirildi`, before: { status: template.status }, after: { status: 'active' } }, draft => {
    draft.templates.forEach(t => { if (t.name === template.name && t.language === template.language && t.status === 'active') t.status = 'archived'; });
    draft.templates.find(t => t.id === template.id)!.status = 'active';
  }) });
  return <><PageHeader eyebrow="BOSHQARUV" title="Shartnomalar" description="Versiyalanadigan andozalar va uch tildagi hujjat matnlari." actions={<button className="button primary" onClick={() => setEditor('new')}><Plus size={17} />Yangi andoza</button>} /><Notice>Matnlar demo. O‘zbekcha nusxa huquqiy ustuvor; ruscha va inglizcha nusxalar tarjima. Faol andozadan tahrir yangi versiya yaratadi.</Notice><Panel><div className="filter-bar"><SelectFilter label="Holat" value={status} onChange={setStatus} options={Object.entries(labels).map(([value, label]) => ({ value, label }))} /><SelectFilter label="Til" value={language} onChange={setLanguage} options={['UZ', 'RU', 'EN'].map(l => ({ value: l, label: l }))} /></div><DataTable rows={db.templates.filter(t => (!status || t.status === status) && (!language || t.language === language))} searchText={t => `${t.name} ${t.note} ${t.author}`} columns={[
    { key: 'name', label: 'Andoza nomi', sortValue: t => t.name, render: t => <div className="cell-stack"><strong>{t.name}</strong><small>{t.note}</small></div> },
    { key: 'language', label: 'Til', sortValue: t => t.language, render: t => <Badge tone="blue">{t.language}</Badge> },
    { key: 'version', label: 'Versiya', sortValue: t => t.version, render: t => `v${t.version}` },
    { key: 'status', label: 'Holat', sortValue: t => t.status, render: t => <Badge tone={t.status === 'active' ? 'success' : 'neutral'}>{labels[t.status]}</Badge> },
    { key: 'createdAt', label: 'Yaratilgan / muallif', sortValue: t => t.createdAt, render: t => <div className="cell-stack"><span>{dateTime(t.createdAt)}</span><small>{t.author}</small></div> },
    { key: 'actions', label: 'Amallar', render: t => <div className="row-actions"><button className="icon-button" aria-label={`${t.name} preview`} onClick={() => setPreview(t)}><Eye size={17} /></button><button className="icon-button" aria-label="Yangi versiya yaratish" onClick={() => setEditor(t)}><FilePlus2 size={17} /></button>{t.status === 'draft' && <button className="button secondary small-button" onClick={() => activate(t)}>Faollashtirish</button>}</div> },
  ]} /></Panel>{editor && <Modal title={editor === 'new' ? 'Yangi shartnoma andozasi' : 'Yangi versiya yaratish'} onClose={() => setEditor(null)} wide><RecordForm fields={[{ name: 'name', label: 'Andoza nomi', required: true }, { name: 'language', label: 'Til', type: 'select', required: true, options: ['UZ', 'RU', 'EN'] }, { name: 'note', label: 'Versiya izohi', required: true, full: true }, { name: 'text', label: 'Shartnoma matni', type: 'textarea', required: true, full: true }]} initial={editor === 'new' ? { language: 'UZ' } : { name: editor.name, language: editor.language, note: '', text: editor.text }} onCancel={() => setEditor(null)} submitLabel="Qoralama saqlash" onSubmit={values => {
    const name = String(values.name).trim();
    const version = Math.max(0, ...db.templates.filter(t => t.name === name && t.language === values.language).map(t => t.version)) + 1;
    const template: ContractTemplate = { id: id('CT'), name, language: String(values.language), version, note: String(values.note), text: String(values.text), status: 'draft', createdAt: now(), author: 'Demo administrator' };
    mutate({ action: 'Yangi versiya', objectType: 'Shartnoma', objectId: template.id, summary: `${name} v${version} qoralamasi`, after: template }, draft => { draft.templates.unshift(template); });
    setEditor(null); setPreview(template);
  }} /></Modal>}{preview && <Modal title={`${preview.name} · v${preview.version} · ${preview.language}`} onClose={() => setPreview(null)} wide><article className="document-preview"><div className="document-brand">SANTEX / DEMO</div><pre>{preview.text}</pre></article>{preview.status === 'draft' && <div className="form-actions"><button className="button primary" onClick={() => { setPreview(null); activate(preview); }}>Faol versiya qilish</button></div>}</Modal>}{confirm && <ConfirmDialog value={confirm} onClose={() => setConfirm(null)} />}</>;
}
