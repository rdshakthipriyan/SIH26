import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, ArrowLeft, Loader2, ChevronRight } from 'lucide-react';
import { Button, Card, KioskHeader, ProgressBar, Badge } from '../components/ui';
import { AYUSH_STREAMS, AYUSH_QUESTIONNAIRES } from '../types';
import type { AyushStream, AyushQuestion } from '../types';

export default function AyushIntakePage() {
  const navigate = useNavigate();
  const isHindi = sessionStorage.getItem('medikiosk_lang') === 'hi';

  const [stream, setStream] = useState<AyushStream>('ayurveda');
  const [questions, setQuestions] = useState<AyushQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [complete, setComplete] = useState(false);

  const streamInfo = AYUSH_STREAMS.find(s => s.id === stream)!;
  const current = questions[currentIdx];
  const progress = questions.length > 0 ? ((currentIdx) / questions.length) * 100 : 0;

  useEffect(() => {
    const qs = AYUSH_QUESTIONNAIRES[stream] || [];
    setQuestions(qs);
    setCurrentIdx(0);
    setAnswers({});
    setComplete(false);
  }, [stream]);

  const getQText = (q: AyushQuestion) => isHindi ? (q.text.hi || q.text.en) : q.text.en;

  const handleSelect = async (value: string) => {
    if (!current) return;
    setLoading(true);
    setAnswers(a => ({ ...a, [current.question_id]: value }));
    await new Promise(r => setTimeout(r, 300));
    setLoading(false);
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(i => i + 1);
    } else {
      setComplete(true);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader
        title={`${streamInfo.name} Assessment`}
        subtitle="Constitutional & Symptom Analysis"
        icon={<span className="text-2xl">{streamInfo.icon}</span>}
        action={<Button variant="ghost" onClick={() => navigate('/mode')}><ArrowLeft className="h-4 w-4 mr-2" /> Back</Button>}
      />

      <div className="flex-1 px-4 md:px-8 py-8 max-w-3xl mx-auto w-full flex flex-col gap-6">
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
            <span>{current?.section || 'Intake'}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <ProgressBar value={progress} />
        </div>

        {!complete ? (
          <Card className="flex-1 flex flex-col justify-center p-12 text-center animate-slide-up">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-12 leading-tight">
              {current ? getQText(current) : 'Loading...'}
            </h2>

            <div className="grid grid-cols-1 gap-4 w-full max-w-lg mx-auto">
              {current?.options?.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => handleSelect(opt.value)}
                  disabled={loading}
                  className={`w-full text-left p-5 rounded-2xl border-2 transition-all flex items-center justify-between ${answers[current.question_id] === opt.value ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:border-brand-300 hover:bg-brand-50/50'}`}
                >
                  <span className="font-medium text-lg text-slate-800">{isHindi ? opt.label_hi : opt.label}</span>
                  {answers[current.question_id] === opt.value && <CheckCircle className="h-6 w-6 text-brand-600 shrink-0" />}
                </button>
              ))}
            </div>
          </Card>
        ) : (
          <Card className="flex-1 flex flex-col items-center justify-center p-12 text-center animate-fade-in">
            <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-6">
              <CheckCircle className="h-10 w-10" />
            </div>
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Assessment Complete</h2>
            <p className="text-slate-500 mb-8 max-w-md">Your {streamInfo.name} profile has been generated and linked to your clinical case.</p>
            <Button
              variant="primary"
              size="lg"
              onClick={() => navigate('/documents')}
              className="px-12 py-4"
            >
              Continue to Documents <ChevronRight className="h-5 w-5 ml-2" />
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
}
