import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { ArrowDownToLine, ArrowRight, ArrowUpRight, Clock3, ClipboardList, Package, Plus, Users, Wallet, Wrench, AlertCircle } from 'lucide-react';
import { useStore } from '../../app/store';
import { number } from '../../shared/format';
import { Badge, DateRange, EmptyState, KeyValue, Money, PageHeader, Panel, StatCard } from '../../shared/ui';
import { OrderTable } from '../orders/OrderTable';
import { buildDashboardModel, initialDashboardWindow } from './model';
import { TrendChart } from './TrendChart';

export default function Dashboard() {
  const { db } = useStore();
  const navigate = useNavigate();
  const [range, setRange] = useState(() => initialDashboardWindow(db.orders));
  const [currentTime, setCurrentTime] = useState(Date.now);
  useEffect(() => {
    const timer = window.setInterval(() => setCurrentTime(Date.now()), 60000);
    return () => window.clearInterval(timer);
  }, []);
  const model = useMemo(() => buildDashboardModel(db, range, currentTime), [db, range, currentTime]);
  const { orders, customers, metrics, period, stages, attention, recent, trend } = model;
  const openOrders = (tab: string) => navigate(`/orders?${new URLSearchParams({ tab, ...range })}`);
  const todayLabel = model.today.split('-').reverse().join('.');

  return (
    <>
      <PageHeader
        eyebrow="XIZMAT MARKAZI / UMUMIY KO‘RINISH" title="Bosh sahifa"
        description="Ish jarayonlari, buyurtmalar va moliya — bir joyda."
        actions={<><Link className="button secondary" to="/reports"><ArrowDownToLine size={16} aria-hidden="true" />Hisobotlar</Link><Link className="button primary" to="/orders?new=1"><Plus size={18} aria-hidden="true" />Yangi so‘rov</Link></>}
      />
      <div className="dashboard-filter">
        <div className="pilot-label"><span className="online-dot" /><strong>Marhamat tumani</strong><Badge tone="blue">Pilot hudud</Badge></div>
        <DateRange {...range} onChange={(from, to) => setRange({ from, to })} />
      </div>
      <div className="stats-grid">
        <StatCard label="Yangi so‘rovlar" value={number(metrics.new)} detail={<><span className="stat-dot blue" />Tanlangan davr bo‘yicha</>} icon={<ClipboardList size={20} />} onClick={() => openOrders('new')} />
        <StatCard label="Tayinlash kutilmoqda" value={number(metrics.unassigned)} detail={<><span className="stat-dot warning" />Santexnik tanlash kerak</>} icon={<Wrench size={20} />} onClick={() => openOrders('unassigned')} />
        <StatCard label="Smeta / do‘kon javobi" value={number(metrics.estimate)} detail="Tasdiqlash jarayonida" icon={<Clock3 size={20} />} onClick={() => openOrders('estimate')} />
        <StatCard label="Faol buyurtmalar" value={number(metrics.active)} detail={<><span className="stat-dot success" />Jarayon kuzatuvda</>} icon={<Package size={20} />} onClick={() => openOrders('active')} />
        <StatCard label="Bugungi tushum" value={<Money value={period.todayIncoming} />} detail={`${todayLabel} · davr filtrida`} icon={<Wallet size={20} />} onClick={() => navigate('/finance')} />
        <StatCard label="Hamkorlarga qoldiq" value={<Money value={metrics.due} />} detail="Nizodagi summa ham kiritilgan" icon={<Users size={20} />} onClick={() => navigate('/finance?tab=partners')} />
      </div>
      <div className="dashboard-chart-grid">
        <Panel title="Buyurtmalar dinamikasi" caption="Tanlangan davr bo‘yicha yangi so‘rovlar · demo" action={<Badge tone="blue">{orders.length} ta buyurtma</Badge>}>
          {trend.points.length ? <TrendChart points={trend.points} bucketDays={trend.bucketDays} /> : <EmptyState text="Tanlangan davrda buyurtma yo‘q." />}
        </Panel>
        <Panel title="Buyurtmalar holati" caption="Tanlangan davr kesimida">
          <div className="status-summary">
            <div className="status-number">{orders.length}<span>jami buyurtma</span></div>
            <div className="stacked-bar" aria-hidden="true">{stages.map(stage => <span key={stage.filter} style={{ width: `${orders.length ? stage.count / orders.length * 100 : 0}%`, background: stage.color }} />)}</div>
            {stages.map(stage => <button type="button" key={stage.filter} onClick={() => openOrders(stage.filter)}><span><i aria-hidden="true" style={{ background: stage.color }} />{stage.label}</span><strong>{stage.count}<ArrowRight size={13} aria-hidden="true" /></strong></button>)}
          </div>
        </Panel>
      </div>
      <div className="dashboard-bottom-grid">
        <Panel title="Diqqat talab qiladi" caption="Eng muhim masalalar birinchi ko‘rsatiladi" action={<Badge tone={attention.length ? 'danger' : 'success'}>{attention.length} ta</Badge>}>
          <div className="attention-list">
            {attention.slice(0, 5).map(item => <Link key={item.order.id} to={`/orders/${item.order.id}`}>
              <span className={`attention-icon ${item.danger ? 'danger' : ''}`}><AlertCircle size={19} aria-hidden="true" /></span>
              <div><strong>{item.label}</strong><small>{item.order.id} · {customers.get(item.order.customerId)?.name}</small></div><ArrowUpRight size={16} aria-hidden="true" />
            </Link>)}
            {!attention.length && <EmptyState title="Hammasi tartibda" text="Tanlangan davrda shoshilinch amal yo‘q." />}
          </div>
        </Panel>
        <Panel title="Moliyaviy qisqacha" caption="Tanlangan davr · UZS" action={<Link to="/finance" className="text-link">Moliya <ArrowRight size={14} aria-hidden="true" /></Link>}>
          <dl className="financial-summary">
            <KeyValue label="Sof tushum (qaytarishlar ayirilgan)"><Money value={period.incoming} /></KeyValue>
            <KeyValue label="Qabul qilingan avans"><Money value={period.advances} /></KeyValue>
            <KeyValue label="Buyurtmalardagi qoldiq"><Money value={metrics.balance} /></KeyValue>
            <KeyValue label="Hamkorlarga to‘langan"><Money value={period.settlements} /></KeyValue>
            <KeyValue label="Hamkorlarga to‘lanmagan"><Money value={metrics.due} /></KeyValue>
            <KeyValue label="Yakunlanganlar komissiyasi"><span className="text-blue"><Money value={metrics.commission} /></span></KeyValue>
          </dl>
        </Panel>
      </div>
      <Panel title="Oxirgi buyurtmalar" caption="Namuna so‘rovlar va joriy jarayonlar" action={<Link className="text-link" to="/orders">Barcha buyurtmalar <ArrowRight size={15} aria-hidden="true" /></Link>}>
        <OrderTable rows={recent} compact />
      </Panel>
    </>
  );
}
