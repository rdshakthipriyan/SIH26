import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Volume2, ChevronRight, ArrowLeft, AlertTriangle, Loader2, Mic, Check, X } from 'lucide-react';
import { Button, Card, KioskHeader, ProgressBar, Spinner } from '../components/ui';
import { conversationApi, voiceApi } from '../services/api';

export default function ConversationPage() {
  const navigate = useNavigate();
  const sessionData = JSON.parse(sessionStorage.getItem('medikiosk_session') || '{}');
  const sessionId = sessionData.session_id || 'demo-session-001';
  // CRITICAL FIX: correct storage key spelling AND support all 3 languages
  const lang = sessionStorage.getItem('medikiosk_lang') || 'en';
  const isHindi = lang === 'hi';
  const isTamil = lang === 'ta';
  const mode = sessionStorage.getItem('medikiosk_mode') || 'allopathy';
  const stream = sessionStorage.getItem('medikiosk_stream') || (mode === 'ayush' ? 'ayurveda' : null);

  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [input, setInput] = useState('');
  const [progress, setProgress] = useState(0);
  const [redFlags, setRedFlags] = useState<string[]>([]);
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [showVoiceConfirm, setShowVoiceConfirm] = useState(false);
  const [ayushProfile, setAyushProfile] = useState<any>(null);

  // Track how the current input was produced
  const inputModeRef = useRef<'touch' | 'voice'>('touch');

  const chunks = useRef<Blob[]>([]);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Get localized question text: prefer selected language, fallback to English
  const getQText = (q: any) => {
    if (!q?.text) return '';
    // Support all 3 demo languages; prefer selected, fallback to English
    if (lang === 'ta' && q.text.ta) return q.text.ta;
    if (lang === 'hi' && q.text.hi) return q.text.hi;
    return q.text.en || Object.values(q.text)[0] || '';
  };

  const playAudio = useCallback((audioBase64: string) => {
    // Clean up any previous audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    try {
      // Mock provider emits WAV silence; real Sarvam emits MP3. Use audio/wav for our mock
      // so the browser doesn't reject the stream. Both work in modern browsers.
      const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
      audioRef.current = audio;
      setIsSpeaking(true);
      audio.onended = () => {
        setIsSpeaking(false);
        audioRef.current = null;
      };
      audio.onerror = () => {
        setIsSpeaking(false);
        audioRef.current = null;
      };
      audio.play().catch(() => {
        setIsSpeaking(false);
      });
    } catch {
      setIsSpeaking(false);
    }
  }, []);

  const speakQuestion = async (q: any) => {
    if (!q) return;
    try {
      // Send actual selected language; backend must receive it for TTS provider
      const result = await voiceApi.speak(sessionId, getQText(q), lang);
      // Play real TTS audio from backend if valid audio base64 is present
      if (result?.audio_base64 && result.audio_base64 !== 'MOCK_AUDIO_DATA' && result.status !== 'unavailable') {
        // Additional check: base64 must decode to valid audio
        try {
          const decoded = atob(result.audio_base64);
          if (decoded.length > 0) {
            playAudio(result.audio_base64);
            return;
          }
        } catch { /* invalid base64 */ }
      }
      // DEMO/MOCK fallback: clearly indicate no real audio available
      setIsSpeaking(false);
    } catch {
      setIsSpeaking(false);
    }
  };

  // Initialize: start conversation with backend
  useEffect(() => {
    const init = async () => {
      if (sessionId === 'demo-session-001') {
        navigate('/mode');
        return;
      }
      try {
        const res = await conversationApi.start(sessionId, {
          mode,
          stream: stream || undefined,
          language_code: lang,
        });
        const q = res.first_question || res;
        setCurrentQuestion(q);
        setProgress(res.completion_percentage || 0);
        speakQuestion(q);
      } catch (e) {
        console.error('Failed to start conversation', e);
      } finally {
        setLoading(false);
      }
    };
    init();

    return () => {
      // Cleanup audio on unmount
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // Voice confirmation flow
  const handleVoiceConfirm = async () => {
    setShowVoiceConfirm(false);
    setInput(voiceTranscript);
    inputModeRef.current = 'voice_edited';
    await handleSubmitAnswer('voice_edited', voiceTranscript);
  };

  const handleVoiceReject = () => {
    setShowVoiceConfirm(false);
    setVoiceTranscript('');
    setIsRecording(false);
  };

  const handleSubmitAnswer = async (overrideInputMode?: 'voice_edited', overrideText?: string) => {
    const textToSubmit = overrideText || input;
    if (!textToSubmit.trim() || !currentQuestion) return;
    setLoading(true);
    try {
      const usedInputMode = overrideInputMode || inputModeRef.current;
      // Build answer payload: for single-choice questions, use the selected option's stable value.
      // Match input text against ALL localized option labels to find the correct internal value.
      let answerValue: string | undefined = undefined;
      if (currentQuestion && currentQuestion.options && Array.isArray(currentQuestion.options)) {
        const textLower = textToSubmit.trim().toLowerCase();
        const opt = currentQuestion.options.find((o: any) => {
          // Match against every translation of the option label
          const labels = [o.text?.en, o.text?.hi, o.text?.ta, o.text?.te, o.text?.ml, o.label, o.label_en, o.label_hi, o.label_ta].filter(Boolean);
          return labels.some(l => l.trim().toLowerCase() === textLower) ||
                 (o.value && String(o.value).toLowerCase() === textLower);
        });
        if (opt) {
          answerValue = opt.value ? String(opt.value) : undefined;
        }
      }

      const res = await conversationApi.respond(sessionId, {
        answer_text: textToSubmit,
        input_mode: usedInputMode,
        raw_transcript: usedInputMode.startsWith('voice') ? textToSubmit : undefined,
        answer_value: answerValue || textToSubmit,
        question_id: currentQuestion?.question_id,
      });
      setInput('');
      setVoiceTranscript('');
      inputModeRef.current = 'touch'; // Reset for next question
      setProgress(res.completion_percentage || 0);
      if (res.extracted_facts && res.extracted_facts.severity?.value >= 7 && res.extracted_facts.chief_complaint) {
        setRedFlags(prev => [...prev, 'EMERGENCY_DETECTED']);
      }
      // Capture AYUSH profile when present
      if (res.ayush_profile) {
        setAyushProfile(res.ayush_profile);
      }
      if (res.is_complete || !res.next_question) {
        await conversationApi.submit(sessionId);
        // For AYUSH mode, stay on this page to show the summary; otherwise go to documents.
        if (mode === 'ayush') {
          // Show summary — the page will render the profile view because currentQuestion is null
          setCurrentQuestion(null);
        } else {
          navigate('/documents');
        }
      } else {
        setCurrentQuestion(res.next_question);
        speakQuestion(res.next_question);
      }
    } catch (e) {
      console.error('Submission failed', e);
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    if (isRecording && recorderRef.current) {
      recorderRef.current.stop();
      return;
    }
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(mediaStream, { mimeType: 'audio/webm' });
      chunks.current = [];
      recorder.ondataavailable = e => { if (e.data.size) chunks.current.push(e.data); };
      recorder.onstop = async () => {
        mediaStream.getTracks().forEach(t => t.stop());
        setIsRecording(false);
        setLoading(true);
        try {
          const audioBlob = new Blob(chunks.current, { type: 'audio/webm' });
          const result = await voiceApi.transcribe(sessionId, audioBlob as File, lang);
          const transcript = result?.transcript || result?.text || result?.transcription || '';
          if (transcript) {
            setVoiceTranscript(transcript);
            setShowVoiceConfirm(true);
          } else {
            setVoiceTranscript('');
          }
        } catch {
          setVoiceTranscript('');
        } finally {
          setLoading(false);
        }
      };
      recorderRef.current = recorder;
      recorder.start(1000);
      setIsRecording(true);
    } catch (e) {
      console.error('Mic access denied', e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader
        title={isHindi ? 'नैदानिक साक्षात्कार' : 'Clinical Interview'}
        subtitle={currentQuestion ? `${isHindi ? 'अनुभाग: ' : 'Section: '}${(currentQuestion as any).section || ''}` : (isHindi ? 'कनेक्ट हो रहा है...' : 'Connecting...')}
        icon={<Volume2 className="h-6 w-6 text-white" />}
        action={<Button variant="ghost" onClick={() => navigate('/mode')}><ArrowLeft className="h-4 w-4 mr-2" /> {isHindi ? 'बाहर' : 'Exit'}</Button>}
      />

      <div className="flex-1 px-4 md:px-8 py-8 max-w-3xl mx-auto w-full flex flex-col gap-6">
        {redFlags.length > 0 && (
          <div className="rounded-xl bg-red-50 border border-red-200 p-4 flex items-center gap-3 animate-slide-up">
            <AlertTriangle className="h-6 w-6 text-red-600 shrink-0" />
            <div>
              <div className="font-bold text-red-700">{isHindi ? 'आपातकालीन लक्षण' : 'Emergency Symptom Detected'}</div>
              <div className="text-sm text-red-600">{isHindi ? '�कृपया तुरंत ट्रायाज नर्स डेस्क पर जाएं।' : 'Please proceed immediately to the triage nurse desk.'}</div>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <div className="flex justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
            <span>{isHindi ? 'प्रगति' : 'Progress'}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <ProgressBar value={progress} />
        </div>

        {/* Voice confirmation modal */}
        {showVoiceConfirm && (
          <Card className="p-6 border-2 border-brand-300 animate-slide-up">
            <h3 className="font-bold text-lg mb-3">{isHindi ? 'क्या आपने यह कहा?' : 'Did you say:'}</h3>
            <p className="text-xl italic text-slate-700 mb-4">"{voiceTranscript}"</p>
            <div className="flex gap-3">
              <Button variant="primary" onClick={handleVoiceConfirm}>
                <Check className="h-4 w-4 mr-2" /> {isHindi ? 'हाँ, आगे' : 'Yes, continue'}
              </Button>
              <Button variant="secondary" onClick={handleVoiceReject}>
                <X className="h-4 w-4 mr-2" /> {isHindi ? 'नहीं, दोबारा बोलें' : 'No, speak again'}
              </Button>
            </div>
          </Card>
        )}

        {loading && !currentQuestion ? (
          <Card className="flex-1 flex flex-col justify-center items-center p-12 text-center">
            <Spinner size="lg" />
            <p className="mt-4 text-slate-500">{isHindi ? 'प्रश्न लोड हो रहे हैं...' : 'Loading question...'}</p>
          </Card>
        ) : mode === 'ayush' && ayushProfile ? (
          // AYUSH intake completion summary
          <Card className="flex-1 flex flex-col p-8 animate-slide-up" data-testid="ayush-summary">
            <div className="text-center mb-6">
              <h2 className="text-2xl md:text-3xl font-bold text-slate-900">
                {isHindi ? 'आपका आयुर्वेद सारांश' : 'Your Ayurvedic Intake Summary'}
              </h2>
              <p className="text-sm text-slate-500 mt-2">
                {isHindi
                  ? 'आपके उत्तरों के आधार पर सांकेतिक मूल्यांकन'
                  : 'Indicative assessment generated from your responses'}
              </p>
              <p className="text-xs text-slate-400 mt-1 italic">
                {isHindi
                  ? 'यह चिकित्सीय निदान नहीं है। चिकित्सक सत्यापन आवश्यक।'
                  : 'Not a medical diagnosis. Practitioner verification required.'}
              </p>
            </div>

            <div className="space-y-5">
              <div>
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                  {isHindi ? 'प्रकृति प्रवृत्ति' : 'Prakriti tendency'}
                </h3>
                {(['vata_score', 'pitta_score', 'kapha_score'] as const).map((k) => {
                  const label = k === 'vata_score' ? 'Vata' : k === 'pitta_score' ? 'Pitta' : 'Kapha';
                  const v = ayushProfile?.prakriti?.[k] ?? 0;
                  return (
                    <div key={k} className="mb-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-700">{label}</span>
                        <span className="font-mono text-slate-500">{Math.round(v * 100)}%</span>
                      </div>
                      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-2 bg-emerald-500" style={{ width: `${Math.min(100, v * 100)}%` }} />
                      </div>
                    </div>
                  );
                })}
                <p className="text-sm text-slate-600 mt-2">
                  {isHindi
                    ? `आपके उत्तर ${ayushProfile?.prakriti?.dominant_type || ''} की प्रवृत्ति दर्शाते हैं।`
                    : `Your responses indicate a higher ${ayushProfile?.prakriti?.dominant_type || ''} tendency.`}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-xs font-bold text-slate-500 uppercase">Agni</div>
                  <div className="text-slate-800 font-medium">{ayushProfile?.agni?.assessment || '—'}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-xs font-bold text-slate-500 uppercase">Koshtha</div>
                  <div className="text-slate-800 font-medium">{ayushProfile?.koshtha?.assessment || '—'}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-xs font-bold text-slate-500 uppercase">Satva (sleep)</div>
                  <div className="text-slate-800 font-medium">{ayushProfile?.satva?.sleep_quality || '—'}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-xs font-bold text-slate-500 uppercase">Satva (stress)</div>
                  <div className="text-slate-800 font-medium">{ayushProfile?.satva?.stress_response || '—'}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 col-span-2">
                  <div className="text-xs font-bold text-slate-500 uppercase">Lifestyle (Ahara-Vihara)</div>
                  <div className="text-slate-800 font-medium">
                    Activity: {ayushProfile?.ahara_vihara?.activity_level || '—'}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-center">
              <Button variant="primary" size="lg" onClick={() => navigate('/documents')}>
                {isHindi ? 'दस्तावेज़ पर जाएं' : 'Continue to Documents'}
                <ChevronRight className="h-5 w-5 ml-2" />
              </Button>
            </div>
          </Card>
        ) : (
          <Card className="flex-1 flex flex-col justify-center p-12 text-center animate-slide-up relative overflow-hidden">
            {isSpeaking && (
              <div className="absolute top-4 right-4">
                <div className="flex gap-1">
                  <div className="w-1 h-4 bg-brand-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1 h-4 bg-brand-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1 h-4 bg-brand-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}

            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-8 leading-tight">
              {currentQuestion ? getQText(currentQuestion) : '...'}
            </h2>

            <div className="w-full max-w-md mx-auto space-y-4">
              <div className="relative">
                <textarea
                  className="w-full p-4 rounded-2xl border-2 border-slate-200 focus:border-brand-500 outline-none text-lg transition-all min-h-[120px]"
                  placeholder={isHindi ? "यहाँ लिखें..." : "Type your answer here..."}
                  value={input}
                  onChange={e => { setInput(e.target.value); inputModeRef.current = 'touch'; }}
                  disabled={loading}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmitAnswer(); } }}
                />
                <button
                  onClick={startRecording}
                  disabled={loading}
                  className={`absolute bottom-4 right-4 p-3 rounded-full transition-all ${isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                  title={isHindi ? "आवाज़ से बोलें" : "Speak with voice"}
                >
                  <Mic className="h-5 w-5" />
                </button>
              </div>

              <div className="flex gap-3 justify-center">
                <Button
                  variant="secondary"
                  className="px-8 py-3"
                  onClick={() => speakQuestion(currentQuestion)}
                  disabled={isSpeaking || !currentQuestion || loading}
                >
                  <Volume2 className="h-5 w-5 mr-2" /> {isHindi ? 'दोहराएं' : 'Repeat'}
                </Button>
                <Button
                  variant="primary"
                  className="px-8 py-3"
                  onClick={() => handleSubmitAnswer()}
                  disabled={!input.trim() || loading}
                >
                  {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <><span>{isHindi ? 'आगे' : 'Next'}</span> <ChevronRight className="h-5 w-5 ml-2" /></>}
                </Button>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
