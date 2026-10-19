import { useStore } from '../../app/store';
import type { EntityCollection } from '../../domain/types';
import { id, money } from '../../shared/format';
import { Modal, RecordForm, type Confirmation, type FormValues } from '../../shared/ui';
import { directoryConfig } from './config';
import { applyDirectoryChange, directoryFormValues, normalizeDirectoryChange, type DirectoryRow } from './model';

interface DirectoryEditorProps {
  kind: EntityCollection;
  row: DirectoryRow | 'new';
  onClose: () => void;
  onConfirm: (confirmation: Confirmation) => void;
}

export function DirectoryEditor({ kind, row, onClose, onConfirm }: DirectoryEditorProps) {
  const { mutate } = useStore();
  const config = directoryConfig[kind];
  const previous = row === 'new' ? null : row;
  const initial = previous ? directoryFormValues(previous, config.fields) : config.initial;

  function save(values: FormValues) {
    const entityId = previous?.id ?? id(config.prefix);
    const change = normalizeDirectoryChange(kind, values, previous, entityId);
    const commit = () => mutate({
      action: previous ? 'Tahrirlash' : 'Yaratish', objectType: config.title, objectId: entityId,
      summary: `${change.entity.name} · demo ${previous ? 'tahrir' : 'yaratish'}`, before: previous, after: change.entity,
    }, draft => applyDirectoryChange(draft, change));

    const rateChanged = change.kind === 'services' && previous?.areaRate !== change.entity.areaRate;
    const commissionChanged = (change.kind === 'plumbers' || change.kind === 'shops') && previous?.commission !== change.entity.commission;
    if (rateChanged || commissionChanged) {
      const nextValue = change.kind === 'services' ? money(change.entity.areaRate)
        : change.kind === 'plumbers' || change.kind === 'shops' ? `${change.entity.commission ?? 'sozlanmagan'}%` : '';
      const oldValue = change.kind === 'services' ? money(previous?.areaRate) : `${previous?.commission ?? 'sozlanmagan'}%`;
      onConfirm({
        title: rateChanged ? 'Tarifni o‘zgartirish' : 'Komissiyani o‘zgartirish',
        description: 'Yangi narx/stavka faqat yangi smeta va keyingi tayinlashlarga qo‘llanadi. Eski va tasdiqlangan buyurtmalar o‘zgarmaydi.',
        details: <div className="change-preview"><span>Oldingi: {oldValue}</span><strong>Yangi: {nextValue}</strong></div>,
        action: commit,
      });
    } else commit();
    onClose();
  }

  return <Modal
    title={`${previous ? 'Tahrirlash:' : 'Yangi'} ${config.singular}`}
    description="Faqat demo ma’lumotlar. Amallar audit jurnaliga yoziladi."
    onClose={onClose}
    wide
  >
    <RecordForm fields={config.fields} initial={initial} onCancel={onClose} onSubmit={save} />
  </Modal>;
}
