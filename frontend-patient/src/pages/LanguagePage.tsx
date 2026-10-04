import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft, Search, Mic, Globe } from 'lucide-react';
import { Button, Card, KioskHeader, LoadingState, ErrorState, Input, InfoBanner } from '../components/ui';
import { languageApi } from '../services/api';
import type { Language } from '../types';

// 23 constitutionally recognized Indian languages
const ALL_LANGUAGES: { code: string; name: string; native: string; flag: string }[] = [
  { code: 'as', name: 'Assamese', native: 'অসমীয়া', flag: '🇮🇳' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা', flag: '🇮🇳' },
  { code: 'brx', name: 'Bodo', native: 'बड़ो', flag: '🇮🇳' },
  { code: 'doi', name: 'Dogri', native: 'डोगरी', flag: '🇮🇳' },
  { code: 'en', name: 'English', native: 'English', flag: '🇬🇧' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'ks', name: 'Kashmiri', native: 'کٲشُر', flag: '🇮🇳' },
  { code: 'kok', name: 'Konkani', native: 'कोंकणी', flag: '🇮🇳' },
  { code: 'mai', name: 'Maithili', native: 'मैथिली', flag: '🇮🇳' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳' },
  { code: 'mni', name: 'Manipuri', native: 'মৈতৈলোন', flag: '🇮🇳' },
  { code: 'mr', name: 'Marathi', native: 'मराठी', flag: '🇮🇳' },
  { code: 'ne', name: 'Nepali', native: 'नेपाली', flag: '🇳🇵' },
  { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ', flag: '🇮🇳' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
  { code: 'sa', name: 'Sanskrit', native: 'संस्कृतम्', flag: '🇮🇳' },
  { code: 'sat', name: 'Santali', native: 'ᱥᱟᱛᱟᱞᱤ', flag: '🇮🇳' },
  { code: 'sd', name: 'Sindhi', native: 'سنڌي', flag: '🇮🇳' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' },
  { code: 'ur', name: 'Urdu', native: 'اردو', flag: '🇮🇳' },
];

const MAJOR_LANGUAGES = ['hi', 'ta', 'te', 'ml', 'bn', 'mr', 'gu', 'kn', 'en', 'or', 'pa', 'as'];

export default function LanguagePage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [langs, setLangs] = useState<Language[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    languageApi.list().then(data => {
      setLangs(Array.isArray(data) ? data : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const langMap = Object.fromEntries(langs.map(l => [l.code, l]));

  const filtered = ALL_LANGUAGES.filter(l =>
    !search || l.name.toLowerCase().includes(search.toLowerCase()) || l.native.includes(search)
  );

  const displayLangs = showAll ? filtered : filtered.filter(l => MAJOR_LANGUAGES.includes(l.code));

  const handleContinue = () => {
    if (!selected) return;
    sessionStorage.setItem('medikiosk_lang', selected);
    navigate('/identity');
  };

  if (loading) return <div className="min-h-screen bg-slate-50"><KioskHeader title="Language Selection" subtitle="Choose your preferred language" icon={<Globe className="h-6 w-6 text-white" />} /><LoadingState detail="Loading language options…" /></div>;
  if (error) return <div className="min-h-screen bg-slate-50"><KioskHeader title="Language Selection" icon={<Globe className="h-6 w-6 text-white" />} /><div className="p-6"><ErrorState title="Could not load languages" detail={error} onRetry={() => window.location.reload()} /></div></div>;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader title="Language Selection" subtitle="Choose your preferred language" icon={<Globe className="h-6 w-6 text-white" />} />

      <div className="flex-1 px-4 md:px-8 py-8 max-w-4xl mx-auto w-full">
        <Card className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search language…"
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                  aria-label="Search languages"
                />
              </div>
            </div>
          </div>

          {!showAll && (
            <button onClick={() => setShowAll(true)} className="text-sm text-brand-600 hover:text-brand-700 font-semibold mb-4 underline">
              Show all {ALL_LANGUAGES.length} languages
            </button>
          )}

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {displayLangs.map(lang => {
              const backend = langMap[lang.code];
              const asr = backend?.capabilities?.asr;
              const tts = backend?.capabilities?.tts;
              return (
                <button
                  key={lang.code}
                  onClick={() => setSelected(lang.code)}
                  className={`flex flex-col items-center gap-1 p-4 rounded-xl border-2 transition-all text-center ${selected === lang.code ? 'border-brand-500 bg-brand-50 ring-2 ring-brand-300' : 'border-slate-200 hover:border-brand-300 hover:bg-brand-50/50'}`}
                >
                  <span className="text-3xl" aria-hidden>{lang.flag}</span>
                  <span className={`font-bold text-sm ${selected === lang.code ? 'text-brand-700' : 'text-slate-800'}`}>{lang.native}</span>
                  <span className="text-xs text-slate-500">{lang.name}</span>
                  <div className="flex gap-1.5 mt-1">
                    {asr && <span title="ASR supported" className="text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded-full">ASR</span>}
                    {tts && <span title="TTS supported" className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full">TTS</span>}
                  </div>
                </button>
              );
            })}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <Button variant="ghost" onClick={() => navigate(-1)}><ArrowLeft className="h-4 w-4" /> Back</Button>
            <Button onClick={handleContinue} disabled={!selected} variant="primary" size="lg">
              Continue <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
