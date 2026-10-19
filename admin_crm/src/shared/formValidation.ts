import { phoneValid } from './format';

export type FormValues = Record<string, string | boolean | string[]>;
export interface FieldSpec {
  name: string;
  label: string;
  type?: 'text' | 'tel' | 'number' | 'textarea' | 'select' | 'checkbox' | 'datetime-local' | 'time' | 'multiselect';
  required?: boolean;
  options?: string[] | { value: string; label: string }[];
  min?: number;
  max?: number;
  step?: string;
  hint?: string;
  full?: boolean;
  validate?: (value: string, values: FormValues) => string | null;
}

export function validateFields(fields: FieldSpec[], values: FormValues): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const field of fields) {
    const raw = values[field.name];
    const text = String(raw ?? '').trim();
    const missing = field.type === 'checkbox' ? raw !== true
      : field.type === 'multiselect' ? !Array.isArray(raw) || !raw.length : !text;

    if (field.required && missing) errors[field.name] = 'Bu maydonni to‘ldiring.';
    else if (text && field.type === 'tel' && !phoneValid(text)) errors[field.name] = 'Telefonni +998 va 9 ta raqam bilan kiriting.';
    else if (text && field.type === 'number') {
      const value = Number(text);
      if (!Number.isFinite(value)) errors[field.name] = 'To‘g‘ri son kiriting.';
      else if (value < (field.min ?? 0)) errors[field.name] = `Qiymat kamida ${field.min ?? 0} bo‘lishi kerak.`;
      else if (field.max !== undefined && value > field.max) errors[field.name] = `Qiymat ${field.max} dan oshmasligi kerak.`;
      else if (field.step !== 'any' && !Number.isInteger(value)) errors[field.name] = 'Butun son kiriting.';
    }

    if (!errors[field.name] && field.validate) {
      const error = field.validate(text, values);
      if (error) errors[field.name] = error;
    }
  }
  return errors;
}
