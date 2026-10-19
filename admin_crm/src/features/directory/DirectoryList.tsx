import { useMemo, useState } from 'react';
import { Link } from 'react-router';
import { Plus, Star } from 'lucide-react';
import type { EntityCollection } from '../../domain/types';
import { dateTime, inDateRange, includesQuery } from '../../shared/format';
import { Avatar, Badge, DataTable, DateRange, Money, PageHeader, Panel, SearchInput, SelectFilter, type Column } from '../../shared/ui';
import { directoryConfig } from './config';
import { emptyOrderSummary, fieldText, isCatalog, isPartner, pathFor, type DirectoryRow, type OrderSummary } from './model';

interface DirectoryListProps {
  kind: EntityCollection;
  rows: DirectoryRow[];
  orderSummaries: Map<string, OrderSummary>;
  ratings: Map<string, string>;
  onCreate: () => void;
  onEdit: (row: DirectoryRow) => void;
  onToggle: (row: DirectoryRow) => void;
}

type DirectoryColumnProps = Pick<DirectoryListProps, 'kind' | 'orderSummaries' | 'ratings' | 'onEdit' | 'onToggle'>;

function directoryColumns({ kind, orderSummaries, ratings, onEdit, onToggle }: DirectoryColumnProps): Column<DirectoryRow>[] {
  const summary = (row: DirectoryRow) => orderSummaries.get(row.id) ?? emptyOrderSummary;
  const columns: Column<DirectoryRow>[] = [{
    key: 'name', label: isCatalog(kind) ? 'Nomi' : kind === 'shops' ? 'Do‘kon' : 'Ism-familiya',
    sortValue: row => row.name,
    render: row => (
      <div className="person">
        {!isCatalog(kind) && <Avatar name={row.name} small />}
        <div>
          <Link className="text-link" to={`${pathFor(kind)}/${row.id}`}>{row.name}</Link>
          <small>{isCatalog(kind) ? row.category : row.phone}</small>
        </div>
      </div>
    ),
  }];

  if (!isCatalog(kind)) columns.push({
    key: 'telegram', label: 'Telegram',
    render: row => (
      <div className="cell-stack">
        <Badge tone={row.telegramId ? 'blue' : 'neutral'}>{row.telegramId ? 'Demo bog‘langan' : 'Bog‘lanmagan'}</Badge>
        {kind === 'shops' && <small>Bitta umumiy akkaunt</small>}
      </div>
    ),
  });

  if (kind === 'customers') columns.push(
    { key: 'orders', label: 'Buyurtmalar', sortValue: row => summary(row).orders.length, render: row => `${summary(row).orders.length} ta` },
    { key: 'last', label: 'Oxirgi buyurtma', sortValue: row => summary(row).lastOrderAt, render: row => dateTime(summary(row).lastOrderAt) },
    { key: 'spent', label: 'Umumiy to‘lov', className: 'numeric', sortValue: row => summary(row).paid, render: row => <Money value={summary(row).paid} /> },
    { key: 'createdAt', label: 'Ro‘yxatdan o‘tgan', sortValue: row => row.createdAt ?? '', render: row => <span className="small nowrap">{dateTime(row.createdAt)}</span> },
  );

  if (isPartner(kind)) columns.push(
    {
      key: 'district', label: 'Hudud / yo‘nalish', sortValue: row => row.district ?? '',
      render: row => <div className="cell-stack"><span>{row.district}</span><small>{kind === 'plumbers' ? row.categories?.join(', ') : row.address}</small></div>,
    },
    {
      key: 'rating', label: 'Reyting', sortValue: row => Number(ratings.get(row.id)) || 0,
      render: row => <span className="rating"><Star size={14} aria-hidden="true" />{ratings.get(row.id) ?? '—'}</span>,
    },
    {
      key: 'work', label: kind === 'plumbers' ? 'Faol buyurtma' : 'Qabul / rad',
      sortValue: row => summary(row).active,
      render: row => kind === 'plumbers' ? `${summary(row).active} ta` : `${summary(row).accepted} / ${summary(row).rejected}`,
    },
    {
      key: 'commission', label: 'Komissiya', sortValue: row => row.commission ?? -1,
      render: row => row.commission == null ? 'Standart / sozlanmagan' : `${row.commission}% (demo)`,
    },
  );

  if (kind === 'services') columns.push(
    { key: 'unit', label: 'Birlik', sortValue: row => row.unit ?? '', render: row => row.unit },
    { key: 'areaRate', label: 'Marhamat tarifi', className: 'numeric', sortValue: row => row.areaRate ?? -1, render: row => <Money value={row.areaRate} /> },
    { key: 'emergencyFee', label: 'Shoshilinch haq', className: 'numeric', render: row => <Money value={row.emergencyFee} /> },
    {
      key: 'warranty', label: 'Kafolat / ko‘rinish',
      render: row => <div className="cell-stack"><span>{row.warranty || 'Belgilanmagan'}</span><small>{row.visible ? 'Mijozga ko‘rinadi' : 'Yashirilgan'}</small></div>,
    },
  );

  if (kind === 'materials') columns.push(
    { key: 'brand', label: 'Marka / model', sortValue: row => row.brand ?? '', render: row => row.brand || '—' },
    { key: 'size', label: 'O‘lcham', sortValue: row => row.size ?? '', render: row => row.size || '—' },
    { key: 'unit', label: 'Birlik', sortValue: row => row.unit ?? '', render: row => row.unit },
  );

  if (kind !== 'customers') columns.push({
    key: 'active', label: 'Holati', sortValue: row => row.isActive ? 1 : 0,
    render: row => <Badge tone={row.isActive ? 'success' : 'neutral'}>{row.isActive ? 'Faol' : 'Nofaol'}</Badge>,
  });

  columns.push({
    key: 'actions', label: 'Amallar',
    render: row => (
      <details className="row-menu">
        <summary aria-label={`${row.name} amallari`}>•••</summary>
        <div>
          <Link to={`${pathFor(kind)}/${row.id}`}>Ko‘rish</Link>
          <button onClick={() => onEdit(row)}>Tahrirlash</button>
          {kind !== 'customers' && <button onClick={() => onToggle(row)}>{row.isActive ? 'Nofaol qilish' : 'Faol qilish'}</button>}
        </div>
      </details>
    ),
  });
  return columns;
}

