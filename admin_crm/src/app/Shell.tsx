import { Suspense, useEffect, useMemo, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from 'react';
import { NavLink, Link, Outlet, useLocation } from 'react-router';
import { Activity, Bell, BookOpen, ChevronDown, ChevronRight, ClipboardList, Droplets, FileText, LayoutDashboard, MapPin, Menu, Package, Search, Settings, ShieldCheck, Star, Store, Users, Wallet, Wrench, RotateCcw, FlaskConical } from 'lucide-react';
import { useStore } from './store';
import { Avatar, Badge, ConfirmDialog, Modal, SearchInput, type Confirmation } from '../shared/ui';
import { includesQuery } from '../shared/format';

export const navigation = [
  { group: 'ISH JARAYONI', links: [{ to: '/dashboard', label: 'Bosh sahifa', icon: LayoutDashboard }, { to: '/orders', label: 'Buyurtmalar', icon: ClipboardList }] },
  { group: 'HAMKORLAR', links: [{ to: '/customers', label: 'Mijozlar', icon: Users }, { to: '/plumbers', label: 'Santexniklar', icon: Wrench }, { to: '/shops', label: 'Do‘konlar', icon: Store }] },
  { group: 'KATALOG VA MOLIYA', links: [{ to: '/catalog/services', label: 'Xizmatlar katalogi', icon: BookOpen }, { to: '/catalog/materials', label: 'Materiallar', icon: Package }, { to: '/finance', label: 'Moliya', icon: Wallet }, { to: '/reports', label: 'Hisobotlar', icon: Activity }] },
  { group: 'BOSHQARUV', links: [{ to: '/contracts', label: 'Shartnomalar', icon: FileText }, { to: '/reviews', label: 'Reytinglar', icon: Star }, { to: '/audit', label: 'Audit jurnali', icon: ShieldCheck }, { to: '/settings', label: 'Sozlamalar', icon: Settings }] },
];
interface SearchResult { label: string; detail: string; to: string }
function SearchResults({ results, hasQuery, onSelect }: { results: SearchResult[]; hasQuery: boolean; onSelect: () => void }) {
  return <><span className="eyebrow">QIDIRUV NATIJALARI</span><span className="sr-only" role="status">{hasQuery ? `${results.length} ta natija ko‘rsatilmoqda` : 'Qidirish uchun matn kiriting'}</span>{results.length ? results.map(r => (
    <Link key={r.to} to={r.to} onClick={onSelect}><span><strong>{r.label}</strong><small>{r.detail}</small></span><ChevronRight size={15} /></Link>
  )) : <p className="search-empty">{hasQuery ? 'Natija topilmadi. Boshqa so‘z yoki raqam kiriting.' : 'Buyurtma raqami, ism yoki telefon orqali qidiring.'}</p>}</>;
}

function moveSearchFocus(event: ReactKeyboardEvent<HTMLDivElement>) {
  if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
  const links = Array.from(event.currentTarget.querySelectorAll<HTMLAnchorElement>('a'));
  if (!links.length) return;
  event.preventDefault();
  const current = links.findIndex(link => link === document.activeElement);
  const next = current < 0 ? (event.key === 'ArrowDown' ? 0 : links.length - 1) : current + (event.key === 'ArrowDown' ? 1 : -1);
  links[(next + links.length) % links.length]?.focus();
}

export default function Shell() {
  const { db, reset } = useStore();
  const location = useLocation();
  const [mobile, setMobile] = useState(false);
  const [query, setQuery] = useState('');
  const [popup, setPopup] = useState<'notifications' | 'profile' | 'search' | null>(null);
  const [confirm, setConfirm] = useState<Confirmation | null>(null);
  const searchRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const mobileSearchRef = useRef<HTMLDivElement>(null);
  const previous = useRef(location.pathname);
  const currentPage = navigation.flatMap(g => g.links).find(l => location.pathname.startsWith(l.to))?.label ?? 'Buyurtma';

  useEffect(() => {
    setMobile(false);
    setQuery('');
    setPopup(null);
    document.title = `${currentPage} · Santex CRM`;
    if (previous.current !== location.pathname) {
      document.querySelector<HTMLElement>('h1')?.focus();
      window.scrollTo(0, 0);
    }
    previous.current = location.pathname;
  }, [location.pathname, currentPage]);

  useEffect(() => {
    const outside = (event: MouseEvent) => {
      if (popup !== 'search' && !searchRef.current?.contains(event.target as Node)) setQuery('');
    };
    document.addEventListener('click', outside);
    return () => document.removeEventListener('click', outside);
  }, [popup]);

  useEffect(() => {
    const shortcut = (event: KeyboardEvent) => {
      if (!(event.ctrlKey || event.metaKey) || event.altKey || event.key.toLowerCase() !== 'k' || document.querySelector('dialog[open]')) return;
      event.preventDefault();
      if (window.matchMedia('(max-width: 760px)').matches) setPopup('search');
      else { searchInputRef.current?.focus(); searchInputRef.current?.select(); }
    };
    window.addEventListener('keydown', shortcut);
    return () => window.removeEventListener('keydown', shortcut);
  }, []);

  useEffect(() => {
    if (popup === 'search') mobileSearchRef.current?.querySelector('input')?.focus();
  }, [popup]);

  const attention = useMemo(() => db.orders.filter(o => ['dispute', 'new', 'rejected', 'assigned'].includes(o.status)), [db.orders]);
  const newOrderCount = useMemo(() => db.orders.filter(o => o.status === 'new').length, [db.orders]);
  const searchIndex = useMemo(() => {
    const customerNames = new Map(db.customers.map(customer => [customer.id, customer.name]));
    return [
      ...db.orders.map(o => ({ label: `${o.id} · ${customerNames.get(o.customerId) ?? 'Mijoz'}`, detail: o.service, to: `/orders/${o.id}` })),
      ...db.customers.map(c => ({ label: c.name, detail: c.phone, to: `/customers/${c.id}` })),
      ...db.plumbers.map(p => ({ label: p.name, detail: 'Santexnik', to: `/plumbers/${p.id}` })),
      ...db.shops.map(s => ({ label: s.name, detail: 'Do‘kon', to: `/shops/${s.id}` })),
    ];
  }, [db.orders, db.customers, db.plumbers, db.shops]);
  const results = useMemo(() => {
    if (!query.trim()) return [];
    const matches: SearchResult[] = [];
    for (const result of searchIndex) {
      if (includesQuery(`${result.label} ${result.detail}`, query)) matches.push(result);
      if (matches.length === 7) break;
    }
    return matches;
  }, [searchIndex, query]);

  const sideContent = (
    <>
      <Link to="/dashboard" className="brand"><span className="brand-mark"><Droplets size={25} strokeWidth={2.2} /></span><span>Santex<span className="brand-caption">XIZMAT MARKAZI</span></span></Link>
      <div className="workspace"><span className="workspace-icon"><MapPin size={17} /></span><div><strong>Marhamat tumani</strong><small>Andijon viloyati · Pilot</small></div><span className="online-dot" /></div>
      <nav aria-label="Asosiy navigatsiya">
        {navigation.map(group => (
          <div className="nav-group" key={group.group}>
            <div className="nav-group-label">{group.group}</div>
            {group.links.map(item => (
              <NavLink to={item.to} key={item.to} onClick={() => setMobile(false)}>
                <item.icon size={18} /><span>{item.label}</span>
                {item.to === '/orders' && <span className="nav-count" aria-label={`${newOrderCount} ta yangi buyurtma`}>{newOrderCount}</span>}
                {item.to === '/reviews' && db.reviews.some(r => r.status === 'pending') && <span className="nav-dot" />}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
      <div className="sidebar-bottom"><ShieldCheck size={18} /><div><strong>Demo ish maydoni</strong><small>Faqat namuna ma’lumotlar</small></div><Badge tone="blue">v1.0</Badge></div>
    </>
  );

  const closeSearch = () => { setQuery(''); setPopup(null); };
  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">Asosiy mazmunga o‘tish</a>
      <aside className="sidebar">{sideContent}</aside>
      {mobile && <Modal title="Navigatsiya" onClose={() => setMobile(false)}><div className="mobile-navigation">{sideContent}</div></Modal>}
      <div className="main-shell">
        <header className="topbar">
          <div className="toolbar-left">
            <button className="icon-button mobile-toggle" aria-label="Menyuni ochish" aria-haspopup="dialog" aria-expanded={mobile} onClick={() => setMobile(true)}><Menu size={22} /></button>
            <span className="breadcrumb"><span>Ish maydoni</span><ChevronRight size={14} aria-hidden="true" /><strong>{currentPage}</strong></span>
          </div>
          <div className="toolbar-right">
            <div className="global-search" ref={searchRef} onKeyDown={event => { if (event.key === 'Escape') { closeSearch(); searchInputRef.current?.focus(); } }}>
              <label><Search size={18} aria-hidden="true" /><span className="sr-only">Global qidiruv</span><input ref={searchInputRef} type="search" value={query} onChange={e => setQuery(e.target.value)} aria-describedby="global-search-help" onKeyDown={event => { if (event.key === 'ArrowDown' && results.length) { event.preventDefault(); searchRef.current?.querySelector<HTMLAnchorElement>('.search-results a')?.focus(); } }} placeholder="Buyurtma, mijoz qidirish…" /><kbd aria-hidden="true">Ctrl K</kbd></label>
              <span id="global-search-help" className="sr-only">Ctrl yoki Command va K bilan oching. Natijalarni pastga va yuqoriga tugmalari bilan tanlang.</span>
              {query.trim() && popup !== 'search' && <div className="search-results" role="region" aria-label="Global qidiruv natijalari" onKeyDown={moveSearchFocus}><SearchResults results={results} hasQuery onSelect={closeSearch} /></div>}
            </div>
            <button className="icon-button mobile-search-toggle" aria-label="Global qidiruvni ochish" aria-haspopup="dialog" onClick={() => setPopup('search')}><Search size={20} /></button>
            <Badge tone="warning">DEMO</Badge>
            <button className="icon-button notification-button" aria-label={`Bildirishnomalar: ${attention.length} ta`} aria-haspopup="dialog" onClick={() => setPopup('notifications')}><Bell size={20} />{db.settings.notifications && attention.length > 0 && <i />}</button>
            <button className="profile-button" onClick={() => setPopup('profile')} aria-label="Profil menyusi" aria-haspopup="dialog"><Avatar name="Demo Admin" small /><span><strong>Demo Admin</strong><small>Administrator</small></span><ChevronDown size={14} /></button>
          </div>
        </header>
        <div className="demo-banner"><FlaskConical size={15} /><span><strong>Namoyish muhiti.</strong> Ma’lumotlar sun’iy. Amallar faqat joriy sessiyada saqlanadi.</span><span className="environment">{import.meta.env.PROD ? 'PRODUCTION · STATIC' : 'DEVELOPMENT'}</span></div>
        <main id="main-content" className="main-content" tabIndex={-1}>
          <Suspense fallback={<div className="empty-state" role="status"><span className="loading-dot" aria-hidden="true" />Sahifa yuklanmoqda…</div>}><Outlet /></Suspense>
        </main>
        <footer className="app-footer"><span>© 2026 Santex · Marhamat pilot</span><span>UZS · QQS narxlarga kiritilgan</span></footer>
      </div>
      {popup === 'search' && (
        <Modal title="Global qidiruv" onClose={closeSearch}>
          <div ref={mobileSearchRef} onKeyDown={moveSearchFocus}>
            <SearchInput label="Global qidiruv" value={query} onChange={setQuery} placeholder="Buyurtma, mijoz yoki hamkor…" />
            <div className="search-results mobile-results"><SearchResults results={results} hasQuery={!!query.trim()} onSelect={closeSearch} /></div>
          </div>
        </Modal>
      )}
      {popup === 'notifications' && (
        <Modal title="Diqqat talab qiladigan buyurtmalar" description={db.settings.notifications ? 'Namuna ogohlantirishlar. Telegram ulanmagan.' : 'CRM bildirishnomalari o‘chirilgan. Buyurtmalar ro‘yxati quyida.'} onClose={() => setPopup(null)}>
          <div className="notification-list">{attention.length ? attention.map(o => (
            <Link to={`/orders/${o.id}`} key={o.id} onClick={() => setPopup(null)}>
              <span className={`notification-mark ${o.status === 'dispute' ? 'danger' : ''}`}><Bell size={17} /></span>
              <div><strong>{o.id}</strong><p>{o.status === 'dispute' ? 'Mijoz nizosini ko‘rib chiqing' : o.status === 'new' ? 'Santexnik tayinlash kerak' : o.status === 'rejected' ? 'Qayta tayinlash kerak' : 'Santexnik javobi kutilmoqda'}</p></div><ChevronRight size={16} />
            </Link>
          )) : <p>Hozircha ogohlantirish yo‘q.</p>}</div>
        </Modal>
      )}
      {popup === 'profile' && (
        <Modal title="Demo administrator" onClose={() => setPopup(null)}>
          <p>Marhamat xizmat markazi · to‘liq admin ko‘rinishi</p>
          <p className="muted">Login va Telegram akkaunt tasdig‘i backend bosqichida ulanadi.</p>
          <div className="profile-actions">
            <Link to="/settings" className="button secondary" onClick={() => setPopup(null)}><Settings size={17} />Sozlamalar</Link>
            <button className="button secondary" onClick={() => {
              setPopup(null);
              setConfirm({ title: 'Demo ma’lumotlarni tiklash', description: 'Joriy sessiyadagi barcha o‘zgarishlar va audit namunalari boshlang‘ich holatga qaytadi.', danger: true, action: reset });
            }}><RotateCcw size={17} />Demo holatini tiklash</button>
          </div>
        </Modal>
      )}
      {confirm && <ConfirmDialog value={confirm} onClose={() => setConfirm(null)} />}
    </div>
  );
}
