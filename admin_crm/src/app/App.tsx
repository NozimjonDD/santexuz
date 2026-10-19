import { Component, lazy, Suspense, type ErrorInfo, type ReactNode } from 'react';
import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router';
import { StoreProvider } from './store';
import Shell from './Shell';
import { EmptyState } from '../shared/ui';

const Dashboard = lazy(() => import('../features/dashboard/Dashboard'));
const Orders = lazy(() => import('../features/orders/Orders'));
const OrderDetail = lazy(() => import('../features/orders/OrderDetail'));
const Directory = lazy(() => import('../features/directory/Directory'));
const Finance = lazy(() => import('../features/finance/Finance'));
const Reports = lazy(() => import('../features/reports/Reports'));
const Contracts = lazy(() => import('../features/management/Contracts'));
const Reviews = lazy(() => import('../features/management/Reviews'));
const Audit = lazy(() => import('../features/management/Audit'));
const Settings = lazy(() => import('../features/management/Settings'));

class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(_error: Error, _info: ErrorInfo) { /* Deliberately omit private data from browser logs. */ }
  render() { return this.state.failed ? <div className="fatal-error"><h1>Sahifani ochib bo‘lmadi</h1><p>Demo sessiyasini qayta yuklang. Lokal o‘zgarishlar boshlang‘ich holatga qaytadi.</p><button className="button primary" onClick={() => window.location.reload()}>Qayta yuklash</button></div> : this.props.children; }
}
export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <StoreProvider>
          <Suspense fallback={<div className="app-loading" role="status"><span className="loading-dot" />Santex ish maydoni yuklanmoqda…</div>}>
            <Routes>
              <Route element={<Shell />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="orders" element={<Orders />} />
                <Route path="orders/:id" element={<OrderDetail />} />
                {(['customers', 'plumbers', 'shops'] as const).map(kind => (
                  <Route key={kind} path={kind}>
                    <Route index element={<Directory key={kind} kind={kind} />} />
                    <Route path=":id" element={<Directory key={`${kind}-detail`} kind={kind} />} />
                  </Route>
                ))}
                <Route path="catalog">
                  <Route index element={<Navigate to="services" replace />} />
                  {(['services', 'materials'] as const).map(kind => (
                    <Route key={kind} path={kind}>
                      <Route index element={<Directory key={kind} kind={kind} />} />
                      <Route path=":id" element={<Directory key={`${kind}-detail`} kind={kind} />} />
                    </Route>
                  ))}
                </Route>
                <Route path="finance" element={<Finance />} />
                <Route path="reports" element={<Reports />} />
                <Route path="contracts" element={<Contracts />} />
                <Route path="reviews" element={<Reviews />} />
                <Route path="audit" element={<Audit />} />
                <Route path="settings" element={<Settings />} />
                <Route path="*" element={<EmptyState title="Sahifa topilmadi" text="Manzilni tekshiring yoki bosh sahifaga qayting." action={<Link className="button primary" to="/dashboard">Bosh sahifaga</Link>} />} />
              </Route>
            </Routes>
          </Suspense>
        </StoreProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
