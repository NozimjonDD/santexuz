import { useDeferredValue, useEffect, useMemo, useState, type ReactNode } from 'react';
import { ArrowDown, ArrowUp, ArrowUpDown, ChevronLeft, ChevronRight, LoaderCircle } from 'lucide-react';
import { includesQuery } from '../format';
import { EmptyState, SearchInput } from './primitives';

export interface Column<T> {
  key: string; label: string; render: (row: T) => ReactNode;
  sortValue?: (row: T) => string | number; className?: string;
}
interface DataTableProps<T> {
  rows: T[]; columns: Column<T>[]; searchText?: (row: T) => string; emptyText?: string;
  loading?: boolean; error?: string; onRetry?: () => void; onRowOpen?: (row: T) => void;
  caption?: string;
}
const collator = new Intl.Collator('uz', { numeric: true, sensitivity: 'base' });

export function DataTable<T extends { id: string }>({
  rows, columns, searchText, emptyText, loading, error, onRetry, onRowOpen, caption = 'Ma’lumotlar jadvali',
}: DataTableProps<T>) {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [sort, setSort] = useState({ key: '', direction: 1 });
  const membership = rows.map(row => row.id).join('\u001f');

  // Reset on changed results, not on a newly allocated array with the same rows.
  useEffect(() => { setPage(1); }, [membership, deferredQuery, size]);
  const filtered = useMemo(() => searchText ? rows.filter(row => includesQuery(searchText(row), deferredQuery)) : rows, [rows, searchText, deferredQuery]);
  const sortValue = columns.find(column => column.key === sort.key)?.sortValue;
  const sorted = useMemo(() => sortValue ? [...filtered].sort((a, b) => {
    const av = sortValue(a), bv = sortValue(b);
    return (typeof av === 'number' && typeof bv === 'number' ? av - bv : collator.compare(String(av), String(bv))) * sort.direction;
  }) : filtered, [filtered, sortValue, sort.direction]);
  const pages = Math.max(1, Math.ceil(sorted.length / size));
  const currentPage = Math.min(page, pages);
  const visible = sorted.slice((currentPage - 1) * size, currentPage * size);

  if (loading) return <div className="empty-state" role="status"><LoaderCircle className="spin" aria-hidden="true" />Ma’lumot yuklanmoqda…</div>;
  if (error) return <EmptyState title="Ma’lumotni ko‘rsatib bo‘lmadi" text={error} action={onRetry && <button type="button" className="button secondary" onClick={onRetry}>Qayta urinish</button>} />;

  return (
    <div className="data-table" aria-busy={query !== deferredQuery}>
      {searchText && <div className="table-search"><SearchInput value={query} onChange={setQuery} /></div>}
      <div className="table-scroll" tabIndex={0} role="region" aria-label={caption}>
        <table>
          <caption className="sr-only">{caption}</caption>
          <thead><tr>{columns.map(column => (
            <th key={column.key} scope="col" className={column.className} aria-sort={sort.key === column.key ? sort.direction === 1 ? 'ascending' : 'descending' : undefined}>
              {column.sortValue ? <button type="button" onClick={() => { setSort(previous => ({ key: column.key, direction: previous.key === column.key ? -previous.direction : 1 })); setPage(1); }}>{column.label}{sort.key === column.key ? sort.direction === 1 ? <ArrowUp size={13} aria-hidden="true" /> : <ArrowDown size={13} aria-hidden="true" /> : <ArrowUpDown size={12} aria-hidden="true" />}</button> : column.label}
            </th>
          ))}</tr></thead>
          <tbody>{visible.map(row => (
            <tr key={row.id} tabIndex={onRowOpen ? 0 : undefined} className={onRowOpen ? 'clickable-row' : undefined}
              onClick={event => { if (onRowOpen && !(event.target as Element).closest('a, button, input, select, textarea, label, details, summary')) onRowOpen(row); }}
              onKeyDown={event => { if (onRowOpen && event.target === event.currentTarget && event.key === 'Enter') onRowOpen(row); }}>
              {columns.map(column => <td key={column.key} className={column.className}>{column.render(row)}</td>)}
            </tr>
          ))}</tbody>
        </table>
      </div>
      {!visible.length && <EmptyState text={emptyText} action={query ? <button type="button" className="button secondary" onClick={() => setQuery('')}>Qidiruvni tozalash</button> : undefined} />}
      <div className="table-footer">
        <span className="table-results-count" role="status">{filtered.length ? `${(currentPage - 1) * size + 1}–${Math.min(currentPage * size, filtered.length)}` : '0'} / {filtered.length} ta yozuv</span>
        <div className="table-controls">
          <label className="page-size"><span>Sahifada</span><select aria-label="Sahifadagi qatorlar" value={size} onChange={event => setSize(Number(event.target.value))}>{[5, 10, 20, 50].map(value => <option key={value}>{value}</option>)}</select></label>
          <div className="table-pagination" role="group" aria-label="Jadval sahifalari">
            <button type="button" className="icon-button" aria-label="Oldingi sahifa" disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}><ChevronLeft size={17} aria-hidden="true" /></button>
            <span className="table-page-indicator" aria-label={`${currentPage}-sahifa, jami ${pages}`}>{currentPage} / {pages}</span>
            <button type="button" className="icon-button" aria-label="Keyingi sahifa" disabled={currentPage === pages} onClick={() => setPage(currentPage + 1)}><ChevronRight size={17} aria-hidden="true" /></button>
          </div>
        </div>
      </div>
    </div>
  );
}
