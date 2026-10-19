import { describe, expect, it } from 'vitest';
import { createSeed } from '../../data/seed';
import { matchesOrderTab } from '../../domain/orderQueries';
import { buildDashboardModel, initialDashboardWindow } from './model';

const timestamp = Date.parse('2026-10-18T16:00:00+05:00');
describe('Dashboard hisoblari', () => {
  it('demo davrini namunadagi eng yangi sanaga nisbatan tanlaydi', () => {
    expect(initialDashboardWindow(createSeed().orders)).toEqual({ from: '2026-10-12', to: '2026-10-18' });
  });
  it('bo‘sh kunlarni nol bilan ko‘rsatadi va uzoq davrni 31 nuqtaga sig‘diradi', () => {
    const db = createSeed();
    const model = buildDashboardModel(db, { from: '2026-01-01', to: '2026-12-31' }, timestamp);
    expect(model.trend.points.length).toBeLessThanOrEqual(31);
    expect(model.trend.points.reduce((sum, point) => sum + point.count, 0)).toBe(db.orders.length);
    expect(model.trend.points.some(point => point.count === 0)).toBe(true);
  });
  it('holat kartasi soni undan ochiladigan filtrga mos keladi', () => {
    const db = createSeed();
    const model = buildDashboardModel(db, { from: '', to: '' }, timestamp);
    for (const stage of model.stages) expect(db.orders.filter(order => matchesOrderTab(order, stage.filter)).length).toBe(stage.count);
    expect(model.attention[0].order.status).toBe('dispute');
  });
  it('qaytarilgan pulni tushumdan ayiradi va tasdiqlanmaganini hisoblamaydi', () => {
    const db = createSeed();
    const window = { from: '2026-10-18', to: '2026-10-18' };
    const before = buildDashboardModel(db, window, timestamp).period.incoming;
    const payment = { ...db.payments[0], id: 'REFUND-DEMO', type: 'refund' as const, amount: 1000, timestamp: '2026-10-18T15:00:00+05:00' };
    db.payments.push(payment);
    db.payments.push({ ...payment, id: 'PENDING-DEMO', status: 'recorded' });
    expect(buildDashboardModel(db, window, timestamp).period.incoming).toBe(before - 1000);
  });
});
