import { type Database, type Estimate, type Order, type OrderStatus, type Payment, type PaymentKind, type MoneyValue } from './types';

export const isClosed = (status: OrderStatus) => ['completed', 'cancelled'].includes(status);
export function lineTotal(lines: Estimate['services']): MoneyValue {
  return lines.some(line => line.price === null) ? null : lines.reduce((sum, line) => sum + Math.round(line.quantity * (line.price ?? 0)), 0);
}
export function estimateTotal(estimate: Estimate): MoneyValue {
  const services = lineTotal(estimate.services);
  const materials = lineTotal(estimate.materials);
  if (services === null || materials === null || estimate.deliveryFee === null || estimate.emergencyFee === null) return null;
  return Math.round(services + materials + estimate.deliveryFee + estimate.emergencyFee);
}
export function advanceRequired(order: Order, estimate = order.estimate): MoneyValue {
  const total = estimateTotal(estimate);
  if (total === null || order.advance.value === null) return null;
  return order.advance.mode === 'percent' ? Math.round(total * order.advance.value / 100) : Math.min(total, order.advance.value);
}
export function paidFor(orderId: string, payments: Payment[]): number {
  return payments.filter(p => p.orderId === orderId && p.status === 'confirmed').reduce((sum, p) =>
    sum + (p.type === 'advance' || p.type === 'balance' ? p.amount : p.type === 'refund' ? -p.amount : 0), 0);
}
export function financials(order: Order, payments: Payment[]) {
  const estimate = order.confirmedEstimate ?? order.estimate;
  const total = estimateTotal(estimate);
  const labor = lineTotal(estimate.services);
  const materials = lineTotal(estimate.materials);
  const plumberFee = labor === null || order.commissions.plumber === null ? null : Math.round(labor * order.commissions.plumber / 100);
  const shopFee = materials === null || order.commissions.shop === null ? null : Math.round(materials * order.commissions.shop / 100);
  const plumberNet = labor === null || plumberFee === null ? null : labor - plumberFee;
  const shopNet = materials === null || shopFee === null || estimate.deliveryFee === null ? null : materials - shopFee + estimate.deliveryFee;
  const paid = paidFor(order.id, payments);
  const settled = (type: PaymentKind) => payments.filter(p => p.orderId === order.id && p.type === type && p.status === 'confirmed').reduce((s, p) => s + p.amount, 0);
  return {
    total, paid, balance: order.status === 'cancelled' ? 0 : total === null ? null : Math.max(0, total - paid), plumberFee, shopFee,
    commission: plumberFee === null || shopFee === null ? null : plumberFee + shopFee,
    plumberNet, shopNet,
    plumberDue: order.status === 'cancelled' ? order.workStarted ? null : 0 : plumberNet === null ? null : Math.max(0, plumberNet - settled('plumber_settlement')),
    shopDue: order.status === 'cancelled' ? order.preparationStarted ? null : 0 : shopNet === null ? null : Math.max(0, shopNet - settled('shop_settlement')),
    refundDue: order.refundDecision === 'pending' ? null : order.status === 'cancelled' && order.refundDecision === 'full' ? paid : 0,
  };
}
export function cashOutstanding(orderId: string, payments: Payment[]) {
  return payments.filter(p => p.orderId === orderId && p.status === 'confirmed').reduce((sum, p) => {
    if (['advance', 'balance'].includes(p.type) && p.collector === 'plumber' && p.method === 'cash') return sum + p.amount;
    return p.type === 'cash_handover' ? sum - p.amount : sum;
  }, 0);
}
export const nextStatuses: Partial<Record<OrderStatus, OrderStatus>> = {
  assigned: 'accepted', accepted: 'inspection', inspection: 'estimating', estimating: 'shop_pending',
  shop_pending: 'approval', approval: 'contract', contract: 'preparing', preparing: 'transit',
  transit: 'delivered', partial: 'delivered', delivered: 'working', working: 'completion', completion: 'completed',
};
export function transitionError(order: Order, next: OrderStatus, payments: Payment[]): string | null {
  if (order.dispute.open) return 'Nizo hal qilinmaguncha jarayon va yakuniy hisob-kitob bloklangan.';
  if (isClosed(order.status)) return 'Yopilgan buyurtmani o‘zgartirib bo‘lmaydi.';
  if (nextStatuses[order.status] !== next) return 'Ushbu bosqichga bevosita o‘tish mumkin emas.';
  if (next === 'accepted' && !order.plumberId) return 'Avval santexnik tayinlang.';
  if (next === 'inspection' && !order.inspectionAt) return 'Avval ko‘rik vaqtini kiriting.';
  if (next === 'shop_pending' && !order.shopId) return 'Avval do‘kon tayinlang.';
  if (next === 'contract' && (!order.estimate.approved || estimateTotal(order.estimate) === null)) return 'Smetaning barcha narxlari va mijoz demo tasdig‘i kerak.';
  if (next === 'preparing') {
    if (!order.estimate.approved) return 'Mijoz yangi smetani tasdiqlashi kutilmoqda.';
    if (!order.contract.signedAt || !order.contract.signatures.every(Boolean)) return 'To‘rt tomon imzosi qayd etilishi kerak.';
    const required = advanceRequired(order);
    if (required === null) return 'Avans qiymati sozlanmagan.';
    if (paidFor(order.id, payments) < required) return 'Kerakli avans hali to‘liq qayd etilmagan.';
    if (order.estimate.materials.length && (!order.shopId || order.preparationMinutes === null)) return 'Do‘kon va uning tayyorlash vaqti belgilanishi kerak.';
  }
  if (next === 'working' && !order.materialReceived) return 'Mijoz material qabulini demo tasdiqlashi kerak.';
  if (next === 'completed' && (!order.customerCompleted || financials(order, payments).balance !== 0)) return 'Mijoz ishni tasdiqlashi va qoldiq to‘lov to‘liq qayd etilishi kerak.';
  return null;
}
export function paymentError(db: Database, payment: Omit<Payment, 'id' | 'recordedBy' | 'status' | 'confirmedBy'>): string | null {
  const order = db.orders.find(o => o.id === payment.orderId);
  if (!order) return 'Buyurtma topilmadi.';
  if (!Number.isFinite(payment.amount) || !Number.isInteger(payment.amount) || payment.amount <= 0) return 'Summa musbat butun UZS bo‘lishi kerak.';
  if (!Number.isFinite(new Date(payment.timestamp).getTime())) return 'Sana va vaqtni tekshiring.';
  if (db.payments.some(p => p.orderId === order.id && p.type === payment.type && p.status === 'recorded')) return 'Shu turdagi yozuv tasdiqlanishini kutmoqda.';
  if (order.dispute.open && ['advance', 'balance', 'shop_settlement', 'plumber_settlement'].includes(payment.type)) return 'Nizo hal bo‘lguncha mijoz to‘lovi va hamkor hisob-kitobi bloklangan.';
  const f = financials(order, db.payments);
  if (['advance', 'balance'].includes(payment.type)) {
    if (order.status === 'cancelled') return 'Bekor qilingan buyurtmaga to‘lov qabul qilinmaydi.';
    if (!order.estimate.approved || !order.contract.signedAt) return 'Avval smeta tasdig‘i va imzolangan shartnoma kerak.';
    if (f.balance === null || payment.amount > f.balance) return 'Summa mijoz qoldig‘idan katta yoki smeta sozlanmagan.';
    const required = advanceRequired(order);
    if (payment.type === 'advance' && (required === null || payment.amount > Math.max(0, required - f.paid))) return 'Avans summasi belgilangan avans qoldig‘idan oshmasin. Qolgan summa ish tasdig‘idan keyin qabul qilinadi.';
    if (payment.type === 'balance' && !order.customerCompleted) return 'Qoldiq to‘lovdan oldin mijoz ishni tasdiqlashi kerak.';
  }
  if (payment.type.endsWith('_settlement')) {
    if (order.status !== 'completed' || !order.customerCompleted) return 'Hamkor hisob-kitobi faqat yakunlangan buyurtmada mumkin.';
    const net = payment.type === 'shop_settlement' ? f.shopDue : f.plumberDue;
    if (net === null || payment.amount > net) return 'Summa hamkorga qolgan sof qarzdan oshmasligi kerak.';
    if (payment.method !== 'cash') return 'Hamkor hisob-kitobi naqd amalga oshiriladi.';
  }
  if (payment.type === 'cash_handover' && (payment.amount > cashOutstanding(order.id, db.payments) || !order.plumberId)) return 'Summa santexnik topshirishi kerak bo‘lgan naqd puldan katta.';
  if (payment.type === 'cash_handover' && payment.method !== 'cash') return 'Naqd topshirish uchun naqd usulni tanlang.';
  if (['cash_handover', 'shop_settlement', 'plumber_settlement', 'refund'].includes(payment.type) && payment.collector !== 'center') return 'Bu amalni xizmat markazi qayd etishi kerak.';
  if (payment.type === 'refund' && (order.status !== 'cancelled' || order.refundDecision !== 'full' || payment.amount > f.paid)) return 'Qaytarish qarori yoki qaytariladigan summa mos emas.';
  return null;
}
export function approvedRating(db: Database, targetId: string): string {
  const reviews = db.reviews.filter(r => r.targetId === targetId && r.status === 'published');
  return reviews.length ? (reviews.reduce((s, r) => s + r.score, 0) / reviews.length).toFixed(1) : '—';
}
