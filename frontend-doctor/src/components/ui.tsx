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
    {detail && <p className="mt-1 text-sm text-slate-500 max-w-md">{detail}</p>}
    {onRetry && (
      <Button variant="secondary" onClick={onRetry} className="mt-6 flex items-center gap-2 mx-auto">
        <RefreshCw className="h-4 w-4" /> Retry
      </Button>
    )}
  </div>
);

// ─── Form Elements ───────────────────────────────────────────────────────────
export const Input = ({ label, value, onChange, type = 'text', placeholder, required, error }: any) => (
  <div className="space-y-1.5">
    {label && <label className="text-sm font-medium text-slate-700">{label}</label>}
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      className={`w-full px-4 py-2.5 rounded-xl border-2 transition-all outline-none ${error ? 'border-red-500 focus:border-red-600' : 'border-slate-200 focus:border-brand-500'}`}
    />
    {error && <p className="text-xs text-red-500">{error}</p>}
  </div>
);

export const Button = ({ children, variant = 'primary', size = 'md', className = '', ...props }: any) => {
  const variants = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700 shadow-sm',
    secondary: 'bg-white text-slate-700 border-2 border-slate-200 hover:bg-slate-50',
    ghost: 'bg-transparent text-slate-600 hover:bg-slate-100',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    success: 'bg-emerald-600 text-white hover:bg-emerald-700',
  };
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg font-semibold',
  };
  return <button className={`rounded-xl transition-all active:scale-95 flex items-center justify-center gap-2 ${variants[variant as keyof typeof variants]} ${sizes[size as keyof typeof sizes]} ${className}`} {...props}>{children}</button>;
};

export const Card = ({ children, className = '', title, subtitle }: any) => (
  <div className={`bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden ${className}`}>
    {(title || subtitle) && (
      <div className="px-6 py-4 border-b border-slate-100">
        {title && <h3 className="text-lg font-bold text-slate-900">{title}</h3>}
        {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
      </div>
    )}
    <div className="p-6">{children}</div>
  </div>
);

export const Badge = ({ children, variant = 'neutral', className = '' }: any) => {
  const variants = {
    neutral: 'bg-slate-100 text-slate-600',
    brand: 'bg-brand-100 text-brand-700',
    success: 'bg-emerald-100 text-emerald-700',
    danger: 'bg-red-100 text-red-700',
    warning: 'bg-amber-100 text-amber-700',
  };
  return <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${variants[variant as keyof typeof variants]} ${className}`}>{children}</span>;
};

export const ProgressBar = ({ progress, label }: { progress: number; label?: string }) => (
  <div className="w-full space-y-2">
    {label && <div className="flex justify-between text-xs font-medium text-slate-500"><span>{label}</span><span>{Math.round(progress)}%</span></div>}
    <div className="h-3 w-full bg-slate-200 rounded-full overflow-hidden">
      <div className="h-full bg-brand-600 transition-all duration-500 ease-out" style={{ width: `${progress}%` }} />
    </div>
  </div>
);

export const KioskHeader = ({ title, subtitle, icon }: any) => (
  <div className="bg-brand-600 text-white px-6 py-8 rounded-b-[2rem] shadow-lg flex items-center gap-4 animate-slide-up">
    {icon && <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-sm">{icon}</div>}
    <div>
      <h1 className="text-2xl md:text-3xl font-bold leading-tight">{title}</h1>
      {subtitle && <p className="text-brand-100 opacity-90">{subtitle}</p>}
    </div>
  </div>
);

export const InfoBanner = ({ title, detail, type = 'info', icon }: any) => {
  const themes = {
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-red-50 text-red-700 border-red-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  };
  return (
    <div className={`p-4 rounded-2xl border-l-4 flex gap-3 animate-fade-in ${themes[type as keyof typeof themes]}`}>
      {icon || <Info className="h-5 w-5 shrink-0" />}
      <div>
        <h4 className="font-bold text-sm">{title}</h4>
        {detail && <p className="text-xs opacity-90">{detail}</p>}
      </div>
    </div>
  );
};
