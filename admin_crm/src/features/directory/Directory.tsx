import { useCallback, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router';
import { useStore } from '../../app/store';
import type { EntityCollection } from '../../domain/types';
import { ConfirmDialog, EmptyState, type Confirmation } from '../../shared/ui';
import { directoryConfig } from './config';
import { DirectoryEditor } from './DirectoryEditor';
import { DirectoryList } from './DirectoryList';
import { DirectoryProfile } from './DirectoryProfile';
import { emptyOrderSummary, indexDirectoryOrders, indexDirectoryRatings, pathFor, setDirectoryActive, type DirectoryRow } from './model';

export default function Directory({ kind }: { kind: EntityCollection }) {
  const { db, mutate } = useStore();
  const { id: selectedId } = useParams();
  const config = directoryConfig[kind];
  const all: DirectoryRow[] = db[kind];
  const [editing, setEditing] = useState<DirectoryRow | 'new' | null>(null);
  const [confirmation, setConfirmation] = useState<Confirmation | null>(null);

  const selected = useMemo(() => all.find(row => row.id === selectedId), [all, selectedId]);
  const orderSummaries = useMemo(() => indexDirectoryOrders(kind, db.orders, db.payments), [kind, db.orders, db.payments]);
  const ratings = useMemo(() => indexDirectoryRatings(db.reviews), [db.reviews]);
  const create = useCallback(() => setEditing('new'), []);
  const edit = useCallback((row: DirectoryRow) => setEditing(row), []);
  const closeEditor = useCallback(() => setEditing(null), []);

  const toggle = useCallback((row: DirectoryRow) => {
    const isActive = !row.isActive;
    setConfirmation({
      title: isActive ? 'Faol holatni yoqish' : 'Faol holatni o‘chirish',
      description: `${row.name}. Eski buyurtmalar va ularning narxlari saqlanadi.`,
      danger: !isActive,
      action: () => mutate({
        action: 'Holat', objectType: config.title, objectId: row.id,
        summary: `${row.name} · ${isActive ? 'faol' : 'nofaol'}`,
        before: { isActive: row.isActive }, after: { isActive },
      }, draft => setDirectoryActive(draft, kind, row.id, isActive)),
    });
  }, [config.title, kind, mutate]);

  return <>
    {selectedId ? selected ? (
      <DirectoryProfile
        key={`${kind}/${selected.id}`}
        kind={kind}
        row={selected}
        orders={(orderSummaries.get(selected.id) ?? emptyOrderSummary).orders}
        db={db}
        onEdit={edit}
      />
    ) : <EmptyState title="Profil topilmadi" action={<Link to={pathFor(kind)}>Ro‘yxatga qaytish</Link>} /> : (
      <DirectoryList
        key={kind}
        kind={kind}
        rows={all}
        orderSummaries={orderSummaries}
        ratings={ratings}
        onCreate={create}
        onEdit={edit}
        onToggle={toggle}
      />
    )}
    {editing && <DirectoryEditor kind={kind} row={editing} onClose={closeEditor} onConfirm={setConfirmation} />}
    {confirmation && <ConfirmDialog value={confirmation} onClose={() => setConfirmation(null)} />}
  </>;
}
