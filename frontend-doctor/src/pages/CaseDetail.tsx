import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, ShieldCheck, FileText, Activity, Clock, Fingerprint, Globe, Info, AlertCircle, CheckCircle2, Save } from 'lucide-react';
import { Button, Card, KioskHeader, Badge, ProgressBar, InfoBanner, Spinner } from '../components/ui';
import { doctorApi } from '../services/api';
import type { ClinicalCase, FHIRBundle, OCREntity } from '../types';

export default function CaseDetail() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<ClinicalCase | null>(null);
  const [fhir, setFhir] = useState<FHIRBundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'summary' | 'fhir' | 'timeline'>('summary');
  const [ocrEntities, setOcrEntities] = useState<OCREntity[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!sessionId) return;
    Promise.all([
      doctorApi.summary(sessionId),
      doctorApi.fhir(sessionId)
    ]).then(([summary, bundle]) => {
      setCaseData(summary);
      setFhir(bundle);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [sessionId]);

  const handleVerifyOcr = async (index: number, value: string) => {
    const next = [...ocrEntities];
    next[index] = { ...next[index], value, requires_verification: false };
    setOcrEntities(next);
  };

  const handleCommitCase = async () => {
    setSaving(true);
    await new Promise(r => setTimeout(r, 1000)); // Mock save
    setSaving(false);
    navigate('/');
  };

  if (loading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div></div>;
  if (!caseData) return <div className="min-h-screen bg-slate-50 p-8 text-center">Case not found</div>;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader
        title={`Clinical Review: ${caseData.session_id.slice(0, 8)}`}
        subtitle={`${caseData.department} | ${caseData.mode.toUpperCase()} | ${caseData.language_code}`}
        icon={<Activity className="h-6 w-6 text-white" />}
        action={<Button variant="ghost" onClick={() => navigate('/')}><ArrowLeft className="h-4 w-4 mr-2" /> Back to Queue</Button>}
      />

      <div className="flex-1 px-4 md:px-8 py-8 max-w-7xl mx-auto w-full">
        <div className="flex gap-2 mb-6 bg-white p-1 rounded-2xl border border-slate-200 w-fit">
          <Button
            variant={view === 'summary' ? 'primary' : 'ghost'}
            onClick={() => setView('summary')}
            className="rounded-xl"
          >Clinical Summary</Button>
          <Button
            variant={view === 'fhir' ? 'primary' : 'ghost'}
            onClick={() => setView('fhir')}
            className="rounded-xl"
          >FHIR Bundle</Button>
          <Button
            variant={view === 'timeline' ? 'primary' : 'ghost'}
            onClick={() => setView('timeline')}
            className="rounded-xl"
          >Provenance Timeline</Button>
        </div>

        {view === 'summary' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              {/* Red Flags */}
              {caseData.has_red_flags && (
                <div className="bg-red-50 border-2 border-red-200 p-6 rounded-3xl flex gap-4 animate-fade-in">
                  <AlertCircle className="h-8 w-8 text-red-600 shrink-0" />
                  <div>
                    <h3 className="text-lg font-bold text-red-800">Emergency Red Flags Detected</h3>
                    <ul className="mt-2 space-y-1">
                      {caseData.red_flags?.map((f, i) => (
                        <li key={i} className="text-red-700 text-sm flex items-start gap-2">
                          <span className="mt-1 h-1.5 w-1.5 rounded-full bg-red-600 shrink-0" /> {f.description}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Structured Clinical Summary */}
              <Card title="Structured Clinical History" subtitle="AI-extracted facts grouped by clinical section">
                <div className="space-y-8">
                  {[ 'Chief Complaint', 'HPI', 'Past Medical History', 'Surgical History', 'CRks' ].map(section => (
                    <div key={section} className="space-y-3">
                      <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <div className="h-px flex-1 bg-slate-100" /> {section} <div className="h-px flex-1 bg-slate-100" />
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {((caseData.clinical_history_array || []) as any[]).filter((f: any) => f.category === section).length > 0 ? (
                          ((caseData.clinical_history_array || []) as any[]).filter((f: any) => f.category === section).map((f: any) => (
                            <div key={f.fact_id || f.label} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center group">
                              <div>
                                <span className="text-xs font-medium text-slate-500 block">{f.label}</span>
                                <span className="text-sm font-bold text-slate-900">{f.value}</span>
                              </div>
                              <Badge variant="neutral" className="text-[10px] opacity-60">{f.provenance.input_mode}</Badge>
                            </div>
                          ))
                        ) : (
                          <div className="text-xs text-slate-400 italic py-2">No facts extracted for this section</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* OCR Verification Workspace */}
              <Card title="Document Verification" subtitle="Verify AI extracted fields against original source">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-slate-200 rounded-2xl aspect-[3/4] flex items-center justify-center relative overflow-hidden border-2 border-slate-300">
                    <FileText className="h-12 w-12 text-slate-400" />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900/20 to-transparent pointer-events-none" />
                    <span className="absolute bottom-4 left-4 text-xs font-medium text-slate-600 bg-white/80 px-2 py-1 rounded">Source_Doc_01.pdf</span>
                  </div>
                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                    {ocrEntities.length > 0 ? ocrEntities.map((e, i) => (
                      <div key={i} className="p-3 rounded-xl border-2 border-slate-200 bg-white transition-all focus-within:border-brand-500">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs font-bold text-slate-500 uppercase">{e.label}</span>
                          {e.requires_verification && <Badge variant="warning">Verify</Badge>}
                        </div>
                        <input
                          type="text"
                          value={e.value}
                          onChange={e => handleVerifyOcr(i, e.target.value)}
                          className="w-full text-sm font-medium text-slate-900 outline-none bg-transparent"
                        />
                      </div>
                    )) : (
                      <div className="text-center py-12 text-slate-400 italic text-sm">No extracted entities to verify.</div>
                    )}
                  </div>
                </div>
              </Card>
            </div>

            <div className="space-y-6">
              {/* Patient Profile & Metadata */}
              <Card title="Patient Context">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-500">Case ID</span>
                    <span className="text-sm font-mono font-bold text-slate-900">{caseData.session_id.slice(0, 12)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-500">Triage Priority</span>
                    <Badge variant={caseData.priority === 'high' ? 'danger' : 'neutral'}>{caseData.priority.toUpperCase()}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-500">ABDM Sync</span>
                    <Badge variant={caseData.abdm_synced ? 'success' : 'warning'}>
                      {caseData.abdm_synced ? 'Synced' : 'Pending'}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-500">Mapping Status</span>
                    <div className="flex gap-1">
                      <Badge variant="neutral" className="text-[10px]">NAMASTE</Badge>
                      <Badge variant="neutral" className="text-[10px]">ICD-11</Badge>
                    </div>
                  </div>
                </div>
              </Card>

              {/* AYUSH Profile (only for Ayurveda — indicative intake assessment) */}
              {caseData.mode === 'ayush' && caseData.ayush_profile && (
                <Card title="AYURVEDA INTAKE PROFILE" subtitle="Indicative intake assessment — practitioner verification required" className="border-amber-200">
                  <div className="space-y-6">
                    {/* Prakriti */}
                    <section>
                      <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-3">Prakriti</h4>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div className="p-3 rounded-xl bg-slate-50">
                          <div className="text-xs text-slate-500">Vata</div>
                          <div className="font-mono font-bold text-slate-900">{Math.round((caseData.ayush_profile?.prakriti?.vata_score || 0) * 100)}%</div>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-50">
                          <div className="text-xs text-slate-500">Pitta</div>
                          <div className="font-mono font-bold text-slate-900">{Math.round((caseData.ayush_profile?.prakriti?.pitta_score || 0) * 100)}%</div>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-50">
                          <div className="text-xs text-slate-500">Kapha</div>
                          <div className="font-mono font-bold text-slate-900">{Math.round((caseData.ayush_profile?.prakriti?.kapha_score || 0) * 100)}%</div>
                        </div>
                      </div>
                      <div className="text-sm text-slate-700 mt-2">
                        Dominant: <span className="font-bold text-amber-700">{caseData.ayush_profile?.prakriti?.dominant_type || 'Not assessed'}</span>
                        <span className="text-slate-400 ml-2">(confidence: {Math.round((caseData.ayush_profile?.prakriti?.confidence || 0) * 100)}%)</span>
                      </div>
                    </section>

                    {/* Agni */}
                    <section>
                      <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">Agni</h4>
                      <div className="text-sm text-slate-800">
                        Assessment: <span className="font-medium">{caseData.ayush_profile?.agni?.assessment || 'Not assessed'}</span>
                        <span className="text-slate-400 ml-2">(confidence: {Math.round((caseData.ayush_profile?.agni?.confidence || 0) * 100)}%)</span>
                      </div>
                    </section>

                    {/* Koshtha */}
                    <section>
                      <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">Koshtha</h4>
                      <div className="text-sm text-slate-800">
                        Assessment: <span className="font-medium">{caseData.ayush_profile?.koshtha?.assessment || 'Not assessed'}</span>
                        <span className="text-slate-400 ml-2">(confidence: {Math.round((caseData.ayush_profile?.koshtha?.confidence || 0) * 100)}%)</span>
                      </div>
                    </section>

                    {/* Satva */}
                    <section>
                      <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">Satva</h4>
                      <div className="text-sm text-slate-800 space-y-1">
                        <div>Stress response: <span className="font-medium">{caseData.ayush_profile?.satva?.stress_response || '—'}</span></div>
                        <div>Sleep quality: <span className="font-medium">{caseData.ayush_profile?.satva?.sleep_quality || '—'}</span></div>
                        <div className="text-slate-400">Confidence: {Math.round((caseData.ayush_profile?.satva?.confidence || 0) * 100)}%</div>
                      </div>
                    </section>

                    {/* Ahara-Vihara */}
                    <section>
                      <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">Ahara-Vihara</h4>
                      <div className="text-sm text-slate-800">
                        Activity: <span className="font-medium">{caseData.ayush_profile?.ahara_vihara?.activity_level || '—'}</span>
                        <span className="text-slate-400 ml-2">(confidence: {Math.round((caseData.ayush_profile?.ahara_vihara?.confidence || 0) * 100)}%)</span>
                      </div>
                    </section>
                  </div>
                </Card>
              )}

              <Button
                variant="primary"
                size="lg"
                className="w-full py-4 shadow-lg"
                onClick={handleCommitCase}
                disabled={saving}
              >
                {saving ? <Spinner size="sm" /> : <><Save className="h-5 w-5 mr-2" /> Verify & Commit Case</>}
              </Button>
            </div>
          </div>
        )}

        {view === 'fhir' && (
          <Card title="FHIR Resource Bundle" subtitle="HL7 FHIR R4 Standardized Output">
            <div className="bg-slate-900 text-emerald-400 p-6 rounded-2xl font-mono text-xs overflow-x-auto leading-relaxed">
              <pre>{JSON.stringify(fhir, null, 2)}</pre>
            </div>
          </Card>
        )}

        {view === 'timeline' && (
          <Card title="Provenance Timeline" subtitle="Traceability of clinical facts">
             <div className="space-y-6 py-4">
                {((caseData.clinical_history_array || []) as any[]).map((f: any, i: number) => (
                  <div key={i} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`h-3 w-3 rounded-full ${f.provenance.input_mode === 'voice' ? 'bg-brand-500' : 'bg-emerald-500'}`} />
                      <div className="w-px h-full bg-slate-200" />
                    </div>
                    <div className="pb-6">
                      <div className="text-xs font-bold text-slate-400 mb-1">{f.provenance.timestamp}</div>
                      <div className="text-sm font-bold text-slate-900">{f.label}: {f.value}</div>
                      <div className="flex gap-2 mt-1">
                        <Badge variant="neutral" className="text-[10px]">{f.provenance.input_mode}</Badge>
                        <Badge variant="neutral" className="text-[10px]">{f.provenance.language}</Badge>
                      </div>
                    </div>
                  </div>
                ))}
             </div>
          </Card>
        )}
      </div>
    </div>
  );
}
