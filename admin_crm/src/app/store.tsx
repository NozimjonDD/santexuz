import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { createSeed } from '../data/seed';
import { id, now } from '../shared/format';
import type { Database } from '../domain/types';

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
  const [db, setDb] = useState(createSeed);
  const current = useRef(db);
  const notify = useContext(Notifications);
  if (!notify) throw new Error('NotificationProvider topilmadi');

  const mutate = useCallback((meta: AuditMeta, mutation: Mutation) => {
    // Keep audit snapshots independent from form values and mutable draft records.
    const event = structuredClone({
      id: id('AUD'), actor: 'Demo administrator', timestamp: now(), before: null, after: null, ...meta,
    });
    // Advance synchronously so consecutive financial writes read the latest data.
    const draft = structuredClone(current.current);
    mutation(draft);
    draft.audit.unshift(event);
    current.current = draft;
    setDb(draft);
    notify('Demo o‘zgarish saqlandi. Haqiqiy tizimga yuborilmadi.');
  }, [notify]);
  const reset = useCallback(() => {
    const seed = createSeed();
    current.current = seed;
    setDb(seed);
    notify('Demo ma’lumotlar boshlang‘ich holatga qaytdi.', 'info');
  }, [notify]);

  const value = useMemo(() => ({ db, mutate, reset, notify }), [db, mutate, reset, notify]);
  return <Store.Provider value={value}>{children}</Store.Provider>;
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
