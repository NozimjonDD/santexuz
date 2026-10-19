import { useEffect, useId, useRef, type ReactNode } from 'react';
import { AlertTriangle, Inbox, Search, X } from 'lucide-react';
import { statusLabels, type OrderStatus } from '../../domain/types';
import { money } from '../format';

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: string }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

export function StatusBadge({ status }: { status: OrderStatus }) {
  const tone = status === 'dispute' ? 'danger'
    : status === 'completed' ? 'success'
      : ['cancelled', 'rejected'].includes(status) ? 'neutral'
        : ['preparing', 'partial', 'transit', 'delivered', 'working', 'completion'].includes(status) ? 'warning' : 'blue';
  return <Badge tone={tone}><i aria-hidden="true" />{statusLabels[status]}</Badge>;
}

export function Money({ value }: { value: number | null | undefined }) {
  return <span className={`money ${value == null ? 'muted' : ''}`}>{money(value)}</span>;
}

export function PageHeader({ title, description, actions, eyebrow }: {
  title: string; description: string; actions?: ReactNode; eyebrow?: string;
}) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus({ preventScroll: true }); }, [title]);
  return (
    <header className="page-header">
      <div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1 ref={heading} tabIndex={-1}>{title}</h1><p>{description}</p></div>
      {actions && <div className="header-actions">{actions}</div>}
    </header>
  );
}

export function Panel({ title, caption, action, children, className = '' }: {
  title?: string; caption?: string; action?: ReactNode; children: ReactNode; className?: string;
}) {
  const headingId = useId();
  return (
    <section className={`panel ${className}`} aria-labelledby={title ? headingId : undefined}>
      {title && <div className="panel-header"><div><h2 id={headingId}>{title}</h2>{caption && <p>{caption}</p>}</div>{action}</div>}
      {children}
    </section>
  );
}

export function EmptyState({ title = 'Natija topilmadi', text = 'Qidiruv yoki filtrlarni o‘zgartirib ko‘ring.', action }: {
  title?: string; text?: string; action?: ReactNode;
}) {
  return <div className="empty-state"><span className="empty-icon"><Inbox size={25} aria-hidden="true" /></span><h3>{title}</h3><p>{text}</p>{action}</div>;
}

export function Notice({ children, danger = false }: { children: ReactNode; danger?: boolean }) {
  return <div className={`notice ${danger ? 'danger' : ''}`} role="note"><AlertTriangle size={17} aria-hidden="true" /><div>{children}</div></div>;
}

export function Tabs({ items, value, onChange }: {
  items: { value: string; label: string; count?: number }[]; value: string; onChange: (value: string) => void;
}) {
  return (
    <div className="tabs" role="group" aria-label="Bo‘lim tanlash">
      {items.map(item => <button type="button" key={item.value} aria-pressed={value === item.value} className={value === item.value ? 'active' : ''} onClick={() => onChange(item.value)}>{item.label}{item.count !== undefined && <span>{item.count}</span>}</button>)}
    </div>
  );
}

export function StatCard({ label, value, detail, icon, onClick }: {
  label: string; value: ReactNode; detail: ReactNode; icon: ReactNode; onClick?: () => void;
}) {
  const content = <><div className="stat-top"><span>{label}</span><span className="stat-icon" aria-hidden="true">{icon}</span></div><div className="stat-value">{value}</div><div className="stat-detail">{detail}</div></>;
  return onClick ? <button type="button" className="stat-card" onClick={onClick}>{content}</button> : <div className="stat-card">{content}</div>;
}

export function SearchInput({ value, onChange, label = 'Qidirish', placeholder = 'Qidirish…' }: {
  value: string; onChange: (value: string) => void; label?: string; placeholder?: string;
}) {
  const inputId = useId();
  return (
    <div className="search-field">
      <Search size={17} aria-hidden="true" /><label className="sr-only" htmlFor={inputId}>{label}</label>
      <input id={inputId} type="search" value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
      {value && <button type="button" className="search-clear" aria-label="Qidiruvni tozalash" onClick={() => { onChange(''); document.getElementById(inputId)?.focus(); }}><X size={15} aria-hidden="true" /></button>}
    </div>
  );
}

export function SelectFilter({ label, value, options, onChange }: {
  label: string; value: string; options: { value: string; label: string }[]; onChange: (value: string) => void;
}) {
  return <label className="filter-select"><span>{label}</span><select value={value} onChange={e => onChange(e.target.value)}><option value="">Barchasi</option>{options.map(o => <option value={o.value} key={o.value}>{o.label}</option>)}</select></label>;
}

export function DateRange({ from, to, onChange }: { from: string; to: string; onChange: (from: string, to: string) => void }) {
  return <div className="date-range"><label><span>Boshlanish</span><input type="date" value={from} max={to || undefined} onChange={e => onChange(e.target.value, to)} /></label><span aria-hidden="true">—</span><label><span>Tugash</span><input type="date" min={from || undefined} value={to} onChange={e => onChange(from, e.target.value)} /></label></div>;
}

export function Avatar({ name, small = false }: { name: string; small?: boolean }) {
  return <span className={`avatar ${small ? 'small' : ''}`} aria-hidden="true">{name.trim().split(/\s+/).slice(0, 2).map(s => s[0]).join('')}</span>;
}

export function KeyValue({ label, children }: { label: string; children: ReactNode }) {
  return <div className="key-value"><dt>{label}</dt><dd>{children}</dd></div>;
}

export function FilePreview({ label, kind = 'photo' }: { label: string; kind?: 'photo' | 'pdf' }) {
  return <div className="file-preview" role="img" aria-label={label}><span>{kind === 'pdf' ? 'PDF' : 'MEDIA'}</span><strong>{label}</strong><small>Statik namuna · fayl yuklanmagan</small></div>;
}
