import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, AlertCircle, Loader2, Save, AlertTriangle } from 'lucide-react';
import { Button, Card, KioskHeader, InfoBanner, Badge } from '../components/ui';
import { ocrApi } from '../services/api';
import type { OCREntity } from '../types';

export default function OCRVerifyPage() {
  const { docId } = useParams();
  const navigate = useNavigate();
  const [entities, setEntities] = useState<OCREntity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const sessionId = JSON.parse(sessionStorage.getItem('medikiosk_session') || '{}').session_id || 'demo-session-001';

  useEffect(() => {
    if (!docId) return;
    ocrApi.detail(sessionId, docId).then(data => {
      setEntities(data.structured_entities || []);
      setLoading(false);
    }).catch(e => {
      setError('Failed to load document details');
      setLoading(false);
    });
  }, [docId]);

  const handleUpdateEntity = (index: number, newValue: string) => {
    setEntities(prev => {
      const next = [...prev];
      next[index] = { ...next[index], value: newValue, requires_verification: false };
      return next;
    });
  };

  const handleSave = async () => {
    setSaving(true);
    await new Promise(r => setTimeout(r, 1000)); // Mock save
    setSaving(false);
    navigate('/documents');
  };

  if (loading) return <div className="min-h-screen bg-slate-50"><KioskHeader title="Verify Extraction" subtitle="Human-in-the-loop verification" /> <div className="flex items-center justify-center h-full"><Loader2 className="h-10 w-10 animate-spin text-brand-600" /></div></div>;
  if (error) return <div className="min-h-screen bg-slate-50"><KioskHeader title="Verify Extraction" /> <div className="p-6 text-center text-red-600">{error}</div></div>;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader title="Verify Extraction" subtitle="Please check the AI-extracted data for accuracy" icon={<CheckCircle className="h-6 w-6 text-white" />} />
      <div className="flex-1 px-4 md:px-8 py-8 max-w-5xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Document View (Mock) */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-3 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
            <span className="text-xs font-bold text-slate-500 uppercase">Document Preview</span>
            <Badge variant="info">PDF/Image</Badge>
          </div>
          <div className="flex-1 bg-slate-200 flex items-center justify-center p-8">
            <div className="w-full h-full bg-white shadow-lg rounded border border-slate-300 p-8 flex flex-col gap-4 opacity-60">
              <div className="h-4 w-1/3 bg-slate-200 rounded" />
              <div className="h-4 w-full bg-slate-100 rounded" />
              <div className="h-4 w-full bg-slate-100 rounded" />
              <div className="h-4 w-2/3 bg-slate-100 rounded" />
              <div className="mt-8 h-20 w-full border-2 border-dashed border-slate-300 rounded flex items-center justify-center text-slate-400 italic text-sm">
                [ Mocked Document View ]
              </div>
            </div>
          </div>
        </div>

        {/* Entities List */}
        <div className="space-y-6">
          <Card title="Extracted Clinical Entities" subtitle="Correct any mistakes below">
            <div className="space-y-4">
              {entities.map((entity, i) => (
                <div key={i} className="p-4 rounded-xl border border-slate-200 bg-white">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase text-slate-500">{entity.type}</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${entity.confidence > 0.8 ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                        {(entity.confidence * 100).toFixed(0)}% Conf.
                      </span>
                      {entity.requires_verification && <AlertCircle className="h-3 w-3 text-amber-500" />}
                    </div>
                  </div>
                  <input
                    type="text"
                    value={entity.value}
                    onChange={e => handleUpdateEntity(i, e.target.value)}
                    className={`w-full px-3 py-2 rounded-lg border ${entity.requires_verification ? 'border-amber-400 bg-amber-50' : 'border-slate-200'} focus:outline-none focus:ring-2 focus:ring-brand-500/20`}
                  />
                  {entity.warning && <p className="text-[10px] text-amber-600 mt-1 flex items-center gap-1"><AlertTriangle className="h-3 w-3" /> {entity.warning}</p>}
                </div>
              ))}
            </div>
            <div className="mt-6 flex items-center justify-between">
              <Button variant="ghost" onClick={() => navigate(-1)}><ArrowLeft className="h-4 w-4" /> Back</Button>
              <Button onClick={handleSave} disabled={saving} variant="primary" size="lg">
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />} Save Corrections
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
