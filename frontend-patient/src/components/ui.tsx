import { ReactNode, useEffect, useState } from 'react';
import { CheckCircle2, XCircle, AlertCircle, Info, Loader2, Wifi, WifiOff, ShieldCheck, AlertTriangle, RefreshCw } from 'lucide-react';

// ─── Loading ────────────────────────────────────────────────────────────────
export const Spinner = ({ size = 'md', className = '' }: { size?: 'sm' | 'md' | 'lg'; className?: string }) => {
  const sz = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' }[size];
  return <Loader2 className={`animate-spin text-brand-600 ${sz} ${className}`} aria-label="Loading" />;
};

export const LoadingState = ({ title = 'Loading…', detail }: { title?: string; detail?: string }) => (
  <div className="flex flex-col items-center justify-center py-16 px-6 text-center animate-fade-in" role="status" aria-live="polite">
    <Spinner size="lg" />
    <h3 className="mt-4 text-lg font-semibold text-slate-700">{title}</h3>
    {detail && <p className="mt-1 text-sm text-slate-500 max-w-md">{detail}</p>}
  </div>
);

// ─── Empty / Error / Info ────────────────────────────────────────────────────
export const EmptyState = ({ title, detail, icon, action }: { title: string; detail?: string; icon?: ReactNode; action?: ReactNode }) => (
  <div className="flex flex-col items-center justify-center py-16 px-6 text-center animate-fade-in" role="status">
    {icon || <Info className="h-12 w-12 text-slate-400" />}
    <h3 className="mt-4 text-lg font-semibold text-slate-700">{title}</h3>
    {detail && <p className="mt-1 text-sm text-slate-500 max-w-md">{detail}</p>}
    {action && <div className="mt-6">{action}</div>}
  </div>
);

export const ErrorState = ({ title = 'Something went wrong', detail, onRetry }: { title?: string; detail?: string; onRetry?: () => void }) => (
  <div className="flex flex-col items-center justify-center py-16 px-6 text-center animate-fade-in" role="alert">
    <XCircle className="h-12 w-12 text-red-500" />
    <h3 className="mt-4 text-lg font-semibold text-slate-800">{title}</h3>
    {detail && <p className="mt-1 text-sm text-slate-600 max-w-md">{detail}</p>}
    {onRetry && <button onClick={onRetry} className="mt-6 inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-white font-semibold hover:bg-brand-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600">
      <RefreshCw className="h-4 w-4" /> Try again
    </button>}
  </div>
);

export const InfoBanner = ({ kind = 'info', title, detail, action, className = '' }: { kind?: 'info' | 'success' | 'warning' | 'error'; title: string; detail?: string; action?: ReactNode; className?: string }) => {
  const styles = {
    info: { bg: 'bg-blue-50', text: 'text-blue-900', icon: <Info className="h-5 w-5 text-blue-500" />, ring: 'ring-blue-200' },
    success: { bg: 'bg-emerald-50', text: 'text-emerald-900', icon: <CheckCircle2 className="h-5 w-5 text-emerald-500" />, ring: 'ring-emerald-200' },
    warning: { bg: 'bg-amber-50', text: 'text-amber-900', icon: <AlertTriangle className="h-5 w-5 text-amber-500" />, ring: 'ring-amber-200' },
    error: { bg: 'bg-red-50', text: 'text-red-900', icon: <XCircle className="h-5 w-5 text-red-500" />, ring: 'ring-red-200' },
  }[kind];
  return (
    <div className={`flex items-start gap-3 rounded-xl ${styles.bg} ${styles.ring} ring-1 p-4 animate-fade-in ${className}`} role={kind === 'error' || kind === 'warning' ? 'alert' : 'status'}>
      <div className="shrink-0 mt-0.5">{styles.icon}</div>
      <div className="flex-1 min-w-0">
        <h4 className={`text-sm font-semibold ${styles.text}`}>{title}</h4>
        {detail && <p className={`mt-0.5 text-sm ${styles.text} opacity-90`}>{detail}</p>}
        {action && <div className="mt-3">{action}</div>}
      </div>
    </div>
  );
};

