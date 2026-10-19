import { describe, expect, it } from 'vitest';
import { createSeed } from '../data/seed';
import { advanceRequired, approvedRating, cashOutstanding, estimateTotal, financials, paymentError, transitionError } from './rules';
import type { Payment } from './types';

const paymentInput = (orderId: string, type: Payment['type'], amount = 1000): Omit<Payment, 'id' | 'recordedBy' | 'status' | 'confirmedBy'> => ({ orderId, type, amount, method: 'cash', timestamp: '2026-10-18T14:00:00+05:00', receivedBy: 'Demo operator', collector: 'center', note: 'Unit test' });

describe('Smeta va tarif nusxalari', () => {
  it('kiritilmagan summani nolga aylantirmaydi', () => {
    const order = createSeed().orders[0];
    expect(estimateTotal(order.estimate)).toBeNull();
    expect(advanceRequired(order)).toBeNull();
  });
  it('katalog yangilanganda tasdiqlangan smeta o‘zgarmaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.id === 'DEMO-1007')!;
    const previous = estimateTotal(order.confirmedEstimate!);
    db.services[6].areaRate = 990000;
    expect(estimateTotal(order.confirmedEstimate!)).toBe(previous);
    order.estimate.services[0].price = 777777;
    expect(estimateTotal(order.confirmedEstimate!)).toBe(previous);
  });
  it('yetkazish qismlari soni smeta yetkazish haqini oshirmaydi', () => {
    const order = createSeed().orders.find(o => o.status === 'partial')!;
    const before = estimateTotal(order.estimate);
    order.deliveries.push({ ...order.deliveries[0], id: 'new-part' });
    expect(estimateTotal(order.estimate)).toBe(before);
  });
  it('komissiyada do‘kon yetkazish haqidan komissiya olinmaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.status === 'completed')!;
    const f = financials(order, db.payments);
    expect(f.shopFee).toBe(7000);
    expect(f.shopNet).toBe(158000);
    expect(f.balance).toBe(0);
    expect(f.shopDue).toBe(0);
    expect(f.plumberDue).toBe(0);
  });
});
describe('Jarayon chegaralari', () => {
  it('imzosiz va avanssiz material tayyorlashga ruxsat bermaydi', () => {
    const order = createSeed().orders.find(o => o.status === 'contract')!;
    expect(transitionError(order, 'preparing', [])).toContain('imzo');
    order.contract.signatures = [true, true, true, true]; order.contract.signedAt = '2026-10-18T10:00:00+05:00';
    expect(transitionError(order, 'preparing', [])).toContain('avans');
  });
  it('qayta tasdiqlanmagan smetada tayyorlash bloklanadi', () => {
    const order = createSeed().orders.find(o => o.status === 'contract')!;
    order.estimate.approved = false;
    expect(transitionError(order, 'preparing', [])).toContain('Mijoz');
  });
  it('mijoz material qabulisiz ish boshlamaydi', () => {
    const order = createSeed().orders.find(o => o.status === 'delivered')!;
    expect(transitionError(order, 'working', [])).toContain('material');
    order.materialReceived = true;
    expect(transitionError(order, 'working', [])).toBeNull();
  });
  it('nizoda yakuniy to‘lov, hisob-kitob va avans bilan chetlab o‘tishni bloklaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.status === 'dispute')!;
    for (const type of ['balance', 'shop_settlement', 'plumber_settlement', 'advance'] as const) {
      expect(paymentError(db, paymentInput(order.id, type))).toContain('Nizo');
    }
  });
});
describe('Moliyaviy yozuvlar', () => {
  it('manfiy, kasr va cheksiz summani rad etadi', () => {
    const db = createSeed();
    for (const amount of [-1, 0, 1.5, Infinity, NaN]) expect(paymentError(db, paymentInput('DEMO-1004', 'advance', amount))).toContain('musbat butun');
  });
  it('tasdiqlanmagan yozuvlarni tushumga qo‘shmaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.status === 'contract')!;
    db.payments.push({ ...paymentInput(order.id, 'advance', 2000), id: 'pending', status: 'recorded', recordedBy: 'Demo', confirmedBy: null });
    expect(financials(order, db.payments).paid).toBe(0);
  });
  it('avans o‘rniga qoldiq to‘lovni oldindan qabul qilishni bloklaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.status === 'preparing')!;
    expect(paymentError(db, paymentInput(order.id, 'advance', 1))).toContain('Avans');
    expect(paymentError(db, paymentInput(order.id, 'balance', 1))).toContain('mijoz ishni tasdiqlashi');
  });
  it('naqd topshirish yig‘ilgan naqd qoldig‘idan oshmaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.id === 'DEMO-1005')!;
    const cash = cashOutstanding(order.id, db.payments);
    expect(cash).toBeGreaterThan(0);
    expect(paymentError(db, paymentInput(order.id, 'cash_handover', cash + 1))).toContain('naqd puldan');
    expect(paymentError(db, paymentInput(order.id, 'cash_handover', cash))).toBeNull();
  });
  it('to‘langan hamkor haqini takroran hisoblashni bloklaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.status === 'completed')!;
    expect(paymentError(db, paymentInput(order.id, 'shop_settlement', 1))).toContain('sof qarzdan');
  });
  it('moderatsiya qilinmagan baho umumiy reytingga kirmaydi', () => {
    const db = createSeed();
    expect(approvedRating(db, db.reviews[0].targetId)).toBe('—');
    db.reviews[0].status = 'published';
    expect(approvedRating(db, db.reviews[0].targetId)).toBe('5.0');
  });
  it('tayyorlashdan keyin bekor qilinganda hamkor qarzini taxmin qilmaydi', () => {
    const db = createSeed();
    const order = db.orders.find(o => o.status === 'working')!;
    order.status = 'cancelled';
    order.refundDecision = 'pending';
    const f = financials(order, db.payments);
    expect(f.balance).toBe(0);
    expect(f.plumberDue).toBeNull();
    expect(f.shopDue).toBeNull();
    expect(f.refundDue).toBeNull();
  });
});
