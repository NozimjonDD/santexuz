export const categories = ['Ta’mirlash', 'O‘rnatish/almashtirish', 'Quvur/kanalizatsiya', 'Isitish tizimi'] as const;
export const statusLabels = {
  new: 'Yangi so‘rov', assigned: 'Santexnik tayinlangan', accepted: 'Santexnik qabul qildi',
  inspection: 'Ko‘rik belgilandi', estimating: 'Smeta tayyorlanmoqda', shop_pending: 'Do‘kon javobi kutilmoqda',
  approval: 'Smeta tasdig‘i kutilmoqda', contract: 'Shartnoma/avans kutilmoqda', preparing: 'Do‘kon tayyorlayapti',
  partial: 'Qisman yetkazildi', transit: 'Kuryer yo‘lda', delivered: 'Material yetkazildi',
  working: 'Ish jarayonida', completion: 'Ish tasdig‘i kutilmoqda', dispute: 'Nizo',
  completed: 'Yakunlangan', cancelled: 'Bekor qilingan', rejected: 'Rad etilgan',
} as const;
export type OrderStatus = keyof typeof statusLabels;
export type Category = typeof categories[number];
export type MoneyValue = number | null;
export interface Customer {
  id: string; name: string; phone: string; telegramId: string; createdAt: string; notes: string; consent: boolean;
}
export interface Plumber {
  id: string; name: string; phone: string; telegramId: string; district: string; categories: string[];
  experience: number; photo: string; notes: string; isActive: boolean; commission: MoneyValue;
}
export interface Shop {
  id: string; name: string; contactName: string; address: string; district: string; phone: string;
  telegramId: string; description: string; isActive: boolean; commission: MoneyValue;
}
export interface Service {
  id: string; name: string; nameRu: string; nameEn: string; category: string; unit: string;
  areaRate: MoneyValue; emergencyFee: MoneyValue; warranty: string; description: string; isActive: boolean; visible: boolean;
}
export interface Material {
  id: string; name: string; category: string; brand: string; size: string; unit: string; description: string; isActive: boolean;
}
export interface EstimateLine {
  id: string; name: string; quantity: number; unit: string; price: MoneyValue; brand?: string; available?: boolean;
}
export interface Estimate {
  version: number; services: EstimateLine[]; materials: EstimateLine[]; deliveryFee: MoneyValue;
  emergencyFee: MoneyValue; approved: boolean; createdAt: string;
}
export interface Delivery {
  id: string; label: string; status: 'preparing' | 'transit' | 'delivered'; eta: string; note: string;
}
export interface TimelineEvent { id: string; at: string; title: string; detail: string }
export interface ContractSnapshot {
  templateId: string; version: number; language: string; text: string;
  signatures: boolean[]; signedAt: string | null; signedBy: string | null;
}
export interface Order {
  id: string; createdAt: string; customerId: string; plumberId: string | null; shopId: string | null;
  category: string; service: string; address: string; coordinates: string; description: string;
  status: OrderStatus; urgent: boolean; urgencyApproved: boolean; consent: boolean;
  assignedAt: string | null; inspectionAt: string; workStart: string; workEnd: string; etaReason: string; preparationMinutes: number | null;
  estimate: Estimate; confirmedEstimate: Estimate | null; estimateHistory: Estimate[];
  advance: { mode: 'percent' | 'fixed'; value: MoneyValue };
  commissions: { plumber: MoneyValue; shop: MoneyValue };
  contract: ContractSnapshot; contractHistory?: ContractSnapshot[]; deliveries: Delivery[]; timeline: TimelineEvent[]; notes: string[];
  dispute: { open: boolean; reason: string; resolution: string; previousStatus: OrderStatus | null };
  materialReceived: boolean; customerCompleted: boolean; preparationStarted: boolean; workStarted: boolean;
  cancelReason: string; refundDecision: 'pending' | 'full' | 'none' | null;
}
export type PaymentKind = 'advance' | 'balance' | 'cash_handover' | 'shop_settlement' | 'plumber_settlement' | 'refund';
export const paymentLabels: Record<PaymentKind, string> = {
  advance: 'Avans', balance: 'Qoldiq to‘lov', cash_handover: 'Naqd topshirish',
  shop_settlement: 'Do‘konga hisob-kitob', plumber_settlement: 'Santexnikka hisob-kitob', refund: 'Avans qaytarish',
};
export interface Payment {
  id: string; orderId: string; type: PaymentKind; method: 'cash' | 'terminal'; amount: number;
  timestamp: string; receivedBy: string; recordedBy: string; note: string; status: 'recorded' | 'confirmed';
  collector: 'center' | 'plumber'; confirmedBy: string | null;
}
export interface Review {
  id: string; orderId: string; customerId: string; targetType: 'plumber' | 'shop'; targetId: string;
  score: number; comment: string; createdAt: string; status: 'pending' | 'published' | 'hidden';
}
export interface ContractTemplate {
  id: string; name: string; language: string; version: number; note: string; text: string;
  status: 'draft' | 'active' | 'archived'; createdAt: string; author: string;
}
export interface AuditEvent {
  id: string; actor: string; action: string; objectType: string; objectId: string; timestamp: string;
  summary: string; before: unknown; after: unknown;
}
export interface Settings {
  centerName: string; address: string; phone: string; opens: string; closes: string;
  responseMinutes: number; advanceMode: 'percent' | 'fixed'; advanceValue: MoneyValue;
  plumberCommission: MoneyValue; shopCommission: MoneyValue; language: string; notifications: boolean;
}
export interface Database {
  customers: Customer[]; plumbers: Plumber[]; shops: Shop[]; services: Service[]; materials: Material[];
  orders: Order[]; payments: Payment[]; reviews: Review[]; templates: ContractTemplate[]; audit: AuditEvent[]; settings: Settings;
}
export type EntityCollection = 'customers' | 'plumbers' | 'shops' | 'services' | 'materials';