// ─── Buttons ────────────────────────────────────────────────────────────────
export const Button = ({ children, onClick, variant = 'primary', size = 'md', disabled, type = 'button', className = '', ariaLabel }: any) => {
  const variants: Record<string, string> = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700 active:bg-brand-800 shadow-sm',
    secondary: 'bg-white text-brand-700 border border-brand-200 hover:bg-brand-50',
    ghost: 'bg-transparent text-slate-700 hover:bg-slate-100',
    danger: 'bg-red-600 text-white hover:bg-red-700 shadow-sm',
    success: 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm',
  };
  const sizes: Record<string, string> = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2.5 text-sm', lg: 'px-6 py-3.5 text-base', xl: 'px-8 py-4 text-lg' };
  return <button type={type} onClick={onClick} disabled={disabled} aria-label={ariaLabel} className={`inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}>{children}</button>;
};

// ─── Card ───────────────────────────────────────────────────────────────────
export const Card = ({ children, className = '', title, subtitle, action }: { children: ReactNode; className?: string; title?: string; subtitle?: string; action?: ReactNode }) => (
  <div className={`bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden animate-fade-in ${className}`}>
    {(title || action) && (
      <div className="px-5 py-4 border-b border-slate-100 flex items-start justify-between gap-4">
        <div className="min-w-0">
          {title && <h3 className="text-lg font-semibold text-slate-900">{title}</h3>}
          {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>
    )}
    <div className="p-5">{children}</div>
  </div>
);

// ─── Badge ──────────────────────────────────────────────────────────────────
export const Badge = ({ children, variant = 'default' }: { children: ReactNode; variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple' }) => {
  const v = {
    default: 'bg-slate-100 text-slate-700',
    success: 'bg-emerald-100 text-emerald-700',
    warning: 'bg-amber-100 text-amber-700',
    danger: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700',
    purple: 'bg-violet-100 text-violet-700',
  }[variant];
  return <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${v}`}>{children}</span>;
};

// ─── Progress ───────────────────────────────────────────────────────────────
export const ProgressBar = ({ value, label, variant = 'default' }: { value: number; label?: string; variant?: 'default' | 'success' | 'warning' }) => {
  const v = { default: 'bg-brand-600', success: 'bg-emerald-600', warning: 'bg-amber-500' }[variant];
  return (
    <div>
      {label && <div className="flex items-center justify-between text-xs font-semibold text-slate-600 mb-1.5"><span>{label}</span><span>{Math.round(value)}%</span></div>}
      <div className="h-2.5 w-full rounded-full bg-slate-200 overflow-hidden"><div className={`h-full ${v} rounded-full transition-all duration-500`} style={{ width: `${Math.min(100, Math.max(0, value))}%` }} /></div>
    </div>
  );
};

// ─── Input ──────────────────────────────────────────────────────────────────
export const Input = ({ label, value, onChange, type = 'text', placeholder, helper, error, disabled, required, autoFocus, name }: any) => (
  <div className="space-y-1.5">
    {label && <label className="block text-sm font-semibold text-slate-700">{label}{required && <span className="text-red-500 ml-1">*</span>}</label>}
    <input type={type} name={name} value={value || ''} onChange={onChange} placeholder={placeholder} disabled={disabled} autoFocus={autoFocus} aria-invalid={!!error} className={`block w-full rounded-xl border ${error ? 'border-red-400 focus:border-red-500' : 'border-slate-300 focus:border-brand-500'} bg-white px-4 py-2.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:opacity-50 transition-colors`} />
    {error && <p className="text-xs text-red-600 flex items-center gap-1"><AlertCircle className="h-3 w-3" />{error}</p>}
    {helper && !error && <p className="text-xs text-slate-500">{helper}</p>}
  </div>
);

