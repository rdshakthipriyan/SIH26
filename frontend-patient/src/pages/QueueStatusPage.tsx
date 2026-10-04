import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, CheckCircle, AlertTriangle, Loader2, User } from 'lucide-react';
import { Button, Card, KioskHeader, ProgressBar, Badge, InfoBanner } from '../components/ui';
import { queueApi } from '../services/api';
import type { QueueToken, QueueListResponse } from '../types';

export default function QueueStatusPage() {
  const navigate = useNavigate();
  const [queue, setQueue] = useState<QueueListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [myToken, setMyToken] = useState<QueueToken | null>(null);

  useEffect(() => {
    queueApi.list().then(data => {
      setQueue(data);
      // Mock finding "my" token
      setMyToken(data.tokens[0] || null);
      setLoading(false);
    }).catch(e => {
      setError('Failed to load queue status');
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="min-h-screen bg-slate-50"><KioskHeader title="Queue Status" icon={<Clock className="h-6 w-6 text-white" />} /><div className="flex items-center justify-center h-full"><Loader2 className="h-10 w-10 animate-spin text-brand-600" /></div></div>;
  if (error) return <div className="min-h-screen bg-slate-50"><KioskHeader title="Queue Status" /> <div className="p-6 text-center text-red-600">{error}</div></div>;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader title="Queue Status" subtitle="Live OPD Token Tracking" icon={<Clock className="h-6 w-6 text-white" />} />
      <div className="flex-1 px-4 md:px-8 py-8 max-w-2xl mx-auto w-full">
        {myToken && (
          <Card className="mb-6 border-brand-500 ring-2 ring-brand-200 shadow-xl overflow-hidden">
            <div className="bg-brand-600 p-4 text-white flex justify-between items-center">
              <span className="font-bold uppercase tracking-wider text-sm">Your Token</span>
              <Badge variant="success">Ready</Badge>
            </div>
            <div className="p-6 flex flex-col items-center text-center">
              <div className="text-6xl font-black text-slate-900 mb-2">{myToken.token_number}</div>
              <div className="text-slate-500 font-medium mb-6">Department: {myToken.department}</div>
              <div className="grid grid-cols-2 gap-4 w-full">
                <div className="p-4 rounded-2xl bg-slate-50">
                  <div className="text-xs text-slate-400 uppercase font-bold mb-1">Position</div>
                  <div className="text-2xl font-bold text-slate-900">{myToken.position}</div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50">
                  <div className="text-xs text-slate-400 uppercase font-bold mb-1">Priority</div>
                  <div className="text-2xl font-bold text-brand-600">{myToken.priority}</div>
                </div>
              </div>
              {myToken.has_red_flags && (
                <InfoBanner kind="warning" title="Priority Triage" detail="Your symptoms indicate a need for priority review. A nurse will call you shortly." className="mt-6 w-full" />
              )}
            </div>
          </Card>
        )}

        <Card title="Waiting Room">
          <div className="space-y-3">
            {queue?.tokens.map(t => (
              <div key={t.token_id} className="flex items-center justify-between p-3 border border-slate-100 rounded-xl bg-white hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-600">{t.token_number}</div>
                  <div>
                    <div className="text-sm font-semibold text-slate-800">{t.department}</div>
                    <div className="text-xs text-slate-500">Pos: {t.position}</div>
                  </div>
                </div>
                <Badge variant={t.status === 'completed' ? 'success' : 'info'}>{t.status}</Badge>
              </div>
            ))}
          </div>
        </Card>

        <div className="mt-8 flex justify-center gap-4">
          <Button onClick={() => navigate('/')} variant="ghost" className="px-8 py-3">Exit Kiosk</Button>
          <Button onClick={() => navigate('/documents')} variant="secondary" className="px-8 py-3">Upload More Docs</Button>
        </div>
      </div>
    </div>
  );
}
