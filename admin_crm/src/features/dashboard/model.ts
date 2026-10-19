import { financials } from '../../domain/rules';
import { matchesOrderTab, progressStatuses, waitingStatuses } from '../../domain/orderQueries';
import type { Database, Order, OrderStatus, Payment } from '../../domain/types';
import { inDateRange, localDate } from '../../shared/format';

export interface DateWindow { from: string; to: string }
export interface TrendPoint { day: string; end: string; count: number }
const dayMilliseconds = 24 * 60 * 60 * 1000;
const dayTime = (day: string) => Date.parse(`${day}T00:00:00Z`);
const dayLabel = (timestamp: number) => new Date(timestamp).toISOString().slice(0, 10);

export function initialDashboardWindow(orders: Order[]): DateWindow {
  const latest = orders.reduce((date, order) => {
    const day = localDate(order.createdAt);
    return day > date ? day : date;
  }, '');
  return latest ? { from: dayLabel(dayTime(latest) - 6 * dayMilliseconds), to: latest } : { from: '', to: '' };
}

function buildTrend(orders: Order[], window: DateWindow) {
  if (!orders.length) return { points: [] as TrendPoint[], bucketDays: 1 };
  const counts = new Map<string, number>();
  for (const order of orders) {
    const day = localDate(order.createdAt);
    counts.set(day, (counts.get(day) ?? 0) + 1);
  }
  const dates = [...counts.keys()].sort();
  const start = dayTime(window.from || dates[0]);
  const end = dayTime(window.to || dates[dates.length - 1]);
  const span = Math.floor((end - start) / dayMilliseconds) + 1;
  if (!Number.isFinite(span) || span < 1) return { points: [] as TrendPoint[], bucketDays: 1 };
  // Bound the SVG to 31 points while retaining every order in long periods.
  const bucketDays = Math.max(1, Math.ceil(span / 31));
  const points: TrendPoint[] = Array.from({ length: Math.ceil(span / bucketDays) }, (_, index) => ({
    day: dayLabel(start + index * bucketDays * dayMilliseconds),
    end: dayLabel(Math.min(end, start + ((index + 1) * bucketDays - 1) * dayMilliseconds)),
    count: 0,
  }));
  for (const [date, count] of counts) {
    const index = Math.floor((dayTime(date) - start) / dayMilliseconds / bucketDays);
    if (points[index]) points[index].count += count;
  }
  return { points, bucketDays };
}

function incomingAmount(payment: Payment) {
  return payment.type === 'refund' ? -payment.amount : ['advance', 'balance'].includes(payment.type) ? payment.amount : 0;
}

export function buildDashboardModel(db: Database, window: DateWindow, currentTime: number) {
  const orders = db.orders.filter(order => inDateRange(order.createdAt, window.from, window.to));
  const customers = new Map(db.customers.map(customer => [customer.id, customer]));
  const paymentsByOrder = new Map<string, Payment[]>();
  const period = { incoming: 0, advances: 0, settlements: 0, todayIncoming: 0 };
  const today = localDate(new Date(currentTime).toISOString());

  for (const payment of db.payments) {
    const group = paymentsByOrder.get(payment.orderId) ?? [];
    group.push(payment);
    paymentsByOrder.set(payment.orderId, group);
    if (payment.status !== 'confirmed' || !inDateRange(payment.timestamp, window.from, window.to)) continue;
    period.incoming += incomingAmount(payment);
    if (payment.type === 'advance') period.advances += payment.amount;
    if (payment.type.endsWith('_settlement')) period.settlements += payment.amount;
    if (localDate(payment.timestamp) === today) period.todayIncoming += incomingAmount(payment);
  }

  const counts = new Map<OrderStatus, number>();
  const metrics = { new: 0, unassigned: 0, estimate: 0, active: 0, due: 0, balance: 0, commission: 0 };
  const attention: { order: Order; label: string; danger: boolean; priority: number }[] = [];
  for (const order of orders) {
    counts.set(order.status, (counts.get(order.status) ?? 0) + 1);
    if (order.status === 'new') metrics.new++;
    if (matchesOrderTab(order, 'unassigned')) metrics.unassigned++;
    if (matchesOrderTab(order, 'estimate')) metrics.estimate++;
    if (matchesOrderTab(order, 'active')) metrics.active++;
    const finance = financials(order, paymentsByOrder.get(order.id) ?? []);
    metrics.due += (finance.shopDue ?? 0) + (finance.plumberDue ?? 0);
    metrics.balance += finance.balance ?? 0;
    if (order.status === 'completed') metrics.commission += finance.commission ?? 0;

    const overdue = order.status === 'assigned' && !!order.assignedAt && currentTime - Date.parse(order.assignedAt) > db.settings.responseMinutes * 60000;
    const late = order.deliveries.some(delivery => delivery.status !== 'delivered' && Date.parse(delivery.eta) < currentTime);
    const issue = order.dispute.open ? { label: 'Mijoz nizosi', priority: 5 }
      : overdue ? { label: 'Santexnik javobi kechikdi', priority: 4 }
        : order.status === 'rejected' ? { label: 'So‘rov rad etilgan', priority: 3 }
          : late ? { label: 'Yetkazish kechikmoqda', priority: 2 }
            : order.status === 'approval' ? { label: 'Smeta tasdig‘i kutilmoqda', priority: 1 }
              : order.status === 'new' ? { label: 'Santexnik tayinlash kerak', priority: 0 } : null;
    if (issue) attention.push({ order, ...issue, danger: order.dispute.open || overdue });
  }

  const countStage = (statuses: OrderStatus[]) => statuses.reduce((sum, status) => sum + (counts.get(status) ?? 0), 0);
  return {
    orders, customers, today, metrics, period,
    attention: attention.sort((a, b) => b.priority - a.priority || a.order.createdAt.localeCompare(b.order.createdAt)),
    recent: [...orders].sort((a, b) => b.createdAt.localeCompare(a.createdAt)).slice(0, 5),
    trend: buildTrend(orders, window),
    stages: [
      { label: 'Kutilmoqda', color: '#4b7cf3', count: countStage(waitingStatuses), filter: 'waiting' },
      { label: 'Jarayonda', color: '#e7ad42', count: countStage(progressStatuses), filter: 'progress' },
      { label: 'Yakunlangan', color: '#19a887', count: counts.get('completed') ?? 0, filter: 'completed' },
      { label: 'Nizo / bekor / rad', color: '#c5ccd8', count: countStage(['dispute', 'cancelled', 'rejected']), filter: 'attention' },
    ],
  };
}