export const Select = ({ label, value, onChange, options, helper, required, disabled, name }: any) => (
  <div className="space-y-1.5">
    {label && <label className="block text-sm font-semibold text-slate-700">{label}{required && <span className="text-red-500 ml-1">*</span>}</label>}
    <select value={value || ''} onChange={onChange} disabled={disabled} name={name} className="block w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:opacity-50">
      <option value="">Select…</option>
      {options.map((o: any) => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
    {helper && <p className="text-xs text-slate-500">{helper}</p>}
  </div>
);

export const Textarea = ({ label, value, onChange, placeholder, rows = 3, helper, required, disabled, name }: any) => (
  <div className="space-y-1.5">
    {label && <label className="block text-sm font-semibold text-slate-700">{label}{required && <span className="text-red-500 ml-1">*</span>}</label>}
    <textarea name={name} rows={rows} value={value || ''} onChange={onChange} placeholder={placeholder} disabled={disabled} className="block w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:opacity-50" />
    {helper && <p className="text-xs text-slate-500">{helper}</p>}
  </div>
);

// ─── Connection / Network status (offline indicator) ────────────────────────
export const NetworkStatus = () => {
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setOnline(true); const off = () => setOnline(false);
    window.addEventListener('online', on); window.addEventListener('offline', off);
    return () => { window.removeEventListener('online', on); window.removeEventListener('offline', off); };
  }, []);
  if (online) return null;
  return (
    <div className="fixed top-3 left-1/2 -translate-x-1/2 z-50 bg-amber-500 text-white text-sm font-semibold px-4 py-2 rounded-full shadow-lg flex items-center gap-2 animate-fade-in" role="status">
      <WifiOff className="h-4 w-4" /> You are offline — some features may be limited
    </div>
  );
};

// ─── Stepper ────────────────────────────────────────────────────────────────
export const Stepper = ({ steps, current }: { steps: string[]; current: number }) => (
  <ol className="flex flex-wrap items-center gap-2" aria-label="Progress">
    {steps.map((s, i) => {
      const done = i < current; const active = i === current;
      return (
        <li key={i} className="flex items-center gap-2">
          <span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-colors ${done ? 'bg-emerald-500 text-white' : active ? 'bg-brand-600 text-white ring-4 ring-brand-200' : 'bg-slate-200 text-slate-500'}`}>{done ? '✓' : i + 1}</span>
          <span className={`text-sm font-semibold ${done ? 'text-emerald-700' : active ? 'text-brand-700' : 'text-slate-500'}`}>{s}</span>
          {i < steps.length - 1 && <span className="text-slate-300 mx-1">→</span>}
        </li>
      );
    })}
  </ol>
);

// ─── Skeleton ───────────────────────────────────────────────────────────────
export const Skeleton = ({ className = '' }: { className?: string }) => (
  <div className={`animate-pulse rounded-lg bg-slate-200/70 ${className}`} aria-hidden />
);

// ─── Section header (kiosk-friendly large text) ──────────────────────────────
export const KioskHeader = ({ title, subtitle, icon, action }: { title: string; subtitle?: string; icon?: ReactNode; action?: ReactNode }) => (
  <header className="px-6 py-5 bg-gradient-to-r from-brand-700 via-brand-600 to-brand-800 text-white">
    <div className="flex items-center justify-between gap-4 max-w-6xl mx-auto">
      <div className="flex items-center gap-4 min-w-0">
        {icon && <div className="shrink-0 bg-white/15 backdrop-blur rounded-xl p-3">{icon}</div>}
        <div className="min-w-0">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight truncate">{title}</h1>
          {subtitle && <p className="text-brand-100 text-sm md:text-base mt-0.5 truncate">{subtitle}</p>}
        </div>
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  </header>
);

// ─── Mode toggle (Kiosk / BYOD) ─────────────────────────────────────────────
export const ModePill = ({ mode }: { mode: 'kiosk' | 'byod' }) => (
  <div className="inline-flex items-center gap-1.5 rounded-full bg-white/15 backdrop-blur px-3 py-1 text-xs font-semibold">
    {mode === 'kiosk' ? <ShieldCheck className="h-3.5 w-3.5" /> : <Wifi className="h-3.5 w-3.5" />}
    {mode === 'kiosk' ? 'Kiosk' : 'BYOD'}
  </div>
);
