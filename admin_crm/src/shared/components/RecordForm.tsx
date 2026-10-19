import { useId, useRef, useState, type FormEvent } from 'react';
import { Check } from 'lucide-react';
import { validateFields, type FieldSpec, type FormValues } from '../formValidation';

export function RecordForm({ fields, initial = {}, onSubmit, onCancel, submitLabel = 'Saqlash' }: {
  fields: FieldSpec[]; initial?: FormValues; onSubmit: (values: FormValues) => void; onCancel?: () => void; submitLabel?: string;
}) {
  const [values, setValues] = useState<FormValues>(initial);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const formId = useId();
  const formRef = useRef<HTMLFormElement>(null);

  function submit(event: FormEvent) {
    event.preventDefault();
    const next = validateFields(fields, values);
    setErrors(next);
    const firstError = Object.keys(next)[0];
    if (firstError) {
      formRef.current?.querySelector<HTMLElement>(`[data-field="${firstError}"] input, [data-field="${firstError}"] select, [data-field="${firstError}"] textarea`)?.focus();
      return;
    }
    try { onSubmit(values); }
    catch (error) { setErrors({ _form: error instanceof Error ? error.message : 'Saqlashda xato.' }); }
  }

  function update(name: string, value: FormValues[string]) {
    setValues(previous => ({ ...previous, [name]: value }));
    setErrors(previous => ({ ...previous, [name]: '', _form: '' }));
  }

  return (
    <form ref={formRef} onSubmit={submit} noValidate>
      <div className="form-grid">
        {fields.map(field => {
          const fieldId = `${formId}-${field.name}`;
          const options = field.options?.map(option => typeof option === 'string' ? { value: option, label: option } : option) ?? [];
          const selected = Array.isArray(values[field.name]) ? values[field.name] as string[] : [];
          const props = { id: fieldId, name: field.name, 'aria-invalid': !!errors[field.name], 'aria-describedby': `${fieldId}-hint`, required: field.required };
          const label = <>{field.label}{field.required && <span className="required"> *</span>}</>;
          const textValue = String(values[field.name] ?? '');

          return (
            <div key={field.name} data-field={field.name} className={`form-field ${field.full || field.type === 'textarea' || field.type === 'multiselect' ? 'full' : ''}`}>
              {field.type !== 'checkbox' && field.type !== 'multiselect' && <label htmlFor={fieldId}>{label}</label>}
              {field.type === 'checkbox' ? (
                <label className="checkbox"><input {...props} type="checkbox" checked={values[field.name] === true} onChange={event => update(field.name, event.target.checked)} />{label}</label>
              ) : field.type === 'multiselect' ? (
                <fieldset className="checkbox-options" aria-describedby={`${fieldId}-hint`} aria-invalid={!!errors[field.name]}>
                  <legend>{label}</legend>
                  {options.map(option => <label key={option.value} className="checkbox"><input type="checkbox" name={field.name} value={option.value} checked={selected.includes(option.value)} onChange={event => update(field.name, event.target.checked ? [...selected, option.value] : selected.filter(value => value !== option.value))} />{option.label}</label>)}
                </fieldset>
              ) : field.type === 'textarea' ? (
                <textarea {...props} rows={4} value={textValue} onChange={event => update(field.name, event.target.value)} />
              ) : field.type === 'select' ? (
                <select {...props} value={textValue} onChange={event => update(field.name, event.target.value)}><option value="">Tanlang</option>{options.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select>
              ) : (
                <input {...props} type={field.type ?? 'text'} min={field.min ?? (field.type === 'number' ? 0 : undefined)} max={field.max} step={field.step} value={textValue} onChange={event => update(field.name, event.target.value)} />
              )}
              <div id={`${fieldId}-hint`}>{errors[field.name] ? <p className="field-error" role="alert">{errors[field.name]}</p> : field.hint ? <p className="field-hint">{field.hint}</p> : null}</div>
            </div>
          );
        })}
      </div>
      {errors._form && <p role="alert" className="field-error">{errors._form}</p>}
      <div className="form-actions">{onCancel && <button type="button" className="button secondary" onClick={onCancel}>Bekor qilish</button>}<button className="button primary" type="submit"><Check size={16} aria-hidden="true" />{submitLabel}</button></div>
    </form>
  );
}
