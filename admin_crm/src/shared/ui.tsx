// Stable public interface; components stay in small modules without circular imports.
export {
  Avatar, Badge, DateRange, EmptyState, FilePreview, KeyValue, Money, Notice,
  PageHeader, Panel, SearchInput, SelectFilter, StatCard, StatusBadge, Tabs,
} from './components/primitives';
export { Modal, ConfirmDialog, type Confirmation } from './components/Modal';
export { RecordForm } from './components/RecordForm';
export { DataTable, type Column } from './components/DataTable';
export type { FieldSpec, FormValues } from './formValidation';
