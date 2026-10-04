import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Stethoscope, Clock, Languages, ShieldCheck, Mic, Wifi, Heart } from 'lucide-react';
import { Button, Card, KioskHeader, InfoBanner, ProgressBar } from '../components/ui';

const STEPS = ['Welcome', 'Language', 'Identity', 'Department', 'Begin'];

export default function WelcomePage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);

  const handleStart = () => navigate('/language');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader title="Welcome" subtitle="MediKiosk — Patient Registration" icon={<Heart className="h-6 w-6 text-white" />} />

      <div className="flex-1 flex items-center justify-center px-6 py-10">
        <div className="w-full max-w-2xl">
          {/* Step indicator */}
          <div className="mb-10">
            <div className="flex items-center justify-between mb-3">
              {STEPS.map((s, i) => (
                <div key={s} className={`flex items-center ${i < STEPS.length - 1 ? 'flex-1' : ''}`}>
                  <div className={`flex flex-col items-center`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${i <= step ? 'bg-brand-600 text-white' : 'bg-slate-200 text-slate-500'}`}>{i + 1}</div>
                    <span className={`text-xs mt-1 font-medium ${i <= step ? 'text-brand-700' : 'text-slate-400'}`}>{s}</span>
                  </div>
                  {i < STEPS.length - 1 && <div className={`flex-1 h-0.5 mx-2 ${i < step ? 'bg-brand-400' : 'bg-slate-200'}`} />}
                </div>
              ))}
            </div>
          </div>

          {/* Step content */}
          <div className="animate-fade-in" key={step}>
            {step === 0 && (
              <Card>
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-100 text-brand-600 mb-6">
                    <Stethoscope className="h-8 w-8" />
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-3">How MediKiosk Works</h2>
                  <p className="text-slate-600 mb-8 leading-relaxed">
                    Complete your medical history before seeing the doctor.<br />
                    Speak or type — in your preferred language.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left mb-8">
                    {[
                      { icon: <Languages className="h-5 w-5 text-brand-600" />, title: 'Choose Your Language', desc: '23 Indian languages supported' },
                      { icon: <ShieldCheck className="h-5 w-5 text-brand-600" />, title: 'Secure & Private', desc: 'Your data stays confidential' },
                      { icon: <Mic className="h-5 w-5 text-brand-600" />, title: 'Voice or Touch', desc: 'Speak your answers or type them' },
                      { icon: <Clock className="h-5 w-5 text-brand-600" />, title: 'Saves Time', desc: 'Doctor gets your history instantly' },
                    ].map(({ icon, title, desc }) => (
                      <div key={title} className="flex items-start gap-3 bg-slate-50 rounded-xl p-4">
                        <div className="shrink-0 mt-0.5">{icon}</div>
                        <div>
                          <div className="font-semibold text-slate-900">{title}</div>
                          <div className="text-sm text-slate-500">{desc}</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <Button onClick={() => setStep(1)} size="lg" className="w-full sm:w-auto">
                    Continue <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            )}

            {step === 1 && (
              <Card>
                <h2 className="text-2xl font-bold text-slate-900 mb-1">What is your language?</h2>
                <p className="text-slate-500 mb-6">Select your preferred language for the session</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                  {[
                    { code: 'en', name: 'English', native: 'English' },
                    { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
                    { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
                    { code: 'te', name: 'Telugu', native: 'తెలుగు' },
                    { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
                    { code: 'mr', name: 'Marathi', native: 'मराठी' },
                    { code: 'bn', name: 'Bengali', native: 'বাংলা' },
                    { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
                    { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
                    { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
                    { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ' },
                    { code: 'as', name: 'Assamese', native: 'অসমীয়া' },
                  ].map((lang) => (
                    <button key={lang.code} onClick={() => setStep(2)} className="flex flex-col items-center gap-1 p-4 rounded-xl border-2 border-slate-200 hover:border-brand-400 hover:bg-brand-50 transition-all text-center">
                      <span className="text-xl">{lang.native}</span>
                      <span className="text-xs font-medium text-slate-600">{lang.name}</span>
                    </button>
                  ))}
                </div>
                <Button variant="ghost" onClick={() => setStep(0)}><ArrowLeft className="h-4 w-4" /> Back</Button>
              </Card>
            )}

            {step === 2 && (
              <Card>
                <h2 className="text-2xl font-bold text-slate-900 mb-1">Verify Your Identity</h2>
                <p className="text-slate-500 mb-6">Choose how you want to identify yourself</p>
                <div className="space-y-4 mb-6">
                  <button onClick={() => setStep(3)} className="w-full text-left p-5 rounded-xl border-2 border-brand-300 bg-brand-50 hover:bg-brand-100 transition-all">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-brand-600 text-white flex items-center justify-center"><ShieldCheck className="h-6 w-6" /></div>
                      <div><div className="font-bold text-slate-900">ABHA Card / Health ID</div><div className="text-sm text-slate-500">Link your official health account</div></div>
                    </div>
                  </button>
                  <button onClick={() => setStep(3)} className="w-full text-left p-5 rounded-xl border-2 border-slate-200 hover:border-brand-300 hover:bg-brand-50 transition-all">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center"><Clock className="h-6 w-6" /></div>
                      <div><div className="font-bold text-slate-900">Guest / Token Number</div><div className="text-sm text-slate-500">Continue with your OPD token (no ABHA needed)</div></div>
                    </div>
                  </button>
                </div>
                <Button variant="ghost" onClick={() => setStep(1)}><ArrowLeft className="h-4 w-4" /> Back</Button>
              </Card>
            )}

            {step === 3 && (
              <Card>
                <h2 className="text-2xl font-bold text-slate-900 mb-1">Select Your Department</h2>
                <p className="text-slate-500 mb-6">Which department are you visiting today?</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
                  {[
                    { id: 'general', label: 'General Medicine', sub: 'Allopathy' },
                    { id: 'ayush', label: 'AYUSH', sub: 'Ayurveda · Siddha · Unani · Homoeopathy · Yoga' },
                  ].map((dept) => (
                    <button key={dept.id} onClick={() => setStep(4)} className="text-left p-5 rounded-xl border-2 border-slate-200 hover:border-brand-400 hover:bg-brand-50 transition-all">
                      <div className="font-bold text-slate-900 text-lg">{dept.label}</div>
                      <div className="text-sm text-slate-500 mt-0.5">{dept.sub}</div>
                    </button>
                  ))}
                </div>
                <Button variant="ghost" onClick={() => setStep(2)}><ArrowLeft className="h-4 w-4" /> Back</Button>
              </Card>
            )}

            {step === 4 && (
              <Card>
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-600 mb-6">
                    <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-3">You're All Set!</h2>
                  <p className="text-slate-600 mb-8">Your session is ready to begin. Click below to start.</p>
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <Button onClick={() => navigate('/identity')} variant="primary" size="lg">
                      Start Registration
                    </Button>
                    <Button variant="ghost" onClick={() => setStep(0)}>Start Over</Button>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