export function DirectoryList(props: DirectoryListProps) {
  const { kind, rows: all, orderSummaries, ratings, onCreate, onEdit, onToggle } = props;
  const config = directoryConfig[kind];
  const [query, setQuery] = useState('');
  const [group, setGroup] = useState('');
  const [active, setActive] = useState('');
  const [special, setSpecial] = useState('');
  const [range, setRange] = useState({ from: '', to: '' });

  const { groups, activeCount, searchableRows } = useMemo(() => {
    const groups = new Set<string>();
    let activeCount = 0;
    const searchableRows = all.map(row => {
      if (row.isActive) activeCount += 1;
      for (const group of row.categories ?? (row.category ? [row.category] : [])) groups.add(group);
      return { row, search: Object.values(row).join(' ') };
    });
    return { groups: Array.from(groups, group => ({ value: group, label: group })), activeCount, searchableRows };
  }, [all]);

  const rows = useMemo(() => searchableRows.filter(({ row, search }) => {
    if (!includesQuery(search, query)) return false;
    if (group && row.category !== group && !row.categories?.includes(group)) return false;
    if (active && row.isActive !== (active === 'yes')) return false;
    if (special) {
      if (kind === 'services' && (row.areaRate != null) !== (special === 'set')) return false;
      if (kind === 'customers' && (orderSummaries.has(row.id)) !== (special === 'yes')) return false;
      if (isPartner(kind) && !!row.telegramId !== (special === 'yes')) return false;
    }
    return kind !== 'customers' || inDateRange(fieldText(row, 'createdAt'), range.from, range.to);
  }).map(({ row }) => row), [searchableRows, query, group, active, special, kind, orderSummaries, range.from, range.to]);

  const columns = useMemo(() => directoryColumns({ kind, orderSummaries, ratings, onEdit, onToggle }),
    [kind, orderSummaries, ratings, onEdit, onToggle]);

  return <>
    <PageHeader
      eyebrow={isPartner(kind) || kind === 'customers' ? 'HAMKORLAR' : 'KATALOG'}
      title={config.title}
      description={config.description}
      actions={<button className="button primary" onClick={onCreate}><Plus size={18} aria-hidden="true" />Yangi {config.singular}</button>}
    />
    <div className="directory-summary">
      <span><strong>{all.length}</strong> jami {config.singular}</span>
      {kind !== 'customers' && <span><i className="stat-dot success" /><strong>{activeCount}</strong> faol</span>}
      <Badge tone="blue">Marhamat pilot · DEMO</Badge>
    </div>
    <Panel>
      <div className="filter-bar">
        <SearchInput value={query} onChange={setQuery} placeholder="Nom, telefon yoki boshqa ma’lumot…" />
        {(kind === 'plumbers' || isCatalog(kind)) && <SelectFilter label="Guruh" value={group} onChange={setGroup} options={groups} />}
        {kind !== 'customers' && <SelectFilter label="Holat" value={active} onChange={setActive} options={[{ value: 'yes', label: 'Faol' }, { value: 'no', label: 'Nofaol' }]} />}
        {kind !== 'materials' && <SelectFilter
          label={kind === 'services' ? 'Tarif' : kind === 'customers' ? 'Buyurtmasi' : 'Telegram'}
          value={special}
          onChange={setSpecial}
          options={kind === 'services' ? [{ value: 'set', label: 'Kiritilgan' }, { value: 'unset', label: 'Sozlanmagan' }] : [{ value: 'yes', label: 'Bor' }, { value: 'no', label: 'Yo‘q' }]}
        />}
      </div>
      {kind === 'customers' && <div className="list-date-row"><span>Ro‘yxatdan o‘tgan sana</span><DateRange {...range} onChange={(from, to) => setRange({ from, to })} /></div>}
      <DataTable rows={rows} columns={columns} />
    </Panel>
  </>;
}
