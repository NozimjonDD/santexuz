import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { loadApplicationData } from '../data/source';
import type { DataConfig } from '../data/config';
import { id, now } from '../shared/format';
import type { Database } from '../domain/types';
import { WriteAccessContext } from '../shared/writeAccess';

interface AuditMeta {
  action: string;
  objectType: string;
  objectId: string;
  summary: string;
  before?: unknown;
  after?: unknown;
  actor?: string;
}
type Mutation = (draft: Database) => void;
interface StoreValue {
  db: Database;
  isMock: boolean;
  reload: () => void;
  mutate: (meta: AuditMeta, mutation: Mutation) => void;
  reset: () => void;
  notify: (message: string, tone?: 'success' | 'error' | 'info') => void;
}
interface Toast { id: string; message: string; tone: 'success' | 'error' | 'info' }
const Store = createContext<StoreValue | null>(null);
const Notifications = createContext<StoreValue['notify'] | null>(null);
const MAX_TOASTS = 4;
const TOAST_DURATION_MS = 6000;

function NotificationProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef(new Map<string, number>());

  const dismiss = useCallback((toastId: string) => {
    window.clearTimeout(timers.current.get(toastId));
    timers.current.delete(toastId);
    setToasts(items => items.filter(toast => toast.id !== toastId));
  }, []);

  const notify = useCallback((message: string, tone: Toast['tone'] = 'success') => {
    const toast: Toast = { id: id('toast'), message, tone };
    if (timers.current.size >= MAX_TOASTS) {
      const oldestId = timers.current.keys().next().value;
      if (oldestId !== undefined) {
        window.clearTimeout(timers.current.get(oldestId));
        timers.current.delete(oldestId);
      }
    }
    setToasts(items => [...items.slice(-(MAX_TOASTS - 1)), toast]);
    timers.current.set(toast.id, window.setTimeout(() => dismiss(toast.id), TOAST_DURATION_MS));
  }, [dismiss]);

  useEffect(() => {
    const activeTimers = timers.current;
    return () => {
      activeTimers.forEach(timer => window.clearTimeout(timer));
      activeTimers.clear();
    };
  }, []);

  return <Notifications.Provider value={notify}>
    {children}
    <div className="toast-stack" aria-live="polite" aria-atomic="false">
      {toasts.map(toast => <div key={toast.id} className={`toast ${toast.tone}`} role={toast.tone === 'error' ? 'alert' : 'status'}>
        <span>{toast.message}</span>
        <button type="button" aria-label="Xabarni yopish" onClick={() => dismiss(toast.id)}>×</button>
      </div>)}
    </div>
  </Notifications.Provider>;
}

function DatabaseProvider({ children }: { children: ReactNode }) {
  type DataState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; db: Database; config: DataConfig };
  const [state, setState] = useState<DataState>({ status: 'loading' });
  const [revision, setRevision] = useState(0);
  const current = useRef<Database | null>(null);
  const notify = useContext(Notifications);
  if (!notify) throw new Error('NotificationProvider topilmadi');
  const isMock = state.status === 'ready' && state.config.mock;
  const reload = useCallback(() => setRevision(value => value + 1), []);

  useEffect(() => {
    const controller = new AbortController();
    current.current = null;
    setState({ status: 'loading' });
    loadApplicationData(controller.signal).then(({ db, config }) => {
      if (controller.signal.aborted) return;
      current.current = db;
      setState({ status: 'ready', db, config });
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) setState({ status: 'error', message: error instanceof Error ? error.message : 'Ma’lumotni yuklab bo‘lmadi.' });
    });
    return () => controller.abort();
  }, [revision]);

  const mutate = useCallback((meta: AuditMeta, mutation: Mutation) => {
    if (!isMock) throw new Error('API rejimi faqat ko‘rish uchun. Haqiqiy saqlash endpointlari hali ulanmagan.');
    if (!current.current) throw new Error('Ma’lumot hali yuklanmagan.');
    // Keep audit snapshots independent from form values and mutable draft records.
    const event = structuredClone({
      id: id('AUD'), actor: 'Demo administrator', timestamp: now(), before: null, after: null, ...meta,
    });
    // Advance synchronously so consecutive financial writes read the latest data.
    const draft = structuredClone(current.current);
    mutation(draft);
    draft.audit.unshift(event);
    current.current = draft;
    setState(previous => previous.status === 'ready' ? { ...previous, db: draft } : previous);
    notify('Demo o‘zgarish saqlandi. Haqiqiy tizimga yuborilmadi.');
  }, [notify, isMock]);
  const reset = useCallback(() => {
    if (!isMock) throw new Error('Haqiqiy ma’lumotlarni demo holatiga qaytarib bo‘lmaydi.');
    reload();
  }, [isMock, reload]);

  const value = useMemo<StoreValue | null>(() => state.status === 'ready'
    ? { db: state.db, isMock, reload, mutate, reset, notify } : null, [state, isMock, reload, mutate, reset, notify]);
  if (!value) return <div className="data-state" aria-busy={state.status === 'loading'}>
    {state.status === 'error' ? <>
      <h1>Ma’lumotni yuklab bo‘lmadi</h1><p role="alert">{state.message}</p>
      <button className="button primary" onClick={reload}>Qayta urinish</button>
    </> : <p role="status"><span className="loading-dot" aria-hidden="true" />Ma’lumotlar yuklanmoqda…</p>}
  </div>;
  return <Store.Provider value={value}><WriteAccessContext.Provider value={isMock}>{children}</WriteAccessContext.Provider></Store.Provider>;
}

export function StoreProvider({ children }: { children: ReactNode }) {
  // Toast updates stay outside the database context and its consumers.
  return <NotificationProvider><DatabaseProvider>{children}</DatabaseProvider></NotificationProvider>;
}

export function useStore() {
  const value = useContext(Store);
  if (!value) throw new Error('StoreProvider topilmadi');
  return value;
}
