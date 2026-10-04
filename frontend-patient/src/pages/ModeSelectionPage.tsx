import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft, Stethoscope } from 'lucide-react';
import { Button, Card, KioskHeader } from '../components/ui';
import { AYUSH_STREAMS } from '../types';
import { streamFromMode } from '../lib/modeMap';

export default function ModeSelectionPage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<'allopathy' | 'ayush' | null>(null);
  const [ayushStream, setAyushStream] = useState<string | null>('ayurveda');

  const handleContinue = () => {
    if (!selected) return;
    const stream = streamFromMode(selected, ayushStream || undefined);
    sessionStorage.setItem('medikiosk_mode', selected);
    sessionStorage.setItem('medikiosk_stream', stream);
    sessionStorage.setItem('medikiosk_ayush_stream', ayushStream || '');
    navigate('/conversation');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader title="Department" subtitle="Select your clinical pathway" icon={<Stethoscope className="h-6 w-6 text-white" />} />
      <div className="flex-1 px-4 md:px-8 py-8 max-w-4xl mx-auto w-full">
        <Card>
          <h2 className="text-2xl font-bold text-slate-900 mb-1">Which pathway?</h2>
          <p className="text-slate-500 mb-6">Choose your department</p>

          <div className="grid sm:grid-cols-2 gap-4 mb-6">
            <button onClick={() => { setSelected('allopathy'); setAyushStream(null); }} className={`p-6 rounded-2xl border-2 transition-all text-left ${selected === 'allopathy' ? 'border-brand-500 bg-brand-50 shadow-md' : 'border-slate-200 hover:border-brand-300 bg-white'}`}>
              <div className="text-3xl mb-3">🩺</div>
              <h3 className="text-xl font-bold text-slate-900">Allopathy</h3>
              <p className="text-sm text-slate-500 mt-1">Modern medicine — SOCRATES / HPI questionnaire</p>
            </button>
            <button onClick={() => { setSelected('ayush'); setAyushStream('ayurveda'); }} className={`p-6 rounded-2xl border-2 transition-all text-left ${selected === 'ayush' ? 'border-brand-500 bg-brand-50 shadow-md' : 'border-slate-200 hover:border-brand-300 bg-white'}`}>
              <div className="text-3xl mb-3">🌿</div>
              <h3 className="text-xl font-bold text-slate-900">AYUSH</h3>
              <p className="text-sm text-slate-500 mt-1">Ayurveda · Siddha · Unani · Homoeopathy · Yoga &amp; Naturopathy</p>
            </button>
          </div>

          {selected === 'ayush' && (
            <div className="animate-fade-in">
              <h3 className="text-lg font-bold text-slate-900 mb-3">Which AYUSH stream?</h3>
              <div className="grid sm:grid-cols-3 gap-3 mb-6">
                {AYUSH_STREAMS.map(s => (
                  <button key={s.id} onClick={() => setAyushStream(s.id)} className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all text-center ${ayushStream === s.id ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-300' : 'border-slate-200 hover:border-brand-300'}`}>
                    <span className="text-2xl">{s.icon}</span>
                    <span className="font-bold text-sm">{s.label}</span>
                    <span className="text-xs text-slate-500">{s.description}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <button onClick={() => navigate(-1)} className="text-brand-600 font-semibold text-sm hover:underline">Back</button>
            <Button onClick={handleContinue} disabled={!selected} variant="primary" size="lg">
              Begin Intake <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
