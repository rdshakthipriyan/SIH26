import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft, ShieldCheck, User, Smartphone, CheckCircle, Loader2 } from 'lucide-react';
import { Button, Card, KioskHeader, Input } from '../components/ui';
import { sessionApi } from '../services/api';
import { normalizeMode } from '../lib/modeMap';

export default function PatientIdentityPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'abha' | 'guest'>('guest');
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [token, setToken] = useState('');
  const [consent, setConsent] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleContinue = async () => {
    setLoading(true);
    setError(null);
    try {
      const lang = sessionStorage.getItem('medikiosk_lang') || 'en';
      const department = sessionStorage.getItem('medikiosk_department') || 'General Medicine';
      const apiMode = normalizeMode(sessionStorage.getItem('medikiosk_mode') || 'allopathy');
      const isGuest = mode === 'guest';
      const payload: any = {
        is_guest: isGuest,
        patient_name: name || (isGuest ? 'Guest' : 'Patient'),
        patient_age: age ? String(age) : undefined,
        patient_gender: gender || undefined,
        consent_given: consent,
        consent_scope: ['intake', 'voice', 'ocr', 'fhir'],
        abha_address: (!isGuest && name.includes('-')) ? name : undefined,
        token_number: isGuest ? token || undefined : undefined,
        department,
        mode: apiMode,
        language_code: lang,
      };
      if (!isGuest && name.includes('-')) {
        payload.abha_id = name;
      }
      const res = await sessionApi.start(payload);
      sessionStorage.setItem('medikiosk_token', res.token);
      sessionStorage.setItem('medikiosk_session', JSON.stringify(res));
      navigate('/mode');
    } catch (e: any) {
      console.error('Session start failed', e);
      const detail = e?.response?.data?.detail;
      let msg = 'Could not start session. Please check your connection.';
      if (e?.response?.status === 422 && detail) {
        const lines = Array.isArray(detail)
          ? detail.map((d: any) => `${(d.loc || []).slice(-1)[0] || 'field'}: ${d.msg}`).join('; ')
          : typeof detail === 'string' ? detail : JSON.stringify(detail);
        msg = `Server rejected the form — ${lines}`;
      } else if (e?.message) {
        msg = `Could not start session (${e.message})`;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader title="Your Identity" subtitle="ABHA or Guest registration — no one is blocked" icon={<ShieldCheck className="h-6 w-6 text-white" />} />
      <div className="flex-1 px-4 md:px-8 py-8 max-w-3xl mx-auto w-full">
        <Card>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">How would you like to register?</h2>
          <p className="text-slate-500 mb-6">You do not need an ABHA card to use MediKiosk</p>

          <div className="grid sm:grid-cols-2 gap-3 mb-6">
            <button onClick={() => setMode('abha')} className={`flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all ${mode === 'abha' ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:border-brand-300'}`}>
              <div className="w-10 h-10 rounded-lg bg-brand-100 text-brand-700 flex items-center justify-center"><ShieldCheck className="h-5 w-5" /></div>
              <div><div className="font-bold">ABHA Card / Health ID</div><div className="text-xs text-slate-500">Link official account</div></div>
            </button>
            <button onClick={() => setMode('guest')} className={`flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all ${mode === 'guest' ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:border-brand-300'}`}>
              <div className="w-10 h-10 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center"><User className="h-5 w-5" /></div>
              <div><div className="font-bold">Guest / Token</div><div className="text-xs text-slate-500">Continue with OPD token</div></div>
            </button>
          </div>

          {mode === 'guest' && (
            <div className="space-y-4 animate-fade-in">
              <div className="grid sm:grid-cols-2 gap-4">
                <Input label="Full Name" value={name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)} placeholder="Your name" />
                <Input label="Age" type="number" value={age} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAge(e.target.value)} placeholder="Age" />
              </div>
              <Input label="Gender" value={gender} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGender(e.target.value)} placeholder="Male / Female / Other" />
              <Input label="OPD Token Number" value={token} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setToken(e.target.value)} placeholder="e.g. 101" />
            </div>
          )}

          {mode === 'abha' && (
            <div className="space-y-4 animate-fade-in">
              <Input label="ABHA Address / Health ID" value={name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)} placeholder="Enter ABHA address" />
              <Input label="Name (as on ABHA)" value={age} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAge(e.target.value)} placeholder="Name" />
              <div className="rounded-xl bg-brand-50 border border-brand-200 p-4 text-sm text-brand-800 font-medium flex items-center gap-3">
                <ShieldCheck className="h-5 w-5 text-brand-600 shrink-0" /> ABHA integration is currently mock; production integration requires production ABHA credentials.
              </div>
            </div>
          )}

          <div className="mt-6 flex items-start gap-2">
            <button onClick={() => setConsent(!consent)} className={`mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${consent ? 'bg-brand-600 border-brand-600' : 'border-slate-300'}`} aria-label="Consent"><CheckCircle className={`h-3.5 w-3.5 text-white ${consent ? 'opacity-100' : 'opacity-0'}`} /></button>
            <label className="text-sm text-slate-600 cursor-pointer select-none">
              I consent to the collection and use of my clinical data for this consultation, including voice input, document processing, and FHIR export.
            </label>
          </div>

          {error && <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-4">{error}</div>}

          <div className="mt-6 flex items-center justify-between">
            <button onClick={() => navigate(-1)} className="text-brand-600 hover:underline font-semibold text-sm">Back</button>
            <Button onClick={handleContinue} disabled={!consent || !name || loading} variant="primary" size="lg">
              {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Starting...</> : <>Continue <ArrowRight className="h-4 w-4" /></>}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
