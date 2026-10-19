import { useEffect, useId, useRef, useState, type ReactNode } from 'react';
import { X } from 'lucide-react';

export function Modal({ title, description, children, onClose, wide = false }: {
  title: string; description?: string; children: ReactNode; onClose: () => void; wide?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const descriptionId = useId();
  const closeRef = useRef(onClose);
  closeRef.current = onClose;

  useEffect(() => {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const dialog = ref.current;
    if (!dialog) return;
    if (!dialog.open) dialog.showModal();
    const cancel = (event: Event) => { event.preventDefault(); closeRef.current(); };
    dialog.addEventListener('cancel', cancel);
    return () => {
      dialog.removeEventListener('cancel', cancel);
      dialog.close();
      if (previous?.isConnected) previous.focus({ preventScroll: true });
    };
  }, []);

  return (
    <dialog ref={ref} className={`modal ${wide ? 'wide' : ''}`} aria-labelledby={titleId} aria-describedby={description ? descriptionId : undefined} onClick={event => { if (event.target === event.currentTarget) onClose(); }}>
      <div className="modal-header">
        <div><h2 id={titleId}>{title}</h2>{description && <p id={descriptionId}>{description}</p>}</div>
        <button type="button" className="icon-button" aria-label="Oynani yopish" onClick={onClose}><X size={20} aria-hidden="true" /></button>
      </div>
      <div className="modal-body">{children}</div>
    </dialog>
  );
}

export interface Confirmation {
  title: string; description: string; details?: ReactNode; action: () => void; label?: string; danger?: boolean;
}

export function ConfirmDialog({ value, onClose }: { value: Confirmation; onClose: () => void }) {
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);
  const submitted = useRef(false);
  function confirm() {
    if (submitted.current) return;
    submitted.current = true;
    setDone(true);
    try { value.action(); onClose(); }
    catch (error) {
      submitted.current = false;
      setDone(false);
      setError(error instanceof Error ? error.message : 'O‘zgarish saqlanmadi.');
    }
  }

  return (
    <Modal title={value.title} description={value.description} onClose={onClose}>
      {value.details}<p className="muted small">Bu amal faqat joriy demo sessiyasiga ta’sir qiladi.</p>
      {error && <p role="alert" className="field-error">{error}</p>}
      <div className="form-actions">
        <button type="button" className="button secondary" onClick={onClose}>Ortga</button>
        <button type="button" disabled={done} className={`button ${value.danger ? 'danger' : 'primary'}`} onClick={confirm}>{value.label ?? 'Tasdiqlash'}</button>
      </div>
    </Modal>
  );
}
