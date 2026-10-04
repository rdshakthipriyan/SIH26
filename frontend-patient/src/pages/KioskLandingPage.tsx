import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, Mic, Wifi, Globe, ShieldCheck, Clock, Languages, Smartphone } from 'lucide-react';
import { Card, Button } from '../components/ui';

export default function KioskLandingPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'kiosk' | 'byod'>('kiosk');

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-slate-50 to-indigo-50 flex flex-col">
      {/* Hero */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 text-center">
        <div className="mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-brand-600 text-white shadow-xl mb-6">
            <Stethoscope className="h-10 w-10" />
          </div>
          <h1 className="text-5xl md:text-6xl font-black text-slate-900 tracking-tight mb-3">
            MediKiosk
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            AI-Assisted Multilingual Patient Intake<br />
            <span className="text-brand-600 font-semibold">Ayush &amp; Allopathy</span>
          </p>
        </div>

        {/* Mode selector */}
        <div className="flex gap-3 mb-12 animate-slide-up">
          <button
            onClick={() => setMode('kiosk')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-full font-semibold text-sm transition-all ${mode === 'kiosk' ? 'bg-brand-600 text-white shadow-lg' : 'bg-white text-slate-600 border border-slate-200 hover:border-brand-300'}`}
          >
            <ShieldCheck className="h-4 w-4" /> Hospital Kiosk
          </button>
          <button
            onClick={() => setMode('byod')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-full font-semibold text-sm transition-all ${mode === 'byod' ? 'bg-brand-600 text-white shadow-lg' : 'bg-white text-slate-600 border border-slate-200 hover:border-brand-300'}`}
          >
            <Smartphone className="h-4 w-4" /> My Phone (BYOD)
          </button>
        </div>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-3 mb-14 animate-slide-up" style={{ animationDelay: '100ms' }}>
          {[
            { icon: <Languages className="h-4 w-4" />, label: '23 Indian Languages' },
            { icon: <Mic className="h-4 w-4" />, label: 'Voice + Touch' },
            { icon: <Clock className="h-4 w-4" />, label: 'Save Doctor Time' },
            { icon: <Wifi className="h-4 w-4" />, label: 'ABHA Connected' },
          ].map(({ icon, label }) => (
            <div key={label} className="flex items-center gap-2 bg-white border border-slate-200 rounded-full px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">
              {icon} {label}
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="w-full max-w-lg animate-slide-up" style={{ animationDelay: '200ms' }}>
          <Button onClick={() => navigate('/welcome')} variant="primary" size="xl" className="w-full text-lg shadow-xl hover:shadow-2xl transition-shadow">
            Begin Registration
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
          </Button>
          <p className="text-xs text-slate-500 mt-4">
            By continuing, you agree to the consent declaration and data handling terms.
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-5 border-t border-slate-200 bg-white/60">
        <p className="text-xs text-slate-400">
          MediKiosk v1.0 &nbsp;·&nbsp; Supporting Allopathy &amp; AYUSH Departments &nbsp;·&nbsp; ABDM Connected
        </p>
      </div>
    </div>
  );
}
