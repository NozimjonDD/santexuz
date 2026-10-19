import { isClosed } from './rules';
import type { Order, OrderStatus } from './types';

export const waitingStatuses: OrderStatus[] = ['new', 'assigned', 'accepted', 'inspection', 'estimating', 'shop_pending', 'approval', 'contract'];
export const progressStatuses: OrderStatus[] = ['preparing', 'partial', 'transit', 'delivered', 'working', 'completion'];
const estimateStatuses: OrderStatus[] = ['estimating', 'shop_pending', 'approval'];
const attentionStatuses: OrderStatus[] = ['dispute', 'cancelled', 'rejected'];

export function matchesOrderTab(order: Order, tab: string): boolean {
  switch (tab) {
    case 'all': return true;
    case 'active': return !isClosed(order.status) && order.status !== 'dispute';
    case 'unassigned': return !order.plumberId && !isClosed(order.status);
    case 'waiting': return waitingStatuses.includes(order.status);
    case 'progress': return progressStatuses.includes(order.status);
    case 'estimate': return estimateStatuses.includes(order.status);
    case 'attention': return attentionStatuses.includes(order.status);
    default: return order.status === tab;
  }
}
