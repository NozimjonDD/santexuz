import { useMemo } from 'react';
import { Link, useNavigate } from 'react-router';
import { ChevronRight, Zap } from 'lucide-react';
import { useStore } from '../../app/store';
import { Avatar, DataTable, Money, StatusBadge, type Column } from '../../shared/ui';
import { dateTime } from '../../shared/format';
import { estimateTotal, isClosed } from '../../domain/rules';
import type { Order } from '../../domain/types';

function OrderActions({ order }: { order: Order }) {
  const canAssign = !isClosed(order.status) && !order.dispute.open && !order.preparationStarted && !order.workStarted;
  return (
    <details className="row-menu">
      <summary aria-label={`${order.id} amallari`}>•••</summary>
      <div>
        <Link to={`/orders/${order.id}`}>Ko‘rish</Link>
        {canAssign && <><Link to={`/orders/${order.id}?action=plumber`}>Santexnik tayinlash</Link>{order.plumberId && <Link to={`/orders/${order.id}?action=shop`}>Do‘kon tayinlash</Link>}</>}
        <Link to={`/orders/${order.id}?section=general`}>Telefonni ko‘rish</Link>
        {!isClosed(order.status) && !order.dispute.open && <Link to={`/orders/${order.id}?action=cancel`}>Bekor qilish</Link>}
      </div>
    </details>
  );
}

export function OrderTable({ rows, compact = false }: { rows: Order[]; compact?: boolean }) {
  const { db } = useStore();
  const navigate = useNavigate();
  const lookup = useMemo(() => ({
    customers: new Map(db.customers.map(customer => [customer.id, customer])),
    plumbers: new Map(db.plumbers.map(plumber => [plumber.id, plumber])),
    shops: new Map(db.shops.map(shop => [shop.id, shop])),
  }), [db.customers, db.plumbers, db.shops]);
  const totals = useMemo(() => new Map(rows.map(order => [order.id, estimateTotal(order.confirmedEstimate ?? order.estimate)])), [rows]);
  const columns = useMemo<Column<Order>[]>(() => {
    const customer = (order: Order) => lookup.customers.get(order.customerId);
    return [
      {
        key: 'id', label: 'Buyurtma', sortValue: order => order.id,
        render: order => <div className="order-id"><Link to={`/orders/${order.id}`}>{order.id}</Link>{order.urgent && <span className="urgent"><Zap size={12} aria-hidden="true" />Shoshilinch</span>}</div>,
      },
      {
        key: 'customer', label: 'Mijoz', sortValue: order => customer(order)?.name ?? '',
        render: order => <div className="person"><Avatar name={customer(order)?.name ?? '?'} small /><div><Link to={`/customers/${order.customerId}`}>{customer(order)?.name ?? 'Mijoz topilmadi'}</Link><small>{compact ? order.service : customer(order)?.phone}</small></div></div>,
      },
      ...(!compact ? [
        { key: 'service', label: 'Xizmat', sortValue: (order: Order) => order.service, render: (order: Order) => <div className="cell-stack"><span>{order.service}</span><small>{order.category}</small></div> },
        { key: 'partners', label: 'Santexnik / do‘kon', render: (order: Order) => <div className="cell-stack"><span>{order.plumberId ? lookup.plumbers.get(order.plumberId)?.name ?? 'Topilmadi' : 'Tayinlanmagan'}</span><small>{order.shopId ? lookup.shops.get(order.shopId)?.name ?? 'Topilmadi' : 'Do‘kon tanlanmagan'}</small></div> },
      ] : []),
      { key: 'status', label: 'Holati', sortValue: order => order.status, render: order => <StatusBadge status={order.status} /> },
      { key: 'total', label: 'Jami', sortValue: order => totals.get(order.id) ?? -1, className: 'numeric', render: order => <Money value={totals.get(order.id)} /> },
      { key: 'createdAt', label: 'Yaratilgan vaqt', sortValue: order => order.createdAt, render: order => <span className="muted small nowrap">{dateTime(order.createdAt)}</span> },
      { key: 'actions', label: 'Amal', render: order => compact ? <Link className="icon-button" aria-label={`${order.id} tafsilotini ochish`} to={`/orders/${order.id}`}><ChevronRight size={18} aria-hidden="true" /></Link> : <OrderActions order={order} /> },
    ];
  }, [lookup, totals, compact]);

  return <DataTable rows={rows} columns={columns} caption="Buyurtmalar jadvali" onRowOpen={order => navigate(`/orders/${order.id}`)} />;
}
